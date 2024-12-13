# Webmin module for basic docker tasks

Created to manage a local Docker install for a home server. Current supports:
* Listing of current containers
* Starting, stopped and restarting containers
* Viewing docker system info
* View, automatically refresh and filter container logs
* View container properties
* 2 new monitor types for [System and server status](https://webmin.com/docs/modules/system-and-server-status/) - 'Docker Up' &amp; 'Docker Container Up'

Currently translated to English, Italian and Polish. UI is responsive across all device sizes.

If you're after a full Docker web interface you should consider https://www.portainer.io or https://yacht.sh.

## How does it work?
It uses the Docker CLI and abuses the `--format {{}}` arg for output parsing. This should work for normal installs of Docker and Rootless Docker installs where the webmin user has an appropriate Docker context and permissions applied (see [Rootless Docker](#rootless-docker)).

For monitors checks, `docker info` is used to get the current Docker status to avoid complexities in determining how Docker is set to startup and run. Container health is checked via `docker container inspect`.

## Install
The fastest way to install is to follow the "Http URL" method (https://webmin.com/docs/modules/webmin-configuration/#installing) and use the latest release package using [https://github.com/dave-lang/webmin-docker/releases/latest/download/docker.wbm.gz](https://github.com/dave-lang/webmin-docker/releases/latest/download/docker.wbm.gz).

Alternatively you can download and install it directly from the [releases page](https://github.com/dave-lang/webmin-docker/releases) or it build manually, the packaging steps are in the GitHub action in the repo.

Once installed:
- 'View docker containers' will appear in the menu under 'Servers'
  - If you are using an alternative context for Docker, set this under the module configuration link in the top left of "View docker containers"
- 'Docker Up' &amp; 'Docker Container Up' will appear in the monitors that can be configured under 'Tools' &gt; 'System and server status'

## Rootless Docker

Experimental rootless docker support has been added via [docker contexts](https://docs.docker.com/engine/manage-resources/contexts/). To use this module with rootless docker:
- Ensure you have a [context setup](https://docs.docker.com/engine/manage-resources/contexts/#create-a-new-context), you can do this via:
    - Open a terminal as the user rootless dockerd runs as
    - Run `id -u` to check the current user id
    - Check the docker.sock file path matches the user id, you can see the running service using `ps -al`
    - Run `docker context create rootless --docker "host=unix:///run/user/$(id -u)/docker.sock"`
    - If you want to always use this context, run `docker context use rootless`
- If you didn't change the docker context via command:
    - Once created, in the module screen click either 'Module config' or the cog icon to the left of the header
    - Set the context override to match your new context, e.g. `rootless`

## Functionality

**Container listing/actions**

<img width="480" alt="Screenshot showing container listing" src="https://github.com/user-attachments/assets/58de37c1-2f8b-42d9-9b49-ea9f541f9e53">

**Container inspection and logs**

<img width="480" alt="Screenshot showing container info" src="https://github.com/user-attachments/assets/940c98c8-fe8d-442c-acc5-9757a3ff4102">

<img width="480" alt="Screenshot showing container logs" src="https://github.com/user-attachments/assets/17bdeec8-c285-41bc-a6d1-3ddcffd34e36">

**Host docker information**

<img width="480" alt="Screenshot showing docker info display" src="https://github.com/user-attachments/assets/d059e89b-8f29-4ee1-b0dc-5caac3d3d8bc">

**Monitors**

<img width="480" alt="Screenshot showing monitor support options" src="https://github.com/user-attachments/assets/b50d10ae-de5b-4329-8d49-b13e6efae09c">

## Contributing

Improvements or fixes are welcome, please raise it under issues and link to your branch.

## Development

Docker configuration has been setup to allow easier development.

The development environment creates 2 containers:
- webmin_master - Webmin on focal ubuntu with docker & webmin auto start, available on port 10000 on the host
- docker_dd - DIND container with rootless docker and webmin, available on port 20000 on the host (DOES NOT AUTO START). Very hacky.

### Setup
1. `cd tools`
1. `docker-compose up -d` to run docker compose as daemon
1. Open http://localhost:10000 to access the webmin console for docker on Ubuntu
1. If you want to test rootless docker, run `docker exec -it --user root:root docker_dd  /etc/webmin/start`
1. Open http://localhost:20000 to access the webmin console for rootless docker
1. Login on both envs is `root` + `password`, this can be adjusted in the Dockerfile
1. The config file will not automatically be loaded due to locking issues, you will need to run:
    1. `docker exec -it --user root:root webmin_master sh -c 'cp /usr/share/webmin/docker/config /etc/webmin/docker'`
    1. `docker exec -it --user root:root docker_dd sh -c 'cp /usr/local/webmin/docker/config /etc/webmin/docker'`

To burn and recreate the environment use `docker-compose down -v`

#### webmin_master
This environment has Webmin and Docker already installed, along with a very basic docker config ready to start in the container (Docker in Docker in Docker?).

The plugin is installed in the Webmin environment via shared folder, changes will appear immediately. This is done via:
- Sharing the ./docker directory into webmin directory using Docker volume (see docker-compose.yml)
- Adding the ACL permission for the module via the Dockerfile

Use `docker exec -it webmin_master /bin/bash` to get a SSH console.

Start the internal container via:
1. `cd dind`
2. `docker-compose up -d`

#### docker_dd

Hacky webmin on DIND rootless container to allow for rootless docker testing. Webmin doesn't auto start, you will need to open a terminal and:
- `docker exec -it --user root:root docker_dd  /etc/webmin/start`
- To setup a docker context for testing:
    - `docker exec -it docker_dd /bin/sh`
    - `docker context create rootless --docker "host=unix:///run/user/$(id -u)/docker.sock"`
    - In the webmin module conf, change to use the rootless context or run `docker context use rootless`

To start a test container
1. `cd /home/dind`
2. `docker-compose --context rootless up -d`

Use `docker exec -it docker_dd /bin/sh` to get a console.
