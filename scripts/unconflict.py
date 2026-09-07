"""Clear the generated-inventory merge conflict that re-stales the whole PR queue.

Every merge into main rewrites four committed-but-generated files. Any open branch that
also touched them then conflicts, so the queue serialises at one PR per manual
rebase-and-fix round. Measured 2026-09-02: 69 of 126 open PRs CONFLICTING, and the
conflicts were generated-file-only in every case inspected (11 of 11).

The fix is mechanical and identical every time:

    merge origin/main -> take MAIN's copy of the generated files -> regenerate -> push

This script does exactly that, and REFUSES when the conflict is anything else, so a real
content conflict is never silently resolved in main's favour.

    python scripts/unconflict.py --dry-run
    python scripts/unconflict.py --branch card/my-thing-master
    python scripts/unconflict.py --all-mine --suffix -master --dry-run

Exit codes: 0 clean/done, 1 refused (real conflict or unsafe state), 2 bad usage.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# The committed-but-generated set. A conflict confined to these is safe to resolve by
# taking main's copy, because the correct contents are then recomputed from scratch by
# the generators below. Anything outside this set is a real disagreement.
#
# This is an explicit OUTPUT allowlist, deliberately not a directory prefix. The SRI layer
# added 2026-09 mixes generated output with hand-written INPUT in one directory:
# workflow/inventories/sri/CURATED.json is the curated prose the build reads, and
# workflow/inventories/sri/runs/** are one-off run records. A prefix rule would silently
# overwrite either with main's copy and then "regenerate" it, destroying hand-written work.
# Both must keep falling through to the refusal path, and there are tests for that.
GENERATED = (
    "workflow/HARNESS-INDEX.json",
    "workflow/HARNESS-INDEX-FULL.json",
    "workflow/ARTIFACT-CATALOG.jsonl",
    "workflow/ARTIFACT-CATALOG.md",
    # SRI layer outputs, rebuilt by scripts/build_sri.py.
    "workflow/inventories/sri/BUILD.json",
    "workflow/inventories/sri/INDEX.md",
    "workflow/inventories/sri/INVENTORY.md",
    "workflow/inventories/sri/MANIFEST.jsonl",
    "workflow/inventories/sri/registers/CLAIMS.md",
    "workflow/inventories/sri/registers/DECISIONS.md",
    "workflow/inventories/sri/registers/KNOWLEDGE-RECORDS.md",
    "workflow/inventories/sri/registers/LEARNINGS.md",
    "workflow/inventories/sri/registers/METHODS.md",
    "workflow/inventories/sri/registers/OPEN.md",
    "workflow/inventories/sri/registers/RETEST-QUEUE.md",
    "workflow/inventories/sri/registers/TIMELINE.md",
    "workflow/inventories/sri/registers/TOMBSTONES.md",
    "workflow/inventories/sri/registers/TOOLS.md",
)

# The generators that recompute GENERATED, in the order they must run. Each is skipped if
# absent (a branch cut before it existed), but a generator that RUNS and FAILS aborts the
# whole repair: a half-regenerated layer pushed to a PR is worse than an unresolved
# conflict, because the freshness gate then fails on content nobody wrote.
GENERATORS = ("regen_indexes.py", "build_sri.py")


# git emits UTF-8 (commit subjects here carry em-dashes and accented names). On Windows the
# default text decoding is cp1252, which raises UnicodeDecodeError mid-read, so pin it.
_DECODE = {"capture_output": True, "text": True, "encoding": "utf-8", "errors": "replace"}


# The tree every git op runs in. A branch checked out in ANOTHER worktree cannot be
# checked out here, but it CAN be operated on in place -- that is the whole point of a
# worktree. Measured 2026-09-02: 8 of 11 refusals on this seat's lane were "held by
# another worktree", so delegating instead of refusing is most of the tool's coverage.
_CWD: str | None = None


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    if check:
        return _checked(["git", *args])
    return subprocess.run(["git", *args], cwd=_CWD, **_DECODE)


def _checked(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, cwd=_CWD, **_DECODE)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{(r.stderr or '').strip()}")
    return r


def out(*args: str) -> str:
    return (_checked(["git", *args]).stdout or "").strip()


def worktree_of(branch: str) -> str | None:
    """The worktree holding `branch`, if one other than the current tree does."""
    r = subprocess.run(["git", "worktree", "list", "--porcelain"], **_DECODE)
    path = None
    for line in (r.stdout or "").splitlines():
        if line.startswith("worktree "):
            path = line[9:].strip()
        elif line.startswith("branch ") and path:
            if line[7:].strip().replace("refs/heads/", "") == branch:
                return path
    return None


def conflicted_paths() -> list[str]:
    r = git("diff", "--name-only", "--diff-filter=U", check=False)
    return [p for p in r.stdout.split("\n") if p.strip()]


def _conflicted_paths_dry() -> list[str] | None:
    """Paths that WOULD conflict, without performing the merge.

    `git merge-tree --write-tree --name-only A B` prints the resulting tree oid, then one
    conflicted path per line, then a blank line and human-readable messages. An empty path
    list means the merge is clean.

    Returns None when git cannot answer (these flags landed in 2.38), so the caller falls
    back to counting hunks rather than silently reporting a branch as clear.
    """
    r = git("merge-tree", "--write-tree", "--name-only", "HEAD", "origin/main", check=False)
    if r.returncode not in (0, 1) or not (r.stdout or "").strip():
        return None
    lines = r.stdout.splitlines()
    paths: list[str] = []
    for ln in lines[1:]:          # line 0 is the tree oid
        if not ln.strip():
            break
        paths.append(ln.strip())
    return paths


def is_dirty() -> bool:
    """True if the worktree holds work that a branch switch could destroy.

    CRLF-ONLY DIFFERENCES DO NOT COUNT, and that distinction is load-bearing on this
    repo. Some files were committed with CRLF already in the blob -- measured
    2026-09-03: 10 files under ptcg-agent/experiments/eval/ whose HEAD blob itself
    carries CR=2469 -- so under core.autocrlf=true git reports them modified forever.
    `git checkout -f` cannot settle them; they are byte-identical modulo CRLF
    (`git diff --ignore-cr-at-eol` returns 0 paths). Treating that as dirt made the
    sweep refuse work it could safely do, on a condition no seat can clear.

    Untracked and STAGED changes still count. Those can be real uncommitted work, and
    `git diff` alone would not see the untracked ones.
    """
    if git("ls-files", "--others", "--exclude-standard", check=False).stdout.strip():
        return True
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        return True
    return git("diff", "--quiet", "--ignore-cr-at-eol", check=False).returncode != 0


def regenerate_and_commit() -> int:
    """Rebuild every generator's output and commit it. 0 on success, 1 on refusal.

    Two state defects found by ASTRA's review of #3511, both reproduced in real git
    fixtures, are fixed here and pinned by tests:

    1. THE FAILURE PATH MUST BE RETRYABLE. The merge resolution used to be committed
       BEFORE the generators ran, so a generator failure left a committed merge behind
       and the retry treated it as completed work. Repaired on two fronts, and both are
       kept because they cover different histories: the CONFLICT path now leaves the
       merge uncommitted until regeneration and staging both succeed, so a retry
       re-executes the merge (SKYNET-CODEX's fix, cherry-picked as b1550f209a); and the
       "already up to date" and "merges clean but ahead" paths regenerate before
       publishing, which also covers a merge committed by an older copy of this tool or
       by a human.
    2. A MISSING OPTIONAL OUTPUT MUST NOT SILENTLY SKIP THE COMMIT. `git add -- <paths>`
       fails outright when a pathspec matches nothing, and the result was unchecked, so a
       branch that legitimately lacks one allowlisted file (cut before it existed) lost
       the whole staging step: successfully rebuilt files stayed uncommitted and the tool
       still returned 0. Stage paths that exist OR are tracked -- tracked-but-absent is
       an intended DELETION and must still be staged, which an existence test alone
       misses (also SKYNET-CODEX's) -- and check the exit code.
    """
    # The generators must run in the DELEGATED tree, not the caller's. Without cwd they
    # regenerated this seat's own worktree instead, leaving it dirty -- which then tripped
    # the dirty-tree guard on every subsequent branch. Caught on the first multi-branch run.
    root = Path(_CWD) if _CWD else Path.cwd()
    ran_any = False
    for name in GENERATORS:
        script = root / "scripts" / name
        if not script.exists():
            continue
        r = subprocess.run([sys.executable, str(script)], cwd=str(root),
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        ran_any = True
        if r.returncode != 0:
            # Do not commit and do not push. Pushing a partial regeneration would put
            # content nobody wrote in front of the freshness gate.
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            print(f"  REFUSED: {name} failed (exit {r.returncode}); not committing, not pushing")
            if tail:
                print(f"    {tail[-1]}")
            return 1

    if not ran_any:
        return 0

    # Stage the allowlisted outputs that exist OR are tracked. The previous
    # `git add -A workflow/` swept in anything else the caller had under workflow/, which
    # is not this tool's to commit; naming the full allowlist instead made git fail on any
    # absent entry. Tracked-but-absent is kept deliberately: that is an intended deletion,
    # and dropping it would leave the removal unstaged while reporting success.
    stageable = [
        p for p in GENERATED
        if (root / p).exists()
        or git("ls-files", "--error-unmatch", "--", p, check=False).returncode == 0
    ]
    if not stageable:
        print("  REFUSED: generators ran but produced none of the allowlisted outputs")
        return 1
    if git("add", "--", *stageable, check=False).returncode != 0:
        print("  REFUSED: staging the regenerated outputs failed; not committing, not pushing")
        return 1

    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        # MERGE_HEAD is normally already cleared, because the conflict path commits the
        # merge before regenerating (see the comment there). This branch survives for a
        # caller that arrives mid-merge, and completes it rather than stranding the
        # resolution behind a second unrelated commit.
        if git("rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0:
            _checked(["git", "commit", "-q", "--no-edit"])
        else:
            _checked(["git", "commit", "-q", "-m", "chore(inventories): regenerate against main"])
        print("  regenerated inventories")

    # VERIFY, DO NOT ASSUME. Both defects previously found in this tool reported SUCCESS
    # while leaving the branch wrong, so a generator's exit code is not evidence that its
    # output is correct -- it regenerated happily against the wrong history on #3514. Ask
    # the freshness checker, which is the same one CI runs, and refuse when it disagrees.
    return 1 if generated_content_is_stale() else 0


def generated_content_is_stale() -> bool:
    """True when the freshness checker reports CONTENT DRIFT in the delegated tree.

    Absence of the checker is NOT staleness: a branch cut before it existed would
    otherwise be refused on a condition its author cannot clear. Returns False there,
    deliberately, and the CI gate remains the backstop.
    """
    root = Path(_CWD) if _CWD else Path.cwd()
    checker = root / "scripts" / "build_sri.py"
    if not checker.exists():
        return False
    r = subprocess.run([sys.executable, str(checker), "--check"], cwd=str(root),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return False
    for line in ((r.stdout or "") + (r.stderr or "")).splitlines():
        if "CONTENT DRIFT" in line or "SRI_CHECK FAIL" in line:
            print(f"    {line.strip()[:160]}")
    return True


def unconflict_one(branch: str, dry_run: bool, push: bool) -> int:
    print(f"=== {branch} ===")

    if is_dirty():
        print("  REFUSED: working tree has uncommitted changes")
        return 1

    # A missing remote-tracking ref does not mean a missing branch. `git fetch origin`
    # honours the configured refspec, which can skip a branch pushed from another worktree,
    # so refs/remotes/origin/<b> is absent while refs/heads/<b> exists on the server.
    # Observed live 2026-09-02 on card/bank-i4070-chain-master (eb76d23e). Confirm against
    # the server before refusing.
    remote = f"origin/{branch}"
    if git("rev-parse", "--verify", "--quiet", remote, check=False).returncode != 0:
        if (git("ls-remote", "--exit-code", "--heads", "origin", branch, check=False)
                .returncode == 0):
            git("fetch", "origin", f"{branch}:refs/remotes/origin/{branch}", check=False)
        if git("rev-parse", "--verify", "--quiet", remote, check=False).returncode != 0:
            print(f"  REFUSED: {remote} does not exist (push the branch first)")
            return 1

    # A local branch may simply not exist yet: the remote-tracking ref is there but
    # refs/heads/<b> is not, and `git checkout <b>` then dies with "pathspec did not
    # match" rather than auto-creating it. Measured 2026-09-03: this was **54 of 80
    # refusals** in a full --all-mine sweep, all of them reported as "no worktree holds
    # it", which blamed worktrees for a missing local ref.
    #
    # Create it from the remote, but ONLY when it does not already exist. Never `-B`:
    # that would reset an existing local branch onto the remote and silently discard
    # local-only commits, which is exactly the stale-ref trap that nearly cost real work
    # on #3080.
    # -f on the switch. The CRLF phantoms described in is_dirty() block a plain checkout
    # with "your local changes would be overwritten" even though they are byte-identical
    # modulo line endings and no action can clear them. is_dirty() is the gate that
    # protects real work; once it has passed, there is nothing here to lose, so forcing
    # the switch is safe by construction rather than by hope.
    if git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}",
           check=False).returncode != 0:
        # No --track: some remote refs here were created by an explicit fetch refspec and
        # git reports "starting point 'origin/<b>' is not a branch", refusing to set up
        # tracking. The branch only needs to exist at the right commit -- the push path
        # names the remote explicitly and does not rely on upstream config.
        if git("checkout", "-f", "-q", "-b", branch, remote,
               check=False).returncode == 0:
            print(f"  created local {branch} from {remote}")
    else:
        git("checkout", "-f", "-q", branch, check=False)

    if out("rev-parse", "--abbrev-ref", "HEAD") != branch:
        held = worktree_of(branch)
        if held and Path(held).is_dir():
            global _CWD
            prev = _CWD
            _CWD = held
            print(f"  delegating to the worktree holding it: {held}")
            try:
                if is_dirty():
                    print("  REFUSED: that worktree has uncommitted changes")
                    return 1
                return _unconflict_here(branch, dry_run, push)
            finally:
                _CWD = prev
        if is_dirty():
            print(f"  REFUSED: cannot check out {branch} -- this worktree has "
                  f"uncommitted changes")
        else:
            print(f"  REFUSED: could not check out {branch} (no worktree holds it, "
                  f"and creating it from {remote} failed)")
        return 1

    return _unconflict_here(branch, dry_run, push)


def _unconflict_here(branch: str, dry_run: bool, push: bool) -> int:
    """The merge/resolve/regen/push body, run in whichever tree holds the branch."""
    remote = f"origin/{branch}"
    # Local copies go stale constantly in a multi-worktree fleet, so the remote tip is
    # normally the source of truth. But "local is ahead" has two very different causes and
    # only one of them is dangerous:
    #
    #   ahead>0, behind==0  local simply has not been pushed (remote is an ancestor).
    #                       Resetting here would DISCARD that work. Keep local, push it.
    #   ahead>0, behind>0   genuine divergence -- someone rewrote the branch under us.
    #                       Refuse; a human has to decide which history survives.
    #   ahead==0            local is stale or equal; take the remote tip.
    #
    # Observed live 2026-09-02: a branch pushed at b56d8e7f later read origin at 3782a1e2,
    # an ancestor of it. An unconditional refusal on ahead>0 stalls on that case, and an
    # unconditional reset would have thrown the merge away.
    ahead = int(out("rev-list", "--count", f"{remote}..HEAD"))
    behind = int(out("rev-list", "--count", f"HEAD..{remote}"))
    if ahead and behind:
        print(f"  REFUSED: diverged from {remote} (+{ahead}/-{behind}); resolve by hand")
        return 1
    if ahead:
        print(f"  local is {ahead} commit(s) ahead and not diverged; keeping local")
    else:
        _checked(["git", "reset", "--hard", "-q", remote])

    if out("rev-list", "--count", "origin/main..HEAD") and not out(
        "rev-list", "--count", "HEAD..origin/main"
    ).strip("0"):
        print("  already up to date with main")
        # THIS IS THE RETRY PATH AFTER A GENERATOR FAILURE, and it used to return here.
        # The merge resolution is committed before the generators run, so a failed
        # generator leaves a branch that already contains main; the next invocation lands
        # exactly here and reported success while the layer was never rebuilt. Reproduced
        # by ASTRA on #3511.
        #
        # Regenerating here does NOT reset CI for nothing: the generators are idempotent,
        # so an up-to-date layer produces no diff, no commit and no new SHA. Only a branch
        # whose outputs are genuinely stale gets a commit -- and that one must also be
        # pushed, or the repair stays local and the PR keeps failing the freshness gate,
        # which is the stranded-work defect recorded above.
        if dry_run:
            return 0
        head_before = out("rev-parse", "HEAD")
        if regenerate_and_commit() != 0:
            return 1
        if out("rev-parse", "HEAD") == head_before:
            return 0
        if not push:
            print("  --no-push: regenerated locally, not pushing")
            return 0
        if git("push", "origin", branch, check=False).returncode != 0:
            print("  PUSH FAILED after regeneration; re-run once the remote settles")
            return 1
        print(f"  PUSHED {out('rev-parse', '--short', 'HEAD')}")
        return 0

    if dry_run:
        # THE DRY-RUN MUST PREDICT THE LIVE DECISION.
        #
        # This used to count "<<<<<<<" hunks and return 0 for every branch, so it reported
        # "6/6 branch(es) clear; 0 refused" for a set the live run then REFUSED 5 of --
        # their conflicts were in IMPROVEMENT-INVENTORY.md, ATTEMPTS-LEDGER.md and
        # knowledge-register/PLAN.md, which are CONTENT and belong to their owners.
        # A dry-run that cannot predict a refusal is worse than no dry-run: it invites a
        # seat to promise a queue-wide sweep it cannot deliver, and the hunk count it
        # printed was not wrong, merely irrelevant to the decision the tool actually makes.
        # Found 2026-09-03 sweeping six stale branches; the tool is mine and so is the defect.
        #
        # Classify exactly as the live path does, against the same GENERATED tuple.
        paths = _conflicted_paths_dry()
        if paths is None:
            mb = out("merge-base", "HEAD", "origin/main")
            r = git("merge-tree", mb, "HEAD", "origin/main", check=False)
            n = (r.stdout or "").count("<<<<<<<")
            print(f"  DRY-RUN: {n} conflict hunk(s); CANNOT classify on this git "
                  f"(needs merge-tree --write-tree --name-only, git >= 2.38)")
            return 0
        if not paths:
            print("  DRY-RUN: merges clean, nothing to do")
            return 0
        unexpected = [p for p in paths if p not in GENERATED]
        if unexpected:
            print("  DRY-RUN: WOULD REFUSE -- real content conflict:")
            for p in unexpected:
                print(f"    {p}")
            return 1
        print(f"  DRY-RUN: would resolve {len(paths)} generated-inventory conflict(s)")
        return 0

    # ONLY TOUCH BRANCHES THAT ACTUALLY CONFLICT.
    #
    # This used to merge main into every branch that was merely BEHIND it, then regen
    # inventories, commit and push. For a branch that would have merged cleanly on its own
    # that is pure harm: it creates a new head SHA, which restarts CI, which destroys any
    # green the branch was holding. Run after every merge across ~120 branches, no PR at
    # the front of the merge order ever holds a green long enough to be merged -- the
    # sweep starves the queue it exists to help. Diagnosed by STRATEGIST 2026-09-03; the
    # tool is mine and so is the defect.
    #
    # A branch that is behind but mergeable needs nothing from us: GitHub merges it fine.
    # Probe first, and skip untouched when there is no conflict.
    _mb = out("merge-base", "HEAD", "origin/main")
    _probe = git("merge-tree", _mb, "HEAD", "origin/main", check=False)
    if (_probe.stdout or "").count("<<<<<<<") == 0:
        # HEAD merges clean -- but GitHub evaluates the REMOTE ref, not this tree.
        #
        # The original skip (#3248) returned here unconditionally, and that stranded
        # work: an earlier sweep merges main into the LOCAL branch, the skip fires on
        # the now-clean local state, and the resolution is never pushed -- while
        # GitHub keeps reporting CONFLICTING, because the remote genuinely still is.
        #
        # Measured 2026-09-03 on this seat: card/compute-watch-master was 8 commits
        # ahead of its remote with 0 local conflict hunks and 15 on the remote.
        # PRs sat CONFLICTING for several ticks with the fix already in the worktree.
        #
        # So "merges clean" only justifies skipping when there is also nothing to
        # deliver. If local is ahead, pushing is not resetting CI for nothing -- it
        # publishes a resolution that already exists.
        _ahead = 0
        if git("rev-parse", "--verify", "--quiet", remote, check=False).returncode == 0:
            _c = git("rev-list", "--count", f"{remote}..HEAD", check=False)
            try:
                _ahead = int((_c.stdout or "0").strip() or 0)
            except ValueError:
                _ahead = 0
        if _ahead == 0:
            print("  behind main but MERGES CLEAN and nothing local to push -- "
                  "skipped, not touched (pushing would reset its CI for nothing)")
            return 0
        if dry_run:
            print(f"  DRY-RUN: merges clean but local is {_ahead} commit(s) ahead of "
                  f"{remote}; would push the existing resolution")
            return 0
        print(f"  MERGES CLEAN locally but local is {_ahead} commit(s) ahead of "
              f"{remote}, which is what GitHub reads -- pushing existing resolution")
        # REGENERATE BEFORE PUBLISHING, even though there was no conflict to resolve.
        # This is the retry path after a generator failure: the merge is already
        # committed, so the probe above finds no conflict and lands here. Without this
        # call the tool would push the unregenerated layer and report success, which is
        # exactly the defect ASTRA reproduced on #3511. It is also correct in general --
        # a branch ahead of its remote with stale generated files should not publish them.
        if regenerate_and_commit() != 0:
            return 1
        if not push:
            print("  --no-push: not pushing")
            return 0
        if git("push", "origin", branch, check=False).returncode != 0:
            print("  REFUSED: push rejected; remote moved, re-run to merge it first")
            return 1
        print(f"  PUSHED {out('rev-parse', '--short', 'HEAD')}")
        return 0

    # Captured BEFORE the merge so a failed repair can be undone exactly. Everything
    # created past this point in this run is the tool's own work and is reproducible by
    # re-running, so rolling back to it destroys nothing a caller authored.
    pre_merge = out("rev-parse", "HEAD")

    git("merge", "origin/main", "--no-edit", check=False)
    conflicts = conflicted_paths()

    if conflicts:
        unexpected = [p for p in conflicts if p not in GENERATED]
        if unexpected:
            print("  REFUSED: real content conflict, not resolving:")
            for p in unexpected:
                print(f"    {p}")
            git("merge", "--abort", check=False)
            return 1
        _checked(["git", "checkout", "--theirs", *conflicts])
        _checked(["git", "add", *conflicts])
        # COMMIT THE MERGE BEFORE REGENERATING. This reverses the ordering introduced to
        # make the failure path retryable, because that ordering produced a worse defect,
        # found by ASTRA on #3514: the generators are HISTORY-DERIVED. build_sri.py's
        # first_adds() walks `git log --diff-filter=A` over HEAD, and registers/TIMELINE.md
        # is built from that walk. With the merge staged but uncommitted, HEAD does not
        # contain the merged commits, so the walk sees the wrong history and the register
        # is rebuilt stale -- while the tool reported success.
        #
        # Recoverability is preserved by the other half instead: the "already up to date"
        # and "merges clean but ahead" paths regenerate before publishing, so a run that
        # dies after this commit self-heals on the next invocation rather than inheriting
        # a completed-looking merge. That is what makes committing here safe.
        _checked(["git", "commit", "-q", "--no-edit"])
        print(f"  resolved {len(conflicts)} generated-file conflict(s) with main's copy; "
              "merge committed so the history-derived generators see it")

    if regenerate_and_commit() != 0:
        # ROLL BACK TO THE PRE-MERGE COMMIT. Two review findings pull in opposite
        # directions and both are right: the merge must be COMMITTED before regenerating,
        # or the history-derived generators read a history without it (ASTRA, #3514); and
        # a failed repair must leave nothing committed, or the next run mistakes the merge
        # for completed work (SKYNET-CODEX, b1550f209a). Committing and then undoing on
        # failure satisfies both, and leaves the branch byte-identical to how it arrived.
        #
        # --hard is safe HERE and only here: the sweep refuses to start on a dirty tree,
        # and `pre_merge` was read moments ago in this same call, so everything discarded
        # was created by this run.
        if out("rev-parse", "HEAD") != pre_merge:
            git("merge", "--abort", check=False)
            git("reset", "--hard", "-q", pre_merge, check=False)
            print(f"  rolled back to {pre_merge[:10]}; branch is unchanged by this run")
        return 1

    if push:
        r = git("push", "-q", "origin", branch, check=False)
        if r.returncode != 0:
            print(f"  PUSH FAILED: {r.stderr.strip().splitlines()[-1] if r.stderr else '?'}")
            return 1
        print(f"  PUSHED {out('rev-parse', '--short', 'HEAD')}")
    return 0


SELF_REL = "scripts/unconflict.py"


def _warn_if_self_is_stale() -> None:
    """Warn when the copy being executed is not main's copy of this script.

    This tool is normally run from whatever worktree the seat is standing in, and that
    worktree sits on a FEATURE BRANCH. A branch cut before a fix to this file carries the
    pre-fix tool, and the seat then runs an old version against the whole queue without
    noticing.

    Observed for real 2026-09-03: a branch cut before the merge-clean skip (#3248) was 19
    lines behind, and a sweep launched from it refused all 14 branches. The refusals read
    as a repository problem and cost a full diagnostic detour before the cause turned out
    to be the tool itself.

    WARN, do not refuse. Refusing would block the one legitimate case -- editing this
    script on its own card branch, where differing from main is the entire point.
    """
    head_blob = git("rev-parse", f"HEAD:{SELF_REL}", check=False)
    main_blob = git("rev-parse", f"origin/main:{SELF_REL}", check=False)
    if head_blob.returncode or main_blob.returncode:
        return
    if (head_blob.stdout or "").strip() == (main_blob.stdout or "").strip():
        return
    branch = out("rev-parse", "--abbrev-ref", "HEAD")
    print(f"  NOTE: {SELF_REL} on '{branch}' differs from origin/main's copy.")
    print("        If you are not deliberately editing this script, you may be running a")
    print("        STALE version -- a branch cut before a fix carries the pre-fix tool.")
    print("        To run main's copy instead:")
    print(f"          git show origin/main:{SELF_REL} > unconflict_main.py")
    print("          python unconflict_main.py <args>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--branch", action="append", default=[], help="branch to unconflict (repeatable)")
    ap.add_argument("--all-mine", action="store_true", help="every remote card/* branch matching --suffix")
    ap.add_argument("--suffix", default="-master", help="seat suffix for --all-mine (default: -master)")
    ap.add_argument("--dry-run", action="store_true", help="report conflict counts, change nothing")
    ap.add_argument("--no-push", action="store_true", help="resolve locally but do not push")
    args = ap.parse_args()

    if not args.branch and not args.all_mine:
        ap.print_usage()
        print("give --branch or --all-mine", file=sys.stderr)
        return 2

    _checked(["git", "fetch", "origin", "--quiet"])
    _warn_if_self_is_stale()
    start = out("rev-parse", "--abbrev-ref", "HEAD")

    branches = list(args.branch)
    if args.all_mine:
        listing = out("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/card")
        for ref in listing.split("\n"):
            name = ref.replace("origin/", "", 1).strip()
            if name.endswith(args.suffix) and name not in branches:
                branches.append(name)

    # This checks out other branches in the caller's worktree. If it exits without putting
    # the original branch back, the caller is silently left somewhere else -- observed once
    # for real, stranding the worktree on a branch that lacked this very file. Restore in a
    # finally, and catch BaseException so a Ctrl-C also restores.
    refused = 0
    try:
        for b in branches:
            try:
                if unconflict_one(b, args.dry_run, push=not args.no_push):
                    refused += 1
            except RuntimeError as e:
                print(f"  ERROR: {e}")
                refused += 1
    finally:
        git("merge", "--abort", check=False)
        # Restore the TREE, not just HEAD. Switching between distant trees under
        # core.autocrlf=true leaves large numbers of files spuriously modified -- observed
        # 2026-09-03: HEAD came back correctly while 1,441 files read as modified and this
        # very script was missing from the worktree, because the tree still held the other
        # branch's content. A plain `checkout` can also be blocked by that churn.
        #
        # -f is safe HERE and only here: the sweep refuses to start on a dirty tree, so
        # anything discarded is churn this tool itself created, never a caller's work.
        git("checkout", "-f", "-q", start, check=False)
        now = out("rev-parse", "--abbrev-ref", "HEAD")
        if now != start:
            print(f"  WARNING: could not restore {start}; worktree is on {now}", file=sys.stderr)
        elif is_dirty():
            print(f"  WARNING: restored {start} but the worktree is still dirty -- "
                  f"inspect before running anything else", file=sys.stderr)

    print(f"\n{len(branches) - refused}/{len(branches)} branch(es) clear; {refused} refused")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
