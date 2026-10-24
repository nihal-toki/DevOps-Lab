#!/bin/sh
set -eu
cd "$(dirname "$0")"
profile=devops-multinode
minikube start -p "$profile" --driver=docker --container-runtime=containerd --nodes=3 --cpus=2 --memory=2048 --kubernetes-version=v1.37.0 --keep-context
kubectl --context "$profile" wait --for=condition=Ready node --all --timeout=300s
minikube -p "$profile" addons enable registry
for app in product-catalog shopping-cart; do
  for kind in deployment service; do
    name="$app"
    [ "$kind" != service ] || name="$app-service"
    if kubectl --context "$profile" -n default get "$kind" "$name" >/dev/null 2>&1; then
      owner=$(kubectl --context "$profile" -n default get "$kind" "$name" -o 'jsonpath={.metadata.labels.devops-lab-exercise}')
      [ "$owner" = 10 ] || { echo "Refusing to replace unowned $kind/$name" >&2; exit 1; }
    fi
  done
done
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .
for image in product-catalog shopping-cart; do
  docker run --rm "$image:latest" python -m unittest -v test_apps
  minikube -p "$profile" image load "$image:latest"
done
for file in product_catalog_deployment.yaml shopping_cart_deployment.yaml product_catalog_service.yaml shopping_cart_service.yaml; do
  kubectl --context "$profile" apply -f "$file"
done
for app in product-catalog shopping-cart; do
  kubectl --context "$profile" -n default rollout status deployment/"$app" --timeout=300s
done
