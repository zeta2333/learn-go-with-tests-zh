# 02 — 翻译提示词：Hello, World（共享上下文）

## 任务

将《Learn Go with Tests》第一章 `hello-world.md` 由英文精翻为简体中文（zh-CN），出版级质量。

## 目标风格

- 预设：**conversational**——像有经验的同事面对面带你入门，亲切、自然、有节奏；原作者的幽默必须保留。
- 读者：**technical**——会编程的开发者。HTTP、终端、编辑器等常识不需要解释；Go 特有概念（包、模块、接口、具名返回值等）首现时以「中文（English）」或加粗括注形式轻量点一次。
- 忌：翻译腔（长定语、名词堆砌、"被"字滥用、"因此/然而"连词堆叠）、逐词直译、把幽默译平。

## 内容背景

TDD 入门教程第一章：以 `Hello, world` 为例完整走一遍 TDD 循环，顺带引入 Go 基础语法（包、函数、变量、if、常量、switch、具名返回值）、测试工具链（go test、子测试、t.Helper、%q）和模块初始化（go mod init）。教学重心是"每一步为什么这么做"。

## 术语表（必须一致）

测试驱动开发（TDD）、包（package）、模块（module）、副作用（side effect）、领域代码（domain code）、子测试（subtest）、断言（assertion）、辅助函数（helper）、基准测试（benchmark）、接口（interface）、具名返回值（named return value）、零值（zero value）、短变量声明（short variable declaration）、格式化动词（format verb）、占位符（placeholder）、魔法字符串（magic string）、版本控制（source control）、重构（refactor）、心流（state of flow）、静态类型（statically typed）、编译器（compiler）。

保留英文不译：mock / stub / spy / fake / map / goroutine / channel / commit（动词语境可译"提交"）/ `Hello, world` / pkgsite / go doc / go run / go test / go mod init 等命令与代码标识符。

## 硬性规则

1. **代码块、终端输出、错误信息一字不改**（含原文即有的拼写原样，如 `want 'Hello, Chris''`）；代码注释如有则一并译出（本章代码块无注释）。
2. 行内代码、加粗、斜体、链接、标题层级与原文一一对应。
3. 章首"本章所有代码"链接保留指向原 GitHub 仓库 `tree/main/hello-world`。
4. 外链（Wikipedia、golang.org、pkg.go.dev、go.dev）全部保留原 URL。
5. 标题 `Hello, YOU` 保留原文；其余标题意译为自然中文。
6. 段落顺序、步骤因果链与原文严格对应，不合并、不拆移。
7. 专有输出（`got %q want %q` 等）在正文中描述时用行内代码原样引用。

## 已知翻译挑战与对策

- "It is traditional for..." → 按"惯例"重组，勿直译"这是传统的"。
- "listen to the compiler" → "听编译器的话"。
- "In a word, modules." → "一个词：模块。"
- "Goodness me" → "好家伙"。
- "Who knew you could get so much out of `Hello, world`?" → "谁能想到一个 `Hello, world` 能学出这么多东西？"
- "quality-of-life feature" → "提升幸福感的设计"。
- "one...last...refactor?" → "最后一次……重构？"
