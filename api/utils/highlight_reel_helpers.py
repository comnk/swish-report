from utils.hs_helpers import high_school_highlights

import os
import subprocess
import cv2
import numpy as np
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy import *
from typing import List

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
    """
    Compute average motion score of a video segment.
    Weighted by scene duration for prioritizing longer, active highlights.
    """
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

    avg_score = score / max(frames, 1)
    # Weight by scene duration to prioritize longer, active scenes
    weighted_score = avg_score * (end - start)
    return weighted_score


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

    if not is_valid_mp4(video_path):
        print(f"⚠️ Skipping invalid video: {video_path}")
        return []

    try:
        video = VideoFileClip(video_path)
    except Exception as e:
        print(f"⚠️ MoviePy could not open video {video_path}: {e}")
        return []

    duration = video.duration
    base = os.path.splitext(os.path.basename(video_path))[0]

    for i, (start, end) in enumerate(segments):
        try:
            safe_end = min(end, duration)
            out_path = os.path.join(output_dir, f"{base}_clip_{i+1}.mp4")
            clip = video.subclipped(start, safe_end)
            clip.write_videofile(out_path, codec="libx264", logger=None)
            clip.close()

            # Optional: remux each clip to fix MP4 header issues
            remuxed_path = out_path.replace(".mp4", "_fixed.mp4")
            subprocess.run([
                "ffmpeg", "-i", out_path, "-c", "copy", remuxed_path, "-y"
            ], check=True)
            os.remove(out_path)  # replace original
            saved_paths.append(remuxed_path)

        except Exception as e:
            print(f"⚠️ Failed to save clip {i+1} from {video_path}: {e}")

    video.close()
    return saved_paths


# -------------------------------
# Generate HS highlights
# -------------------------------
def generate_high_school_highlights(full_name: str, class_year: str, max_videos=1, top_k=3) -> List[str]:
    urls = high_school_highlights(full_name, class_year, max_videos=max_videos)
    if not urls:
        raise ValueError("No videos found for this player.")

    clips = []
    for url in urls:
        try:
            video_path = download_youtube_video(url)
            segments = extract_highlight_clips(video_path, top_k=top_k)
            clips.extend(save_highlight_clips(video_path, segments, output_dir=TEMP_CLIP_DIR))
        except Exception as e:
            print(f"⚠️ Skipping video {url} due to error: {e}")
    return clips

# -------------------------------
# Concatenate clips into final reel
# -------------------------------
def make_final_reel(clips: List[str], output_path=os.path.join(FINAL_DIR, "final_reel.mp4"), cleanup=True) -> str:
    video_clips = [VideoFileClip(c) for c in clips]
    final = concatenate_videoclips(video_clips, method="compose")
    final.write_videofile(output_path, codec="libx264", logger=None)
    for clip in video_clips:
        clip.close()
    final.close()

    if cleanup:
        for c in clips:
            try:
                os.remove(c)
            except Exception as e:
                print(f"⚠️ Could not delete {c}: {e}")

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