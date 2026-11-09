# AI assistance record

This document records the AI assistance used in the System Health Dashboard project, for both mini projects.

## Mini Project 1

| Area | What Claude did |
|------|-----------------|
| Planning | Organised the mthree course pages into a study map and blank templates for issues, the pipeline and the README |
| Learning support | Explained Git branches, virtual environments, environment variables and Flask concepts; reviewed my code and pointed out errors |
| `app.py` | Wrote the `/environment` route after I drafted it, and an upgraded version adding the timestamp, uptime, `APP_VERSION`, hostname and JSON 404 handler |
| Documentation | Tidied the wording of the Overview, Docker section and merge conflict record, and drafted the README |

I wrote the first `/health` and `/version` endpoints, set up the repository and branches, resolved the merge conflict, built and ran the Docker image, and built and ran the Jenkins pipeline myself.

## Mini Project 2

Claude (Claude Code, model Claude Sonnet 5.5) wrote the second half of this project from the Mini Project 2 participant guide. Its commits carry a `Co-Authored-By: Claude Sonnet 5.5` line, so the Git history shows exactly which work it did.

| Area | What Claude did |
|------|-----------------|
| Application | Added `/metrics` and the metrics, JSON request logging, `/simulate-error`, the `ENVIRONMENT` setting and the new tests |
| Environments and pipeline | Wrote both Compose files, `scripts/smoke_test.sh`, `scripts/rollback.sh`, the extended `Jenkinsfile` and `jenkins/Dockerfile` (found that the existing Jenkins image had no Compose plugin) |
| Monitoring | Wrote the monitoring Compose file, Prometheus, Loki and Promtail configuration, the alert rules, the Grafana provisioning files and the dashboard JSON |
| Testing | Ran the test suite, started both environments and the monitoring stack in Docker, and checked the endpoints, smoke test, rollback script, targets, alert rules, logs and dashboard against the running system. Also repeated the stack start from a fresh clone, and replayed the pipeline's deploy steps from inside the Jenkins image. These were tooling checks: the Jenkins pipeline itself was not run, and the incident drill evidence is the learner's own |
| Documentation | Wrote the README, the architecture diagram and the `INCIDENT.md`, `REFLECTION.md` and screenshots templates |

Not done by Claude: the Jenkins pipeline runs, the approval, the rollback demonstration, the incident drill with its timeline, the screenshots and the reflection answers. These must be performed and written by the learner from their own running system.
