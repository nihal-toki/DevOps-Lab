# Exercise 6 Results

Run date: 24 October 2026. The owner's manual macOS monitoring setup is preserved separately from the supplementary Jenkins verification on Ubuntu 24.04.

## Original manual monitoring evidence

The supplied screenshots show the metrics endpoint, two UP Prometheus targets, a completed-deliveries query, the five-panel dashboard, alert-rule configuration, dashboard export and JSON validation. The original five panel queries are correct. Completed deliveries is a derived expression, not an exported Gauge.

A read-only audit of the original local services found both scrape targets UP, both rules healthy, and `HighPendingDeliveries` firing. The average-time rule was inactive at that observation because the measured mean was below 30 seconds. This corrects the earlier draft statement that alert firing had never been verified. See [original-local-status.json](evidence/original-local-status.json).

The original Grafana V2 export contained an empty saved `autoRefresh` even though 5 seconds appeared among the available interval choices. The exported file is now corrected to `5s`. The original local Grafana instance was not edited; five-second refresh was verified on the newly provisioned pipeline dashboard.

## Genuine Jenkins builds

[GitHub Actions run 40092471612](https://github.com/nihal-toki/DevOps-Lab/actions/runs/40092471612) passed using commit `6f25f3674fe5bf96c3697848efc620fe0027481f`. It started a real Jenkins controller and ran the checked-in five-stage Jenkinsfile for all scenarios. These are Jenkins build results, not shell scripts labelled as Jenkins output.

| Scenario | Jenkins build | Result | Pending snapshot | Mean snapshot (seconds) | Firing alerts at recorded check |
| --- | ---: | --- | ---: | ---: | --- |
| normal | 1 | SUCCESS | 10 | 25.03 | None at recorded alert check |
| high_pending | 2 | SUCCESS | 51 | 32.08 | HighPendingDeliveries |
| high_pending_slow | 3 | SUCCESS | 74 | 41.81 | HighPendingDeliveries, HighAverageDeliveryTime |

Each build ran all **four Python tests successfully**, and `promtool` accepted the monitoring configuration and both rules. Each scenario passed all **nine monitoring check groups**: metric ranges and totals, increasing Summary observations, two UP scrape targets, healthy Grafana data source, five metric queries returning data through Grafana, saved five-second refresh, alert-rule checks, required scenario alert states, and firing-alert visibility through Grafana.

The table's pending and mean values are individual snapshots taken before the final alert wait, not fixed simulator values or a guarantee of the alert state at that exact instant. Rule evaluation uses subsequent scrapes; this explains why a mean snapshot can exceed 30 without the average-time alert appearing in the later recorded alert set. The controlled slow run required and observed both alerts firing. Normal traffic has no requirement that all alerts remain inactive; its pending rule was pending at the recorded check.

## Dashboard and alert verification

Grafana's data-source health endpoint returned OK. Its saved dashboard used `refresh: 5s`; each of the original five metric expressions returned series through Grafana's Prometheus proxy. The additional alerts table's expression returned the required firing alert names in the controlled scenarios.

The pending rule retained a 15-second hold and warning severity. The average-time rule retained no hold time and critical severity. The Summary query is a cumulative observed mean. No percentile, external notification delivery or capacity benchmark is claimed.

## Evidence

- Normal: [Jenkins console](evidence/jenkins-normal.txt), [build result](evidence/jenkins-normal.json), [metrics](evidence/metrics-normal.txt), [verification](evidence/verification-normal.json)
- High pending: [Jenkins console](evidence/jenkins-high_pending.txt), [build result](evidence/jenkins-high_pending.json), [metrics](evidence/metrics-high_pending.txt), [verification](evidence/verification-high_pending.json)
- High pending and slow: [Jenkins console](evidence/jenkins-high_pending_slow.txt), [build result](evidence/jenkins-high_pending_slow.json), [metrics](evidence/metrics-high_pending_slow.txt), [verification](evidence/verification-high_pending_slow.json)
- [Jenkins image build](evidence/jenkins-image-build.txt)
- [Runner and image environment](evidence/pipeline-environment.json)
- [Cleanup](evidence/cleanup.json)
- [Workflow and artifact provenance](evidence/workflow-run.json)

The JSON and text reports above were downloaded from the successful workflow artifact without editing their measurements. Temporary service URLs in them are historical and no longer active after cleanup.

## Original screenshot captures

| PDF page | Screenshot |
| --- | --- |
| 1 | [Metrics endpoint](evidence/metrics-endpoint.png) |
| 2 | [Prometheus targets](evidence/prometheus-targets.png) |
| 3 | [Prometheus query](evidence/prometheus-query.png) |
| 4 | [Original dashboard](evidence/dashboard-original.png) |
| 5 | [Original alert-rule editor](evidence/alert-rules-original.png) |
| 6 | [Dashboard export](evidence/dashboard-export-original.png) |
| 7 | [JSON validation](evidence/dashboard-json-validation.png) |

These are unchanged full-page captures of the supplied PDF. No new Jenkins or controlled-alert browser screenshots were captured; their real console logs and API reports provide the execution evidence instead.

## Cleanup and completion

Cleanup removed four temporary containers (Jenkins, simulator, Prometheus and Grafana) and the temporary network. No owned containers remained, and previously existing runner networks were preserved. The original local simulator and monitoring containers were not stopped or changed.

The required metrics, monitoring dashboard, alert simulation and successful Jenkins pipeline are now demonstrated. The extra completed-deliveries panel and deterministic slow scenario extend the source without replacing the original implementation. The missing practical steps are complete.
