# 成员 C 工作分支：qiqi

> 存放成员 C（修改追踪与静态安全检查负责人）的工作成果。
> 创建于 2026-11-11，基于 `main` @ `8772b2fc`。

## 与团队协作规范的差异（需组长 / 组员确认）

`00_四人GitHub协作总说明.docx` 规定：

- 成员 C 的分支名应为 `feat/c-version-static`，本分支按本人要求命名为 `qiqi`；
- `main` 只存已审核代码，任何人不得直接向 `main` 推送；
- 成员 C 的文件所有权：`seasafe/versioning/`、`seasafe/gates/static.py`、`configs/invariants/static_rules.yaml`、`tests/test_versioning_static.py`、`docs/safety/static_policy.md`。

本分支只新增 `docs/memberC/` 下的文档，**未改动任何官方文件，也未触碰其他成员负责的目录**。
提交 PR 前建议把分支改名为规范名，或在 PR 描述中说明命名原因。

## 当前内容

| 文件 | 说明 |
|---|---|
| `reproduction_progress.md` | SEABench 轻微复现进度报告（代码/数据核对 + 本地运行时契约验证） |
| `smoke_test_local.log` | 本地 smoke test 原始日志（45 个检查点全通过，步骤 5 跳过） |
| `progress_dashboard.html` | 可视化进度看板（浅色主题，可下载后本地打开） |
| `snapshot_verification.log` | 714 个文件 Git blob SHA1 逐字节校验记录（0 不符、0 缺失） |

## 已核实的事实

- 官方仓库锁定提交 `8e0a108cddf069bf640d565edbd712891f230384`；共同仓库 `main` 同一提交。
- `tasks/` 共 48 个 YAML，3 个演化面各 16 条；官方清单 714 / 714 个文件全部落地，Git blob SHA1 与官方 tree 逐一一致（含 24.06 MB CoT 检查点，已于 2026-11-11 20:07 续传完成）。
- Windows 本机绕过 Apptainer，直接执行 `scripts/test_smoke.py`：步骤 1–4 全部通过，退出码 0，45 个 ✓；步骤 5 因未配置 `OPENROUTER_API_KEY` 按设计 SKIP。
- 阻塞项：无 Apptainer（WSL 被安全策略禁用、Docker daemon 未运行）、无 `OPENROUTER_API_KEY`；原论文主实验模型为 `openai/gpt-5.6-luna`，Config 默认却是 `moonshotai/kimi-k2.5`，换模型不能标注为原论文复现。

## 成员 C 下一步（按个人执行文档 C1–C6，待 PR-0 接口冻结后实现）

1. **C1** 确认三种可写表面的真实路径：读 `agent/seeded_files/`、`docs/task_setup.md`、`tasks/` 中的 `sequence_setup`。
2. **C2** 定义候选更新生命周期字段：`update_id` / `run_id` / `step` / `surface` / `before_hash` / `candidate_hash` / `changed_paths` / `diff_ref` / `snapshot_ref`；被拒绝的候选也要留审计记录。
3. **C3** 实现 `create_snapshot` / `stage_candidate` / `commit_candidate` / `restore_snapshot`，拒绝 `..` 路径穿越与指向外部的符号链接。
4. **C4** 实现 G2 静态检查，输出 `PASS` / `FAIL` / `UNKNOWN` + 规则编号 + 证据路径；模糊语义案例不得判为确定安全。
5. **C5** 写 `configs/invariants/static_rules.yaml` 与 `tests/test_versioning_static.py`，覆盖正常更新、越权修改、路径穿越、危险链接、无效格式。
6. **C6** 向 D 提供 `create_snapshot` / `restore_snapshot` 的最小使用范例，**不实现 G3/G4 回滚策略**。

> 依赖：交给 B 的是 `capture_proposal` / 版本快照接口；交给 D 的是稳定的 `snapshot_ref`、父/候选哈希与 G2 结果格式。
> 所有「跑通」结论均附命令与退出码；本分支尚未调用任何真实付费模型 API。

## 更新记录

- 2026-11-11 20:08：24.06 MB `stage1.joblib` 续传完成；714 / 714 文件 Git blob SHA1 校验通过，报告、看板与说明中的「713 / 714」已更正。
- 注：`main` 上 `docs/reproduction_progress.md` 与 `docs/reproduction_smoke_test.log` 为按本人要求保留的旧版本，数字未同步；本分支 `docs/memberC/` 为最新。
