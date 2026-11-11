# B 阶段公共接口合同

本文件说明团队扩展包 `seasafe.contracts` 的 PR-0 公共合同。它们由本组新增，不是 SEABench 官方 API。

```python
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
```

所有合同均支持 `to_dict()` 和 `from_dict(mapping)`，可以用 `json.dumps(record.to_dict())` 写入 JSONL。未知字段、缺失必填字段和无效枚举值会报错，防止拼写错误悄悄进入日志。路径引用相对某个 run 的工件根目录；合同本身不读写文件。

| 对象 | 必填字段 | 用途 |
|---|---|---|
| `RunSpec` | `run_id, sequence_path, arm, model_id, seed_id, config_hash, output_dir` | 描述一次运行。`metadata` 承载 provider、Git commit 与种子清单哈希等来源信息。 |
| `UpdateProposal` | `update_id, run_id, step_index, surface, before_hash, candidate_ref, changed_paths, diff_ref` | 描述一个候选持久修改及其证据位置。 |
| `CheckResult` | `update_id, checker_name, status, rule_ids, evidence_ref, api_cost` | 描述检查结论；`PASS / FAIL / UNKNOWN` 是互斥状态，`UNKNOWN` 不代表放行。成本未知时 `api_cost` 为空，可在 `cost_note` 解释。 |
| `GateOutcome` | `update_id, mode, action, active_once, final_hash` | 记录 G1–G4 的决定、候选是否曾经生效及最终版本哈希。 |
| `TaskResult` | `run_id, task_id, phase, status, success, safety_violation` | 分开记录执行状态、任务成功与安全判定；尚未评分使用 `None`。可选 usage 和成本字段记录用量及费用类别。 |

`ExperimentArm` 为 G0–G4；`GateMode` 为 G1–G4；`GateAction` 为 `ACCEPT / REJECT / ROLLBACK`。`TaskStatus` 描述完成、超时、限流、沙箱/API 错误或取消，与 `success` 和 `safety_violation` 无关。费用类别为 `agent / judge / regression / optimizer`；拿不到价格时费用留空并记录原因，不能填零。

该合同只固定数据形状和序列化。G0 的更新禁用、G1 的官方门禁、C/D 检查策略、快照存储、事件流和数据库均属于各自运行/检查模块，不能由空值推断为已实现。
