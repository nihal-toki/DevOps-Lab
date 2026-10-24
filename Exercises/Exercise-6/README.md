# Exercise 6: Delivery Monitoring with Prometheus, Grafana and Jenkins

Simulate delivery activity, scrape metrics, display a Grafana dashboard and verify alert rules through a real Jenkins pipeline.

**Completed:** the original manual macOS setup is preserved, and [GitHub workflow run 40092471612](https://github.com/nihal-toki/DevOps-Lab/actions/runs/40092471612) completed three successful Jenkins builds covering normal traffic, high pending deliveries and a controlled slow-delivery scenario. Measured results and original screenshots are in [RESULTS.md](RESULTS.md).

## Original application and local setup

The preserved `delivery_monitoring/delivery_metrics.py` exposes three Gauges and a Summary at `http://localhost:8000/metrics` and updates once per second. Normal ranges are pending 10–20, on-the-way 5–20, completed 30–70, and delivery time 15–45 seconds. Total deliveries is the sum of the three counts.

`completed_deliveries` is not an exported metric. The completed-deliveries panel calculates `total_deliveries - pending_deliveries - on_the_way_deliveries`. The average-time panel uses `average_delivery_time_sum / average_delivery_time_count`, the cumulative observed mean since application startup, rather than a percentile.

The original macOS Prometheus configuration uses `host.docker.internal:8000`, a 15-second scrape/evaluation interval, and the supplied `delivery_monitoring/alert_rules.yml`. The local Prometheus and Grafana containers remain unchanged at ports 9090 and 3000.

## Jenkins pipeline

The root `Jenkinsfile` follows the source's five stages:

1. **Pre-check Docker:** verify the Docker CLI and daemon.
2. **Setup Workspace:** copy this exercise's saved files into Jenkins's workspace.
3. **Build Docker Image:** build the application and monitoring images, run all four Python tests and validate Prometheus configuration and both rules with `promtool`.
4. **Run Application:** start the selected simulator scenario.
5. **Run Prometheus & Grafana:** start the monitoring services with their saved provisioning configuration.

Each scenario uses the same pipeline and replaces only containers carrying its unique run label. Docker DNS names connect the services: Prometheus scrapes `delivery_metrics:8000` and Grafana uses `http://prometheus:9090`. The isolated configuration in `prometheus/` uses five-second scrape/evaluation intervals; the original macOS YAML is preserved.

## Repeat the verified run

In this repository's GitHub **Actions**, select **Exercise 6 Jenkins monitoring verification** and choose **Run workflow**. Alternatively:

```sh
gh workflow run exercise-6.yml --repo nihal-toki/DevOps-Lab
```

The workflow starts a real Jenkins controller on a disposable Ubuntu 24.04 runner, creates the job from `Jenkinsfile`, and executes all three builds. Jenkins uses root access to that disposable runner's Docker socket. This is a trusted-repository CI lab configuration; it is not a controller configuration for a laptop, shared host or production system. `run_pipeline.py` refuses to run outside GitHub Actions and never connects to the laptop Docker engine. This avoids changing existing local services.

Temporary Jenkins and Grafana administrator passwords are generated into a private temporary directory and are never printed, embedded into images or committed. The scripts publish temporary localhost ports, not fixed host ports. Service URLs in reports describe the recorded run and cease working after cleanup.

The `exercise6-pipeline-evidence` artifact contains real Jenkins console logs, build results, metrics, verification reports and cleanup results. The workflow clears checked-in report copies in its disposable workspace before running, so a failed run cannot upload old reports as fresh measurements.

## Metrics and alert scenarios

`run_metrics.py` wraps the original simulator without modifying it. It changes only the random ranges needed for each scenario:

| Scenario | Pending deliveries | Delivery-time observations |
| --- | --- | --- |
| normal | 10–20 | 15–45 seconds |
| high_pending | 50–100 | 15–45 seconds |
| high_pending_slow | 50–100 | 35–45 seconds |

`high_pending` implements the sheet's required 50–100 test. `high_pending_slow` is an additional deterministic check of both rules. On-the-way and completed-delivery ranges remain unchanged.

| Rule | Expression | Hold time | Severity |
| --- | --- | --- | --- |
| HighPendingDeliveries | `pending_deliveries > 10` | 15 seconds | warning |
| HighAverageDeliveryTime | `(average_delivery_time_sum / average_delivery_time_count) > 30` | none | critical |

The rules retain the source YAML, including warning severity for the pending rule and no `for` on the average-time rule. Normal random values can also trigger these thresholds. The tests require the appropriate alert states for each controlled scenario, not that normal traffic always has no alerts.

The verifier checks metric ranges and count growth, both scrape targets, Grafana data-source health, all five panel queries through Grafana, saved five-second refresh, rule definitions, and the required firing alerts through both Prometheus and Grafana's proxy. There is no Alertmanager or external email/Slack receiver; firing rule states are verified, not notification delivery.

## Dashboard files and screenshots

`dashboard.json` preserves the owner's Grafana V2 export and five original panel queries. Its saved `spec.timeSettings.autoRefresh` was corrected from an empty string to `5s`. This changes the export, not the existing manually configured local Grafana instance.

`grafana/dashboards/delivery.json` is a provisioned Classic-schema equivalent for Grafana 12.1.1. It contains the same five metric expressions plus a table of firing Prometheus alerts. The pipeline verified all five metric queries, alert visibility and the five-second refresh setting through Grafana APIs. Provisioning follows [Grafana's documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/).

Seven genuine unchanged full-page captures from `Exercise_6_Screenshots.pdf` are in `evidence/`. They show the original metrics, scrape targets, query, dashboard, alert-rule editor, export and JSON validation. They are not presented as Jenkins or controlled-scenario screenshots; those results are supported by actual logs and API reports.

## Cleanup and preserved work

After verification, the orchestrator removes only containers with its unique run label and its temporary network, including the Jenkins controller. Previously existing runner networks are checked for preservation. Local monitoring containers, the original application and YAML files, and Exercises 1–5 are unchanged. Images on the disposable runner are discarded when GitHub releases it.

The first pipeline attempt built and tested the images but stopped because a generic Docker inspect call matched a same-named image during the container ownership check. The corrected script explicitly inspects containers. The successful rerun passed all build and monitoring assertions; the failed attempt remains visible in GitHub history.
