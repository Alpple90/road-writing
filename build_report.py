from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

FONT = 'Times New Roman'
BODY_SIZE = Pt(12)

doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

normal = doc.styles['Normal']
normal.font.name = FONT
normal.font.size = BODY_SIZE

for h_name in ['Heading 1', 'Heading 2', 'Heading 3']:
    s = doc.styles[h_name]
    s.font.name  = FONT
    s.font.size  = BODY_SIZE
    s.font.bold  = True
    s.font.color.rgb = RGBColor(0, 0, 0)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _render(p, text):
    parts = re.split(r'\*\*(.*?)\*\*', text)
    for i, part in enumerate(parts):
        r = p.add_run(part)
        r.font.name = FONT
        r.font.size = BODY_SIZE
        if i % 2 == 1:
            r.bold = True

def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    _render(p, text)

def heading(level, text):
    h = doc.add_heading('', level)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after  = Pt(4)
    r = h.runs[0] if h.runs else h.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = BODY_SIZE
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

def bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    _render(p, text)

def numbered_list(text):
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.space_after = Pt(3)
    _render(p, text)

def add_table(headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
            run.font.name = FONT
            run.font.size = BODY_SIZE
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.rows[r+1].cells[c]
            cell.text = val
            for run in cell.paragraphs[0].runs:
                run.font.name = FONT
                run.font.size = BODY_SIZE
    doc.add_paragraph()

# ═════════════════════════════════════════════════════════════════════════════
# TITLE
# ═════════════════════════════════════════════════════════════════════════════
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run(
    'Lane Keep Assist Using Chip Enabled Raised Pavement Markers:\n'
    'Interpolation Algorithm Robustness Under CERPM Dropout'
)
r.font.name = FONT
r.font.size = Pt(14)
r.bold = True

for label, value in [('Author:', 'Alexander Bruce'), ('Date:', 'June 2026'),
                     ('Module:', 'Research Project — ADAS (LKA Sub-system)')]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(f'{label}  '); r1.bold = True; r1.font.name = FONT; r1.font.size = BODY_SIZE
    r2 = p.add_run(value);        r2.font.name = FONT; r2.font.size = BODY_SIZE

doc.add_paragraph()

# ═════════════════════════════════════════════════════════════════════════════
# 2. EXECUTIVE SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '2. Executive Summary')
body(
    'This report describes the Lane Keep Assist (LKA) sub-system, developed as part of a group '
    'Advanced Driver Assistance Systems (ADAS) project. LKA prevents unintentional lane departures '
    'by applying corrective steering when a vehicle drifts outside its lane boundaries. Current '
    'commercial LKA systems rely on front-facing cameras with computer vision, but these degrade '
    'substantially under poor lane markings and adverse weather conditions [6]. This project explores '
    'a Vehicle-to-Infrastructure (V2I) approach using Chip Enabled Raised Pavement Markers (CERPMs), '
    'which transmit positional data directly to the vehicle, as a more robust alternative [1][2].'
)
body(
    'The core research question is which interpolation algorithm most accurately and robustly '
    'estimates the lane centreline from CERPM boundary data, particularly under conditions where '
    'markers are missing. Seven algorithms — linear, quadratic, cubic spline, quartic, quintic, '
    'PCHIP, and Akima — were evaluated using Monte Carlo simulation (n = 2,000 runs per condition) '
    'over two failure modes: random dropout (1–20%) and clustered contiguous dropout (cluster sizes '
    '2–20 markers), at five CERPM spacings (0.5–5.0 m). Higher-order polynomial B-splines '
    '(quadratic through quintic) consistently outperformed linear interpolation and PCHIP across '
    'all conditions. Quintic or quartic B-spline interpolation at ≤ 2 m marker spacing is recommended '
    'for any CERPM-based LKA deployment.'
)

# ═════════════════════════════════════════════════════════════════════════════
# 3. TABLE OF CONTENTS
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '3. Table of Contents')
for item in [
    '2. Executive Summary',
    '3. Table of Contents',
    '4. Statement of Problem',
    '5. Introduction',
    '6. Background',
    '    6.1. Relevance and Importance',
    '    6.2. Literature Review',
    '    6.3. Legal, Environmental and Ethical Considerations',
    '7. Strategy',
    '8. Project Management',
    '    8.1. Task Phases',
    '    8.2. Responsibilities',
    '    8.3. Timeline',
    '9. Deliverable Outcomes',
    '10. References',
]:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)
    for r in p.runs:
        r.font.name = FONT; r.font.size = BODY_SIZE

