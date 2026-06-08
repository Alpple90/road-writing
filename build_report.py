"""
Generates Final_Report.docx — full research thesis for the CERPM/LKA project.
Run from the repo root: python3 build_report.py
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

IMG = {
    't07_road':        'Results/Town07G/Figure_1.png',
    't07_rand_heatmap':'Results/Town07G/random_iqr_heatmap - Copy.png',
    't07_rand_bands':  'Results/Town07G/random_iqr_bands.png',
    't07_rand_fail':   'Results/Town07G/random_failure_rate.png',
    't07_gap_heatmap': 'Results/Town07G/gaplength_iqr_heatmap.png',
    't07_gap_bands':   'Results/Town07G/gaplength_iqr_bands.png',
    't07_gap_fail':    'Results/Town07G/gaplength_failure_rate.png',
    't42_road':        'Results/Town042G/Figure_1.png',
    't42_rand_heatmap':'Results/Town042G/random_iqr_heatmap.png',
    't42_rand_bands':  'Results/Town042G/random_iqr_bands.png',
    't42_rand_fail':   'Results/Town042G/random_failure_rate.png',
    't42_gap_heatmap': 'Results/Town042G/gaplength_iqr_heatmap.png',
    't42_gap_bands':   'Results/Town042G/gaplength_iqr_bands.png',
    't42_gap_fail':    'Results/Town042G/gaplength_failure_rate.png',
    't44_road':        'Results/Town044G/Figure_1.png',
    't44_rand_heatmap':'Results/Town044G/random_iqr_heatmap.png',
    't44_rand_bands':  'Results/Town044G/random_iqr_bands.png',
    't44_rand_fail':   'Results/Town044G/random_failure_rate.png',
    't44_gap_heatmap': 'Results/Town044G/gaplength_iqr_heatmap.png',
    't44_gap_bands':   'Results/Town044G/gaplength_iqr_bands.png',
    't44_gap_fail':    'Results/Town044G/gaplength_failure_rate.png',
}


def shade_cell(cell, hex_colour):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
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
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    if not p.runs:
        p.add_run(text)
        p.clear()
        p.add_run(text)
    for run in p.runs:
        run.font.name  = 'Calibri'
        run.font.size  = Pt(9)
        run.italic     = True
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


def table_row(tbl, cells, bold=False, bg=None):
    row = tbl.add_row()
    for i, text in enumerate(cells):
        row.cells[i].text = text
        for run in row.cells[i].paragraphs[0].runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            run.bold = bold
        if bg:
            shade_cell(row.cells[i], bg)
    return row


# ─────────────────────────────────────────────
doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ══════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════
for _ in range(5):
    doc.add_paragraph()

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run('Interpolation Algorithm Evaluation for\nCERPM-Based Lane Keep Assist Systems')
r.font.name = 'Calibri'; r.font.size = Pt(20); r.bold = True

doc.add_paragraph()
sp = doc.add_paragraph()
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sp.add_run('Final Research Thesis')
r2.font.name = 'Calibri'; r2.font.size = Pt(13); r2.italic = True

doc.add_paragraph()
for label, value in [('Unit:', 'Advanced Driver Assistance Systems Research Project'),
                      ('Author:', 'Alexander Bruce'), ('Date:', 'June 2026')]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rb = p.add_run(label + ' '); rb.bold = True; rb.font.name = 'Calibri'; rb.font.size = Pt(12)
    rv = p.add_run(value);       rv.font.name = 'Calibri';                 rv.font.size = Pt(12)

doc.add_paragraph()
cp = doc.add_paragraph()
cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
rch = cp.add_run('Student Contribution: ')
rch.bold = True; rch.font.name = 'Calibri'; rch.font.size = Pt(11)
rct = cp.add_run(
    'Alexander Bruce was solely responsible for the LKA subsystem within the group ADAS '
    'project, encompassing problem definition, literature review, full Python simulation '
    'development (road geometry parsing, CERPM resampling, Monte Carlo engine, '
    'visualisation), experiment execution across three road geometries, and all results '
    'analysis.')
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
    'Monte Carlo simulation framework across three real-world road geometries and three '
    'CERPM dropout scenarios. At spacings of 0.5–1.0 m all methods perform equivalently '
    'with sub-centimetre error. Beyond 2.0 m, smooth methods outperform linear and '
    'quadratic substantially. Under gap-length dropout, linear fails catastrophically on '
    'all curved roads; Akima is the most robust method across all geometry types, '
    'including sharp-corner roads where PCHIP degrades due to its monotonicity constraint. '
    'Recommendations for CERPM spacing standards and algorithm selection are provided.')

doc.add_page_break()

# ══════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════
heading(doc, 'Table of Contents', level=1)
toc = [
    ('1.', 'Introduction'), ('2.', 'Literature Review'), ('3.', 'Methodology'),
    ('4.', 'Results and Analysis'), ('5.', 'Conclusions and Recommendations'),
    ('6.', 'References'), ('7.', 'Appendices'),
]
for num, title in toc:
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
    'Lane departure — encompassing run-off-road and head-on collisions — accounts for 62% '
    'of Australian road fatalities nationally (73% in regional areas) [3]. In the United '
    'States, NHTSA estimates that LKA-equipped vehicles are 24% less likely to be involved '
    'in a fatal road departure crash [4]. From July 2024, the European Commission mandated '
    'LKA on all new vehicles sold in the EU, projecting over 25,000 lives saved by 2038 [5]. '
    'LKA also forms the perceptual foundation for higher-order ADAS functions.')
body(doc,
    'Current production LKA systems use forward-facing cameras with computer vision to '
    'detect lane markings. Field evidence confirms substantial performance degradation under '
    'worn markings, adverse weather, and lane transitions [6]. Lane Departure Warning (LDW) '
    'systems require a driver response — unreliable under fatigue or impairment. LKA '
    'directly actuates steering, eliminating this dependency.')
body(doc,
    'Chip Enabled Raised Pavement Markers (CERPMs) offer an alternative V2I approach: '
    'road-embedded devices transmit GPS lane-boundary coordinates directly to the vehicle '
    '(range up to 350 m), enabling centreline computation through interpolation entirely '
    'independent of visual conditions. Kadav et al. [2] demonstrated that CERPM-based '
    'lane centering outperformed the Mobileye 630 commercial system across all tested '
    'conditions. However, neither this study nor its predecessor [1] investigated which '
    'interpolation algorithm is most accurate, or how the system behaves when individual '
    'CERPMs fail — an inevitable scenario given road-embedded hardware.')
body(doc,
    'This project addresses these gaps with three aims: (1) evaluate seven interpolation '
    'algorithms for centreline accuracy across multiple road geometries; (2) characterise '
    'how random, gap-length, and clustered CERPM dropout degrade accuracy at varying '
    'marker spacings; and (3) provide algorithm and spacing recommendations for deployment.')

# ══════════════════════════════════════════════
# 2. LITERATURE REVIEW
# ══════════════════════════════════════════════
heading(doc, '2. Literature Review', level=1)
body(doc,
    'The OpenLKA dataset [6] — 400 hours of real-world LKA data from 62 production vehicles '
    '— establishes that modern deep-learning LKA systems still fail at high rates under '
    'degraded markings and lane transitions, confirming the ceiling of camera-based '
    'approaches. Fakhari and Anwar [7][8] improved robustness with a Multiple Model '
    'Adaptive Estimation (MMAE) Kalman filter fusing front and rear cameras, but their '
    'system remains dependent on some minimum marking quality.')
body(doc,
    'Sharma et al. [1] and Kadav et al. [2] validated the CERPM V2I concept, showing '
    'CERPMs outperform the Mobileye 630 on sharp curves, degraded markings, and variable '
    'lighting, with ten times the detection range. Neither study addressed interpolation '
    'algorithm choice or the effect of marker failures — the gap this project fills.')
body(doc,
    'Arc-length parameterisation is standard for spatial curve reconstruction, expressing '
    'the interpolation variable as normalised path distance. Linear interpolation (C⁰) '
    'provides a piecewise-straight baseline. Cubic spline (C², natural) is the most common '
    'smooth engineering interpolator and the implicit standard in prior CERPM work. Higher '
    'degree B-splines (quadratic, quartic, quintic) provide increasing smoothness but '
    'greater endpoint sensitivity. PCHIP enforces C¹ monotone cubic construction — no '
    'overshoot, well-suited to sparse data, but constrained at sharp curvature reversals. '
    'Akima uses locally weighted C¹ cubic slopes so that a single gap does not propagate '
    'oscillation to neighbouring segments, providing the best local robustness.')
body(doc,
    'On the control side, Perozzi et al. [9] proposed a quasi-continuous high-order sliding '
    'mode shared controller for steer-by-wire LKA validated in the SHERPA simulator, '
    'providing smooth driver–automation authority transitions — the control layer upon '
    'which this perception work would operate. Wei et al. [10] review LKA assessment '
    'frameworks and identify standardisation gaps that future CERPM systems should address.')

# ══════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════
heading(doc, '3. Methodology', level=1)
body(doc,
    'A simulation-based approach was adopted for controlled, repeatable, exhaustive testing '
    'across parameter combinations impractical to replicate physically. All code was '
    'implemented in Python using NumPy, SciPy, Shapely, and Matplotlib.')

heading(doc, 'Road Geometries', level=2)
body(doc,
    'Three real-world road geometries were parsed from Lanelet2 OSM files, which encode '
    'each lane as a left and right boundary way with local Cartesian coordinates (metres). '
    'Town07 is a sinuous S-curve (~280 m, multiple curvature reversals — most challenging). '
    'Town042 is a long gradual curve (~560 m — easiest, gentle bends). Town044 has two '
    'sharp 90° corners (~520 m — tests sharp curvature reversal). Consecutive lanelets '
    'were chain-linked into continuous boundary polylines.')

heading(doc, 'CERPM Simulation and Centreline', level=2)
body(doc,
    'CERPMs were simulated by resampling boundary polylines at uniform intervals of '
    '0.5, 1.0, 2.0, 4.0, 6.0, and 12.0 m using Shapely\'s LineString.interpolate. '
    'The ground-truth centreline was computed at 0.5 m intervals from the full-resolution '
    'boundaries using a perpendicular-nearest-point algorithm: for each boundary sample '
    'point the nearest point on the opposite boundary is found, and their midpoint taken.')

heading(doc, 'Interpolation Methods', level=2)
body(doc,
    'All seven methods use arc-length parameterisation (t ∈ [0,1] = normalised cumulative '
    'path length), interpolating x and y independently. Methods requiring minimum point '
    'counts fall back to linear if insufficient markers survive dropout.')

m_tbl = doc.add_table(rows=1, cols=4)
m_tbl.style = 'Table Grid'
for i, h in enumerate(['Method', 'Implementation', 'Continuity', 'Key Property']):
    m_tbl.rows[0].cells[i].text = h
    for run in m_tbl.rows[0].cells[i].paragraphs[0].runs:
        run.bold = True; run.font.name = 'Calibri'; run.font.size = Pt(10)
    shade_cell(m_tbl.rows[0].cells[i], 'BDD7EE')
for row in [
    ('Linear',       'numpy.interp',           'C⁰', 'No overshoot; piecewise straight'),
    ('Quadratic',    'make_interp_spline(k=2)', 'C¹', 'Low-order B-spline'),
    ('Cubic Spline', 'CubicSpline (natural)',   'C²', 'Standard smooth; prior CERPM default'),
    ('Quartic',      'make_interp_spline(k=4)', 'C³', 'Higher smoothness'),
    ('Quintic',      'make_interp_spline(k=5)', 'C⁴', 'Highest smoothness; Runge-prone'),
    ('PCHIP',        'PchipInterpolator',       'C¹', 'Monotone; no overshoot; sparse-robust'),
    ('Akima',        'Akima1DInterpolator',     'C¹', 'Local slopes; gap-resilient'),
]:
    table_row(m_tbl, row)
doc.add_paragraph()

heading(doc, 'Dropout Scenarios and Error Metrics', level=2)
body(doc,
    'Three dropout models were tested. Random dropout: each CERPM independently fails '
    'with probability p (10%, 15%, 20%, 25%); 2,000 Monte Carlo trials per condition. '
    'Gap-length dropout: a contiguous block equivalent to 2, 5, 10, 15, or 20 m is '
    'removed from one side; all valid positions exhaustively tested. Clustered dropout: '
    'same as gap-length but parameterised by marker count (2, 5, 10, 15, 20).')
body(doc,
    'Per trial, the reconstructed centreline error is the Euclidean distance from each '
    'estimated centreline point to the nearest point on the true centreline LineString. '
    'Mean and max errors are recorded. A trial is a failure if max error exceeds 0.2 m — '
    'derived from the 3.5 m standard lane width and a ±0.3 m LKA intervention threshold. '
    'Distributions are summarised by P25, P75, and IQR = P75 − P25.')

# ══════════════════════════════════════════════
# 4. RESULTS AND ANALYSIS
# ══════════════════════════════════════════════
heading(doc, '4. Results and Analysis', level=1)

heading(doc, '4.1 Road Geometries', level=2)
body(doc, 'Figures 1–3 show the resampled boundary polylines for each road geometry.')

figure(doc, 't07_road',
       'Figure 1. Town07 — sinuous road (~280 m). Multiple curvature reversals; hardest geometry.',
       width=Inches(4.8))
figure(doc, 't42_road',
       'Figure 2. Town042 — gradual curve (~560 m). Smooth, consistent curvature; easiest geometry.',
       width=Inches(3.8))
figure(doc, 't44_road',
       'Figure 3. Town044 — sharp corners (~520 m). Two 90° turns; tests abrupt curvature changes.',
       width=Inches(4.8))

heading(doc, '4.2 Effect of CERPM Spacing', level=2)
body(doc,
    'At 0.5–1.0 m spacing all seven methods are effectively equivalent, producing median '
    'centreline errors below 0.01 m with near-zero IQR across all geometries and dropout '
    'scenarios. Algorithm choice is irrelevant at dense deployments. Beyond 2.0 m, methods '
    'diverge: linear IQR rises measurably at 2.0 m, reaches unacceptable levels at 4.0 m, '
    'and fails at 100% under any dropout at 6.0 m+ on curved roads. Smooth methods '
    '(cubic spline, PCHIP, Akima) remain below 0.05 m median error at 2.0 m and '
    '0.03–0.07 m at 4.0 m. At 12.0 m all methods degrade substantially regardless of '
    'algorithm, confirming this spacing is unsuitable for any realistic dropout scenario.')

heading(doc, '4.3 Random Dropout Results', level=2)
body(doc,
    'Figures 4–12 show IQR heatmaps, IQR band plots, and failure rate heatmaps for all '
    'three geometries under random dropout. At 2.0 m spacing, linear fails at '
    '24%–43% (10% dropout) depending on geometry, rising to 56%–97% at 25% dropout. '
    'All smooth methods remain below 5% failure at 2.0 m across all geometries and rates.')
body(doc,
    'At 4.0 m, linear reaches 100% failure on all geometries. On Town07 (sinuous), '
    'cubic spline shows 32%–91% failure, quartic 29%–75%, quintic 29%–74%, PCHIP '
    '65%–85%, Akima 56%–96% — elevated overall due to the geometry complexity. '
    'On Town042 (gradual), the same spacing yields much lower failure rates: cubic '
    'spline 8%–38%, Akima 5%–30% — the best result. On Town044 (sharp corners), '
    'a significant divergence emerges: Akima achieves only 12% failure at 10% dropout '
    'while PCHIP reaches 46% — worse than cubic spline (18%). PCHIP\'s monotonicity '
    'constraint, beneficial on smooth roads, limits its ability to represent abrupt '
    '90° curvature reversals when markers are sparse.')

figure(doc, 't07_rand_heatmap',
       'Figure 4. Town07 — Random dropout IQR centreline error (P25–P75, m). n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't07_rand_fail',
       'Figure 5. Town07 — Random dropout failure rate (max error > 0.2 m, %). n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't42_rand_heatmap',
       'Figure 6. Town042 — Random dropout IQR centreline error (P25–P75, m). n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't42_rand_fail',
       'Figure 7. Town042 — Random dropout failure rate. n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't44_rand_heatmap',
       'Figure 8. Town044 — Random dropout IQR centreline error. n=2000 runs.',
       width=Inches(6.0))
figure(doc, 't44_rand_fail',
       'Figure 9. Town044 — Random dropout failure rate. PCHIP notably worse than Akima at 4.0 m.',
       width=Inches(6.0))

heading(doc, '4.4 Gap-Length Dropout Results', level=2)
body(doc,
    'Gap-length dropout reveals the most practically important findings. Linear is '
    'uniquely catastrophic: on Town07, any gap ≥ 2 m at spacing ≥ 2.0 m causes 100% '
    'failure; even at 1.0 m spacing a 10 m gap produces ~14% failure. The cause is '
    'geometric — linear draws a straight chord across the gap, which diverges from any '
    'curved road boundary regardless of curvature magnitude.')
body(doc,
    'Cubic spline, quartic, and quintic handle moderate gaps well: at 1.0 m spacing '
    'with gaps up to 10 m, failure rates are 0%–5% on all geometries. Town042 (gradual '
    'curve) shows near-zero failure for all smooth methods at up to 4.0 m spacing and '
    '20 m gaps, providing a best-case deployment benchmark. On Town044 (sharp corners), '
    'PCHIP fails at 100% for gap = 10 m at 4.0 m spacing while Akima remains at ~4%–8%. '
    'Akima\'s local slope construction limits gap-induced error to the immediate vicinity '
    'of the gap, making it the consistently superior choice across all geometry types.')

figure(doc, 't07_gap_heatmap',
       'Figure 10. Town07 — Gap-length dropout IQR centreline error. Exhaustive enumeration.',
       width=Inches(4.8))
figure(doc, 't07_gap_fail',
       'Figure 11. Town07 — Gap-length dropout failure rate. Linear catastrophic at all curved spacings.',
       width=Inches(4.4))
figure(doc, 't42_gap_heatmap',
       'Figure 12. Town042 — Gap-length dropout IQR error. Smooth methods near-zero even at 20 m gaps.',
       width=Inches(4.8))
figure(doc, 't42_gap_fail',
       'Figure 13. Town042 — Gap-length dropout failure rate.',
       width=Inches(4.4))
figure(doc, 't44_gap_heatmap',
       'Figure 14. Town044 — Gap-length dropout IQR error. PCHIP orange/red at corner gaps; Akima stable.',
       width=Inches(4.8))
figure(doc, 't44_gap_fail',
       'Figure 15. Town044 — Gap-length dropout failure rate. Akima consistently lowest.',
       width=Inches(4.4))

heading(doc, '4.5 IQR Band Plots', level=2)
body(doc,
    'Figures 16–21 show IQR band plots for all geometries under both dropout scenarios. '
    'The shaded band width (IQR) quantifies estimation consistency. At ≤ 2.0 m spacing, '
    'all smooth methods show near-invisible bands. At 4.0–6.0 m spacing, Akima '
    'consistently maintains the narrowest band on Town07 and Town044, confirming it '
    'produces the most consistent results at the sparse spacings most vulnerable to '
    'dropout. Linear\'s bands are wide even at 2.0 m, reinforcing its unsuitability.')

figure(doc, 't07_rand_bands',
       'Figure 16. Town07 — Random dropout IQR bands. Linear (red) diverges sharply from 2.0 m.',
       width=Inches(5.5))
figure(doc, 't07_gap_bands',
       'Figure 17. Town07 — Gap-length dropout IQR bands. Akima (purple) narrowest at sparse spacings.',
       width=Inches(5.5))
figure(doc, 't42_rand_bands',
       'Figure 18. Town042 — Random dropout IQR bands.',
       width=Inches(5.5))
figure(doc, 't42_gap_bands',
       'Figure 19. Town042 — Gap-length dropout IQR bands. All smooth methods very stable.',
       width=Inches(5.5))
figure(doc, 't44_rand_bands',
       'Figure 20. Town044 — Random dropout IQR bands. PCHIP (green) widens at 4.0 m+.',
       width=Inches(5.5))
figure(doc, 't44_gap_bands',
       'Figure 21. Town044 — Gap-length dropout IQR bands. Akima maintains tightest band throughout.',
       width=Inches(5.5))

heading(doc, '4.6 Algorithm Summary and Changes from Plan', level=2)

s_tbl = doc.add_table(rows=1, cols=4)
s_tbl.style = 'Table Grid'
for i, h in enumerate(['Method', 'Random Dropout', 'Gap-Length Dropout', 'Sharp Corners']):
    s_tbl.rows[0].cells[i].text = h
    for run in s_tbl.rows[0].cells[i].paragraphs[0].runs:
        run.bold = True; run.font.name = 'Calibri'; run.font.size = Pt(10)
    shade_cell(s_tbl.rows[0].cells[i], 'BDD7EE')
for r in [
    ('Akima',        'Excellent', 'Excellent',  'Best — recommended default'),
    ('PCHIP',        'Excellent', 'Very Good',  'Poor — monotonicity fails corners'),
    ('Cubic Spline', 'Very Good', 'Good',       'Good'),
    ('Quartic',      'Good',      'Good',       'Good'),
    ('Quintic',      'Good',      'Moderate',   'Good'),
    ('Quadratic',    'Moderate',  'Moderate',   'Moderate'),
    ('Linear',       'Poor',      'Unacceptable','Unacceptable'),
]:
    table_row(s_tbl, r)
doc.add_paragraph()
caption(doc, 'Table 1. Algorithm ranking across all geometries and dropout scenarios.')

body(doc,
    'The CERPM interval set was revised from the planned (0.5, 1.0, 2.0, 3.0, 5.0 m) '
    'to (0.5, 1.0, 2.0, 4.0, 6.0, 12.0 m) to better characterise the failure transition '
    'zone and include a low-cost rural spacing. Monte Carlo runs were increased from 500 '
    'to 2,000 per condition to reduce failure-rate uncertainty from ±4.4 to ±2.2 pp at '
    '95% confidence. The finding that PCHIP is inferior to Akima on sharp-corner roads '
    'was not anticipated in the initial plan and represents the most significant revision '
    'to the original algorithm recommendation.')

# ══════════════════════════════════════════════
# 5. CONCLUSIONS
# ══════════════════════════════════════════════
heading(doc, '5. Conclusions and Recommendations', level=1)
body(doc,
    'At CERPM spacings of 0.5–1.0 m all seven algorithms perform equivalently and '
    'excellently under all tested dropout scenarios — making algorithm choice irrelevant '
    'when CERPMs are densely deployed. Beyond 2.0 m, algorithm selection becomes critical.')
body(doc,
    'Akima interpolation is the recommended default for CERPM-based LKA systems, replacing '
    'cubic spline. Its locally weighted slope construction limits gap-induced error '
    'propagation and handles sharp-corner geometries that disable PCHIP. PCHIP remains a '
    'strong choice for known smooth or gradual road geometries but should not be used as '
    'a general-purpose algorithm. Linear interpolation is categorically unsuitable for '
    'deployment on curved roads at any realistic spacing.')
body(doc,
    'A maximum CERPM spacing of 1.0 m is recommended for safety-critical applications; '
    '2.0 m is acceptable for lower-speed or cost-constrained routes with a maintenance '
    'protocol to limit physical gap lengths. Spacings beyond 4.0 m produce unacceptably '
    'high failure rates under any realistic dropout model on non-trivially curved roads.')
body(doc,
    'Future work should characterise the combined effect of CERPM spacing, dropout, and '
    'GPS positioning noise (0.1–1.0 m RMS for commercial GNSS), and evaluate sensor '
    'fusion with camera-based LKA to quantify the accuracy improvement from redundancy.')

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
    '[3]  Dept. of Infrastructure, Transport, Cities and Regional Development, "Fact sheet: '
     'Evidence supporting the priority focus areas," National Road Safety Strategy, 2021.',
    '[4]  NHTSA, "Estimating Effectiveness of Lane Keeping Assist Systems in Fatal Road '
     'Departure Crashes," 2024. https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813663',
    '[5]  European Commission, "Mandatory drivers assistance systems expected to help save '
     'over 25,000 lives by 2038," Jul. 2024.',
    '[6]  Y. Wang, A. Alhuraish, S. Yuan, and H. Zhou, "OpenLKA: Open source multimodal '
     'OpenLKA dataset," GitHub, 2025. https://github.com/OpenLKA/OpenLKA',
    '[7]  I. Fakhari and S. Anwar, "A Multiple Model Estimation Approach to Robust Lane '
     'Detection via Computer Vision Based Models," IEEE ISIE, pp. 576–581, Jun. 2022, '
     'doi: 10.1109/isie51582.2022.9831692.',
    '[8]  I. Fakhari and S. Anwar, "Computer vision model based robust lane detection '
     'using multiple model adaptive estimation methodology," Frontiers in Mechanical '
     'Engineering, vol. 11, Feb. 2025, doi: 10.3389/fmech.2025.1436338.',
    '[9]  G. Perozzi et al., "Lateral Shared Sliding Mode Control for Lane Keeping Assist '
     'System in Steer-by-Wire Vehicles," IEEE Trans. Intelligent Vehicles, vol. 8, no. 4, '
     'pp. 3073–3082, Apr. 2023, doi: 10.1109/tiv.2021.3097352.',
    '[10] S. Wei, P. E. Pfeffer, and J. Edelmann, "State of the Art: Ongoing Research in '
     'Assessment Methods for Lane Keeping Assistance Systems," IEEE Trans. Intelligent '
     'Vehicles, vol. 9, no. 9, pp. 5853–5875, Sep. 2024, doi: 10.1109/tiv.2023.3269156.',
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
g_cols = ['Section', 'Task', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', 'Wk 9', 'Wk 10', 'Wk 11', 'Wk 12']
gtbl = doc.add_table(rows=1, cols=len(g_cols))
gtbl.style = 'Table Grid'
for i, h in enumerate(g_cols):
    gtbl.rows[0].cells[i].text = h
    for run in gtbl.rows[0].cells[i].paragraphs[0].runs:
        run.bold = True; run.font.name = 'Calibri'; run.font.size = Pt(8)
    shade_cell(gtbl.rows[0].cells[i], 'BDD7EE')
G = '●'
for gr in [
    ('Research',     'Interpolation Algorithms',       G,  G,  '',  '',  '',  '',  '',  '',  ''),
    ('Research',     'Australian RPM Standards',        G,  G,  '',  '',  '',  '',  '',  '',  ''),
    ('Research',     'Road Geometry Sources',           '',  G,  G,  '',  '',  '',  '',  '',  ''),
    ('Research',     'Importing Road Geometry',         '',  '',  G,  G,  '',  '',  '',  '',  ''),
    ('Planning',     'Class Diagram',                   '',  '',  G,  '',  '',  '',  '',  '',  ''),
    ('Development',  'Coding',                          '',  '',  G,  G,  G,  '',  '',  '',  ''),
    ('Development',  'Testing and Debugging',           '',  '',  '',  '',  G,  G,  '',  '',  ''),
    ('Simulation',   'Data Collection',                 '',  '',  '',  '',  '',  G,  '',  '',  ''),
    ('Results',      'Algorithm Comparison',            '',  '',  '',  '',  '',  '',  G,  G,  ''),
    ('Results',      'CERPM Dropout Analysis',          '',  '',  '',  '',  '',  '',  G,  G,  ''),
    ('Results',      'Combine Findings',                '',  '',  '',  '',  '',  '',  '',  G,  G),
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
for i, h in enumerate(['Parameter', 'Values']):
    ptbl.rows[0].cells[i].text = h
    for run in ptbl.rows[0].cells[i].paragraphs[0].runs:
        run.bold = True; run.font.name = 'Calibri'; run.font.size = Pt(10)
    shade_cell(ptbl.rows[0].cells[i], 'BDD7EE')
for p_row in [
    ('CERPM intervals',          '0.5, 1.0, 2.0, 4.0, 6.0, 12.0 m'),
    ('Random dropout rates',     '10%, 15%, 20%, 25%'),
    ('Gap lengths',              '2, 5, 10, 15, 20 m'),
    ('Cluster sizes',            '2, 5, 10, 15, 20 markers'),
    ('Monte Carlo runs (random)','2,000 per condition'),
    ('Gap/cluster trials',       'Exhaustive enumeration — all valid positions, both sides'),
    ('Failure threshold',        'Max centreline error > 0.2 m'),
    ('Centreline sample interval','0.5 m'),
    ('Road geometries',          'Town07, Town042, Town044'),
]:
    table_row(ptbl, p_row)

# ── Save ──
out = 'Final_Report.docx'
doc.save(out)
print(f'Saved: {out}')
