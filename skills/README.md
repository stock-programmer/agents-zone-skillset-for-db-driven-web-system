手动化软件开发全流程
前提 - 你在 Claude Code CLI 中，工作目录在项目根目录

- 项目里已有 agents/、skills/、PROGRESS.md

---

Step 1: 产品需求 — /prd

你: /prd

Claude 会进入 PRD 技能，和你做需求对话：

1. 先调研：检查现有代码、基础设施约束、API 格式
2. 问你要做什么、为什么做
3. 产出 docs/prd-{feature-name}.md
4. 自动更新 PROGRESS.md，标记 [x] Design (PRD)

你唯一要做的：回答 Claude 的需求问题

---

Step 2: 架构设计 — /architect

你: /architect

Claude 读取 PRD + 现有代码库，产出：

1. 数据模型设计（SQL DDL）
2. API 端点设计
3. 组件架构、数据流泳道图
4. 产出 docs/arch-{feature-name}.md
5. 更新 PROGRESS.md，标记 [x] Architecture

你唯一要做的：审核架构方案，提出修改意见（如果有）

---

Step 3: 开发者故事 — /story

你: /story

Claude 读取 PRD + 架构文档 + 现有代码，产出开发者唯一信源：

1. User Story（As a... I want... so that...）
2. 验收标准 AC（Given/When/Then，Then 必须包含副作用断言）
3. 技术上下文（精确到 file:line 的模式引用）
4. 任务列表映射到 AC
5. 测试需求表 + 副作用验证表
6. 产出 docs/story-{feature-name}.md
7. 更新 PROGRESS.md，标记 [x] Story

你唯一要做的：审核 Story 是否完整准确

---

Step 4（可选）: 环境准备 — /setup

你: /setup DOC-CONFIG-LIST-ENHANCEMENT

创建 git worktree + 独立分支。大多数情况可跳过，直接在当前分支开发。

---

Step 5: 写测试（TDD Red） — 启动 Tester 子代理

你: 请用 tester 子代理为 docs/story-configuration-list-enhancement.md 编写测试

Claude 启动 agents/tester.md 子代理：

1. 只读 Story 文件（不看实现代码）
2. 按 AC 编写失败测试，AAA 模式
3. 必须断言副作用（DB 状态、磁盘文件），不只是 API 响应
4. 运行测试确认全部 FAIL（Red phase）
5. 报告完成：测试文件列表、AC 覆盖映射、失败输出

如果是前端项目，tester 同样遵循红灯验证：
- 用 Vitest + Vue Test Utils 写组件测试
- 用 Playwright 写 E2E 浏览器测试
- 运行 npm run test:unit 和 npm run test:e2e 确认全部 FAIL

自动触发 auto_qc：Claude 检测到 tester 完成关键词后，自动执行 /qc --phase=tester

如果 QC 不通过（假测试、弱断言、缺失场景）：
Claude: QC 发现 5 个假测试、19 个弱断言，已退回 tester 修复
Tester 修复后再次触发 QC，循环直到通过。

你唯一要做的：等待。如果 QC 反复不过，可以介入决策

---

Step 6: 写实现（TDD Green） — 启动 Coder 子代理

你: 请用 coder 子代理实现 docs/story-configuration-list-enhancement.md

Claude 启动 agents/coder.md 子代理：

1. 读 Story + 失败的测试文件
2. 按 Story 中引用的模式实现代码
3. 运行 make test + make test-integration
4. 最多迭代 3 次，不允许留 TODO/FIXME
5. 报告完成：新增/修改文件、测试通过数、DoD 状态

如果是前端项目，coder 使用 npm run test:unit + npm run test:e2e 验证，
QC 通过后同样自动 commit + push。

自动触发 auto_qc：Claude 检测到 coder 完成后，自动执行 /qc --phase=coder

QC 通过后自动执行：
git add .
git commit -m "[DOC-CONFIG-LIST-ENHANCEMENT] 配置清单模块增强 ..."
git push origin {branch}

你唯一要做的：等待。如果 coder 3 轮后仍 blocked，需要介入决策

---

Step 7: CI 自愈 — /follow

如果 push 后 GitHub Actions 失败：

你: /follow

Claude 会：

1. 下载 CI 失败日志
2. 分类失败原因（lint / test / build / deploy）
3. 本地修复 → 验证 → commit → push
4. 轮询 CI，最多 2 轮
5. 如果仍失败，给出根因分析报告

你唯一要做的：如果 2 轮后仍失败，根据报告手动介入

---

Step 8: 创建 PR

你: 创建 PR 合并到 main

Claude 用 gh pr create 创建 PR，包含变更摘要和测试计划。

---

Step 9: HR 技能学习 — /mentor

Story 完成后，把开发过程中学到的经验反馈给系统：

你: /mentor 经验教训：tester 写的测试中，对文件上传的测试没有验证磁盘上是否真的有文件，导致 coder 用 mock
就通过了。以后 tester 必须断言物理文件存在。

Claude 会：

1. 扫描所有 agents/_.md 和 skills/_.md
2. 把这条经验有机地嵌入到最相关的文件里（这里是 agents/tester.md）
3. 匹配现有文档的语气和风格
4. 报告修改了哪些文件的哪些位置

这让系统越用越聪明 — 下次 tester 不会再犯同样的错误

---

完整流程速查表

┌──────┬─────────────────┬───────────────────────────────────┬─────────────────────┐
│ 步骤 │ 你输入什么 │ Claude 做什么 │ 产出 │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 1 │ /prd │ 对话式需求分析 │ docs/prd-_.md │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 2 │ /architect │ 技术架构设计 │ docs/arch-_.md │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 3 │ /story │ 开发者故事编写 │ docs/story-_.md │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 4 │ /setup（可选） │ git worktree 隔离 │ 新分支 │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 5 │ "启动 tester" │ TDD Red + auto*qc 门禁 │ tests/test*_.py 或 tests/**/*.spec.ts │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 6 │ "启动 coder" │ TDD Green + auto_qc + 自动 commit │ 实现代码 + git push │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 7 │ /follow（如需） │ CI 失败自愈 │ 修复 + 重新 push │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 8 │ "创建 PR" │ gh pr create │ PR 链接 │
├──────┼─────────────────┼───────────────────────────────────┼─────────────────────┤
│ 9 │ /mentor │ 经验嵌入到 agent/skill 文档 │ 更新后的文档 │
└──────┴─────────────────┴───────────────────────────────────┴─────────────────────┘

全程 9 步，你的角色是"审核者+决策者"：审核文档、在卡住时做决策、最后提炼经验。代码一行都不用自己写。

---

2. 启动 Tester（红灯测试）

请调用 tester subagent，基于 docs/story-configuration-list-enhancement.md 编写测试（TDD Red）。
要求：覆盖 story 的 AC，先设计测试再看实现，最后确认测试是 FAIL，并汇报测试文件和失败输出。

3. 手动做测试质检

/qc docs/story-configuration-list-enhancement.md --phase=tester

4. 启动 Coder（实现让测试通过）

请调用 coder subagent，基于 docs/story-configuration-list-enhancement.md 和当前 failing tests 做实现（TDD Green）。
要求：迭代修复直到测试通过，输出修改文件、测试结果和完成报告。

5. 手动做实现质检

/qc docs/story-configuration-list-enhancement.md --phase=coder
