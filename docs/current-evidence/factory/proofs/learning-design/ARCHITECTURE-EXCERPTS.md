# Bounded excerpts from the August 13 architecture

Project-authored source: `workflow/WINNING-STRATEGY-ARCHITECTURE.md`.

- Source commit: `4238c61932f970529b29133ac43842e05d656c50`, 2026-08-13.
- Full source SHA-256: `94c57e89e07c515bb9178cdef07d04fa3f2773ed695af546246fa6c56a51af42`.
- The exact closure record in this directory binds that same architecture SHA-256.
- Excerpts retain the historical text. They document decisions, not completion of the proposed future phases.

## Original lines 386–401

> ## 7. Representation path: close v1, then activate v2 if needed
>
> The semantic projector and menu builder already protect information and identity. The
> current fixed-width `FeatureEncoder` hashes arbitrary leaves into 64 state buckets and 12
> option buckets. It is a constrained prototype, not an unconstrained representation.
>
> Hash-v1 is closed as the bootstrap class: four terminal local G1 receipts failed the frozen
> behavior-fidelity gate and the fifth run failed operationally. Phase A0 banks and adjudicates
> those negatives and verifies runtime restoration; it does not send hash-v1 to the competence
> game test. Only a newly frozen representation that first passes its offline G1 may enter the
> fixed-`N` competence test. Outcome-driven repair of hash-v1 is prohibited.
>
> ### 7.1 Representation contract
>
> Create `ptcg.lf_features/v2-explicit` with four typed blocks. No value below may contain
> native menu position as an input.

## Original lines 1263–1279

> ### Phase A0 — bank the hash-v1 negative and verify executable identity
>
> **Build/fix:** real checkpoint-to-runtime integration, inference-only restore, complete
> source/treatment identity, tracked coordinator, and one end-to-end test without a fake
> runtime.
> **Done when:** all hash-v1 failure receipts are identity-bound and banked, the real restore
> path is reproducible, and hash-v1 is terminally closed without consuming the competence game
> sample. Runtime restoration does not revive a model that failed offline G1.
> **Decision:** proceed to Phase A1 with a new representation identity.
>
> ### Phase A1 — explicit representation fallback and competent bootstrap
>
> **Build:** the actor-view projector/firewall for direct-byte sources,
> `semantic_features_v2`, model wiring, rematerialized exact-deck behavior corpus, and behavior
> trainer parity. Censored fallback stores are excluded from bootstrap training until Phase A2.
> **Borrow:** DouZero explicit action/state encoding patterns; RLCard state/legal-action
> contract.
