import urllib.request
import re

for filename in ['utils.py', 'server.py', 'client.py']:
    url = f"https://gitfront.io/r/weeebdev/gnm1dXbMqiHh/auto-fl-fit/blob/pycaret-fl/{filename}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            text = re.sub(r'<[^>]+>', '', html)
            with open(f"scripts/{filename}", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Downloaded and extracted {filename}, length={len(text.splitlines())}")
    except Exception as e:
        print(f"Error {filename}:", e)
