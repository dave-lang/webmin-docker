# Use the latest Ubuntu image as a parent
FROM cruizba/ubuntu-dind:focal-27.3.1

ENV DEBIAN_FRONTEND=noninteractive TZ=Australia/Brisbane

# Initial updates and install core utilities
# net-tools = ifconfig, ip
RUN apt-get update -qq -y && \
    apt-get upgrade -y && \
    apt-get install -y \
       gnupg2 \
       net-tools

# Install Webmin
RUN echo root:password | chpasswd && \
    echo "Acquire::GzipIndexes \"false\"; Acquire::CompressionTypes::Order:: \"gz\";" >/etc/apt/apt.conf.d/docker-gzip-indexes && \
    # update-locale LANG=C.UTF-8 && \
    echo deb https://download.webmin.com/download/repository sarge contrib >> /etc/apt/sources.list && \
    wget http://www.webmin.com/jcameron-key.asc && \
    apt-key add jcameron-key.asc && \
    apt-get update && \
    apt-get install -y webmin && \
    # apt-get clean && \
    echo "$(cat /etc/webmin/webmin.acl) docker" > /etc/webmin/webmin.acl && \
    mkdir /etc/webmin/docker && chmod 755 /etc/webmin/docker

# Last 2 line adds docker module to webmin's acl, for easier development and creates the config dir.
# Also requires the volume & config in the compose

EXPOSE 10000
ENV LC_ALL C.UTF-8

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
