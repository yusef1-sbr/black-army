
from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
BASE = TEMPLATES / "base.html"
CSS_SRC = Path(__file__).resolve().parent / "static" / "black-army-v3.css"
JS_SRC = Path(__file__).resolve().parent / "static" / "black-army-v3.js"


def backup(path: Path):
    bak = path.with_suffix(path.suffix + ".bak-ui-v3")
    if path.exists() and not bak.exists():
        shutil.copy2(path, bak)


def patch_base():
    if not BASE.exists():
        raise SystemExit(f"پیدا نشد: {BASE}")
    backup(BASE)
    text = BASE.read_text(encoding="utf-8")

    # Load the V3 layer after the original theme, preserving current styles.
    if "black-army-v3.css" not in text:
        marker = "<link\\n        rel=\"stylesheet\"\\n        href=\"{{ url_for('static', filename='style.css') }}\">"
        if marker in text:
            text = text.replace(marker, marker + '\n\n    <link\\n        rel="stylesheet"\\n        href="{{ url_for(\'static\', filename=\'black-army-v3.css\') }}">')
        else:
            needle = "</head>"
            text = text.replace(needle, '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'black-army-v3.css\') }}">\n\n' + needle, 1)

    if "black-army-v3.js" not in text:
        needle = "</body>"
        text = text.replace(needle, '    <script src="{{ url_for(\'static\', filename=\'black-army-v3.js\') }}"></script>\n\n' + needle, 1)

    # Dedicated owner-login entry in public navigation.
    if "class=\"owner-entry\"" not in text:
        nav_close = "        </nav>"
        owner = '''\n            <a href="{{ url_for('admin_login') }}" class="owner-entry">\n                🔐 ورود مالکین\n            </a>\n'''
        # Insert before the nav close, so it appears alongside the regular sections.
        if nav_close in text:
            text = text.replace(nav_close, owner + "\n" + nav_close, 1)

    BASE.write_text(text, encoding="utf-8")


def install_assets():
    STATIC.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CSS_SRC, STATIC / "black-army-v3.css")
    shutil.copy2(JS_SRC, STATIC / "black-army-v3.js")


if __name__ == "__main__":
    patch_base()
    install_assets()
    print("✅ Black Army UI V3 installed.")
    print("✅ Owner login entry added to the public navigation.")
    print("✅ Owner access footer card will be injected automatically.")
    print("✅ Original base.html backup: templates/base.html.bak-ui-v3")
