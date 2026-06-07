from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

FONT = 'Times New Roman'
BODY_SIZE = Pt(12)
HEAD_SIZE = Pt(12)

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Global default font ───────────────────────────────────────────────────────
normal = doc.styles['Normal']
normal.font.name = FONT
normal.font.size = BODY_SIZE

for h_name in ['Heading 1', 'Heading 2', 'Heading 3']:
    s = doc.styles[h_name]
    s.font.name  = FONT
    s.font.size  = HEAD_SIZE
    s.font.bold  = True
    s.font.color.rgb = RGBColor(0, 0, 0)

# ── Helpers ───────────────────────────────────────────────────────────────────
def body(text, bold_parts=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    _render(p, text)
    return p

def _render(p, text):
    """Render **bold** markdown within a paragraph."""
    parts = re.split(r'\*\*(.*?)\*\*', text)
    for i, part in enumerate(parts):
        r = p.add_run(part)
        r.font.name = FONT
        r.font.size = BODY_SIZE
        if i % 2 == 1:
            r.bold = True

def heading(level, text):
    h = doc.add_heading('', level)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after  = Pt(4)
    r = h.runs[0] if h.runs else h.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = HEAD_SIZE
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

def bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    _render(p, text)

def table(headers, rows):
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
# TITLE PAGE
# ═════════════════════════════════════════════════════════════════════════════
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run('Interpolation Method Robustness for Road Centreline\nReconstruction Under CERPM Dropout Conditions')
r.font.name = FONT
r.font.size = Pt(16)
r.bold = True

for label, value in [('Author:', 'Alexander Bruce'), ('Date:', 'June 2026'), ('Module:', 'Research Project')]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(f'{label}  ')
    r1.bold = True
    r1.font.name = FONT
    r1.font.size = BODY_SIZE
    r2 = p.add_run(value)
    r2.font.name = FONT
    r2.font.size = BODY_SIZE

doc.add_paragraph()

# ═════════════════════════════════════════════════════════════════════════════
# 2. EXECUTIVE SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '2. Executive Summary')
body(
    "This report investigates which interpolation method most robustly reconstructs road centrelines "
    "from incomplete Cat's Eye Road Position Marker (CERPM) boundary data. Seven methods — linear, "
    "quadratic, cubic spline, quartic, quintic, PCHIP, and Akima — were evaluated using Monte Carlo "
    "simulation (n = 2,000 runs per condition) across two failure modes: random marker dropout (1–20%) "
    "and clustered contiguous dropout (cluster sizes 2–20 markers), tested at five CERPM spacings "
    "(0.5 m to 5.0 m). Reconstruction accuracy was measured as the perpendicular distance from the "
    "reconstructed centreline to a Lanelet2 ground-truth centreline."
)
body(
    "Higher-order polynomial B-splines (quadratic, cubic spline, quartic, quintic) consistently "
    "outperformed linear interpolation, PCHIP, and Akima across all conditions. Linear interpolation "
    "failed at failure rates of up to 100% under clustered dropout at 5 m spacing. Quintic and quartic "
    "B-splines are recommended as the default algorithm for any CERPM-based road geometry system, "
    "combined with a marker spacing of 2 m or finer on curved road sections."
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
        r.font.name = FONT
        r.font.size = BODY_SIZE

doc.add_paragraph()

# ═════════════════════════════════════════════════════════════════════════════
# 4. STATEMENT OF PROBLEM
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '4. Statement of Problem')
body(
    "Cat's Eye Road Position Markers embedded in road surfaces can provide real-time road boundary "
    "geometry to connected and autonomous vehicles (CAVs). However, no sensor network operates without "
    "data loss. Individual markers may fail to report due to battery depletion, physical damage, "
    "flooding, or wireless communication congestion. When markers drop out, the receiving system must "
    "reconstruct the missing boundary geometry algorithmically. The wrong algorithm can introduce "
    "lateral positioning errors exceeding the 0.2 m safety margin required by autonomous driving "
    "standards [1], potentially causing unsafe lane positioning or collision."
)
body(
    "The core problem is that no systematic, evidence-based comparison of interpolation methods exists "
    "for this specific application. Practitioners currently default to linear interpolation — the "
    "simplest option — without quantitative justification. This project addresses that gap by "
    "providing a statistically rigorous, simulation-based ranking of seven candidate algorithms "
    "across a comprehensive parameter space of marker spacings and failure severities."
)

# ═════════════════════════════════════════════════════════════════════════════
# 5. INTRODUCTION
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '5. Introduction')
body(
    "This project evaluates seven interpolation methods for reconstructing road centrelines from "
    "incomplete CERPM boundary data, using Monte Carlo simulation over a Lanelet2 road map. The aim "
    "is to determine which method is most resilient to data loss, and to define the conditions under "
    "which each method fails. The output is actionable guidance for engineers and infrastructure "
    "managers selecting algorithms for CERPM-based road systems."
)
body(
    "Road centreline reconstruction is a well-defined geometric problem: given a subset of left and "
    "right road boundary points, reconstruct the boundary curves and compute their midpoint at each "
    "location. The challenge lies in how well different curve-fitting algorithms extrapolate across "
    "gaps — segments where markers are missing — particularly for curved road sections where a naive "
    "straight-line approximation introduces significant lateral error."
)
body(
    "The project targets two distinct failure modes: random independent dropout (modelling sporadic "
    "sensor faults distributed across the network) and clustered contiguous dropout (modelling a "
    "localised zone of failure, such as a flooded road section or a stretch of physical damage). "
    "Both are operationally relevant and place different demands on the reconstruction algorithm. "
    "Random dropout preserves local geometric information at most locations; clustered dropout "
    "removes all geometric information across an extended stretch, demanding that the algorithm "
    "extrapolate across the gap using only the shape of the road on either side."
)