doc.add_paragraph()

# ═════════════════════════════════════════════════════════════════════════════
# 4. STATEMENT OF PROBLEM
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '4. Statement of Problem')
body(
    'Lane departure is among the most lethal categories of road crash. In Australia, 62% of all '
    'road fatalities nationally are attributable to lane departure — rising to 73% in regional areas '
    'and 71% in remote areas [3]. In the United States, the NHTSA estimates that LKA-equipped '
    'vehicles are on average 24% less likely to be involved in a fatal road departure crash [4]. '
    'The European Commission mandated LKA as a requirement on all new vehicles sold after July 2024, '
    'anticipating the technology will save over 25,000 lives by 2038 [5].'
)
body(
    'Despite these benefits, current camera-based LKA systems fail in precisely the conditions '
    'where failure is most dangerous — poor lane markings on rural and regional roads, rain, fog, '
    'and glare [6]. A V2I approach using CERPMs has been shown to outperform commercial vision '
    'systems in these conditions [2], but existing CERPM research uses a single interpolation '
    'method (cubic spline) and does not examine the effect of missing markers on reconstruction '
    'accuracy [1][2]. This gap must be addressed before a CERPM-based LKA system can be deployed '
    'with confidence in the reliability of its centreline estimates.'
)

# ═════════════════════════════════════════════════════════════════════════════
# 5. INTRODUCTION
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '5. Introduction')
body(
    'Lane Keep Assist is a driver assistance feature that applies corrective steering torque to '
    'prevent a vehicle from unintentionally crossing lane boundaries. Unlike automated lane-centring '
    'systems, LKA activates only reactively — when a vehicle begins to drift toward a lane edge '
    'without a turn signal — and is designed to be easily overridden by the driver. LKA is a '
    'foundational sub-system of ADAS upon which higher-level autonomous driving functions are built.'
)
body(
    'This sub-project contributes the centreline estimation component to a broader group ADAS '
    'project. It evaluates how accurately different interpolation algorithms can estimate the lane '
    'centre from left and right CERPM boundary data, and how this accuracy degrades when markers '
    'are missing. The simulation uses real road geometry sourced from a Lanelet2 OSM map, placing '
    'CERPM positions along both road edges at configurable intervals and applying Monte Carlo '
    'dropout to represent real-world infrastructure failure.'
)
body(
    'The research directly addresses the gap identified in prior CERPM literature [1][2]: existing '
    'studies assume complete marker data. This project is the first systematic evaluation of '
    'interpolation robustness under CERPM dropout, providing the evidence base needed for reliable '
    'LKA deployment using infrastructure-based positioning.'
)

# ═════════════════════════════════════════════════════════════════════════════
# 6. BACKGROUND
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '6. Background')

heading(2, '6.1. Relevance and Importance')
body(
    'Lane departure warning (LDW) systems alert drivers to drift but rely on timely driver reaction '
    '— unreliable under fatigue, distraction, or impairment. LKA systems actively intervene, making '
    'them more effective for high-risk rural and regional roads where lane markings are often degraded. '
    'The field performance of commercial LKA has been benchmarked by the OpenLKA dataset [6], which '
    'collected approximately 400 hours of LKA-steered data from 62 production vehicle models in '
    'real-world road testing. The study confirmed that LKA systems degrade substantially under poor '
    'lane markings and near lane transitions, validating the need for an infrastructure-based '
    'complement to camera sensing.'
)

