import json
import requests
import subprocess

from pathlib import Path
from tqdm import tqdm

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

def extract_speaker_name(second_last_line):
    """Extracts the speaker's name from the second last line of text.

    Args:
        second_last_line (str): The second last line of text.

    Returns:
        str: Extracted speaker's name.
    """
    parts = second_last_line.split(' ')
    if len(parts) > 1:
        return ' '.join(parts[1:])  
    return ''  

def prepare_news_data_with_audio(news_info, news_house):
    """Prepares a structure for news data with audio, including speaker's name if applicable for the news house.

    Args:
        news_info (dict): The news information dictionary containing all relevant data.
        news_house (str): The news house identifier (e.g., 'VOA', 'VOT', 'RFA').

    Returns:
        dict: A dictionary containing the title, body text, audio URL, and metadata.
    """
    body_text_lines = news_info['data']['body'].get('Text', [])
    body_text = "\n".join(body_text_lines)

    speaker_name = "Unknown"  # Default speaker name

    if news_house == 'VOA' and len(body_text_lines) >= 2:
        second_last_line = body_text_lines[-2].strip()  
        
        
        speaker_name = extract_speaker_name(second_last_line)  

    news_data_with_audio = {
        'title': news_info['data']['title'],
        'body_text': body_text,
        'audio_url': news_info['data']['body'].get('Audio', ''),
        'metadata': {
            'published_date': news_info['data']['meta_data'].get('Date'),
            'author': news_info['data']['meta_data'].get('Author'),
            'speaker': speaker_name ,
            'category': news_info['data']['meta_data'].get('Tags', []),
            'news_url': news_info['data']['meta_data'].get('URL')

        }
    }
    return news_data_with_audio

def get_news_with_audio(news_data, news_house):
    """Filters news with audio

    Args:
        news_data (dict): news dataset

    Returns:
        dict: dict of news dataset with audio
    """
    news_data_with_audio = {}
    for news_id, news_info in news_data.items():
        if has_news_audio(news_info):
            news_data_with_audio[news_id] = prepare_news_data_with_audio(news_info, news_house)
    return news_data_with_audio
   
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
    """Saves content to a file

    Args:
        article_data (dict): The article data containing audio URL, body text, and metadata.
        article_id (str): The ID of the article, used for naming the directory.
        output_dir (Path): The directory where the article data will be saved.
    """
def save_news_file(article_data, article_id, output_dir):
    """Saves content to a file

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

    # Instead of downloading, save the audio URL to a text file
    with open(article_dir / f"{article_id}_audio_url.txt", 'w', encoding='utf-8') as url_file:
        url_file.write(audio_url)
    print(f"Audio URL saved for article {article_id} as {article_id}_audio_url.txt")

    save_body_text(article_data, article_dir)
    save_metadata(article_data, article_dir)

if __name__ == "__main__":
    news_houses = ['VOA', 'VOT', 'RFA']
    for news_house in news_houses:
        news_dataset_dir = Path(f'./data/{news_house}/news_dataset')
        output_dir = Path(f'./data/{news_house}/news_dataset_with_audio')
        output_dir.mkdir(parents=True, exist_ok=True)

        news_dataset_file_paths = list(news_dataset_dir.iterdir())
        news_dataset_file_paths.sort()

        for news_dataset_file_path in tqdm(news_dataset_file_paths, desc=f'Processing {news_house} news files'):
            news_data = read_json_file(news_dataset_file_path)
            news_data_with_audio = get_news_with_audio(news_data, news_house)

            for article_id, article_data in tqdm(news_data_with_audio.items(), desc='Saving articles'):
                save_news_file(article_data, article_id, output_dir)
