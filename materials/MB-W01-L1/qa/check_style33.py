#!/usr/bin/env python3
"""Structural+typesetting QA for Math Blast Academic 3.3; not expert math review."""
import fitz,json,re,subprocess,hashlib,collections,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1]
tex=(R/'book.tex').read_text(encoding='utf8')
book=json.loads((R/'content/book.json').read_text(encoding='utf8'))
pdf=fitz.open(R/'book.pdf')
texts=[p.get_text() for p in pdf]
full='\n'.join(texts)
log=(R/'book.log').read_text(encoding='utf8',errors='replace')
fonts=subprocess.run(['pdffonts',str(R/'book.pdf')],capture_output=True,text=True).stdout
page_algorithms={}
for k in range(1,10):
    ix=[i+1 for i,t in enumerate(texts) if f'Алгоритм {k}. ' in t]
    page_algorithms[str(k)]=ix

checks={
    'pages_at_least_100':len(pdf)>=100,
    'all_A4_portrait':all(abs(p.rect.width-595.276)<1 and abs(p.rect.height-841.890)<1 for p in pdf),
    'body_11pt':r'\documentclass[11pt,a4paper,openany]{book}' in tex,
    'exact_geometry':r'\geometry{left=20mm,right=20mm,top=20mm,bottom=22mm}' in tex,
    'dejavu_embedded':'DejaVuSerif' in fonts and 'yes yes yes' in fonts,
    'russian_pdf_metadata':'Лёвин Артём' in (pdf.metadata.get('author') or ''),
    'pdf_latex_engine':'pdfTeX' in (pdf.metadata.get('producer') or ''),
    'line_spacing_1_21':r'\linespread{1.21}' in tex,
    'paragraph_spacing_043':r'\setlength{\parskip}{.43em}' in tex,
    'math_jot_7pt':r'\setlength{\jot}{7pt}' in tex,
    'no_indent':r'\setlength{\parindent}{0pt}' in tex,
    'palette_all_four':all(f'{{HTML}}{{{color}}}' in tex for color in ['243447','486780','66798B','BAC9D4']),
    'booktabs_tabularx_used':r'\begin{tabularx}' in tex and r'\toprule' in tex,
    'no_external_tikz_dependencies':r'\input{figures/' not in tex,
    'title_has_blank_student_field':r'\rule[-.8ex]{85mm}{.4pt}' in tex and 'Ученик:' in texts[0] and 'ФИО_Ученика' not in texts[0],
    'title_has_blank_attribution_field':r'\rule[-.8ex]{70mm}{.4pt}' in tex and 'Лёвин Артём Александрович эксклюзивно для' in texts[0],
    'bookmarked_toc_present':len(pdf.get_toc())>=30,
    'footer_page_over_total':f'{len(pdf)} / {len(pdf)}' in texts[-1],
    '39_mini_exercises_in_content':len(book['theory_mini'])==13 and sum(map(len,book['theory_mini']))==39,
    '13_theory_mini_groups_in_PDF':sum(t.count('Мини-тренировка: три коротких шага') for t in texts)==13,
    'nine_flowchart_pages':all(len(pgs)==1 for pgs in page_algorithms.values()),
    'no_training_on_flowchart_pages':all('MB-W01-L1-PR-' not in texts[pgs[0]-1] and 'Тренировочный блок' not in texts[pgs[0]-1] for pgs in page_algorithms.values()),
    'nine_training_sections':sum(bool(re.search(r'Тренировочный блок\s+[1-9]\s+[·.]',t)) for i,t in enumerate(texts) if i>=10)==9,
    'nine_four_column_answer_tables':tex.count(r'\begin{tabularx}{\textwidth}{@{}p{10mm}X p{10mm}X@{}}')==9,
    'original_90_problems_preserved':len(book['practice'])==90 and all(p['id'] in full for p in book['practice']),
    'original_30_examples_preserved':len(book['examples'])==30 and all(x['id'] in full for x in book['examples']),
    'full_solutions_preserved':len([p for p in book['practice'] if p['solution']])==90,
    'no_overfull_hbox':'Overfull \\hbox' not in log,
    'no_missing_glyphs':'Missing character:' not in log,
    'no_undefined_reference':'undefined references' not in log.lower(),
    'all_pages_contain_text':all(len(t)>180 for t in texts),
    'text_blocks_within_media':all(all(x[0]>-2 and x[1]>-2 and x[2]<pg.rect.width+2 and x[3]<pg.rect.height+2 for x in pg.get_text('blocks') if len(x)>4 and x[4].strip()) for pg in pdf),
}
items={'checks':checks,'passed':sum(checks.values()),'total':len(checks),'unpassed':[k for k,v in checks.items() if not v],
       'pages':len(pdf),'algorithms_on_pages':page_algorithms,'toc_entries':len(pdf.get_toc()),
       'text_chars_min':min(map(len,texts)), 'text_chars_median':statistics.median(map(len,texts)),
       'overfull_hbox':len(re.findall(r'^Overfull',log,re.M)),
       'underfull_hbox':len(re.findall(r'^Underfull \\hbox',log,re.M)),
       'underfull_vbox':len(re.findall(r'^Underfull \\vbox',log,re.M)),
       'pdf_sha256':hashlib.sha256((R/'book.pdf').read_bytes()).hexdigest(),
       'content_sha256':hashlib.sha256((R/'content'/'book.json').read_bytes()).hexdigest()}
(R/'qa'/'style33-results.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(items,ensure_ascii=False,indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
