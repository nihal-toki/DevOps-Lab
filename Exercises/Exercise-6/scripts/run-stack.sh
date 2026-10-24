#!/bin/sh
set -eu
: "${LAB_PREFIX:?Missing lab prefix}"
: "${SCENARIO:?Missing scenario}"
case "$SCENARIO" in normal|high_pending|high_pending_slow) ;; *) exit 2;; esac
case "${1:-all}" in
  app) roles=metrics ;;
  monitoring) roles="prometheus grafana" ;;
  all) roles="metrics prometheus grafana" ;;
  *) exit 2 ;;
esac
for role in $roles; do
  name="$LAB_PREFIX-$role"
  if docker inspect "$name" >/dev/null 2>&1; then
    owner=$(docker inspect --format '{{index .Config.Labels "devops.lab.run"}}' "$name")
    test "$owner" = "$LAB_PREFIX"
    docker rm -f -v "$name"
  fi
done
if [ "${1:-all}" != monitoring ]; then
docker run -d --name "$LAB_PREFIX-metrics" --label "devops.lab.run=$LAB_PREFIX" --network "$LAB_PREFIX-net" --network-alias delivery_metrics -e "DELIVERY_SCENARIO=$SCENARIO" -p 127.0.0.1::8000 "$LAB_PREFIX-metrics:latest"
fi
if [ "${1:-all}" != app ]; then
docker run -d --name "$LAB_PREFIX-prometheus" --label "devops.lab.run=$LAB_PREFIX" --network "$LAB_PREFIX-net" --network-alias prometheus -p 127.0.0.1::9090 "$LAB_PREFIX-prometheus:latest"
docker run -d --name "$LAB_PREFIX-grafana" --label "devops.lab.run=$LAB_PREFIX" --network "$LAB_PREFIX-net" --network-alias grafana --env-file /lab-private/grafana.env -p 127.0.0.1::3000 "$LAB_PREFIX-grafana:latest"
fi
