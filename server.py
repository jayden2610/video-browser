#!/usr/bin/env python3
"""Video Browser — local HTML media browser for any folder.

Usage:
    python server.py                  # scan current directory
    python server.py /path/to/folder  # scan specific folder
    python server.py --port 9000      # custom port
"""

import argparse
import http.server
import json
import os
import socketserver
import sys
import urllib.parse
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv", ".wmv"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"}
MEDIA_EXTS = VIDEO_EXTS | AUDIO_EXTS


def scan_media(root: Path):
    """Walk root and return list of media file dicts."""
    files = []
    for dirpath, _, filenames in os.walk(root):
        parts = Path(dirpath).parts
        if any(p.startswith(".") or p == "node_modules" for p in parts):
            continue
        for fn in sorted(filenames):
            ext = Path(fn).suffix.lower()
            if ext not in MEDIA_EXTS:
                continue
            full = Path(dirpath) / fn
            try:
                rel = full.relative_to(root)
            except ValueError:
                continue
            stat = full.stat()
            is_video = ext in VIDEO_EXTS
            folder = rel.parts[0] if len(rel.parts) > 1 else "_root"
            files.append({
                "name": fn,
                "path": str(rel).replace("\\", "/"),
                "folder": folder,
                "size": stat.st_size,
                "ext": ext.lstrip("."),
                "type": "video" if is_video else "audio",
            })
    files.sort(key=lambda f: (f["folder"], f["name"]))
    return files


class MediaHandler(http.server.SimpleHTTPRequestHandler):
    media_list = []
    root_dir = Path(".")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/media":
            self.send_json(self.media_list)
        elif path == "/" or path == "/index.html":
            self.send_file(HTML_PATH, "text/html")
        elif path.startswith("/file/"):
            rel = urllib.parse.unquote(path[6:])
            full = self.root_dir / rel
            if full.exists() and full.suffix.lower() in MEDIA_EXTS:
                self.serve_media(full)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, filepath, content_type):
        with open(filepath, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def serve_media(self, filepath):
        size = filepath.stat().st_size
        range_header = self.headers.get("Range")

        if range_header:
            range_header = range_header.replace("bytes=", "")
            start, end = range_header.split("-")
            start = int(start)
            end = int(end) if end else min(start + 1024 * 1024 - 1, size - 1)
            length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(str(filepath)))
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", length)
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(filepath, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(length))
        else:
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(filepath)))
            self.send_header("Content-Length", size)
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(filepath, "rb") as f:
                while chunk := f.read(1024 * 64):
                    self.wfile.write(chunk)

    def guess_type(self, path):
        ext = Path(path).suffix.lower()
        types = {
            ".mp4": "video/mp4", ".webm": "video/webm", ".mkv": "video/x-matroska",
            ".mov": "video/quicktime", ".avi": "video/x-msvideo", ".m4v": "video/mp4",
            ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
            ".flac": "audio/flac", ".ogg": "audio/ogg", ".aac": "audio/aac",
        }
        return types.get(ext, "application/octet-stream")

    def log_message(self, format, *args):
        pass


HTML_PATH = Path(__file__).parent / "index.html"


def main():
    parser = argparse.ArgumentParser(description="Video Browser — local media file browser")
    parser.add_argument("folder", nargs="?", default=".", help="Folder to scan (default: current directory)")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to serve on (default: 8765)")
    args = parser.parse_args()

    root = Path(args.folder).resolve()
    if not root.exists():
        print(f"  Error: {root} does not exist")
        sys.exit(1)

    print(f"\n  Video Browser")
    print(f"  Scanning {root} ...")
    media = scan_media(root)
    MediaHandler.media_list = media
    MediaHandler.root_dir = root

    video_count = sum(1 for m in media if m["type"] == "video")
    audio_count = sum(1 for m in media if m["type"] == "audio")
    print(f"  Found {len(media)} files ({video_count} video, {audio_count} audio)")
    print(f"  Serving at http://localhost:{args.port}")
    print(f"  Press Ctrl+C to stop\n")

    with socketserver.TCPServer(("", args.port), MediaHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")


if __name__ == "__main__":
    main()
