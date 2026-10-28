export const labels={risk0:'€0 tail budget',risk25:'€25 tail budget',risk100:'€100 tail budget',mean:'Mean cost only',uniform:'Uniform demand'};
export function tail(values,alpha=.9){
  if(!values.length||values.some(v=>!Number.isFinite(v))||!Number.isFinite(alpha)||alpha<0||alpha>=1)throw Error('Invalid tail inputs');
  const v=[...values].sort((a,b)=>b-a),mass=v.length*(1-alpha);
  return v.reduce((s,x,i)=>s+x*Math.max(0,Math.min(1,mass-i)),0)/mass;
}
export function cumulative(values){let n=0;return values.map(x=>n+=x);}
export function exportRows(day,key){const p=day.policies[key];return day.utc.map((utc,i)=>({area:day.area,day:day.day,policy:key,issue_utc:day.issue,delivery_utc:utc,delivery_local:day.local[i],quantity_mwh:p.quantity[i],power_mw:p.quantity[i]*4,actual_eur_mwh:day.actual[i],total_cost_eur:p.quantity[i]*(day.actual[i]+.5)}));}
export function csv(rows){if(!rows.length)return '';const keys=Object.keys(rows[0]),quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';return [keys.map(quote).join(','),...rows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\r\n');}
