"""Deliberately replace this lab's three cart pods; their in-memory carts are lost."""
import datetime,json,subprocess,time
from pathlib import Path
from verify import obj,k,ready,pod_http

def carts():return [p for p in obj('pods','-l','app=shopping-cart')['items'] if not p['metadata'].get('deletionTimestamp')]
def main():
    d=obj('deployment','shopping-cart')
    assert d['metadata']['labels'].get('devops-lab-exercise')=='10','Refusing unowned deployment'
    strategy=d['spec']['strategy']['rollingUpdate'];assert strategy=={'maxSurge':0,'maxUnavailable':1}
    before=carts();assert len(before)==3 and all(ready(p) for p in before)
    original={p['metadata']['uid'] for p in before};samples=[]
    k('rollout','restart','deployment/shopping-cart')
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        d=obj('deployment','shopping-cart');current=carts()
        samples.append({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'available':d['status'].get('availableReplicas',0),'updated':d['status'].get('updatedReplicas',0),'pods':[{'pod':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec'].get('nodeName'),'ready':ready(p)} for p in current]})
        if len(current)==3 and all(ready(p) for p in current) and not original.intersection(p['metadata']['uid'] for p in current):break
        time.sleep(1)
    else:raise RuntimeError('Rollout timed out')
    after=carts();checks={'all_three_uids_replaced':len(after)==3 and not original.intersection(p['metadata']['uid'] for p in after),'three_distinct_nodes':len(set(p['spec']['nodeName'] for p in after))==3,'at_least_two_available_each_sample':all(s['available']>=2 for s in samples),'new_carts_empty':all(pod_http(p['metadata']['name'],'cart')=={'status':200,'body':[]} for p in after)}
    report={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'strategy':strategy,'before':[{'pod':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec']['nodeName']} for p in before],'samples':samples,'checks':checks,'all_passed':all(checks.values()),'note':'Intentional rolling replacement of only Exercise 10 cart pods; old per-pod cart data discarded. Availability is sampled, not a continuous no-downtime guarantee.'}
    (Path(__file__).parent/'evidence/rollout.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0 if report['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