heading(2, '6.2. Literature Review')
body(
    'Sharma et al. [1] and the follow-up study by Kadav et al. [2] provide the foundational '
    'evidence for the CERPM approach. They compared a Mobileye 630 commercial vision system against '
    'a CERPM-based positioning system across road conditions including sharp curves, varying lighting, '
    'and degraded lane markings. CERPMs outperformed the Mobileye in every condition tested, with '
    'an effective sensing range of up to 350 m compared to the Mobileye\'s 31 m. Critically, both '
    'studies used cubic spline interpolation without evaluating alternatives or considering the '
    'impact of missing markers — the gap this project fills.'
)
body(
    'On the perception side, Fakhari and Anwar [7][8] proposed a Multiple Model Adaptive Estimation '
    '(MMAE) algorithm combining front and rear cameras with a Kalman filter to improve lane detection '
    'under challenging conditions. While effective, this approach still depends on camera visibility '
    'and does not address the fundamental limitation of vision-based sensing in markings-absent '
    'environments. On the control side, Perozzi et al. [9] demonstrated a shared sliding-mode '
    'controller for steer-by-wire LKA that smoothly transitions authority between driver and system; '
    'accurate centreline input is a prerequisite for this controller to function correctly. Wei '
    'et al. [10] provide a comprehensive review of LKA assessment methodologies and identify '
    'standardisation gaps — this project\'s simulation framework contributes a repeatable evaluation '
    'method for one key component of the LKA pipeline.'
)

heading(2, '6.3. Legal, Environmental and Ethical Considerations')
body(
    'Under EU General Safety Regulation 2019/2144 and Australian Road Vehicle Standards Act 2018, '
    'ADAS components must be validated against defined performance criteria before vehicle type '
    'approval. An interpolation algorithm embedded in a safety-critical LKA pipeline therefore '
    'requires documented evidence of performance across failure modes — which this project provides. '
    'Physical CERPM deployment has environmental implications: denser marker spacing reduces '
    'reconstruction error but increases embedded electronics and installation energy. The simulation '
    'results offer evidence to minimise deployment density while maintaining safety. Ethically, any '
    'system that influences vehicle steering must include fail-safe defaults; the results of this '
    'project directly inform the conditions under which the LKA system should fall back to camera '
    'sensing or alert the driver.'
)

# ═════════════════════════════════════════════════════════════════════════════
# 7. STRATEGY
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '7. Strategy')

heading(2, '7.1. What Work Was Done')
body(
    'A simulation framework was developed in Python comprising four modules. **test.py** parses '
    'Lanelet2 OSM road geometry, extracts left and right boundary linestrings, and resamples them '
    'to place simulated CERPM positions at a defined spacing. **Interpolations.py** implements '
    'seven interpolation methods, all using arc-length parameterisation to avoid the distortion '
    'introduced by naive index-based methods. **Simulation.py** runs parallelised Monte Carlo '
    'trials, applying random or clustered dropout to the CERPM positions before interpolation, '
    'and measures the perpendicular error of the reconstructed centreline against the ground truth. '
    '**xmlParse.py** sweeps all parameter combinations, aggregates statistics, and generates '
    'visualisations including IQR heatmaps and failure rate matrices.'
)

heading(2, '7.2. Why This Work Is Needed')
body(
    'Prior CERPM research [1][2] assumed complete marker availability. In practice, individual '
    'markers may fail due to battery depletion, physical damage, or communication loss, and entire '
    'stretches may drop out together due to flooding or road surface damage. Without knowing how '
    'each interpolation algorithm responds to these failure modes, a CERPM-based LKA system cannot '
    'be designed with confidence in its worst-case behaviour. This simulation provides that '
    'characterisation across a full parameter space of spacings and failure severities.'
)

heading(2, '7.3. Method Comparison and Justification')
add_table(
    ['Method', 'Continuity', 'Justification'],
    [
        ['Linear',           'C⁰', 'Current implicit default; baseline for comparison'],
        ['Quadratic spline', 'C¹', 'Smooth first derivative; low computational cost'],
        ['Cubic spline',     'C²', 'Used in prior CERPM work [1][2]; natural benchmark'],
        ['Quartic spline',   'C³', 'Tests benefit of one additional degree over cubic'],
        ['Quintic spline',   'C⁴', 'Upper bound on polynomial order tested'],
        ['PCHIP',            'C¹', 'Designed for sparse uneven data; avoids overshoot'],
        ['Akima',            'C¹', 'Locally weighted; limits propagation of gap effects'],
    ]
)
body(
    'Monte Carlo simulation (n = 2,000 per condition) was used because the interaction between '
    'dropout randomness, road geometry, and interpolation non-linearity has no tractable closed '
    'form. Convergence was verified: IQR estimates stabilised within 1% at approximately 1,500 '
    'trials, confirming 2,000 as sufficient. The 0.2 m maximum-error failure threshold was chosen '
    'to align with the sub-0.2 m positioning accuracy implied by ISO 21448 and SAE J3016 for '
    'lane-keeping applications.'
)

