import typst

# test without author text
code = """
#set page(paper: "us-letter", margin: (x: 18mm, top: 19mm, bottom: 20mm))
#align(center)[
  #v(-3mm)
  #text(size: 17pt, weight: "bold")[
    Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data
  ]
]
"""
try:
    typst.compile(code.encode('utf-8'), output='t.pdf')
    print("Base title compiles OK!")
except Exception as e:
    print("Base title failed:", e)

# now add authors:
code2 = """
#set page(paper: "us-letter", margin: (x: 18mm, top: 19mm, bottom: 20mm))
#align(center)[
  #v(-3mm)
  #text(size: 17pt, weight: "bold")[
    Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data
  ]
  #v(3mm)
  #text(size: 9.8pt)[
    K.Srigan, K.Bala Venkat, K.Sasank, Sangeetha S
  ]
]
"""
try:
    typst.compile(code2.encode('utf-8'), output='t.pdf')
    print("Title + authors compiles OK!")
except Exception as e:
    print("Title + authors failed:", e)
