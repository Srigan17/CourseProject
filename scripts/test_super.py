import typst

# test super
for s in ['super[1]', '#super[1]', '^1', '#super("1")']:
    c = f'#set page(paper: "us-letter")\nHello {s} World'
    try:
        typst.compile(c.encode('utf-8'), output='t.pdf')
        print(f"'{s}' SUCCESS!")
    except Exception as e:
        print(f"'{s}' FAILED: {e}")
