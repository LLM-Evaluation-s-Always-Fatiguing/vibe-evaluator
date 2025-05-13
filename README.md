# Vibe Evaluator

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/LLM-Evaluation-s-Always-Fatiguing/vibe-evaluator)

## Concept: Vibe Evaluating (English)

This project explores "Vibe Evaluating": an automated approach to assessing AI agents or services based on their standardized capability descriptions, primarily using protocols such as:

*   **Model Context Protocol (MCP):** [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction)
*   **Agent-to-Agent (A2A):** [https://google.github.io/A2A/#/](https://google.github.io/A2A/#/)

These protocols act as the "resume" or "self-introduction" of an agent in the LLM era, standardizing how capabilities are presented.

### Core Evaluation Process

At its foundation, Vibe Evaluating involves a structured, automated process driven by an "Evaluator Agent" (akin to a universal interviewer):

1.  **Analyze Description:** The Evaluator Agent reads and parses the target agent/service's self-description (e.g., MCP server definition).
2.  **Design Metrics:** Based on the described capabilities, it automatically designs relevant evaluation metrics (like a competency radar chart).
3.  **Create Plan:** It generates a structured evaluation plan or outline based on these metrics.
4.  **Define Tasks:** The plan is broken down into specific unit tasks. Each task is designed to exercise one or more of the agent's described capabilities, resulting in measurable outcomes and execution logs.
5.  **Execute & Score:** The tasks are executed (potentially by interacting with the target agent). The Evaluator Agent analyzes the results and logs to assess performance and assign scores for each task.
6.  **Aggregate Assessment:** Scores are aggregated to provide an overall assessment against the initially designed metrics.

### The "Vibe" Layer: Beyond Functional Testing

"Vibe Evaluating" deliberately goes beyond purely objective, functional testing. It aims to capture the more nuanced, qualitative aspects – the "vibe" – of the agent, inferred from *how* it describes itself via the protocol. The Evaluator Agent also acts as a discerning critic, assessing:

1.  **Presentation & Style Analysis:**
    *   **Clarity & Thoroughness:** How well-documented, clear, and understandable are the descriptions? (Reflects "communication skill").
    *   **Cohesion & Design:** Do capabilities seem thoughtfully designed and logically organized? (Hints at design philosophy).
    *   **Language & Naming:** Does the choice of words suggest a specific "personality" (e.g., precise, creative)?

2.  **Inferring Soft Qualities:**
    *   **Potential Robustness:** Does the description imply considerations like error handling?
    *   **Potential Creativity/Flexibility:** Do capability *types* suggest adaptability or rigid execution?
    *   **Implicit Focus:** Does the capability set strongly suggest a specific domain or style?

3.  **Creative Evaluation Design:** Assessment tasks might become more creative, probing inferred qualities through:
    *   Novel combinations of tools.
    *   Ambiguous scenarios to test adaptability.
    *   Comparison against stylistic benchmarks.

4.  **Nuanced Reporting:** The final output integrates objective results with subjective insights:
    *   Objective performance scores.
    *   Subjective assessments of inferred "soft skills."
    *   An overall "vibe" narrative capturing perceived character, potential, and style.

The term "Vibe Evaluating" intentionally embraces this element of subjectivity and intuition, aiming to understand the *spirit*, *style*, and *potential* of an agent alongside its demonstrable functions, much like assessing a person.

---

## 概念：Vibe Evaluating (中文)

本项目探索 "Vibe Evaluating"：一种基于 AI agent 或服务的标准化能力描述，对其进行自动化评估的方法，主要利用以下协议：

*   **模型上下文协议 (MCP):** [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction)
*   **Agent-to-Agent (A2A):** [https://google.github.io/A2A/#/](https://google.github.io/A2A/#/)

这些协议在 LLM 时代扮演着 agent 的"简历"或"自我介绍"的角色，标准化了能力的呈现方式。

### 核心评估流程

在其基础上，Vibe Evaluating 包含一个由"评估者 Agent"（类似于一位全能面试官）驱动的结构化、自动化流程：

1.  **分析描述：** 评估者 Agent 读取并解析目标 agent/服务的自我描述（例如 MCP 服务器定义）。
2.  **设计指标：** 基于所描述的能力，它自动设计相关的评估指标（如同能力雷达图）。
3.  **创建大纲：** 基于这些指标，生成结构化的评估计划或大纲。
4.  **定义任务：** 将计划分解为具体的单元任务。每个任务旨在实践 agent 的一个或多个描述能力，并产生可衡量的结果和执行日志。
5.  **执行与评分：** 执行任务（可能通过与目标 agent 交互）。评估者 Agent 分析结果和日志以评估表现，并为每个任务打分。
6.  **综合评估：** 汇总分数，以提供针对初始设计指标的整体评估。

### "Vibe" 层面：超越功能测试

"Vibe Evaluating" 有意超越纯粹客观的功能性测试。它旨在捕捉 agent 更细微、定性的方面——即"感觉"（vibe）——这是从 agent *如何*通过协议描述自身中推断出来的。评估者 Agent 同时扮演着有眼光的评论家，评估：

1.  **呈现与风格分析：**
    *   **清晰度与彻底性：** 描述的文档是否完善、清晰易懂？（反映"沟通技巧"）。
    *   **内聚性与设计：** 能力看起来是否经过深思熟虑的设计且逻辑组织良好？（暗示设计哲学）。
    *   **语言与命名：** 词语选择是否暗示了特定的"个性"（例如，精确、创意）？

2.  **推断软性素质：**
    *   **潜在稳健性：** 描述是否隐含了对错误处理等因素的考虑？
    *   **潜在创造力/灵活性：** 能力 *类型* 是否暗示了适应性而非僵化执行？
    *   **隐含焦点：** 能力集是否强烈暗示了特定的领域或风格？

3.  **创造性评估设计：** 评估任务可能更具创意，通过以下方式探究推断出的品质：
    *   工具的新颖组合。
    *   使用模棱两可的场景测试适应性。
    *   与风格基准进行比较。

4.  **细致的报告：** 最终输出整合了客观结果和主观见解：
    *   客观的性能分数。
    *   对推断出的"软技能"的主观评估。
    *   一个整体的 "vibe" 叙述，捕捉感知的特性、潜力和风格。

术语 "Vibe Evaluating" 有意包含了这种主观性和直觉的元素，旨在理解 agent 的 *精神*、*风格* 和 *潜力*，以及其可证明的功能，就像评估一个人一样。

## MVP Implementation

This repository includes a Minimum Viable Product (MVP) implementation of the Vibe Evaluator concept in the `mvp/` directory. The MVP demonstrates a self-introspection approach for agent evaluation:

1. **Tool Collection Loading**: Loads tools from an MCP server using the MCP protocol
2. **Self-Analysis**: Prompts the agent to create a detailed list of its own capabilities
3. **Metric Design**: The agent identifies and defines 6 evaluation metrics for itself
4. **Task Creation**: Designs specific executable tasks that test its declared capabilities
5. **Task Execution**: Performs these tasks and records execution results
6. **Self-Scoring**: Derives quantified values (0-1) for each evaluation metric
7. **Structured Reporting**: Outputs the complete evaluation in various formats (console, JSON, YAML, HTML)

### Report Example

Below is an example of the generated HTML report from the agent self-evaluation:

![Report Example](mvp/report-example.png)

See [MVP README](mvp/README.md) for detailed usage instructions.

---

## MVP 实现

此仓库在 `mvp/` 目录中包含了 Vibe Evaluator 概念的最小可行产品 (MVP) 实现。该 MVP 展示了一种代理自我内省评估方法：

1. **工具集加载**：使用 MCP 协议从 MCP 服务器加载工具
2. **自我分析**：提示代理创建自身能力的详细列表
3. **指标设计**：代理为自己确定并定义 6 个评估指标
4. **任务创建**：设计测试其声明能力的具体可执行任务
5. **任务执行**：执行这些任务并记录执行结果
6. **自我评分**：为每个评估指标导出量化值（0-1）
7. **结构化报告**：以各种格式（控制台、JSON、YAML、HTML）输出完整评估

### 报告示例

以下是代理自我评估生成的 HTML 报告示例：

![报告示例](mvp/report-example.png)

有关详细使用说明，请参阅 [MVP README](mvp/README.md)。
