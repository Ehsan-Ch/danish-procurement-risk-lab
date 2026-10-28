"""Empirical fractional-tail risk and constrained load scheduling."""
import numpy as np
from scipy.optimize import linprog

ENERGY = 4.0
MAX_QUANTITY = .25
FEE = .5
ALPHA = .9
BUDGETS = {'risk0':0., 'risk25':25., 'risk100':100., 'mean':None, 'uniform':None}

def vector(values):
    v=np.asarray(values,dtype=float)
    if v.ndim!=1 or not len(v) or not np.isfinite(v).all(): raise ValueError('Expected a finite nonempty vector')
    return v

def tail(values,alpha=ALPHA):
    v=np.sort(vector(values))
    if not np.isfinite(alpha) or not 0<=alpha<1: raise ValueError('Invalid tail probability')
    mass=len(v)*(1-alpha); weights=np.clip(mass-np.arange(len(v)),0,1)
    return {'var':float(v[max(0,int(np.ceil(alpha*len(v)))-1)]),
            'cvar':float(np.dot(v[::-1],weights)/mass)}

def validate_quantity(q,energy=ENERGY,maximum=MAX_QUANTITY):
    q=vector(q)
    if q.min() < -1e-7 or q.max()>maximum+1e-7 or abs(q.sum()-energy)>1e-6:
        raise ValueError('Load constraints violated')
    return q

def evaluate(prices,q):
    p=vector(prices);q=validate_quantity(q)
    if len(p)!=len(q): raise ValueError('Price/quantity mismatch')
    return float(p@q+FEE*q.sum())

def solve(scenarios,budget=None,uniform=False):
    S=np.asarray(scenarios,dtype=float)
    if S.ndim!=2 or min(S.shape)<1 or not np.isfinite(S).all(): raise ValueError('Invalid scenarios')
    m,n=S.shape
    if n*MAX_QUANTITY<ENERGY: raise ValueError('Insufficient delivery capacity')
    if budget is not None and (not np.isfinite(budget) or budget<0): raise ValueError('Invalid budget')
    base=np.full(n,ENERGY/n)
    if uniform: q=base; status=0
    else:
        if budget is None:
            objective=S.mean(axis=0); A=None; rhs=None
            bounds=[(0,MAX_QUANTITY)]*n; eq=np.ones((1,n))
        else:
            objective=np.r_[S.mean(axis=0),np.zeros(m+1)]
            A=np.zeros((m+1,n+1+m));rhs=np.r_[S@base,budget]
            A[:m,:n]=S; A[:m,n]=-1; A[:m,n+1:]=-np.eye(m)
            A[m,n]=1; A[m,n+1:]=1/(m*(1-ALPHA))
            bounds=[(0,MAX_QUANTITY)]*n+[(None,None)]+[(0,None)]*m
            eq=np.zeros((1,n+1+m)); eq[0,:n]=1
        result=linprog(objective,A_ub=A,b_ub=rhs,A_eq=eq,b_eq=[ENERGY],bounds=bounds,
                       method='highs',options={'time_limit':20})
        if result.status!=0: raise RuntimeError(f'Optimization failed: {result.status}: {result.message}')
        q=result.x[:n];status=int(result.status)
    validate_quantity(q)
    excess=S@(q-base);risk=tail(excess)
    if budget is not None and risk['cvar']>budget+1e-5: raise RuntimeError('Tail budget failed independent check')
    return {'quantity':q,'scenario_excess':excess,'var':risk['var'],'cvar':risk['cvar'],
            'expected_cost':float(S.mean(axis=0)@q+FEE*ENERGY),'status':status}
