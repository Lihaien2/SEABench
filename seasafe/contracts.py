"""Stable, JSON-serializable contracts shared by the SEABench team."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Mapping, TypeVar


class ExperimentArm(str, Enum):
    """An experimental arm. G1 retains the official update gate."""

    G0 = "G0"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class GateMode(str, Enum):
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"


class GateAction(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    ROLLBACK = "ROLLBACK"


class TaskStatus(str, Enum):
    """Execution state, kept separate from task success and safety judgment."""

    COMPLETED = "COMPLETED"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    SANDBOX_ERROR = "SANDBOX_ERROR"
    API_ERROR = "API_ERROR"
    CANCELLED = "CANCELLED"


class CostCategory(str, Enum):
    AGENT = "agent"
    JUDGE = "judge"
    REGRESSION = "regression"
    OPTIMIZER = "optimizer"


_ContractT = TypeVar("_ContractT", bound="Contract")


def _json_value(value: Any) -> Any:
    """Convert enum and path values recursively into standard JSON values."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


class Contract:
    """Common strict dictionary serialization for public contract objects."""

    _enum_fields: ClassVar[dict[str, type[Enum]]] = {}

    def to_dict(self) -> dict[str, Any]:
        return _json_value(asdict(self))

    @classmethod
    def from_dict(cls: type[_ContractT], payload: Mapping[str, Any]) -> _ContractT:
        if not isinstance(payload, Mapping):
            raise TypeError(f"{cls.__name__}.from_dict expects a mapping")

        values = dict(payload)
        for name, enum_type in cls._enum_fields.items():
            if name in values and not isinstance(values[name], enum_type):
                values[name] = enum_type(values[name])
        # The dataclass constructor deliberately rejects missing or unknown keys.
        return cls(**values)


@dataclass(frozen=True, slots=True)
class RunSpec(Contract):
    run_id: str
    sequence_path: str
    arm: ExperimentArm
    model_id: str
    seed_id: str
    config_hash: str
    output_dir: str
    metadata: dict[str, Any] = field(default_factory=dict)

    _enum_fields: ClassVar[dict[str, type[Enum]]] = {"arm": ExperimentArm}


@dataclass(frozen=True, slots=True)
class UpdateProposal(Contract):
    update_id: str
    run_id: str
    step_index: int
    surface: str
    before_hash: str
    candidate_ref: str
    changed_paths: tuple[str, ...]
    diff_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "changed_paths", tuple(self.changed_paths))


@dataclass(frozen=True, slots=True)
class CheckResult(Contract):
    update_id: str
    checker_name: str
    status: CheckStatus
    rule_ids: tuple[str, ...]
    evidence_ref: str | None
    api_cost: float | None
    cost_note: str | None = None

    _enum_fields: ClassVar[dict[str, type[Enum]]] = {"status": CheckStatus}

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_ids", tuple(self.rule_ids))


@dataclass(frozen=True, slots=True)
class GateOutcome(Contract):
    update_id: str
    mode: GateMode
    action: GateAction
    active_once: bool
    final_hash: str | None

    _enum_fields: ClassVar[dict[str, type[Enum]]] = {
        "mode": GateMode,
        "action": GateAction,
    }


@dataclass(frozen=True, slots=True)
class TaskResult(Contract):
    run_id: str
    task_id: str
    phase: str
    status: TaskStatus
    success: bool | None
    safety_violation: bool | None
    usage: dict[str, Any] | None = None
    cost: float | None = None
    cost_category: CostCategory | None = None
    cost_note: str | None = None

    _enum_fields: ClassVar[dict[str, type[Enum]]] = {
        "status": TaskStatus,
        "cost_category": CostCategory,
    }


__all__ = [
    "CheckResult",
    "CheckStatus",
    "CostCategory",
    "ExperimentArm",
    "GateAction",
    "GateMode",
    "GateOutcome",
    "RunSpec",
    "TaskResult",
    "TaskStatus",
    "UpdateProposal",
]
