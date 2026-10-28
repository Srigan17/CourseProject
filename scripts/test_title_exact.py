import typst

with open('journal_paper.typ', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(20, 45):
    sub = ''.join(lines[:i])
    # check if closing bracket is needed
    if sub.count('[') > sub.count(']'):
        sub += ']' * (sub.count('[') - sub.count(']'))
    try:
        typst.compile(sub.encode('utf-8'), output='t.pdf')
        print(f"Line {i} compiles!")
    except Exception as e:
        print(f"Line {i} error: {e}")
