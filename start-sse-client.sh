#! /usr/bin/bash

cd $(dirname "$0")
sudo ENV=dev python -m sse_client.main --log-to-file --log-level=DEBUG