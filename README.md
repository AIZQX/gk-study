# gk-study · 研究任何领域

这是一个通用的 Agent Skill，Claude Code、Codex 等支持 Skill 的 Agent 都能使用。它把你想学的任意学科或领域整理成零基础就能读懂的通识报告：先梳理历史发展，再描绘现状全貌，最后把两者结合做综合研究，并附上思维导图总览、术语表和信息来源，最终生成一份排版完整的 PDF。

## 安装

把整个 `gk-study` 文件夹放进你所用 Agent 的 skills 目录，例如：

| Agent | 放到这里 |
| --- | --- |
| Claude Code | `~/.claude/skills/gk-study/` |
| 其他 Agent | 该 Agent 的 skills 目录，见它的文档 |

放好后重新打开 Agent 即可。不支持 Skill 的 Agent 也能用：直接让它读一遍 `SKILL.md`，按里面的流程执行。

**方法一：用 git 克隆**（以 Claude Code 为例）

```bash
git clone https://github.com/AIZQX/gk-study.git ~/.claude/skills/gk-study
```

**方法二：下载压缩包**

1. 在本页点 **Code → Download ZIP**，或者用别人发给你的压缩包。
2. 解压后，把文件夹改名为 `gk-study`。从 GitHub 下载的文件夹名会是 `gk-study-main`。
3. 把这个文件夹放进上面说的 skills 目录。在 Mac 的访达里按 ⌘⇧. 可以显示隐藏文件夹。

## 使用

对 Agent 说「帮我入门 XX 这个领域」或「领域通识 XX」，它就会调用这个 skill。

单独排版 PDF 的命令如下，`<技能目录>` 指 `gk-study` 文件夹所在的位置：

```bash
python3 <技能目录>/scripts/build_pdf.py input.md output.pdf --title "研究对象名称" --author "作者"
```

脚本第一次运行时，会在技能目录下的 `.venv` 里自动装好依赖（markdown、pypdfium2、pillow）。生成 PDF 需要本机装有 Python 3 和 Google Chrome。
