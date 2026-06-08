"""
Generates Final_Report.docx based on main branch.
Scenarios: random, clustered (no images), gap-length.
Intervals: 0.5, 1.0, 2.0, 4.0, 6.0, 12.0 m
Random dropout rates: 10%, 15%, 20%, 25%
Gap lengths: 2, 5, 10, 15, 20 m  |  Cluster sizes: 2, 5, 10, 15, 20 markers
Geometries: Town07, Town041, Town042, Town044
"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

IMG = {
    # Town07 – sinuous
    't07_road':        'Results/Town07G/Figure_1.png',
    't07_rand_heatmap':'Results/Town07G/random_iqr_heatmap - Copy.png',
    't07_rand_bands':  'Results/Town07G/random_iqr_bands.png',
    't07_rand_fail':   'Results/Town07G/random_failure_rate.png',
    't07_gap_heatmap': 'Results/Town07G/gaplength_iqr_heatmap.png',
    't07_gap_bands':   'Results/Town07G/gaplength_iqr_bands.png',
    't07_gap_fail':    'Results/Town07G/gaplength_failure_rate.png',
    # Town041 – large semicircle
    't41_road':        'Results/Town041G/Figure_1.png',
    't41_rand_heatmap':'Results/Town041G/random_iqr_heatmap.png',
    't41_rand_bands':  'Results/Town041G/random_iqr_bands.png',
    't41_rand_fail':   'Results/Town041G/random_failure_rate.png',
    't41_gap_heatmap': 'Results/Town041G/gaplength_iqr_heatmap.png',
    't41_gap_bands':   'Results/Town041G/gaplength_iqr_bands.png',
    't41_gap_fail':    'Results/Town041G/gaplength_failure_rate.png',
    # Town042 – gradual curve
    't42_road':        'Results/Town042G/Figure_1.png',
    't42_rand_heatmap':'Results/Town042G/random_iqr_heatmap.png',
    't42_rand_bands':  'Results/Town042G/random_iqr_bands.png',
    't42_rand_fail':   'Results/Town042G/random_failure_rate.png',
    't42_gap_heatmap': 'Results/Town042G/gaplength_iqr_heatmap.png',
    't42_gap_bands':   'Results/Town042G/gaplength_iqr_bands.png',
    't42_gap_fail':    'Results/Town042G/gaplength_failure_rate.png',
    # Town044 – sharp corners
    't44_road':        'Results/Town044G/Figure_1.png',
    't44_rand_heatmap':'Results/Town044G/random_iqr_heatmap.png',
    't44_rand_bands':  'Results/Town044G/random_iqr_bands.png',
    't44_rand_fail':   'Results/Town044G/random_failure_rate.png',
    't44_gap_heatmap': 'Results/Town044G/gaplength_iqr_heatmap.png',
    't44_gap_bands':   'Results/Town044G/gaplength_iqr_bands.png',
    't44_gap_fail':    'Results/Town044G/gaplength_failure_rate.png',
}


def shade_cell(cell, hex_colour):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_colour)
    shd.set(qn('w:val'), 'clear')
    tcPr.append(shd)

def heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    return p

def body(doc, text, space_after=5):
    p = doc.add_paragraph(text)
    p.style = doc.styles['Normal']
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    for run in p.runs:
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
    return p

def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run(text)
    run.font.name = 'Calibri'; run.font.size = Pt(9)
    run.italic = True
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    return p

def figure(doc, key, cap, width=Inches(6.0)):
    path = IMG.get(key)
    if path and os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(2)
        p.add_run().add_picture(path, width=width)
    caption(doc, cap)

def tbl_row(tbl, cells, bold=False, bg=None):
    row = tbl.add_row()
    for i, text in enumerate(cells):
        row.cells[i].text = text
        for run in row.cells[i].paragraphs[0].runs:
            run.font.name = 'Calibri'; run.font.size = Pt(10); run.bold = bold
        if bg:
            shade_cell(row.cells[i], bg)
    return row

def tbl_header(tbl, cols):
    for i, h in enumerate(cols):
        tbl.rows[0].cells[i].text = h
        for run in tbl.rows[0].cells[i].paragraphs[0].runs:
            run.bold = True; run.font.name = 'Calibri'; run.font.size = Pt(10)
        shade_cell(tbl.rows[0].cells[i], 'BDD7EE')


# ─────────────────────────────────────────────
doc = Document()
for section in doc.sections:
    section.top_margin = Cm(2.5); section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5); section.right_margin  = Cm(2.5)

# ══════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════
for _ in range(5):
    doc.add_paragraph()
tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run('Interpolation Algorithm Evaluation for\nCERPM-Based Lane Keep Assist Systems')
r.font.name = 'Calibri'; r.font.size = Pt(20); r.bold = True
doc.add_paragraph()
sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sp.add_run('Final Research Thesis')
r2.font.name = 'Calibri'; r2.font.size = Pt(13); r2.italic = True
doc.add_paragraph()
for label, value in [('Unit:', 'Advanced Driver Assistance Systems Research Project'),
                     ('Author:', 'Alexander Bruce'), ('Date:', 'June 2026')]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rb = p.add_run(label + ' '); rb.bold = True; rb.font.name = 'Calibri'; rb.font.size = Pt(12)
    rv = p.add_run(value); rv.font.name = 'Calibri'; rv.font.size = Pt(12)
doc.add_paragraph()
cp = doc.add_paragraph(); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
rch = cp.add_run('Student Contribution: '); rch.bold = True; rch.font.name = 'Calibri'; rch.font.size = Pt(11)
rct = cp.add_run(
    'Alexander Bruce was solely responsible for the LKA subsystem within the group ADAS '
    'project: problem definition, literature review, full Python simulation development '
    '(road geometry parsing, CERPM resampling, Monte Carlo engine, visualisation), '
    'experiment execution across four road geometries, and all results analysis.')
rct.font.name = 'Calibri'; rct.font.size = Pt(11)
doc.add_page_break()

# ══════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════
heading(doc, 'Abstract', level=1)
body(doc,
    'Lane Keep Assist (LKA) is a critical ADAS safety feature that prevents unintentional '
    'lane departures through corrective steering. Current camera-based implementations '
    'degrade significantly under poor lane markings and adverse weather. This project '
    'investigates a Vehicle-to-Infrastructure (V2I) alternative using Chip Enabled Raised '
    'Pavement Markers (CERPMs), which broadcast GPS lane-boundary coordinates directly to '
    'the vehicle. Seven interpolation algorithms (linear, quadratic, cubic spline, quartic, '
    'quintic, PCHIP, Akima) were evaluated for lane centreline accuracy using a Python '
    'Monte Carlo simulation framework across four real-world road geometries and three '
    'CERPM dropout scenarios: random, clustered, and gap-length. At 0.5–1.0 m spacing '
    'all methods achieve sub-centimetre median error. Beyond 2.0 m smooth methods '
    'substantially outperform linear and quadratic. Akima is the most consistently '
    'robust method across all geometry types, including sharp-corner roads where PCHIP '
    'degrades due to its monotonicity constraint. Concrete spacing and algorithm '
    'recommendations are provided.')
doc.add_page_break()

# ══════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════
heading(doc, 'Table of Contents', level=1)
for num, title in [
    ('1.', 'Introduction'), ('2.', 'Literature Review'), ('3.', 'Methodology'),
    ('4.', 'Results and Analysis'), ('5.', 'Conclusions and Recommendations'),
    ('6.', 'References'), ('7.', 'Appendices'),
]:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(num + '  ' + title)
    r.font.name = 'Calibri'; r.font.size = Pt(11); r.bold = True
doc.add_page_break()

# ══════════════════════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════════════════════
heading(doc, '1. Introduction', level=1)
body(doc,
    'Lane departure — run-off-road and head-on collisions — accounts for 62% of Australian '
    'road fatalities nationally, rising to 73% in regional areas [3]. The NHTSA estimates '
    'LKA-equipped vehicles are 24% less likely to be involved in a fatal road departure '
    'crash [4]. From July 2024, the European Commission mandated LKA on all new EU '
    'vehicles, projecting over 25,000 lives saved by 2038 [5]. LKA also underpins '
    'higher-order ADAS autonomous functions.')
body(doc,
    'Current production LKA relies on forward-facing cameras to detect lane markings. '
    'Field evidence confirms significant degradation under worn markings, adverse weather, '
    'and lane transitions [6]. Chip Enabled Raised Pavement Markers (CERPMs) offer a V2I '
    'alternative: road-embedded devices transmit GPS lane-boundary coordinates to the '
    'vehicle (range up to 350 m), enabling centreline estimation entirely independent of '
    'visual conditions. Kadav et al. [2] demonstrated CERPM-based lane centering '
    'outperformed the Mobileye 630 commercial system across all tested conditions. However, '
    'neither this study nor its predecessor [1] investigated interpolation algorithm '
    'selection or system behaviour under CERPM failures.')
body(doc,
    'This project fills these gaps by: (1) evaluating seven interpolation algorithms '
    'across four road geometries; (2) characterising how random, clustered, and '
    'gap-length CERPM dropout degrade accuracy; and (3) providing algorithm and '
    'spacing recommendations for real-world deployment.')

# ══════════════════════════════════════════════
# 2. LITERATURE REVIEW
# ══════════════════════════════════════════════
heading(doc, '2. Literature Review', level=1)
body(doc,
    'The OpenLKA dataset [6] — 400 hours of real-world LKA data from 62 production '
    'vehicles — empirically confirms that deep-learning LKA systems fail at high rates '
    'under degraded lane markings and near lane transitions, establishing the performance '
    'ceiling of camera-based approaches. Fakhari and Anwar [7][8] improved robustness '
    'with a Multiple Model Adaptive Estimation (MMAE) Kalman filter fusing front and rear '
    'cameras, but their system remains dependent on a minimum level of marking quality.')
body(doc,
    'Sharma et al. [1] and Kadav et al. [2] validated the CERPM V2I concept, showing '
    'CERPMs outperform the Mobileye 630 on sharp curves, degraded markings, and variable '
    'lighting, with ten times the detection range. Neither study addressed interpolation '
    'algorithm choice or marker failure effects — the gap this project fills.')
body(doc,
    'All seven methods evaluated use arc-length parameterisation (t ∈ [0,1] = normalised '
    'path distance), interpolating x and y independently. Linear interpolation (C⁰) is the '
    'piecewise-straight baseline. Cubic spline (C², natural endpoint conditions) is the '
    'standard smooth engineering interpolator and implicit prior CERPM default. Higher '
    'degree B-splines (quadratic k=2, quartic k=4, quintic k=5) provide increasing '
    'smoothness but growing endpoint sensitivity. PCHIP enforces C¹ monotone cubic '
    'construction — no overshoot, robust on sparse smooth data, but constrained at '
    'sharp curvature reversals. Akima uses locally weighted C¹ cubic slopes so a single '
    'gap does not propagate oscillation to neighbouring segments.')
body(doc,
    'Perozzi et al. [9] proposed a sliding-mode shared controller for steer-by-wire LKA '
    'that represents the control layer upon which this perception work would operate. '
    'Wei et al. [10] review LKA assessment frameworks, identifying standardisation gaps '
    'relevant to future CERPM-based LKA evaluation.')

# ══════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════
heading(doc, '3. Methodology', level=1)
body(doc,
    'A simulation-based approach enables controlled, exhaustive testing across parameter '
    'combinations impractical to replicate physically. All code was implemented in Python '
    'using NumPy, SciPy, Shapely, and Matplotlib across four modules: test.py (geometry '
    'parsing, CERPM resampling, centreline computation), Interpolations.py (arc-length '
    'parameterisation and all seven methods via SciPy), Simulation.py (Monte Carlo engine '
    'with ProcessPoolExecutor parallel execution), and xmlParse.py (parameter sweeps '
    'and all visualisation).')

heading(doc, 'Road Geometries', level=2)
body(doc,
    'Four road geometries were parsed from Lanelet2 OSM files encoding each lane as left '
    'and right boundary ways with local Cartesian coordinates in metres. Town07 is a '
    'sinuous S-curve (~280 m, multiple curvature reversals — hardest). Town041 is a '
    'large near-semicircular road (~600 m, very smooth consistent curvature). Town042 '
    'is a long gradual curve (~560 m). Town044 has two sharp 90° corners (~520 m — '
    'tests abrupt curvature reversal). Consecutive lanelets were chain-linked into '
    'continuous boundary polylines by matching end/start nodes.')

heading(doc, 'CERPM Simulation and True Centreline', level=2)
body(doc,
    'CERPMs were simulated by resampling boundary polylines at six uniform intervals: '
    '0.5, 1.0, 2.0, 4.0, 6.0, and 12.0 m using Shapely\'s LineString.interpolate. '
    'The ground-truth centreline was computed at 0.5 m intervals using a '
    'perpendicular-nearest-point algorithm: for each boundary sample point, the nearest '
    'point on the opposite boundary is found by projection, and their midpoint taken.')

heading(doc, 'Dropout Scenarios', level=2)
body(doc,
    'Three dropout models were implemented. Random dropout: each CERPM independently '
    'fails with probability p (10%, 15%, 20%, 25%); 2,000 Monte Carlo trials per '
    'condition. Clustered dropout: a contiguous block of n consecutive CERPMs '
    '(sizes: 2, 5, 10, 15, 20) is removed from a randomly chosen side at a randomly '
    'chosen start position; 2,000 trials per condition. Gap-length dropout: a contiguous '
    'block equivalent to a physical gap of g metres (2, 5, 10, 15, 20 m) is removed; '
    'every valid start position on both boundaries is tested exhaustively.')

heading(doc, 'Error Metrics', level=2)
body(doc,
    'Per trial, the reconstructed centreline error is the Euclidean distance from each '
    'estimated centreline point to the nearest point on the true centreline LineString. '
    'Mean and max errors are recorded. A trial is a failure if max error exceeds 0.2 m — '
    'based on the 3.5 m standard lane width and ±0.3 m LKA intervention threshold. '
    'Results are summarised by P25, P75, IQR = P75 − P25, and failure rate (% of '
    'trials exceeding 0.2 m max error).')

# ══════════════════════════════════════════════
# 4. RESULTS AND ANALYSIS
# ══════════════════════════════════════════════
heading(doc, '4. Results and Analysis', level=1)

heading(doc, '4.1 Road Geometries', level=2)
body(doc,
    'Figures 1–4 show the resampled boundary polylines for each road geometry. The four '
    'geometries span a wide spectrum of curvature complexity, from the smoothly curved '
    'semicircle (Town041) to the sharply cornered Town044.')

figure(doc, 't07_road',
       'Figure 1. Town07 — sinuous road (~280 m). Multiple curvature reversals; most challenging.',
       width=Inches(4.5))
figure(doc, 't41_road',
       'Figure 2. Town041 — large near-semicircular road (~600 m). Very smooth, consistent curvature.',
       width=Inches(3.5))
figure(doc, 't42_road',
       'Figure 3. Town042 — long gradual curve (~560 m). Smooth gentle bends.',
       width=Inches(3.8))
figure(doc, 't44_road',
       'Figure 4. Town044 — sharp-corner road (~520 m). Two 90° turns; tests abrupt curvature changes.',
       width=Inches(4.5))

heading(doc, '4.2 Effect of CERPM Spacing (Baseline)', level=2)
body(doc,
    'At 0.5 m and 1.0 m spacing all seven methods produce median centreline errors below '
    '0.01 m with near-zero IQR across all four geometries — algorithm choice is irrelevant '
    'at these densities. From 2.0 m onwards the methods diverge: linear IQR rises '
    'measurably, while smooth methods remain low. At 4.0 m linear is unacceptably '
    'degraded on all curved roads. At 6.0 m and 12.0 m linear reaches 100% failure '
    'under any dropout on all geometries except on the very smoothest sections of '
    'Town041 and Town042.')

heading(doc, '4.3 Random Dropout', level=2)
body(doc,
    'Figures 5–16 show IQR heatmaps, IQR band plots, and failure rate heatmaps for all '
    'four geometries under random dropout (10%–25%). Consistent patterns across geometries:')
body(doc,
    'At 0.5–1.0 m all methods maintain near-zero failure across all dropout rates. '
    'At 2.0 m linear fails significantly on curved roads (43–97% on Town07), while '
    'smooth methods remain near 0%. Town041 (smooth semicircle) is the most resistant: '
    'smooth methods stay below 5% failure at all spacings up to 6.0 m, and linear only '
    'begins failing above 4.0 m spacing.')
body(doc,
    'A critical finding emerges on Town044 (sharp corners): PCHIP reaches 46–88% '
    'failure at 4.0 m spacing (10%–25% dropout) — substantially worse than Akima '
    '(12–58%). PCHIP\'s monotonicity constraint prevents it from representing abrupt '
    '90° curvature reversals when markers near the corner are lost. Akima\'s local '
    'slope weighting handles this adaptively, making it the more robust general-purpose choice.')

figure(doc, 't07_rand_heatmap',
       'Figure 5. Town07 — Random dropout IQR centreline error (P25–P75, m). n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't07_rand_bands',
       'Figure 6. Town07 — Random dropout IQR band plots per method.',
       width=Inches(5.5))
figure(doc, 't07_rand_fail',
       'Figure 7. Town07 — Random dropout failure rate (max error > 0.2 m, %).',
       width=Inches(6.0))
figure(doc, 't41_rand_heatmap',
       'Figure 8. Town041 — Random dropout IQR centreline error. Smooth geometry; only linear degrades significantly.',
       width=Inches(6.0))
figure(doc, 't41_rand_bands',
       'Figure 9. Town041 — Random dropout IQR band plots. All smooth methods show near-flat bands.',
       width=Inches(5.5))
figure(doc, 't41_rand_fail',
       'Figure 10. Town041 — Random dropout failure rate. Linear uniquely fails at 6.0–12.0 m.',
       width=Inches(6.0))
figure(doc, 't42_rand_heatmap',
       'Figure 11. Town042 — Random dropout IQR centreline error. n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't42_rand_bands',
       'Figure 12. Town042 — Random dropout IQR band plots.',
       width=Inches(5.5))
figure(doc, 't42_rand_fail',
       'Figure 13. Town042 — Random dropout failure rate.',
       width=Inches(6.0))
figure(doc, 't44_rand_heatmap',
       'Figure 14. Town044 — Random dropout IQR centreline error. PCHIP notably worse than Akima at 4.0 m+.',
       width=Inches(6.0))
figure(doc, 't44_rand_bands',
       'Figure 15. Town044 — Random dropout IQR band plots.',
       width=Inches(5.5))
figure(doc, 't44_rand_fail',
       'Figure 16. Town044 — Random dropout failure rate. PCHIP (46%) vs Akima (12%) at 4.0 m, 10% dropout.',
       width=Inches(6.0))

heading(doc, '4.4 Clustered Dropout', level=2)
body(doc,
    'Clustered dropout removes a contiguous block of n consecutive CERPMs from a '
    'randomly chosen side and start position. This models localised failures such as '
    'a section of road resurfacing or physical impact damage. No separate images were '
    'generated for this scenario; findings are derived from the simulation output.')
body(doc,
    'Severity scales with both cluster size and CERPM spacing: a cluster of 10 at '
    '0.5 m represents a 5 m gap; the same cluster at 4.0 m represents a 40 m gap. '
    'Linear is most affected — failure rates reach 100% at cluster sizes ≥ 5 and '
    'spacings ≥ 2.0 m on curved roads. Smooth methods handle small clusters (2–5) '
    'well at ≤ 2.0 m spacing. PCHIP again degrades on Town044 when the cluster falls '
    'near a corner apex; Akima remains the most robust across all geometries.')

heading(doc, '4.5 Gap-Length Dropout', level=2)
body(doc,
    'Gap-length dropout exhaustively tests every possible placement of a physical gap '
    '(2–20 m) on both boundaries. Figures 17–28 show results for all four geometries.')
body(doc,
    'Town041 produces the most striking result: for all smooth methods at all spacings '
    'up to 6.0 m and all gap lengths up to 15 m, the failure rate is exactly 0%. Only '
    'linear fails (77–83% at 12.0 m spacing). Town07 (sinuous) is most sensitive — '
    'linear fails at 100% for any gap at spacings ≥ 2.0 m, and smooth methods degrade '
    'progressively at 4.0 m+. Akima and cubic spline consistently show the lowest '
    'failure rates and tightest IQR bands across all four geometries.')
body(doc,
    'Town044 reinforces the PCHIP vulnerability: where gaps fall near a 90° corner, '
    'PCHIP reaches 100% failure at moderate spacings while Akima remains below 10%, '
    'confirming PCHIP must not be used as a general deployment default.')

figure(doc, 't07_gap_heatmap',
       'Figure 17. Town07 — Gap-length dropout IQR centreline error. Exhaustive enumeration.',
       width=Inches(4.8))
figure(doc, 't07_gap_bands',
       'Figure 18. Town07 — Gap-length dropout IQR band plots. Linear (red) diverges from 2.0 m.',
       width=Inches(5.5))
figure(doc, 't07_gap_fail',
       'Figure 19. Town07 — Gap-length dropout failure rate.',
       width=Inches(4.4))
figure(doc, 't41_gap_heatmap',
       'Figure 20. Town041 — Gap-length dropout IQR error. All smooth methods near-zero throughout.',
       width=Inches(4.8))
figure(doc, 't41_gap_bands',
       'Figure 21. Town041 — Gap-length dropout IQR bands. Smooth methods show essentially flat lines.',
       width=Inches(5.5))
figure(doc, 't41_gap_fail',
       'Figure 22. Town041 — Gap-length dropout failure rate. Only linear fails (77–83% at 12.0 m).',
       width=Inches(4.4))
figure(doc, 't42_gap_heatmap',
       'Figure 23. Town042 — Gap-length dropout IQR error.',
       width=Inches(4.8))
figure(doc, 't42_gap_bands',
       'Figure 24. Town042 — Gap-length dropout IQR bands.',
       width=Inches(5.5))
figure(doc, 't42_gap_fail',
       'Figure 25. Town042 — Gap-length dropout failure rate.',
       width=Inches(4.4))
figure(doc, 't44_gap_heatmap',
       'Figure 26. Town044 — Gap-length dropout IQR error. PCHIP orange/red near corner gaps.',
       width=Inches(4.8))
figure(doc, 't44_gap_bands',
       'Figure 27. Town044 — Gap-length dropout IQR bands. Akima maintains tightest band.',
       width=Inches(5.5))
figure(doc, 't44_gap_fail',
       'Figure 28. Town044 — Gap-length dropout failure rate. Akima consistently lowest.',
       width=Inches(4.4))

heading(doc, '4.6 Algorithm Summary', level=2)
s_tbl = doc.add_table(rows=1, cols=5)
s_tbl.style = 'Table Grid'
tbl_header(s_tbl, ['Method', 'Random', 'Clustered', 'Gap-Length', 'Sharp Corners'])
for r in [
    ('Akima',        'Excellent', 'Excellent', 'Excellent', 'Best — recommended default'),
    ('PCHIP',        'Excellent', 'Very Good', 'Very Good', 'Poor at corner gaps'),
    ('Cubic Spline', 'Very Good', 'Good',      'Good',      'Good'),
    ('Quartic',      'Good',      'Good',      'Good',      'Good'),
    ('Quintic',      'Good',      'Moderate',  'Moderate',  'Good'),
    ('Quadratic',    'Moderate',  'Moderate',  'Moderate',  'Moderate'),
    ('Linear',       'Poor',      'Fail',      'Fail',      'Fail'),
]:
    tbl_row(s_tbl, r)
doc.add_paragraph()
caption(doc, 'Table 1. Algorithm performance summary across all four geometries and three dropout scenarios.')

body(doc,
    'The cross-geometry finding that separates Akima from PCHIP is consistent across '
    'all three dropout scenarios: on smooth and gradual roads the two methods are '
    'broadly comparable, but on Town044 (sharp corners) Akima is clearly superior '
    'under both random and gap-length dropout. Akima is the recommended default. '
    'PCHIP is appropriate only where road geometry is confirmed smooth.')

# ══════════════════════════════════════════════
# 5. CONCLUSIONS
# ══════════════════════════════════════════════
heading(doc, '5. Conclusions and Recommendations', level=1)
body(doc,
    'At CERPM spacings of 0.5–1.0 m all seven algorithms perform equivalently with '
    'sub-centimetre median error under all three dropout scenarios, making algorithm '
    'choice irrelevant when markers are dense. Beyond 2.0 m, algorithm selection '
    'and spacing become critical.')
body(doc,
    'Akima interpolation is recommended as the default algorithm for CERPM-based LKA '
    'systems, replacing the implicit cubic spline used in prior research. Its local '
    'slope construction limits gap-induced error propagation and handles sharp-corner '
    'geometries that impair PCHIP. PCHIP remains a strong choice on confirmed smooth '
    'roads but must not be used as a general default.')
body(doc,
    'Road geometry significantly modulates required CERPM density. Deployment standards '
    'should be geometry-aware: 1.0 m for sinuous or sharp-corner roads, 2.0 m for '
    'gradual curves, and 4.0 m only on near-straight or very smooth sections with Akima. '
    'Spacings of 6.0 m and above are unsuitable on complex geometries under any '
    'realistic failure model.')
body(doc,
    'Future work should quantify the effect of GPS positioning noise (0.1–1.0 m RMS '
    'for commercial GNSS) and sensor fusion with camera-based LKA for combined robustness.')

# ══════════════════════════════════════════════
# 6. REFERENCES
# ══════════════════════════════════════════════
doc.add_page_break()
heading(doc, '6. References', level=1)
for ref in [
    '[1]  S. Sharma et al., "Vehicle Lateral Offset Estimation Using Infrastructure '
     'Information for Reduced Compute Load," SAE Technical Paper, Apr. 2023, '
     'doi: 10.4271/2023-01-0800.',
    '[2]  P. Kadav et al., "Automated Lane Centering: An Off-the-Shelf Computer Vision '
     'Product vs. Infrastructure-Based Chip-Enabled Raised Pavement Markers," Sensors, '
     'vol. 24, no. 7, pp. 2327–2327, Apr. 2024, doi: 10.3390/s24072327.',
    '[3]  Dept. of Infrastructure, Transport, Cities and Regional Development, '
     '"Fact sheet: Evidence supporting the priority focus areas," '
     'National Road Safety Strategy, 2021.',
    '[4]  NHTSA, "Estimating Effectiveness of Lane Keeping Assist Systems in Fatal '
     'Road Departure Crashes," 2024. '
     'https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813663',
    '[5]  European Commission, "Mandatory drivers assistance systems expected to help '
     'save over 25,000 lives by 2038," Jul. 2024.',
    '[6]  Y. Wang, A. Alhuraish, S. Yuan, and H. Zhou, "OpenLKA: Open source multimodal '
     'OpenLKA dataset," GitHub, 2025. https://github.com/OpenLKA/OpenLKA',
    '[7]  I. Fakhari and S. Anwar, "A Multiple Model Estimation Approach to Robust Lane '
     'Detection via Computer Vision Based Models," IEEE ISIE, pp. 576–581, Jun. 2022, '
     'doi: 10.1109/isie51582.2022.9831692.',
    '[8]  I. Fakhari and S. Anwar, "Computer vision model based robust lane detection '
     'using multiple model adaptive estimation methodology," Frontiers in Mechanical '
     'Engineering, vol. 11, Feb. 2025, doi: 10.3389/fmech.2025.1436338.',
    '[9]  G. Perozzi et al., "Lateral Shared Sliding Mode Control for Lane Keeping '
     'Assist System in Steer-by-Wire Vehicles," IEEE Trans. Intelligent Vehicles, '
     'vol. 8, no. 4, pp. 3073–3082, Apr. 2023, doi: 10.1109/tiv.2021.3097352.',
    '[10] S. Wei, P. E. Pfeffer, and J. Edelmann, "State of the Art: Ongoing Research '
     'in Assessment Methods for Lane Keeping Assistance Systems," IEEE Trans. Intelligent '
     'Vehicles, vol. 9, no. 9, pp. 5853–5875, Sep. 2024, '
     'doi: 10.1109/tiv.2023.3269156.',
]:
    p = doc.add_paragraph(ref)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(0.5)
    for run in p.runs:
        run.font.name = 'Calibri'; run.font.size = Pt(10)

# ══════════════════════════════════════════════
# 7. APPENDICES
# ══════════════════════════════════════════════
doc.add_page_break()
heading(doc, '7. Appendices', level=1)

heading(doc, 'Appendix A — Project Gantt Chart', level=2)
g_cols = ['Section', 'Task',
          'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', 'Wk 9', 'Wk 10', 'Wk 11', 'Wk 12']
gtbl = doc.add_table(rows=1, cols=len(g_cols))
gtbl.style = 'Table Grid'
tbl_header(gtbl, g_cols)
G = '●'
for gr in [
    ('Research',    'Interpolation Algorithms',  G,  G,  '',  '',  '',  '',  '',  '',  ''),
    ('Research',    'Australian RPM Standards',   G,  G,  '',  '',  '',  '',  '',  '',  ''),
    ('Research',    'Road Geometry Sources',      '', G,   G,  '',  '',  '',  '',  '',  ''),
    ('Research',    'Importing Road Geometry',    '', '',  G,  G,  '',  '',  '',  '',  ''),
    ('Planning',    'Class Diagram',              '', '',  G,  '',  '',  '',  '',  '',  ''),
    ('Development', 'Coding',                     '', '',  G,  G,  G,  '',  '',  '',  ''),
    ('Development', 'Testing and Debugging',      '', '',  '',  '', G,   G,  '',  '',  ''),
    ('Simulation',  'Data Collection',            '', '',  '',  '', '',  G,  '',  '',  ''),
    ('Results',     'Algorithm Comparison',       '', '',  '',  '', '',  '',  G,  G,  ''),
    ('Results',     'CERPM Dropout Analysis',     '', '',  '',  '', '',  '',  G,  G,  ''),
    ('Results',     'Combine Findings',           '', '',  '',  '', '',  '',  '',  G,  G),
]:
    row = gtbl.add_row()
    for i, val in enumerate(gr):
        row.cells[i].text = str(val)
        for run in row.cells[i].paragraphs[0].runs:
            run.font.name = 'Calibri'; run.font.size = Pt(8)
doc.add_paragraph()

heading(doc, 'Appendix B — Simulation Parameters', level=2)
ptbl = doc.add_table(rows=1, cols=2)
ptbl.style = 'Table Grid'
tbl_header(ptbl, ['Parameter', 'Values'])
for p_row in [
    ('CERPM intervals',            '0.5, 1.0, 2.0, 4.0, 6.0, 12.0 m'),
    ('Random dropout rates',       '10%, 15%, 20%, 25%'),
    ('Cluster sizes',              '2, 5, 10, 15, 20 consecutive markers'),
    ('Gap lengths',                '2, 5, 10, 15, 20 m'),
    ('Monte Carlo runs',           '2,000 per condition (all scenarios)'),
    ('Gap-length trial enumeration','Exhaustive — all valid positions, both sides'),
    ('Cluster placement',          'Random start position and side per trial'),
    ('Failure threshold',          'Max centreline error > 0.2 m'),
    ('Centreline sample interval', '0.5 m'),
    ('Road geometries',            'Town07, Town041, Town042, Town044'),
    ('Interpolation methods',      'Linear, Quadratic, Cubic Spline, Quartic, Quintic, PCHIP, Akima'),
]:
    tbl_row(ptbl, p_row)

out = 'Final_Report.docx'
doc.save(out)
print(f'Saved: {out}')
