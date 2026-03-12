set pptxPath to POSIX file "/Users/haoranliu/Desktop/southlake-agentic-synthetic-data/pitch/Southlake-Agentic-Synthetic-Data-Studio-Deck.pptx"
set pdfPath to POSIX file "/Users/haoranliu/Desktop/southlake-agentic-synthetic-data/pitch/Southlake-Agentic-Synthetic-Data-Studio-Deck.pdf"

tell application "Keynote"
    activate
    set theDocument to open pptxPath
    delay 3
    export theDocument to pdfPath as PDF
    close theDocument saving no
end tell
