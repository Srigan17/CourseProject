import re

with open('scripts/manuscript_template.typ', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace ($...$) with $(...)$
def fix_parens(match):
    inner = match.group(1)
    return f"$({inner})$"

fixed = re.sub(r'\(\$([^$]+)\$\)', fix_parens, text)

# Also fix any LaTeX-style commands in typst:
# e.g. \epsilon -> epsilon, \delta -> delta, \sigma -> sigma, \Delta -> Delta, \pm -> plus.minus
fixed = fixed.replace(r'\epsilon', 'epsilon')
fixed = fixed.replace(r'\delta', 'delta')
fixed = fixed.replace(r'\sigma', 'sigma')
fixed = fixed.replace(r'\Delta', 'Delta')
fixed = fixed.replace(r'\pm', 'plus.minus')
fixed = fixed.replace(r'\text', 'text')
fixed = fixed.replace(r'\{', '{')
fixed = fixed.replace(r'\}', '}')

with open('journal_paper.typ', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("Fixed template written to journal_paper.typ")
