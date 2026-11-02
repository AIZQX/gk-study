# gk-study · 领域通识报告

这是一个 Claude Code Skill，可以把任意学科或领域讲给零基础读者。它先梳理历史发展，再描绘现状全貌，最后把两者结合做综合研究，生成一份排版完整的「领域通识报告」PDF。

## 安装

把本仓库克隆到 `~/.claude/skills/gk-study`：

```bash
git clone <仓库地址> ~/.claude/skills/gk-study
```

## 使用

在 Claude Code 里说「帮我入门 XX 这个领域」或「领域通识 XX」，Claude 就会自动调用这个 skill。

单独排版 PDF 的命令如下：

```bash
python3 ~/.claude/skills/gk-study/scripts/build_pdf.py input.md output.pdf --title "研究对象名称" --author "作者"
```

脚本第一次运行时，会在 skill 目录下的 `.venv` 里自动装好依赖（markdown、pypdfium2、pillow）。生成 PDF 需要本机装有 Google Chrome。
