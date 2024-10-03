import os
import pandas as pd
import requests
import re
import json

data_root_dir = './data'  
news_channels = ['RFA', 'VOA', 'VOT']

data_list = []

# Regex pattern for validating URLs
url_pattern = re.compile(r'^(http|https)://.*$')

# Headers for RFA requests
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
    "cache-control": "max-age=0",
    "cookie": "AMCVS_518ABC7455E462B97F000101%40AdobeOrg=1; s_cc=true; utag_main=v_id:019169eade56002296e6ea4a443c0507d001b075008f7$_sn:11$_se:5$_ss:0$_st:1727788387180$vapi_domain:rfa.org$ses_id:1727786558635%3Bexp-session$_pn:5%3Bexp-session; AMCV_518ABC7455E462B97F000101%40AdobeOrg=1176715910%7CMCIDTS%7C19997%7CMCMID%7C92058839809215745258174654077801968713%7CMCAID%7CNONE%7CMCOPTOUT-1727793787s%7CNONE%7CvVersion%7C5.4.0; s_sq=%5B%5BB%5D%5D",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
}

# Loop through each news channel directory
for channel in news_channels:
    channel_dir = os.path.join(data_root_dir, channel, 'news_dataset_with_audio')
    
    if not os.path.exists(channel_dir):
        print(f"Directory {channel_dir} not found.")
        continue
    
    for root, dirs, files in os.walk(channel_dir):
        audio_id = os.path.basename(root)  # Get the folder name as the ID
        audio_url = None
        audio_text = 'Transcript not found'  
        speaker_name = ''
        speaker_gender = ''
        publishing_year = ''
        author = ''
        
        for file in files:
            if file.endswith('.txt') and file != 'news_text.txt':
                audio_url_path = os.path.join(root, file)
                with open(audio_url_path, 'r', encoding='utf-8') as f:
                    url_content = f.read().strip()  # Read the URL and strip whitespace
                    if url_pattern.match(url_content):  # Validate if it's a URL
                        audio_url = url_content
            
            if file == 'news_text.txt':
                text_file_path = os.path.join(root, file)
                if os.path.exists(text_file_path):
                    with open(text_file_path, 'r', encoding='utf-8') as f:
                        audio_text = f.read().strip()  

            if file.endswith('.json'):
                metadata_path = os.path.join(root, file)
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                        if channel == 'VOA':
                            # Correct the publishing year for VOA
                            publishing_year = metadata.get('author', '') 
                            speaker_name = metadata.get('speaker', '') 
                        else:
                            # Use regular metadata for RFA and VOT
                            speaker_name = metadata.get('speaker', '')
                            publishing_year = metadata.get('published_date', '') 
                            speaker_gender = metadata.get('gender', '')

        # Append collected data to the list
        data_list.append({
            'ID': audio_id,
            'Audio URL': audio_url if audio_url else 'URL not found',
            'Audio Text': audio_text,
            'Speaker Name': speaker_name,
            'Speaker Gender': speaker_gender,
            'News Channel': channel,  
            'Publishing Year': publishing_year
        })

# Sort data_list by ID
data_list.sort(key=lambda x: x['ID'])

# Create DataFrame and save to CSV
df = pd.DataFrame(data_list, columns=['ID', 'Audio URL', 'Audio Text', 'Speaker Name', 'Speaker Gender', 'News Channel', 'Publishing Year'])
output_metadata_csv_path = './news_data.csv'
df.to_csv(output_metadata_csv_path, index=False, encoding='utf-8')
print(f"CSV file saved at {output_metadata_csv_path}")

# Create a session object
session = requests.Session()
session.headers.update(headers)

# Directory to save downloaded RFA audio
rfa_audio_dir = os.path.join(data_root_dir, 'RFA', 'downloaded_audio')
os.makedirs(rfa_audio_dir, exist_ok=True)

# RFA audio URL handling with headers and downloading
for index, row in df.iterrows():
    audio_url = row['Audio URL']
    audio_id = row['ID']
    news_channel = row['News Channel']
    
    if news_channel == 'RFA':
        try:
            if audio_url and audio_url != 'URL not found':
                response = session.get(audio_url, headers=headers, stream=True)  
                response.raise_for_status()  # Check for HTTP errors

                # Define the audio file path
                audio_file_path = os.path.join(rfa_audio_dir, f'{audio_id}.mp3')
                
                # Save the audio file
                with open(audio_file_path, 'wb') as audio_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            audio_file.write(chunk)

                print(f"Downloaded RFA audio: {audio_id}.mp3")
            else:
                print(f"No valid audio URL found for RFA ID: {audio_id}")
        except Exception as e:
            print(f"Failed to access or download RFA URL {audio_url}: {e}")
