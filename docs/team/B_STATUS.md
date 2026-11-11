# 成员 B 工作状态

最近更新：2026-11-11（Asia/Shanghai）

| 项目 | 当前情况 |
|---|---|
| 阶段 | PR-0 合同已实现；正在同一分支推进离线 G0/G1 runner 与记录层，主分支恢复并行处理 |
| 当前开发分支 | `feat/b-paired-runner`，本地与远端均包含合同提交；远端分支已确认存在 |
| PR-0 基线 | 工作开始前的 `main` 为 `8772b2fc7802f1f9a2af4411218f5bde9017e55a` |
| 当前远端 `main` | `432fe2cba3bf67650c43896461d9657503afd9ec`，包含误推的 PR-0 合同提交；待恢复 PR 审阅和合并 |
| 当前 PR | [恢复 main 的 draft PR #1](https://github.com/Lihaien2/SEABench/pull/1)，分支 `revert/b-paired-runner-main-restore`，提交 `bbca3521b098adbceda4d70055ba06cfac3ff710` |
| PR-0 状态 | 合同代码已提交到远端功能分支；当前未单独开 PR。PR #1 合并后再从干净基线重建完整可审阅分支，避免 diff 隐藏首个合同提交 |
| 验证级别 | Windows Python 3.13.7：合同单测 7 项通过；`git diff --check` 通过；未运行模型、Ubuntu、完整 smoke test 或真实实验 |
| 卡点与影响 | PR #1 需要另一位组员审阅并合并；这不阻止当前分支继续实现和离线验证，但合并前不发布不完整的 PR-0 diff，也不向 `main` 推送 |
| 下一步 | 在当前分支实现 fake G0/G1 配对编排、隔离目录和 JSONL/SQLite 记录；通过 fake 集成后整理完整 PR diff |
| 负责人需要安排 | 请安排一位组员审阅并在确认后合并 [PR #1](https://github.com/Lihaien2/SEABench/pull/1)，以恢复团队约定的主分支状态 |

## PR-0 已实现范围

- 新增五个团队公共记录合同：`RunSpec`、`UpdateProposal`、`CheckResult`、`GateOutcome`、`TaskResult`。
- 定义实验组、检查状态、门控动作、任务状态和费用类别枚举；未知评分和费用保留为空值，并要求明确原因。
- 提供严格的字典/JSON 序列化与反序列化；拒绝未知字段、缺失必需字段和无效枚举。
- 添加合同字段说明和序列化测试。G0/G1 runner、事件日志、SQLite、官方适配、C/D 钩子均未开始。

## Git 协作记录

- PR-0 合同最初提交到 `feat/b-paired-runner`。由于该分支当时误跟踪 `origin/main`，一次未指定远端 refspec 的 push 将提交 `432fe2c` 推到了 `main`。
- 发现后停止向 `main` 推送，修正本地分支跟踪，并用显式 refspec 发布 `feat/b-paired-runner`。
- 为恢复 `main`，从误推提交创建普通 revert 提交 `bbca352`，并显式推送到 `revert/b-paired-runner-main-restore`。没有改写历史或 force push。
- [PR #1](https://github.com/Lihaien2/SEABench/pull/1) 已成功创建并核实为 open、draft、未合并，目标为 `main`；diff 仅撤销上述五个 B 文件。
- 仓库关闭 GitHub Issues（`has_issues=false`），所以用状态页和 PR 跟踪，不把分工代号写成实际 Issue 编号。
- GitHub 报告 `main` 未受保护；由于保护设置接口返回 403，详细规则未知。

## 验证与环境边界

- `python -m pytest -q tests/test_contracts.py`：退出码 0；7 passed（Windows Python 3.13.7）。仅验证合同数据对象和 JSON 往返。
- `git diff --check`：退出码 0；未发现已跟踪文件的空白错误。
- 未连接 Ubuntu SSH；未执行完整仓库 smoke test；未调用真实模型 API；未产生真实实验结果或费用。
- PR #1 是恢复变更，不把合同测试结果说成该恢复 PR 的测试。
- 负责人明确要求继续在 `feat/b-paired-runner` 推进，不等待 PR #1；故本分支继续开发 runner，恢复审阅保持并行。
