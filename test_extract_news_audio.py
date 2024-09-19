import json
from extract_news_audio import has_news_audio

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_has_news_audio():
    # Load news data from a JSON file
    news_data = read_json_file(f'./test_dataset.json')
    
    for article_id, article in news_data.items():
        audio_url = article["data"]["body"]["Audio"]
        expected_result = bool(audio_url)  # True if audio URL exists, else False
        
        result = has_news_audio(article)
        
        if result == expected_result:
            print(f"Test passed for {article_id}.")
        else:
            print(f"Test failed for {article_id}: Expected {expected_result}, got {result}.")

if __name__ == "__main__":
    test_has_news_audio()
    print("All tests checked!")