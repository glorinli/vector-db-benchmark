#!/usr/bin/env bash

set -e

DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular"}
#DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular-with-schema"}

SERVER_HOST=${SERVER_HOST:-"10.74.148.41"}

SERVER_USERNAME=${SERVER_USERNAME:-"root"}

export MOCK_PAYLOAD="true"

function run_exp() {
    SERVER_PATH=$1
    ENGINE_NAME=$2
    MONITOR_PATH=$(echo "$ENGINE_NAME" | sed -e 's/[^A-Za-z0-9._-]/_/g')
    ssh "${SERVER_USERNAME}@${SERVER_HOST}" "nohup bash -c 'cd /projects/glorin.li/code/vector-db-benchmark/monitoring && rm -f docker.stats.jsonl && bash monitor_docker.sh' > /dev/null 2>&1 &"
    ssh -t "${SERVER_USERNAME}@${SERVER_HOST}" "cd /projects/glorin.li/code/vector-db-benchmark/engine/servers/$SERVER_PATH ; docker compose down ; docker compose up -d"
    sleep 10
    python3 run.py --engines "$ENGINE_NAME" --datasets "${DATASETS}" --host "$SERVER_HOST" --skip-search
#    ssh -t "${SERVER_USERNAME}@${SERVER_HOST}" "cd /projects/glorin.li/code/vector-db-benchmark/engine/servers/$SERVER_PATH ; docker compose down"
    ssh -t "${SERVER_USERNAME}@${SERVER_HOST}" "cd /projects/glorin.li/code/vector-db-benchmark/monitoring && mkdir -p results && mv docker.stats.jsonl ./results/${MONITOR_PATH}-docker.stats.jsonl"

    # Pull results from server
    scp "${SERVER_USERNAME}@${SERVER_HOST}:/projects/glorin.li/code/vector-db-benchmark/monitoring/results/${MONITOR_PATH}-docker.stats.jsonl" "./monitoring/results/${MONITOR_PATH}-docker.stats.jsonl"
}

run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256'
#run_exp "qdrant-single-node" 'qdrant-m-*'
#run_exp "weaviate-single-node" 'weaviate-m-*'
#run_exp "milvus-single-node" 'milvus-m-*'
#run_exp "qdrant-single-node" 'qdrant-rps-m-*'


# run_exp "elasticsearch-single-node" 'elastic-m-*'
# run_exp "redis-single-node" 'redis-m-*'

#run_exp "opensearch-single-node" 'opensearch-m-16-ef-128'

