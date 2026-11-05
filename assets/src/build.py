"""Embed a per-file Inter Tight subset (Google Fonts text= API) into each SVG template."""
import base64, html, re, sys, urllib.parse, urllib.request, pathlib
TPL = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()
for tpl in sorted(TPL.glob("*.svg")):
    if len(sys.argv) > 3 and tpl.stem not in sys.argv[3:]: continue
    src = tpl.read_text()
    texts = re.findall(r"<text\b[^>]*>(.*?)</text>", src, re.S)
    chars = set(html.unescape(re.sub(r"<[^>]+>", "", "".join(texts)))) | set("0123456789")
    chars.discard("\n")
    q = urllib.parse.quote("".join(sorted(chars)))
    css = get(f"https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400..600&text={q}").decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    b64 = base64.b64encode(get(url)).decode()
    face = f"@font-face {{ font-family: 'IT'; src: url(data:font/woff2;base64,{b64}) format('woff2'); font-weight: 400 600; }}"
    (OUT / tpl.name).write_text(src.replace("/*FONT*/", face))
    print(f"{tpl.name}: {len(chars)} glyphs, font {len(b64)//1024} KB")
