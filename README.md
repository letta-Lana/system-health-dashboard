System Health Dashboard API
Overview
<!-- What it does, who it's for, the three endpoints -->

A lightweight API that returns basic status information for engineers and automated monitoring 
checks. It exposes three endpoints: /health (whether the service is up), /version 
(the current application version) and /environment (the environment it’s running in). 

Prerequisites
<!-- Tools and versions needed -->

Setup
<!-- Clone, install dependencies -->

Configuration
<!-- Which environment variable(s), defaults, how to set them -->

Running locally
<!-- Start command; how to verify each endpoint -->

Running tests
<!-- The one command; what passing output looks like -->

Docker
<!-- Build command, image tag format, run command with env var, verification -->
To containerise the API, I first updated the last line of app.py so the app listens on 
all network interfaces (host="0.0.0.0") with debug mode turned off. Without this, the app 
only accepts connections from inside the container, so requests from the host machine fail even 
with the port mapped. I then wrote a Dockerfile based on the official python:3.11-slim image 
and added a .dockerignore to keep the virtual environment, Git history and cache files out of 
the image. Finally, I built a versioned image (system-health-dashboard:1.0.0), ran it as a 
container with APP_ENV=staging, and verified all three endpoints with curl.

commands
docker build -t system-health-dashboard:1.0.0 .
docker run -d -p 5000:5000 -e APP_ENV=staging --name health-api system-health-dashboard:1.0.0
curl http://localhost:5000/health
curl http://localhost:5000/version
curl http://localhost:5000/environment

Jenkins pipeline
<!-- Stages, how tagging works, what happens on test failure -->

Git workflow
<!-- Branch model, branch names used, PR and review link -->

Merge conflict record
<!-- See conflict log template -->

<!--| Field | Details |
| --- | --- |
| **Branches** | `feature/health-version-endpoint` and `feature/environment-version-endpoint`, 
both merged into `develop` |
| **File** | `app.py` (whole file). Both branches created `app.py` independently, so Git 
raised an add/add conflict |
| **Health branch changes** | Added the `/health` and `/version` endpoints |
| **Environment branch changes** | Added the `/environment` endpoint, which reads `APP_ENV` and 
defaults to `development` |
| **Resolution** | Used the health/version file as the base, added `import os` and 
the `/environment` route above the `if __name__ == "__main__":` block. The final file has 
all three endpoints and a single `app.run` |
| **Commands (resolve)** | `git merge`, `nano app.py`, `git add app.py`, `git commit` |
| **Commands (verify)** | `cat app.py`, `python app.py`, `curl` against `/health`, `/version` 
and `/environment` |
| **Issue found** | The first resolution left a `<<<<<<< HEAD` marker in the file. The app 
failed to start with a `SyntaxError`, so I removed the marker and committed the fix |
| **Commits** | Merge: `6dcd466` · Fix: `5e2a01f` |
| **Reference** | mthree Git 2.2 Code-Along, Steps 4–6 |

**Lesson learned:** after resolving a conflict, check for leftover markers and run the app 
before committing. Once the Jenkins test stage is in place, a broken file like this would 
fail the pipeline automatically.-->

Reflection
<!-- The brief's four reflection questions -->

AI assistance
<!-- Required by the brief if used substantially -->
