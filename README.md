System Health Dashboard API
Overview

A lightweight API that returns basic status information for engineers and automated monitoring checks. It exposes three endpoints:

Endpoint	Returns	Example response
/health	Whether the service is up, the current time and uptime	{"status": "healthy", "timestamp": "2026-10-26T22:47:29+00:00", "uptime_seconds": 1.5}
/version	The service name and application version	{"service": "system-health-dashboard", "version": "1.0.0"}
/environment	The environment the app is running in, and the host that answered	{"environment": "development", "hostname": "LAPTOP-0F4GHKAR"}

Unknown routes return a JSON error with HTTP 404: {"error": "Endpoint not found"}.

The project's focus is the delivery workflow around the API: feature branches, a reviewed pull request, automated tests, a Docker image and a Jenkins pipeline.

Prerequisites
Tool	Version used	Purpose
Git	2.x	Version control
Python	3.11 or later	Running the app and tests locally
Docker Desktop	Current	Building and running the container
Jenkins	LTS (run locally in Docker)	CI/CD pipeline
curl	Any	Verifying endpoints
Setup
bash
git clone https://github.com/letta-Lana/system-health-dashboard.git
cd system-health-dashboard

python -m venv venv
source venv/Scripts/activate     # Windows (Git Bash)
# source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt

(venv) appears in your prompt when the virtual environment is active. Activate it again in every new terminal.

Configuration

Configuration is read from environment variables, so nothing is hard-coded in the source.

Variable	Purpose	Default
APP_ENV	Environment name returned by /environment	development
APP_VERSION	Version returned by /version	1.0.0

Set them when starting the app:

bash
APP_ENV=staging APP_VERSION=1.1.0 python app.py
Running locally
bash
python app.py

The app listens on port 5000. In a second terminal, verify each endpoint:

bash
curl http://localhost:5000/health
curl http://localhost:5000/version
curl http://localhost:5000/environment

Each endpoint returns HTTP 200 with JSON. Stop the server with Ctrl+C.

Running tests

Run the full suite from the project root with the virtual environment active:

bash
python -m pytest -v

The suite in tests/test_app.py contains five tests:

Test	Checks
test_health_returns_healthy	/health returns 200 and "status": "healthy"
test_version_returns_a_version	/version returns 200 and a version key
test_environment_defaults_to_development	/environment returns development when APP_ENV is unset
test_environment_reads_app_env	/environment returns the value of APP_ENV
test_unknown_route_returns_404	An unknown route returns 404

Passing output ends with 5 passed. The tests use Flask's test client, so the server does not need to be running. pytest's built-in monkeypatch fixture sets or clears APP_ENV for a single test only.

Intentional failure: I changed the expected /health status from "healthy" to "UP", ran the suite, and confirmed pytest reported 1 failed, 4 passed. I then restored the test and confirmed all five passed.

Docker

To containerise the API, I updated the last line of app.py so the app listens on all network interfaces (host="0.0.0.0") with debug mode turned off. Without this, the app only accepts connections from inside the container, so requests from the host machine fail even with the port mapped. The Dockerfile is based on the official python:3.11-slim image and installs dependencies before copying the code, so Docker can reuse the cached dependency layer when only the code changes. The .dockerignore keeps the virtual environment, Git history, cache files and local env files out of the image.

Build a versioned image

bash
docker build -t system-health-dashboard:1.0.0 .
docker images system-health-dashboard

Run with an environment variable

bash
docker run -d -p 5000:5000 -e APP_ENV=staging --name health-api system-health-dashboard:1.0.0
docker ps

Verify all endpoints from the container

bash
curl http://localhost:5000/health
curl http://localhost:5000/version
curl http://localhost:5000/environment     # returns "staging" and the container ID as hostname

If a request fails, check docker logs health-api.

Clean up

bash
docker stop health-api
docker rm health-api
Jenkins pipeline

The Jenkinsfile defines a declarative pipeline. The job uses Pipeline script from SCM, pointing at this repository.

Stage	What it does
Checkout	checkout scm retrieves the repository and the branch configured in the job
Install	Creates a virtual environment and installs requirements.txt
Test	Runs python -m pytest -v. A failing test fails the stage and stops the pipeline
Build	docker build -t system-health-dashboard:latest .
Tag	Tags the image with the Jenkins build number: system-health-dashboard:${BUILD_NUMBER}
Health check	Runs the tagged image on port 5050 with APP_ENV=ci and curls /health up to 10 times, 2 seconds apart. Fails the build if it never returns 200
Post (always)	Removes the test container, whether the build passed or failed

