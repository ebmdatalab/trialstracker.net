#!/bin/bash

set -e

nginxconf=$1/trialstracker.net/deploy/nginx-$2

if [ ! -f $nginxconf ]; then
    echo "Unable to find $nginxconf!"
    exit 1
fi

ln -sf $nginxconf /etc/nginx/sites-enabled/$2
