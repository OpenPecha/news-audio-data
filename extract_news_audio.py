import json
from pathlib import Path
from tqdm import tqdm

def read_json_file(file_path):
    """Reads all JSON files from a directory and concatenates their content."""
    json_file_content = ""
    file_paths = list(Path(file_path).iterdir())  
    for file in tqdm(file_paths):
        if file.suffix == '.json':  
            with open(file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)  
            json_file_content += json.dumps(json_data, indent=4) + "\n" 
    return json_file_content

def get_news_with_audio(news_data):
    news_with_audio = []
    for news_data in news_with_audio:

if __name__ == "__main__":
    file_path = Path('./data/input/')
    json_file_content = read_json_file(file_path)
    print(json_file_content)