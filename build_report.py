from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

FONT = 'Times New Roman'
SZ   = Pt(12)

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.5)

doc.styles['Normal'].font.name = FONT
doc.styles['Normal'].font.size = SZ
for hn in ['Heading 1','Heading 2','Heading 3']:
    s = doc.styles[hn]
    s.font.name = FONT; s.font.size = SZ
    s.font.bold = True; s.font.color.rgb = RGBColor(0,0,0)

def _r(p, text):
    for i,part in enumerate(re.split(r'\*\*(.*?)\*\*', text)):
        r = p.add_run(part); r.font.name = FONT; r.font.size = SZ
        if i%2==1: r.bold = True

def body(text):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6); _r(p,text)

def h1(t): _h(1,t)
def h2(t): _h(2,t)
def _h(lv,t):
    h = doc.add_heading('',lv)
    h.paragraph_format.space_before = Pt(10); h.paragraph_format.space_after = Pt(4)
    r = h.runs[0] if h.runs else h.add_run()
    r.text=t; r.font.name=FONT; r.font.size=SZ; r.font.bold=True; r.font.color.rgb=RGBColor(0,0,0)

def bullet(text):
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(3); _r(p,text)

def nbullet(text):
    p = doc.add_paragraph(style='List Number'); p.paragraph_format.space_after = Pt(3); _r(p,text)

def tbl(headers, rows):
    t = doc.add_table(rows=1+len(rows), cols=len(headers)); t.style='Table Grid'
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=h
        for r in c.paragraphs[0].runs: r.bold=True; r.font.name=FONT; r.font.size=SZ
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for ri,row in enumerate(rows):
        for ci,val in enumerate(row):
            c=t.rows[ri+1].cells[ci]; c.text=val
            for r in c.paragraphs[0].runs: r.font.name=FONT; r.font.size=SZ
    doc.add_paragraph()

def pb(): doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════════
for _ in range(3): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Lane Keep Assist Using Chip Enabled Raised Pavement Markers:\nInterpolation Algorithm Robustness Under CERPM Dropout Conditions')
r.font.name=FONT; r.font.size=Pt(16); r.bold=True

doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Final Research Report — Advanced Driver Assistance Systems')
r.font.name=FONT; r.font.size=Pt(13); r.bold=True

doc.add_paragraph()
for label, value in [('Author:', 'Alexander Bruce'), ('Date:', 'June 2026')]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1=p.add_run(f'{label}  '); r1.bold=True; r1.font.name=FONT; r1.font.size=SZ
    r2=p.add_run(value); r2.font.name=FONT; r2.font.size=SZ

doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Student Contributions'); r.bold=True; r.font.name=FONT; r.font.size=SZ
tbl(['Student','Role','Contribution'],
    [['Alexander Bruce','Sole author',
      'Literature review; simulation framework; Monte Carlo execution; analysis; report']])
pb()

# ══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════════════════
h1('Abstract')
body(
    'This report presents the Lane Keep Assist (LKA) sub-system of a group Advanced Driver '
    'Assistance Systems (ADAS) project. Current camera-based LKA degrades under poor lane '
    'markings and adverse weather [6] — conditions associated with the highest crash risk. '
    'A Vehicle-to-Infrastructure (V2I) alternative using Chip Enabled Raised Pavement Markers '
    '(CERPMs) has been shown to outperform commercial vision systems [1][2], but prior work '
    'used only cubic spline interpolation and assumed complete marker availability. This project '
    'fills that gap: seven interpolation algorithms were evaluated via Monte Carlo simulation '
    '(n = 2,000 runs per condition) under random dropout (1–20%) and clustered contiguous '
    'dropout (cluster sizes 2–20) at six CERPM spacings (0.5–12.0 m), where 12 m reflects '
    'the real-world deployment interval used in the foundational literature [2]. Quintic and '
    'quartic B-splines with arc-length parameterisation consistently achieved the lowest error '
    'and failure rates. At the literature deployment spacing of 12 m, all methods reach 100% '
    'failure under clustered dropout, demonstrating that finer spacing is necessary for '
    'robust real-world deployment.'
)
pb()

