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
    """Checks if the file is a stream file.

    Args:
        file_name (str): name of the file

    Returns:
        bool: True if the file is a stream file, False otherwise
    """
    return file_name.endswith('.stream')

def is_mp3(file_name):
    """Checks if the file is an mp3 file.

    Args:
        file_name (str): name of the file

    Returns:
        bool: True if the file is an mp3 file, False otherwise
    """
    return file_name.endswith('.mp3')

def download_stream_file(url, dest_path):
    """Downloads a stream file using ffmpeg and saves it with .mp3 extension.

    Args:
        url (str): url of the file
        dest_path (str): destination path to save the file

    Returns:
        str: destination path of the file
    """
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    try:
        subprocess.run(["ffmpeg", "-headers", f"User-Agent: {user_agent}", "-i", url, "-c", "copy", dest_path], check=True)
        print(f"Downloaded stream file: {url}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading stream file: {e}")

def download_mp3_file(url, dest_path):
    """function to download the mp3 file

    Args:
        url (str): link of the audio file
        dest_path (str): destination of the file path
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded MP3: {url}")
    else:
        print(f"Failed to download the MP3 file: {url}, status code: {response.status_code}")

def save_body_text(article_data, article_dir):
    """Saves the body text of the article to a text file.

    Args:
        article_data (dict): The article data containing the body text.
        article_dir (Path): The directory where the text file will be saved.
    """
    with open(article_dir / 'news_text.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(article_data['body_text'])

def save_metadata(article_data, article_dir):
    """Saves metadata of the article to a JSON file.

    Args:
        article_data (dict): The article data containing metadata.
        article_dir (Path): The directory where the metadata file will be saved.
    """
    with open(article_dir / 'metadata.json', 'w', encoding='utf-8') as meta_file:
        json.dump(article_data['metadata'], meta_file, ensure_ascii=False, indent=4)

def save_news_file(article_data, article_id, output_dir):
    """Saves content to a json file

    Args:
        article_data (dict): The article data containing audio URL, body text, and metadata.
        article_id (str): The ID of the article, used for naming the directory.
        output_dir (Path): The directory where the article data will be saved.
    """
    article_dir = output_dir / article_id
    article_dir.mkdir(parents=True, exist_ok=True)

    audio_url = article_data['audio_url']
    
    if isinstance(audio_url, list) and audio_url:
        audio_url = audio_url[0]  # Use the first audio URL
    
    if not audio_url.startswith(('http://', 'https://')):
        print(f"Invalid audio URL for article {article_id}: {audio_url}")
        return

    audio_file_name = f"{article_id}.mp3"
    audio_file_path = article_dir / audio_file_name

    try:
        download_mp3_file(audio_url, audio_file_path)

        # Check if the file was created
        if not audio_file_path.exists():
            raise FileNotFoundError("Audio file was not saved.")

    except Exception as e:
        print(f"Failed to download audio for article {article_id}: {e}")
        # Save the audio URL as a text file
        with open(article_dir / f"{audio_file_name}", 'w', encoding='utf-8') as url_file:
            url_file.write(audio_url)
        print(f"Audio URL saved for article {article_id} as {audio_file_name}")

    save_body_text(article_data, article_dir)
    save_metadata(article_data, article_dir)

if __name__ == "__main__":
    news_houses = ['VOA', 'VOT', 'RFA']
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