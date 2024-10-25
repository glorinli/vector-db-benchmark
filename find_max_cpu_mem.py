import json

def find_max_usage(file_path, container_name):
    max_cpu = 0
    max_mem = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data["Name"] == container_name:
                max_cpu = max(max_cpu, float(data["CPUPerc"].replace('%', '')))
                max_mem = max(max_mem, float(data["MemUsage"].split('/')[0].replace('GiB', '').strip()))
    
    return max_cpu, max_mem

file_path = './monitoring/results/opensearch-faiss-m-32-ef-256-search-ef-256-p-200-docker.stats.jsonl'
container_name = 'opensearch-single-node-opensearch-1'

max_cpu, max_mem = find_max_usage(file_path, container_name)
print(f"Max CPU: {max_cpu}%, Max Memory: {max_mem} GiB")
