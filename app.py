import argparse
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

def instagram_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or (parsed.hostname or "").removeprefix("www.") != "instagram.com":
        raise argparse.ArgumentTypeError("use an https://instagram.com URL")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Instagram audio and metadata.")
    parser.add_argument("url", type=instagram_url)
    url = parser.parse_args().url

    options = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s/audio.%(ext)s",
        "writeinfojson": True,
        "noplaylist": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"Saved in {Path(ydl.prepare_filename(info)).parent}")


if __name__ == "__main__":
    main()
