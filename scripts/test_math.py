import typst

# test inside math
code = """
$(epsilon = 4.29, delta = 10^(-5))$
$(N = 732)$
"""
try:
    typst.compile(code.encode('utf-8'), output='t.pdf')
    print("Parens inside math SUCCESS!")
except Exception as e:
    print("Failed:", e)
