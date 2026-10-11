"""Ingest (Step 7): Instagram URL -> audio.m4a and audio.info.json in downloads/<id>/."""

import argparse
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp


def instagram_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or (parsed.hostname or "").removeprefix("www.") != "instagram.com":
        raise argparse.ArgumentTypeError("use an https://instagram.com URL")
    return value


def download(url: str) -> Path:
    options = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s/audio.%(ext)s",
        "writeinfojson": True,
        "noplaylist": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info)).parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Instagram audio and metadata.")
    parser.add_argument("url", type=instagram_url)
    print(f"Saved in {download(parser.parse_args().url)}")


if __name__ == "__main__":
    main()
