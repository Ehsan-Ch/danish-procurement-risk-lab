import {labels,cumulative,exportRows,csv} from './core.mjs';
const $=id=>document.getElementById(id),fmt=(n,d=0)=>new Intl.NumberFormat('en-GB',{minimumFractionDigits:d,maximumFractionDigits:d}).format(Math.abs(n)<.5*10**(-d)?0:n),eur=n=>`${n<-.5?'−':''}€${fmt(Math.abs(n))}`;
let report,day;
function chart(id,series,{min,max,ticks=[],bars=false}={}){
  const el=$(id),[,,W,H]=el.getAttribute('viewBox').split(' ').map(Number),l=45,r=20,t=18,b=30,w=W-l-r,h=H-t-b;
  const vals=series.flatMap(s=>s.values),n=Math.max(...series.map(s=>s.values.length));
  min=min??Math.min(0,...vals);max=max??Math.max(0,...vals);if(max-min<1e-9)max=min+1;
  const x=i=>l+i*w/(n-1||1),y=v=>t+(max-v)*h/(max-min);let html='';
  for(let i=0;i<5;i++){const v=min+(max-min)*i/4;html+=`<line x1="${l}" x2="${W-r}" y1="${y(v)}" y2="${y(v)}" stroke="#dce5eb"/><text x="${l-8}" y="${y(v)+4}" fill="#6c7e8c" font-size="10" text-anchor="end">${fmt(v,max-min<5?1:0)}</text>`;}
  for(const s of series){if(bars&&s.bars){const width=w/n;html+=s.values.map((v,i)=>`<rect x="${l+i*width}" y="${Math.min(y(0),y(v))}" width="${Math.max(.5,width-1)}" height="${Math.abs(y(v)-y(0))}" fill="${s.color}"/>`).join('');}
    else html+=`<polyline points="${s.values.map((v,i)=>`${x(i)},${y(v)}`).join(' ')}" fill="none" stroke="${s.color}" stroke-width="2.5" ${s.dash?'stroke-dasharray="5 4"':''}/>`;}
  for(const k of ticks)html+=`<text x="${x(k.i)}" y="${H-6}" text-anchor="middle" fill="#6c7e8c" font-size="10">${k.label}</text>`;
  el.innerHTML=html;
}
function distribution(p){
  const v=[...p.scenario_excess].sort((a,b)=>a-b),low=Math.min(...v,p.actual_excess,p.cvar,0),high=Math.max(...v,p.actual_excess,p.cvar,0),pad=Math.max(10,(high-low)*.12),min=low-pad,max=high+pad,x=n=>50+(n-min)/(max-min)*590;
  let html='';for(let i=0;i<5;i++){const val=min+(max-min)*i/4;html+=`<line x1="${x(val)}" x2="${x(val)}" y1="20" y2="215" stroke="#e4ebef"/><text x="${x(val)}" y="245" text-anchor="middle" font-size="11" fill="#6c7e8c">${fmt(val)}</text>`;}
  html+=`<line x1="${x(0)}" x2="${x(0)}" y1="20" y2="215" stroke="#a5b5c2" stroke-dasharray="4 4"/>`;
  html+=v.map((val,i)=>`<circle cx="${x(val)}" cy="${60+(i%4)*12}" r="4.5" fill="${i>=25?'#bd7b31':'#54799c'}"><title>Scenario excess cost €${fmt(val,2)}</title></circle>`).join('');
  html+=`<path d="M${x(p.cvar)} 135v28" stroke="#bd7b31" stroke-width="3"/><text x="${x(p.cvar)}" y="181" font-size="12" text-anchor="middle" fill="#946022">CVaR90</text>`;
  html+=`<circle cx="${x(p.actual_excess)}" cy="202" r="6" fill="#238783"/><text x="${x(p.actual_excess)}" y="222" font-size="12" text-anchor="middle" fill="#238783">Actual</text>`;
  $('distribution').innerHTML=html;
}
function render(){
  const area=$('area').value,key=$('policy').value,days=report.days.filter(d=>d.area===area);day=days.find(d=>d.day===$('day').value)||days[0];
  const p=day.policies[key],s=report.summary[area][key],mean=report.summary[area].mean;
  $('context').textContent=`Decision: ${day.issue.slice(0,10)} at 10:00 Europe/Copenhagen · ${report.selected_models[area]} forecast + 28 eligible whole-day error paths · Prices in EUR/MWh`;
  $('cost').textContent=eur(s.cost);$('savings').textContent=eur(s.savings);$('premium').textContent=eur(s.cost-mean.cost);$('exceed').textContent=`${s.above_var} / 61`;
  const affected=days.filter(d=>d.policies.mean.cvar>1e-5).length;
  $('finding').textContent=area==='DK1'?'In DK1, even the €0 tail budget leaves every mean-cost schedule unchanged in this sample. The risk constraint adds no protection here. Estimated tail risk is not a guarantee about future outcomes.':`In DK2, the mean-only schedule exceeds the €0 scenario tail budget on ${affected} of 61 days. Tightening that limit increases total observed procurement cost by ${eur(report.summary[area].risk0.cost-mean.cost)}. We report the trade-off without selecting a winner after seeing outcomes.`;
  const ticks=[0,24,48,72,95].map(i=>({i,label:day.local[i].slice(11,16)}));
  chart('prices',[{values:day.actual,color:'#284f81'},{values:day.scenario_mean,color:'#238783',dash:true}],{ticks});
  chart('load',[{values:p.quantity.map(v=>v*4),color:'#284f81',bars:true},{values:day.utc.map(()=>4/24),color:'#a8b5bf',dash:true}],{min:0,max:1,ticks,bars:true});
  distribution(p);
  $('risk-readout').innerHTML=[['Tail budget',p.budget===null?'None':eur(p.budget)],['Planned CVaR90',eur(p.cvar)],['Actual excess cost',eur(p.actual_excess)]].map(([k,v])=>`<div><span>${k}</span><strong>${v}</strong></div>`).join('');
  $('policies').innerHTML=Object.entries(labels).map(([k,label])=>{const r=day.policies[k];return `<tr class="${key===k?'selected':''}"><td>${label}</td><td>${eur(r.expected_cost)}</td><td>${eur(r.cvar)}</td><td>${eur(r.actual_cost)}</td></tr>`;}).join('');
  chart('savings-chart',[{values:[0,...cumulative(days.map(d=>d.policies.mean.savings))],color:'#238783',dash:true},{values:[0,...cumulative(days.map(d=>d.policies[key].savings))],color:'#284f81'}],{ticks:[{i:0,label:'1 Aug'},{i:31,label:'1 Sep'},{i:61,label:'30 Sep'}]});
  $('summary').innerHTML=Object.entries(labels).map(([k,label])=>{const r=report.summary[area][k];return `<tr class="${key===k?'selected':''}"><td>${label}</td><td>${eur(r.cost)}</td><td>${eur(r.savings)}</td><td>${eur(r.worst_excess)}</td><td>${eur(r.realized_cvar)}</td><td>${r.above_budget===null?'—':r.above_budget+' / 61'}</td></tr>`;}).join('');
  $('audit').textContent=`Cutoff: ${day.issue}. All 28 source days below became eligible before this decision. Each availability time is the source day's delivery end plus 24 hours. Uniform demand remains feasible at every nonnegative budget.`;
  $('lineage').innerHTML=day.lineage.map(r=>`<span>${r.day}<small>Available ${r.available}</small></span>`).join('');
  $('journal').innerHTML=exportRows(day,key).map(r=>`<tr><td>${r.delivery_local.slice(11,16)}</td><td>${fmt(r.quantity_mwh,4)}</td><td>${fmt(r.power_mw,3)}</td><td>${fmt(r.actual_eur_mwh,2)}</td><td>${fmt(r.total_cost_eur,2)}</td></tr>`).join('');
}
async function init(){try{
  const response=await fetch('reports/results.json');if(!response.ok)throw Error(`Report request failed (${response.status})`);report=await response.json();if(report.days.length!==122)throw Error('Incomplete replay');
  $('day').innerHTML=report.days.filter(d=>d.area==='DK1').map(d=>`<option>${d.day}</option>`).join('');
  for(const id of ['area','policy','day'])$(id).addEventListener('change',render);
  $('binding').disabled=false;$('binding').addEventListener('click',()=>{const target=report.days.find(d=>d.area==='DK2'&&d.policies.mean.cvar>25);if(target){$('area').value='DK2';$('day').value=target.day;$('policy').value='risk0';render();}});
  $('download').addEventListener('click',()=>{const key=$('policy').value,url=URL.createObjectURL(new Blob([csv(exportRows(day,key))],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`harbor-${day.area}-${day.day}-${key}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  render();$('loading').hidden=true;$('dashboard').hidden=false;
}catch(e){$('loading').hidden=true;$('error').hidden=false;$('error').textContent=`Could not load the replay. Use the public preview or serve this folder over HTTP. ${e.message}`;}}
init();
