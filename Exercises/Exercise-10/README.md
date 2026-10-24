# Exercise 10: Multi-Node Kubernetes Applications

## Aim

Deploy the Product Catalog with two replicas and the Shopping Cart with three replicas on three Minikube nodes. Spread each application's replicas across nodes, expose NodePort Services, and verify the source's GET and POST operations.

## Files and setup

The application names, Python files, Dockerfiles and four YAML filenames follow the question sheet and [reference repository](https://github.com/Anas2694/DevOps-Lab/tree/main/Exercises/Exercise-10). The macOS helpers `start.sh`, `verify.py` and `verify_rollout.py` replace the reference's PowerShell helpers. README, RESULTS and `evidence/` follow the same organization. No personal screenshots, terminal output or explanations were copied from the reference.

Prerequisites: Docker Desktop running, Minikube, kubectl, Python 3 and curl. From this exercise folder:

```bash
sh start.sh
python3 verify.py --require-empty-carts
```

The startup script creates/reuses only `devops-multinode`, using three Docker-driver/containerd nodes, Kubernetes 1.37.0, two CPUs and a 2 GiB memory limit per node. It retains the current kubectl context, enables the registry addon, builds `product-catalog:latest` and `shopping-cart:latest`, runs five unit tests in each image, loads the images and applies the manifests. Objects with conflicting names must carry this exercise's ownership label before the script will update them. It never deletes another profile or stops unrelated containers.

On a fresh profile, all carts are empty. Later checks should omit `--require-empty-carts` because the verifier adds one Laptop item and deliberately preserves existing carts. Do not expect subsequent service GETs to return the same list: each replica has independent state.

`start.sh` does not force a rollout when a local `latest` image changes. If you change application code, explicitly replace its pods after loading the rebuilt image. Cart replacement loses the source app's in-memory contents. Do not reuse the profile for unrelated workloads.

## Applications and Kubernetes configuration

- `product_catalog.py`: GET `/products` returns the three source products.
- `shopping_cart.py`: GET `/cart` returns that process's list; POST `/cart` appends JSON and returns HTTP 201.
- Both apps retain the source's Flask development server on port 80. The source's Python 3.9 slim base is retained and Flask is pinned to 3.1.3. This is a teaching deployment, not a production server.
- Product Catalog has two replicas; Shopping Cart has three. Both use required pod anti-affinity on `kubernetes.io/hostname`, `imagePullPolicy: Never`, readiness probes and small resource requests/limits.
- Both Deployments and Services use `default`. This corrects the sheet's cart Deployment/Service namespace mismatch: a Service cannot select pods across namespaces.
- Rolling updates use `maxSurge: 0`, `maxUnavailable: 1`. A cart rollout can therefore replace one of three pods without waiting for a fourth node that strict anti-affinity would require.

The registry addon is enabled as requested. `minikube image load` distributes images into the node runtimes; it does not push them to that registry. Both images are verified on every node using `crictl images` for containerd. See the official [Minikube image-loading guide](https://minikube.sigs.k8s.io/docs/handbook/pushing/) and [Kubernetes pod placement documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/).

## Access and curl

Open two terminals and keep these Service tunnels running:

```bash
minikube -p devops-multinode service product-catalog-service -n default --url
minikube -p devops-multinode service shopping-cart-service -n default --url
```

Each prints a current `http://127.0.0.1:PORT` URL. On macOS Docker-driver nodes, use that tunnel URL rather than assuming the node IP is reachable. Ports from the question and saved evidence are examples, not permanent URLs.

Substitute the catalog and cart URLs printed by your current tunnels:

```bash
curl http://127.0.0.1:CATALOG_PORT/products
curl http://127.0.0.1:CART_PORT/cart
curl -X POST http://127.0.0.1:CART_PORT/cart \
  -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Laptop","quantity":1}'
```

The verifier starts its own Minikube Service tunnels, sends real HTTP GET and POST requests, additionally records curl GET headers/bodies, then stops only those temporary tunnels. POST returns the updated list of the pod that handled it. After verification, create fresh tunnels to browse the applications.

## Verification and rolling replacement

The verification report records 21 initial checks covering three Ready nodes; deployment and ReplicaSet counts; required anti-affinity and actual placement; ready Service endpoints; images on every node; registry and proxy readiness; both catalog pod responses; all initially empty carts; Service GET/POST requests; exactly one additional item across the replicas; and an unchanged kubectl context.

The optional replacement demonstration has already been executed for this submission:

```bash
python3 verify_rollout.py
```

It deliberately replaces only the three Exercise 10 cart pods, checks new UIDs and placement, and samples replica availability. This discards those pods' in-memory carts. The report requires at least two available cart replicas in every sample and three empty new carts afterward. This is a rolling replacement test, not a simulated node failure or a continuous zero-downtime guarantee.

## Evidence and limitations

- [Measured initial verification](evidence/verification.json)
- [Rolling replacement measurements](evidence/rollout.json)
- [Actual startup and image unit-test output](evidence/startup.txt)
- [Catalog image build](evidence/build-product.txt) and [cart image build](evidence/build-shopping.txt)
- [Actual curl responses](evidence/curl-responses.txt)
- [Initial pod distribution](evidence/pods-wide.txt)
- [Product Catalog browser capture](evidence/product-catalog.png)
- [Shopping Cart browser capture](evidence/shopping-cart.png)
- [Question hash and evidence provenance](evidence/source-provenance.json)

Raw API snapshots for nodes, pods, deployments, ReplicaSets, Services, registry pods and node image caches accompany the measured reports. These are historical evidence; node ports remain assigned while Services exist, but temporary tunnel URLs expire. The cart screenshot was captured after the rolling replacement, which reset all three per-pod lists.

The source application's carts are neither shared nor persistent. Strict anti-affinity also requires all three nodes to schedule all three cart replicas. No external registry publication, production deployment, node-failure simulation, external notification or GitHub Actions run is claimed. Unlike the reference's supplementary CI workflow, this submission records an actual local macOS run.

To pause only this exercise while retaining the cluster, run `minikube stop -p devops-multinode`. Resume with `minikube start -p devops-multinode --keep-context`. Do not run the question's blanket `minikube delete` command against earlier lab work.

See [RESULTS.md](RESULTS.md) for the actual run.
