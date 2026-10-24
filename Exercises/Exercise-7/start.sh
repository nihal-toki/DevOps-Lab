#!/bin/sh
set -eu
cd "$(dirname "$0")"
if docker container inspect exercise7-jenkins >/dev/null 2>&1; then
  docker start exercise7-jenkins
else
  docker volume create jenkins_home >/dev/null
  docker compose up -d
fi
printf '%s\n' 'Open http://localhost:8080/ and use the setup wizard for a new installation.'
