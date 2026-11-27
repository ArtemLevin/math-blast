'use strict';
const {validate,readInputs}=require('./validate-bank.cjs');
// Each fixture changes a real valid input independently and checks a specific diagnostic.
function negativeFixtures(files,schema,options={}){
 const p='materials/physics/kasatkina-vol-1/',bank=p+'chapter-07-supplement.json',html=p+'chapter-07.html',first=p+'chapter-01.json';
 const edit=(files,name,fn)=>{const j=JSON.parse(files[name]);fn(j);files[name]=JSON.stringify(j)};
 const cases=[
 ['missing required field',x=>edit(x,bank,j=>delete j.tasks[0].answer),'required answer'],
 ['invalid schema version',x=>edit(x,bank,j=>j.schema_version='1.0'),'const'],
 ['missing hint',x=>edit(x,bank,j=>j.tasks[0].hints.pop()),'minItems'],
 ['duplicate hints',x=>edit(x,bank,j=>j.tasks[0].hints[1]=j.tasks[0].hints[0]),'uniqueItems'],
 ['duplicate normalized hints',x=>edit(x,bank,j=>j.tasks[0].hints[1]=j.tasks[0].hints[0]+' '),'duplicate normalized hints'],
 ['blank answer',x=>edit(x,bank,j=>j.tasks[0].answer=' '),'pattern'],
 ['unsupported answer kind',x=>edit(x,bank,j=>j.tasks[0].answer_spec.kind='automatic'),'const'],
 ['negative tolerance',x=>edit(x,bank,j=>j.tasks[0].answer_spec.parts[0].tolerance=-1),'minimum'],
 ['zero rubric points',x=>edit(x,bank,j=>j.tasks[0].rubric[0].points=0),'minimum'],
 ['duplicate rubric criterion',x=>edit(x,bank,j=>j.tasks[0].rubric[1].criterion=j.tasks[0].rubric[0].criterion),'duplicate rubric criterion'],
 ['unknown competency',x=>edit(x,bank,j=>j.tasks[0].primary_competency='KIN-99'),'pattern'],
 ['primary absent',x=>edit(x,bank,j=>j.tasks[0].primary_competency='KIN-10'),'primary competency absent'],
 ['duplicate global ID',x=>edit(x,bank,j=>j.tasks.push({...j.tasks[0]})),'duplicate global ID'],
 ['wrong number',x=>edit(x,bank,j=>j.tasks[0].number=99),'ID/chapter/kind/number mismatch'],
 ['wrong scope',x=>edit(x,bank,j=>j.scope.worked++),'scope.worked mismatch'],
 ['deleted task with adjusted scope',x=>edit(x,bank,j=>{j.tasks.shift();j.scope.worked--}),'missing baseline ID MB-07-W-01'],
 ['author source contamination',x=>edit(x,bank,j=>j.tasks[0].source_pages=[1]),'author provenance mismatch'],
 ['unsafe scan reference',x=>edit(x,first,j=>j.tasks[0].source_images=['../bad.jpg']),'unsafe source image reference'],
 ['embedded mismatch',x=>{x[html]=x[html].replace(/^const SUPPLEMENT=.*;$/m,'const SUPPLEMENT={};')},'parity SUPPLEMENT differs'],
 ['missing module',(x,o)=>{delete x[html];o.knownPaths=(o.knownPaths||[]).filter(n=>n!==html)},'missing module'],
 ['broken local link',x=>{x[html]=x[html].replace('href="README.md"','href="missing.md"')},'broken local link'],
 ['broken anchor',x=>{x[html]=x[html].replace('href="#theory"','href="#missing"')},'missing static anchor'],
 ['unsafe URL',x=>{x[html]=x[html].replace('href="README.md"','href="javascript:alert(1)"')},'unsupported URL'],
 ['invalid JSON',x=>{x[bank]='{'},'invalid JSON']
 ];
 if(!options.partial)cases.push(['missing existing chapter',x=>delete x[first],'missing existing chapter']);
 const baseline=validate(files,schema,options);
 if(baseline.status!=='PASS')throw Error('Baseline invalid: '+JSON.stringify(baseline.errors));
 return cases.map(([name,mutate,expect])=>{const copy={...files},opts={...options};mutate(copy,opts);const result=validate(copy,schema,opts);const ok=result.status==='FAIL'&&result.errors.some(s=>s.includes(expect));return {name,ok,expected:expect,...(!ok?{errors:result.errors.slice(0,8)}:{})}});
}
if(require.main===module){
 const {files,schema,options}=readInputs();const results=negativeFixtures(files,schema,options);
 console.log(JSON.stringify({total:results.length,passed:results.filter(x=>x.ok).length,results},null,2));
 if(results.some(x=>!x.ok))process.exitCode=1;
}
module.exports={negativeFixtures};
