# Two small checks behind the writeup

From this `proofs` directory, run:

```text
python representation/verify.py
python selection/selection_demo.py
```

The first command needs only Python 3.10+ and the standard library. It verifies the retained files' SHA-256 hashes and recalculates the reported **48.62% → 74.25%** and **47.33% → 77.26%** mean validation agreement from twelve historical run rows across two caches. It does not retrain the models or reconstruct the original validation sets.

The second command also needs PyTorch installed. It runs seven generic checks on CPU against the exact project-authored training-side decoder. It loads no trained model, game engine or card data and uses no network or GPU. One case changes prescribed scores after a selection; another checks rejection of an impossible minimum. These demonstrate component behavior, not strategic quality. Each directory includes the output captured from the public candidate's verification run.

- [Representation result and limits](representation/README.md)
- [Selection component and limits](selection/README.md)
- [Why the later hash-v1 design was replaced](learning-design/README.md)
- [Original components and design reasoning](ORIGINAL-COMPONENTS.md)

The Python code supplied here is released under the [MIT license](LICENSE). PyTorch is a separate dependency under its own license. The JSON receipts contain project-generated aggregate experiment records; they do not include game records, hidden state, card data, teacher implementations, or trained weights. Their original local paths identify historical provenance and are not required to run these checks.
