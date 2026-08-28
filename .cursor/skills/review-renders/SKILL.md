---
name: review-renders
description: Open Video Browser on a videouse out/ folder (or any render dir) to visually review newly rendered videos. Use when the user has new out/*.mp4 files, wants to inspect a batch, says open video browser, review renders, look at the new clips, or keep/kill after produce.py.
---

# Review renders in Video Browser

Default job: five (or N) new `produce.py` outputs, open a visual grid, inspect them. Do not open a file manager. Do not scan the whole videouse tree.

This skill is for **reviewing finished clips**. Mechanical gates (face, cards, duration, watermarks) still run from videouse tools. Human keep/kill on a phone is still the inspire gate.

## Pick the folder

| Goal | Scan this | Never this |
|---|---|---|
| Fresh batch after `produce.py` | `<videouse>/out` | repo root, `source/`, `work/`, `music/` |
| Posting library | `<videouse>/all_rendered` | same |
| Caption / style A/B | the specific gallery dir (`renders/gallery`, `captions/…`) | mixed with long-form sources |

`out/` is the review bucket. `all_rendered/` is what already shipped. Scanning videouse root walks `source/` and dumps hour-long tapes next to 30s TikToks.

Resolve `<videouse>` from cwd, a path the user named, or a sibling checkout. Resolve **this** tool as the directory that contains `server.py` + `index.html` (this repo, `../video-browser`, or a clone of `jayden2610/video-browser`).

## Launch

Scan is **one-shot at process start**. If you already have a server from an older batch, kill that PID and start again. New files will not appear otherwise.

```bash
python /path/to/video-browser/server.py /path/to/videouse/out --port 8765
```

On the user's own machine, add `--open` so their default browser hits the UI. In a cloud agent VM, skip `--open` (it opens the VM browser, not Jayden's Chrome). Run the server in tmux so it outlives the shell call. Do not background with a raw `&` and walk away.

Ready when `http://127.0.0.1:8765/api/media` returns JSON. Doctor:

```bash
curl -sS http://127.0.0.1:8765/api/media | python3 -c "
import json, sys
rows = json.load(sys.stdin)
print(len(rows), 'files')
for r in rows[:8]:
    print(f\"{r['mtime']:.0f}  {r['type']:5}  {r['name']}\")
"
```

The list is newest-first. The five new renders should be the first five video rows, or identifiable by `produce.py --stamp` (`_YYYY-MM-DD_HH-MM` in the name). If they are missing, you pointed at the wrong folder or the server started before the encode finished.

UI: `http://127.0.0.1:8765`. Video tab, sort stays on Newest, search by stem (`chris_23`) if `out/` is noisy.

## How to look (this is the whole point)

Three different jobs. Mixing them up is how agents "review" a video by screenshotting a paused `<video>` tag and missing motion, captions, and audio.

### 1. Inventory

Use `/api/media` (or `ls -t out/*.mp4`). Do not screenshot the grid just to list files.

### 2. Human keep/kill (inspire / Gate H)

Open the grid in a real browser. Hover a card (muted loop preview). Click for fullscreen with native controls. Watch end-to-end: hook in the first 3s, crop, captions, bed, last sentence.

This is the path for "I have 5 new videos, open video browser so I can analyse them." You start the server and hand over the URL. Do not substitute a write-up for the watch.

Browser rules for this repo's localhost UI:

- Cloud agent: drive `http://127.0.0.1:8765` with `computerUse`. That is a local page, not a logged-in Google property.
- Do not use Browser MCP / user Chrome for this. That session is for Gmail and live sites, and it cannot see the VM's localhost.
- Do not use Browser MCP to "watch" the mp4s either. Local files go through this server or a local player.

### 3. Agent visual QA

Screenshots of a playing HTML5 player lose motion. For an agent that must actually see the clips:

1. **Stills videouse already dumped.** After produce, Read `work/verify/<id>/` (`*_bl.jpg` corners, `*_under.jpg`). That is Gate J (watermarks / SOVYN / channel bugs). Do this before showing clips to the user.
2. **`videoReview` on the file paths.** Pass the five `out/*.mp4` paths as `file_attachments`. Ask it to check: 9:16 vs landscape, face in frame, caption placement, burned-in source text, abrupt ending, black frames. This is the watch tool.
3. **`computerUse` on the grid** only to prove the browser loaded the new files and hover preview plays. One pass. Not the QA of the edit.
4. **ffmpeg stills** if verify dumps are missing: extract 0s / 1/3 / 2/3 / last frame, then Read the jpgs.

A/B two cuts of the same window: use `motion-compare`, not this grid (one player, no overlay).

## Cleanup

Stop the tmux session or send Ctrl+C to the `server.py` you started. Do not `pkill -f server.py`. Leave `out/` and evidence frames on disk.

## Videouse checklist after a 5-clip batch

1. Restart Video Browser on `out/` (not repo root).
2. Confirm `/api/media` lists the five new names at the top.
3. Gate J stills for each id.
4. `videoReview` each mp4 (or the user watches in the grid).
5. Keep/kill in `project.md`. Copy keeps to `all_rendered/` only after that.
