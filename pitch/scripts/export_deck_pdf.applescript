set pptxPath to POSIX file "/Users/haoranliu/Desktop/southlake-agentic-synthetic-data/pitch/Southlake-Agentic-Synthetic-Data-Studio-Deck.pptx"
set pdfPath to POSIX file "/Users/haoranliu/Desktop/southlake-agentic-synthetic-data/pitch/Southlake-Agentic-Synthetic-Data-Studio-Deck.pdf"

tell application "Keynote"
    activate
    repeat with i from (count of documents) to 1 by -1
        close document i saving no
    end repeat
    delay 1
    set theDocument to open pptxPath
    delay 2
    export theDocument to pdfPath as PDF
    close theDocument saving no
end tell
