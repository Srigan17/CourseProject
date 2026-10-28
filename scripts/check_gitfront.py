import urllib.request

url = "https://gitfront.io/r/weeebdev/gnm1dXbMqiHh/auto-fl-fit"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("Page length:", len(html))
        # Print a snippet of links
        import re
        links = re.findall(r'href="([^"]+)"', html)
        for l in links[:30]:
            print("Link:", l)
except Exception as e:
    print("Error:", e)