# ══════════════════════════════════════════════════════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════════
h1('1. Introduction')
body(
    'Lane departure is a leading cause of road fatalities. In Australia, 62% of all road '
    'deaths nationally are attributable to lane departure events — rising to 73% in regional '
    'and 71% in remote areas [3]. The NHTSA estimates LKA-equipped vehicles are 24% less '
    'likely to be involved in fatal road departure crashes [4], and the EU has mandated LKA '
    'on all new vehicles sold after July 2024 [5]. LKA applies corrective steering when a '
    'vehicle drifts toward a lane boundary without signalling, and forms the foundation of '
    'higher-level ADAS functionality.'
)
body(
    'Current LKA systems use front-facing cameras, but field benchmarking via the OpenLKA '
    'dataset [6] confirmed substantial degradation under poor lane markings and adverse '
    'weather — precisely the conditions most associated with fatal crashes on regional roads. '
    'Sharma et al. [1] and Kadav et al. [2] demonstrated that CERPMs — GPS-transmitting road '
    'studs — outperform the Mobileye 630 vision system across all tested conditions, with '
    'an effective sensing range of 350 m versus 31 m for the camera. Their experiments '
    'physically deployed CERPMs at 40-foot (~12 m) intervals. However, both studies applied '
    'cubic spline interpolation without evaluating alternatives and did not investigate '
    'the impact of missing markers on reconstruction accuracy.'
)
body(
    'This project addresses that gap. Three research questions are investigated: '
    '(RQ1) Which algorithm provides the most accurate centreline reconstruction under CERPM '
    'dropout? (RQ2) At what spacing and dropout severity does reconstruction error exceed '
    'the 0.2 m safety threshold? (RQ3) Is clustered dropout more damaging than random '
    'dropout at equivalent effective loss rates?'
)

