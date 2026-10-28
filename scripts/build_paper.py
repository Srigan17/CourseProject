import typst
import pypdf
import shutil

# Copy manuscript template to journal_paper.typ
shutil.copyfile("scripts/manuscript_template.typ", "journal_paper.typ")

print("Compiling journal_paper.typ to journal_paper.pdf...")
typst.compile("journal_paper.typ", output="journal_paper.pdf")

reader = pypdf.PdfReader("journal_paper.pdf")
page_count = len(reader.pages)
print(f"Compilation finished successfully! Page count: {page_count}")
