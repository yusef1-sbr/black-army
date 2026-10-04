from pathlib import Path
from shutil import copy2

ROOT = Path.cwd()
STATIC = ROOT / 'static'
TEMPLATES = ROOT / 'templates'

STYLE = STATIC / 'black-army-v2.css'
SCRIPT = STATIC / 'black-army-v2.js'
BASE = TEMPLATES / 'base.html'

for path in (STYLE, SCRIPT, BASE):
    if not path.exists():
        raise SystemExit(f'File not found: {path}')

backup = TEMPLATES / 'base.html.bak-ui-v2'
if not backup.exists():
    copy2(BASE, backup)

base = BASE.read_text(encoding='utf-8')
css_tag = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'black-army-v2.css\') }}">'
js_tag = '<script src="{{ url_for(\'static\', filename=\'black-army-v2.js\') }}"></script>'

if css_tag not in base:
    marker = '</head>'
    if marker not in base:
        raise SystemExit('Could not locate </head> in base.html')
    base = base.replace(marker, f'    {css_tag}\n\n{marker}', 1)

if js_tag not in base:
    marker = '</body>'
    if marker not in base:
        raise SystemExit('Could not locate </body> in base.html')
    base = base.replace(marker, f'    {js_tag}\n\n{marker}', 1)

BASE.write_text(base, encoding='utf-8')
print('✅ Black Army UI v2 installed.')
print(f'   CSS: {STYLE}')
print(f'   JS : {SCRIPT}')
print(f'   Backup: {backup}')
