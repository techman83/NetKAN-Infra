#!/bin/bash

# Indexer
docker tag "kspckan/netkan" "kspckan/netkan:latest"
docker push "kspckan/netkan:latest"

# Legacy Webhooks
docker pull "kspckan/webhooks" || true
docker build webhooks/. -t kspckan/webhooks
docker tag "kspckan/webhooks" "kspckan/webhooks:latest"
docker push "kspckan/webhooks:latest"

# Webhooks Proxy
docker pull "kspckan/webhooks-proxy" || true
docker build nginx/. -t kspckan/webhooks-proxy
docker tag "kspckan/webhooks-proxy" "kspckan/webhooks-proxy:latest"
docker push "kspckan/webhooks-proxy:latest"
