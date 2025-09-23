import random, os

from core.config import set_youtube_key, set_gemini_key

from utils.highlight_reel_helpers import DOWNLOAD_DIR, TEMP_CLIP_DIR, deduplicate_clips, download_youtube_video, get_duration, motion_score, cleanup_files, extract_highlight_clips, save_highlight_clips

from rapidfuzz import fuzz
from typing import List

def nba_highlights(full_name: str, max_videos: int = 15) -> List[str]:
    """
    Get NBA highlights for a player by pulling a pool of YouTube videos,
    then letting the LLM decide which ones to include in the highlight reel.
    """
    youtube = set_youtube_key()
    client = set_gemini_key()

    query_variants = [
        f"{full_name} NBA basketball",
        f"{full_name} NBA highlights",
        f"{full_name} best plays",
    ]
    query = random.choice(query_variants)

    candidate_videos = []  # (score, video_id, title, description)

    next_page_token = None
    for _ in range(3):  # fetch up to 3 pages
        search_request = youtube.search().list(
            part="snippet",
            maxResults=50,
            q=query,
            type="video",
            videoEmbeddable="true",
            pageToken=next_page_token
        )
        search_response = search_request.execute()
        next_page_token = search_response.get("nextPageToken")

        for item in search_response.get("items", []):
            vid_id = item["id"].get("videoId")
            if not vid_id:
                continue
            snippet = item["snippet"]
            title = snippet["title"]
            description = snippet.get("description", "")

            score_name = fuzz.partial_ratio(full_name.lower(), title.lower())
            candidate_videos.append((score_name, vid_id, title, description))

        if not next_page_token:
            break

    if not candidate_videos:
        return []

    # Sort by fuzzy score so better matches float up
    candidate_videos.sort(key=lambda x: x[0], reverse=True)

    # Cap the pool size so we don’t overwhelm the model
    pool_size = min(max(50, max_videos * 6), len(candidate_videos))
    pool = candidate_videos[:pool_size]

    # Format pool for LLM
    def short(txt, n=160):
        return (txt[:n] + "...") if txt and len(txt) > n else (txt or "")

    pool_lines = []
    pool_url_map = {}
    for idx, (score, vid_id, title, description) in enumerate(pool, start=1):
        url = f"https://www.youtube.com/watch?v={vid_id}"
        pool_url_map[url] = vid_id
        pool_lines.append(
            f"{idx}. Title: {title}\n   URL: {url}\n   Desc: {short(description)}\n   Score: {score}"
        )

    system_prompt = globals().get("NBA_HIGHLIGHT_SYSTEM_PROMPT", "")
    user_instructions = (
        f"You are selecting highlight sources for {full_name}.\n\n"
        f"There are {len(pool)} candidate videos below. Choose exactly {max_videos} videos "
        "that are most likely to contain clean, single-player highlights (not interviews, "
        "not podcasts, not analysis, not full games). Prefer official highlight uploads and "
        "clips that focus on in-game plays.\n\n"
        "Output MUST be a JSON array of selected video URLs (exactly as shown). Example:\n"
        '["https://www.youtube.com/watch?v=abc", "https://www.youtube.com/watch?v=def"]\n\n'
        "Candidate list:\n\n" + "\n\n".join(pool_lines)
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_instructions},
    ]

    chosen_urls: List[str] = []
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=messages,
        )

        # Extract text
        resp_text = None
        if hasattr(response, "choices"):
            ch = response.choices[0]
            resp_text = getattr(getattr(ch, "message", {}), "content", None) \
                        or ch.message.get("content") if isinstance(ch.message, dict) else None
        if not resp_text:
            resp_text = str(response)

        import re, json
        m = re.search(r"\[.*\]", resp_text, flags=re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
                if isinstance(parsed, list):
                    chosen_urls = [u for u in parsed if isinstance(u, str)]
            except Exception:
                chosen_urls = []
        if not chosen_urls:
            # fallback: regex for youtube URLs
            chosen_urls = re.findall(r"https?://(?:www\.)?youtube\.com/watch\?v=[\w\-]+", resp_text)

    except Exception as e:
        print("⚠️ LLM selection failed:", e)
        chosen_urls = []

    # Validate + trim
    seen = set()
    final = []
    for url in chosen_urls:
        if url in pool_url_map and url not in seen:
            final.append(url)
            seen.add(url)
        if len(final) >= max_videos:
            break

    # Fallback: if not enough valid picks
    if len(final) < max_videos:
        for _, vid_id, _, _ in pool:
            url = f"https://www.youtube.com/watch?v={vid_id}"
            if url not in seen:
                final.append(url)
                seen.add(url)
            if len(final) >= max_videos:
                break

    return final


def generate_nba_highlights(full_name: str, max_videos=25, top_k_per_video=3, max_duration: int = 1200) -> List[str]:
    """
    Generate highlight clips for an NBA player.
    Memory-optimized version that processes videos sequentially and cleans up immediately.
    """
    urls = nba_highlights(full_name, max_videos=max_videos)
    if not urls:
        raise ValueError("No videos found for this player.")

    all_clips: List[str] = []

    for i, url in enumerate(urls):
        video_path = None
        clips_from_this_video = []
        
        try:
            print(f"📹 Processing video {i+1}/{len(urls)}: {url}")
            
            video_path = download_youtube_video(url, output_dir=DOWNLOAD_DIR)

            # Duration guard (skip > max_duration)
            duration = get_duration(video_path)
            if duration > max_duration:
                print(f"⚠️ Skipping long video ({duration/60:.1f} min): {url}")
                continue

            # Early "dead video" check (low motion in first 10s)
            avg_motion = motion_score(video_path, 0, min(10, duration))
            if avg_motion < 0.05:
                print(f"⚠️ Skipping dead/low-motion video: {url}")
                continue

            # Extract highlight segments
            segments = extract_highlight_clips(video_path, top_k=top_k_per_video)

            # Fallback: guarantee at least one short clip if video isn't empty
            if not segments and duration > 2:
                segments = [(0, min(5, duration))]

            # Save extracted highlight clips
            clips_from_this_video = save_highlight_clips(video_path, segments, output_dir=TEMP_CLIP_DIR)
            all_clips.extend(clips_from_this_video)
            
            print(f"✅ Extracted {len(clips_from_this_video)} clips from video {i+1}")

        except Exception as e:
            print(f"⚠️ Error processing {url}: {e}")
            # Clean up any partial clips from failed processing
            if clips_from_this_video:
                cleanup_files(clips_from_this_video)
        finally:
            # ALWAYS clean up the downloaded video immediately
            if video_path and os.path.exists(video_path):
                cleanup_files([video_path])
            
            # Force garbage collection after each video
            import gc
            gc.collect()

    # Deduplicate + shuffle
    print(f"🔍 Deduplicating {len(all_clips)} clips...")
    unique_clips = deduplicate_clips(all_clips)
    
    # Clean up duplicates that were removed
    duplicates_to_remove = [clip for clip in all_clips if clip not in unique_clips]
    if duplicates_to_remove:
        cleanup_files(duplicates_to_remove)
    
    random.shuffle(unique_clips)

    if not unique_clips:
        raise ValueError("No valid highlight clips found for this player.")

    print(f"✅ Generated {len(unique_clips)} unique highlight clips")
    return unique_clips