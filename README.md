# Webmin module for basic docker tasks

Created to manage a local Docker install for a home server. Allows listing of containers; viewing basic container perf stats and docker state; and starting/stopping/restarting containers.

It uses the Docker CLI and abuses the `--format {{}}` arg for output parsing.

## Development

Docker configuration has been setup to allow easier development.

This environment has webmin and docker already installed, along with a very basic Ubuntu 18 docker config ready to start in the container (Docker in Docker).

1. `cd tools`
2. `docker-compose up -d` to run docker compose as daemon
3. Open http://localhost:10000 to access the webmin console

Use `docker exec -it webmin_master /bin/bash` to get a SSH console.

Docker will not be running by default, use `dockerd` to run it, Ctrl+C to stop.

To setup the test DinD container
