#!/usr/bin/env python3
"""校验译文与原文的一致性：代码块（忽略 Go 注释翻译差异）、链接完整性、Gitbook 转义残留、引号体例。

用法: python3 verify.py <source.md> <translation.md>
退出码 0 = 通过；1 = 有错误（stderr 列出）。
"""
import re
import sys


def split_code_blocks(text):
    # CommonMark 允许围栏缩进 0-3 个空格（roman-numerals 上游正文有一处 " ```go"）
    return re.findall(r'^ {0,3}```([^\n]*)\n(.*?)^ {0,3}```', text, re.S | re.M)


def strip_go_comments(code):
    """逐行剔除 // 注释（引号状态感知，不动字符串里的 //）。"""
    out = []
    for line in code.split('\n'):
        res, quote, i = [], None, 0
        while i < len(line):
            c = line[i]
            if quote:
                if c == '\\':
                    res.append(line[i:i + 2])
                    i += 2
                    continue
                if c == quote:
                    quote = None
                res.append(c)
                i += 1
                continue
            if c in ('"', "'", '`'):
                quote = c
                res.append(c)
                i += 1
                continue
            if c == '/' and i + 1 < len(line) and line[i + 1] == '/':
                break
            res.append(c)
            i += 1
        out.append(''.join(res).rstrip())
    return '\n'.join(out)


def norm(code, lang):
    if lang.strip() == 'go':
        code = strip_go_comments(code)
    # Gitbook 自动链接泄漏（<http://...>）允许清理
    return code.replace('<http://', 'http://')


def clean_url(u):
    return u.rstrip('.,;:!?"\'，。；：！？）»')


def urls(text):
    prose = re.sub(r'^ {0,3}```.*?^ {0,3}```', '', text, flags=re.S | re.M)
    prose = re.sub(r'`[^`\n]*`', '', prose)
    # 外链图片允许本地化（assets/），不计入必须保留的 URL
    prose = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', prose)
    # quii.gitbook.io 书内链接允许改写为本站站内链接
    prose = re.sub(r'https?://quii\.gitbook\.io[^\s)]*', '', prose)
    inline = re.findall(r'\]\((https?://[^)\s]+)\)?', prose)
    rest = re.sub(r'\]\([^)\s]*\)', '', prose)
    bare = re.findall(r'https?://[^\s)\]>"`]+', rest)
    return {clean_url(u) for u in inline + bare}


def main():
    src, tra = open(sys.argv[1]).read(), open(sys.argv[2]).read()
    errs, imgs = [], []

    sb, tb = split_code_blocks(src), split_code_blocks(tra)
    if len(sb) != len(tb):
        errs.append(f'代码块数量不一致: 原文 {len(sb)} vs 译文 {len(tb)}')
    for i, ((sl, sc), (tl, tc)) in enumerate(zip(sb, tb)):
        if sl.strip() != tl.strip():
            errs.append(f'代码块 {i + 1} 语言标记不一致: {sl!r} vs {tl!r}')
        if norm(sc, sl) != norm(tc, tl):
            errs.append(f'代码块 {i + 1} 内容不一致（Go 注释除外）')

    missing = urls(src) - urls(tra)
    if missing:
        errs.append('译文缺失原文链接: ' + ', '.join(sorted(missing)))

    for ch in '「」':
        if ch in tra:
            errs.append(f'引号体例：发现直角引号 {ch}（统一用弯引号 ""）')

    prose = re.sub(r'^ {0,3}```.*?^ {0,3}```', '', tra, flags=re.S | re.M)
    prose = re.sub(r'`[^`\n]*`', '', prose)
    for m in re.finditer(r'\\[.,()\[\]_!/~%-]', prose):
        errs.append(f'疑似 Gitbook 转义残留: {prose[max(0, m.start() - 15):m.start() + 15]!r}')

    imgs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', tra)
    for p in imgs:
        if p.startswith('.gitbook') or p.startswith('..'):
            errs.append(f'图片路径仍指向上游仓库，需拷贝资源并改写: {p}')

    if errs:
        print('\n'.join('FAIL: ' + e for e in errs))
        sys.exit(1)
    print(f'OK: {len(tb)} 个代码块一致, 链接完整, 无转义残留'
          + (f'（含图片 {len(imgs)} 张，请确认已拷贝）' if imgs else ''))


if __name__ == '__main__':
    main()
