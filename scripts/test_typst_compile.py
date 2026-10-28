import typst
import pypdf

# Test basic elements
test_code = """
#set page(
  paper: "us-letter",
  margin: (x: 18mm, top: 19mm, bottom: 20mm),
  columns: 2
)
#set text(
  font: "Times New Roman",
  size: 9.8pt,
  lang: "en"
)

#place(
  top,
  scope: "parent",
  float: false,
  [
    #align(center)[
      #text(size: 17.5pt, weight: "bold")[
        Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data Using Differential Privacy and Secure Aggregation
      ]
      #v(2mm)
      #text(size: 10pt)[
        #super[1]K.Srigan, #super[2]K.Bala Venkat, #super[3]K.Sasank, #super[4]Sangeetha S#super[*]
      ]
      #v(1mm)
      #text(size: 9.2pt)[
        School of Computer Science and Engineering, Vellore Institute of Technology, Vellore 632014, India
      ]
      #v(0.8mm)
      #text(size: 8.5pt)[
        #super[1]kakaraparthi.srigan2023@vitstudent.ac.in, #super[2]kancharla.naga2023@vitstudent.ac.in, #super[3]kandepalli.bala2023@vitstudent.ac.in, #super[4]s.sangeetha@vit.ac.in#super[*]
      ]
      #v(3mm)
    ]
  ]
)

#v(35mm)

#text(weight: "bold", style: "italic")[Abstract]---Continuous physiological monitoring via consumer wearables offers transformative potential.

#v(1mm)
#text(weight: "bold", style: "italic")[Index Terms]---Federated Learning, Wearables, Healthcare, Differential Privacy.

= I. INTRODUCTION
Federated Learning enables distributed model optimization.
"""

with open("test.typ", "w", encoding="utf-8") as f:
    f.write(test_code)

typst.compile("test.typ", output="test.pdf")
reader = pypdf.PdfReader("test.pdf")
print("Test compiled successfully! Pages:", len(reader.pages))
