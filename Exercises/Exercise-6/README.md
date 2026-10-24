# Exercise 6 — Monitoring and Alerting with Prometheus and Grafana

## Objective

Implement a delivery monitoring system using Python, Prometheus, and Grafana to collect application metrics, visualize delivery statistics, and configure alerting rules.

## Technologies Used

- **Python** — Delivery metrics application
- **Prometheus** — Metrics collection and monitoring
- **Grafana** — Dashboard visualization
- **Docker** — Running Grafana in a container
- **YAML** — Prometheus configuration and alert rules

## Project Structure

```text
Exercise-6/
├── delivery_monitoring/
│   ├── delivery_metrics.py
│   ├── prometheus.yml
│   └── alert_rules.yml
├── dashboard.json
└── README.md
```

## Tasks Performed

### Task 1 — Create the Delivery Metrics Application

Created `delivery_metrics.py` to expose delivery-related metrics for Prometheus.

The monitored metrics include:

- `total_deliveries` — Total number of deliveries
- `pending_deliveries` — Deliveries awaiting completion
- Completed deliveries — calculated as `total_deliveries - pending_deliveries - on_the_way_deliveries`; not a separately exported metric
- `on_the_way_deliveries` — Deliveries currently in transit
- `average_delivery_time` — Average delivery duration

The metrics endpoint was accessible on port `8000`.

### Task 2 — Configure Prometheus

Created `prometheus.yml` to configure Prometheus to collect metrics from the Python delivery application.

The delivery monitoring target was configured using the job name `delivery_service`.

Prometheus was used to execute queries and inspect the collected delivery metrics.

### Task 3 — Configure Alert Rules

Created `alert_rules.yml` with monitoring alerts.

**HighPendingDeliveries**

- Expression: `pending_deliveries > 10`
- Duration: `15s`
- Severity: `warning`
- Purpose: Identify situations where too many deliveries remain pending.

**HighAverageDeliveryTime**

- Purpose: Detect unusually high average delivery times.
- Severity: `critical`

### Task 4 — Create the Grafana Dashboard

Configured Grafana with Prometheus as its data source.

Created the **Delivery Monitoring Dashboard** containing five panels:

1. Total Deliveries
2. Pending Deliveries
3. Completed Deliveries
4. On-the-Way Deliveries
5. Average Delivery Time

The dashboard displays delivery statistics using Stat visualizations and sparklines.

### Task 5 — Configure Dashboard Thresholds

Configured threshold-based coloring to make delivery metrics easier to interpret.

For the Total Deliveries panel, the threshold configuration was adjusted so that the displayed value used green coloring.

### Task 6 — Enable Automatic Refresh

Configured the Grafana dashboard to refresh every **5 seconds**.

This allows the displayed metrics to update automatically while the monitoring services are running.

### Task 7 — Export the Dashboard

Exported the Grafana dashboard configuration to `dashboard.json`.

Validated the JSON file using:

```bash
python3 -m json.tool Exercises/Exercise-6/dashboard.json > /dev/null && echo "JSON is valid"
```

Observed result:

```text
JSON is valid
```

Verified that the exported configuration contains all five dashboard panel titles.

## Verification Results

| Test | Result |
|---|---|
| Delivery metrics visible in Prometheus | Passed |
| Prometheus query execution | Passed |
| Grafana dashboard created | Passed |
| Five dashboard panels present | Passed |
| Dashboard auto-refresh configured | Passed |
| Dashboard JSON syntax validation | Passed |
| Dashboard panel titles verified | Passed |
| Alert rule configuration file created | Passed |
| Alert firing and notification delivery | Not verified |

## Conclusion

Exercise 6 demonstrates application monitoring using Python, Prometheus, and Grafana.

The delivery metrics were successfully displayed in Prometheus and visualized through a Grafana dashboard. Alert rule configurations were created, and the dashboard was exported as a valid JSON file.

The dashboard provides visibility into delivery counts, pending orders, completed deliveries, in-transit deliveries, and average delivery time.

## Remaining requirements: pipeline verification in progress

The original simulator and local monitoring YAML are preserved. `run_metrics.py` wraps the same simulator for three scenarios without editing its code: `normal` (pending 10–20), `high_pending` (pending 50–100, delivery time 15–45 seconds), and `high_pending_slow` (pending 50–100, delivery time 35–45 seconds). The last scenario is an additional deterministic check that both alert expressions fire.

`Jenkinsfile` contains the five required stages: Docker pre-check, workspace setup, image build/tests, application startup, and Prometheus/Grafana startup. The provisioning files supply the original five metric expressions plus an alert table. `dashboard.json` retains the owner's Grafana V2 export with its saved `autoRefresh` corrected to `5s`; the reproducible dashboard in `grafana/dashboards/delivery.json` is a provisioned Classic-schema equivalent for Grafana 12.1.1.

The workflow `.github/workflows/exercise-6.yml` runs actual Jenkins builds on a disposable Ubuntu runner. Jenkins uses that isolated runner's Docker socket as root; `run_pipeline.py` refuses to run outside GitHub Actions. Do not use that controller configuration on a laptop or production host. It never connects to the laptop Docker engine or changes the existing local monitoring containers. Temporary administrator passwords are generated into a private directory and never committed or printed.

`run_pipeline.py` waits for Jenkins, creates the job from the checked-in Jenkinsfile, builds all three scenarios, checks real console results, queries Prometheus and Grafana APIs, and removes only resources with its unique run label. The script saves measured reports under `evidence/`; CI removes checked-in report copies first to avoid treating old evidence as a new run.

The original API targets use `host.docker.internal` for a simulator on macOS. The isolated pipeline uses Docker DNS `delivery_metrics:8000` and Grafana's `http://prometheus:9090`, with five-second scrape/evaluation intervals. Source alert expressions, severities and hold times are retained. The Summary expression is a cumulative observed mean, not a latency percentile.

The original local `HighPendingDeliveries` rule was observed firing during audit; `HighAverageDeliveryTime` was inactive because the observed mean was below 30 seconds. External email/Slack delivery is not configured and is not demonstrated by a firing Prometheus rule. The sheet requires alert states; it does not specify an external receiver.

Seven genuine full-page screenshot captures from the supplied `Exercise_6_Screenshots.pdf` are saved in `evidence/`, covering the metrics endpoint, targets, query, original dashboard, rule editor, export and JSON validation. They are not relabelled as Jenkins or controlled-alert screenshots. Pipeline completion remains pending until measured build and API checks pass.
