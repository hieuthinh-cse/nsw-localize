---
name: inject-gamewin-fonts
description: Transfer selected GameMaker font glyphs and their texture atlases from a donor game.win into a compatible target game.win using a Python driver and UndertaleModTool CLI.
---

# Inject GameMaker fonts

Run [scripts/inject_gamewin_fonts.py](scripts/inject_gamewin_fonts.py) with the target and donor `game.win` files, the UndertaleModTool CLI executable, and a new output path. Python prepares and runs the UndertaleModTool script because UndertaleModTool understands GameMaker's binary structures.

The transfer copies each selected font's glyph metadata, appends its embedded texture atlas and texture page item, then points the target font at the appended page. Appending avoids overwriting texture page items that a newer game version may have added. Preserve the original files and use a fresh output path; the helper refuses to overwrite an existing output.

The default font names are `fnt_default`, `fnt_default2`, `fnt_default3`, and `fnt_title`. Pass `--fonts` to select other names. The helper checks that UndertaleModTool can reopen the result and reports its size and SHA-256.
