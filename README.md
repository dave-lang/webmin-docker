# Webmin module for basic docker tasks

Created to manage a local Docker install for a home server. Allows listing of containers; viewing basic container perf stats and docker state; and starting/stopping/restarting containers.

It uses the Docker CLI and abuses the `--format {{}}` arg for output parsing.

Currently translated to English, Italian and Polish.

## Install

The fastest way to install is to follow the "Http URL" method (https://webmin.com/docs/modules/webmin-configuration/#installing) and the latest `docker.tar.gz` release package from https://github.com/dave-lang/webmin-docker/releases.

Alternatively you can download and install it directly or build manually, the packaging steps are in the GitHub action in the repo.

Once installed a new option 'Docker Containers' will appear in the menu under 'Servers'.
![image](https://github.com/user-attachments/assets/e4eeda35-1800-48d5-8b15-b498f7305311)

## Contibuting

Improvements or fixes are welcome, please raise it under issues and link to your branch.

## Development

Docker configuration has been setup to allow easier development.

This environment has Webmin and Docker already installed, along with a very basic Ubuntu 18 docker config ready to start in the container (Docker in Docker).

The plugin is installed in the Webmin environment via shared folder, changes will appear immediately.

1. `cd tools`
2. `docker-compose up -d` to run docker compose as daemon
3. Open http://localhost:10000 to access the webmin console
4. Login is `root` + `password`, this can be adjusted in the Dockerfile

To burn and recreate the environment use `docker-compose down -v`

Use `docker exec -it webmin_master /bin/bash` to get a SSH console.

Docker will not be running by default, use `dockerd` to run it, Ctrl+C to stop. Start the internal container via:
1. `cd dind`
2. `docker-compose up -d`
