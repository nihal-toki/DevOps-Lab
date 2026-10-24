# Exercise 10 Results

Verified on 24 October 2026 on macOS using Docker Desktop, Minikube 1.39.0, Kubernetes 1.37.0 and containerd 2.3.4.

## Initial deployment

All three nodes were Ready. Product Catalog had two ready replicas on different nodes, and Shopping Cart had three ready replicas across all three nodes. Their active ReplicaSets and ready Service endpoints matched 2 and 3 respectively.

| Node | Catalog replicas | Cart replicas |
| --- | --- | --- |
| devops-multinode | 0 | 1 |
| devops-multinode-m02 | 1 | 1 |
| devops-multinode-m03 | 1 | 1 |

Both application images were present in all three node runtimes. The registry pod and three registry proxies were Running and Ready. Five unit tests passed in each application image; the actual output is retained in [startup.txt](evidence/startup.txt).

The initial audit passed all **21 checks**. Both catalog pods and the NodePort Service returned the exact three products: Laptop (1200), Phone (800), Headphones (150). Every cart pod initially returned `[]`. The cart Service GET returned HTTP 200, and POST of `{"id":1,"name":"Laptop","quantity":1}` returned HTTP 201 with the new item.

Catalog NodePort: **31562**. Cart NodePort: **31829**. Real requests used Minikube's local Service tunnels on macOS. Their historical URLs are not permanent endpoints.

After the POST, only `shopping-cart-f795c88b-xpcj9` held the item; the other two remained empty. This proves the source's per-replica state rather than shared cart consistency. See [verification.json](evidence/verification.json) for before/after responses and [curl-responses.txt](evidence/curl-responses.txt) for actual HTTP headers and response bodies.

## Rolling replacement

See [rollout.json](evidence/rollout.json) for actual replacement pod UIDs, placement and availability samples. Replacement intentionally discards the original in-memory carts. The browser cart capture was taken after this replacement and shows an empty list, not the earlier post-request state.

## Scope and preservation

The existing `minikube` profile, Exercise 7 Jenkins controller, Exercise 6 monitoring containers and current kubectl context were preserved. Exercise 9 files and Jenkins configuration were not changed. This exercise follows the source's application behavior and required filenames, with the cart namespace mismatch corrected. The reference's file conventions were compared; all evidence and explanations here are from this run.

No original Exercise 10 screenshots were supplied; genuine browser captures of both running Services were taken during execution. No required execution evidence is missing. Node failure and shared cart storage were not implemented or claimed; the question's in-memory app does not provide persistent cart data. CI workflow repetition is an extra in the reference, not part of this local run.

All four rolling replacement checks passed across 93 samples, with a minimum of two available cart replicas. Final source-hash checks on all five running application pods matched the repository; see [source-hashes.json](evidence/source-hashes.json). Both applications remain running in the new profile.
