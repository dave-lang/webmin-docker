#!/bin/bash

# Start docker
start-docker.sh

# Your commands go here
sed -i 's;ssl=1;ssl=0;' /etc/webmin/miniserv.conf
# systemctl enable cron
service webmin start
tail -f /dev/null
