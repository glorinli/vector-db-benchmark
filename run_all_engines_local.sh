#!/usr/bin/env bash

set -e

DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular"}

SERVER_HOST=${SERVER_HOST:-"localhost"}

function run_exp() {
    SERVER_PATH=$1
    ENGINE_NAME=$2
    MONITOR_PATH=$(echo "$ENGINE_NAME" | sed -e 's/[^A-Za-z0-9._-]/_/g')
    echo "Starting server ${SERVER_PATH} ..."
    nohup bash -c 'cd ./monitoring && rm -f docker.stats.jsonl && bash monitor_docker.sh' > /dev/null 2>&1 &
    bash -c "cd ./engine/servers/$SERVER_PATH ; docker compose down ; docker compose up -d"
    sleep 30
    echo 'Activate poetry'
    source $(poetry env info --path)/bin/activate
    which python
    echo 'Run experiments...'
    python3 run.py --engines "$ENGINE_NAME" --datasets "${DATASETS}" --host "$SERVER_HOST" --skip-search
    echo 'Shutdown server...'
    bash -c "cd ./engine/servers/$SERVER_PATH ; docker compose down"
    bash -c "cd ./monitoring && mkdir -p results && mv docker.stats.jsonl ./results/${MONITOR_PATH}-docker.stats.jsonl"
}


run_exp "qdrant-single-node" 'qdrant-m-16-ef-128'
# run_exp "weaviate-single-node" 'weaviate-m-*'
# run_exp "milvus-single-node" 'milvus-m-*'
# run_exp "qdrant-single-node" 'qdrant-rps-m-*'


# run_exp "elasticsearch-single-node" 'elastic-m-*'
# run_exp "redis-single-node" 'redis-m-*'

# Extra: qdrant configured to tune RPS

