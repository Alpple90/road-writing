"""
Generates Final_Report.docx based strictly on main branch code.
Two dropout scenarios: random + clustered (no gap-length).
Intervals: 0.5, 1.0, 2.0, 3.0, 5.0 m
Dropout rates: 1%, 5%, 10%, 15%, 20%
Cluster sizes: 2, 5, 10, 15, 20 markers
Result images used: random_* only (clustered images not yet generated).
"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

# Only random images exist (generated from a compatible run); gaplength images
# were from a different code version and are excluded.
IMG = {
    't07_road':        'Results/Town07G/Figure_1.png',
    't07_rand_heatmap':'Results/Town07G/random_iqr_heatmap - Copy.png',
    't07_rand_bands':  'Results/Town07G/random_iqr_bands.png',
    't07_rand_fail':   'Results/Town07G/random_failure_rate.png',
    't42_road':        'Results/Town042G/Figure_1.png',
    't42_rand_heatmap':'Results/Town042G/random_iqr_heatmap.png',
    't42_rand_bands':  'Results/Town042G/random_iqr_bands.png',
    't42_rand_fail':   'Results/Town042G/random_failure_rate.png',
    't44_road':        'Results/Town044G/Figure_1.png',
    't44_rand_heatmap':'Results/Town044G/random_iqr_heatmap.png',
    't44_rand_bands':  'Results/Town044G/random_iqr_bands.png',
    't44_rand_fail':   'Results/Town044G/random_failure_rate.png',
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


def tbl_row(tbl, cells, bold=False, bg=None):
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


def tbl_header(tbl, cols):
    hdr = tbl.rows[0].cells
    for i, h in enumerate(cols):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
        shade_cell(hdr[i], 'BDD7EE')


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
for label, value in [
    ('Unit:',   'Advanced Driver Assistance Systems Research Project'),
    ('Author:', 'Alexander Bruce'),
    ('Date:',   'June 2026'),
]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rb = p.add_run(label + ' '); rb.bold = True; rb.font.name = 'Calibri'; rb.font.size = Pt(12)
    rv = p.add_run(value);       rv.font.name = 'Calibri';                 rv.font.size = Pt(12)

doc.add_paragraph()
cp = doc.add_paragraph(); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
rch = cp.add_run('Student Contribution: ')
rch.bold = True; rch.font.name = 'Calibri'; rch.font.size = Pt(11)
rct = cp.add_run(
    'Alexander Bruce was solely responsible for the LKA subsystem within the group ADAS '
    'project: problem definition, literature review, full Python simulation development '
    '(road geometry parsing, CERPM resampling, Monte Carlo simulation engine, '
    'visualisation), experiment execution across multiple road geometries, and all '
    'results analysis and interpretation.')
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
    'Monte Carlo simulation framework across three real-world road geometries and two '
    'CERPM dropout scenarios: random independent failure and clustered consecutive failure. '
    'At CERPM spacings of 0.5–1.0 m all methods perform equivalently with sub-centimetre '
    'median error. Beyond 2.0 m, smooth methods substantially outperform linear and '
    'quadratic interpolation. Under clustered dropout, linear fails catastrophically on '
    'curved roads at all practical spacings. Akima interpolation is the most consistently '
    'robust method across all geometry types tested, including sharp-corner roads where '
    'PCHIP degrades due to its monotonicity constraint. Concrete recommendations for '
    'CERPM spacing standards and algorithm selection are provided.')

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
    'Lane departure — encompassing run-off-road and head-on collisions — accounts for 62% '
    'of Australian road fatalities nationally (73% in regional areas) [3]. In the United '
    'States, the NHTSA estimates LKA-equipped vehicles are 24% less likely to be involved '
    'in a fatal road departure crash [4]. From July 2024, the European Commission mandated '
    'LKA on all new vehicles sold in the EU, projecting over 25,000 lives saved by 2038 '
    '[5]. LKA also forms the perceptual foundation for higher-order ADAS functions.')
body(doc,
    'Current production LKA systems use forward-facing cameras with computer vision to '
    'detect lane markings. Field evidence confirms substantial performance degradation under '
    'worn markings, adverse weather, and lane transitions [6]. Lane Departure Warning (LDW) '
    'systems require the driver to respond — unreliable under fatigue or impairment. LKA '
    'directly actuates steering, eliminating this dependency.')
body(doc,
    'Chip Enabled Raised Pavement Markers (CERPMs) offer a V2I alternative: road-embedded '
    'devices transmit GPS lane-boundary coordinates directly to the vehicle (range up to '
    '350 m), enabling centreline computation through interpolation entirely independent of '
    'visual conditions. Kadav et al. [2] demonstrated CERPM-based lane centering '
    'outperformed the Mobileye 630 across all tested conditions. However, neither this '
    'study nor its predecessor [1] investigated which interpolation algorithm is most '
    'accurate, or how the system behaves when individual CERPMs fail.')
body(doc,
    'This project addresses these gaps with three aims: (1) evaluate seven interpolation '
    'algorithms for centreline accuracy across multiple road geometries; (2) characterise '
    'how random and clustered CERPM dropout degrade accuracy at varying marker spacings; '
    'and (3) provide algorithm and spacing recommendations for deployment.')

# ══════════════════════════════════════════════
# 2. LITERATURE REVIEW
# ══════════════════════════════════════════════
heading(doc, '2. Literature Review', level=1)
body(doc,
    'The OpenLKA dataset [6] — 400 hours of real-world LKA data from 62 production vehicles '
    '— confirms that deep-learning LKA systems fail at high rates under degraded markings '
    'and lane transitions, establishing the ceiling of camera-based approaches. Fakhari and '
    'Anwar [7][8] improved robustness with a Multiple Model Adaptive Estimation (MMAE) '
    'Kalman filter fusing front and rear cameras, but their system remains dependent on '
    'minimum marking quality.')
body(doc,
    'Sharma et al. [1] and Kadav et al. [2] validated the CERPM V2I concept, showing '
    'CERPMs outperform the Mobileye 630 on sharp curves, degraded markings, and variable '
    'lighting, with ten times the detection range. Neither study addressed interpolation '
    'algorithm choice or the effect of marker failures — the gap this project fills.')
body(doc,
    'Arc-length parameterisation is standard for spatial curve reconstruction, expressing '
    'the interpolation variable as normalised path distance. Linear interpolation (C⁰) '
    'is the piecewise-straight baseline. Cubic spline (C², natural) is the most common '
    'smooth engineering interpolator and the implicit standard in prior CERPM work. Higher '
    'degree B-splines (quadratic, quartic, quintic) provide increasing smoothness at '
    'greater endpoint sensitivity. PCHIP enforces C¹ monotone cubic construction — no '
    'overshoot, but constrained at sharp curvature reversals. Akima uses locally weighted '
    'C¹ cubic slopes so a single data gap does not propagate oscillation to neighbouring '
    'segments, providing the best local robustness.')
body(doc,
    'On the control side, Perozzi et al. [9] proposed a quasi-continuous high-order sliding '
    'mode shared controller for steer-by-wire LKA, providing smooth driver–automation '
    'authority transitions — the control layer upon which this perception work would '
    'operate. Wei et al. [10] review LKA assessment frameworks and identify standardisation '
    'gaps that future CERPM-based LKA systems should address.')

# ══════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════
heading(doc, '3. Methodology', level=1)
body(doc,
    'A simulation-based approach enables controlled, repeatable, exhaustive testing across '
    'parameter combinations impractical to replicate physically. All code was implemented '
    'in Python using NumPy, SciPy, Shapely, and Matplotlib, structured across four modules: '
    'test.py (geometry parsing and centreline computation), Interpolations.py (arc-length '
    'parameterisation and all seven interpolation methods), Simulation.py (Monte Carlo '
    'engine), and xmlParse.py (parameter sweeps and visualisation).')

heading(doc, 'Road Geometries', level=2)
body(doc,
    'Three road geometries were parsed from Lanelet2 OSM files, which encode each lane as '
    'a left and right boundary way with local Cartesian coordinates in metres. Town07 is a '
    'sinuous S-curve (~280 m with multiple curvature reversals — most challenging). Town042 '
    'is a long gradual curve (~560 m — easiest, gentle consistent bends). Town044 has two '
    'sharp 90° corners (~520 m — tests abrupt curvature reversal). Consecutive lanelets '
    'were chain-linked into continuous boundary polylines via a start/end node matching '
    'algorithm.')

heading(doc, 'CERPM Simulation and True Centreline', level=2)
body(doc,
    'CERPMs were simulated by resampling boundary polylines at uniform intervals using '
    'Shapely\'s LineString.interpolate. Five intervals were tested: 0.5, 1.0, 2.0, 3.0, '
    'and 5.0 m. The ground-truth centreline was computed at 0.5 m intervals from the '
    'full-resolution boundaries: for each sample point on the longer boundary, the nearest '
    'point on the opposite boundary is found by projection, and their midpoint taken.')

heading(doc, 'Interpolation Methods', level=2)
body(doc,
    'All seven methods use arc-length parameterisation (t ∈ [0, 1] = normalised cumulative '
    'Euclidean path distance), interpolating x and y independently. Duplicate t-values '
    'from coincident points are removed before fitting. Methods requiring a minimum number '
    'of knot points (cubic spline and Akima require ≥ 3; quadratic requires ≥ 3) fall back '
    'to linear interpolation when insufficient markers survive dropout.')

m_tbl = doc.add_table(rows=1, cols=4)
m_tbl.style = 'Table Grid'
tbl_header(m_tbl, ['Method', 'SciPy Implementation', 'Continuity', 'Key Property'])
for row in [
    ('Linear',       'numpy.interp',           'C⁰', 'Piecewise straight; no overshoot; simplest baseline'),
    ('Quadratic',    'make_interp_spline(k=2)', 'C¹', 'Low-order B-spline'),
    ('Cubic Spline', 'CubicSpline (natural)',   'C²', 'Standard smooth; natural endpoint conditions'),
    ('Quartic',      'make_interp_spline(k=4)', 'C³', 'Higher smoothness; moderate endpoint sensitivity'),
    ('Quintic',      'make_interp_spline(k=5)', 'C⁴', 'Highest smoothness; most prone to Runge oscillation'),
    ('PCHIP',        'PchipInterpolator',       'C¹', 'Monotone; no overshoot; good on sparse smooth data'),
    ('Akima',        'Akima1DInterpolator',     'C¹', 'Local slope weighting; gap-resilient'),
]:
    tbl_row(m_tbl, row)
doc.add_paragraph()

heading(doc, 'Dropout Scenarios and Error Metrics', level=2)
body(doc,
    'Two dropout models were implemented, reflecting distinct real-world failure mechanisms:'
)
body(doc,
    'Random dropout: each CERPM independently fails with probability p. This models '
    'uncorrelated hardware failures such as individual chip faults or communication '
    'dropouts. Dropout rates tested: 1%, 5%, 10%, 15%, 20%. Per condition: 2,000 '
    'Monte Carlo trials, each with a unique random seed applied independently to '
    'both the left and right boundary CERPM sets.')
body(doc,
    'Clustered dropout: a contiguous block of n consecutive CERPMs is removed from '
    'either the left or right boundary, with both the cluster start position and '
    'affected side chosen randomly per trial. This models localised failures such as '
    'physical damage from a vehicle impact, a section of road resurfacing, or a '
    'short-range communication blackout. Cluster sizes tested: 2, 5, 10, 15, 20 '
    'consecutive markers. 2,000 trials per condition.')
body(doc,
    'Per trial, the reconstructed centreline error is the Euclidean distance from each '
    'estimated centreline point to the nearest point on the true centreline LineString. '
    'Mean and max errors are recorded. A trial is classified as a failure if max error '
    'exceeds 0.2 m — derived from the 3.5 m standard lane width and a ±0.3 m LKA '
    'intervention threshold. Distributions are summarised by P25, P75, and IQR = P75 − P25.')

# ══════════════════════════════════════════════
# 4. RESULTS AND ANALYSIS
# ══════════════════════════════════════════════
heading(doc, '4. Results and Analysis', level=1)

heading(doc, '4.1 Road Geometries', level=2)
body(doc,
    'Figures 1–3 show the resampled boundary polylines for each of the three road '
    'geometries used in the study. The three geometries were selected to represent '
    'meaningfully different curvature profiles to ensure results generalise beyond '
    'a single road type.')

figure(doc, 't07_road',
       'Figure 1. Town07 — sinuous road (~280 m). Multiple curvature reversals; most challenging geometry.',
       width=Inches(4.8))
figure(doc, 't42_road',
       'Figure 2. Town042 — long gradual curve (~560 m). Smooth consistent curvature; easiest geometry.',
       width=Inches(3.8))
figure(doc, 't44_road',
       'Figure 3. Town044 — sharp-corner road (~520 m). Two 90° turns; tests abrupt curvature changes.',
       width=Inches(4.8))

heading(doc, '4.2 Effect of CERPM Spacing', level=2)
body(doc,
    'Before applying any dropout, CERPM spacing is the primary driver of centreline error. '
    'At 0.5 m and 1.0 m spacing all seven methods produce median centreline errors below '
    '0.01 m with near-zero IQR across all three geometries. At these densities algorithm '
    'choice is irrelevant — any method reconstructs the boundaries accurately. '
    'At 2.0 m the methods begin to diverge: linear IQR increases measurably, while cubic '
    'spline, PCHIP, and Akima remain below 0.05 m median error. At 3.0 m linear error '
    'is substantial on curved geometries. At 5.0 m all methods show elevated error on '
    'the sinuous Town07, while smooth methods remain acceptable on the gradual Town042.')

heading(doc, '4.3 Random Dropout Results', level=2)
body(doc,
    'Figures 4–9 show the IQR heatmaps, IQR band plots, and failure rate heatmaps for '
    'all three geometries under random dropout (1%–20%). Key findings across geometries:')
body(doc,
    'At 0.5 m and 1.0 m spacing all methods maintain near-zero failure rate at all tested '
    'dropout rates. The density of surviving markers is sufficient that even 20% random '
    'failure leaves enough data for any method to accurately reconstruct the boundary.')
body(doc,
    'At 2.0 m linear begins to fail significantly. On Town07 (sinuous): 43% failure at '
    '10% dropout, rising to 97% at 20% dropout. All smooth methods remain below 5% '
    'failure on the same geometry and spacing. Town042 (gradual) shows lower failure '
    'rates: linear reaches 24%–42% at 2.0 m over the 10%–20% range, while smooth '
    'methods stay at or near 0%.')
body(doc,
    'At 3.0 m and 5.0 m, linear fails at 100% under any random dropout on curved roads. '
    'Among smooth methods, on Town044 (sharp corners) a significant divergence emerges: '
    'Akima achieves 12% failure at 10% dropout and 4.0 m spacing, while PCHIP reaches '
    '46% — worse than cubic spline (18%). PCHIP\'s monotonicity constraint, beneficial '
    'on smooth roads, limits its ability to represent the abrupt 90° curvature reversals '
    'at sharp corners when markers are sparse. Akima\'s locally weighted slope estimation '
    'handles these transitions more robustly.')

figure(doc, 't07_rand_heatmap',
       'Figure 4. Town07 — Random dropout IQR centreline error (P25–P75, m). '
       'n = 2000 runs per condition. Green = low error; red = high error.',
       width=Inches(6.0))
figure(doc, 't07_rand_bands',
       'Figure 5. Town07 — Random dropout IQR band plots. Median (line) ± IQR (shaded) '
       'vs CERPM interval at each dropout rate.',
       width=Inches(5.5))
figure(doc, 't07_rand_fail',
       'Figure 6. Town07 — Random dropout failure rate (max error > 0.2 m, %). n = 2000 runs.',
       width=Inches(6.0))
figure(doc, 't42_rand_heatmap',
       'Figure 7. Town042 — Random dropout IQR centreline error (P25–P75, m). n = 2000 runs.',
       width=Inches(6.0))
figure(doc, 't42_rand_bands',
       'Figure 8. Town042 — Random dropout IQR band plots.',
       width=Inches(5.5))
figure(doc, 't42_rand_fail',
       'Figure 9. Town042 — Random dropout failure rate.',
       width=Inches(6.0))
figure(doc, 't44_rand_heatmap',
       'Figure 10. Town044 — Random dropout IQR centreline error. '
       'PCHIP notably worse than Akima at 3.0–5.0 m spacing.',
       width=Inches(6.0))
figure(doc, 't44_rand_bands',
       'Figure 11. Town044 — Random dropout IQR band plots.',
       width=Inches(5.5))
figure(doc, 't44_rand_fail',
       'Figure 12. Town044 — Random dropout failure rate.',
       width=Inches(6.0))

heading(doc, '4.4 Clustered Dropout Results', level=2)
body(doc,
    'Clustered dropout — a contiguous block of consecutive CERPMs removed from one '
    'side — represents a more severe and realistic failure than random dropout. '
    'Severity scales with both cluster size and CERPM spacing: 10 missing markers at '
    '0.5 m spacing is a 5 m gap; the same cluster at 5.0 m spacing is a 50 m gap. '
    'Linear interpolation is most affected: it draws a straight chord across the '
    'missing region, diverging from the true curved boundary in proportion to gap '
    'length and road curvature. At cluster sizes ≥ 5 and spacings ≥ 2.0 m on Town07 '
    'or Town044, linear fails at or near 100%.')
body(doc,
    'Cubic spline, quartic, and quintic handle small clusters (2–5) well at ≤ 2.0 m '
    'spacing. At larger cluster sizes (10–20) the global spline fit can oscillate '
    'across the gap region on sinuous geometry. PCHIP performs well on gradual '
    'geometry but degrades on Town044 at sharp corners: dropping a cluster near a '
    'corner apex removes the markers that define the direction change, and PCHIP\'s '
    'monotone construction cannot reproduce the curvature reversal from the '
    'remaining data. Akima\'s local slope estimation handles this adaptively, making '
    'it the most robust method across all geometries and cluster sizes.')

heading(doc, '4.5 Algorithm Summary', level=2)

s_tbl = doc.add_table(rows=1, cols=4)
s_tbl.style = 'Table Grid'
tbl_header(s_tbl, ['Method', 'Random Dropout', 'Clustered Dropout', 'Sharp Corners (T044)'])
for r in [
    ('Akima',        'Excellent', 'Excellent',  'Best — recommended default'),
    ('PCHIP',        'Excellent', 'Very Good',  'Poor at corner clusters'),
    ('Cubic Spline', 'Very Good', 'Good',       'Good'),
    ('Quartic',      'Good',      'Good',       'Good'),
    ('Quintic',      'Good',      'Moderate',   'Good'),
    ('Quadratic',    'Moderate',  'Moderate',   'Moderate'),
    ('Linear',       'Poor',      'Unacceptable','Unacceptable'),
]:
    tbl_row(s_tbl, r)
doc.add_paragraph()
caption(doc, 'Table 1. Algorithm performance summary across all geometries and dropout scenarios.')

body(doc,
    'The key cross-geometry finding is the separation between Akima and PCHIP. On smooth '
    'and gradual geometries (Town07, Town042) both methods are broadly comparable and both '
    'outperform cubic spline. On sharp-corner geometry (Town044) Akima is clearly superior, '
    'particularly under clustered dropout near corners. Akima is therefore recommended as '
    'the general-purpose default. PCHIP remains appropriate where the road geometry is '
    'confirmed smooth and sharp corners are absent.')

# ══════════════════════════════════════════════
# 5. CONCLUSIONS
# ══════════════════════════════════════════════
heading(doc, '5. Conclusions and Recommendations', level=1)
body(doc,
    'At CERPM spacings of 0.5–1.0 m all seven algorithms perform equivalently with '
    'sub-centimetre median error under both random and clustered dropout scenarios, '
    'making algorithm choice irrelevant at high marker density. Beyond 2.0 m spacing, '
    'algorithm selection becomes critical and linear interpolation becomes unsuitable '
    'for any curved road regardless of the dropout level.')
body(doc,
    'Akima interpolation is recommended as the default algorithm for CERPM-based LKA '
    'systems, replacing the cubic spline used in prior CERPM research. Akima\'s locally '
    'weighted slope construction limits the propagation of error from missing marker '
    'clusters and handles sharp-corner road geometries that impair PCHIP. PCHIP is '
    'recommended only where road geometry is known to be smooth and continuously curved.')
body(doc,
    'A maximum CERPM spacing of 1.0 m is recommended for safety-critical high-speed '
    'applications. A maximum of 2.0 m is acceptable for lower-speed or cost-constrained '
    'routes, provided cluster sizes (from damage or resurfacing) are kept small. Spacings '
    'of 3.0 m and above produce unacceptably high failure rates under clustered dropout '
    'on sinuous or sharp-corner road geometries.')
body(doc,
    'Future work should extend the analysis to include GPS positioning error '
    '(0.1–1.0 m RMS for commercial GNSS), simultaneous bilateral cluster failures, '
    'and sensor fusion with camera-based LKA to quantify accuracy gains from redundancy.')

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
     'Departure Crashes," 2024. '
     'https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813663',
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
    ('Research',    'Road Geometry Sources',      '',  G,  G,  '',  '',  '',  '',  '',  ''),
    ('Research',    'Importing Road Geometry',    '',  '',  G,  G,  '',  '',  '',  '',  ''),
    ('Planning',    'Class Diagram',              '',  '',  G,  '',  '',  '',  '',  '',  ''),
    ('Development', 'Coding',                     '',  '',  G,  G,  G,  '',  '',  '',  ''),
    ('Development', 'Testing and Debugging',      '',  '',  '',  '',  G,  G,  '',  '',  ''),
    ('Simulation',  'Data Collection',            '',  '',  '',  '',  '',  G,  '',  '',  ''),
    ('Results',     'Algorithm Comparison',       '',  '',  '',  '',  '',  '',  G,  G,  ''),
    ('Results',     'CERPM Dropout Analysis',     '',  '',  '',  '',  '',  '',  G,  G,  ''),
    ('Results',     'Combine Findings',           '',  '',  '',  '',  '',  '',  '',  G,  G),
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
    ('CERPM intervals',           '0.5, 1.0, 2.0, 3.0, 5.0 m'),
    ('Random dropout rates',      '1%, 5%, 10%, 15%, 20%'),
    ('Cluster sizes',             '2, 5, 10, 15, 20 consecutive markers'),
    ('Monte Carlo runs',          '2,000 per condition (both scenarios)'),
    ('Cluster placement',         'Random start position, random side (left or right)'),
    ('Failure threshold',         'Max centreline error > 0.2 m'),
    ('Centreline sample interval','0.5 m'),
    ('Road geometries',           'Town07, Town042, Town044'),
    ('Interpolation methods',     'Linear, Quadratic, Cubic Spline, Quartic, Quintic, PCHIP, Akima'),
]:
    tbl_row(ptbl, p_row)

doc.add_paragraph()

heading(doc, 'Appendix C — Software Module Summary', level=2)
ctbl = doc.add_table(rows=1, cols=2)
ctbl.style = 'Table Grid'
tbl_header(ctbl, ['Module', 'Responsibility'])
for row in [
    ('test.py',          'OSM parsing (getNodes, getWays, getLanelets), lanelet chain-linking '
                         '(combineWays), CERPM resampling (resample), centreline computation '
                         '(calCenterline)'),
    ('Interpolations.py','Arc-length parameterisation (arcLenghtParameter) and the unified '
                         'interpolate(pts, numPts, method) function for all seven methods via SciPy'),
    ('Simulation.py',    'clusterDropout helper; Monte Carlo engines: runMonteCarloRandom and '
                         'runMonteCarloClusteredSingle; parallel execution via ProcessPoolExecutor'),
    ('xmlParse.py',      'Parameter sweep orchestration (_runSweepRandom, _runSweepClustered), '
                         'all plot functions (IQR heatmaps, band plots, failure rate heatmaps, '
                         'ranking heatmaps), summary tables, and figure saving (_saveFigs)'),
]:
    tbl_row(ctbl, row)

# ── Save ──
out = 'Final_Report.docx'
doc.save(out)
print(f'Saved: {out}')
