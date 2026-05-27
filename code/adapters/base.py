"""Minimal adapter interface for paper experiments."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, MutableMapping

Batch = MutableMapping[str, Any]
Metrics = Mapping[str, float]


class BaseModelAdapter(ABC):
    """Standard interface between arbitrary model code and experiment runners."""

    adapter_name = "base"
    task_type = "unspecified"
    input_fields: list[str] = []
    target_field = ""
    primary_metric = ""

    @abstractmethod
    def build_model(self) -> Any:
        """Construct and return the project model."""

    @abstractmethod
    def prepare_batch(self, raw_batch: Batch) -> Batch:
        """Convert one raw batch to model-ready inputs."""

    @abstractmethod
    def forward(self, model: Any, batch: Batch) -> Any:
        """Run model inference for one batch."""

    @abstractmethod
    def compute_loss(self, model_output: Any, batch: Batch) -> Any:
        """Compute a real training loss."""

    @abstractmethod
    def compute_metrics(self, model_output: Any, batch: Batch) -> Metrics:
        """Compute real evaluation metrics."""
