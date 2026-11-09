# INCIDENT-001: Elevated 5xx on staging

> **TEMPLATE - not filled in yet.** Complete this file from your own incident drill (README, section
> "Incident drill"). Every time, query and log line must come from your running system. Do not write
> anything here you did not observe.

## Timeline (UTC)

| Time  | Event |
|-------|-------|
| hh:mm | Fault injection enabled on staging (`ENABLE_FAULT_INJECTION=true`) |
| hh:mm | Error-rate panel rises above 5% |
| hh:mm | `HighErrorRate` alert goes pending, then firing (detection) |
| hh:mm | ERROR logs identify the endpoint and the start time |
| hh:mm | Fault injection disabled, staging redeployed |
| hh:mm | Error rate back to 0% and the alert resolved |

## Detection

How was the problem noticed: alert, dashboard panel, or both? At what time?

## Evidence from logs

The LogQL query used, and one sample ERROR line copied from Grafana.

## Root cause

What actually caused the 5xx responses?

## Recovery

The action taken, and the dashboard evidence that it worked (name the screenshot).

## Prevention

One idea that would stop this happening, or make it faster to detect, next time.