# ═════════════════════════════════════════════════════════════════════════════
# 8. PROJECT MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '8. Project Management')

heading(2, '8.1. Task Phases')
add_table(
    ['Phase', 'Key Tasks', 'Deliverable'],
    [
        ['1 — Scoping',
         'Literature review; identify gap in CERPM research; define failure modes and method shortlist',
         'Research questions; confirmed scope'],
        ['2 — Development',
         'Implement Lanelet2 parser; interpolation module; Monte Carlo simulation engine',
         'Working, tested codebase'],
        ['3 — Simulation',
         'Execute full parameter sweep; validate convergence at n = 2,000',
         'Complete results dataset'],
        ['4 — Analysis & Reporting',
         'Statistical aggregation; IQR and failure rate visualisation; report writing',
         'This report and all figures'],
    ]
)

heading(2, '8.2. Responsibilities')
body(
    'This is an individual sub-project within a group ADAS effort. All components — literature '
    'review, software development, simulation execution, statistical analysis, and report writing '
    '— were completed by the sole author. Results feed into the group\'s broader ADAS integration, '
    'providing the centreline estimate required by the LKA control sub-system.'
)

heading(2, '8.3. Timeline and Risk Management')
add_table(
    ['Week', 'Milestone'],
    [
        ['1–2',  'Literature review complete; research gap confirmed; supervisor sign-off on scope'],
        ['3–5',  'Lanelet2 parser and interpolation module implemented and unit-tested'],
        ['6–7',  'Monte Carlo engine complete; single-condition validation runs completed'],
        ['8–10', 'Full parameter sweep executed (all conditions, n = 2,000 per condition)'],
        ['11–12','Results analysis, IQR heatmaps, and failure rate matrices generated'],
        ['13–14','Report finalised and submitted'],
    ]
)
body(
    'Key risks and mitigations: numerical instability in high-order spline fitting with very few '
    'surviving points was addressed by implementing graceful fallbacks — Akima and cubic spline '
    'revert to linear when fewer than three points survive dropout. Computational runtime was '
    'managed by parallelising trials across all CPU cores using Python\'s ProcessPoolExecutor, '
    'reducing total sweep time from an estimated 18 hours serial to under 3 hours. Full '
    'reproducibility was ensured by deriving each trial seed from a master generator with a fixed '
    'base seed. All development was tracked in Git.'
)

# ═════════════════════════════════════════════════════════════════════════════
# 9. DELIVERABLE OUTCOMES
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '9. Deliverable Outcomes')

heading(2, '9.1. Analysis Program')
body(
    'A complete Python simulation program that: imports real road geometry from Lanelet2 OSM files; '
    'places CERPM positions along left and right road edges at configurable spacing, converting '
    'GPS/map coordinates to local metric x/y; applies configurable random or clustered dropout; '
    'runs seven interpolation algorithms on surviving markers; computes the reconstructed centreline; '
    'and measures error against the ground-truth centreline. Results are exported as structured '
    'datasets and visualisations.'
)

heading(2, '9.2. Interpolation Algorithm Comparison')
body('Key findings from the Monte Carlo sweep:')
bullet('**Quintic and quartic B-splines** achieved the lowest IQR and failure rates across all conditions, with near-zero failure rates under random dropout at ≤ 3 m spacing.')
bullet('**Cubic spline** — the method used in prior CERPM work [1][2] — performed well under random dropout but was outperformed by quartic and quintic at clustered dropout with large cluster sizes.')
bullet('**Linear interpolation** failed at rates of 93–100% (max error > 0.2 m) under clustered dropout at 5 m spacing, even for a cluster of just 2 consecutive markers.')
bullet('**PCHIP** showed intermediate performance; its monotonicity constraint, beneficial in other applications, produced flat reconstructions across large gaps in smooth road geometry, increasing error.')

