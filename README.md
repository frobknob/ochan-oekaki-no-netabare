# おーちゃんのおえかきロジック — Solution Viewer

Solution viewer for all 372 nonogram puzzles in **O-Chan no Oekaki Logic**
(おーちゃんのおえかきロジック), WonderSwan, SunSoft 2000.

Live: https://frobknob.github.io/ochan-oekaki-no-netabare/

---

## Using the viewer

Open `docs/index.html` directly in a browser, or use the GitHub Pages link above.

- Pick a difficulty level and puzzle number from the dropdowns.
- **Show ring** reveals only the outer border row and column — usually enough
  to get unstuck without handing you the answer.
- **Full solution** shows everything.
- **Reset** hides it again.
- The **◐/◑** button toggles light and dark mode.

---

## Rebuilding from ROM

```
python3 oekaki-decode.py /path/to/oekaki.ws [output.json]
python3 build.py  # regenerates docs/index.html, expects ROM at /tmp/oekaki.ws
```

---

## Files

| File | Purpose |
|------|---------|
| `docs/index.html` | Self-contained viewer (puzzle data baked in, ~225KB) |
| `docs/about.html` | How this was built |
| `build.py` | Generates `docs/index.html` from ROM |
| `oekaki-decode.py` | Decodes all 372 puzzles from the ROM binary |

---

## How it was built

See [docs/about.html](docs/about.html) or the live [about page](https://frobknob.github.io/ochan-oekaki-no-netabare/about.html).

Short version: MAME Lua scripting to observe live RAM, Capstone to verify
V30MZ opcodes, Python to decode the 2-bit-per-cell packed grid format.

---

## License

Viewer code: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Puzzle content &copy; SunSoft 2000 / Bandai Namco Holdings.
