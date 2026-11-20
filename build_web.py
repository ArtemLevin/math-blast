#!/usr/bin/env python3
"""Rebuild Math Blast lesson 01 HTML directly from canonical content/book.json.
No third-party HTTP dependency.  Run: python build_web.py
"""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
WEB=ROOT/'books'/'MB-W01-L1'
source=WEB/'content.json'
data=json.loads(source.read_text('utf-8'))
raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
(WEB/'index.html').write_text((WEB/'book_shell.html').read_text('utf-8').replace('__BOOK_DATA__',raw),encoding='utf-8')
sha=lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest={
 'book_id':data['book_id'],'lesson_id':data['lesson_id'],'module':data['module'],'week':data['week'],'slot':data['slot'],
 'title':data['title'],'plan_source_sha':data['plan_source_sha'],'route':'books/MB-W01-L1/index.html',
 'book_content_sha256':sha(source),'book_pdf_sha256':sha(ROOT/'materials/MB-W01-L1/book.pdf'),
 'web_revision':sha(WEB/'index.html'),
 'web_status':'PREVIEW','manual_status':'DRAFT','date':'2026-11-20',
 'theory_section_ids':[f'theory-{i+1:02}' for i in range(len(data['theory']))],
 'example_ids':[e['id'] for e in data['examples']],
 'problem_ids':[p['id'] for p in data['practice']],
 'hint_ids':[p['id'] for p in data['practice'] for _ in p['hints']],
 'solution_ids':[p['id'] for p in data['practice']],
 'answer_ids':[p['id'] for p in data['practice']],
 'reflection_ids':[v['id'] for g in data['reflections'].values() for v in g],
 'figure_ids':data['figures'],
 'flow_diagrams':[f'algorithm-{i:02}' for i in range(1,len(data['flow_blocks'])+1)],
 'source_count':len(data['sources']),
 'notes':'Preview only until 02_REVIEW_MANUAL.md independent review approves PDF. Student progress stored under separate namespace.'}
(WEB/'web-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('HTML',len((WEB/'index.html').read_bytes()),'bytes; content sha',manifest['book_content_sha256']);print('PDF sha',manifest['book_pdf_sha256']);print('web sha',manifest['web_revision'])