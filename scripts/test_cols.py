import typst
import pypdf

code = """
#set page(paper: "us-letter", margin: (x: 18mm, top: 19mm, bottom: 20mm))
#set text(font: "Times New Roman", size: 9.8pt)

#align(center)[
  #text(size: 17pt, weight: "bold")[Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data]
  
  #v(2mm)
  K.Srigan, K.Bala Venkat, K.Sasank, Sangeetha S
]

#show: columns.with(2, gutter: 5mm)

= I. INTRODUCTION
Federated Learning is a decentralized learning paradigm @mcmahan2017communication.
Differential privacy was proposed by @abadi2016deep.
SecAgg was proposed by @bonawitz2017practical.

#bibliography("references.bib", style: "ieee", title: [REFERENCES])
"""

with open('test_col.typ', 'w', encoding='utf-8') as f:
    f.write(code)

typst.compile('test_col.typ', output='test_col.pdf')
print('Success! Pages:', len(pypdf.PdfReader('test_col.pdf').pages))
