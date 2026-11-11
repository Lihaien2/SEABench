import json

import pytest

from seasafe.contracts import (
    CheckResult,
    CheckStatus,
    CostCategory,
    ExperimentArm,
    GateAction,
    GateMode,
    GateOutcome,
    RunSpec,
    TaskResult,
    TaskStatus,
    UpdateProposal,
)


@pytest.mark.parametrize(
    "contract",
    [
        RunSpec(
            run_id="run-1",
            sequence_path="tasks/example.yaml",
            arm=ExperimentArm.G0,
            model_id="fake/model",
            seed_id="seed-1",
            config_hash="config-hash",
            output_dir="artifacts/run-1",
            metadata={
                "pair_id": "pair-1",
                "provider": "fake",
                "git_commit": "abc123",
                "seed_manifest_hash": "seed-hash",
                "requested_surface": "controller_update",
            },
        ),
        UpdateProposal(
            update_id="update-1",
            run_id="run-1",
            step_index=2,
            surface="controller_update",
            before_hash="before",
            candidate_ref="snapshots/candidate",
            changed_paths=["AGENTS.md"],
            diff_ref="diffs/update-1.diff",
        ),
        CheckResult(
            update_id="update-1",
            checker_name="static",
            status=CheckStatus.UNKNOWN,
            rule_ids=["I1"],
            evidence_ref=None,
            api_cost=None,
            cost_note="checker not configured",
        ),
        GateOutcome(
            update_id="update-1",
            mode=GateMode.G4,
            action=GateAction.ROLLBACK,
            active_once=True,
            final_hash="restored-parent",
        ),
        TaskResult(
            run_id="run-1",
            task_id="task-1",
            phase="downstream",
            status=TaskStatus.COMPLETED,
            success=False,
            safety_violation=None,
            effective_surface="none",
            usage={"prompt_tokens": 12, "completion_tokens": 4},
            cost=None,
            cost_category=CostCategory.AGENT,
            cost_note="provider did not return pricing",
        ),
    ],
)
def test_contract_json_round_trip(contract):
    restored = type(contract).from_dict(json.loads(json.dumps(contract.to_dict())))

    assert restored == contract
    assert restored.to_dict() == contract.to_dict()


def test_unknown_check_and_unscored_task_remain_explicit():
    check = CheckResult.from_dict(
        {
            "update_id": "update-2",
            "checker_name": "behavior",
            "status": "UNKNOWN",
            "rule_ids": [],
            "evidence_ref": None,
            "api_cost": None,
        }
    )
    task = TaskResult.from_dict(
        {
            "run_id": "run-1",
            "task_id": "task-2",
            "phase": "downstream",
            "status": "COMPLETED",
            "success": None,
            "safety_violation": None,
        }
    )

    assert check.status is CheckStatus.UNKNOWN
    assert task.success is None
    assert task.safety_violation is None


def test_from_dict_rejects_missing_fields_unknown_fields_and_invalid_enums():
    with pytest.raises(TypeError):
        RunSpec.from_dict({"run_id": "incomplete"})

    with pytest.raises(TypeError):
        RunSpec.from_dict(
            {
                "run_id": "run-1",
                "sequence_path": "tasks/example.yaml",
                "arm": "G0",
                "model_id": "fake/model",
                "seed_id": "seed-1",
                "config_hash": "config-hash",
                "output_dir": "artifacts/run-1",
                "unexpected": True,
            }
        )

    with pytest.raises(ValueError):
        RunSpec.from_dict(
            {
                "run_id": "run-1",
                "sequence_path": "tasks/example.yaml",
                "arm": "G9",
                "model_id": "fake/model",
                "seed_id": "seed-1",
                "config_hash": "config-hash",
                "output_dir": "artifacts/run-1",
            }
        )
