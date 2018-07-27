#!/bin/sh
if [ -z "$1" ]; then
  echo "No hostname specified"
  echo "usage: ansible-ssh [hostname] [user=jsnow]";
  exit 1;
fi

if [ -z "$2" ]; then
  USER="jsnow"
else
  USER="$2"
fi

IPV4S=".ipv4.json"

if [ ! -f "$IPV4S" ]; then
    touch "$IPV4S" &&
    python2.7 inventory/openstack.py --list |
    jq -r "[._meta.hostvars | \
            to_entries[] | \
            {id: .key, \
             hostname: .value.openstack.name, \
             ipv4: .value.ansible_ssh_host}]" |
    tee $IPV4S
fi

HOST=$(cat $IPV4S |
       jq -r --arg HOSTNAME "$1" '.[] | select(.hostname == $HOSTNAME) | .ipv4')

if [ -z "$HOST" ]; then
    echo "No such hostname '$1'"
    exit 2
fi

ssh -o "StrictHostKeyChecking=no" \
    -o "UserKnownHostsFile /dev/null" \
    -o "LogLevel ERROR" \
    -t $USER@$HOST bash
