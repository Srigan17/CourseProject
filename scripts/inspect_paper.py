import typst
import pypdf
import os

# We will construct the full manuscript with rich academic content
# and calibrate spacing so that it compiles to EXACTLY 8 PAGES.

with open("journal_paper.typ", "r", encoding="utf-8") as f:
    current_working_typ = f.read()

# Let's inspect current working text
print(f"Current journal_paper.typ length: {len(current_working_typ)} chars")
