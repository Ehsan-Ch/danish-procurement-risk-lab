import csv,gzip,hashlib,io,json,platform
from pathlib import Path
import numpy as np
import scipy
from .source import load,SHA256,URL,SELECTED
from .scenarios import build
from .risk import BUDGETS,solve,evaluate,tail,FEE,ENERGY

def run(root,out=None):
    root=Path(root);out=Path(out) if out else root/'reports';out.mkdir(parents=True,exist_ok=True)
    history=load(root/'data/forecasts.csv.gz');days=[];daily=[];journal=[]
    for target in history:
        if target['day']<'2026-08-01': continue
        S,lineage=build(target,history)
        d={k:target[k] for k in ('area','day','issue','utc','local','actual','selected')}
        d['lineage']=lineage;d['scenario_mean']=S.mean(axis=0).tolist();d['policies']={}
        base=np.full(len(target['actual']),ENERGY/len(target['actual']));basecost=evaluate(target['actual'],base)
        for key,budget in BUDGETS.items():
            s=solve(S,budget,uniform=key=='uniform');q=s['quantity'];cost=evaluate(target['actual'],q)
            p={**s,'quantity':q.tolist(),'scenario_excess':s['scenario_excess'].tolist(),'budget':budget,
               'actual_cost':cost,'uniform_cost':basecost,'actual_excess':cost-basecost,'savings':basecost-cost}
            d['policies'][key]=p
            daily.append({'area':d['area'],'day':d['day'],'policy':key,'budget':budget,
                          **{k:p[k] for k in ('expected_cost','var','cvar','actual_cost','uniform_cost','actual_excess','savings','status')}})
            for t in range(len(q)):
                journal.append({'area':d['area'],'day':d['day'],'policy':key,'issue_utc':d['issue'],
                                'delivery_utc':d['utc'][t],'delivery_local':d['local'][t],'quantity_mwh':q[t],
                                'actual_eur_mwh':d['actual'][t],'energy_cost_eur':q[t]*d['actual'][t],
                                'fee_eur':q[t]*FEE,'total_cost_eur':q[t]*(d['actual'][t]+FEE)})
        days.append(d)
        if len(days)%20==0: print(f'Replayed {len(days)}/122 area-days',flush=True)
    summary={}
    for area in SELECTED:
        summary[area]={}
        for key,budget in BUDGETS.items():
            rows=[r for r in daily if r['area']==area and r['policy']==key];excess=[r['actual_excess'] for r in rows]
            summary[area][key]={'days':len(rows),'cost':sum(r['actual_cost'] for r in rows),'savings':sum(r['savings'] for r in rows),
                'worst_excess':max(excess),'realized_cvar':tail(excess)['cvar'],
                'days_more_expensive':sum(v>1e-6 for v in excess),
                'above_budget':None if budget is None else sum(v>budget+1e-6 for v in excess),
                'above_var':sum(r['actual_excess']>r['var']+1e-6 for r in rows),
                'mean_planned_cvar':sum(r['cvar'] for r in rows)/len(rows)}
    report={'title':'Harbor','source':{'url':URL,'sha256':SHA256},'selected_models':SELECTED,
            'protocol_sha256':hashlib.sha256((root/'docs/PROTOCOL.md').read_bytes()).hexdigest(),
            'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'summary':summary,'days':days}
    (out/'results.json').write_text(json.dumps(report,separators=(',',':'),allow_nan=False),encoding='utf-8')
    for name,rows in [('daily.csv',daily),('intervals.csv.gz',journal)]:
        buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
        data=buf.getvalue().encode();(out/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
    print(json.dumps(summary,indent=2));return report
