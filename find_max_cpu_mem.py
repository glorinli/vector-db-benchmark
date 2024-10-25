import json
import argparse

def find_max_usage(file_path, container_name):
    max_cpu = 0
    max_mem = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            if container_name in data["Name"]:
                max_cpu = max(max_cpu, float(data["CPUPerc"].replace('%', '')))
                max_mem = max(max_mem, float(data["MemUsage"].split('/')[0].replace('GiB', '').strip()))
    
    return max_cpu, max_mem

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find max CPU and Memory usage for a container.")
    parser.add_argument("file_path", type=str, help="Path to the JSONL file.")
    parser.add_argument("container_name", type=str, help="Container name to filter.")
    
    args = parser.parse_args()
    max_cpu, max_mem = find_max_usage(args.file_path, args.container_name)
    
    print(f"Max CPU: {max_cpu}%, Max Memory: {max_mem} GiB")
