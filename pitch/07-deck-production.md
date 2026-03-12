# Deck Production

Use this document when you need to regenerate the presentation files.

## Generated Files

- `Southlake-Agentic-Synthetic-Data-Studio-Deck.pptx`
- `Southlake-Agentic-Synthetic-Data-Studio-Deck.pdf`

## Source Files

- `01-three-slide-deck.md`
- `06-visual-assets.md`
- `scripts/build_deck.py`
- `scripts/export_deck_pdf.applescript`
- `scripts/build_and_export_deck.sh`

## Regeneration

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
source .venv/bin/activate
python pitch/scripts/build_deck.py
```

If Keynote is available, export the PDF with:

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
osascript pitch/scripts/export_deck_pdf.applescript
```

Or run both steps together:

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
pitch/scripts/build_and_export_deck.sh
```
