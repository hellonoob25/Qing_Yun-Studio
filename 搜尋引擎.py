from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs, unquote

app = Flask(__name__)
cache = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>一個搜尋引擎(*¯︶¯*)</title>
    <style>
        body { background:black;color:white;font-family:'Noto Sans',sans-serif;text-align:center;}
        h1   { color:#ff79c6;}
        input[type=text]{width:60%%;padding:10px;font-size:18px;border-radius:12px;border:none;}
        input[type=submit]{padding:10px 20px;font-size:18px;border-radius:12px;background:#ff79c6;color:white;border:none;cursor:pointer;}
        .result{margin-top:20px;text-align:left;width:80%%;margin-left:auto;margin-right:auto;}
        .result a{color:#8be9fd;font-size:20px;text-decoration:none;}
        .result p{font-size:14px;color:#ccc;}
    </style>
</head>
<body>
    <h1>一個搜尋引擎(*¯︶¯*)</h1>
    <form method="GET" action="/search">
        <input type="text" name="q" placeholder="喵～想找什麼呢？" required>
        <input type="submit" value="搜尋喵！">
    </form>
    {% if results %}
      <div class="result">
      {% for title, link in results %}
        <p><a href="{{ link }}" target="_blank">{{ title }}</a></p>
      {% endfor %}
      </div>
    {% endif %}
</body>
</html>
"""

def search_duckduckgo(query, max_results=30):
    if query in cache:
        return cache[query]

    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"

    try:
        r = requests.get(url, headers=headers, timeout=3)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select(".result__title a")[:max_results]
        for link in links:
            title = link.get_text(strip=True)
            raw_href = link.get("href")
            if "uddg=" in raw_href:
                parsed = urlparse(raw_href)
                real = parse_qs(parsed.query).get("uddg", [""])[0]
                href = unquote(real)
            else:
                href = raw_href
            if title and href:
                results.append((title, href))
        if not results:
            results.append(("喵喵找不到東西QAQ", "#"))
    except Exception as e:
        results.append((f"搜尋失敗：{e}", "#"))

    cache[query] = results
    return results

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/search")
def search():
    q = request.args.get("q", "")
    res = search_duckduckgo(q) if q else []
    return render_template_string(HTML_TEMPLATE, results=res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
