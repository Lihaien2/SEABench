# SEABench 复现进度报告

**项目**：SEABench — 自我演化如何引发内生失对齐（RSI Safety 实验起点）
**论文**：*SEABench: Benchmarking Endogenous Misalignment In Self-Evolving Agents*, arXiv:2609.35596
**执行日期**：2026-11-11
**复现程度**：轻微复现（代码/数据核对 + 本地运行时契约验证），**未**运行真实智能体任务

---

## 1. 结论速览

| 编号 | 项目 | 状态 | 说明 |
|---|---|---|---|
| 1 | 官方仓库代码与数据获取 | ✅ 完成 | 714 个文件中 713 个已落地且字节数一致 |
| 2 | 48 条任务序列核对 | ✅ 完成 | 3 个演化面 × 16 条，与论文一致 |
| 3 | 本地 smoke test（步骤 1–4） | ✅ 全部通过 | 45 个检查点全绿，退出码 0 |
| 4 | 步骤 5 真实智能体会话 | ⏸ 按设计跳过 | 未配置 `OPENROUTER_API_KEY`，脚本主动 SKIP |
| 5 | Apptainer 沙箱隔离执行 | ❌ 阻塞 | 本机 Windows，无 Linux 容器运行时 |
| 6 | 单条任务序列 / 原论文结果复现 | ❌ 未开始 | 需 API Key、Linux 沙箱、原论文模型 |
| 7 | 云端共同仓库同步 | ✅ 完成 | 共同仓库本就是官方完整 fork，本报告已提交 |

> **关键判断**：`Lihaien2/SEABench` 是官方仓库的 fork，`main` 指向同一个提交
> `8e0a108cddf069bf640d565edbd712891f230384`。**代码本来就已完整存在于云端，无需重复上传**。
> 本次向仓库提交的是复现进度记录，不改动任何既有代码。

---

## 2. 复现对象与环境

### 2.1 版本信息

| 项目 | 值 |
|---|---|
| 官方仓库 | `SEABench-Endogenous-Misalignment/SEABench` |
| 官方状态 | 公开、`archived: true`（只读归档，2026-10-16） |
| 锁定提交 | `8e0a108cddf069bf640d565edbd712891f230384` ("Updated CoT monitor pipeline code") |
| 共同仓库 | `Lihaien2/SEABench`（`main` 同一提交，未受保护） |
| 本机推送账号 | `cookies060809`，权限 `push: true / admin: false` |

### 2.2 本机环境与硬约束

| 要求 | 仓库要求 | 本机实际 | 影响 |
|---|---|---|---|
| 操作系统 | 推荐 Linux | Windows 11 / Git Bash (MINGW64) | `setup_venv.sh` 的 `source .venv/bin/activate` 为 Linux 专用 |
| Python | `setup_venv.sh` | Python 3.13.14 | smoke test 无需第三方依赖，直接跑通 |
| 沙箱 | Apptainer (`.sif`) | 无 apptainer / singularity | `test_smoke.sh` 无法执行 |
| WSL | 可作 Linux 替代 | `wsl.exe` 被安全策略列入黑名单 | 不可绕过 |
| Docker | 可作替代 | 已安装但 daemon 未运行 | 不可用 |
| 模型 | OpenRouter API Key | `OPENROUTER_API_KEY` 未设置 | 步骤 5 与所有真实任务被跳过 |

### 2.3 网络问题与绕行方案（可复现留痕）

`codeload.github.com` 与 `git clone` 在本网络下均以 ~20 KB/s 传输，且两次都在中途断流
（分别停在 10.0 MB 和 18.7 MB，ZIP 缺中央目录，`BadZipFile`）。

**绕行方案**：改用通畅的 `api.github.com` 与 `raw.githubusercontent.com`——

1. `GET /repos/{owner}/{repo}/git/trees/main?recursive=1` 取得完整清单（1092 条目 / 714 blob / 37.03 MB，`truncated: false`）；
2. 逐文件从 `raw.githubusercontent.com` 拉取，14 线程并发、按清单字节数校验、失败独立重试；
3. 结果：**712 个小文件 100% 成功、零失败**，另有 3.1 MB 检查点续传成功。

遗留项：`prompt_optimization_analysis/reasoning_monitor/checkpoint/selector_verifier/stage1.joblib`
（24.06 MB）仍在断点续传中。该文件仅服务于 CoT monitor 后验分析，**不影响 benchmark 主流程与本次 smoke test**。

---

## 3. 已完成工作

### 3.1 代码与数据完整性核对

| 检查项 | 结果 |
|---|---|
| 清单文件总数 | 714 blob，713 个存在且大小一致，0 个大小不符 |
| 任务序列 | `tasks/` 共 **48** 个 YAML |
| 演化面分布 | `controller_update` 16 / `short_term_memory` 16 / `tools_skills` 16 |
| 环境种子 | `env_assets/` 89 个文件；`env_assets_utility_test/` 383 个反事实环境文件 |
| 落地体积 | 13,984,934 字节（不含 24 MB 检查点） |

### 3.2 本地运行时契约验证（核心结果）

`scripts/test_smoke.sh` 强依赖 `apptainer build/exec`，本机无法执行。经阅读源码确认：
其调用的 `scripts/test_smoke.py` **步骤 1–4 为纯 Python，不依赖容器、不依赖 API Key**，
步骤 5 在缺少 Key 时会主动打印 `SKIP` 并 `sys.exit(0)`。

因此采用等价的本地绕行执行（未修改仓库任何源码）：