Tagging: each run produces an image such as system-health-dashboard:1, so every build can be traced back to its Jenkins run.

Failure handling: when a test fails, the Test stage exits with a non-zero code. Jenkins marks the build as failed and skips Build, Tag and Health check, so a broken image is never built.

Local Jenkins setup: Jenkins runs as a Docker container with Python and the Docker CLI added, and with the host's Docker socket mounted. Because Jenkins is itself a container, the health check reaches the app through host.docker.internal rather than localhost.

Evidence

<!-- Replace with your build numbers and screenshot links -->
Successful run: build #___ (all stages green)
Failed run: build #___ (stopped at Test after the intentional failure)
Final successful run: build #___

In build #1, the first health-check attempt failed because the app was still starting, and the second attempt passed. The retry loop prevented a false failure.

Git workflow

The project follows a simplified GitFlow model:

main: reviewed, release-ready code. It only changes through a pull request from develop.
develop: integration branch. Feature branches are merged here first.
feature/<short-description>: one branch per piece of work, created from develop.

Branches used:

Branch	Work
feature/health-version-endpoint	/health and /version endpoints
feature/environment-version-endpoint	/environment endpoint reading APP_ENV
feature/tests	pytest suite and requirements.txt
feature/docker	Dockerfile and .dockerignore
feature/jenkins	Jenkinsfile

Work was planned as GitHub Issues before coding started, and commits were kept small with action-oriented messages.

Pull request: https://github.com/letta-Lana/system-health-dashboard/pull/11 (develop → main), reviewed by kpashindla29 before merging.

View the branch history with:

bash
git log --oneline --graph --all
Merge conflict record
Field	Details
Branches	feature/health-version-endpoint and feature/environment-version-endpoint, both merged into develop
File	app.py (whole file). Both branches created app.py independently, so Git raised an add/add conflict
Health branch changes	Added the /health and /version endpoints
Environment branch changes	Added the /environment endpoint, which reads APP_ENV and defaults to development
Resolution	Used the health/version file as the base, added import os and the /environment route above the if __name__ == "__main__": block. The final file has all three endpoints and a single app.run
Commands (resolve)	git merge, nano app.py, git add app.py, git commit
Commands (verify)	cat app.py, python app.py, curl against /health, /version and /environment
Issue found	The first resolution left a <<<<<<< HEAD marker in the file. The app failed to start with a SyntaxError, so I removed the marker and committed the fix
Commits	Merge: 6dcd466 · Fix: 5e2a01f
Reference	mthree Git 2.2 Code-Along, Steps 4–6

Lesson learned: after resolving a conflict, check for leftover markers and run the app before committing. With the Jenkins Test stage in place, a broken file like this now fails the pipeline automatically.

Reflection
<!-- Draft based on what happened in this project. Rewrite in your own words. -->

Which Git practice most improved the way I organised my work? Feature branches. Keeping /health + /version and /environment on separate branches meant each change was small and easy to review, and merging them showed exactly where the two pieces of work overlapped. Planning the work as issues first also gave me a clear order to follow.

Where did automation detect or prevent an error? Two places. The pytest suite caught my intentional failure, and the Jenkins Test stage stopped the pipeline before an image was built. The health-check retry loop also prevented a false failure in build #1, where the app needed a moment to start before /health responded.

What would I change before using this workflow in production?

Replace Flask's development server with a production WSGI server such as Gunicorn
Split runtime and test dependencies so pytest isn't shipped in the production image
Run the Jenkins container without -u root, and run the app container as a non-root user
Push tagged images to a registry instead of keeping them only on the build machine
Enforce branch protection on main so changes require an approved PR

Which step still depends on manual action, and how could it be automated? Starting Jenkins builds. I clicked Build Now after each push. A GitHub webhook or a multibranch pipeline could trigger builds automatically on every push and run the tests on pull requests before review. Deployment after a successful build is also manual and could become a pipeline stage.

AI assistance

I used Claude (Anthropic) during this project. I reviewed, ran and tested everything it produced, and can explain every file.

Area	What Claude did
Planning	Organised the mthree course pages into a study map and blank templates for issues, the pipeline and the README
Learning support	Explained Git branches, virtual environments, environment variables and Flask concepts; reviewed my code and pointed out errors
app.py	Wrote the /environment route after I drafted it, and an upgraded version adding the timestamp, uptime, APP_VERSION, hostname and JSON 404 handler
Documentation	Tidied the wording of the Overview, Docker section and merge conflict record, and drafted this README

I wrote the first /health and /version endpoints, set up the repository and 
branches, resolved the merge conflict, built and ran the Docker image, and 
ran the Jenkins pipeline myself.
