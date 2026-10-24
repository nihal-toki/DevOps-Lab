"""Verify Exercise 10 using real cluster, per-pod HTTP and NodePort requests.

python3 verify.py [--require-empty-carts]
Adds one test item through the cart Service; never clears existing cart data.
Saves evidence and stops only its own temporary Service tunnels.
"""
import argparse,datetime,json,re,subprocess,tempfile,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROFILE='devops-multinode'

def run(*args):return subprocess.check_output(args,text=True)
def k(*args):return run('kubectl','--context',PROFILE,'-n','default',*args)
def obj(*args):return json.loads(k('get',*args,'-o','json'))
def ready(p):return p['status'].get('phase')=='Running' and any(c['type']=='Ready' and c['status']=='True' for c in p['status'].get('conditions',[]))
def pod_http(pod,path):
    code="import urllib.request,json; r=urllib.request.urlopen('http://127.0.0.1:80/"+path+"'); print(json.dumps({'status':r.status,'body':json.load(r)}))"
    return json.loads(k('exec',pod,'--','python','-c',code))
def request(url,data=None):
    data=None if data is None else json.dumps(data).encode()
    req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=10) as r:return {'status':r.status,'body':json.load(r)}

class Tunnel:
    def __init__(self,service):self.service=service
    def __enter__(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='exercise10-service-');self.log=Path(self.tmp.name)/'tunnel.log';self.stream=self.log.open('w')
        self.p=subprocess.Popen(['minikube','-p',PROFILE,'service',self.service,'-n','default','--url'],stdout=self.stream,stderr=subprocess.STDOUT)
        for _ in range(600):
            found=re.findall(r'http://127\.0\.0\.1:\d+',self.log.read_text())
            if found:return found[-1]
            if self.p.poll() is not None:break
            time.sleep(.1)
        self.__exit__(None,None,None)
        raise RuntimeError('Service tunnel did not provide loopback URL')
    def __exit__(self,*args):
        if self.p.poll() is None:
            self.p.terminate()
            try:self.p.wait(timeout=5)
            except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
        self.stream.close();self.tmp.cleanup()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-empty-carts',action='store_true');args=parser.parse_args()
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    initial_context=run('kubectl','config','current-context').strip()
    checks={};nodes=obj('nodes')['items'];pods=obj('pods','-l','devops-lab-exercise=10')['items'];deployments=obj('deployments','-l','devops-lab-exercise=10')['items'];services=obj('services','-l','devops-lab-exercise=10')['items'];replicasets=obj('replicasets','-l','devops-lab-exercise=10')['items']
    checks['three_ready_nodes']=len(nodes)==3 and all(any(c['type']=='Ready' and c['status']=='True' for c in n['status']['conditions']) for n in nodes)
    placement={};perpod={};expected=[{'id':1,'name':'Laptop','price':1200},{'id':2,'name':'Phone','price':800},{'id':3,'name':'Headphones','price':150}]
    for app,count,path in [('product-catalog',2,'products'),('shopping-cart',3,'cart')]:
        selected=[p for p in pods if p['metadata']['labels']['app']==app and not p['metadata'].get('deletionTimestamp')]
        placement[app]=[{'pod':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec']['nodeName'],'ready':ready(p)} for p in selected]
        checks[app+'_replicas_and_distribution']=len(selected)==count and all(ready(p) for p in selected) and len(set(p['spec']['nodeName'] for p in selected))==count
        d=next(d for d in deployments if d['metadata']['name']==app)
        checks[app+'_deployment_ready']=d['spec']['replicas']==count and d['status'].get('availableReplicas')==count and d['status'].get('updatedReplicas')==count
        affinity=d['spec']['template']['spec']['affinity']['podAntiAffinity']['requiredDuringSchedulingIgnoredDuringExecution']
        checks[app+'_strict_anti_affinity']=any(t['topologyKey']=='kubernetes.io/hostname' and t['labelSelector']['matchLabels']=={'app':app} for t in affinity)
        active=[rs for rs in replicasets if rs['metadata']['labels']['app']==app and rs['spec']['replicas']>0]
        checks[app+'_replicaset_ready']=len(active)==1 and active[0]['status'].get('readyReplicas')==count
        s=next(s for s in services if s['metadata']['name']==app+'-service')
        slices=obj('endpointslices','-l','kubernetes.io/service-name='+app+'-service')['items']
        endpoints=[ep for sl in slices for ep in sl.get('endpoints',[]) if ep.get('conditions',{}).get('ready')]
        checks[app+'_nodeport_endpoints']=s['spec']['type']=='NodePort' and len(endpoints)==count
        perpod[app]={p['metadata']['name']:pod_http(p['metadata']['name'],path) for p in selected}
    checks['all_catalog_pods_exact_products']=all(v=={'status':200,'body':expected} for v in perpod['product-catalog'].values())
    checks['cart_get_all_pods']=all(v['status']==200 and isinstance(v['body'],list) for v in perpod['shopping-cart'].values())
    if args.require_empty_carts:checks['all_initial_carts_empty']=all(v['body']==[] for v in perpod['shopping-cart'].values())
    images={}
    for n in nodes:
        name=n['metadata']['name'];images[name]=json.loads(run('minikube','-p',PROFILE,'ssh','--node',name,'--','sudo crictl images -o json'))
    checks['both_images_on_all_nodes']=all(all(any(app+':latest' in t for image in report['images'] for t in image.get('repoTags',[])) for app in ['product-catalog','shopping-cart']) for report in images.values())
    registry=json.loads(run('kubectl','--context',PROFILE,'-n','kube-system','get','pods','-o','json'))['items']
    checks['registry_addon_running']=any(p['metadata']['name'].startswith('registry-') and not p['metadata']['name'].startswith('registry-proxy-') and ready(p) for p in registry) and sum(p['metadata']['name'].startswith('registry-proxy-') and ready(p) for p in registry)==3
    if not all(checks.values()):raise RuntimeError(json.dumps(checks,indent=2))
    with Tunnel('product-catalog-service') as product_url, Tunnel('shopping-cart-service') as cart_url:
        product=request(product_url+'/products');cart_before=request(cart_url+'/cart');item={'id':1,'name':'Laptop','quantity':1};cart_post=request(cart_url+'/cart',item)
        checks['catalog_nodeport_http']=product=={'status':200,'body':expected}
        checks['cart_nodeport_get']=cart_before['status']==200 and isinstance(cart_before['body'],list)
        checks['cart_nodeport_post']=cart_post['status']==201 and cart_post['body'][-1]==item
        after={name:pod_http(name,'cart') for name in perpod['shopping-cart']}
        checks['post_added_one_item_to_one_replica']=sum(len(v['body']) for v in after.values())==sum(len(v['body']) for v in perpod['shopping-cart'].values())+1
        # Actual curl requests through the same Minikube NodePort tunnels.
        curl_product=run('curl','--fail-with-body','-sS','-i',product_url+'/products');curl_cart=run('curl','--fail-with-body','-sS','-i',cart_url+'/cart')
        (evidence/'curl-responses.txt').write_text('GET '+product_url+'/products\n'+curl_product+'\nGET '+cart_url+'/cart\n'+curl_cart)
        http={'catalog_url':product_url,'cart_url':cart_url,'catalog':product,'cart_before':cart_before,'cart_post':cart_post,'per_pod_before':perpod,'cart_per_pod_after':after,'tunnels_stopped_after_verification':True}
    checks['kubectl_context_unchanged']=run('kubectl','config','current-context').strip()==initial_context
    report={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'profile':PROFILE,'checks':checks,'all_passed':all(checks.values()),'placement':placement,'services':{s['metadata']['name']:{'nodePort':s['spec']['ports'][0]['nodePort'],'namespace':s['metadata']['namespace']} for s in services},'http':http,'limitations':['Cart state is per-process, not shared or persistent','No node failure simulation','Historical loopback URLs stop working when the verification tunnels close']}
    for name,value in [('verification.json',report),('nodes.json',nodes),('pods.json',pods),('deployments.json',deployments),('services.json',services),('replicasets.json',replicasets),('node-images.json',images)]:
        (evidence/name).write_text(json.dumps(value,indent=2)+'\n')
    (evidence/'pods-wide.txt').write_text(k('get','pods','-l','devops-lab-exercise=10','-o','wide'))
    print(json.dumps(report,indent=2));return 0 if report['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
