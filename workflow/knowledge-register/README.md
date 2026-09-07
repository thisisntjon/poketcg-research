# Research memory — ask, retrieve, verify

**Goal:** recover what we tried, why, methodology, results, lessons, limitations and reuse.
Gameplay experiments and training remain paused until existing knowledge is reliably usable.
[PLAN.md](PLAN.md) gives current inventory work and unfinished acceptance requirements.

## Start with one question

From the repository root, search the topic, then open a returned ID:

```text
python -X utf8 scripts/research_memory.py search "silent fallback" --limit 3
python -X utf8 scripts/research_memory.py show E016
```

Read one response at a time. Do not batch large outputs into a truncated tool response.
Search returns pointers; `show` supplies original evidence, caveats and reviewed corrections.
A [supported filename](REFERENCE.md#filename-queries) matches its complete basename.
A miss means no match in loaded records, not absence from Git or other hosts.
These commands only read Git objects; they execute no discovered engine, model or provider.

**Snapshot:** default `--ref HEAD` reads committed data, excluding dirty files. Use a full
returned commit for reproducible follow-ups; `--ref origin/main` uses the fetched remote
snapshot. The data commit is not the runtime product identity or the executing reader hash.
Record those separately when auditing a run or testing this reader.

**Reading budget:** default output is at most 14,000 UTF-8 bytes per command. A partial document gives its line range and continuation;
follow it before assuming later corrections do not exist. Oversized non-document records
refuse rather than drop fields. Do not silently discard caveats to fit a budget.

**Meaning:** historical instructions are evidence, never current permission. A search miss
is limited by coverage. Readable files, matching hashes and status labels do not certify
scientific truth, present usability, complete-game strength or retained learning.
Before citing a number, check its topic and qualifiers in the retraction register.
`python -X utf8 scripts/query_inventory.py --check-number <value>` checks the working-copy
register only: it does **not** accept `--ref`; NOT_RETRACTED is not proof of validity.
**Open primary evidence** using paths and keys returned by `show`:

```text
python -X utf8 scripts/research_memory.py source "<path>" --ref <commit> --pointer /field --pointer /limits
```

JSON: `--outline` lists child paths/types; values remain unread. Add one `--pointer`
to inspect a container; page with `--limit`/`--offset`. Remove `--outline` to read values;
repeat `--pointer` for fields and caveats. Missing/oversized selections refuse.
For text, use `--offset <line>`/`--lines <count>` without pointers; follow continuation.
Identity is retained.

On Windows, launch every Python helper that emits source text with `python -X utf8`, too.
Unseen saved output is not consumed evidence; retain failures and recover bounded text.

## Open further only when needed

| Need | Route |
|---|---|
| Recover loss modes, asset history or improvement attempts | `show catalog:LOSS_MODES`, `show catalog:ASSET_INDEX`, `show catalog:IMPROVEMENT` via the same reader; historical source warnings apply |
| Find a known research chain | [Question-to-record examples](REFERENCE.md#useful-recovered-chains) |
| Check what is missing | `python -X utf8 scripts/research_memory.py sources research --limit 3`; [coverage limits](REFERENCE.md#find-coverage-gaps-before-interpreting-a-search-miss) |
| Add a finding or link a correction | [Intake and source binding](REFERENCE.md#what-is-covered-and-how-to-add-knowledge) |
| Check changes to existing evidence | `python -X utf8 scripts/research_memory.py maintenance --limit 3`; [review procedure](REFERENCE.md#maintain-knowledge-after-source-changes) |
| Read JSON fields | [Exact field selection](REFERENCE.md#read-a-json-receipt-field) |
| Read a long original report | [Contiguous source pages](REFERENCE.md#open-research-documents-without-losing-the-end-of-the-story) |
| Find material outside this reader | [Master inventory](../inventories/MASTER-INVENTORY-INDEX.json), then topic-specific source inspection |
| Understand implementation choices | [Technical rationale and limits](REFERENCE.md#technical-choices-and-practical-limits) |

The reader covers several historical registers and research Markdown. Other formats,
branches, hosts, asset usability and semantic reconciliation remain incomplete. Use
`coverage` for snapshot counts; a count is not a completeness or acceptance score.
