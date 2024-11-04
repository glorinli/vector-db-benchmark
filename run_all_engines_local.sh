#!/usr/bin/env bash

set -e

# DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular"}
DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular-with-schema-1+2+1"}
# DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular-with-schema-1"}
# DATASETS=${DATASETS:-"dbpedia-openai-100K-1536-angular-with-schema-9"}

SERVER_HOST=${SERVER_HOST:-"localhost"}

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

export FILTER_CONFIG="filter-1-1x24"
export QDRANT_VERSION="v1.12.1"
# export MAX_ITEMS_PER_SEC="500"

# Clear
read -p "Clear results? (yes/no): " clear_results
if [ "$clear_results" == "yes" ]; then
    rm ./monitoring/results/*.jsonl || true
    rm ./results/*.json || true
fi

# STREAMING_TEST="true"

function run_exp() {
    SERVER_PATH=$1
    ENGINE_NAME=$2
    MONITOR_PATH=$(echo "$ENGINE_NAME" | sed -e 's/[^A-Za-z0-9._-]/_/g')
    echo "Starting server ${SERVER_PATH} ..."
    nohup bash -c 'cd ./monitoring && rm -f docker.stats.jsonl && bash monitor_docker.sh' > /dev/null 2>&1 &

    if [ "$restart_server" == "yes" ]; then
        echo "Restarting server..."
        bash -c "cd ./engine/servers/$SERVER_PATH ; docker compose down ; docker compose up -d"
        sleep 30
    fi

    echo 'Activate poetry'
    source $(poetry env info --path)/bin/activate
    which python
    echo 'Run experiments...'

    if [ "$STREAMING_TEST" == "true" ]; then
        # Run two python scripts in parallel, and wait for both to finish
        python3 run.py --engines "$ENGINE_NAME" --datasets "${DATASETS}" --host "$SERVER_HOST" $extra_args &
        python3 auto_search_after_uploaded.py --engine-name "$ENGINE_NAME" --dataset-name "${DATASETS}" --server-host "$SERVER_HOST" &
        wait
    else
        python3 run.py --engines "$ENGINE_NAME" --datasets "${DATASETS}" --host "$SERVER_HOST" $extra_args
    fi

    echo 'Shutdown server...'
    # bash -c "cd ./engine/servers/$SERVER_PATH ; docker compose down"
    bash -c "cd ./monitoring && mkdir -p results && mv docker.stats.jsonl ./results/${MONITOR_PATH}-docker.stats.jsonl"

    python3 find_max_cpu_mem.py ./monitoring/results/${MONITOR_PATH}-docker.stats.jsonl $SERVER_PATH

    if [ "$STREAMING_TEST" == "true" ]; then
        python3 result_analyze.py
    fi
}


# run_exp "qdrant-single-node" 'qdrant-m-16-ef-128'
# run_exp "qdrant-single-node" 'qdrant-m-32-ef-256-scalar-quantization'
# run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256'
# run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256-tenant'
# run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256-scalar-quantization'
# run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256-scalar-quantization-tenant'
# run_exp "qdrant-single-node" 'qdrant-m-32-ef-256-batch-128'
# run_exp "weaviate-single-node" 'weaviate-m-*'
# run_exp "milvus-single-node" 'milvus-m-*'
# run_exp "qdrant-single-node" 'qdrant-rps-m-*'

# run_exp "qdrant-single-node" 'qdrant-m-16-ef-128-search-ef-128-p-500'
# run_exp "qdrant-single-node" 'qdrant-m-32-ef-256-search-ef-256-p-100'
run_exp "qdrant-single-node" 'qdrant-payload-m-32-ef-256-search-ef-256-p-200-mmap'



# run_exp "elasticsearch-single-node" 'elastic-m-*'
# run_exp "redis-single-node" 'redis-m-*'

# Extra: qdrant configured to tune RPS
# run_exp "opensearch-single-node" 'opensearch-m-16-ef-128'
# run_exp "opensearch-single-node" 'opensearch-m-32-ef-256'
# run_exp "opensearch-single-node" 'opensearch-m-32-ef-256-scalar-quantization'
# run_exp "opensearch-single-node" 'opensearch-m-32-ef-256-batch-128'
# run_exp "opensearch-single-node" 'opensearch-m-16-ef-128-search-ef-128-p-500'
# run_exp "opensearch-single-node" 'opensearch-m-32-ef-256-search-ef-256-p-200'
# run_exp "opensearch-single-node" 'opensearch-faiss-m-32-ef-256-search-ef-256-p-100'
# run_exp "opensearch-single-node" 'opensearch-faiss-m-32-ef-256-search-ef-256-p-200'
# run_exp "opensearch-single-node" 'opensearch-faiss-hnsw-innerproduct-m-32-ef-256-search-ef-256-p-100'
# run_exp "opensearch-single-node" 'opensearch-faiss-ivf-l2-m-32-ef-256-search-ef-256-p-200'
# run_exp "opensearch-single-node" 'opensearch-nmsli-hnsw-cosine-m-32-ef-256-search-ef-256-p-200'
# run_exp "opensearch-single-node" 'opensearch-nmsli-hnsw-l2-m-32-ef-256-search-ef-256-p-100'
# run_exp "opensearch-single-node" 'opensearch-nmsli-hnsw-l2-m-32-ef-256-search-ef-256-p-200'
# run_exp "opensearch-single-node" 'opensearch-nmsli-hnsw-innerproduct-m-32-ef-256-search-ef-256-p-100'
# run_exp "opensearch-single-node" 'opensearch-nmsli-hnsw-innerproduct-m-32-ef-256-search-ef-256-p-200'
# run_exp "opensearch-single-node" 'opensearch-faiss-quantization-m-32-ef-256-search-ef-256-p-100'
# run_exp "opensearch-single-node" 'opensearch-faiss-hnsw-innerproduct-quantization-m-32-ef-256-search-ef-256-p-100'