# ═════════════════════════════════════════════════════════════════════════════
# 6. BACKGROUND
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '6. Background')

heading(2, '6.1. Relevance and Importance')
body(
    "The UK government's CAV roadmap and the EU C-Roads programme both identify infrastructure-based "
    "positioning as a key enabler for Level 3+ vehicle automation. CERPMs offer a low-cost, "
    "weather-independent complement to on-vehicle sensing, but their utility depends entirely on the "
    "accuracy of centreline reconstruction when data is incomplete. ISO 21448 (Safety of the Intended "
    "Functionality) and SAE J3016 imply sub-0.2 m positioning accuracy requirements for lane-keeping "
    "assistance [1][2], making algorithm selection safety-critical."
)

heading(2, '6.2. Literature Review')
body(
    "Polynomial spline interpolation is well established in numerical analysis. Burden and Faires [3] "
    "describe natural cubic splines (C² continuous), which enforce zero second derivative at endpoints "
    "but can exhibit Runge oscillations with sparse data. Fritsch and Carlson [4] introduced PCHIP to "
    "address this by enforcing monotonicity in each interval, preventing overshoot. Akima [5] proposed "
    "a locally-weighted spline that limits the influence of distant data on local curve shape. B-splines "
    "of degree k (de Boor [6]) provide a unified framework for linear (k=1) through quintic (k=5) "
    "interpolants. All methods tested here use arc-length parameterisation — computing a normalised "
    "cumulative chord length t ∈ [0,1] — following Hartley and Zisserman [7], which prevents the "
    "systematic distortion introduced by naive index-based parameterisation."
)
body(
    "Dropout modelling in road sensor networks has precedent from inductive loop detector studies [8]. "
    "Toth and Jóźków [9] note that sensor occlusion produces spatially correlated gaps, supporting "
    "the relevance of a clustered failure model alongside random dropout. Levinson et al. [10] "
    "demonstrate that HD map quality directly affects autonomous vehicle safety margins, reinforcing "
    "the importance of robust boundary reconstruction."
)

heading(2, '6.3. Legal, Environmental and Ethical Considerations')
body(
    "An interpolation algorithm embedded in an autonomous driving pipeline is safety-critical software. "
    "UK Product Safety and Telecommunications Product Safety regulations, and the emerging EU AI Act, "
    "impose obligations to validate and document algorithm performance before deployment. This project "
    "contributes to that validation evidence base. Environmental considerations are minimal — the "
    "study is computational — but the results may influence physical CERPM deployment density: a "
    "recommendation to halve marker spacing from 5 m to 2 m roughly doubles material and installation "
    "costs, so evidence that finer spacing is necessary carries direct economic weight. There are no "
    "identified ethical concerns specific to the algorithmic comparison itself, though any system "
    "used to guide autonomous vehicles in safety-critical scenarios requires appropriate human "
    "oversight and fail-safe mechanisms regardless of the reconstruction algorithm selected."
)

# ═════════════════════════════════════════════════════════════════════════════
# 7. STRATEGY
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '7. Strategy')

