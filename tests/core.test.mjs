import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {tail,cumulative,exportRows,csv} from '../core.mjs';
const report=JSON.parse(fs.readFileSync(new URL('../reports/results.json',import.meta.url)));
test('fractional tail mass',()=>{assert.ok(Math.abs(tail([...Array(28).keys()])-(27+26+.8*25)/2.8)<1e-10);});
test('negative tail and invalid values',()=>{assert.equal(tail([-3,-3]),-3);assert.throws(()=>tail([]));assert.throws(()=>tail([NaN]));assert.throws(()=>tail([1],1));});
test('running sums preserve adverse days',()=>{assert.deepEqual(cumulative([20,-30,40]),[20,-10,30]);});
test('all downloadable schedules reconcile',()=>{for(const d of report.days)for(const k of Object.keys(d.policies)){const rows=exportRows(d,k);assert.equal(rows.length,96);assert.ok(Math.abs(rows.reduce((s,r)=>s+r.quantity_mwh,0)-4)<1e-6);assert.ok(Math.abs(rows.reduce((s,r)=>s+r.total_cost_eur,0)-d.policies[k].actual_cost)<1e-6);}});
test('CSV quotes special characters',()=>{assert.equal(csv([{name:'a,"b"',n:2}]),'"name","n"\r\n"a,""b""","2"');});
test('constrained-day shortcut has an eligible target',()=>{assert.ok(report.days.some(d=>d.area==='DK2'&&d.policies.mean.cvar>25));});
