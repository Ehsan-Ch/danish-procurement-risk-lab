import copy,csv,gzip,hashlib,json,tempfile,unittest
from pathlib import Path
import numpy as np
from harbor.source import load,parse,slots
from harbor.scenarios import build,available
from harbor.risk import evaluate,tail,validate_quantity,solve

ROOT=Path(__file__).resolve().parents[1]
class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history=load(ROOT/'data/forecasts.csv.gz');cls.report=json.loads((ROOT/'reports/results.json').read_text())
    def test_source_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'bad';p.write_bytes(b'broken')
            with self.assertRaises(ValueError):load(p)
    def test_complete_period(self):
        self.assertEqual(len(self.report['days']),122)
        self.assertEqual(min(d['day'] for d in self.report['days']),'2026-08-01')
        self.assertEqual(max(d['day'] for d in self.report['days']),'2026-09-30')
    def test_information_boundary(self):
        for d in self.report['days']:
            self.assertEqual(len(d['lineage']),28)
            self.assertTrue(all(parse(s['available'])<=parse(d['issue']) for s in d['lineage']))
        first=self.report['days'][0]
        self.assertEqual(first['lineage'][-1]['day'],'2026-07-29')
    def test_future_actuals_do_not_change_scenarios_or_decision(self):
        target=next(d for d in self.history if d['day']=='2026-08-15')
        S,_=build(target,self.history);changed=copy.deepcopy(self.history)
        for d in changed:
            if available(d)>parse(target['issue']):d['actual']=[999999]*96
        altered=copy.deepcopy(target);altered['actual']=[-9999]*96
        T,_=build(altered,changed);np.testing.assert_array_equal(S,T)
        np.testing.assert_allclose(solve(S,25)['quantity'],solve(T,25)['quantity'])
    def test_residual_vectors_preserved(self):
        target=next(d for d in self.history if d['day']=='2026-08-01')
        S,lineage=build(target,self.history)
        for row,ref in zip(S,lineage):
            old=next(d for d in self.history if d['area']==target['area'] and d['day']==ref['day'])
            np.testing.assert_allclose(row,np.array(target['selected'])+np.array(old['actual'])-np.array(old['selected']))
    def test_insufficient_and_incompatible_history(self):
        with self.assertRaises(ValueError):build(self.history[0],self.history)
        target=copy.deepcopy(next(d for d in self.history if d['day']=='2026-08-01'));target['selected']=target['selected'][:-4]
        with self.assertRaisesRegex(ValueError,'Incompatible'):build(target,self.history)
        self.assertEqual(len(slots('2026-03-29')),92)
        self.assertEqual(len(slots('2025-10-26')),100)
    def test_every_quantity_risk_and_cost_reconciles(self):
        for d in self.report['days']:
            for p in d['policies'].values():
                validate_quantity(p['quantity']);risk=tail(p['scenario_excess'])
                self.assertAlmostEqual(risk['cvar'],p['cvar'],places=5)
                if p['budget'] is not None:self.assertLessEqual(p['cvar'],p['budget']+1e-5)
                self.assertAlmostEqual(evaluate(d['actual'],p['quantity']),p['actual_cost'],places=5)
                self.assertAlmostEqual(p['savings'],p['uniform_cost']-p['actual_cost'],places=5)
                self.assertEqual(p['status'],0)
    def test_summary_reconciles(self):
        for a,policies in self.report['summary'].items():
            for key,s in policies.items():
                days=[d['policies'][key] for d in self.report['days'] if d['area']==a]
                self.assertEqual(s['days'],61)
                self.assertAlmostEqual(sum(d['actual_cost'] for d in days),s['cost'])
                self.assertAlmostEqual(tail([d['actual_excess'] for d in days])['cvar'],s['realized_cvar'])
    def test_protocol_fingerprint(self):
        self.assertEqual(self.report['protocol_sha256'],hashlib.sha256((ROOT/'docs/PROTOCOL.md').read_bytes()).hexdigest())
    def test_full_precision_journal(self):
        with gzip.open(ROOT/'reports/intervals.csv.gz','rt') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),122*5*96)
        self.assertEqual(len({(r['area'],r['policy'],r['delivery_utc']) for r in rows}),len(rows))
        for r in rows:self.assertAlmostEqual(float(r['quantity_mwh'])*(float(r['actual_eur_mwh'])+.5),float(r['total_cost_eur']),places=7)

if __name__=='__main__':unittest.main()
