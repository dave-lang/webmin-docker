# Use the latest Ubuntu image as a parent
FROM docker:27-dind-rootless

USER root

# Install Webmin on DIND container
RUN set -eux; \
    echo "root:root" | chpasswd && \
    apk add perl perl-net-ssleay expect

COPY webmin.exp /

WORKDIR /opt
   
RUN set -eux; \
    wget -O - https://github.com/webmin/webmin/archive/refs/tags/2.202.tar.gz | tar -xzf - && \
    mv webmin-2.202 webmin && \
    /usr/bin/expect /webmin.exp && \
    echo "$(cat /etc/webmin/webmin.acl) docker" > /etc/webmin/webmin.acl && \
    mkdir /etc/webmin/docker
    
# Last 2 line adds docker module to webmin's acl, for easier development and creates the config dir.
# Also requires the volume & config in the compose file

EXPOSE 10000

ENV LC_ALL C.UTF-8

WORKDIR /home


#USER rootless