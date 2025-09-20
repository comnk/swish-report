from core.config import set_youtube_key

import os
import random
import isodate
import subprocess
import cv2
import numpy as np
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from rapidfuzz import fuzz
from typing import List

from PIL import Image
import imagehash

DOWNLOAD_DIR = "downloads"
TEMP_CLIP_DIR = "highlights"
FINAL_DIR = "final_reels"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_CLIP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

# -------------------------------
# Download YouTube video (safe filenames)
# -------------------------------
def remux_mp4(file_path: str) -> str:
    """Fix edge-case MP4s by remuxing via FFmpeg."""
    fixed_path = file_path.replace(".mp4", "_fixed.mp4")
    subprocess.run([
        "ffmpeg", "-i", file_path,
        "-c", "copy", fixed_path,
        "-y"
    ], check=True)
    return fixed_path

def download_youtube_video(url: str, output_dir: str = DOWNLOAD_DIR) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename_template = os.path.join(output_dir, "%(title)s.%(ext)s")
    
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",
                "--merge-output-format", "mp4",
                "--recode-video", "mp4",  # ensure valid MP4
                "--restrict-filenames",
                "-o", filename_template,
                url
            ],
            check=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print("yt-dlp stdout:", result.stdout)
        if result.stderr:
            print("yt-dlp stderr:", result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"⚠️ yt-dlp failed for {url} with exit code {e.returncode}")
        print("stdout:", getattr(e, "stdout", None))
        print("stderr:", getattr(e, "stderr", None))
        raise
    except Exception as e:
        print(f"⚠️ Error downloading {url}: {e}")
        raise

    # Return the most recently downloaded file
    downloaded_files = sorted(
        [os.path.join(output_dir, f) for f in os.listdir(output_dir)],
        key=os.path.getmtime,
        reverse=True
    )
    if not downloaded_files:
        raise RuntimeError(f"No files found in {output_dir} after downloading {url}")

    downloaded_file = downloaded_files[0]

    # Check file size
    if os.path.getsize(downloaded_file) == 0:
        raise RuntimeError(f"Downloaded file is empty: {downloaded_file}")

    # Optional: remux to fix MP4 edge cases
    try:
        downloaded_file = remux_mp4(downloaded_file)
    except Exception as e:
        print(f"⚠️ Could not remux {downloaded_file}, using original file. Error: {e}")

    return downloaded_file


# -------------------------------
# Scene detection
# -------------------------------
def detect_scenes(video_path: str, threshold: float = 27.0):
    """Detect scenes in a video using content detection."""
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    return [(start.get_seconds(), end.get_seconds()) for start, end in scene_manager.get_scene_list()]


# -------------------------------
# Motion scoring (weighted by scene length)
# -------------------------------
def motion_score(video_path: str, start: float, end: float, sample_rate: int = 5) -> float:
    """Compute average motion score of a video segment."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)

    ret, prev = cap.read()
    if not ret:
        cap.release()
        return 0.0
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    score, frames = 0.0, 0
    while cap.get(cv2.CAP_PROP_POS_MSEC) < end * 1000:
        for _ in range(sample_rate):
            ret, frame = cap.read()
            if not ret:
                break
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        score += np.sum(diff) / diff.size
        frames += 1
        prev_gray = gray

    cap.release()
    return score / max(frames, 1)


# -------------------------------
# Extract highlight scenes
# -------------------------------

def extend_scene_to_motion_end(video_path: str, start: float, end: float, max_extend: float = 3.0, threshold: float = 5.0):
    """Extend the end of a scene until motion drops below threshold."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, end * 1000)
    
    ret, prev = cap.read()
    if not ret:
        cap.release()
        return end

    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    frame_time = 1 / cap.get(cv2.CAP_PROP_FPS)
    total_extend = 0.0

    while total_extend < max_extend:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = np.sum(cv2.absdiff(prev_gray, gray)) / gray.size

        # stop extending if motion drops below threshold
        if diff < threshold:
            break

        total_extend += frame_time
        prev_gray = gray

    cap.release()
    return min(end + total_extend, end + max_extend)

