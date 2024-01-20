import json

def extract_ids_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    ids = [entry['id'] for entry in data]
    return ids

def save_ids_to_json(ids, output_file_path):
    with open(output_file_path, 'w') as file:
        json.dump(ids, file, indent=4)

def main():
    input_file_path = 'search.json'
    output_file_path = 'member_ids_113_118.json'

    ids = extract_ids_from_json(input_file_path)
    save_ids_to_json(ids, output_file_path)
    print(f"Extracted IDs saved to {output_file_path}")

if __name__ == "__main__":
    main()
