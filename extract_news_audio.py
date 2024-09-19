import json
from pathlib import Path

def read_json_file(file_path):
    """Reads a json file and returns the content

    Args:
        file_path (str): file path to the json file

    Returns:
        dict: json file content
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        json_file_content = json.load(file)  # Load and return the content of the JSON file
    return json_file_content

def has_news_audio(news_info):
    """Checks if news has audio

    Args:
        news_info (dict): news information

    Returns:
        bool: True if news has audio, False otherwise
    """
    news_data = news_info.get('data', {})
    news_body = news_data.get('body', {})
    news_audio_url = news_body.get('Audio', '') # Get the audio URL if it exists

    if news_audio_url:
        return True
    else:
        return False # Check if audio key exists in news_info

def get_news_with_audio(news_data):
    """Filters news with audio

    Args:
        news_data (dict): news dataset

    Returns:
        dict: dict of news dataset with audio
    """
    news_data_with_audio = {}
    # Iterate through the news dataset and filter out items with audio
    for news_id, news_info in news_data.items():
        if has_news_audio(news_info):
            news_data_with_audio[news_id] = news_info
    return news_data_with_audio

def save_json_file(file_path, content):
    """Saves content to a json file

    Args:
        file_path (str): file path to save the content
        content (dict): content to save
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)  # Save the content passed as argument
        print(f"JSON file saved successfully at {file_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


if __name__ == "__main__":
    news_houses = ['VOT', 'VOA', 'RFA']
    for news_house in news_houses:
        news_dataset_dir = Path(f'./data/{news_house}/news_dataset')
        
        # Create output directory if it doesn't exist
        output_dir = Path(f'./data/{news_house}/news_dataset_with_audio')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all JSON file paths from the dataset directory
        news_dataset_file_paths = list(news_dataset_dir.iterdir())
        news_dataset_file_paths.sort()
        
        for news_dataset_file_path in news_dataset_file_paths:
            # Read each JSON file
            news_data = read_json_file(news_dataset_file_path)
            
            # Filter the news data for entries with audio
            news_data_with_audio = get_news_with_audio(news_data)
            
            # Save the filtered dataset to a new file
            news_data_with_audio_file_path = output_dir / news_dataset_file_path.name
            save_json_file(news_data_with_audio_file_path, news_data_with_audio)