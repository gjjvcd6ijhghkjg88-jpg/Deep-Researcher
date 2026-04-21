import json
import time
import requests
from bs4 import BeautifulSoup

def web_search(query, max_results=3, retries=2):
    """
    Search engine interface using Bing (CN node).
    Returns a JSON string containing titles, links, and snippets.
    """
    # 使用标准技术日志格式代替拟人化输出
    print(f"[*] Retrieval started. Query: '{query}'")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    for i in range(retries):
        try:
            # 采用 cn.bing.com 确保国内环境直连的稳定性
            url = f"https://cn.bing.com/search?q={query}"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []

            # 解析 Bing 搜索结果 DOM
            for li in soup.find_all('li', class_='b_algo')[:max_results]:
                h2 = li.find('h2')
                snippet_box = li.find('div', class_='b_caption') or li.find('p')

                if h2 and snippet_box:
                    title = h2.text.strip()
                    link = h2.find('a')['href'] if h2.find('a') else None
                    snippet = snippet_box.text.strip()[:300]
                    
                    if link:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })

            if not results:
                if i < retries - 1:
                    print(f"[!] Null response. Retrying ({i+1}/{retries})...")
                    time.sleep(1.5)
                    continue
                return json.dumps({"error": "No relevant data retrieved."}, ensure_ascii=False)

            print(f"[+] Successfully retrieved {len(results)} items.")
            return json.dumps(results, ensure_ascii=False)

        except Exception as e:
            if i < retries - 1:
                print(f"[!] Network exception: {type(e).__name__}. Retrying...")
                time.sleep(2)
            else:
                return json.dumps({"error": f"Search interface failure: {str(e)}"}, ensure_ascii=False)

    return json.dumps({"error": "Max retries exceeded."}, ensure_ascii=False)

if __name__ == "__main__":
    # Integration Test
    print("[System] Running connectivity test...")
    test_res = web_search("DeepSeek R1 development")
    print(f"[Results] {test_res}")
