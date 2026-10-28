import typst

with open('journal_paper.typ', encoding='utf-8') as f:
    lines = f.readlines()

low = 1
high = len(lines)
ans = -1

# Find first line where compiling lines[:i] gives unclosed delimiter
# Check if lines[:high] fails
try:
    typst.compile(''.join(lines).encode('utf-8'), output='tmp.pdf')
    print("Full file compiles!")
except Exception as e:
    print("Full file fails with:", e)

while low <= high:
    mid = (low + high) // 2
    sub = ''.join(lines[:mid])
    try:
        typst.compile(sub.encode('utf-8'), output='tmp.pdf')
        # if it succeeds, the error is further down
        low = mid + 1
    except Exception as e:
        # it failed. Is it unclosed delimiter or just incomplete block?
        # let's see
        high = mid - 1

print(f"Bisection stopped near line {low}")
for j in range(max(1, low-3), min(len(lines), low+4)):
    print(f"{j}: {repr(lines[j-1])}")
