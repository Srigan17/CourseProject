with open("scripts/manuscript_template_calib.typ", "r", encoding="utf-8") as f:
    text = f.read()

# Replace all LaTeX commands in typst math
replacements = {
    r'\sigma': 'sigma',
    r'\mu': 'mu',
    r'\pm': 'plus.minus',
    r'\kappa': 'kappa',
    r'\epsilon': 'epsilon',
    r'\delta': 'delta',
    r'\Delta': 'Delta',
    r'\sqrt': 'sqrt',
    r'\approx': 'approx',
    r'\times': 'times',
    r'\quad': 'quad',
    r'\le': '<=',
    r'\ge': '>=',
    r'\in': 'in',
    r'\forall': 'forall',
    r'\rm ': '',
    r'\text{PRV}': '"PRV"',
    r'\text{Acc}': '"Acc"',
    r'\text{pp}': '"pp"',
    r'\text{sample}': '"sample"',
    r'\text{pop}': '"pop"',
    r'\text{mean}': '"mean"',
    r'\text{opt}': '"opt"',
    r'\text{': '"',
    r'\%': '%',
    r'\{': '{',
    r'\}': '}'
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open("scripts/manuscript_template_calib.typ", "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned manuscript_template_calib.typ successfully!")
