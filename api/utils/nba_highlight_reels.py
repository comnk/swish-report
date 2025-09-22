import random, time

from core.config import set_youtube_key
from utils.highlight_reel_helpers import DOWNLOAD_DIR, TEMP_CLIP_DIR, deduplicate_clips, download_youtube_video, get_duration, motion_score, cleanup_files, extract_highlight_clips, save_highlight_clips

from rapidfuzz import fuzz
from typing import List

def nba_highlights(full_name: str, max_videos: int = 15) -> List[str]:
    youtube = set_youtube_key()

    # Rotate queries for more variety
    query_variants = [
        f"{full_name} NBA basketball",
        f"{full_name} NBA basketball highlights",
    ]
    query = random.choice(query_variants)

    exclude_keywords = [
        "interview", "press conference", "announcement", "commitment", "docuseries",
        "mic", "mic'd", "speaks", "talks", "podcast", "intro", "recap", "analysis",
        "one-on-one", "interview", "story", f"{full_name.lower()}:", "recruitment",
        "recruiting", "tryout", "invite", "breakdown", "reveals", "tries"
    ]
    full_game_keywords = ["full game", "vs", "v.", "replay", "preview", "matchup", "team"]

    candidate_videos = []
    highlight_videos = []

    next_page_token = None
    for _ in range(3):
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
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            title = snippet["title"].lower()
            description = snippet.get("description", "").lower()

            if full_name.lower() not in (title + description):
                continue
            if any(kw in title or kw in description for kw in exclude_keywords):
                continue
            if any(kw in title for kw in full_game_keywords):
                continue

            score_name = fuzz.partial_ratio(full_name.lower(), title)

            # ✅ If "highlights" in title, mark for guaranteed inclusion
            if "highlights" in title or "plays" in title:
                highlight_videos.append((score_name, video_id, title))
            else:
                candidate_videos.append((score_name, video_id, title))

        if not next_page_token:
            break

    if not (candidate_videos or highlight_videos):
        return []

    # Add randomness that changes per run
    random.seed(time.time())

    # Weighted random for non-highlight vids
    random.shuffle(candidate_videos)
    weights = [max(score, 1) for score, _, _ in candidate_videos]
    chosen = random.choices(
        candidate_videos,
        weights=weights,
        k=min(max_videos * 4, len(candidate_videos))
    )

    # ✅ Dedup + merge (highlight videos always included first)
    seen = set()
    selected = []

    # Force-included highlight videos
    for _, vid_id, _ in highlight_videos:
        if vid_id not in seen:
            selected.append(f"https://www.youtube.com/watch?v={vid_id}")
            seen.add(vid_id)
        if len(selected) >= max_videos:
            return selected

    # Fill remaining slots from weighted sample
    for _, vid_id, _ in chosen:
        if vid_id not in seen:
            selected.append(f"https://www.youtube.com/watch?v={vid_id}")
            seen.add(vid_id)
        if len(selected) >= max_videos:
            break

    return selected

def generate_nba_highlights(full_name: str, max_videos=15, top_k_per_video=3, max_duration: int = 1200) -> List[str]:
    """
    Generate highlight clips for an NBA player.
    Skips long or low-motion videos to avoid wasting resources.
    """
    urls = nba_highlights(full_name, max_videos=max_videos)
    if not urls:
        raise ValueError("No videos found for this player.")

    all_clips: List[str] = []

    for url in urls:
        video_path = None
        try:
            video_path = download_youtube_video(url, output_dir=DOWNLOAD_DIR)

            # 🔹 Duration guard (skip > 20 min, or whatever you set)
            duration = get_duration(video_path)
            if duration > max_duration:
                print(f"⚠️ Skipping long video ({duration/60:.1f} min): {url}")
                cleanup_files([video_path])
                continue

            # 🔹 Early "dead video" check (low motion in first 10s)
            avg_motion = motion_score(video_path, 0, min(10, duration))
            if avg_motion < 0.05:
                print(f"⚠️ Skipping dead/low-motion video: {url}")
                cleanup_files([video_path])
                continue

            # 🔹 Extract highlight segments
            segments = extract_highlight_clips(video_path, top_k=top_k_per_video)

            # Fallback: guarantee at least one short clip if video isn't empty
            if not segments and duration > 2:
                segments = [(0, min(5, duration))]

            # Save extracted highlight clips
            clips = save_highlight_clips(video_path, segments, output_dir=TEMP_CLIP_DIR)
            all_clips.extend(clips)

        except Exception as e:
            print(f"⚠️ Error processing {url}: {e}")
        finally:
            if video_path:
                cleanup_files([video_path])  # 🔹 always clean up

    # Deduplicate + shuffle
    unique_clips = deduplicate_clips(all_clips)
    random.shuffle(unique_clips)

    if not unique_clips:
        raise ValueError("No valid highlight clips found for this player.")

    return unique_clips