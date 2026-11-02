# gk-study · 领域通识报告

这是一个 Claude Code Skill，可以把任意学科或领域讲给零基础读者。它先梳理历史发展，再描绘现状全貌，最后把两者结合做综合研究，生成一份排版完整的「领域通识报告」PDF。

## 安装

装好以后，路径应该是 `~/.claude/skills/gk-study/SKILL.md`。装完重新打开 Claude Code 即可使用。

**方法一：用 git 克隆**

```bash
git clone https://github.com/AIZQX/gk-study.git ~/.claude/skills/gk-study
```

**方法二：下载压缩包**

1. 在本页点 **Code → Download ZIP**，或者用别人发给你的压缩包。
2. 解压后，把文件夹改名为 `gk-study`。从 GitHub 下载的文件夹名会是 `gk-study-main`。
3. 把这个文件夹放进 `~/.claude/skills/`，也就是用户目录下的 `.claude/skills` 文件夹。如果没有这个文件夹，就新建一个。在 Mac 的访达里按 ⌘⇧. 可以显示隐藏文件夹。

## 使用

在 Claude Code 里说「帮我入门 XX 这个领域」或「领域通识 XX」，Claude 就会自动调用这个 skill。

单独排版 PDF 的命令如下：

```bash
python3 ~/.claude/skills/gk-study/scripts/build_pdf.py input.md output.pdf --title "研究对象名称" --author "作者"
```

脚本第一次运行时，会在 skill 目录下的 `.venv` 里自动装好依赖（markdown、pypdfium2、pillow）。生成 PDF 需要本机装有 Google Chrome。