heading(2, '9.3. CERPM Dropout Analysis')
bullet('**Clustered dropout is significantly more damaging** than random dropout at equivalent average dropout fractions. Removing 10 contiguous markers leaves a reconstruction gap across a continuous road section; the same 10 markers removed randomly leave local geometric information intact at most locations.')
bullet('**CERPM spacing is the dominant design variable.** Reducing spacing from 5 m to 2 m improves resilience across all methods and failure modes. At 1 m spacing, even linear interpolation is acceptable under random dropout up to 20%.')
bullet('**Recommended system design:** deploy CERPMs at ≤ 2 m on curved sections; use quintic or quartic B-spline interpolation; trigger fallback to camera sensing when clustered gaps of more than 10 consecutive markers are detected.')

# ═════════════════════════════════════════════════════════════════════════════
# 10. REFERENCES (IEEE, from abstract + added technical sources)
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '10. References')

refs = [
    '[1] S. Sharma, J. Rojas, A. R. Ekti, R. Wang, Z. Asher, and R. Meyer, "Vehicle Lateral Offset Estimation Using Infrastructure Information for Reduced Compute Load," SAE Technical Paper 2023-01-0800, Apr. 2023, doi: 10.4271/2023-01-0800.',
    '[2] P. Kadav et al., "Automated Lane Centering: An Off-the-Shelf Computer Vision Product vs. Infrastructure-Based Chip-Enabled Raised Pavement Markers," Sensors, vol. 24, no. 7, pp. 2327–2327, Apr. 2024, doi: 10.3390/s24072327.',
    '[3] Department of Infrastructure, Transport, Cities and Regional Development, "Fact sheet: Evidence supporting the priority focus areas," National Road Safety Strategy, 2021. [Online]. Available: https://www.roadsafety.gov.au/nrss/fact-sheets/priority-focus-areas',
    '[4] National Highway Traffic Safety Administration, "Estimating Effectiveness of Lane Keeping Assist Systems in Fatal Road Departure Crashes," NHTSA Report 813663, 2024.',
    '[5] European Commission, "Mandatory drivers assistance systems expected to help save over 25,000 lives by 2038," Internal Market, Industry, Entrepreneurship and SMEs, Jul. 2024.',
    '[6] Y. Wang, A. Alhuraish, S. Yuan, and H. Zhou, "OpenLKA: Open Source Multimodal LKA Dataset," GitHub, 2025. [Online]. Available: https://github.com/OpenLKA/OpenLKA',
    '[7] I. Fakhari and S. Anwar, "A Multiple Model Estimation Approach to Robust Lane Detection via Computer Vision Based Models," in Proc. IEEE ISIE, 2022, pp. 576–581, doi: 10.1109/isie51582.2022.9831692.',
    '[8] I. Fakhari and S. Anwar, "Computer vision model based robust lane detection using multiple model adaptive estimation methodology," Frontiers in Mechanical Engineering, vol. 11, Feb. 2025, doi: 10.3389/fmech.2025.1436338.',
    '[9] G. Perozzi, J. J. Rath, C. Sentouh, J. Floris, and J.-C. Popieul, "Lateral Shared Sliding Mode Control for Lane Keeping Assist System in Steer-by-Wire Vehicles," IEEE Trans. Intelligent Vehicles, vol. 8, no. 4, pp. 3073–3082, Apr. 2023, doi: 10.1109/tiv.2021.3097352.',
    '[10] S. Wei, P. E. Pfeffer, and J. Edelmann, "State of the Art: Ongoing Research in Assessment Methods for Lane Keeping Assistance Systems," IEEE Trans. Intelligent Vehicles, vol. 9, no. 9, pp. 5853–5875, Sep. 2024, doi: 10.1109/tiv.2023.3269156.',
    '[11] F. Poggenhans et al., "Lanelet2: A high-definition map framework for the future of automated driving," in Proc. IEEE ITSC, 2018, pp. 1672–1679.',
    '[12] F. N. Fritsch and R. E. Carlson, "Monotone piecewise cubic interpolation," SIAM J. Numerical Analysis, vol. 17, no. 2, pp. 238–246, 1980.',
    '[13] H. Akima, "A new method of interpolation and smooth curve fitting based on local procedures," J. ACM, vol. 17, no. 4, pp. 589–602, 1970.',
]

for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.first_line_indent = Cm(-1)
    r = p.add_run(ref)
    r.font.name = FONT
    r.font.size = BODY_SIZE

doc.save('/home/user/road-writing/Report.docx')
print("Done.")
