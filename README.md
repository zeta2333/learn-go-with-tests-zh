# Learn Go with Tests 中文版

[quii/learn-go-with-tests](https://github.com/quii/learn-go-with-tests)（Learn Go with test-driven development）的中文翻译，使用 [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) 构建。

官方中文版（studygolang Gitbook）停留在多年前的版本，未随英文版更新。本项目基于上游最新代码重译，并记录翻译基线，之后随上游增量更新。

## 翻译基线

- 上游 commit：`4675d96` — Simplify error handling in html-templates chapter snippets
- 起译日期：2026-10-07
- **已完成：前言 + Go 基础篇全部 21 章（22/42 篇）**
- 待续：测试基础（4）、构建应用（8）、问答（4）、Meta（2）等

## 本地预览

```shell
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve   # http://127.0.0.1:8000
```

构建静态站点：`.venv/bin/mkdocs build`（输出到 `site/`）。

## 仓库结构

```
docs/                 # 站点内容（译文 md，与上游章节数量逐步对齐）
  index.md            # 首页 + 进度
  hello-world.md      # 第一章译文
_translation/         # 翻译工作目录（精翻流程中间产物，保留备查）
  hello-world/
    source.md         #   原文快照
    01-analysis.md    #   内容分析
    02-prompt.md      #   翻译提示词（含术语约束）
    03-draft.md       #   初译
    04-critique.md    #   审校诊断
    05-revision.md    #   修订
    translation.md    #   定稿（= docs/hello-world.md）
```

## 翻译规范

- 代码块、终端输出与原文逐字节一致（含原文即有的笔误），代码注释随章翻译
- 清除上游为 Gitbook 添加的转义符（`\.` `\/` `\(` `\)` `\_` 等），按 mkdocs/CommonMark 规则重新判断是否需要转义；反引号内的内容（如 Windows 路径 `%USERPROFILE%\go\bin`）不动
- 术语全书统一，术语表保存在用户级 `~/.config/baoyu-skills/baoyu-translate/EXTEND.md`，新术语随章节回填
- mock / stub / spy / goroutine / channel / commit 等约定保留英文，首现加注
- 校验脚本：译文发布前逐块比对原文代码块与链接（见 `_translation/` 流程）

## 随上游更新

```shell
git -C ../learn-go-with-tests fetch --unshallow   # 如需完整历史
# diff 上游变更章节，只重译有改动的 md，并更新本文件的基线 commit
```

## 授权

原著 [Learn Go with Tests](https://github.com/quii/learn-go-with-tests) © Chris James，[MIT 协议](https://github.com/quii/learn-go-with-tests/blob/main/LICENSE.md)。中文翻译遵循同一协议。
