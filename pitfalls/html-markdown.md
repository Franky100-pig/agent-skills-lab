# HTML 转 Markdown 后正文凭空少了一段，数一下 $ 还是奇数

Date: 2026-10-31 · Tags: `html-to-markdown` `regex` `math` `pandoc`

## Symptom

用「剥掉 HTML 标签」的思路把题面转成 Markdown，转完没报错，但某一段正文从中间断掉，
后半句不见了；而且那一段的 `$` 计数是奇数（数学没闭合），pandoc 因此报
`Missing $ inserted`。

```text
**(d)** For $2I$ we get $2I - 2I = \mathbf{0}$, whose null space is all of $\mathbb{R}^2$:
geometric multiplicity $2$, ... the shear's $1
                                  ^ 到这里就断了，后面的 ";  when it falls short — eigenvalues…" 没了
```

## The wrong assumption

"先剥标签、再处理数学" 看起来顺序无所谓 —— 反正 `$...$` 里也不会出现 HTML。

**里面偏偏会出现 `<`。** 一旦写了 `$1 < 2$`，正则 `<[^>]+>` 就把这个 `<` 当成标签开头，
一路删到**同一段里下一个 `>`**（常常是下一个 `<p>` 的结尾），于是中间整块正文被当成标签吃掉。
最阴险的是：转出来的文件语法完全合法，构建也不失败，只有内容悄悄变少。

## Spot it in 5 seconds

逐行数单 `$`（排除 display 的 `$$` 行）：内联数学必须成对，奇数就是被截断了。

```bash
python3 - <<'PY'
import pathlib
for name in ("set6/problems.md", "set6/solutions.md"):
    for i, line in enumerate(pathlib.Path(name).read_text().splitlines(), 1):
        if line.strip().startswith("$$"):
            continue
        if line.replace("$$", "").count("$") % 2:
            print(name, i, line[:80])
PY
```

再补一刀：源 HTML 里 `\$[^$]*<[^$]*\$` 的匹配数 > 0，就一定会触发。

## Fix

**先给数学段占位，再剥标签，最后还原。**

```python
MATH_RE = re.compile(r'\$\$.*?\$\$|\$[^$\n]*\$', re.S)

def inline(text):
    math = []
    text = MATH_RE.sub(lambda m: (math.append(m.group(0)), f"\x00{len(math)-1}\x00")[1], text)
    text = re.sub(r'<[^>]+>', '', text)      # 此时数学已变成 \x000\x00，随便剥
    text = re.sub(r'\x00(\d+)\x00', lambda m: math[int(m.group(1))], text)
    return html.unescape(text)
```

顺带一条：`.docx` 与 `.pdf` 的构建要用 `pandoc -s`（standalone），否则没有 preamble，
tectonic 直接报 `Undefined control sequence \section`。

## Globalise it

- 任何「用正则处理带数学/代码的标记语言」都会踩：HTML→MD、MD→HTML、模板替换、
  富文本清洗。**受保护片段必须先占位**（代码块、行内代码、数学、URL）。
- 同一个正则还会误吃 `a < b` 这种纯文本比较符（不在数学里时同样消失）。
- 判断标准永远是「内容完整性」，不是「构建成功」：`$` 奇偶、句子末尾是否悬空、
  字符数有没有莫名其妙变少。

## Evidence

```text
# 修前（数学里的 < 被当标签，正文被截断）
$ python3 tools/html2md.py set6/solutions.html
set6/solutions.html -> set6/solutions.md (27330 bytes)
行 115 单 $ 计数为奇: ... the shear's $1

# 修后（占位保护数学段）
$ python3 tools/html2md.py set6/solutions.html
set6/solutions.html -> set6/solutions.md (27444 bytes)     # +114 字符，正是被吃掉的那段
可疑行: []
$ grep "the shear's" set6/solutions.md
the shear's $1 < 2$ — eigenvalues and eigenvectors alone cannot build a basis.
```

## Takeaway

剥标签前先把数学和代码换成占位符；验收看「有没有少字」，别只看「有没有报错」。
