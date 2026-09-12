"""Semantic-menu encoding and legal without-replacement selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import torch


class SelectionError(ValueError):
    """The declared selection bounds or legal menu cannot be satisfied."""


@dataclass(frozen=True)
class EncodedMenu:
    numeric: torch.Tensor
    kinds: torch.Tensor
    semantic_keys: tuple[str, ...]
    source_indices: tuple[int, ...]


@dataclass(frozen=True)
class SelectionResult:
    relative_indices: tuple[int, ...]
    stopped: bool
    log_prob: torch.Tensor


def encode_menu(options: Sequence[Mapping[str, object]], *, numeric_dim: int) -> EncodedMenu:
    """Encode semantic fields while retaining source indices only as output mapping."""
    if numeric_dim <= 0:
        raise SelectionError("numeric_dim must be positive")
    numeric: list[list[float]] = []
    kinds: list[int] = []
    semantic_keys: list[str] = []
    source_indices: list[int] = []
    for option in options:
        features = option.get("features")
        if not isinstance(features, Sequence) or isinstance(features, (str, bytes)):
            raise SelectionError("option features must be a numeric sequence")
        if len(features) != numeric_dim:
            raise SelectionError(f"option features must have length {numeric_dim}")
        try:
            row = [float(value) for value in features]
            kind = int(option["kind"])
            source_index = int(option["source_index"])
            semantic_key = str(option["semantic_key"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SelectionError("invalid semantic option") from exc
        tensor_row = torch.tensor(row, dtype=torch.float32)
        if not torch.isfinite(tensor_row).all():
            raise SelectionError("option features must be finite")
        if kind < 0 or source_index < 0 or not semantic_key:
            raise SelectionError("kind, source_index, and semantic_key must be valid")
        numeric.append(row)
        kinds.append(kind)
        semantic_keys.append(semantic_key)
        source_indices.append(source_index)
    return EncodedMenu(
        numeric=torch.tensor(numeric, dtype=torch.float32).reshape(len(options), numeric_dim),
        kinds=torch.tensor(kinds, dtype=torch.long),
        semantic_keys=tuple(semantic_keys),
        source_indices=tuple(source_indices),
    )


def decode_selection(
    score_fn: Callable[[tuple[int, ...]], torch.Tensor],
    *,
    legal_mask: torch.Tensor,
    min_count: int,
    max_count: int,
    sample: bool = False,
    generator: torch.Generator | None = None,
) -> SelectionResult:
    """Decode options plus learned STOP under exact min/max and legality constraints."""
    if legal_mask.ndim != 1 or legal_mask.dtype is not torch.bool:
        raise SelectionError("legal_mask must be a rank-1 bool tensor")
    option_count = legal_mask.numel()
    if not 0 <= min_count <= max_count <= option_count:
        raise SelectionError("selection bounds must satisfy 0 <= min <= max <= menu size")
    selected: list[int] = []
    log_prob = torch.zeros((), dtype=torch.float32, device=legal_mask.device)
    while len(selected) < max_count:
        logits = score_fn(tuple(selected))
        if logits.ndim != 1 or logits.numel() != option_count + 1:
            raise SelectionError("score_fn must return one logit per option plus STOP")
        logits = logits.to(device=legal_mask.device)
        allowed = legal_mask.clone()
        if selected:
            allowed[torch.tensor(selected, device=allowed.device)] = False
        allowed = torch.cat(
            [allowed, torch.tensor([len(selected) >= min_count], dtype=torch.bool, device=allowed.device)]
        )
        if not allowed.any():
            raise SelectionError("no legal selection can satisfy min_count")
        if not torch.isfinite(logits[allowed]).all():
            raise SelectionError("available selection logits must be finite")
        masked = logits.masked_fill(~allowed, -torch.inf)
        distribution = torch.distributions.Categorical(logits=masked)
        choice = (
            int(torch.multinomial(torch.softmax(masked, dim=0), 1, generator=generator).item())
            if sample
            else int(masked.argmax().item())
        )
        log_prob = log_prob + distribution.log_prob(torch.tensor(choice, device=masked.device))
        if choice == option_count:
            return SelectionResult(tuple(selected), True, log_prob)
        selected.append(choice)
    return SelectionResult(tuple(selected), True, log_prob)


def map_to_source(selection: SelectionResult, menu: EncodedMenu) -> tuple[int, ...]:
    return tuple(menu.source_indices[index] for index in selection.relative_indices)
