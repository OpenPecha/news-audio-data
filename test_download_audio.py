import tempfile
import os

from extract_news_audio import download_mp3_file, download_stream_file

def test_download_mp3_file():
    url = ""
    with tempfile.TemporaryDirectory() as tmpdirname:
        dest_path = tmpdirname + "/test.mp3"

        download_mp3_file(url, dest_path)
        assert os.path.exists(dest_path), "File not downloaded"

def test_download_stream_file():
    url = "https://www.rfa.org/tibetan/sargyur/sarah-college-youth-symposium-tibetan-culture-08202024062707.html/@@stream"
    # with tempfile.TemporaryDirectory() as tmpdirname:
    dest_path = "./test.mp3"

    download_stream_file(url, dest_path)
        # assert os.path.exists(dest_path), "File not downloaded"

if __name__ == "__main__":
    test_download_stream_file()
