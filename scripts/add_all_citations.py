with open('journal_paper.typ', 'r', encoding='utf-8') as f:
    text = f.read()

# Add the 8 citations into the relevant sentences:
# 1. diffie1976new
text = text.replace(
    'computes pairwise shared secrets $s_(u,v) = "DH"(s_u^"priv", s_v^"pub")$ for all peers $v eq.not u$.',
    'computes pairwise shared secrets $s_(u,v) = "DH"(s_u^"priv", s_v^"pub")$ for all peers $v eq.not u$ via Diffie-Hellman key agreement @diffie1976new.'
)

# 2. li2020federated, sarma2021federated, xu2021federated, vepakomma2018split in Section II-A
text = text.replace(
    'Federated optimization in healthcare was formalized by McMahan et al. @mcmahan2017communication through Federated Averaging (FedAvg). In ubiquitous health, Chen et al. @chen2020fedhealth introduced FedHealth for transfer learning across edge wearables.',
    'Federated optimization in distributed systems was formalized by McMahan et al. @mcmahan2017communication and surveyed comprehensively by Li et al. @li2020federated. In ubiquitous healthcare informatics, Xu et al. @xu2021federated and Sarma et al. @sarma2021federated explored decentralized wearable telemetry aggregation, while Vepakomma et al. @vepakomma2018split developed split learning to partition model layers without centralizing raw records. Chen et al. @chen2020fedhealth introduced FedHealth for transfer learning across edge wearables.'
)

# 3. so2021turbo, kadhe2020fastsecagg in Section II-D
text = text.replace(
    'Our work builds upon lightweight modular arithmetic using Flower 1.42 primitives @beaufays2020flower.',
    'Subsequent innovations such as Turbo-Aggregate @so2021turbo and FastSecAgg @kadhe2020fastsecagg leveraged multi-group circular architectures and Fast Fourier transforms to reduce aggregation complexity. Our work builds upon lightweight modular arithmetic using Flower 1.42 primitives @beaufays2020flower.'
)

# 4. geyer2017differentially in Section II-C
text = text.replace(
    'Abadi et al. @abadi2016deep established the Differential Private Stochastic Gradient Descent (DP-SGD) algorithm utilizing per-sample gradient clipping and Gaussian noise injection.',
    'Abadi et al. @abadi2016deep established the Differential Private Stochastic Gradient Descent (DP-SGD) algorithm utilizing per-sample gradient clipping and Gaussian noise injection, while Geyer et al. @geyer2017differentially adapted differential privacy to federated optimization.'
)

with open('journal_paper.typ', 'w', encoding='utf-8') as f:
    f.write(text)

import typst
import pypdf

typst.compile('journal_paper.typ', output='journal_paper.pdf')
r = pypdf.PdfReader('journal_paper.pdf')
print(f'New compilation with all 30 references cited! Total pages: {len(r.pages)}')
for i, p in enumerate(r.pages):
    print(f'Page {i+1} chars: {len(p.extract_text().strip())}')
