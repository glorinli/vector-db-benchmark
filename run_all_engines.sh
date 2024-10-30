#!/usr/bin/env bash

set -e

#DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular"}
DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular-with-schema"}

SERVER_HOST=${SERVER_HOST:-"10.74.148.41"}

SERVER_USERNAME=${SERVER_USERNAME:-"root"}

export FILTER_CONFIG="one_filter"

# Wait user input yes/no to decide whether to skip search
read -p "Skip search? (yes/no): " skip_search

extra_args=""
if [ "$skip_search" == "yes" ]; then
    extra_args="--skip-search"
fi

read -p "Skip upload? (yes/no): " skip_upload

if [ "$skip_upload" == "yes" ]; then
    extra_args="$extra_args --skip-upload"
fi

read -p "Restart server? (yes/no): " restart_server

function run_exp() {
    SERVER_PATH=$1
    ENGINE_NAME=$2
    MONITOR_PATH=$(echo "$ENGINE_NAME" | sed -e 's/[^A-Za-z0-9._-]/_/g')
    ssh "${SERVER_USERNAME}@${SERVER_HOST}" "nohup bash -c 'cd /projects/glorin.li/code/vector-db-benchmark/monitoring && rm -f docker.stats.jsonl && bash monitor_docker.sh' > /dev/null 2>&1 &"

    if [ "$restart_server" == "yes" ]; then
        ssh -t "${SERVER_USERNAME}@${SERVER_HOST}" "cd /projects/glorin.li/code/vector-db-benchmark/engine/servers/$SERVER_PATH ; docker compose down ; docker compose up -d"
        sleep 10
    fi

    python3 run.py --engines "$ENGINE_NAME" --datasets "${DATASETS}" --host "$SERVER_HOST" $extra_args
#    ssh -t "${SERVER_USERNAME}@${SERVER_HOST}" "cd /projects/glorin.li/code/vector-db-benchmark/engine/servers/$SERVER_PATH ; docker compose down"
    ssh -t "${SERVER_USERNAME}@${SERVER_HOST}" "cd /projects/glorin.li/code/vector-db-benchmark/monitoring && mkdir -p results && mv docker.stats.jsonl ./results/${MONITOR_PATH}-docker.stats.jsonl"

    # Pull results from server
    scp "${SERVER_USERNAME}@${SERVER_HOST}:/projects/glorin.li/code/vector-db-benchmark/monitoring/results/${MONITOR_PATH}-docker.stats.jsonl" "./monitoring/results/${MONITOR_PATH}-docker.stats.jsonl"
}

#run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256'
#run_exp "qdrant-single-node" 'qdrant-m-*'
#run_exp "weaviate-single-node" 'weaviate-m-*'
#run_exp "milvus-single-node" 'milvus-m-*'
#run_exp "qdrant-single-node" 'qdrant-rps-m-*'

run_exp "qdrant-single-node" 'qdrant-m-32-ef-256-search-ef-256-p-1'


# run_exp "elasticsearch-single-node" 'elastic-m-*'
# run_exp "redis-single-node" 'redis-m-*'

#run_exp "opensearch-single-node" 'opensearch-m-16-ef-128'

