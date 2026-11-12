"""Keep generated diagnostic pages aligned with the static project homepage."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def with_project_navigation(document: str) -> str:
    """Decorate an almanac page without changing its scientific contents.

    The homepage is the canonical markup for project-level links. Existing
    static pages carry the same markup so navigation also works without JS.
    """
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    header = re.search(r'<header class="osw-global">.*?</header>', home, re.S)
    footer = re.search(r'<footer class="osw-support">.*?</footer>', home, re.S)
    if header is None or footer is None:
        raise ValueError("Project homepage navigation is missing")
    navigation = header.group(0).replace('href="', 'href="../')
    navigation = navigation.replace('href="../almanac/"', 'aria-current="location" href="../almanac/"')
    support = footer.group(0).replace('href="', 'href="../')
    document = document.replace('</head>', '<link rel="stylesheet" href="../site.css"></head>', 1)
    document = document.replace('<body>', '<body><a class="osw-skip" href="#main-content">Skip to content</a>' + navigation, 1)
    document = document.replace('<main>', '<main id="main-content">', 1)
    return document.replace('</body>', support + '</body>', 1)
