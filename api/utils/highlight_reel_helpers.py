from core.config import set_youtube_key

import os
import time
import random
import subprocess
import cv2
import numpy as np
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from pydub import AudioSegment
from scenedetect.stats_manager import StatsManager
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
    scene_manager = SceneManager(stats_manager=StatsManager())
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video=video)
    scene_list = scene_manager.get_scene_list()

    return [(start.get_seconds(), end.get_seconds()) for start, end in scene_list]

def detect_audio_spikes(video_path: str, window_ms: int = 500, threshold: float = 1.5):
    audio = AudioSegment.from_file(video_path)
    samples = np.array(audio.get_array_of_samples())
    samples = samples.astype(np.float32) / (2**15)  # normalize

    # RMS per window
    step = int(window_ms * audio.frame_rate / 1000)
    rms_values = [np.sqrt(np.mean(samples[i:i+step]**2)) for i in range(0, len(samples), step)]
    mean_rms = np.mean(rms_values)

    # Spike timestamps in seconds
    spikes = [i * (window_ms/1000) for i, rms in enumerate(rms_values) if rms > mean_rms * threshold]
    return spikes

# -------------------------------
# Motion scoring (weighted by scene length)
# -------------------------------
def motion_density(video_path: str, start: float, end: float, sample_rate: int = 5, motion_thresh: float = 20):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    ret, prev = cap.read()
    if not ret:
        cap.release()
        return 0.0
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    frames = 0
    density_sum = 0.0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = int(max(1, fps // sample_rate))
    
    while cap.get(cv2.CAP_PROP_POS_MSEC) < end * 1000:
        for _ in range(step):
            ret, frame = cap.read()
            if not ret:
                break
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        density = np.sum(diff > motion_thresh) / diff.size  # fraction of moving pixels
        density_sum += density
        frames += 1
        prev_gray = gray
    
    cap.release()
    return density_sum / max(frames, 1)

def motion_score(video_path: str, start: float, end: float, sample_rate: int = 5) -> float:
    """
    Compute average motion score of a video segment.
    Uses frame differences at a fixed sampling interval.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0

    # Seek to start time
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)

    ret, prev = cap.read()
    if not ret:
        cap.release()
        return 0.0
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    score, frames = 0.0, 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = int(max(1, fps // sample_rate))  # sample every N frames

    while cap.get(cv2.CAP_PROP_POS_MSEC) < end * 1000:
        # Skip ahead by step frames
        for _ in range(step):
            ret, frame = cap.read()
            if not ret:
                break
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        score += np.mean(diff)  # normalized per pixel
        frames += 1
        prev_gray = gray

    cap.release()
    return score / max(frames, 1)

def score_scene(video_path: str, start: float, end: float, audio_spikes: list):
    motion = motion_score(video_path, start, end)
    density = motion_density(video_path, start, end)
    audio_bonus = 1.0 if any(start <= spike <= end for spike in audio_spikes) else 0.0
    # weighted sum: density helps filter intros/interviews
    return motion * 0.7 + density * 0.5 + audio_bonus * 0.5


# -------------------------------
# Extract highlight scenes
# -------------------------------
def extend_scene_to_motion_end(
    video_path: str,
    start: float,
    end: float,
    max_extend: float = 3.0,
    motion_thresh: float = 5.0,
    cooldown_frames: int = 10,
    audio_spikes: list = None,
):
    """Extend scene end until motion/audio both drop below threshold."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, end * 1000)

    ret, prev = cap.read()
    if not ret:
        cap.release()
        return end

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_time = 1 / fps
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    total_extend = 0.0
    low_motion_streak = 0

    while total_extend < max_extend:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = np.sum(cv2.absdiff(prev_gray, gray)) / gray.size
        prev_gray = gray

        # Check if there's an audio spike near this timestamp
        cur_time = end + total_extend
        has_audio = audio_spikes and any(abs(spike - cur_time) < 0.5 for spike in audio_spikes)

        if diff < motion_thresh and not has_audio:
            low_motion_streak += 1
        else:
            low_motion_streak = 0  # reset if motion or audio active

        if low_motion_streak >= cooldown_frames:
            break

        total_extend += frame_time

    cap.release()
    return min(end + total_extend, end + max_extend)

def extract_highlight_clips(
    video_path: str,
    top_k: int = 3,
    min_len: int = 3,
    max_len: int = 12,
    pad_before: float = 0.3,
    early_skip: float = 10.0,       # skip first 10s by default
    motion_thresh: float = 20,      # pixel difference threshold for motion density
):
    """
    Extract top-k highlight clips from a video.
    Filters out low-density motion and early non-game sections.
    """
    # Precompute audio spikes
    audio_spikes = detect_audio_spikes(video_path)

    scenes = detect_scenes(video_path)
    scored_scenes = []

    for start, end in scenes:
        duration = end - start
        if duration < min_len:
            continue
        if end < early_skip:  # skip very early non-game scenes
            continue

        # Weighted score: motion + motion density + audio spikes
        motion = motion_score(video_path, start, end)
        density = motion_density(video_path, start, end, motion_thresh=motion_thresh)
        audio_bonus = 1.0 if any(start <= spike <= end for spike in audio_spikes) else 0.0
        score = motion * 0.7 + density * 0.5 + audio_bonus * 0.5

        # Dynamic extension to avoid cutting off shots
        extended_end = extended_end = extend_scene_to_motion_end(
            video_path,
            start,
            end,
            max_extend=max_len - duration,
            motion_thresh=5.0,
            cooldown_frames=10,
            audio_spikes=audio_spikes
        )

        seg_start = max(0, start - pad_before)
        seg_end = min(extended_end, start + max_len)

        scored_scenes.append(((seg_start, seg_end), score))

    # Sort scenes by score descending
    scored_scenes.sort(key=lambda x: x[1], reverse=True)

    # Pick top_k non-overlapping segments
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
    import ffmpeg
    os.makedirs(output_dir, exist_ok=True)
    saved_paths = []
    base = os.path.splitext(os.path.basename(video_path))[0]

    for i, (start, end) in enumerate(segments):
        out_path = os.path.join(output_dir, f"{base}_clip_{i+1}.mp4")
        duration = end - start
        try:
            (
                ffmpeg
                .input(video_path, ss=start, t=duration)
                .output(
                    out_path,
                    vcodec='libx264',
                    preset='fast',
                    crf=23,
                    acodec='aac',
                    audio_bitrate='128k',
                    movflags='faststart'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            saved_paths.append(out_path)
        except ffmpeg.Error as e:
            print(f"⚠️ Failed to save clip {i+1} from {video_path}: {e.stderr.decode()}")
    return saved_paths


# -------------------------------
# Generate HS highlights
# -------------------------------
def high_school_highlights(full_name: str, class_year: str, max_videos: int = 15) -> List[str]:
    youtube = set_youtube_key()

    # Rotate queries for more variety
    query_variants = [
        f"{full_name} basketball {class_year}",
        f"{full_name} basketball highlights {class_year}",
        f"{full_name} hoops mixtape {class_year}",
        f"{full_name} class of {class_year} basketball",
        f"{full_name} class of {class_year} basketball camp",
        f"{full_name} class of {class_year} camp highlights",
    ]
    query = random.choice(query_variants)

    exclude_keywords = [
        "interview", "press conference", "announcement", "commitment", "docuseries", "mic", "mic'd"
        "speaks", "talks", "podcast", "intro", "recap", "analysis", "one-on-one", "Interview", "story",
        f"{full_name.lower()}:", "recruitment"
    ]
    full_game_keywords = [
        "full game", "vs", "v.", "replay", "preview", "matchup", "team"
    ]

    # Collect across multiple pages to diversify results
    candidate_videos = []
    next_page_token = None
    for _ in range(3):  # fetch up to 3 pages (can tune)
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
            candidate_videos.append((score_name, video_id, title))

        if not next_page_token:
            break  # no more pages

    if not candidate_videos:
        return []

    # Add randomness that changes per run
    random.seed(time.time())

    # Shuffle and sample
    random.shuffle(candidate_videos)
    weights = [max(score, 1) for score, _, _ in candidate_videos]
    chosen = random.choices(
        candidate_videos,
        weights=weights,
        k=min(max_videos * 4, len(candidate_videos))  # sample bigger pool
    )

    # Deduplicate and limit
    seen = set()
    selected = []
    for _, vid_id, _ in chosen:
        if vid_id not in seen:
            selected.append(f"https://www.youtube.com/watch?v={vid_id}")
            seen.add(vid_id)
        if len(selected) >= max_videos:
            break

    return selected

def generate_high_school_highlights(full_name: str, class_year: str, max_videos=15, top_k_per_video=3) -> List[str]:
    urls = high_school_highlights(full_name, class_year, max_videos=max_videos)
    if not urls:
        raise ValueError("No videos found for this player.")

    all_clips: List[str] = []

    for url in urls:
        video_path = None
        try:
            video_path = download_youtube_video(url, output_dir=DOWNLOAD_DIR)
            duration = get_duration(video_path)

            # Quick early check for dead videos (first 10 seconds)
            avg_motion = motion_score(video_path, 0, min(10, duration))
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

    # Deduplicate by near-duplicate frames (optional)
    unique_clips = deduplicate_clips(all_clips)
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

    import ffmpeg
    preprocessed = []
    for i, clip in enumerate(clips):
        tmp = clip.replace(".mp4", "_prep.mp4")
        (
            ffmpeg
            .input(clip)
            .output(
                tmp,
                vf='scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1',
                r=30,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='aac',
                audio_bitrate='192k',
                ac=2
            )
            .overwrite_output()
            .run(quiet=True)
        )
        preprocessed.append(tmp)

    # Build xfade via CLI (subprocess) using preprocessed clips
    inputs = []
    filter_parts = []
    last_v, last_a = "[0:v]", "[0:a]"
    durations = [get_duration(c) for c in preprocessed]
    cumulative = durations[0]
    offsets = []
    for d in durations[1:]:
        offsets.append(round(cumulative - 0.5, 3))  # fade 0.5s
        cumulative += d - 0.5

    for i, clip in enumerate(preprocessed):
        inputs.extend(["-i", clip])

    for i in range(1, len(preprocessed)):
        filter_parts.append(
            f"{last_v}[{i}:v]xfade=transition=fade:duration=0.5:offset={offsets[i-1]}[v{i}out];"
            f"{last_a}[{i}:a]acrossfade=d=0.5[a{i}out]"
        )
        last_v, last_a = f"[v{i}out]", f"[a{i}out]"

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", last_v, "-map", last_a,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
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