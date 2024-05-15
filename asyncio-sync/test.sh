#!/bin/bash
set -eo pipefail
echo using "$1"

if [[ "$1" == "sync" ]]; then
    ENDPOINT="sync-sleep"
elif [[ "$1" == "async" ]]; then
    ENDPOINT="async-sleep"
else
    echo "either sync or async accepted."
    exit 1
fi

curl localhost:8000/$ENDPOINT &
# this is here to stop a race on which request arrives first.
sleep 0.1
curl localhost:8000/return && echo

wait

echo
echo done
