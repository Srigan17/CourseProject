import typst

with open('journal_paper.typ', encoding='utf-8') as f:
    lines = f.readlines()

for i in [17, 24, 28, 33, 42]:
    sub = ''.join(lines[:i])
    try:
        typst.compile(sub.encode('utf-8'), output='t.pdf')
        print(f"Lines 1-{i}: SUCCESS!")
    except Exception as e:
        print(f"Lines 1-{i}: FAILED with {e}")
