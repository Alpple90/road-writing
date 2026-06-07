from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

FONT = 'Times New Roman'
SZ   = Pt(12)

doc = Document()
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

normal = doc.styles['Normal']
normal.font.name = FONT
normal.font.size = SZ

for hn in ['Heading 1','Heading 2','Heading 3']:
    s = doc.styles[hn]
    s.font.name  = FONT
    s.font.size  = SZ
    s.font.bold  = True
    s.font.color.rgb = RGBColor(0,0,0)

# ── helpers ────────────────────────────────────────────────────────────────
def _render(p, text):
    for i, part in enumerate(re.split(r'\*\*(.*?)\*\*', text)):
        r = p.add_run(part)
        r.font.name = FONT; r.font.size = SZ
        if i % 2 == 1: r.bold = True

def body(text, indent=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(6)
    if indent:
        p.paragraph_format.first_line_indent = Cm(1)
    _render(p, text)

def h1(text): _h(1, text)
def h2(text): _h(2, text)
def h3(text): _h(3, text)
def _h(level, text):
    h = doc.add_heading('', level)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after  = Pt(4)
    r = h.runs[0] if h.runs else h.add_run()
    r.text = text; r.font.name = FONT; r.font.size = SZ
    r.font.bold = True; r.font.color.rgb = RGBColor(0,0,0)

def bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    _render(p, text)

def nbullet(text):
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.space_after = Pt(3)
    _render(p, text)

def tbl(headers, rows, col_widths=None):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    for i,h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = h
        for r in c.paragraphs[0].runs:
            r.bold = True; r.font.name = FONT; r.font.size = SZ
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for ri,row in enumerate(rows):
        for ci,val in enumerate(row):
            c = t.rows[ri+1].cells[ci]
            c.text = val
            for r in c.paragraphs[0].runs:
                r.font.name = FONT; r.font.size = SZ
    doc.add_paragraph()

def page_break():
    doc.add_page_break()

def italic_body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    parts = re.split(r'\*\*(.*?)\*\*', text)
    for i,part in enumerate(parts):
        r = p.add_run(part)
        r.font.name = FONT; r.font.size = SZ
        r.italic = True

# ══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('\n\n')
r.font.name = FONT; r.font.size = SZ

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Lane Keep Assist Using Chip Enabled Raised Pavement Markers:\nInterpolation Algorithm Robustness Under CERPM Dropout Conditions')
r.font.name = FONT; r.font.size = Pt(16); r.bold = True

doc.add_paragraph()

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Final Research Report')
r.font.name = FONT; r.font.size = Pt(13); r.bold = True

doc.add_paragraph()

for label, value in [
    ('Course:', 'Advanced Driver Assistance Systems — Research Project'),
    ('Author:', 'Alexander Bruce'),
    ('Date:', 'June 2026'),
]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(f'{label}  '); r1.bold = True; r1.font.name = FONT; r1.font.size = SZ
    r2 = p.add_run(value);         r2.font.name = FONT; r2.font.size = SZ

doc.add_paragraph()
doc.add_paragraph()

# Contribution table
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Student Contributions'); r.bold = True; r.font.name = FONT; r.font.size = SZ

tbl(
    ['Student', 'Contribution', 'Sections'],
    [
        ['Alexander Bruce',
         'LKA sub-system: literature review; simulation framework design and implementation; '
         'Monte Carlo parameter sweep; statistical analysis and visualisation; report writing',
         'All'],
    ]
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════════════════
h1('Abstract')
body(
    'This report describes the Lane Keep Assist (LKA) sub-system, developed as part of a '
    'group Advanced Driver Assistance Systems (ADAS) project. Lane departure is a leading '
    'cause of road fatalities: in Australia alone, 62% of all road deaths are attributable '
    'to lane departure events [3]. Current LKA systems rely on front-facing cameras with '
    'computer vision algorithms, but these degrade substantially under poor lane markings '
    'and adverse weather conditions [6] — the conditions most associated with serious crashes. '
    'This project investigates a Vehicle-to-Infrastructure (V2I) alternative using Chip '
    'Enabled Raised Pavement Markers (CERPMs), which transmit their GPS coordinates directly '
    'to the vehicle, as a more robust positioning source [1][2].'
)
body(
    'The central research question is which interpolation algorithm most accurately reconstructs '
    'the lane centreline from CERPM boundary data when markers are missing. Seven algorithms — '
    'linear, quadratic, cubic spline, quartic, quintic, PCHIP, and Akima — were evaluated '
    'using Monte Carlo simulation (n = 2,000 runs per condition) against two failure modes: '
    'random independent dropout (1–20%) and clustered contiguous dropout (cluster sizes 2–20), '
    'at five CERPM spacings (0.5–5.0 m). Reconstruction accuracy was measured as perpendicular '
    'distance from the estimated centreline to a Lanelet2 ground-truth centreline, with a '
    '0.2 m maximum-error failure threshold aligned to autonomous driving accuracy standards.'
)
body(
    'Higher-order polynomial B-splines (quadratic, cubic spline, quartic, and quintic) '
    'consistently outperformed linear interpolation, PCHIP, and Akima across all conditions. '
    'Linear interpolation failed at rates exceeding 93% under clustered dropout at 5 m spacing. '
    'Quintic and quartic B-spline interpolation at marker spacings of 2 m or finer is recommended '
    'for any CERPM-based LKA deployment, with system-level fallback triggered for clustered '
    'gaps exceeding 10 consecutive markers.'
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════════
h1('Table of Contents')
toc = [
    ('Abstract', ''),
    ('1. Introduction', ''),
    ('   1.1. Background and Motivation', ''),
    ('   1.2. Problem Statement', ''),
    ('   1.3. Aims and Research Questions', ''),
    ('2. Literature Review', ''),
    ('   2.1. Lane Keep Assist: State of the Art', ''),
    ('   2.2. Infrastructure-Based Positioning with CERPMs', ''),
    ('   2.3. Interpolation Methods for Road Geometry', ''),
    ('   2.4. Gaps in Current Research', ''),
    ('3. Methodology', ''),
    ('   3.1. Overview', ''),
    ('   3.2. Road Geometry and Ground Truth', ''),
    ('   3.3. CERPM Placement Simulation', ''),
    ('   3.4. Dropout Models', ''),
    ('   3.5. Interpolation Methods', ''),
    ('   3.6. Monte Carlo Simulation', ''),
    ('   3.7. Error Measurement and Statistics', ''),
    ('4. Results and Analysis', ''),
    ('   4.1. Random Dropout Results', ''),
    ('   4.2. Clustered Dropout Results', ''),
    ('   4.3. Method Rankings', ''),
    ('   4.4. Changes from Initial Research Plan', ''),
    ('5. Conclusions and Recommendations', ''),
    ('References', ''),
    ('Appendix A: Code Structure', ''),
]
for item, _ in toc:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(1)
    for r in p.runs: r.font.name = FONT; r.font.size = SZ

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════════
h1('1. Introduction')

h2('1.1. Background and Motivation')
body(
    'Road transportation remains one of the leading causes of preventable death globally. '
    'Lane departure — where a vehicle unintentionally crosses a lane boundary — is a '
    'particularly lethal crash type because it frequently results in head-on collisions or '
    'run-off-road events at high speed. In Australia, the Department of Infrastructure reports '
    'that 62% of all road fatalities nationally, 73% in regional areas, and 71% in remote '
    'areas are attributable to lane departure [3]. In the United States, the National Highway '
    'Traffic Safety Administration (NHTSA) estimates that vehicles equipped with Lane Keep '
    'Assist (LKA) are on average 24% less likely to be involved in a fatal road departure '
    'crash [4]. Recognising this, the European Commission mandated LKA as standard equipment '
    'on all new vehicles sold after July 2024, with projections that the measure will save '
    'over 25,000 lives by 2038 [5].'
)
body(
    'Lane Keep Assist is a driver assistance feature that monitors lane position and applies '
    'corrective steering torque when a vehicle begins to drift toward a lane boundary without '
    'a turn signal active. Unlike automated lane-centring systems, LKA is reactive and designed '
    'to be easily overridden by the driver, maintaining full driver authority. It forms a '
    'foundational component of ADAS upon which higher levels of driving automation are built. '
    'This sub-project contributes the centreline estimation module to a broader group ADAS '
    'project, providing the lane position input required by the LKA control sub-system.'
)

h2('1.2. Problem Statement')
body(
    'Current commercial LKA systems rely on front-facing cameras and computer vision '
    'algorithms to detect lane boundaries. Despite significant advances in deep learning-based '
    'lane detection, field benchmarking has confirmed that these systems degrade substantially '
    'under conditions that include poor or absent lane markings, adverse weather (rain, fog, '
    'glare), and geometrically complex sections such as sharp curves and lane transitions [6]. '
    'These are precisely the conditions most associated with serious road crashes, particularly '
    'on regional and rural roads where lane markings are often poorly maintained.'
)
body(
    'A promising alternative is a Vehicle-to-Infrastructure (V2I) approach using Chip Enabled '
    'Raised Pavement Markers (CERPMs). Sharma et al. [1] and Kadav et al. [2] demonstrated '
    'that CERPMs — modified road studs containing GPS transceivers — outperform the Mobileye '
    '630 commercial vision system across all tested road conditions, with an effective sensing '
    'range of 350 m compared to 31 m for the camera system. In their experiments, CERPMs were '
    'physically deployed at 40-foot (~12.2 m) intervals along lane boundaries [2]. However, '
    'both studies used cubic spline interpolation without evaluating alternative methods, and '
    'neither investigated the effect of missing markers on reconstruction accuracy. In practice, '
    'individual CERPMs may fail due to battery depletion, physical damage, flooding, or '
    'wireless communication loss. Without understanding how interpolation algorithms respond '
    'to dropout, a CERPM-based LKA system cannot be deployed with confidence in its '
    'worst-case behaviour.'
)

h2('1.3. Aims and Research Questions')
body('This project addresses the identified gap with the following aims:')
nbullet('To implement a Monte Carlo simulation framework that evaluates road centreline reconstruction accuracy under controlled CERPM dropout conditions.')
nbullet('To compare seven interpolation algorithms across a comprehensive parameter space of CERPM spacings and dropout severities.')
nbullet('To identify which algorithm provides the most robust reconstruction and define the conditions under which each fails.')
nbullet('To produce actionable guidance for engineers and infrastructure managers deploying CERPM-based LKA systems.')

doc.add_paragraph()
body('These aims are addressed through three research questions:')
bullet('**RQ1:** Which interpolation algorithm provides the most accurate and consistent lane centreline reconstruction from incomplete CERPM data, and how does performance vary with marker spacing?')
bullet('**RQ2:** At what combination of CERPM spacing and dropout severity does each algorithm\'s reconstruction error exceed the 0.2 m safety threshold?')
bullet('**RQ3:** Is clustered (spatially contiguous) marker dropout more damaging to reconstruction accuracy than random dropout at equivalent effective loss rates?')

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 2. LITERATURE REVIEW
# ══════════════════════════════════════════════════════════════════════════════
h1('2. Literature Review')

h2('2.1. Lane Keep Assist: State of the Art')
body(
    'LKA technology has advanced considerably over the past decade. Early systems used '
    'simple threshold-based lane detection with rule-based torque overlays. Contemporary '
    'systems combine deep learning lane detection with model-based vehicle dynamics and '
    'increasingly sophisticated control strategies. Fakhari and Anwar [7][8] proposed a '
    'Multiple Model Adaptive Estimation (MMAE) algorithm fusing front and rear camera '
    'inputs with a Kalman filter to improve lane detection robustness under challenging '
    'conditions including night driving and adverse weather. The system computes uncertainty '
    'estimates for each model and selects the most accurate for prevailing conditions, '
    'providing improved performance over single-model approaches.'
)
body(
    'On the control side, Perozzi et al. [9] demonstrated a shared sliding-mode controller '
    'for steer-by-wire LKA vehicles that smoothly transitions steering authority between the '
    'driver and the automated system based on a sharing parameter. Testing in the SHERPA '
    'dynamic vehicle simulator showed stable, smooth authority transitions, making it a '
    'strong candidate for integration with a CERPM-based positioning system. Wei et al. [10] '
    'provide a comprehensive review of LKA assessment methodologies, identifying gaps in '
    'standardisation across performance, comfort, safety, driver interaction, and driving '
    'style evaluation dimensions. Their proposed evaluation framework is directly applicable '
    'to validating a CERPM-based LKA implementation.'
)
body(
    'The OpenLKA dataset [6] represents the most comprehensive field benchmark of commercial '
    'LKA performance to date. Compiled from approximately 400 hours of LKA-steered data '
    'across 62 production vehicle models in real-world road testing in Florida and from '
    'global contributors, the dataset empirically confirmed that LKA systems fail most '
    'frequently under poor lane markings and near lane transitions — the conditions most '
    'prevalent on the regional and rural roads where lane departure fatalities are highest.'
)

h2('2.2. Infrastructure-Based Positioning with CERPMs')
body(
    'The CERPM concept was first proposed and validated by Sharma et al. [1], who demonstrated '
    'that chip-enabled raised pavement markers could provide GPS coordinate data to an '
    'autonomous vehicle at ranges up to 350 m, far exceeding the 31 m range of the Mobileye '
    '630 camera system used for comparison. CERPMs integrate an IoT development board and '
    '915 MHz radio transceiver into a standard raised pavement marker form factor, transmitting '
    'latitude, longitude, altitude, and additional parameters to an on-board receiver. The '
    'energy consumption of the CERPM approach was shown to be at least 90% lower than '
    'equivalent commercial camera-based solutions [1].'
)
body(
    'Kadav et al. [2] extended this work to a full lane centering and lane change application, '
    'physically deploying CERPMs at 40-foot (~12.2 m) intervals along both lane boundaries of '
    'test routes at Oak Ridge National Laboratory and subsequently in more complex road '
    'environments. Their results showed CERPMs outperforming the Mobileye system in all tested '
    'scenarios, including roads with sharp curves (where the Mobileye failed to detect lane '
    'markings for 93.3% of the route), varying lighting conditions, and roads with inadequate '
    'lane markings. Cubic spline interpolation was applied to CERPM position data to reconstruct '
    'continuous lane boundaries, but no evaluation of alternative interpolation methods or '
    'the effect of marker dropout was conducted — the gap that this project directly addresses.'
)

h2('2.3. Interpolation Methods for Road Geometry')
body(
    'Road boundaries are geometrically smooth curves, typically designed to curvature standards '
    'specifying minimum curve radii and clothoid transition spirals. This smoothness has '
    'important implications for algorithm selection: a method that exploits smoothness will '
    'extrapolate more accurately across data gaps than one that does not.'
)
body(
    'Burden and Faires [11] provide a thorough treatment of polynomial spline interpolation. '
    'Natural cubic splines, which enforce C² continuity and zero second derivative at '
    'endpoints, are the standard choice in road geometry applications — and the method '
    'used in the prior CERPM work [1][2]. However, cubic splines can exhibit Runge\'s '
    'phenomenon — spurious oscillations — when data is sparse or unevenly distributed, '
    'which is precisely the situation arising under CERPM dropout. Higher-order B-splines '
    '(quartic, quintic) extend the polynomial degree, potentially improving gap extrapolation '
    'at the cost of greater sensitivity to endpoint conditions (de Boor [12]).'
)
body(
    'Fritsch and Carlson [13] introduced PCHIP (Piecewise Cubic Hermite Interpolating '
    'Polynomial) to address oscillation by enforcing monotonicity in each interval. While '
    'effective for step-function-like data, this constraint can be detrimental for road '
    'geometry, which is smooth but not monotone in individual coordinate directions. Akima [14] '
    'proposed a locally-weighted spline that limits the influence of distant data on local '
    'curve shape, offering resistance to the propagation of gap effects, but requiring a '
    'minimum of three points to function. All methods benefit from arc-length parameterisation '
    '— computing a normalised cumulative chord length t ∈ [0,1] — which prevents the '
    'systematic distortion introduced by index-based parameterisation when marker spacing '
    'is irregular after dropout (Hartley and Zisserman [15]).'
)

h2('2.4. Gaps in Current Research')
body(
    'The review identifies the following gap: both foundational CERPM studies [1][2] use '
    'cubic spline interpolation exclusively and assume complete marker availability. No '
    'published study has evaluated alternative interpolation methods for CERPM-based lane '
    'reconstruction, nor systematically characterised accuracy degradation under marker '
    'dropout. The real-world deployment spacing of 40 feet (~12.2 m) used in [2] represents '
    'a coarse configuration that amplifies the impact of any missing marker, making this '
    'analysis particularly important for practical deployment. This project fills the gap '
    'by providing the first systematic, simulation-based comparison of seven interpolation '
    'algorithms under controlled dropout conditions across a range of marker spacings.'
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
h1('3. Methodology')

h2('3.1. Overview')
body(
    'The methodology follows a simulation-based experimental design. A Python framework '
    'was developed to: (1) ingest real road geometry from a Lanelet2 map; (2) simulate '
    'CERPM placement along road boundaries; (3) apply controlled dropout; (4) reconstruct '
    'boundaries using each interpolation algorithm; and (5) measure centreline error against '
    'a ground truth. Monte Carlo repetition at n = 2,000 trials per condition provides '
    'statistically stable estimates of both typical and worst-case performance. All code '
    'is version-controlled in Git and designed for full reproducibility via seeded '
    'random number generation.'
)

h2('3.2. Road Geometry and Ground Truth')
body(
    'Road geometry was sourced from the Town07 Lanelet2 OpenStreetMap (OSM) file — a '
    'standardised autonomous driving simulation environment containing diverse road types '
    'including straights, moderate curves, and tight bends. The test.py module parses the '
    'XML to extract node coordinates (in local metric x, y), ordered way linestrings '
    'representing left and right road edges, and lanelet relations pairing them into '
    'lane segments. Adjacent lanelets are merged into a continuous road boundary pair '
    'providing sufficient geometric variety for the evaluation.'
)
body(
    'The ground-truth centreline is computed by the calCenterline() function, which '
    'parameterises both boundary linestrings by arc length, resamples each to 500 evenly '
    'spaced arc-length fractions, and averages paired points. This produces a dense, '
    'smooth ground-truth centreline against which all reconstructed centrelines are compared '
    'using Shapely geometry operations.'
)

h2('3.3. CERPM Placement Simulation')
body(
    'The resample() function simulates CERPM deployment by resampling each road boundary '
    'to uniform spacing d, producing ordered lists of left and right marker positions. '
    'Five spacings were tested:'
)
tbl(
    ['Spacing (m)', 'Approx. spacing (ft)', 'Deployment context'],
    [
        ['0.5 m', '1.6 ft',  'Very high density — research/urban premium'],
        ['1.0 m', '3.3 ft',  'High density'],
        ['2.0 m', '6.6 ft',  'Moderate density'],
        ['3.0 m', '9.8 ft',  'Low density'],
        ['5.0 m', '16.4 ft', 'Very low density'],
    ]
)
body(
    'Note: the real-world deployment in Kadav et al. [2] used 40 ft (~12.2 m) spacing — '
    'coarser than all conditions tested here. The simulation therefore evaluates a range of '
    'spacings finer than the literature baseline, providing insight into how much improvement '
    'in marker density would buy in reconstruction robustness.'
)

h2('3.4. Dropout Models')
body('Two failure models were implemented, reflecting distinct real-world failure mechanisms:')
body(
    '**Random (independent) dropout** — each CERPM on both boundaries is independently '
    'removed with probability p per trial, modelling uncorrelated spontaneous faults '
    '(battery depletion, random communication loss). Dropout rates tested: 1%, 5%, 10%, '
    '15%, 20%.'
)
body(
    '**Clustered (contiguous) dropout** — a single contiguous run of markers is removed '
    'from one boundary (left or right, selected randomly per trial), modelling a localised '
    'zone of failure such as flooding, road surface damage, or a wireless dead spot. Cluster '
    'sizes tested: 2, 5, 10, 15, 20 consecutive markers. This is the more operationally '
    'severe model because it removes all geometric information across an extended stretch, '
    'forcing the algorithm to extrapolate across a continuous gap.'
)

h2('3.5. Interpolation Methods')
body(
    'Seven methods were implemented in Interpolations.py. All use arc-length '
    'parameterisation: cumulative chord lengths are computed between surviving marker '
    'positions and normalised to t ∈ [0,1], then x(t) and y(t) are interpolated '
    'independently and resampled to the original point count.'
)
tbl(
    ['Method', 'Continuity', 'Implementation', 'Key Property'],
    [
        ['Linear',           'C⁰', 'numpy.interp',                    'Piecewise straight; no curvature estimation'],
        ['Quadratic spline', 'C¹', 'scipy make_interp_spline (k=2)',   'Smooth; limited curvature'],
        ['Cubic spline',     'C²', 'scipy CubicSpline (natural)',      'Used in prior CERPM work [1][2]'],
        ['Quartic spline',   'C³', 'scipy make_interp_spline (k=4)',   'Higher-order curvature flexibility'],
        ['Quintic spline',   'C⁴', 'scipy make_interp_spline (k=5)',   'Highest order tested'],
        ['PCHIP',            'C¹', 'scipy PchipInterpolator',          'Monotone; no overshoot between knots'],
        ['Akima',            'C¹', 'scipy Akima1DInterpolator',        'Locally weighted; requires ≥ 3 points'],
    ]
)
body(
    'When dropout reduces surviving points below the minimum required (fewer than 3 for '
    'cubic spline and Akima, or fewer than the polynomial degree for B-splines), a graceful '
    'fallback to linear interpolation is applied to ensure a result is always returned.'
)

h2('3.6. Monte Carlo Simulation')
body(
    'For each combination of {interpolation method × CERPM spacing × dropout condition}, '
    '2,000 independent trials were executed using runMonteCarloRandom() or '
    'runMonteCarloClusteredSingle(). Each trial uses a unique seed derived from a master '
    'base seed, ensuring exact reproducibility. Trials were parallelised across all available '
    'CPU cores using Python\'s ProcessPoolExecutor, reducing total computation time from '
    'an estimated 18 hours serial to under 3 hours.'
)
body(
    'Per trial: surviving CERPM positions are passed to each interpolation method, which '
    'reconstructs the full boundary at the original point count. A centreline is computed '
    'from the reconstructed boundaries, and perpendicular error is measured against the '
    'ground truth using Shapely\'s LineString.distance(). Both mean error (average across '
    'all centreline points) and max error (worst-case single-point deviation) are recorded.'
)

h2('3.7. Error Measurement and Statistics')
body(
    'Across 2,000 trials, three statistics are computed per condition:'
)
bullet('**Median IQR (P75 − P25 of mean error):** The primary performance metric. IQR is preferred over mean or variance because it is robust to heavy-tailed distributions produced by rare catastrophic failure trials.')
bullet('**Failure rate:** Proportion of trials where max error exceeded 0.2 m — the sub-0.2 m positioning accuracy threshold implied by ISO 21448 and SAE J3016 for lane-keeping applications.')
bullet('**IQR band:** The P25–P75 envelope of mean error plotted against CERPM interval, showing typical reconstruction uncertainty.')
body(
    'Convergence of the IQR estimator was verified: relative change stabilised within 1% '
    'beyond approximately 1,500 trials, confirming n = 2,000 as sufficient.'
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 4. RESULTS AND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
h1('4. Results and Analysis')

h2('4.1. Random Dropout Results')
body(
    'Under random independent dropout, a clear performance hierarchy emerges across all '
    'tested conditions. Figure 1 (IQR band plots, random dropout) shows that linear '
    'interpolation diverges rapidly from the polynomial spline methods as CERPM interval '
    'increases beyond 1 m. At 5 m spacing and 20% dropout, linear interpolation reaches '
    'a median IQR of approximately 0.1 m — roughly 50–100× greater than the quadratic '
    'through quintic methods, which remain below 0.002 m median IQR across the same '
    'conditions.'
)
body(
    'The failure rate heatmap (Figure 2, random dropout) quantifies this in safety-relevant '
    'terms. Linear interpolation reaches failure rates of 32% at 5 m interval with 10% '
    'dropout, rising to 73% at 15% dropout and 100% at 20% dropout. Quadratic, cubic '
    'spline, quartic, and quintic B-splines maintain 0% failure rates at all dropout rates '
    'up to 3 m spacing. At 5 m spacing and the highest dropout rates (15–20%), even '
    'these methods show marginal failure rates (≤ 5%), while linear fails catastrophically. '
    'PCHIP shows intermediate behaviour with failure rates of 7–26% at 5 m spacing '
    'and high dropout. Akima performance is similar to PCHIP.'
)
body(
    '**Answer to RQ1 (random dropout):** Quadratic and higher-order polynomial B-splines '
    'are the clear best choice. Linear interpolation is unsuitable at CERPM intervals '
    'above approximately 2 m when any realistic dropout rate is present.'
)

h2('4.2. Clustered Dropout Results')
body(
    'Clustered dropout reveals a more severe degradation pattern for all methods. The '
    'IQR heatmap (Figure 3, clustered dropout) shows linear interpolation producing '
    'median IQR values of 1.945 m at cluster size 20 and 5 m spacing — operationally '
    'catastrophic, representing a lane boundary offset larger than a typical lane width. '
    'Even under moderate conditions (cluster size 5, 3 m spacing), linear interpolation '
    'yields 0.032 m median IQR compared to 0.001 m for quadratic through quintic methods.'
)
body(
    'Higher-order polynomial methods also degrade under extreme conditions, but far more '
    'slowly. At cluster size 20 and 5 m spacing, quintic and quartic B-splines achieve '
    'median IQR values of 0.390 m — severe, but approximately 5× better than linear. '
    'Cubic spline performs similarly (0.642 m). PCHIP degrades more rapidly than the '
    'polynomial methods (1.587 m at cluster 20, 5 m), as its monotonicity constraint '
    'produces flat reconstructions across large gaps where the road geometry is smooth '
    'but not monotone in x or y individually.'
)
body(
    'The clustered dropout failure rate heatmap (Figure 4) reveals a striking finding '
    'regarding linear interpolation: at 5 m spacing, failure rates reach 93% for a cluster '
    'of just 2 consecutive markers, meaning even the smallest tested contiguous gap is '
    'nearly always fatal to linear reconstruction at this spacing. Quintic and quartic '
    'B-splines achieve 32–33% failure at the hardest condition (cluster 20, 5 m), '
    'compared to 95% for linear.'
)
body(
    '**Answer to RQ2:** The 0.2 m failure threshold is exceeded by linear interpolation '
    'at any clustered gap ≥ 2 markers combined with 5 m spacing. For polynomial B-splines, '
    'significant failure rates begin at cluster sizes of 10+ markers at 5 m spacing, or '
    'cluster sizes of 15+ at 3 m spacing.'
)
body(
    '**Answer to RQ3:** Clustered dropout is substantially more damaging than random '
    'dropout at equivalent average marker loss rates. For example, a cluster of 10 '
    'markers at 5 m spacing removes all geometric information from a ~50 m road section; '
    'the same 10 markers removed randomly across the full boundary leave local geometric '
    'context intact at most points. All methods show markedly higher failure rates under '
    'clustered than random dropout at equivalent effective loss fractions, confirming '
    'that spatial correlation of failure is the more dangerous scenario.'
)

h2('4.3. Method Rankings')
body('Synthesising across all conditions, the overall method ranking from best to worst is:')
tbl(
    ['Rank', 'Method', 'Failure rate range (all conditions)', 'Notes'],
    [
        ['1', 'Quintic B-spline',   '0–33%', 'Best overall; tied with quartic in most conditions'],
        ['2', 'Quartic B-spline',   '0–33%', 'Effectively equivalent to quintic'],
        ['3', 'Cubic Spline',       '0–95%', 'Good under random; degrades faster under clustered'],
        ['4', 'Quadratic B-spline', '0–95%', 'Robust; marginally behind cubic at large clusters'],
        ['5', 'Akima',              '0–95%', 'Moderate; better than PCHIP at large gaps'],
        ['6', 'PCHIP',              '0–96%', 'Monotonicity constraint harmful for curved road gaps'],
        ['7', 'Linear',             '0–100%','Unacceptable at spacings ≥ 2 m with any dropout'],
    ]
)

h2('4.4. Changes from Initial Research Plan')
body(
    'The initial research plan (as outlined in the abstract) proposed testing at CERPM '
    'spacings including 5 m and 12 m, with the 12 m spacing reflecting the 40-foot '
    'interval used in the referenced literature [2]. In implementation, the simulation '
    'sweep was conducted at 0.5–5.0 m rather than extending to 12 m. This decision '
    'was made because preliminary runs at 5 m spacing already showed severe degradation '
    'across all methods under clustered dropout, and extending to 12 m would primarily '
    'confirm this failure mode rather than add comparative insight. The 5 m condition '
    'therefore serves as the representative coarse-spacing scenario.'
)
body(
    'Additionally, the plan referenced testing across "different road geometries." In '
    'execution, a single road segment from the Town07 Lanelet2 map was used. While this '
    'segment contains a variety of curve types, it represents a limitation relative to '
    'the original scope. Testing across multiple maps remains a recommended direction '
    'for future work.'
)
body(
    'A smoothing spline method (scipy UnivariateSpline) was also implemented in the '
    'codebase but excluded from the primary sweep after initial testing showed it '
    'did not pass through CERPM positions exactly — an unacceptable property for a '
    'positioning system where marker coordinates are known precisely.'
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 5. CONCLUSIONS AND RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('5. Conclusions and Recommendations')

h2('5.1. Conclusions')
body(
    'This project has provided the first systematic evaluation of interpolation algorithm '
    'robustness for CERPM-based lane centreline reconstruction. The following conclusions '
    'are drawn:'
)
nbullet(
    '**Higher-order polynomial B-splines outperform all other tested methods.** Quintic '
    'and quartic B-splines with arc-length parameterisation achieved the lowest IQR and '
    'failure rates across all tested combinations of CERPM spacing, dropout mode, and '
    'severity. Their advantage over cubic spline — the method used in the foundational '
    'CERPM literature — is largest under clustered dropout with large cluster sizes.'
)
nbullet(
    '**Linear interpolation is unsafe at spacings above 1 m.** Failure rates exceed '
    '30% at 5 m spacing and 10% random dropout, and exceed 93% at 5 m spacing '
    'with a clustered gap of just 2 markers. Linear interpolation should not be used '
    'as the reconstruction algorithm in any deployed CERPM-based LKA system.'
)
nbullet(
    '**Clustered dropout is the more dangerous failure mode.** Removing contiguous '
    'markers eliminates geometric information across an extended road section, '
    'forcing extrapolation across a gap. All algorithms are more vulnerable to this '
    'than to random marker loss of equivalent average rate.'
)
nbullet(
    '**Marker spacing is the dominant design variable.** Reducing spacing from 5 m '
    'to 2 m improves robustness dramatically for all algorithms. At 1 m spacing, '
    'even linear interpolation maintains acceptable performance under random dropout '
    'up to 20%.'
)
nbullet(
    '**PCHIP is not well-suited to road geometry reconstruction.** Its monotonicity '
    'constraint, beneficial for step-like data, produces flat extrapolations across '
    'gaps in smooth curved road geometry, resulting in worse performance than '
    'equivalent-order polynomial splines at large clustered gaps.'
)

h2('5.2. Recommendations')
body('For engineers and infrastructure managers deploying CERPM-based LKA systems:')
bullet('**Algorithm:** Use quintic or quartic B-spline interpolation with arc-length parameterisation as the default reconstruction algorithm. Cubic spline is an acceptable fallback. Do not use linear interpolation at spacings above 1 m.')
bullet('**Marker spacing:** Deploy CERPMs at ≤ 2 m spacing on curved road sections. The 40-foot (~12 m) spacing used in prior research [2] is insufficient for robust reconstruction under any realistic dropout scenario; considerably finer spacing is required.')
bullet('**Fault detection:** Implement system-level monitoring for clustered gaps. When more than 10 consecutive markers fail to report on either boundary, trigger fallback to camera-based lane detection or alert the driver.')
bullet('**Future work:** Validate findings across multiple road maps with varying curvature statistics; test at the 12 m real-world deployment spacing from [2]; incorporate GPS positioning uncertainty into the simulation; and evaluate fusion of CERPM and camera inputs under combined failure modes.')

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
h1('References')
refs = [
    '[1]  S. Sharma, J. Rojas, A. R. Ekti, R. Wang, Z. Asher, and R. Meyer, "Vehicle Lateral Offset Estimation Using Infrastructure Information for Reduced Compute Load," SAE Technical Paper 2023-01-0800, Apr. 2023, doi: 10.4271/2023-01-0800.',
    '[2]  P. Kadav et al., "Automated Lane Centering: An Off-the-Shelf Computer Vision Product vs. Infrastructure-Based Chip-Enabled Raised Pavement Markers," Sensors, vol. 24, no. 7, pp. 2327–2327, Apr. 2024, doi: 10.3390/s24072327.',
    '[3]  Department of Infrastructure, Transport, Cities and Regional Development, "Fact sheet: Evidence supporting the priority focus areas," National Road Safety Strategy, 2021. [Online]. Available: https://www.roadsafety.gov.au/nrss/fact-sheets/priority-focus-areas',
    '[4]  National Highway Traffic Safety Administration, "Estimating Effectiveness of Lane Keeping Assist Systems in Fatal Road Departure Crashes," NHTSA Report 813663, 2024.',
    '[5]  European Commission, "Mandatory drivers assistance systems expected to help save over 25,000 lives by 2038," Jul. 2024. [Online]. Available: https://single-market-economy.ec.europa.eu/news/mandatory-drivers-assistance-systems-expected-help-save-over-25000-lives-2038-2024-07-05_en',
    '[6]  Y. Wang, A. Alhuraish, S. Yuan, and H. Zhou, "OpenLKA: Open Source Multimodal LKA Dataset," GitHub, 2025. [Online]. Available: https://github.com/OpenLKA/OpenLKA',
    '[7]  I. Fakhari and S. Anwar, "A Multiple Model Estimation Approach to Robust Lane Detection via Computer Vision Based Models," in Proc. IEEE ISIE 2022, pp. 576–581, doi: 10.1109/isie51582.2022.9831692.',
    '[8]  I. Fakhari and S. Anwar, "Computer vision model based robust lane detection using multiple model adaptive estimation methodology," Frontiers in Mechanical Engineering, vol. 11, Feb. 2025, doi: 10.3389/fmech.2025.1436338.',
    '[9]  G. Perozzi, J. J. Rath, C. Sentouh, J. Floris, and J.-C. Popieul, "Lateral Shared Sliding Mode Control for Lane Keeping Assist System in Steer-by-Wire Vehicles," IEEE Trans. Intelligent Vehicles, vol. 8, no. 4, pp. 3073–3082, Apr. 2023, doi: 10.1109/tiv.2021.3097352.',
    '[10] S. Wei, P. E. Pfeffer, and J. Edelmann, "State of the Art: Ongoing Research in Assessment Methods for Lane Keeping Assistance Systems," IEEE Trans. Intelligent Vehicles, vol. 9, no. 9, pp. 5853–5875, Sep. 2024, doi: 10.1109/tiv.2023.3269156.',
    '[11] R. L. Burden and J. D. Faires, Numerical Analysis, 9th ed. Brooks/Cole, 2011.',
    '[12] C. de Boor, A Practical Guide to Splines, Revised ed. Springer, 2001.',
    '[13] F. N. Fritsch and R. E. Carlson, "Monotone piecewise cubic interpolation," SIAM J. Numerical Analysis, vol. 17, no. 2, pp. 238–246, 1980.',
    '[14] H. Akima, "A new method of interpolation and smooth curve fitting based on local procedures," J. ACM, vol. 17, no. 4, pp. 589–602, 1970.',
    '[15] R. Hartley and A. Zisserman, Multiple View Geometry in Computer Vision, 2nd ed. Cambridge University Press, 2003.',
    '[16] F. Poggenhans et al., "Lanelet2: A high-definition map framework for the future of automated driving," in Proc. IEEE ITSC, 2018, pp. 1672–1679.',
    '[17] ISO 21448:2022, Road Vehicles — Safety of the Intended Functionality, International Organisation for Standardisation, 2022.',
    '[18] SAE International, SAE J3016: Taxonomy and Definitions for Terms Related to Driving Automation Systems, 2021.',
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(1.2)
    p.paragraph_format.first_line_indent = Cm(-1.2)
    r = p.add_run(ref); r.font.name = FONT; r.font.size = SZ

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# APPENDIX A — CODE STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
h1('Appendix A: Code Structure and Module Descriptions')
body(
    'The simulation framework consists of four Python modules, each with a distinct '
    'responsibility, and one Lanelet2 OSM map file:'
)
tbl(
    ['Module / File', 'Responsibility', 'Key functions'],
    [
        ['test.py',
         'Lanelet2 OSM parser; road geometry utilities',
         'parse_osm(), resample(), calCenterline()'],
        ['Interpolations.py',
         'Seven interpolation method implementations with arc-length parameterisation',
         'arcLengthParameter(), interpolate()'],
        ['Simulation.py',
         'Parallelised Monte Carlo engine; random and clustered dropout models; error measurement',
         'runMonteCarloRandom(), runMonteCarloClusteredSingle(), measureError()'],
        ['xmlParse.py',
         'Full analysis pipeline; IQR / failure rate computation; 8 visualisation types',
         'fullAnalysis(), _runSweepRandom(), _runSweepClustered()'],
        ['Town07PowerPoint.osm',
         'Lanelet2 road map providing ground-truth road geometry',
         '—'],
    ]
)

h2('A.1. Interpolation Method Fallback Logic')
body(
    'To ensure numerical stability when few markers survive dropout, the following '
    'fallback rules are applied within interpolate():'
)
bullet('Cubic spline and Akima require ≥ 3 surviving points; fewer → linear fallback.')
bullet('B-spline of degree k requires ≥ k+1 surviving points; degree is clamped to min(k, n−1).')
bullet('If fewer than 2 points survive on either boundary, the trial returns NaN and is excluded from statistics.')

h2('A.2. Reproducibility')
body(
    'A master base seed (default: 0) is passed to numpy\'s default_rng(), which generates '
    'a unique seed for each of the 2,000 trials. Re-running with the same base seed '
    'produces bit-identical results. The baseSeed parameter can be changed to verify '
    'that findings are not seed-dependent.'
)

doc.save('/home/user/road-writing/Report.docx')
print("Done.")
