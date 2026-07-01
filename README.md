# Paper Explainer

> 把任意论文变成**逐格溯源、可复习**的结构化知识卡 —— 内置忠实度校验，专门标记模型「无出处 / 疑似编造」的格子。
>
> **跨 agent 通用**：Claude Code / claude.ai 走 [Agent Skill](https://agentskills.io)（`SKILL.md`），
> Codex / Cursor / Copilot 走 [`AGENTS.md`](AGENTS.md)，两者共用同一套模板和校验脚本。
> 也可当独立 CLI 离线使用。

普通「论文总结 prompt」的通病是：模型会一本正经地**编造证据来源**——给一个根本不存在的
"实验" 或 "结果" 安上煞有介事的出处，你还无从分辨。Paper Explainer 的差异点只有一个，但很关键：

**每一条结论都必须带一句逐字原文引文，而这些引文会被脚本拿回原文校验。编造的引文匹配不上，会被标红。**

## 30 秒看懂它做什么

```
论文文本 ──▶ ① 概念映射表   ──▶ ② 填 15 张表      ──▶ ③ 忠实度校验     ──▶ ④ 报告
            (先锁术语)         (每格带原文引文)      (check_sources.py)   (标记可疑格)
```

```
$ python scripts/check_sources.py --tables filled.json --source paper.txt
============================================================
FAITHFULNESS REPORT
============================================================
Claims checked : 4   (skipped/empty: 1)
L1 quote-exists: 3 ok / 1 unsupported
  ⚠ [表7 · 编造检验] no source match (best ratio 0.33)
      claim: 该方法在 ImageNet 上达到 99% top-1 准确率
      quote: our method achieves 99% top-1 accuracy on the ImageNet benchmark
------------------------------------------------------------
VERDICT: REVIEW NEEDED
```

那条 ImageNet 结论是**故意植入的假引文**，原文根本没有——校验器抓住了它。

## 快速开始

作为 Claude Skill（推荐）：把本仓库作为 plugin 安装，然后直接说
「帮我拆解这篇论文 <链接/PDF>」，Claude 会自动加载 skill 并按流程产出表格。

在 Codex / Cursor / Copilot 里：这些工具会自动读取根目录的 [`AGENTS.md`](AGENTS.md)，
拿到同一套流程，并调用同一个 `check_sources.py`。无需额外配置。

手动跑校验（无需任何 agent、离线）：

```bash
cd skills/paper-explainer/examples
python ../scripts/check_sources.py --tables claims.json --source source.txt
```

## 兼容性：一份核心，两层适配

| 工具 | 入口 | 说明 |
|---|---|---|
| Claude Code / claude.ai / Agent SDK | `skills/paper-explainer/SKILL.md` | 原生 Agent Skill 格式，含长触发描述，自动加载 |
| Codex / Cursor / Copilot / 其他 | [`AGENTS.md`](AGENTS.md)（根目录） | 跨工具标准，由 Agentic AI Foundation 维护 |
| 任何人（离线） | `scripts/check_sources.py` | 纯标准库，直接命令行跑校验 |

两个入口只是**薄适配层**，真正的资产——`reference/tables.md` 模板和
`scripts/check_sources.py` 校验器——只有一份，两边共用，不重复维护。

## 为什么这么设计（工程取舍）

这一节是本项目的核心，也是它区别于一段 prompt 的地方。

### 1. 校验分两层，按「抓什么错」划分，而不是按技术划分

| 层 | 抓的问题 | 手段 | 成本 |
|---|---|---|---|
| **L1**（默认） | 模型编了一句原文没有的话当来源 | `difflib` 归一化模糊匹配，纯标准库 | 离线、确定性、零依赖 |
| **L2**（`--strict`） | 引文是真的，但根本不支持这一格结论（张冠李戴） | LLM-as-judge 逐条判据 | 一次模型调用 |

L1 是确定性的、可复现的、任何人 clone 下来就能跑；L2 是需要更高鲁棒性时的升级路径。
两层各抓一类错，边界清晰。

### 2. 为什么不做 embedding 语义匹配

embedding 只会让 L1 对「措辞不同但意思相近」更宽容——它不解决任何**新的**错误类别，
却引入联网和重依赖。而我们**故意要求逐字引文**：一条改写过的引文即使意思对，也应被标出，
因为它不再是「原文说的」。所以 embedding 被明确排除，不是没做，是**不该做**。
（见 `examples/` 里那条 paraphrase 被标 unsupported 的演示。）

### 3. 为什么先填概念映射表再填 15 张表（渐进式披露）

15 张表不一次性塞给模型。先锁定术语，模型就不会在表与表之间悄悄改变某个术语的定义。
这对应 Claude Skill 的 progressive disclosure 原则——`SKILL.md` 只给流程，
庞大的表模板放在 `reference/tables.md`，用到才读，省 token 也更准。

## 目录结构

```
paper-explainer/
├── AGENTS.md                      # 跨 agent 入口（Codex / Cursor / Copilot ...）
├── .claude-plugin/plugin.json     # 让整仓可作为 Claude plugin 安装
└── skills/paper-explainer/
    ├── SKILL.md                   # Claude 入口：长触发描述 + Quick Reference + workflow
    ├── reference/tables.md        # 15 张表 + 概念映射表（渐进披露，用到才读）
    ├── examples/                  # 可运行的 worked example（含故意植入的假引文）
    └── scripts/check_sources.py   # 忠实度校验：L1 默认 + --strict(L2)
```

## Roadmap（明确不做的，也列出来）

- [ ] 更多领域的 worked examples（CV / NLP / 系统方向各一篇）
- [ ] `--strict` 的 L2 judge 增加批量与缓存
- [ ] 一个从 arXiv ID 直接抓全文的取论文脚本
- [ ] ~~embedding 语义匹配~~ —— 刻意不做，理由见上「为什么不做 embedding」
- [ ] ~~web UI / Notion 导出~~ —— 超出 skill 定位，保持克制

## License

MIT（见 [LICENSE](LICENSE)）。
