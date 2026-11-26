# Blunderbuss History: Automation Runbook

Channel: **Blunderbuss History**, "The full stories of history's biggest blunders". Faceless, animated, 16:9 long-form episodes of about 10–12 minutes.
Owner timezone: **Europe/London**. Posting slots: **08:00, 10:00, 12:00, 14:00, 16:00, 18:00** (6 a day).

Two scheduled tasks run this channel:

| Task | When | Job |
|---|---|---|
| Blunderbuss: post next video | 08:01, 10:01, 12:01, 14:01, 16:01, 18:01 | Upload the next `ready` item in `queue.json` to YouTube |
| Blunderbuss: production batch | 18:37 and 22:13 | Make 3 new episodes per batch for tomorrow's 6 slots, add them to the queue |

Files: code and queue live on `main`. Finished MP4s and thumbnails for each publish date live on their own orphan branch
**`videos-YYYY-MM-DD`** under `videos/` (GitHub releases are not available from these sessions). Each queue item has
`video_url` / `thumbnail_url` (raw.githubusercontent.com links to that branch).

---

## A. Posting run (one video per run)
YouTube account in Composio: alias **blunderbuss** (youtube_mirate-zone, @blunderbusshistorychannel). Always pass it.


1. `add_repo` this repo (access: push), clone it, read `queue.json`.
2. Pick the item whose `publish_date` is today (Europe/London) and whose `slot` is the slot this run is for (the next slot after now), with `status: "ready"`.
   If there is none for this slot, take the earliest `ready` item from an earlier date. If nothing is ready, stop and report "queue empty".
3. Duplicate guard: list the channel's latest uploads (Composio `YOUTUBE_LIST_CHANNEL_VIDEOS`, `mine: true`). If a video with the same title already exists, mark the item `posted` with that id and stop.
4. Upload via Composio (YouTube toolkit is connected in Composio):
   - In `COMPOSIO_REMOTE_WORKBENCH`: `requests.get(item["video_url"])` to `/home/user/`, then `upload_local_file(path)` → take `s3key` (tested: works, ~3 s per 10 MB).
   - Run `YOUTUBE_UPLOAD_VIDEO` with `title`, `description`, `tags`, `categoryId` ("27" Education), `privacyStatus: "public"`, and `videoFilePath: {name, mimetype: "video/mp4", s3key}`.
   - If the item has a thumbnail: `YOUTUBE_UPDATE_THUMBNAIL` with `videoId` and `thumbnail_url`. (Fails until the channel is phone-verified; that's not fatal.)
5. Update the item: `status: "posted"`, `youtube_id`, `posted_at`. Commit `queue.json` and push.
6. **If the upload fails with `quotaExceeded`** (Composio's shared YouTube quota): do not retry in a loop. Set `status: "ready"` (unchanged), add `last_error`, commit, and send the owner a short notification:
   "Couldn't post <title> at <slot>: YouTube API quota. Files: <video URL>, <thumbnail URL>. You can upload it in YouTube Studio; I'll retry at the next slot."
7. Never post the same item twice. Never change the channel's settings. Never delete videos.

## B. Production batch (3 episodes per batch)

Target: by the end of the night, tomorrow has 6 `ready` items, one per slot. Each batch fills the next 3 empty slots for tomorrow.

1. `add_repo` + clone, run `./setup.sh` (installs Kokoro TTS + fonts). `rsvg-convert`, `ffmpeg` and the Anton/Montserrat fonts are already in the image.
2. Choose 3 topics from `topics.md` with status `todo` (top of the list first). Mark them `in-progress` and commit straight away so the other batch doesn't take them.
3. For each topic, make one episode with the same pipeline as `pipeline/ep1..ep5`:
   1. **Research first** (WebSearch/WebFetch; Wikipedia plus at least 2 other sources). Every date, name and number in the script must come from a source you fetched. Say "reportedly" or "legend says" for anything weakly sourced. Keep a sources list for the description.
   2. **Script** (`script.py`, list of `(shot, chapter-or-None, narration)`): cold open with the absurd moment, title line, 6–8 named chapters, "What Remains" ending, the standard outro line. **1,450–1,800 words** (≈10–12 min). Spell years out in words ("nineteen-oh-four") so Kokoro reads them right.
   3. **Voice**: copy `pipeline/epN/voice.py` (af_heart, per-sentence cache) → `voice.wav` + `timing.json`. Check total ≥ 600 s; if short, add researched paragraphs.
   4. **Art**: copy the closest episode as a template (ships/sea → ep1/ep3/ep4; land/animals/soldiers → ep2; space/tech/diagrams → ep5). Write new SVG scenes for the topic (8–14 scenes), flat silhouette style, brand palette (navy #14202E, parchment #F1E4C8, red #D9482B, brass #C9A04A). Use a map or diagram scene for any journey or manoeuvre, and documents or newspapers for reactions (the masthead is always "BLUNDERBUSS GAZETTE"; no newspapers before about 1700, use an official document instead).
   5. **Render** with the shared engine (camera moves, scene tags, chapter cards, karaoke captions, vignette): 1920×1080, 24 fps, two parallel parts, then mux with the audio mix, `loudnorm I=-14`.
   6. **QA (required)**: contact sheet every ~25 s plus 6 full-size frames. Check that the captions are readable, nothing is clipped or cut off at the frame edge, lights and gunfire come from the right source, objects sitting on water or ground stay attached as the camera moves, there are no long static stretches (split any scene longer than about 40 s by giving some paragraphs a different shot), and the scene matches the narration. Fix and re-render if needed.
   7. **Thumbnail** 1280×720: 2–3 huge Anton words (cream + gold, dark stroke), one dramatic image, red year tag. Must be under 2 MB.
   8. **Metadata**: title (outcome first, under 70 chars), description (2-line hook, chapter timestamps from `chapters.txt`, sources, 3–5 hashtags), tags.
4. Store files: `git fetch --depth=1 origin videos-<tomorrow>` if it exists, otherwise `git checkout --orphan videos-<tomorrow>` with an empty tree. Add the MP4 and thumbnail under `videos/`, **one file per commit, push after each** (files must stay under 100 MB; re-encode with a higher CRF if needed). Then on `main`: add the queue item for tomorrow's next free slot (`status: "ready"`, `video_url`/`thumbnail_url` = raw.githubusercontent.com links to that branch), mark the topic `done` in `topics.md`, commit `pipeline/epN/` (code only, no renders), push.
   Housekeeping: delete remote `videos-*` branches whose date is 3 or more days ago and whose items are all `posted` (`git push origin --delete videos-<date>`).
5. Report: titles made, slots filled, anything that failed. If fewer than 3 were finished, say so. The posting run will skip empty slots.

## Rules that always apply
- Accuracy beats speed: no invented quotes, numbers or events. If a fact can't be confirmed, cut it.
- No real people's photos or likenesses, no copyrighted images, no real newspaper names.
- Don't repeat a topic already in `queue.json` or marked `done`.
- Keep the visual style consistent with episodes 1–5.
