# humanizer-zh

[humanizer](https://github.com/blader/humanizer) 3.1.0 的中文版：一个去掉 AI 写作痕迹的 Agent Skill。改写表达，不动事实。

原文按 `SKILL.md` 的分节顺序逐节译出，A–F 六组、26 条都在。英文排版特有的条目（§10 连字符、§20 标题大小写、§21 弯引号）保留原文说明，另附一句中文里对应的问题；中文语料里更常见的词（赋能、闭环、抓手、底层逻辑这类）补进了 §12 的词表，并按频率和语境判断，技术本义除外。

## 安装

在项目目录里用 [skills CLI](https://github.com/vercel-labs/skills)：

```sh
npx skills add QingZhou-YangHY/humanizer-zh --skill humanizer-zh
```

装到 `.agents/skills/humanizer-zh`，Pi、Codex、Cursor、Copilot 这类通用位置直接可用，Claude Code 会建一份符号链接，来源 commit 记进 `skills-lock.json`。之后用 `npx skills update` 升级。

想锁具体版本，或者装进 Pi 自己的包管理：

```bash
pi install git:github.com/QingZhou-YangHY/humanizer-zh@v0.1.2
```

本地调试，把 skill 目录链进发现路径：

```bash
ln -s "$PWD/skills/humanizer-zh" ~/.agents/skills/humanizer-zh
```

`/reload` 之后生效，`/skill:humanizer-zh <文本>` 强制加载。其他 Agent Skills 实现把 `skills/humanizer-zh/` 整个目录拷进去即可，没有运行时依赖。

## 改它

```bash
npm run check    # 校验 frontmatter、版本一致性、A–F 分组与 1–26 条是否齐全、相对路径
```

改译文时保持条目编号不变，编号是引用锚点。新增中文特有条目挂在对应分组末尾，往下顺延编号会让别处的引用失效。

发版就是一个 tag：

```bash
git tag -a v0.1.2 -m "v0.1.2: …"
git push origin main --follow-tags
```

仓库没发 npm，两种锁版本的方式：`pi install git:...@v0.1.2` 按 tag 锁，`npx skills add` 按 `skills-lock.json` 里记的 commit 锁。推代码前先跑一遍 `npm run check`，PR 上也会跑（`.github/workflows/check.yml`，Python 3.12 和 3.13）。

版本怎么定：

- patch：措辞修正、例子调整，条目和编号不变
- minor：新增条目、调整条目顺序、改 `description`（路由会变，值得单独一个版本）
- major：改动了 SKILL.md 的操作流程或输出约定

`CHANGELOG.md` 顶部的版本号要和 `package.json` 一致，否则校验不过。

## 许可

MIT。原文版权归 Siqi Chen，许可全文见 `THIRD_PARTY_LICENSES.md`。条目来源是 Wikipedia 的 [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)（WikiProject AI Cleanup 维护）。
