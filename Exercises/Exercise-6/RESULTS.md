# Exercise 6 — Results

## Experiment: Monitoring a Python Delivery Service Using Prometheus and Grafana

### Aim

To monitor a Python-based delivery service using Prometheus and Grafana, visualize application metrics, and configure alerting rules.

## 1. Python Delivery Metrics

**Result:** Successful

Created a Python application that exposes delivery metrics through an HTTP endpoint.

**Metrics endpoint:**

`http://localhost:8000/metrics`

**Observed metrics:**

- `total_deliveries`
- `pending_deliveries`
- `on_the_way_deliveries`
- `average_delivery_time_count`
- `average_delivery_time_sum`

The application generated changing delivery statistics that could be collected by Prometheus.

## 2. Prometheus Monitoring

**Result:** Successful

Configured Prometheus to scrape the Python application using:

- Job name: `delivery_service`
- Target: `host.docker.internal:8000`
- Prometheus URL: `http://localhost:9090`

Verified that Prometheus could query delivery metrics.

**Example PromQL query:**

```promql
total_deliveries - pending_deliveries - on_the_way_deliveries
```

This calculates the number of completed deliveries.

## 3. Grafana Dashboard

**Result:** Successful

Configured Grafana with Prometheus as the data source.

**Grafana URL:** `http://localhost:3000`

**Dashboard:** Delivery Monitoring Dashboard

Created five visualization panels:

| Panel | Description |
|---|---|
| Total Deliveries | Displays the total delivery count |
| Pending Deliveries | Displays pending deliveries |
| Completed Deliveries | Displays calculated completed deliveries |
| On-the-Way Deliveries | Displays deliveries in transit |
| Average Delivery Time | Displays the average delivery duration |

All five panels were visible and displayed monitoring data.

## 4. Dashboard Auto-Refresh

**Result:** Successful

Configured the Grafana dashboard to refresh every **5 seconds**.

Verified that delivery statistics changed as the Python application continued generating metrics.

## 5. Prometheus Alert Rules

**Result:** Configuration created

Created `alert_rules.yml` with the following alert definitions:

**HighPendingDeliveries**

- Condition: `pending_deliveries > 10`
- Duration: `15s`
- Severity: `warning`

**HighAverageDeliveryTime**

- Purpose: Identify high average delivery times
- Severity: `critical`

Alert definitions were created. Actual alert firing and notification delivery were not verified.

## 6. Dashboard Export

**Result:** Successful

Exported the Grafana dashboard to:

`Exercises/Exercise-6/dashboard.json`

Validated the file using:

```bash
python3 -m json.tool Exercises/Exercise-6/dashboard.json > /dev/null && echo "JSON is valid"
```

**Output:**

```text
JSON is valid
```

Verified that the exported JSON contained all five dashboard panel titles.

## Final Results

| Test | Status |
|---|---|
| Python metrics endpoint | PASS |
| Prometheus metrics collection | PASS |
| Prometheus query execution | PASS |
| Grafana dashboard configuration | PASS |
| Five visualization panels | PASS |
| Automatic refresh | PASS |
| Alert rule file creation | PASS |
| Dashboard JSON validation | PASS |
| Alert firing and notifications | NOT VERIFIED |

## Conclusion

The delivery monitoring system was successfully implemented using Python, Prometheus, and Grafana.

Prometheus collected delivery metrics from the Python application, and Grafana displayed the collected data through five dashboard panels with automatic refresh.

Prometheus alert rules were also defined to identify high pending delivery counts and excessive average delivery times.

## Audit and supplementary verification

The original screenshots demonstrate metrics, two UP scrape targets and the manual dashboard. During a later read-only audit, both loaded Prometheus rules were healthy and `HighPendingDeliveries` was firing. This updates the historical statement that firing had not been verified. The five panel queries were checked against live Prometheus and returned data.

The exported Grafana V2 JSON contained all five correct queries but saved an empty `autoRefresh`; the available interval list alone did not enable refresh. The export is now corrected to `5s`. The original local Grafana instance is preserved; the corrected setting will be checked in the separately provisioned pipeline dashboard.

The missing Jenkins and controlled alert tests have been prepared in a disposable GitHub runner. Their result remains pending the actual run. No Jenkins success, controlled alert firing or external notification is claimed before execution.
