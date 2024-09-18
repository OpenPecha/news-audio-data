import json
from pathlib import Path

def read_json_file(file_path):
    """Reads a json file and returns the content

    Args:
        file_path (str): file path to the json file

    Returns:
        dict: json file content
    """
    json_file_content = None
    # Write read json file code here
    return json_file_content

def has_news_audio(news_info):
    """Checks if news has audio

    Args:
        news_info (dict): news information

    Returns:
        bool: True if news has audio, False otherwise
    """
    has_news_audio_bool = False
    # Check if audio key exists in news_info
    return has_news_audio_bool

def get_news_with_audio(news_data):
    """Filters news with audio

    Args:
        news_data (dict): news dataset

    Returns:
        dict: dict of news dataset with audio
    """
    news_data_with_audio = {}
    for news_id, news_info in zip(news_data.items()):
        if has_news_audio(news_info):
            news_data_with_audio[news_id] = news_info
    return news_data_with_audio

def save_json_file(file_path, content):
    """Saves content to a json file

    Args:
        file_path (str): file path to save the content
        content (dict): content to save
    """
    # Write save json file code here
    pass


if __name__ == "__main__":
    news_house = ''
    news_dataset_dir  = Path(f'./data/{news_house}/news_dataset')
    news_dataset_file_paths = list(news_dataset_dir.iterdir())
    news_dataset_file_paths.sort()
    for news_dataset_file_path in news_dataset_file_paths:
        news_data = read_json_file(news_dataset_file_path)
        news_data_with_audio = get_news_with_audio(news_data)
        news_data_with_audio_file_path = Path(f'./data/{news_house}/news_dataset_with_audio/{news_dataset_file_path.name}')
        save_json_file(news_data_with_audio_file_path, news_data_with_audio)
        