heading(2, '7.1. What Work Was Done')
body(
    "A Python simulation framework was developed comprising four modules: **test.py** (Lanelet2 OSM "
    "map parser and road geometry utilities), **Interpolations.py** (seven interpolation method "
    "implementations with arc-length parameterisation), **Simulation.py** (Monte Carlo simulation "
    "engine with parallel execution), and **xmlParse.py** (analysis pipeline and visualisation). "
    "The Town07 Lanelet2 map was used as the ground-truth road geometry source."
)
body(
    "For each of 70 parameter combinations (7 methods × 5 intervals × 2 dropout modes × varying "
    "severities), 2,000 independent Monte Carlo trials were executed. Each trial: (1) resampled "
    "road boundaries to the target CERPM interval; (2) applied random or clustered dropout; "
    "(3) interpolated surviving markers to reconstruct boundaries; (4) computed a centreline from "
    "reconstructed boundaries; (5) measured perpendicular error against the ground-truth centreline."
)

heading(2, '7.2. Why This Work Is Needed')
body(
    "Linear interpolation — the current implicit default — assumes road geometry is piecewise straight. "
    "This is accurate only at very fine marker spacings. At spacings of 2 m or more, linear "
    "interpolation on a curved road section introduces a chord-midpoint error proportional to the "
    "square of the gap length. Higher-order methods can exploit the smoothness of real road geometry "
    "to extrapolate across gaps far more accurately. Without a systematic comparison, practitioners "
    "have no evidence base for selecting an alternative — this project provides it."
)

heading(2, '7.3. Method Comparison and Justification')
table(
    ['Method', 'Continuity', 'Key Property', 'Justification for Inclusion'],
    [
        ['Linear',           'C⁰', 'Piecewise straight',         'Baseline; current implicit default'],
        ['Quadratic spline', 'C¹', 'Smooth; limited curvature',  'Low-cost step above linear'],
        ['Cubic spline',     'C²', 'Natural; zero 2nd deriv.',   'Standard smooth interpolant'],
        ['Quartic spline',   'C³', 'Higher-order curvature',     'Tests benefit of added degree'],
        ['Quintic spline',   'C⁴', 'Very smooth',                'Upper bound on polynomial order'],
        ['PCHIP',            'C¹', 'Monotone; no overshoot',     'Designed for sparse uneven data'],
        ['Akima',            'C¹', 'Locally weighted',           'Resilient to propagation of gaps'],
    ]
)
body(
    "Monte Carlo simulation was chosen over analytical methods because the interaction of dropout "
    "randomness, road geometry, and interpolation non-linearity has no tractable closed form. "
    "2,000 trials per condition was validated by convergence analysis — IQR estimates stabilised "
    "within 1% relative change beyond ~1,500 runs."
)

# ═════════════════════════════════════════════════════════════════════════════
# 8. PROJECT MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '8. Project Management')

heading(2, '8.1. Task Phases')
table(
    ['Phase', 'Tasks', 'Deliverable'],
    [
        ['1 — Scoping',          'Literature review; define failure modes; shortlist methods', 'Research questions, method list'],
        ['2 — Development',      'Implement parser, interpolation module, simulation engine',   'Working codebase'],
        ['3 — Simulation',       'Run Monte Carlo sweeps; validate convergence',                'Full results dataset'],
        ['4 — Analysis & Report','Statistical analysis; visualisation; report writing',         'This report + figures'],
    ]
)

heading(2, '8.2. Responsibilities')
body(
    "This is an individual project. All components — literature review, software development, "
    "simulation execution, analysis, and report writing — were completed by the sole author. "
    "Supervisory input was received at phase boundaries to review scope and direction."
)

heading(2, '8.3. Timeline')
body(
    "The project followed a four-phase sequential schedule across the semester. Key milestones:"
)
table(
    ['Week', 'Milestone'],
    [
        ['1–2',  'Literature review complete; research questions agreed with supervisor'],
        ['3–5',  'map parser and interpolation module implemented and unit-tested'],
        ['6–7',  'Simulation engine complete; initial single-condition test runs validated'],
        ['8–10', 'Full Monte Carlo sweep executed (all 70 parameter combinations, n=2,000)'],
        ['11–12','Results analysis and visualisation complete'],
        ['13–14','Report written and submitted'],
    ]
)
body(
    "Risk management was active throughout. Numerical instability in high-order spline fitting with "
    "few surviving points was mitigated by implementing graceful fallbacks: Akima and cubic spline "
    "revert to linear interpolation when fewer than three points survive dropout, ensuring a result "
    "is always produced without crashing. Computational time was managed by parallelising trials "
    "across all available CPU cores using Python's ProcessPoolExecutor, reducing full sweep time "
    "from an estimated 18 hours serial to under 3 hours parallel. Reproducibility was ensured by "
    "deriving each trial's random seed from a master generator with a fixed base seed, so the entire "
    "simulation can be re-run and produce bit-identical results. All code was version-controlled "
    "with Git, providing a traceable record of incremental development and design decisions."
)

# ═════════════════════════════════════════════════════════════════════════════
# 9. DELIVERABLE OUTCOMES
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '9. Deliverable Outcomes')

