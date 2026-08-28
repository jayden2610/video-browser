# Video Browser

A local HTML media browser for your video and audio files. Zero dependencies, two files, one command.

Scans any folder for video/audio files and serves a dark-themed web UI with folder navigation, instant search, hover-to-preview, and fullscreen playback.

![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)

## Features

- **Folder sidebar** — browse by project/folder with file counts
- **Grid view** — visual cards with hover-to-preview (video) or audio icons
- **Instant search** — filter by filename or folder name
- **Type filter** — All / Video / Audio tabs
- **Fullscreen player** — click any card to play with native controls
- **Range requests** — video seeking works without buffering the whole file
- **Dark theme** — easy on the eyes, clean UI
- **Zero dependencies** — pure Python stdlib + a single HTML file
- **Portable** — works on macOS, Linux, Windows

## Quick Start

```bash
# Clone
git clone https://github.com/jayden2610/video-browser.git
cd video-browser

# Run — scans current directory
python server.py

# Or scan a specific folder
python server.py ~/Videos

# Custom port
python server.py --port 9000
```

Then open **http://localhost:8765** in your browser.

## Usage

```
python server.py [FOLDER] [--port PORT]

Arguments:
  FOLDER              Folder to scan (default: current directory)

Options:
  -p, --port PORT     Port to serve on (default: 8765)
```

## Supported Formats

| Video | Audio |
|-------|-------|
| `.mp4` `.mov` `.avi` `.mkv` `.webm` `.m4v` `.flv` `.wmv` | `.mp3` `.wav` `.m4a` `.flac` `.ogg` `.aac` |

## How It Works

`server.py` is a Python HTTP server (no dependencies beyond stdlib) that:
1. Recursively scans a folder for media files
2. Serves a JSON API at `/api/media` with file metadata
3. Serves the actual media files at `/file/...` with range request support
4. `index.html` is a single-file dark-themed web UI that fetches the API and renders a browsable grid

## Use with videouse

After a batch render, point the browser at `out/` (the review bucket), not the repo root. Scanning the whole project pulls hour-long `source/` tapes into the grid.

```bash
# from this repo, against a videouse checkout
python server.py /path/to/videouse/out --open
```

Keep it open while you keep/kill. Hover a card to preview, click for fullscreen. Newest files sort first.

Agent workflow (locate this repo, scan `out/`, inventory via `/api/media`, visually review with `videoReview` rather than screenshots of a playing player) lives in `.cursor/skills/review-renders/SKILL.md`.

## License

[MIT](LICENSE)
