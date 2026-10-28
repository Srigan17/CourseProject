import typst

with open('test_calib.typ', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(250, len(lines)+1, 15):
    sub = ''.join(lines[:i])
    try:
        typst.compile(sub.encode('utf-8'), output='tmp.pdf')
        print(f"Line {i} compiles OK!")
    except Exception as e:
        if 'unclosed delimiter' in str(e):
            print(f"Line {i} fails with unclosed delimiter")
            # find exact line
            for j in range(max(1, i-20), i+1):
                sub_j = ''.join(lines[:j])
                try:
                    typst.compile(sub_j.encode('utf-8'), output='tmp.pdf')
                except Exception as e2:
                    if 'unclosed delimiter' in str(e2):
                        print(f"Exact line {j}: {repr(lines[j-1])}")
                        break
            break
        else:
            print(f"Line {i} other error: {e}")
