# Worked Example — 多模态感知驱动决策综述

> 演示 paper-explainer 的输出形态。论文：*Multimodal Perception-Driven
> Decision-Making for Human-Robot Interaction: a Survey* (Zhao et al., 2025,
> Frontiers in Robotics and AI, DOI 10.3389/frobt.2025.1604472)。
>
> 注意每个证据格都带了「原文引文」——这些引文可用同目录的
> `claims.json` + `scripts/check_sources.py` 验证。这一节演示的是**输出应该长什么样**，
> 而不是让你照抄。

## 概念-定位映射表（先填）

| 术语 | 一句话定义 | 上位概念 | 同类概念区别 | 在文中角色 |
| --- | --- | --- | --- | --- |
| 多模态感知 | 从视觉/语音/触觉等多个异质传感器提取并集成信息 | 感知科学 | vs 单模态：信息源更广 | MPDDM 的输入阶段 |
| 多模态融合 | 在数据/特征/决策不同阶段组合多模态信息 | 信息融合 | vs 感知：强调"合并策略" | 连接感知与决策的中枢 |
| MPDDM | 用融合的多模态感知直接驱动机器人动作的端到端框架 | HRI 系统设计 | vs POMDP：MPDDM 是应用，POMDP 是工具 | 全文核心架构 |

知识树：`HRI → MPDDM →（多模态感知 → 多模态融合 → 决策）`，三个子术语均见于上表。

## 表1 一句话看懂全文

| 项目 | 内容 | 原文引文 |
| --- | --- | --- |
| 核心问题 | 机器人如何整合多模态感知来做出更优的人机交互决策 | "how robots integrate multimodal perception ... to make decisions in human-robot interaction" |
| 关键机制 | 多模态融合缓解纯视觉系统在动态导航中的不稳定 | "combining RGB-D and LiDAR mitigates the instability of vision-only systems" |
| 最有说服力的实验 | MEAL 框架多模态探索使物体属性学习准确度提升约 50% | "improving accuracy by 50% over single-modality baselines" |

## 表7 实验设计与结果（节选）

| 场景/数据 | 任务 | 指标 | 本文数值 | 结论 | 原文引文 |
| --- | --- | --- | --- | --- | --- |
| MEAL 物体交互 | 属性学习 | 准确度 | +50% vs 单模态 | 多模态显著优于单模态 | "improving accuracy by 50% over single-modality baselines" |

## 校验演示

本目录的 `claims.json` 抽出了上面这些 (claim, quote) 对，其中**故意混入一条编造引文**
（一条原文根本没有的 "99% on ImageNet" 结论）。运行：

```bash
python ../scripts/check_sources.py --tables claims.json --source source.txt
```

你会看到编造的那条被标为 `⚠ unsupported`，其余通过。这就是本 skill 相比普通
"论文总结 prompt" 的关键区别：**证据是可验证的，不是模型说了算。**
