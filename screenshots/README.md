# Evidence screenshots

Capture each screenshot from your own running system while you do the step, then save it in this folder
with the exact name below. Tick the box when the file is committed.

| Done | File | What it must show |
|------|------|-------------------|
| [ ] | `01-pipeline-full-run.png` | Jenkins Stage View of a successful run showing every stage |
| [ ] | `02-approval-gate.png` | The pipeline paused at the Approval stage |
| [ ] | `03-failure-rollback.png` | A failed run and the rollback restoring the previous image tag |
| [ ] | `04-prometheus-targets-up.png` | Prometheus Status > Targets with both environments UP |
| [ ] | `05-alert-rules-firing.png` | Prometheus Alerts page with both rules loaded and one firing |
| [ ] | `06-dashboard-healthy.png` | Grafana "System Health Overview" with healthy traffic |
| [ ] | `07-dashboard-incident.png` | The dashboard during the incident: error spike and ERROR logs |
| [ ] | `08-dashboard-recovered.png` | The dashboard after recovery, error rate back to normal |