# ══════════════════════════════════════════════════════════════════════════════
# 2. LITERATURE REVIEW
# ══════════════════════════════════════════════════════════════════════════════
h1('2. Literature Review')
body(
    'LKA technology has advanced from simple threshold-based detection to deep learning lane '
    'detection combined with Kalman filtering. Fakhari and Anwar [7][8] proposed a Multiple '
    'Model Adaptive Estimation (MMAE) approach fusing front and rear cameras with a Kalman '
    'filter, improving detection under night and adverse weather conditions. Perozzi et al. [9] '
    'demonstrated a shared sliding-mode controller for steer-by-wire LKA that smoothly '
    'transitions authority between driver and automated system. Wei et al. [10] reviewed LKA '
    'assessment methodologies and identified standardisation gaps across performance, safety, '
    'and driver interaction dimensions.'
)
body(
    'On the infrastructure sensing side, Sharma et al. [1] introduced CERPMs as an '
    'energy-efficient IIS achieving at least 90% energy savings over commercial camera '
    'solutions. Kadav et al. [2] extended this to lane centering and lane change, deploying '
    'CERPMs at 40 ft (~12 m) spacing. Where the Mobileye failed to detect lane markings '
    'for 93.3% of a sharp-curve route, the CERPM system maintained reconstruction '
    'throughout. Critically, both studies used cubic spline interpolation — the method '
    'originally proposed for road centreline fitting by Burden and Faires [11] — without '
    'exploring alternatives or simulating marker failures.'
)
body(
    'Higher-order B-splines (de Boor [12]), PCHIP (Fritsch and Carlson [13]), and Akima '
    'splines [14] each address different limitations of cubic spline in sparse data '
    'scenarios. Arc-length parameterisation (Hartley and Zisserman [15]) is essential for '
    'all these methods when marker spacing becomes irregular after dropout. No prior work '
    'has applied these alternatives to the CERPM lane reconstruction problem, nor '
    'characterised accuracy under marker failure — establishing the clear need for '
    'this research.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
h1('3. Methodology')
body(
    'A Python simulation framework was developed across four modules: **test.py** (Lanelet2 '
    'OSM parser, CERPM placement, ground-truth centreline computation); **Interpolations.py** '
    '(seven interpolation methods with arc-length parameterisation); **Simulation.py** '
    '(parallelised Monte Carlo engine with random and clustered dropout); and **xmlParse.py** '
    '(full parameter sweep, statistical aggregation, and visualisation).'
)
body(
    'Road geometry was sourced from the Town07 Lanelet2 map — a standardised autonomous '
    'driving environment with varied curve types. The ground-truth centreline was computed '
    'by resampling both boundary linestrings to 500 arc-length fractions and averaging '
    'paired points. CERPM positions were simulated at six uniform spacings: 0.5, 1, 2, 4, '
    '6, and 12 m, where 12 m corresponds to the ~40 ft deployment in Kadav et al. [2].'
)
body(
    'Two dropout models were applied. **Random dropout** removed each marker independently '
    'at rates of 1%, 5%, 10%, 15%, and 20%, modelling uncorrelated faults. **Clustered '
    'dropout** removed a single contiguous run of 2, 5, 10, 15, or 20 markers from one '
    'boundary per trial, modelling localised failure (flooding, surface damage). Seven '
    'interpolation algorithms were tested:'
)
tbl(
    ['Method','Continuity','Key property'],
    [
        ['Linear',           'C⁰','Piecewise straight; baseline comparison'],
        ['Quadratic spline', 'C¹','Smooth; low computational cost'],
        ['Cubic spline',     'C²','Used in prior CERPM work [1][2]'],
        ['Quartic spline',   'C³','Higher-order curvature flexibility'],
        ['Quintic spline',   'C⁴','Highest order tested; very smooth'],
        ['PCHIP',            'C¹','Monotone; no overshoot between knots'],
        ['Akima',            'C¹','Locally weighted; limits gap propagation'],
    ]
)
body(
    'All methods use arc-length parameterisation. Methods requiring ≥ 3 points (cubic spline, '
    'Akima) fall back to linear when fewer points survive dropout. For each of the 420 '
    'parameter combinations, 2,000 independent seeded Monte Carlo trials were executed in '
    'parallel using ProcessPoolExecutor. Per trial, perpendicular distance from the '
    'reconstructed centreline to the ground truth was measured via Shapely geometry, '
    'yielding mean error and max error. Statistics reported are: IQR (P75 − P25 of mean '
    'error) as the primary robustness metric, and failure rate (proportion of trials '
    'where max error > 0.2 m) as the safety-relevant threshold, aligned to ISO 21448 and '
    'SAE J3016 positioning accuracy requirements.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 4. RESULTS AND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
h1('4. Results and Analysis')

h2('4.1. Random Dropout')
body(
    'Under random dropout, higher-order polynomial B-splines (quadratic through quintic) '
    'maintain near-zero IQR at spacings up to 4 m across all dropout rates. Linear '
    'interpolation diverges markedly beyond 2 m spacing: at 4 m and 20% dropout, linear '
    'reaches failure rates of 100%, while quadratic through quintic remain below 65% and '
    'cubic spline below 76%. At 6 m spacing the polynomial splines show failure rates '
    'of 54–82% at 20% dropout, while linear reaches 100% even at 1% dropout.'
)
body(
    'At the literature deployment spacing of **12 m**, all methods fail at rates of '
    '100% under random dropout of 9% or above. Even at 1% random dropout and 12 m '
    'spacing, linear interpolation fails at 100%. Quadratic through quintic reach '
    '100% failure by 5% random dropout at 12 m. This confirms that 12 m spacing is '
    'fundamentally insufficient for any algorithm under realistic random dropout rates, '
    'directly challenging the viability of the deployment interval used in the '
    'foundational literature [2].'
)

h2('4.2. Clustered Dropout')
body(
    'Clustered dropout produces more severe degradation. The IQR band plots (exhaustive '
    'enumeration) show linear interpolation reaching median IQR values exceeding 8 m at '
    'cluster size 20 and 12 m spacing — far larger than a lane width. Even quintic and '
    'quartic B-splines show IQR values of several metres at these extreme conditions, '
    'though their advantage over linear remains clear at moderate conditions.'
)
body(
    'The clustered failure rate heatmap reveals the critical finding: at 12 m spacing, '
    '**all methods reach 100% failure for every tested cluster size.** At 6 m spacing, '
    'linear interpolation reaches 100% failure at cluster size 2, while quartic and '
    'quintic reach 29% failure at cluster size 2, rising to 100% at cluster size 10. '
    'At 4 m spacing, polynomial splines maintain below 10% failure for cluster sizes '
    'of 2, but exceed 80% at cluster size 10. PCHIP consistently underperforms the '
    'polynomial methods at larger cluster sizes — at cluster size 20, 6 m spacing, '
    'PCHIP reaches 100% failure while cubic spline reaches 66% and quartic/quintic '
    'reach 70–76%.'
)
body(
    'At moderate conditions (cluster size ≤ 5, spacing ≤ 2 m), quartic and quintic '
    'B-splines maintain below 4% failure, compared to 53% for linear at the same '
    'conditions. This confirms the practical operating envelope: CERPM-based LKA '
    'with polynomial spline reconstruction is robust only at spacings of 2 m or '
    'finer with small cluster sizes.'
)

h2('4.3. Method Rankings and Key Findings')
tbl(
    ['Rank','Method','Clustered (cs=5, 4m)','Random (20%, 4m)','Notes'],
    [
        ['1','Quintic B-spline','36%','65%','Best or tied-best across all conditions'],
        ['2','Quartic B-spline','35%','65%','Effectively equal to quintic'],
        ['3','Cubic spline',    '39%','76%','Prior CERPM baseline; outperformed at large gaps'],
        ['4','Quadratic spline','40%','71%','Robust; minimal gap vs cubic'],
        ['5','Akima',           '50%','77%','Moderate; falls back to linear below 3 points'],
        ['6','PCHIP',           '60%','80%','Monotonicity constraint harmful for curved gaps'],
        ['7','Linear',          '100%','100%','Unsafe at any spacing ≥ 2 m with dropout'],
    ]
)
body(
    '**RQ1:** Quintic and quartic B-splines are the best-performing methods across all '
    'conditions. Cubic spline — the prior CERPM standard — is outperformed at larger '
    'cluster sizes and coarser spacings.'
)
body(
    '**RQ2:** The 0.2 m safety threshold is exceeded by linear interpolation at any '
    'clustered gap ≥ 2 markers with spacing ≥ 4 m (100% failure). Polynomial splines '
    'begin significant failure at cluster size 10+ and spacing ≥ 4 m. At 12 m spacing '
    'all methods fail under any dropout.'
)
body(
    '**RQ3:** Clustered dropout is substantially more damaging than random dropout at '
    'equivalent average loss fractions. Removing 10 contiguous markers eliminates all '
    'geometric information across a continuous road section; the same 10 markers removed '
    'randomly leave local context intact at most points.'
)

h2('4.4. Deviations from Initial Research Plan')
body(
    'The initial plan proposed testing at 5 m and 12 m spacings among others. The '
    'simulation was implemented at 0.5, 1, 2, 4, 6, and 12 m — the 12 m condition was '
    'included to directly match the real-world deployment in [2]. A smoothing spline '
    '(scipy UnivariateSpline) was implemented but excluded from the sweep as it does '
    'not pass through known CERPM coordinates exactly, which is unacceptable when '
    'marker positions are precisely known. Testing across multiple road maps remains '
    'a limitation and is recommended for future work.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 5. CONCLUSIONS AND RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('5. Conclusions and Recommendations')
body(
    'This project provides the first systematic evaluation of interpolation algorithm '
    'robustness for CERPM-based lane centreline reconstruction. Five conclusions are drawn:'
)
nbullet('**Quintic and quartic B-splines with arc-length parameterisation are the recommended algorithms**, outperforming cubic spline — the current literature default — particularly under clustered dropout with large gap sizes.')
nbullet('**Linear interpolation is unsafe at spacings above 1 m** under any realistic dropout. It reaches 100% failure at 4 m spacing even with cluster size 2, and must not be used in any deployed CERPM-based LKA system.')
nbullet('**The 12 m (~40 ft) real-world deployment spacing from Kadav et al. [2] is insufficient** for robust reconstruction under any tested failure mode. All methods reach 100% failure at this spacing under clustered dropout of any tested size, and under random dropout above approximately 5%.')
nbullet('**Clustered dropout is the more dangerous failure mode.** Spatially correlated marker loss destroys geometric information across an extended road section, producing larger errors than equivalent-rate random loss.')
nbullet('**2 m spacing is the recommended minimum** for CERPM deployment on curved road sections when using polynomial spline reconstruction, with robust performance achieved at cluster sizes up to 5 and random dropout up to 20%.')

doc.add_paragraph()
body('Recommendations for practitioners:')
bullet('Use **quintic or quartic B-spline** interpolation with arc-length parameterisation as the default reconstruction algorithm; cubic spline is an acceptable fallback.')
bullet('Deploy CERPMs at **≤ 2 m spacing** on curved sections. The 40 ft spacing used in [2] requires revision given the results presented here.')
bullet('Implement **clustered-gap detection**: when > 10 consecutive markers fail to report on either boundary, trigger fallback to camera sensing or raise a driver alert.')
bullet('**Future work** should validate across multiple road maps, test GPS positioning uncertainty, and evaluate fusion of CERPM and camera inputs under combined failure modes.')

# ══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
pb()
h1('References')
refs = [
    '[1]  S. Sharma et al., "Vehicle Lateral Offset Estimation Using Infrastructure Information for Reduced Compute Load," SAE Technical Paper 2023-01-0800, Apr. 2023.',
    '[2]  P. Kadav et al., "Automated Lane Centering: An Off-the-Shelf Computer Vision Product vs. Infrastructure-Based Chip-Enabled Raised Pavement Markers," Sensors, vol. 24, no. 7, p. 2327, Apr. 2024.',
    '[3]  Dept. of Infrastructure, Transport, Cities and Regional Development, "Fact sheet: Evidence supporting the priority focus areas," National Road Safety Strategy, 2021.',
    '[4]  NHTSA, "Estimating Effectiveness of Lane Keeping Assist Systems in Fatal Road Departure Crashes," Report 813663, 2024.',
    '[5]  European Commission, "Mandatory drivers assistance systems expected to help save over 25,000 lives by 2038," Jul. 2024.',
    '[6]  Y. Wang et al., "OpenLKA: Open Source Multimodal LKA Dataset," GitHub, 2025.',
    '[7]  I. Fakhari and S. Anwar, "A Multiple Model Estimation Approach to Robust Lane Detection via Computer Vision Based Models," in Proc. IEEE ISIE, 2022, pp. 576–581.',
    '[8]  I. Fakhari and S. Anwar, "Computer vision model based robust lane detection using MMAE methodology," Frontiers in Mechanical Engineering, vol. 11, Feb. 2025.',
    '[9]  G. Perozzi et al., "Lateral Shared Sliding Mode Control for LKA in Steer-by-Wire Vehicles," IEEE Trans. Intelligent Vehicles, vol. 8, no. 4, pp. 3073–3082, 2023.',
    '[10] S. Wei et al., "State of the Art: Assessment Methods for Lane Keeping Assistance Systems," IEEE Trans. Intelligent Vehicles, vol. 9, no. 9, pp. 5853–5875, 2024.',
    '[11] R. L. Burden and J. D. Faires, Numerical Analysis, 9th ed. Brooks/Cole, 2011.',
    '[12] C. de Boor, A Practical Guide to Splines, Revised ed. Springer, 2001.',
    '[13] F. N. Fritsch and R. E. Carlson, "Monotone piecewise cubic interpolation," SIAM J. Numerical Analysis, vol. 17, no. 2, pp. 238–246, 1980.',
    '[14] H. Akima, "A new method of interpolation and smooth curve fitting," J. ACM, vol. 17, no. 4, pp. 589–602, 1970.',
    '[15] R. Hartley and A. Zisserman, Multiple View Geometry in Computer Vision, 2nd ed. Cambridge University Press, 2003.',
    '[16] ISO 21448:2022, Road Vehicles — Safety of the Intended Functionality, ISO, 2022.',
    '[17] SAE International, SAE J3016: Taxonomy and Definitions for Driving Automation Systems, 2021.',
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(1.2)
    p.paragraph_format.first_line_indent = Cm(-1.2)
    r = p.add_run(ref); r.font.name=FONT; r.font.size=SZ

# ══════════════════════════════════════════════════════════════════════════════
# APPENDIX A
# ══════════════════════════════════════════════════════════════════════════════
pb()
h1('Appendix A: Code Module Descriptions')
tbl(
    ['Module','Responsibility','Key functions'],
    [
        ['test.py',          'Lanelet2 parser; CERPM resampling; centreline computation', 'resample(), calCenterline()'],
        ['Interpolations.py','Seven interpolation methods; arc-length parameterisation',  'arcLengthParameter(), interpolate()'],
        ['Simulation.py',    'Parallelised Monte Carlo; dropout models; error measurement','runMonteCarloRandom(), runMonteCarloClusteredSingle()'],
        ['xmlParse.py',      'Parameter sweep; IQR/failure stats; visualisation',         'fullAnalysis()'],
    ]
)
body(
    'Reproducibility: each trial seed is derived from a master base seed via numpy default_rng(). '
    'Re-running with identical base seed produces bit-identical results. '
    'Fallback logic: cubic spline and Akima revert to linear when fewer than 3 points survive; '
    'B-spline degree is clamped to min(k, n−1) where n is surviving point count.'
)

doc.save('/home/user/road-writing/Report.docx')
print("Done.")