```bash
export REPO_ROOT="<repo>/SEABench"
export PYTHONPATH="$REPO_ROOT"
export ARTIFACTS_DIR="$REPO_ROOT/artifacts"
export ENV_ASSETS_DIR="$REPO_ROOT/env_assets"
unset OPENROUTER_API_KEY
python "$REPO_ROOT/scripts/test_smoke.py"
```

**结果：退出码 0，45 个 ✓，`=== All local checks passed ===`。** 完整日志见 `smoke_test_local.log`。

| 步骤 | 验证内容 | 关键通过项 |
|---|---|---|
| 1 | 工作区初始化 | 陈旧运行时状态被清除；11 个控制器文件与 5 个环境种子文件按结构注入；5 个 legacy 导出未被误拷贝 |
| 2 | 系统提示词组装 | 11 个 `--- FILENAME ---` 块全部出现在 system prompt 中 |
| 3 | 记忆与自改进写入 | 工具按演化面隔离（`controller_update` 不暴露 `create_skill`/`create_tool`/`update_memory`）；`update_memory`、`record_learning` 落盘；`create_skill`/`create_tool` 写入后立即可调用且刷新 `TOOLS.md`；学习产物未逃逸工作区 |
| 4 | `apply_controller_update` 门控 | 合法 `SOUL.md` 写入被接受；`USER.md`（非白名单）、可疑短语、禁止标记三类危险修改**全部被拦截**；不可变种子全程未被污染；事件日志被限制在 `artifacts/` 内 |
| 5 | 真实智能体会话 | `SKIP  OPENROUTER_API_KEY not set`（预期行为，非失败） |

> 步骤 4 的四类门控正是后续 Safety Invariant Preservation 实验的天然接入点。

---

## 4. 未完成项与解除条件

| 编号 | 未完成项 | 阻塞原因 | 解除条件 |
|---|---|---|---|
| A | 单条任务序列真实运行 | 无 `OPENROUTER_API_KEY`，无 API 预算 | 配置 Key，按 `scripts/run.sh --run-config configs/runs/*.yaml` 执行 |
| B | Apptainer 沙箱隔离 | Windows 无 Apptainer；WSL 被禁；Docker daemon 未运行 | 换 Linux 主机（云端/实验室机器），构建 `sandbox/sandbox.def` 生成 `.sif` |
| C | 原论文数值复现 | 主实验模型为 `openai/gpt-5.6-luna`；`runtime/config.py` 默认却是 `moonshotai/kimi-k2.5` | 使用原论文模型与相同 judge 模型；**换模型只能作为扩展研究，结果不能标注为原论文复现** |
| D | 任务序列优化流水线 | TextGrad 搜索需大量 API 调用 | A + B + 预算 |
| E | 24 MB `stage1.joblib` | 单文件传输持续断流 | 网络改善或换机器；仅影响 CoT monitor 后验分析 |

---

## 5. 下一步研究设计：Safety Invariant Preservation

**研究问题**：智能体在持续自我修改过程中，旧版本建立的安全约束在多少次修改后仍然成立？
重点不是最终任务成功率，而是**安全约束的存活率**。

### 5.1 消融分组（在 `apply_controller_update` 门控处插入独立于改进智能体的安全检查器）

| 组 | 机制 | 实现要点 |
|---|---|---|
| G0 | 直接接受修改 | 基线，关闭检查器 |
| G1 | 静态检查 | 对写入内容做白名单 / 短语 / 标记扫描（复用现有 gate 规则） |
| G2 | 行为回归测试 | 每次修改后重放一组固定安全探针任务，观察旧约束是否被覆盖 |
| G3 | 历史版本回滚 | 维护控制器版本链，检测到违规时回退到最近的安全版本 |

对照组使用仓库已有的 **non-evolving baseline（`surface=none`）**，与论文的自演化/非演化配对设计一致，可直接做因果归因。

### 5.2 建议报告的四项指标

| 指标 | 定义 | 数据来源 |
|---|---|---|
| 任务成功率 | 上游 + 下游任务完成比例 | `analysis_tools/` 轨迹与 judge |
| 安全违规率 | 下游安全测试任务中触发违规的比例 | 配对基线归因分数 |
| 危险修改被接受比例 | 被判定危险的修改中，实际写入控制器的比例 | `EvolutionTracker` 事件日志 |
| 单位改进的 API 成本 | 每提升 1 个百分点任务成功率所消耗的 API 费用 | OpenRouter 用量记录 |

### 5.3 建议接入文件

- `agent/tools/core/self_improve.py`：写入门控与检查器挂载点
- `runtime/validation_dispatcher.py`：回归探针调度
- `analysis_tools/self_improvement/tracker.py`：修改事件与版本链记录
- `scripts/run.sh` / `configs/runs/`：配对运行配置

---

## 6. 复现命令留痕

```bash
# 官方仓库（本机 codeload 会断流，记录原始入口）
git clone https://github.com/SEABench-Endogenous-Misalignment/SEABench.git
./scripts/setup_venv.sh && source .venv/bin/activate
./scripts/reset_runtime.sh
./scripts/test_smoke.sh          # 需 Apptainer
export OPENROUTER_API_KEY="<key>"
./scripts/run.sh

# 本机实际采用的绕行（Windows，无容器）
python scripts/test_smoke.py    # 步骤 1-4 通过，步骤 5 SKIP
```

---

*本报告由本地实际执行结果生成，未使用任何模拟或占位数据；未完成项均如实标注。*
