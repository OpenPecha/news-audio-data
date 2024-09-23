import json
import requests
import subprocess

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
    news_audio_url = news_body.get('Audio', '')  # Get the audio URL if it exists

    return bool(news_audio_url)

def prepare_news_data_with_audio(news_info):
    """Prepares a structure for news data with audio.

    Args:
        news_info (dict): The news information dictionary containing all relevant data.

    Returns:
        dict: A dictionary containing the title, body text, audio URL, and metadata.
    """
    news_data_with_audio = {
        'title': news_info['data']['title'],
        'body_text': "\n".join(news_info['data']['body'].get('Text', [])),
        'audio_url': news_info['data']['body'].get('Audio', ''),
        'metadata': {
            'published_date': news_info['data']['meta_data'].get('Date'),
            'author': news_info['data']['meta_data'].get('Author'),
            'category': news_info['data']['meta_data'].get('Tags', []),
            'news_url': news_info['data']['meta_data'].get('URL')
        }
    }
    return news_data_with_audio

def get_news_with_audio(news_data):
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
   

def is_stream(file_name):
    """The function checks if the file is a stream file

    Args:
        file_name (str): name of the file
    """
    pass

def is_mp3(file_name):
    pass

def download_stream_file(url, dest_path):
    """Downloads a stream file

    Args:
        url (str): url of the file
        dest_path (str): destination path to save the file

    Returns:
        str: destination path of the file
    """
    subprocess.run(["curl", "-o", dest_path, url])
    return dest_path

def download_mp3_file(url, dest_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download the file: {url}, status code: {response.status_code}")

def save_body_text(article_data, article_dir):
    with open(article_dir / 'news_text.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(article_data['body_text'])
    pass

def save_metadata(article_data, article_dir):
    with open(article_dir / 'metadata.json', 'w', encoding='utf-8') as meta_file:
        json.dump(article_data['metadata'], meta_file, ensure_ascii=False, indent=4)
    pass

def save_news_file(article_data, article_id, output_dir):
    """Saves content to a json file

    Args:
        article_data (dict): The article data containing audio URL, body text, and metadata.
        article_id (str): The ID of the article, used for naming the directory.
        output_dir (Path): The directory where the article data will be saved.
    """
    article_dir = output_dir / article_id
    article_dir.mkdir(parents=True, exist_ok=True)

    # Check if audio URL is valid
    audio_url = article_data['audio_url']
    if isinstance(audio_url, list) and audio_url:
        audio_url = audio_url[0]  # Use the first audio URL

    audio_file_name = audio_url.split('/')[-1]
    audio_file_path = article_dir / audio_file_name
    if is_stream(audio_file_name):
        download_stream_file(audio_url, audio_file_path)
    elif is_mp3(audio_file_name):
        download_mp3_file(audio_url, audio_file_path)

    save_body_text(article_data, article_dir)
    save_metadata(article_data, article_dir)
    
    return article_dir
    
    

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
            for article_id, article_data in news_data_with_audio.items():
                save_news_file(article_data, article_id, output_dir)
