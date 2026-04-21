Deep-Researcher: 基于 Harness 架构的自愈式调研智能体

## 1. 项目背景与设计哲学
本项目针对 LLM 的**时效性缺失**与**事实幻觉**问题，构建了一个自愈式 Agent 工作流。通过将大模型作为决策核心，配合外部检索工具与代码沙盒，实现了研究链路的闭环。

2. 核心架构设计

2.1 任务规划与协议管理
* **Skill 注入：** 通过 `SKILL.md` 显式定义 Agent 行为协议，规避输出漂移。
* **ReAct 范式：** 遵循 `Thought -> Action -> Observation -> Reflection` 链路，确保推理过程可追溯。

2.2 外部工具调用 (Tooling)
**动态 RAG：** 封装 `search_tool.py` 接入 Bing (CN) 节点，实现实时数据获取。
**数据投喂：** 将 Web 原始 Observation 转化为结构化上下文，补齐垂直领域知识短板。

2.3 自愈式反馈循环 (Self-Healing)
**检索纠错：** 搜索结果为空时，自动触发关键词重构策略。
**自修复执行：** 集成代码执行沙盒，捕获报错信息并驱动 Agent 执行自动化 Debug。

3. 实现进度对照 (Compliance)

| 维度 | 技术实现细节 | 模块定位 |
| :--- | :--- | :--- |
| **Agent Skill** | 结构化指令集 + 逻辑边界约束 | `SKILL.md` |
| **工具集成** | 封装 Bing (CN) 搜索引擎接口 | `search_tool.py` |
| **反馈循环** | 检索纠错 + 代码执行自修复 | `app.py` |
| **工程化 UI** | 基于 Streamlit 的状态监控仪表盘 | `app.py` |

4. 运行说明

方式一：启动 Web 可视化界面
streamlit run app.py
启动后在浏览器访问提示的本地地址即可使用 Research Engine。

方式二：运行终端核心 Workflow
python main.py
在终端中输入研究主题即可触发检索与沙盒自愈流程

5. 输出规范 (Output Schema)
根据 SKILL.md 协议，智能体的最终交付物将严格遵循以下结构 ：
Executive Summary (核心摘要)： 3-5 行高度凝练的调研结论 。
Technical Analysis (深度分析)： 结合检索数据进行逻辑推导，若涉及计算必含 Python 脚本支持 。
Validation & References (引用溯源)： 所有关键事实锚定真实来源 。
