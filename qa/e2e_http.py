#!/usr/bin/env python3
"""Real-HTTP browser, localStorage, WCAG axe and full-SVG print checks for MB-W01-L1.

Unlike the isolated smoke suite, this loads every script/image via actual HTTP from
an ephemeral server rooted at the checked-out repository. Exits nonzero on failure.
"""
from __future__ import annotations
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import fitz
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parents[1]
QA=ROOT/'qa'/'http-results'
QA.mkdir(exist_ok=True,parents=True)
PORT=8765
BASE=f'http://127.0.0.1:{PORT}'
BOOK=BASE+'/books/MB-W01-L1/index.html'
SRC=json.loads((ROOT/'books/MB-W01-L1/content.json').read_text())
CHECKS={}
ISSUES=[]

def ck(name,ok,detail=''):
    CHECKS[name]=bool(ok)
    if not ok: ISSUES.append(f'{name}: {detail}')
    print(('PASS' if ok else 'FAIL'),name,str(detail)[:180],flush=True)

def started():
    for _ in range(80):
        try:
            with urllib.request.urlopen(BASE+'/books/MB-W01-L1/app.css',timeout=1) as r:
                if r.status==200:return True
        except OSError: time.sleep(.15)
    return False

log=(QA/'server.log').open('w')
server=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
errors=[]
try:
    ck('HTTP server responds',started())
    if not CHECKS['HTTP server responds']:raise RuntimeError('Server startup failed')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(viewport={'width':1440,'height':900},accept_downloads=True)
        page=context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        r=page.goto(BOOK,wait_until='domcontentloaded',timeout=60000)
        ck('Book served with HTTP 200',r is not None and r.status==200, r.status if r else None)
        page.wait_for_function('window.__MB_TEST__ && document.querySelector(".book-cover")',timeout=60000)
        page.wait_for_timeout(1000)
        ck('Book loads its canonical data',page.evaluate('window.__MB_TEST__.BOOK.practice.length')==90)
        ck('MathJax SVG renders',page.locator('mjx-container').count()>0)
        ck('No failed resources',not page.evaluate('Array.from(document.images).some(x=>x.complete&&!x.naturalWidth)'))
        old_value=json.dumps({'done':{'1':True},'ratings':{'A':3},'theme':'dark'},ensure_ascii=False)
        page.evaluate('(v)=>localStorage.setItem("olympiad_math_plan_v2",v)',old_value)
        page.evaluate('location.hash="#practice"');page.wait_for_timeout(800)
        ck('First practice page has ten tasks',page.locator('.problem').count()==10)
        page.locator('[data-note]').first.fill('Моё самостоятельное доказательство: 14 - 6 = 8.')
        page.locator('[data-status]').first.select_option('solved')
        ck('Book state written to localStorage',page.evaluate("!!localStorage.getItem('mathblast_book_progress_v1:MB-W01-L1')"))
        page.reload(wait_until='domcontentloaded',timeout=60000)
        page.wait_for_function('window.__MB_TEST__ && document.querySelector("[data-note]")',timeout=60000)
        ck('Written solution survives real reload',page.locator('[data-note]').first.input_value().startswith('Моё самостоятельное'))
        ck('Solved status survives real reload',page.locator('[data-status]').first.input_value()=='solved')
        ck('Main plan progress survives book reload',page.evaluate("localStorage.getItem('olympiad_math_plan_v2')") == old_value)
        page.locator('[data-hint]').first.click();page.locator('[data-hint]').first.click()
        ck('Both hints reveal progressively',page.locator('[data-hint-panel]').first.locator('p').count()==2)
        page.locator('[data-reveal]').first.click()
        ck('Complete solution reveals',page.locator('[data-solution-panel]').first.is_visible())
        for width in [320,375,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':900})
            for route in ['#theory-03','#practice']:
                page.evaluate('(x)=>location.hash=x',route)
                page.wait_for_timeout(380)
                ck(f'No viewport overflow {width} {route}',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
        page.set_viewport_size({'width':375,'height':800})
        page.locator('#menu-open').click()
        ck('Mobile menu opens and focus enters',page.evaluate("document.querySelector('#sidebar').classList.contains('open') && document.activeElement.closest('#sidebar')!==null"))
        page.keyboard.press('Escape')
        ck('Mobile Escape closes and restores focus',page.evaluate("!document.querySelector('#sidebar').classList.contains('open') && document.activeElement.id==='menu-open'"))
        page.set_viewport_size({'width':1440,'height':900})
        page.evaluate('location.hash="#theory-03"');page.wait_for_timeout(600)
        ck('Section transition moves focus to reading',page.evaluate("document.activeElement.id==='reading'"))
        page.evaluate('location.hash="#sources"');page.wait_for_timeout(600)
        ck('All six bibliography entries rendered',page.locator('.source').count()==6)
        ck('No JavaScript exceptions',not errors,errors[:5])
        page.screenshot(path=str(QA/'desktop.png'),full_page=False)
        # Legacy main plan must still export and import the same completed lesson IDs.
        plan=context.new_page()
        plan.on('dialog',lambda dialog:dialog.accept())
        plan_response=plan.goto(BASE+'/index.html',wait_until='domcontentloaded',timeout=60000)
        ck('Main plan HTTP 200',plan_response is not None and plan_response.status==200)
        plan.evaluate("""()=>localStorage.setItem('olympiad_math_plan_v2',JSON.stringify({done:{1:true,144:true},ratings:{0:4},theme:'dark'}))""")
        plan.reload(wait_until='domcontentloaded',timeout=60000)
        ck('Main plan restores both marked lessons',plan.evaluate("Object.keys(JSON.parse(localStorage.getItem('olympiad_math_plan_v2')).done).length===2"))
        with plan.expect_download() as download_info:
            plan.locator('#export-button').click()
        downloaded=download_info.value
        export_path=QA/'legacy-progress-export.json'
        downloaded.save_as(str(export_path))
        exported=json.loads(export_path.read_text())
        ck('Legacy progress export preserves lesson 1 and 144',exported.get('completedLessons')==[1,144])
        ck('Legacy competency export preserves ratings',4 in exported.get('competencies',{}).values())
        plan.evaluate("""()=>localStorage.setItem('olympiad_math_plan_v2',JSON.stringify({done:{},ratings:{},theme:'light'}))""")
        plan.reload(wait_until='domcontentloaded',timeout=60000)
        plan.locator('#import-file').set_input_files(str(export_path))
        plan.wait_for_timeout(350)
        recovered=plan.evaluate("JSON.parse(localStorage.getItem('olympiad_math_plan_v2'))")
        ck('Legacy import restores both lesson flags',bool(recovered['done'].get('1') and recovered['done'].get('144')))
        ck('Legacy import restores competency 0',recovered['ratings'].get('0')==4)
        ck('Book progress unaffected by main plan import',page.evaluate("!!localStorage.getItem('mathblast_book_progress_v1:MB-W01-L1')"))
        plan.close()
        # Axe is installed by CI: npm install --no-save axe-core
        axe=ROOT/'node_modules/axe-core/axe.min.js'
        if axe.exists():
            page.add_script_tag(path=str(axe))
            audit=page.evaluate("""async()=>{let x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {violations:x.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,selectors:v.nodes.slice(0,8).map(n=>n.target)})),passes:x.passes.length}}""")
            (QA/'axe.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
            ck('Automated axe-core WCAG A/AA',len(audit['violations'])==0,audit['violations'][:6])
        else:
            ck('axe-core test installed',False,'Missing node_modules/axe-core')
        # Real HTTP + original SVG URLs, no data-URI substitution.
        page.evaluate("""()=>{
            const node=document.querySelector('#print-book-content');
            node.innerHTML=window.__MB_TEST__.printFullHTML();
            node.setAttribute('aria-hidden','false');
        }""")
        page.wait_for_function("document.querySelectorAll('#print-book-content img').length===22",timeout=20000)
        page.evaluate("""async()=>{
            const node=document.querySelector('#print-book-content');
            await Promise.all(Array.from(node.querySelectorAll('img')).map(img=>img.decode()));
            await MathJax.typesetPromise([node]);
            await document.fonts.ready;
        }""")
        svg_count=page.evaluate("Array.from(document.querySelectorAll('#print-book-content img')).filter(x=>x.naturalWidth>0).length")
        ck('All 22 SVG actually loaded by HTTP',svg_count==22,svg_count)
        ck('No raw MathJax delimiters in print',page.locator('#print-book-content').locator('mjx-container').count()>20)
        page.emulate_media(media='print')
        page.pdf(path=str(QA/'web-book-print.pdf'),format='A4',print_background=True,prefer_css_page_size=True)
        pdf=fitz.open(QA/'web-book-print.pdf')
        text='\n'.join(x.get_text() for x in pdf)
        ck('Printable PDF has at least 100 A4 pages',len(pdf)>=100 and all(abs(pg.rect.width-595.28)<1 for pg in pdf),len(pdf))
        ck('Printed PDF contains all 90 task IDs',all(x['id'] in text for x in SRC['practice']))
        ck('Printed PDF contains all 30 example IDs',all(x['id'] in text for x in SRC['examples']))
        ck('Printed PDF contains all 59 reflection IDs',all(x['id'] in text for group in SRC['reflections'].values() for x in group))
        ck('No empty print pages',all(len(pg.get_text().strip())>120 for pg in pdf))
        browser.close()
finally:
    server.terminate()
    try:server.wait(timeout=6)
    except subprocess.TimeoutExpired:server.kill()
    log.close()

result={'passed':sum(CHECKS.values()),'total':len(CHECKS),'failed':ISSUES,'checks':CHECKS,'browser_errors':errors,
        'hosting':'Real HTTP on GitHub Actions ephemeral localhost, not published GitHub Pages',
        'print_pdf_pages':len(fitz.open(QA/'web-book-print.pdf')) if (QA/'web-book-print.pdf').exists() else None}
(QA/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('FINAL',result['passed'],'/',result['total'],flush=True)
sys.exit(1 if ISSUES else 0)
