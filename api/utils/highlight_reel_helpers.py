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
def download_youtube_video(url: str, output_dir: str = DOWNLOAD_DIR) -> str:
    os.makedirs(output_dir, exist_ok=True)
    try:
        filename_template = os.path.join(output_dir, "%(title)s.%(ext)s")
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",
            "--merge-output-format", "mp4",
            "--restrict-filenames",  # sanitize filenames
            "-o", filename_template,
            url
        ], check=True)
        downloaded_files = sorted(
            [os.path.join(output_dir, f) for f in os.listdir(output_dir)],
            key=os.path.getmtime,
            reverse=True
        )
        return downloaded_files[0]
    except Exception as e:
        print(f"⚠️ Error downloading {url}: {e}")
        raise

# -------------------------------
# Scene detection
# -------------------------------
def detect_scenes(video_path: str, threshold: float = 27.0):
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    return [(start.get_seconds(), end.get_seconds()) for start, end in scene_manager.get_scene_list()]

# -------------------------------
# Motion scoring
# -------------------------------
def motion_score(video_path: str, start: float, end: float, sample_rate: int = 5) -> float:
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
def extract_highlight_clips(
    video_path: str,
    top_k: int = 3,
    min_len: int = 3,
    max_len: int = 12,
    pad_after: float = 3
):
    scenes = detect_scenes(video_path)
    scored_scenes = []

    for start, end in scenes:
        if end - start < min_len:
            continue
        score = motion_score(video_path, start, end)

        # Add small padding after to catch shots
        seg_end = min(end + pad_after, start + max_len)

        scored_scenes.append(((start, seg_end), score))

    scored_scenes.sort(key=lambda x: x[1], reverse=True)
    return [seg for seg, _ in scored_scenes[:top_k]]

# -------------------------------
# Save highlight clips
# -------------------------------
def save_highlight_clips(video_path: str, segments, output_dir=TEMP_CLIP_DIR) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    saved_paths = []
    video = VideoFileClip(video_path)
    duration = video.duration
    base = os.path.splitext(os.path.basename(video_path))[0]

    for i, (start, end) in enumerate(segments):
        try:
            # clamp to duration safely and add tiny padding
            safe_end = min(end, duration - 0.1)
            out_path = os.path.join(output_dir, f"{base}_clip_{i+1}.mp4")
            clip = video.subclipped(start, safe_end)
            clip.write_videofile(out_path, codec="libx264", logger=None)
            clip.close()
            saved_paths.append(out_path)
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