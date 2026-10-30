# 命令明明写了相对路径却报 No such file or directory 或 MODULE_NOT_FOUND，单跑一遍又好了

Date: 2026-10-30 · Tags: `bash-tool` `cwd` `node` `git`

## Symptom

上一条命令 `cd /repo && …` 明明成功了，下一条命令用相对路径就炸：

```text
Error: Cannot find module '/Users/x/WorkBuddy/2026-09-13-10-24-32/tools/test_examples.js'
    at Function._resolveFilename (node:internal/modules/cjs/loader:153:15)
…
python: can't open file '/…/2026-09-13-10-24-32/tools/test_examples.py': [Errno 2] No such file or directory
fatal: pathspec 'tools/build_preview.py' did not match any files
```

单跑一遍（重新 cd）又全好了。更迷惑的是：文件**明明存在**，同一路径上一条命令还用过。

## The wrong assumption

「Bash 工具的工作目录会在命令之间保持」。工具文档说 working directory persists，
但实际观测里每条命令都可能回到默认目录（尤其并行/超时/报错后）——`cd` 过 ≠ 下一条还在那里。
于是所有相对路径（node 脚本、git add、python 文件）都变成**相对默认目录**的路径，
报错信息里那个奇怪的完整路径就是这么拼出来的。

## Spot it in 5 seconds

看报错里的**绝对路径前缀**是不是你以为的那个目录：

```bash
pwd   # 不带 cd 单跑一条 —— 如果不是仓库根，就是这个坑
```

报错路径少了或多了一段目录（比如 `/…/2026-09-13-10-24-32/tools/` 而不是
`/…/2026-09-13-10-24-32/la-helper/tools/`），一眼认出。

## Fix

**每条命令都显式带 `cd`**，不要依赖上一条的 cd：

```bash
# bad  —— 假设 cwd 还在仓库
git add tools/foo.py && git commit -m …

# good —— 自包含
cd /abs/path/to/repo && git add tools/foo.py && git commit -m …
```

写多条命令时用 `&&` 串在同一条 Bash 调用里（同一个 shell 里 cd 是有效的），
而不是发多条独立命令各自赌 cwd。

## Globalise it

- `git add`/`git commit` 中招最隐蔽：报 `pathspec did not match`，人会先怀疑
  文件没保存/被 .gitignore，而不是 cwd。
- node/pytest 同理：`MODULE_NOT_FOUND` / `can't open file` / `no tests ran in 2.62s`
  （pytest 在空目录跑出 0 tests）全是同根因。
- 并行发多条 Bash 调用时尤其容易踩——各自独立 shell，cwd 从头开始。

## Evidence

2026-10-30 LA-Helper 会话，同一 `tools/test_examples.js`（文件确实存在）连炸三次：

```text
$ NODE tools/test_step_player.js          # 没带 cd
Error: Cannot find module '/Users/…/2026-09-13-10-24-32/tools/test_step_player.js'

$ cd /Users/…/la-helper && NODE tools/test_step_player.js
step-player: 38 项通过，0 项失败
```

## Takeaway

Bash 命令要自包含：每条都 `cd /abs/repo && …`，别信 cwd 会保持。
