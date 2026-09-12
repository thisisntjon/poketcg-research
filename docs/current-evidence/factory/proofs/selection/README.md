# Seven checks of an original selection component

```text
python selection_demo.py
```

Python 3.10+ and PyTorch are required. A CPU-only PyTorch installation is sufficient; the checks create CPU tensors explicitly through the existing demo's default tensor construction. No package installation is performed by the command. No engine, card data, checkpoint, network or GPU is used.

`action_decoder.py` is an exact byte copy of the project's training-side selection component. `selection_demo.py` is the existing seven-check demonstration, also copied exactly. It verifies the decoder hash before exercising optional empty selection, minimum counts, illegal-option masking, selection without replacement, maximum counts, context-dependent STOP, and rejection of an impossible minimum. The demo prints seven passing checks and exits with status 0; an assertion or unexpected exception produces a nonzero exit. Run normally, without Python's `-O` option, because the preserved demo uses assertions.

These are prescribed-score examples, including a context-dependent score function. They demonstrate legal-selection mechanics. They do **not** test learned scores, tactical quality, the unordered-set training objective, the full inference policy, or game strength. The original demo's short docstring says “fixed scores”; this refers to prescribed test scores, not a claim that every example uses a constant score vector.

[MANIFEST.json](MANIFEST.json) supplies the source origins and exact hashes. [CHECK-RESULT.json](CHECK-RESULT.json) captures the single CPU execution on this final candidate and names its actual PyTorch version. A build with CUDA support may be installed on the verification machine; the demo itself uses CPU and performs no CUDA operation.

The decoder was implemented during Jonathan Simone's AI-assisted project. Its methods use established masking and autoregressive selection patterns; originality here concerns the project implementation, not invention of those methods. The supplied source and demo are released under [../LICENSE](../LICENSE). PyTorch remains a separately licensed dependency.
