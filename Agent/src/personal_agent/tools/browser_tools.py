from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from personal_agent.config import MAX_READ_CHARS


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
        elif self._skip_depth == 0:
            self.parts.append(text)


def fetch_url(url: str, max_chars: int = 8000) -> str:
    """
    Fetch a public http or https URL and return readable page text.

    Args:
        url: Full URL beginning with http:// or https://.
        max_chars: Maximum characters to return.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "unsupported URL scheme. Use http or https."
    if not parsed.netloc:
        return "URL must include a hostname."

    limit = min(max(max_chars, 1000), MAX_READ_CHARS)
    request = Request(
        url,
        headers={"User-Agent": "personal-agent/0.1 (+local assistant)"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get("content-type", "")
            raw = response.read(limit * 4)
    except HTTPError as error:
        return f"HTTP error while fetching URL: {error.code} {error.reason}"
    except URLError as error:
        return f"could not fetch URL: {error.reason}"
    except OSError as error:
        return f"could not fetch URL: {error}"

    if "text/html" not in content_type and "text/plain" not in content_type:
        return f"unsupported content type: {content_type or 'unknown'}"

    text = raw.decode("utf-8", errors="replace")
    if "text/html" in content_type:
        parser = _TextExtractor()
        parser.feed(text)
        body = "\n".join(parser.parts)
        title = parser.title or url
        text = f"Title: {title}\nURL: {url}\n\n{body}"
    else:
        text = f"URL: {url}\n\n{text}"

    if len(text) > limit:
        return text[:limit] + "\n\n[TRUNCATED: response is too large]"

    return text
