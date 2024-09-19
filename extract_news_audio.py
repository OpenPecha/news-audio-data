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

def prepare_news_data_with_audio(news_info):
    """Prepares a structure for news data with audio.

    Args:
        news_info (dict): The news information dictionary containing all relevant data.

    Returns:
        dict: A dictionary containing the title, body text, audio URL, and metadata.
    """
    news_data_with_audio = {
        'title': news_info['data']['title'],
        'body_text':  "\n".join(news_info['data']['body'].get('Text', [])),
        'audio_url':  news_info['data']['body'].get('Audio', ''),
        'metadata': {
            'published_date': news_info['data']['meta_data'].get('Date'),
            'author': news_info['data']['meta_data'].get('Author'),
            'category': news_info['data']['meta_data'].get('Tags', []),
            'news_url': news_info['data']['meta_data'].get('URL')
        }
    }
    return news_data_with_audio

def get_news_with_audio(news_data, output_dir):
    """Filters news with audio

    Args:
        news_data (dict): news dataset

    Returns:
        dict: dict of news dataset with audio
    """
    news_data_with_audio = {}
    for news_id, news_info in news_data.items():
        if has_news_audio(news_info):
            news_data_with_audio[news_id] = prepare_news_data_with_audio(news_info)
    return news_data_with_audio

def save_json_file(article_data, article_id, output_dir):
    """Saves content to a json file

    Args:
        article_data (dict): The article data containing audio URL, body text, and metadata.
        article_id (str): The ID of the article, used for naming the directory.
        output_dir (Path): The directory where the article data will be saved.
    """
    article_dir = output_dir / article_id
    article_dir.mkdir(parents=True, exist_ok=True)

    # Get the first audio URL if it is a list
    audio_url = article_data['audio_url']
    if isinstance(audio_url, list) and audio_url:
        audio_url = audio_url[0]  # Use the first audio URL

    # Now you can safely use split
    audio_file_name = audio_url.split('/')[-1]  # Extracts the audio file name from the URL

    with open(article_dir / audio_file_name, 'w', encoding='utf-8') as audio_file:
        audio_file.write(audio_url)  # Simulate saving the audio file

    # Save body text
    with open(article_dir / 'news_text.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(article_data['body_text'])

    # Save metadata
    with open(article_dir / 'metadata.json', 'w', encoding='utf-8') as meta_file:
        json.dump(article_data['metadata'], meta_file, ensure_ascii=False, indent=4)

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
            news_data_with_audio = get_news_with_audio(news_data, output_dir)  
            
            # Save the filtered dataset to a new file
            for article_id, article_data in news_data_with_audio.items():
                save_json_file(article_data, article_id, output_dir) 
