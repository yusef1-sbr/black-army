from pathlib import Path
import shutil
import re

ROOT = Path.cwd()
BASE = ROOT / "templates" / "base.html"
STATIC = ROOT / "static"
HERE = Path(__file__).resolve().parent

if not BASE.exists():
    raise SystemExit(
        f"پروژه پیدا نشد: {ROOT}\n"
        "این فایل را از داخل ~/black-army اجرا کن."
    )

backup = BASE.with_suffix(BASE.suffix + ".bak-ui-v3")
if not backup.exists():
    shutil.copy2(BASE, backup)

text = BASE.read_text(encoding="utf-8")

css_tag = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'black-army-v3.css\') }}">'
js_tag = '<script src="{{ url_for(\'static\', filename=\'black-army-v3.js\') }}"></script>'

if "black-army-v3.css" not in text:
    if re.search(r"\n\s*</head>", text):
        text = re.sub(r"\n(\s*)</head>", rf"\n\1    {css_tag}\n\1</head>", text, count=1)
    else:
        raise SystemExit("تگ </head> در base.html پیدا نشد.")

if "black-army-v3.js" not in text:
    if re.search(r"\n\s*</body>", text):
        text = re.sub(r"\n(\s*)</body>", rf"\n\1    {js_tag}\n\1</body>", text, count=1)
    else:
        raise SystemExit("تگ </body> در base.html پیدا نشد.")

if 'class="owner-entry"' not in text:
    owner = '''\n            <a href="{{ url_for('admin_login') }}" class="owner-entry">\n                🔐 ورود مالکین\n            </a>\n'''
    nav_match = re.search(r"\n(\s*)</nav>", text)
    if nav_match:
        indent = nav_match.group(1)
        owner = owner.replace("            ", indent + "    ")
        text = text[:nav_match.start()] + owner + text[nav_match.start():]
    else:
        raise SystemExit("تگ </nav> پیدا نشد؛ دکمه ورود مالکین اضافه نشد تا قالب خراب نشود.")

BASE.write_text(text, encoding="utf-8")
STATIC.mkdir(parents=True, exist_ok=True)
shutil.copy2(HERE / "black-army-v3.css", STATIC / "black-army-v3.css")
shutil.copy2(HERE / "black-army-v3.js", STATIC / "black-army-v3.js")

print("✅ Black Army UI V3 installed directly into this project.")
print("✅ Public owner-login entry added -> /admin")
print("✅ V3 CSS + JS installed.")
print("✅ Backup: templates/base.html.bak-ui-v3")
