# Vibe Evaluator MVP

## Overview (English)

This directory contains a Minimum Viable Product (MVP) implementation of the Vibe Evaluator concept, implemented using the [smolagents](https://huggingface.co/docs/smolagents/en/index) framework's CodeAgent. It provides a simplified yet functional demonstration of the core idea: evaluating AI agents through their standardized capability descriptions.

## The Self-Introspection Approach

The `introspect_agent_mvp.py` script implements a self-introspection approach for agent evaluation. Instead of having a separate evaluator agent assess another agent, this MVP demonstrates how an agent can introspect and evaluate its own capabilities:

1. **Tool Collection Loading**: Loads tools from an MCP server using the MCP protocol
2. **Self-Analysis**: Prompts the agent to create a detailed list of its own capabilities
3. **Metric Design**: The agent identifies and defines 6 evaluation metrics for itself
4. **Task Creation**: Designs specific executable tasks that test its declared capabilities
5. **Task Execution**: Performs these tasks and records execution results
6. **Self-Scoring**: Derives quantified values (0-1) for each evaluation metric
7. **Structured Reporting**: Outputs the complete evaluation in various formats (console, JSON, YAML, HTML)

This approach demonstrates the minimal core concept of capability-based evaluation while still producing meaningful metrics and assessments.

## Usage

```bash
# Basic usage with default time server (stdio)
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York"

# Using an SSE server
python introspect_agent_mvp.py --server-type sse --server-params "https://example.com/mcp-endpoint"

# Output format options
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York" --output json
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York" --output yaml
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York" --output html
```

## Report Example

Below is an example of the generated HTML report from the agent self-evaluation:

![Report Example](report-example.png)

---

## 概述 (中文)

此目录包含 Vibe Evaluator 概念的最小可行产品 (MVP) 实现，使用 [smolagents](https://huggingface.co/docs/smolagents/en/index) 框架中的 CodeAgent 实现。它提供了核心理念的简化但功能完整的演示：通过标准化能力描述评估 AI 代理。

## 自我内省方法

`introspect_agent_mvp.py` 脚本实现了一种自我内省的代理评估方法。与让独立的评估代理评估另一个代理不同，这个 MVP 演示了代理如何内省并评估自身能力：

1. **工具集加载**：使用 MCP 协议从 MCP 服务器加载工具
2. **自我分析**：提示代理创建自身能力的详细列表
3. **指标设计**：代理为自己确定并定义 6 个评估指标
4. **任务创建**：设计测试其声明能力的具体可执行任务
5. **任务执行**：执行这些任务并记录执行结果
6. **自我评分**：为每个评估指标导出量化值（0-1）
7. **结构化报告**：以各种格式（控制台、JSON、YAML、HTML）输出完整评估

这种方法展示了基于能力评估的最小核心概念，同时仍能产生有意义的指标和评估。

## 使用方法

```bash
# 使用默认时间服务器的基本用法 (stdio)
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York"

# 使用 SSE 服务器
python introspect_agent_mvp.py --server-type sse --server-params "https://example.com/mcp-endpoint"

# 输出格式选项
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York" --output json
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York" --output yaml
python introspect_agent_mvp.py --server-type stdio --server-params "uvx mcp-server-time --local-timezone=America/New_York" --output html
```

## 报告示例

以下是代理自我评估生成的 HTML 报告示例：

![报告示例](report-example.png)
