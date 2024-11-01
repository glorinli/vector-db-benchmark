import os
import json

if __name__ == '__main__':
    # Traverse json files in ./results dir
    # Read the content of each file

    search_result_file_count = 0
    upload_result_file_count = 0

    sum_of_fields = {}

    for filename in os.listdir('./results'):
        if filename.endswith('.json'):
            with open(f'./results/{filename}', 'r') as f:
                content = json.load(f)
                results = content['results']

                if 'upload_time' in results:
                    upload_result_file_count += 1
                    continue

                search_result_file_count += 1

                for key, value in results.items():
                    # Only handle number values
                    if isinstance(value, (int, float)):
                        if key not in sum_of_fields:
                            sum_of_fields[key] = 0
                        sum_of_fields[key] += value

    # Print average
    for key, value in sum_of_fields.items():
        print(f'Average {key}: {value / search_result_file_count}')

