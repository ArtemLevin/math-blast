'use strict';
// PHY-KIN-01: structural and simulated-DOM regression; no browser claim.
const fs=require('node:fs');
const path=require('node:path');
function run(html,raw,main){
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const data=JSON.parse(raw),primary=JSON.parse(main),ts=data.tasks;
 const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const embedded=(name)=>{const line=html.split("\n").find(x=>x.startsWith("const "+name+"="));assert(line&&line.endsWith(";"),name+" declaration");return JSON.parse(line.slice(("const "+name+"=").length,-1))};
 assert(eq(embedded("SUPPLEMENT"),data),"supplement parity");assert(eq(embedded("DATA"),primary),"main parity");
 const expected=[...Array.from({length:10},(_,i)=>"MB-07-W-"+String(i+1).padStart(2,"0")),...Array.from({length:14},(_,i)=>"MB-07-P-"+String(i+1).padStart(2,"0"))];
 assert(data.schema_version==="2.0"&&eq(ts.map(t=>t.id),expected),"schema/IDs");
 assert(new Set([...primary.tasks,...ts].map(t=>t.id)).size===69,"chapter IDs");
 const totals={tasks:0,hints:0,steps:0,formulaRecords:0,renderedCards:0,hintClicks:0,solutionToggles:0,rubricChecks:0,progressToggles:0};
 for(const t of ts){
  assert(t.hints.length===3&&new Set(t.hints).size===3&&t.hints.every(Boolean),t.id+" hints");
  assert(t.solution_steps.length===3&&t.solution_steps.every(s=>s.title&&s.explanation&&s.math.length),t.id+" steps");
  assert(t.answer&&t.answer_spec.kind==="manual"&&t.answer_spec.parts.every(x=>x.label&&x.expected),t.id+" answer");
  assert(t.rubric.length===3&&t.rubric.every(x=>x.criterion&&x.points===1),t.id+" rubric");
  assert(t.prerequisites.length&&t.competency_ids.includes(t.primary_competency)&&t.competency_ids.every(x=>/^KIN-(0[1-9]|1[0-2])$/.test(x)),t.id+" competency");
  assert(t.verification==="original_authoring"&&t.answer_source===null&&!t.source_pages.length&&!t.source_images.length,t.id+" provenance");
  assert(t.pedagogical_role===(t.kind==="worked"?"worked_example":"independent_practice"),t.id+" role");
  totals.tasks++;totals.hints+=t.hints.length;totals.steps+=t.solution_steps.length;
 }
 class N {constructor(tag,txt=""){this.tag=tag;this.textContent=txt;this.children=[];this.attrs={};this.hidden=false;this.checked=false;}append(...xs){this.children.push(...xs)}setAttribute(k,v){this.attrs[k]=String(v)}}
 const nodes=new Map();
 const document={createElement:t=>new N(t),createElementNS:(_ns,t)=>new N(t),createTextNode:t=>new N("#text",t),getElementById:id=>{if(!nodes.has(id))nodes.set(id,new N("div"));return nodes.get(id)}};
 const storageKey="math-blast-kasatkina-v1-solved",initial=[primary.tasks.find(t=>t.kind==="practice").id,"MB-07-P-01"],store=new Map([[storageKey,JSON.stringify(initial)],["olympiad_math_plan_v2","preserve"]]);
 const localStorage={getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v)};
 const src=html.match(/<script>'use strict';([\s\S]*?)<\/script>/);assert(src,"inline script");new Function(src[1]); // compile complete script, do not execute labs
 const a=html.indexOf("const $=id=>"),b=html.indexOf("const S='http",a),c=html.indexOf("const key='math-blast-kasatkina-v1-solved'"),d=html.indexOf("document.querySelectorAll('[data-math]')",c);
 assert(a>=0&&b>a&&c>=0&&d>c,"renderer boundaries");
 const render=new Function("document","localStorage","DATA","SUPPLEMENT","legacyTask","circularV2Figure","alternativeBlock",html.slice(a,b)+html.slice(c,d)+"\nreturn {mathNode,task,updateProgress};")(document,localStorage,primary,data,()=>{throw Error("legacy renderer invoked")},()=>{throw Error("unexpected figure")},(_a,t)=>assert(!t.alternative_exercise,"unexpected alternative"));
 const all=n=>[n,...n.children.flatMap(all)];
 const find=(n,f)=>all(n).find(f);
 for(const t of ts){
  for(const f of [...t.formulas,...t.solution_steps.flatMap(s=>s.math)]){assert(render.mathNode(f).tag==="math",t.id+" formula fallback: "+f);totals.formulaRecords++}
  const card=render.task(t);assert(card.id===t.id,t.id+" rendered ID");totals.renderedCards++;
  const hint=find(card,n=>n.tag==="button"&&n.textContent.startsWith("Подсказка"));const list=find(card,n=>n.id==="hints-"+t.id);
  assert(hint&&list&&list.children.length===0,t.id+" initial hints");
  for(let i=1;i<=3;i++){hint.onclick();assert(list.children.length===i,t.id+" hint "+i);totals.hintClicks++}
  assert(hint.disabled,t.id+" final hint state");
  const sol=find(card,n=>n.id==="solution-"+t.id),toggle=find(card,n=>n.tag==="button"&&n.textContent==="Показать решение");
  assert(sol.hidden&&toggle.attrs["aria-expanded"]==="false",t.id+" initial solution");
  toggle.onclick();assert(!sol.hidden&&toggle.attrs["aria-expanded"]==="true",t.id+" open");toggle.onclick();assert(sol.hidden&&toggle.attrs["aria-expanded"]==="false",t.id+" close");totals.solutionToggles+=2;
  const checks=all(sol).filter(n=>n.tag==="input"&&n.type==="checkbox"),score=find(sol,n=>n.attrs.role==="status");assert(checks.length===3&&score.textContent==="0 из 3 баллов",t.id+" rubric state");
  checks.forEach((n,i)=>{n.checked=true;n.onchange();assert(score.textContent===(i+1)+" из 3 баллов",t.id+" rubric +");totals.rubricChecks++});
  checks[0].checked=false;checks[0].onchange();assert(score.textContent==="2 из 3 баллов",t.id+" rubric -");totals.rubricChecks++;
  assert(all(card).some(n=>n.textContent.includes("Math Blast · авторская тренировочная задача")),t.id+" attribution");
  if(t.kind==="practice"){
   const mark=find(card,n=>n.tag==="button"&&(n.textContent.includes("решённой")||n.textContent.includes("Решена")));
   assert(mark,t.id+" mark");const prior=JSON.parse(store.get(storageKey));mark.onclick();const after=JSON.parse(store.get(storageKey));assert(after.includes(t.id)!==prior.includes(t.id),t.id+" toggle");assert(after.includes(initial[0]),t.id+" main progress");mark.onclick();assert(eq(JSON.parse(store.get(storageKey)).slice().sort(),prior.slice().sort()),t.id+" restore");totals.progressToggles+=2;
  }
 }
 assert(store.get("olympiad_math_plan_v2")==="preserve","unrelated progress");
 render.updateProgress();assert(nodes.get("suppBar").value===1&&nodes.get("practiceBar").value===1,"separate counters");
 return totals;
}
const dir=path.resolve(__dirname,'..');
const read=name=>fs.readFileSync(path.join(dir,name),'utf8');
console.log(JSON.stringify(run(read('chapter-07.html'),read('chapter-07-supplement.json'),read('chapter-07.json')),null,2));