heading(2, '9.1. Software')
bullet("**test.py** — Lanelet2 OSM parser; road boundary extraction; CERPM resampling; centreline computation.")
bullet("**Interpolations.py** — Seven interpolation methods with arc-length parameterisation; graceful fallbacks.")
bullet("**Simulation.py** — Parallelised Monte Carlo engine; random and clustered dropout models; error measurement.")
bullet("**xmlParse.py** — Full analysis pipeline; IQR and failure rate computation; eight visualisation types.")

heading(2, '9.2. Results')
body(
    "Key findings from the simulation sweep:"
)
bullet("**Quintic and quartic B-splines** achieved the lowest IQR and failure rates across all tested conditions.")
bullet("**Linear interpolation** reached failure rates of 93–100% (max error > 0.2 m) under clustered dropout at 5 m spacing, even for a cluster of just 2 markers.")
bullet("**Clustered dropout is more damaging than random dropout** at equivalent effective dropout fractions — removing 10 contiguous markers is far worse than randomly removing 10 scattered markers from the same boundary.")
bullet("**At 1 m or finer spacing**, all methods perform acceptably under random dropout up to 20%; algorithm choice matters most at 2–5 m spacing.")
bullet("**PCHIP** underperformed relative to pure polynomial B-splines at large clustered gaps because its monotonicity constraint, designed to prevent oscillation in step-like data, produces flat reconstructions across gaps in road geometry that is smooth but not monotone in individual x or y coordinates. This makes PCHIP a poor fit for curved road sections despite its success in other engineering applications.")

heading(2, '9.3. Recommendations for Practitioners')
body(
    "Based on the simulation results, the following guidance is offered to infrastructure engineers, "
    "road asset managers, and system architects deploying CERPM-based road geometry systems. These "
    "recommendations are grounded in quantitative failure rates across 2,000 trials per condition "
    "and are intended to be directly actionable without requiring specialist knowledge of "
    "interpolation theory:"
)
bullet("Use **quintic or quartic B-spline interpolation** with arc-length parameterisation as the default reconstruction algorithm.")
bullet("Deploy CERPMs at **≤ 2 m spacing** on curved road sections; 5 m spacing is insufficient for robust reconstruction under any realistic dropout scenario.")
bullet("Implement **system-level alerts** when clustered gaps of more than 10 consecutive markers are detected, triggering fallback to on-vehicle sensing or a prior HD map.")
bullet("Do not use **linear interpolation** in any production road geometry reconstruction system at marker spacings above 1 m.")

# ═════════════════════════════════════════════════════════════════════════════
# 10. REFERENCES (IEEE style)
# ═════════════════════════════════════════════════════════════════════════════
heading(1, '10. References')

refs = [
    "[1] ISO 21448:2022, Road Vehicles — Safety of the Intended Functionality, International Organisation for Standardisation, 2022.",
    "[2] SAE International, SAE J3016: Taxonomy and Definitions for Terms Related to Driving Automation Systems for On-Road Motor Vehicles, 2021.",
    "[3] R. L. Burden and J. D. Faires, Numerical Analysis, 9th ed. Brooks/Cole, 2011.",
    "[4] F. N. Fritsch and R. E. Carlson, \"Monotone piecewise cubic interpolation,\" SIAM Journal on Numerical Analysis, vol. 17, no. 2, pp. 238–246, 1980.",
    "[5] H. Akima, \"A new method of interpolation and smooth curve fitting based on local procedures,\" Journal of the ACM, vol. 17, no. 4, pp. 589–602, 1970.",
    "[6] C. de Boor, A Practical Guide to Splines, Revised ed. Springer, 2001.",
    "[7] R. Hartley and A. Zisserman, Multiple View Geometry in Computer Vision, 2nd ed. Cambridge University Press, 2003.",
    "[8] B. Coifman, \"Estimating travel times and vehicle trajectories on freeways using dual loop detectors,\" Transportation Research Part A, vol. 36, no. 4, pp. 351–364, 2002.",
    "[9] C. Toth and G. Jóźków, \"Remote sensing platforms and sensors: A survey,\" ISPRS Journal of Photogrammetry and Remote Sensing, vol. 115, pp. 22–36, 2016.",
    "[10] J. Levinson, M. Montemerlo, and S. Thrun, \"Map-based precision vehicle localisation in urban environments,\" in Proc. Robotics: Science and Systems, 2011.",
    "[11] F. Poggenhans et al., \"Lanelet2: A high-definition map framework for the future of automated driving,\" in Proc. IEEE Intelligent Transportation Systems Conference (ITSC), 2018, pp. 1672–1679.",
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
