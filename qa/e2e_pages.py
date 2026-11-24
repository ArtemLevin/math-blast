#!/usr/bin/env python3
"""Smoke test the *published* GitHub Pages site, not an isolated or ephemeral HTTP server.

PAGES_BASE_URL must be the URL returned by actions/deploy-pages.
The test checks real relative URLs, localStorage reload, MathJax, all SVG and axe WCAG.
"""
from __future__ import annotations
import json, os, pathlib, time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

BASE=os.environ.get('PAGES_BASE_URL','').strip()
if not BASE.startswith('https://'):
    raise SystemExit('PAGES_BASE_URL must be a deployed HTTPS GitHub Pages URL')
BASE=BASE.rstrip('/')+'/'
BOOK=urljoin(BASE,'books/MB-W01-L1/index.html')
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/'pages-results';OUT.mkdir(parents=True,exist_ok=True)
checks={};errors=[]
def ck(name,predicate,detail=''):
    checks[name]=bool(predicate)
    print(('PASS' if predicate else 'FAIL'),name,detail,flush=True)

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':900})
    page.on('pageerror',lambda err: errors.append(str(err)))
    # GitHub Pages can take a short while to propagate after the deploy job.
    home=None
    for attempt in range(12):
        try:
            home=page.goto(BASE,wait_until='domcontentloaded',timeout=30000)
            if home and home.status==200: break
        except Exception:
            pass
        time.sleep(5)
    ck('Published root returns 200',home is not None and home.status==200, BASE)
    ck('Root contains a book link',page.locator('a[href*="books/MB-W01-L1/index.html"]').count()>0)
    response=page.goto(BOOK,wait_until='domcontentloaded',timeout=60000)
    ck('Published book returns 200',response is not None and response.status==200,BOOK)
    page.wait_for_function('window.__MB_TEST__ && document.querySelector(".book-cover")',timeout=60000)
    page.wait_for_timeout(500)
    ck('Published page has MathJax rendered',page.locator('mjx-container').count()>0)
    ck('Book data contains 90 practice problems',page.evaluate('window.__MB_TEST__.BOOK.practice.length')==90)
    page.evaluate('location.hash="#practice"');page.wait_for_timeout(550)
    page.locator('[data-note]').first.fill('Сохранённое решение при выпускном E2E')
    page.locator('[data-status]').first.select_option('solved')
    page.reload(wait_until='domcontentloaded',timeout=60000)
    page.wait_for_function('window.__MB_TEST__ && document.querySelector("[data-note]")',timeout=60000)
    ck('Published localStorage survives reload',page.locator('[data-note]').first.input_value().startswith('Сохранённое решение'))
    ck('Published task status survives reload',page.locator('[data-status]').first.input_value()=='solved')
    for route in ['#theory-01','#methods','#sources']:
        page.evaluate('(r)=>location.hash=r',route);page.wait_for_timeout(750)
    ck('Published page generates no JS errors',len(errors)==0, errors[:5])
    page.add_script_tag(path=str(ROOT/'node_modules/axe-core/axe.min.js'))
    results=page.evaluate('''async()=>{let a=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {violations:a.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.map(n=>n.target).slice(0,8)})),passes:a.passes.length}}''')
    (OUT/'axe-pages.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ck('Published site axe-core WCAG A/AA',not results['violations'],results['violations'][:5])
    # Each original SVG is fetched over the deployed HTTPS origin.
    page.evaluate('''()=>{const node=document.querySelector('#print-book-content');node.innerHTML=window.__MB_TEST__.printFullHTML();node.setAttribute('aria-hidden','false')}''')
    page.evaluate('''async()=>{let node=document.querySelector('#print-book-content');await Promise.all(Array.from(node.querySelectorAll('img')).map(x=>x.decode()));await MathJax.typesetPromise([node])}''')
    count=page.evaluate("Array.from(document.querySelectorAll('#print-book-content img')).filter(x=>x.naturalWidth>0).length")
    ck('Published site loads all 22 SVG over HTTPS',count==22,count)
    page.screenshot(path=str(OUT/'live-book.png'),full_page=False)
    browser.close()

report={'base_url':BASE,'book_url':BOOK,'checked':len(checks),'passed':sum(checks.values()),'checks':checks,'page_errors':errors}
(OUT/'site-e2e.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT',report['passed'],'/',report['checked'])
raise SystemExit(0 if all(checks.values()) else 1)
