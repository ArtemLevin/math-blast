'use strict';
// Deliberately dependency-free implementation of the JSON Schema subset used by this project.
// Unknown assertion keywords fail explicitly; this is not a general-purpose Draft 2020-12 engine.
const fs=require('node:fs'),path=require('node:path');
const PREFIX='materials/physics/kasatkina-vol-1/';
const pad=n=>String(n).padStart(2,'0');
function canonical(v){if(Array.isArray(v))return v.map(canonical);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])]));return v}
function equal(a,b){return JSON.stringify(canonical(a))===JSON.stringify(canonical(b))}
function schemaErrors(value,rule,where='$'){
 const out=[],bad=c=>out.push(where+' '+c),type=x=>x===null?'null':Array.isArray(x)?'array':typeof x;
 const supported=new Set(['$schema','$id','title','description','type','const','enum','pattern','minimum','maximum','minItems','maxItems','uniqueItems','items','required','properties']);
 for(const k of Object.keys(rule))if(!supported.has(k))bad('unsupported schema keyword '+k);
 if(rule.type){if(![rule.type].flat().some(t=>t==='integer'?Number.isInteger(value):t==='number'?typeof value==='number'&&Number.isFinite(value):type(value)===t)){bad('type');return out}}
 if('const' in rule&&!equal(value,rule.const))bad('const');
 if(rule.enum&&!rule.enum.some(v=>equal(v,value)))bad('enum');
 if(typeof value==='string'&&rule.pattern&&!new RegExp(rule.pattern).test(value))bad('pattern');
 if(typeof value==='number'){if(rule.minimum!==undefined&&value<rule.minimum)bad('minimum');if(rule.maximum!==undefined&&value>rule.maximum)bad('maximum')}
 if(Array.isArray(value)){
  if(rule.minItems!==undefined&&value.length<rule.minItems)bad('minItems');if(rule.maxItems!==undefined&&value.length>rule.maxItems)bad('maxItems');
  if(rule.uniqueItems&&new Set(value.map(v=>JSON.stringify(canonical(v)))).size!==value.length)bad('uniqueItems');
  if(rule.items)value.forEach((v,i)=>out.push(...schemaErrors(v,rule.items,where+'['+i+']')));
 }
 if(type(value)==='object'){for(const k of rule.required||[])if(!Object.hasOwn(value,k))bad('required '+k);for(const [k,s] of Object.entries(rule.properties||{}))if(Object.hasOwn(value,k))out.push(...schemaErrors(value[k],s,where+'.'+k))}
 return out;
}
function validate(files,schema,options={}){
 const errors=[],warnings=[],stats={banks:0,chapters:0,tasks:0,worked:0,practice:0,main:0,author:0,hints:0,steps:0,rubrics:0,rubricPoints:0,alternatives:0,parity:0,links:0,externalLinks:0,sourceImageRefs:0,formulaRecords:0};
 const add=(file,msg)=>errors.push(file+': '+msg),ids=new Set();
 const known=new Set([...Object.keys(files),...(options.knownPaths||[])]);
 const bankNames=Object.keys(files).filter(n=>/^materials\/physics\/kasatkina-vol-1\/chapter-\d{2}(-supplement)?\.json$/.test(n)).sort();
 const htmlNames=Object.keys(files).filter(n=>/^materials\/physics\/kasatkina-vol-1\/(index|chapter-\d{2})\.html$/.test(n)).sort();
 const norm=p=>{const a=[];for(const seg of p.split('/')){if(seg==='..'){if(!a.length)return null;a.pop()}else if(seg&&seg!=='.')a.push(seg)}return a.join('/')};
 function parse(file){try{return JSON.parse(files[file])}catch(e){add(file,'invalid JSON: '+e.message);return null}}
 function parity(bank,data){
  const suffix=bank.match(/chapter-(\d{2})(-supplement)?\.json$/),html=PREFIX+'chapter-'+suffix[1]+'.html',name=suffix[2]?'SUPPLEMENT':'DATA';
  if(!Object.hasOwn(files,html)){if(!options.partial||!known.has(html))add(bank,'missing module '+html);return}
  const lines=files[html].split(/\r?\n/).filter(x=>x.startsWith('const '+name+'='));
  if(lines.length!==1||!lines[0].endsWith(';')){add(html,'expected one JSON declaration '+name);return}
  try{const embedded=JSON.parse(lines[0].slice(('const '+name+'=').length,-1));if(!equal(embedded,data))add(html,'parity '+name+' differs from '+bank);else stats.parity++}catch(e){add(html,'invalid embedded JSON '+name)}
 }
 if(!bankNames.length&&!options.partial)add(PREFIX,'no banks');
 if(!options.partial){
  if(!Object.hasOwn(files,PREFIX+'index.html'))add(PREFIX,'missing navigator');
  for(let i=1;i<=8;i++)if(!bankNames.includes(PREFIX+'chapter-'+pad(i)+'.json'))add(PREFIX,'missing existing chapter '+pad(i));
  if(!bankNames.includes(PREFIX+'chapter-07-supplement.json'))add(PREFIX,'missing MB-07 bank');
 }
 for(const bank of bankNames){
  const j=parse(bank);if(!j)continue;stats.banks++;
  const se=schemaErrors(j,schema);if(se.length){se.forEach(s=>add(bank,s));continue}
  const m=bank.match(/chapter-(\d{2})(-supplement)?\.json$/),chapter=Number(m[1]),author=Boolean(m[2]);if(!author)stats.chapters++;
  if(j.chapter.number!==chapter)add(bank,'chapter number differs from filename');
  if(author&&(chapter!==7||j.source.type!=='original_exercises'))add(bank,'invalid author source metadata');
  if(j.chapter.printed_pages&&j.chapter.printed_pages[0]>j.chapter.printed_pages[1])add(bank,'printed page range reversed');
  const counts={worked:0,practice:0};
  for(const t of j.tasks){
   const id=t.id,kind=t.kind==='worked'?'W':'P';counts[t.kind]++;stats.tasks++;stats[t.kind]++;stats[author?'author':'main']++;
   if(ids.has(id))add(bank,'duplicate global ID '+id);ids.add(id);
   if(t.chapter!==chapter||id!==[author?'MB':'KAS1',pad(chapter),kind,pad(t.number)].join('-'))add(bank,'ID/chapter/kind/number mismatch '+id);
   if(!t.competency_ids.includes(t.primary_competency))add(bank,'primary competency absent '+id);
   if(new Set(t.hints.map(x=>x.trim())).size!==3)add(bank,'duplicate normalized hints '+id);
   if(new Set(t.rubric.map(x=>x.criterion.trim())).size!==t.rubric.length)add(bank,'duplicate rubric criterion '+id);
   if(author&&(t.verification!=='original_authoring'||t.answer_source!==null||t.source_pages.length||t.source_images.length))add(bank,'author provenance mismatch '+id);
   if(!author&&(!t.source_pages.length||!t.source_images.length||t.verification==='original_authoring'))add(bank,'missing/inconsistent source references '+id);
   for(const image of t.source_images){stats.sourceImageRefs++;if(!/^[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+\.(jpg|jpeg|png)$/i.test(image)||image.split('/').includes('..'))add(bank,'unsafe source image reference '+id+' '+image)}
   if(!t.formulas.length&&t.task_type!=='graph_reading'&&t.task_type!=='concept')warnings.push(bank+': no formula list '+id);
   stats.hints+=t.hints.length;stats.steps+=t.solution_steps.length;stats.rubrics+=t.rubric.length;stats.rubricPoints+=t.rubric.reduce((a,r)=>a+r.points,0);stats.formulaRecords+=t.formulas.length+t.solution_steps.reduce((n,s)=>n+s.math.length,0);if(t.alternative_exercise)stats.alternatives++;
  }
  for(const kind of ['worked','practice'])if(counts[kind]!==j.scope[kind])add(bank,'scope.'+kind+' mismatch');
  parity(bank,j);
 }
 for(const html of htmlNames)if(html!==PREFIX+'index.html'&&!known.has(html.replace(/\.html$/,'.json')))add(html,'orphan chapter module');
 const docs=[...htmlNames,...['README.md','ROADMAP.md','AGENTS.md','methodological-standard-v2.md','methodological-review-kinematics.md'].map(n=>PREFIX+n).filter(n=>Object.hasOwn(files,n))];
 for(const file of docs){
  const content=files[file],html=file.endsWith('.html'),markup=html?content.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,''):content;
  const refs=html?[...markup.matchAll(/\b(?:href|src)\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1]):[...markup.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)].map(m=>m[1]);
  for(const ref of refs){
   if(/^https?:\/\//i.test(ref)||/^mailto:/i.test(ref)){stats.externalLinks++;continue}
   if(/^[a-z][a-z0-9+.-]*:/i.test(ref)||ref.startsWith('//')){add(file,'unsupported URL '+ref);continue}
   const [pathHash,hash]=ref.split('#',2),p=pathHash.split('?')[0];const target=p?norm(file.slice(0,file.lastIndexOf('/')+1)+p):file;stats.links++;
   if(!target||!known.has(target)){add(file,'broken local link '+ref);continue}
   if(hash&&target.endsWith('.html')){
    if(target===PREFIX+'index.html'&&(hash==='all'||(/^chapter-\d{2}$/.test(hash)&&known.has(PREFIX+hash+'.json'))))continue;
    if(!Object.hasOwn(files,target)){if(!options.partial)add(file,'anchor target not loaded '+ref);continue}
    const targetMarkup=files[target].replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'');
    const anchors=[...targetMarkup.matchAll(/\bid\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1]);
    if(!anchors.includes(hash))add(file,'missing static anchor '+ref);
   }
  }
 }
 return {status:errors.length?'FAIL':'PASS',mode:options.partial?'partial':'full',stats,errors,warnings,limitations:['Structure and consistency only; no physical/mathematical verification, browser tests, external HTTP checks or scan existence/rights.','Static links only; dynamically generated links require browser tests.','Source image paths are provenance references, not published assets.']};
}
function readInputs(){
 const dir=path.resolve(__dirname,'..'),root=path.resolve(dir,'../../..');
 const files={'index.html':fs.readFileSync(path.join(root,'index.html'),'utf8')};
 for(const n of fs.readdirSync(dir)){if(/^(index|chapter-\d{2})\.html$|^chapter-\d{2}(-supplement)?\.json$|^(README|ROADMAP|AGENTS|methodological-standard-v2|methodological-review-kinematics)\.md$/.test(n))files[PREFIX+n]=fs.readFileSync(path.join(dir,n),'utf8')}
 return {files,schema:JSON.parse(fs.readFileSync(path.join(dir,'schema/kinematics-v2.schema.json'),'utf8'))};
}
if(require.main===module){const {files,schema}=readInputs();const report=validate(files,schema);console.log(JSON.stringify(report,null,2));if(report.status!=='PASS')process.exitCode=1}
module.exports={validate,readInputs,schemaErrors};
