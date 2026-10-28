"""Build causal whole-day forecast-error scenarios."""
from datetime import timedelta
import numpy as np
from .source import parse,stamp

def available(day): return parse(day['utc'][-1])+timedelta(minutes=15,hours=24)

def build(target,history,count=28):
    if not isinstance(count,int) or count<1: raise ValueError('Invalid scenario count')
    cutoff=parse(target['issue'])
    candidates=sorted((d for d in history if d['area']==target['area'] and available(d)<=cutoff),key=lambda d:d['day'])
    if len(candidates)<count: raise ValueError('Insufficient eligible residual history')
    chosen=candidates[-count:]
    if len({d['day'] for d in chosen})!=count: raise ValueError('Duplicate residual day')
    if any(len(d['actual'])!=len(target['selected']) or len(d['selected'])!=len(target['selected']) for d in chosen):
        raise ValueError('Incompatible day lengths; DST alignment is not modeled')
    S=np.asarray(target['selected'])+np.asarray([np.asarray(d['actual'])-np.asarray(d['selected']) for d in chosen])
    if not np.isfinite(S).all(): raise ValueError('Nonfinite scenario')
    return S,[{'day':d['day'],'available':stamp(available(d))} for d in chosen]
