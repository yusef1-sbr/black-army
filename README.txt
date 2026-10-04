BLACK ARMY UI V3
================

This is a visual upgrade package for the existing Flask Black Army website.
It does NOT replace app.py, database logic, form endpoints, authentication,
or notification logic.

What it adds:
- Major public-site redesign using the existing HTML structure.
- Dedicated owner-login button in public navigation -> /admin.
- Dedicated owner access card in the footer.
- New animated ambient background, grid, scanlines, noise, vignette and scroll progress.
- Hero redesign with status strip and parallax glow.
- Larger, deeper public cards, people cards, member cards, news cards, relations,
  honors, timeline and forms.
- Owner login visual redesign.
- Owner dashboard visual redesign with sticky sidebar, command chips, mobile drawer,
  active-section tracking and animated admin panels.
- Pointer glow, card tilt, ripple effects, reveal animations and reduced-motion fallback.
- Responsive mobile and tablet layouts.

INSTALL IN TERMUX
=================
1) Put this folder in or copy this package next to your project.
2) From the extracted package directory run:

   python apply_v3.py

The script expects the real project root to be the parent directory of this package.
For example:

   ~/black-army/
   ~/black-army-ui-v3/

If you instead unpack the package directly inside ~/black-army, run the script from
there only after adjusting ROOT in apply_v3.py. The safest method is to extract
this package to ~/ and keep it next to ~/black-army.

Then validate your Flask file:

   cd ~/black-army
   python -m py_compile app.py

Then commit:

   git add templates/base.html static/black-army-v3.css static/black-army-v3.js
   git commit -m "Major Black Army UI V3 overhaul"
   git push origin main

If the design causes a problem, restore the base template with:

   cp templates/base.html.bak-ui-v3 templates/base.html

and remove the two V3 assets.
