import typst

with open('test_calib.typ', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(284, len(lines)+1):
    sub = ''.join(lines[:i])
    # add bib if not in sub
    if 'bibliography(' not in sub:
        sub += '\n#bibliography("references.bib", style: "ieee")\n'
    try:
        typst.compile(sub.encode('utf-8'), output='tmp.pdf')
    except Exception as e:
        # check if it's just an open block
        if sub.count('[') != sub.count(']') or sub.count('(') != sub.count(')'):
            continue
        print(f"Failed at line {i}: {e}")
        print("Line content:", repr(lines[i-1]))
        break
else:
    print("Full file compiles successfully!")
