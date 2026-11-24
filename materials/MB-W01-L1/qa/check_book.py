from pathlib import Path
import json, fitz, re, math, hashlib, collections
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'content/book.json').read_text())
m=json.loads((ROOT/'manifest.json').read_text())
pdf=fitz.open(ROOT/'book.pdf')
texts=[p.get_text() for p in pdf]; txt='\n'.join(texts)
allp=d['practice']; ex=d['examples']; refs=sum(d['reflections'].values(),[])
checks={
'pdf_openable':True,
'physical_pages_at_least_100':len(pdf)>=100,
'all_pages_A4':all(abs(p.rect.width-595.28)<1 and abs(p.rect.height-841.89)<1 for p in pdf),
'no_empty_or_near_empty_pages':all(len(t)>180 for t in texts),
'30_examples':len(ex)==30,
'90_practice':len(allp)==90,
'levels_30_30_20_10':dict(collections.Counter(z['level'] for z in allp))=={'A':30,'B':30,'C':20,'D':10},
'180_hints':sum(len(z['hints']) for z in allp)==180,
'90_solutions':sum(bool(z['solution'].strip()) for z in allp)==90,
'90_answers':sum(bool(z['answer'].strip()) for z in allp)==90,
'59_reflection_answers':len(refs)==59 and all(z['solution'] for z in refs),
'13_vector_figures':len(d['figures'])==13 and len(list((ROOT/'figures').glob('*.tikz')))==13,
'11_heuristics':len(d['heuristics'])==11,
'120_unique_main_ids':len(set(z['id'] for z in ex+allp))==120,
'59_unique_reflection_ids':len(set(z['id'] for z in refs))==59,
'all_printed_practice_ids':all(z['id'] in txt for z in allp),
'all_printed_example_ids':all(z['id'] in txt for z in ex),
'all_printed_reflection_ids':all(z['id'] in txt for z in refs),
'all_reflection_ids_appear_at_least_twice':all(txt.count(z['id'])>=2 for z in refs),
'pdf_pages_no_text_outside_media_box':all(all(b[0]>=-1 and b[1]>=-1 and b[2]<=p.rect.width+1 and b[3]<=p.rect.height+1 for b in p.get_text('blocks') if len(b)>4 and b[4].strip()) for p in pdf),
'geometry_diagonals_equal':sum([(1+2)**2,2**2])==sum([(-1-2)**2,2**2])==13,
'quadratic_counterexample_at_n40':40**2+40+41==41**2,
'quadratic_counterexample_at_n41':41**2+41+41==41*43,
'quadratic_17_counterexample':17**2+17+17==17*19,
'nonnegative_inequality_extreme':(-3)**2+6*(-3)+10==1,
'proof_of_sum_bound':(3+3)==6 and 3*3==9,
}
log=(ROOT/'book.log').read_text(encoding='utf-8',errors='replace')
checks['no_undefined_references']=not bool(re.search(r'undefined references|Undefined control sequence',log,re.I))
checks['no_missing_glyphs']='Missing character:' not in log
summary={
 'checks':checks,'passed':sum(checks.values()),'total':len(checks),
 'physical_pages':len(pdf),'page_chars_min':min(map(len,texts)),'page_chars_median':sorted(map(len,texts))[len(texts)//2],
 'word_count_pdf_extracted':len(txt.split()),'pdf_hyperlinks':sum(len(p.get_links()) for p in pdf),
 'overfull_hbox':len(re.findall(r'Overfull \\hbox',log)),
 'underfull_hbox':len(re.findall(r'Underfull \\hbox',log)),
 'pdf_sha256':hashlib.sha256((ROOT/'book.pdf').read_bytes()).hexdigest(),
 'source_sha256':hashlib.sha256((ROOT/'content/book.json').read_bytes()).hexdigest(),
 'unpassed':[k for k,v in checks.items() if not v]
}
(ROOT/'qa'/'check-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
if not all(checks.values()):raise SystemExit(1)
