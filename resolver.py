# resolver.py
import re
import sys
import requests
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0 Mobile Safari/537.36"
    )
}

def resolve(url, max_hops=15):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    session = requests.Session()
    session.headers.update(HEADERS)

    history = []

    for _ in range(max_hops):
        try:
            r = session.get(
                url,
                allow_redirects=False,
                timeout=12
            )
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "history": history
            }

        history.append({
            "url": url,
            "status": r.status_code
        })

        # HTTP redirect
        if r.status_code in (301, 302, 303, 307, 308):
            location = r.headers.get("Location")

            if not location:
                break

            url = urljoin(url, location)
            continue

        # HTML meta refresh
        content_type = r.headers.get("Content-Type", "")

        if "text/html" in content_type:
            html = r.text

            match = re.search(
                r'<meta[^>]+http-equiv=["\']?refresh["\']?'
                r'[^>]+content=["\'][^"\']*url=([^"\']+)',
                html,
                re.I
            )

            if match:
                new_url = match.group(1).strip()
                url = urljoin(url, new_url)
                continue

            # Simple JS redirect patterns
            patterns = [
                r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)',
                r'location\.href\s*=\s*["\']([^"\']+)',
                r'location\.replace\(["\']([^"\']+)'
            ]

            found = None

            for pattern in patterns:
                m = re.search(pattern, html, re.I)
                if m:
                    found = m.group(1)
                    break

            if found:
                url = urljoin(url, found)
                continue

        return {
            "success": True,
            "final_url": url,
            "history": history
        }

    return {
        "success": True,
        "final_url": url,
        "history": history
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Dùng: python resolver.py <link>")
        sys.exit()

    result = resolve(sys.argv[1])

    print("\n=== KẾT QUẢ ===")

    for hop in result.get("history", []):
        print(f'{hop["status"]} -> {hop["url"]}')

    if result.get("success"):
        print("\nLink cuối:")
        print(result["final_url"])
    else:
        print("\nLỗi:")
        print(result["error"])
