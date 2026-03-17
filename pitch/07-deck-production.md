# Deck Production

Use this document when you need to regenerate the presentation files.

## Generated Files

- `Southlake-Agentic-Synthetic-Data-Studio-Deck.pptx`
- `Southlake-Agentic-Synthetic-Data-Studio-Deck.pdf`

## Source Files

- `deck.html`
- `01-three-slide-deck.md`
- `06-visual-assets.md`
- `../apps/web/scripts/render-deck-slides.mjs`
- `scripts/build_deck.py`
- `scripts/build_and_export_deck.sh`

## Regeneration

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
pitch/scripts/build_and_export_deck.sh
```

This native deck pipeline does two things:

- builds a native editable `Southlake-Agentic-Synthetic-Data-Studio-Deck.pptx`
- attempts to export the PDF backup from that editable deck when Keynote is available, while keeping the existing PDF if Keynote automation stalls

If you want to run the steps manually:

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
source .venv/bin/activate
python pitch/scripts/build_deck.py
```

If Keynote is installed and you want the PDF to come directly from the editable deck:

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
open -a Keynote
osascript pitch/scripts/export_deck_pdf.applescript
```
