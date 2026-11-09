# Adds the Docker Compose plugin to the Jenkins image used in Mini Project 1.
#
# That image already has the Docker CLI (and the host's Docker socket is mounted), but the delivery
# pipeline deploys with "docker compose", which the image did not include.
#
# Build it on top of your existing Jenkins image:
#   docker build -t jenkins-local:compose -f jenkins/Dockerfile --build-arg BASE=jenkins-local .
# Then recreate the Jenkins container from jenkins-local:compose with the same volume, ports and
# Docker socket mount as before. Check with:  docker exec <jenkins-container> docker compose version
ARG BASE=jenkins-local
FROM ${BASE}

# The Mini Project 1 image runs as root (it needs the Docker socket)
USER root

ARG COMPOSE_VERSION=v2.34.0
RUN mkdir -p /usr/local/lib/docker/cli-plugins \
 && curl -fsSL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
      -o /usr/local/lib/docker/cli-plugins/docker-compose \
 && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose \
 && docker compose version
