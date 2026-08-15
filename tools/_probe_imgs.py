import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
target = "https://www.aliexpress.com/w/wholesale-tws-earbuds.html"
proxy = "https://api.allorigins.win/raw?url=" + urllib.parse.quote(target, safe="")
req = urllib.request.Request(proxy, headers={"User-Agent": UA})
html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
print("len", len(html), "punish", "punish" in html.lower(), "title", "wholesale" in html.lower() or "earbuds" in html.lower())
jpgs = re.findall(r"https://ae-pic-a1\.aliexpress-media\.com/kf/[A-Za-z0-9]+\.jpg", html)
print("jpgs", len(set(jpgs)))
for u in list(dict.fromkeys(jpgs))[:8]:
    print(u)
# also item ids
ids = re.findall(r"/item/(\d+)\.html", html)
print("items", len(set(ids)), list(dict.fromkeys(ids))[:5])