def extract_highlight_clips(
    video_path: str,
    top_k: int = 3,
    min_len: int = 3,
    max_len: int = 12,
    pad_before: float = 0.3
):
    scenes = detect_scenes(video_path)
    scored_scenes = []

    for start, end in scenes:
        duration = end - start
        if duration < min_len:
            continue

        score = motion_score(video_path, start, end)

        # Dynamic extension to avoid cutting off shots
        extended_end = extend_scene_to_motion_end(video_path, start, end, max_extend=max_len - duration)

        seg_start = max(0, start - pad_before)
        seg_end = min(extended_end, start + max_len)

        scored_scenes.append(((seg_start, seg_end), score))

    # Sort by score
    scored_scenes.sort(key=lambda x: x[1], reverse=True)

    # Pick top_k non-overlapping
    final_segments = []
    for (seg_start, seg_end), _ in scored_scenes:
        if any(seg_start < existing_end and seg_end > existing_start
            for existing_start, existing_end in final_segments):
            continue
        final_segments.append((seg_start, seg_end))
        if len(final_segments) >= top_k:
            break

    return final_segments

# -------------------------------
# Save highlight clips
# -------------------------------
def is_valid_mp4(file_path: str) -> bool:
    """Check if FFmpeg can read the file without errors."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", file_path, "-f", "null", "-"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Invalid or corrupted video file: {file_path}")
        print(e.stderr)
        return False

def save_highlight_clips(video_path: str, segments, output_dir=TEMP_CLIP_DIR) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    saved_paths = []
    base = os.path.splitext(os.path.basename(video_path))[0]

    for i, (start, end) in enumerate(segments):
        try:
            out_path = os.path.join(output_dir, f"{base}_clip_{i+1}.mp4")

            # ✅ Re-encode for stable timestamps + CFR
            subprocess.run([
                "ffmpeg",
                "-ss", str(start), "-to", str(end),
                "-i", video_path,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # re-encode video
                "-c:a", "aac", "-b:a", "128k",                       # re-encode audio
                "-r", "30", "-vsync", "cfr",                        # force constant frame rate
                "-y", out_path
            ], check=True)

            saved_paths.append(out_path)
        except Exception as e:
            print(f"⚠️ Failed to save clip {i+1} from {video_path}: {e}")

    return saved_paths


# -------------------------------
# Generate HS highlights
# -------------------------------

def high_school_highlights(full_name: str, class_year: str, max_videos: int = 6) -> List[str]:
    """
    Fetch diverse YouTube video URLs for a HS basketball player.
    Looser filtering: allows partial matches, prefers diversity in titles.
    """
    youtube = set_youtube_key()
    search_request = youtube.search().list(
        part="snippet",
        maxResults=25,
        q=f"{full_name} basketball {class_year}",
        type="video",
        videoEmbeddable="true",
    )
    search_response = search_request.execute()

    candidate_videos = []
    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"].lower()

        # Compute multiple fuzzy scores
        score_name = fuzz.partial_ratio(full_name.lower(), title)
        score_last = fuzz.partial_ratio(full_name.split()[-1].lower(), title)
        score_combo = max(score_name, score_last)

        if score_combo >= 30:  # looser threshold
            candidate_videos.append((score_combo, video_id, title))

    if not candidate_videos:
        return []

    # Sort by score, but also randomize within bins to avoid only top-1
    candidate_videos.sort(key=lambda x: x[0], reverse=True)
    seen_titles = set()
    selected = []
    for _, vid_id, title in candidate_videos:
        if title not in seen_titles:  # crude diversity filter
            selected.append(f"https://www.youtube.com/watch?v={vid_id}")
            seen_titles.add(title)
        if len(selected) >= max_videos:
            break

    return selected


def generate_high_school_highlights(full_name: str, class_year: str, max_videos=6, top_k_per_video=3) -> List[str]:
    urls = high_school_highlights(full_name, class_year, max_videos=max_videos)
    if not urls:
        raise ValueError("No videos found for this player.")

    all_clips: List[str] = []

    for url in urls:
        video_path = None
        try:
            video_path = download_youtube_video(url, output_dir=DOWNLOAD_DIR)
            duration = get_duration(video_path)
            avg_motion = motion_score(video_path, 0, min(30, duration))

            # Only skip if *completely dead*, not just low motion
            if avg_motion < 0.05:
                print(f"⚠️ Skipping dead video: {url}")
                cleanup_files([video_path])
                continue

            segments = extract_highlight_clips(video_path, top_k=top_k_per_video)

            # Guarantee at least one segment per video
            if not segments and duration > 2:
                segments = [(0, min(5, duration))]

            clips = save_highlight_clips(video_path, segments, output_dir=TEMP_CLIP_DIR)
            all_clips.extend(clips)

            cleanup_files([video_path])

        except Exception as e:
            print(f"⚠️ Error processing {url}: {e}")
            if video_path:
                cleanup_files([video_path])

    # Deduplicate only exact duplicates, not near-duplicates
    unique_clips = list(dict.fromkeys(all_clips))
    random.shuffle(unique_clips)

    if not unique_clips:
        raise ValueError("No valid highlight clips found for this player.")

    return unique_clips


# -------------------------------
# Concatenate clips into final reel
# -------------------------------
def make_final_reel(clips: List[str], output_path: str) -> str:
    if not clips:
        raise ValueError("No clips provided.")

    inputs = []
    filters = []
    xfade_cmds = []

    # Input streams
    for i, clip in enumerate(clips):
        inputs.extend(["-i", clip])
        filters.append(
            f"[{i}:v]scale=1280:720,setsar=1[v{i}];"
            f"[{i}:a]aformat=sample_fmts=s16p:sample_rates=44100:channel_layouts=stereo[a{i}]"
        )

    # --- Dynamic offsets ---
    offsets = []
    cur_time = 0
    for i, clip in enumerate(clips[:-1]):  # skip last
        dur = get_duration(clip)
        # offset for xfade: duration minus half fade (0.5s)
        cur_time += max(0.5, dur - 0.5)
        offsets.append(cur_time)

    # --- Build xfade/acrossfade chain ---
    last_v, last_a = "[v0]", "[a0]"
    for i in range(1, len(clips)):
        offset = offsets[i - 1]
        xfade_cmds.append(
            f"{last_v}[v{i}]xfade=transition=fade:duration=0.5:offset={offset}[v{i}out];"
            f"{last_a}[a{i}]acrossfade=d=0.5[a{i}out]"
        )
        last_v, last_a = f"[v{i}out]", f"[a{i}out]"

    filter_complex = ";".join(filters + xfade_cmds)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", last_v, "-map", last_a,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",        # force compatible pixel format
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",               # explicit audio bitrate
        "-shortest",                  # in case audio/video mismatch
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path



# -------------------------------
# Cleanup helper
# -------------------------------
def cleanup_files(files: List[str]):
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"⚠️ Could not delete {f}: {e}")
            
def get_duration(video_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", 
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True
    )
    return float(result.stdout)

# --- Step 4: deduplicate by frame similarity ---
def is_duplicate_clip(clip_a: str, clip_b: str, hash_size=8, threshold=5) -> bool:
    cap_a, cap_b = cv2.VideoCapture(clip_a), cv2.VideoCapture(clip_b)
    ret_a, frame_a = cap_a.read()
    ret_b, frame_b = cap_b.read()
    cap_a.release(); cap_b.release()
    if not (ret_a and ret_b):
        return False
    img_a = Image.fromarray(cv2.cvtColor(frame_a, cv2.COLOR_BGR2RGB))
    img_b = Image.fromarray(cv2.cvtColor(frame_b, cv2.COLOR_BGR2RGB))
    hash_a = imagehash.average_hash(img_a, hash_size=hash_size)
    hash_b = imagehash.average_hash(img_b, hash_size=hash_size)
    return hash_a - hash_b <= threshold

def deduplicate_clips(clips: List[str]) -> List[str]:
    unique_clips = []
    for clip in clips:
        if all(not is_duplicate_clip(clip, existing) for existing in unique_clips):
            unique_clips.append(clip)
    return unique_clips