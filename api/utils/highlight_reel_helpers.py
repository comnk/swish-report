import os
import subprocess
import cv2
import imagehash
import numpy as np
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from pydub import AudioSegment
from PIL import Image
from scenedetect.stats_manager import StatsManager
from typing import List

from core.config import set_gemini_key


DOWNLOAD_DIR = "downloads"
TEMP_CLIP_DIR = "highlights"
FINAL_DIR = "final_reels"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_CLIP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

# -------------------------------
# Download YouTube video (safe filenames)
# -------------------------------
def safe_float(val):
    """Convert LLM output to float, handling dicts like {'seconds': 12}"""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict):
        for key in ("value", "seconds"):
            if key in val:
                return float(val[key])
        return 0.0  # fallback
    try:
        return float(val)
    except Exception:
        return 0.0

def download_youtube_video(url: str, output_dir: str = DOWNLOAD_DIR) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    # Fixed format candidates - remove duration filters as they may not work
    format_candidates = [
        # Try simple quality-based filters first
        "worst[height>=360][height<=720]/worst[height<=720]",
        "bestvideo[height<=720]+bestaudio[abr<=128]/best[height<=720]",
        "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "best[height<=720]",
        "worst",  # Last resort - get anything
    ]

    success = False
    downloaded_file = None
    
    for fmt in format_candidates:
        try:
            print(f"➡️ Trying yt-dlp with format: {fmt}")
            
            cmd = [
                "yt-dlp",
                "-f", fmt,
                "--merge-output-format", "mp4",
                "--restrict-filenames",
                "--no-playlist",
                "--max-filesize", "200M",  # Size limit still works
                "-o", filename_template,
                url,
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            print(f"✅ yt-dlp succeeded with format: {fmt}")
            success = True
            break
            
        except subprocess.TimeoutExpired:
            print(f"⚠️ yt-dlp timeout for format: {fmt}")
            continue
        except subprocess.CalledProcessError as e:
            print(f"⚠️ yt-dlp failed with {fmt}, exit {e.returncode}")
            if e.stderr:
                print(f"stderr: {e.stderr[:200]}...")  # Show first 200 chars
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error with format {fmt}: {e}")
            continue

    if not success:
        # Try one more time with absolutely minimal requirements
        try:
            print("➡️ Final attempt with minimal format requirements")
            result = subprocess.run([
                "yt-dlp",
                "--merge-output-format", "mp4",
                "--restrict-filenames",
                "--no-playlist",
                "-o", filename_template,
                url,
            ], check=True, capture_output=True, text=True, timeout=300)
            success = True
        except Exception as e:
            print(f"⚠️ Final attempt failed: {e}")

    if not success:
        raise RuntimeError(f"yt-dlp failed for {url} with all format candidates")

    # Find the downloaded file
    downloaded_files = []
    if os.path.exists(output_dir):
        downloaded_files = sorted(
            [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
             if f.endswith('.mp4')],
            key=os.path.getmtime,
            reverse=True,
        )
    
    if not downloaded_files:
        raise RuntimeError(f"No MP4 files found in {output_dir} after downloading {url}")

    downloaded_file = downloaded_files[0]
    
    # Check if file exists and is not empty
    if not os.path.exists(downloaded_file) or os.path.getsize(downloaded_file) == 0:
        raise RuntimeError(f"Downloaded file is empty or missing: {downloaded_file}")

    # Check file size and duration AFTER download
    file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
    duration = get_duration(downloaded_file)
    
    print(f"📁 Downloaded: {os.path.basename(downloaded_file)}")
    print(f"📊 Size: {file_size_mb:.1f}MB, Duration: {duration/60:.1f}min")
    
    # Post-download filtering
    if file_size_mb > 250:  # Allow slightly larger files
        print(f"⚠️ File too large: {file_size_mb:.1f}MB, removing")
        os.remove(downloaded_file)
        raise RuntimeError(f"Downloaded file too large: {file_size_mb:.1f}MB")
    
    if duration > 1200:  # 20 minutes max
        print(f"⚠️ Video too long: {duration/60:.1f}min, removing")
        os.remove(downloaded_file)
        raise RuntimeError(f"Video too long: {duration/60:.1f}min")

    print(f"✅ Accepted: {os.path.basename(downloaded_file)} ({file_size_mb:.1f}MB, {duration/60:.1f}min)")
    return downloaded_file  # No remuxing!


# Also add a fallback function to handle video info checking
def check_video_info(url: str) -> dict:
    """
    Get basic video info without downloading to pre-filter videos.
    """
    try:
        result = subprocess.run([
            "yt-dlp",
            "--dump-single-json",
            "--no-playlist",
            url
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            return {
                'duration': info.get('duration', 0),
                'title': info.get('title', ''),
                'filesize': info.get('filesize', 0),
                'width': info.get('width', 0),
                'height': info.get('height', 0)
            }
    except Exception as e:
        print(f"⚠️ Could not get video info for {url}: {e}")
    
    return {'duration': 0, 'title': '', 'filesize': 0, 'width': 0, 'height': 0}


# -------------------------------
# Scene detection
# -------------------------------
def detect_scenes(video_path: str, threshold: float = 30.0):  # Increased threshold for fewer scenes
    """
    Memory-optimized scene detection with higher threshold to reduce memory usage.
    """
    try:
        video = open_video(video_path)
        scene_manager = SceneManager(stats_manager=StatsManager())
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        scene_manager.detect_scenes(video=video)
        scene_list = scene_manager.get_scene_list()
        
        # Limit number of scenes to prevent memory issues
        max_scenes = 50
        if len(scene_list) > max_scenes:
            print(f"⚠️ Too many scenes detected ({len(scene_list)}), using first {max_scenes}")
            scene_list = scene_list[:max_scenes]

        return [(start.get_seconds(), end.get_seconds()) for start, end in scene_list]
    except Exception as e:
        print(f"⚠️ Scene detection failed: {e}")
        return []

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
def motion_density(video_path: str, start: float, end: float, sample_rate: int = 3, motion_thresh: float = 20):
    """
    Memory-optimized motion density calculation.
    """
    start, end = float(start), float(end)
    motion_thresh = float(motion_thresh)
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    ret, prev = cap.read()
    if not ret or prev is None:
        cap.release()
        return {"avg_density": 0.0, "max_density": 0.0, "frame_count": 0}

    # Downscale for memory efficiency
    height, width = prev.shape[:2]
    if width > 640:
        scale = 640.0 / width
        new_width, new_height = int(width * scale), int(height * scale)
        prev = cv2.resize(prev, (new_width, new_height))

    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    frames, density_sum, max_density = 0, 0.0, 0.0
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30)
    step = max(1, int(fps // sample_rate))

    while cap.get(cv2.CAP_PROP_POS_MSEC) < end * 1000:
        for _ in range(step):
            ret, frame = cap.read()
            if not ret or frame is None:
                break
        if not ret or frame is None:
            break

        # Resize frame to match prev
        if frame.shape[:2] != prev.shape[:2]:
            frame = cv2.resize(frame, (prev.shape[1], prev.shape[0]))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        if diff.size == 0:
            continue

        density = float(np.sum(diff > motion_thresh) / diff.size)
        density_sum += density
        max_density = max(max_density, density)
        frames += 1
        prev_gray = gray

    cap.release()
    return {
        "avg_density": float(density_sum / max(frames, 1)),
        "max_density": float(max_density),
        "frame_count": frames
    }

def motion_score(video_path: str, start: float, end: float, sample_rate: int = 3) -> float:
    """
    Memory-optimized motion scoring with lower sample rate and immediate cleanup.
    """
    start, end = float(start), float(end)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0

    # Reduce memory usage by lowering sample rate
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    ret, prev = cap.read()
    if not ret or prev is None:
        cap.release()
        return 0.0

    # Resize frames for motion detection to reduce memory usage
    height, width = prev.shape[:2]
    if width > 640:  # Downscale if too large
        scale = 640.0 / width
        new_width, new_height = int(width * scale), int(height * scale)
        prev = cv2.resize(prev, (new_width, new_height))
    
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    score, frames = 0.0, 0
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30)
    step = max(1, int(fps // sample_rate))

    while cap.get(cv2.CAP_PROP_POS_MSEC) < end * 1000:
        for _ in range(step):
            ret, frame = cap.read()
            if not ret or frame is None:
                break
        if not ret or frame is None:
            break

        # Resize frame to match prev
        if frame.shape[:2] != prev.shape[:2]:
            frame = cv2.resize(frame, (prev.shape[1], prev.shape[0]))
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        if diff.size == 0:
            continue

        score += float(np.mean(diff))
        frames += 1
        prev_gray = gray

    cap.release()
    return float(score / max(frames, 1))

def score_scene(video_path: str, start: float, end: float, audio_spikes: list):
    start, end = float(start), float(end)
    motion = motion_score(video_path, start, end)
    density_data = motion_density(video_path, start, end)
    has_audio = any(float(start) <= float(spike) <= float(end) for spike in audio_spikes)
    duration = float(end) - float(start)

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    ret, frame = cap.read()
    cap.release()
    
    thumbnail_hash = None
    if ret and frame is not None:
        try:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            thumbnail_hash_obj = imagehash.average_hash(img, hash_size=8)
            # Store as string for JSON serialization, but ensure it's a proper hash first
            thumbnail_hash = str(thumbnail_hash_obj)
        except Exception as e:
            print(f"⚠️ Failed to generate thumbnail hash: {e}")
            thumbnail_hash = None

    return {
        "start": float(start),
        "end": float(end),
        "duration": duration,
        "motion_score": motion,
        "avg_density": density_data["avg_density"],
        "max_density": density_data["max_density"],
        "frame_count": density_data["frame_count"],
        "has_audio_spike": has_audio,
        "thumbnail_hash": thumbnail_hash
    }


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
    start, end = float(start), float(end)
    total_extend = 0.0
    low_motion_streak = 0

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, end * 1000)
    ret, prev = cap.read()
    if not ret:
        cap.release()
        return float(end)

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30)
    frame_time = 1.0 / fps
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    while total_extend < max_extend:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = float(np.sum(cv2.absdiff(prev_gray, gray)) / gray.size)
        prev_gray = gray

        cur_time = float(end + total_extend)
        has_audio = any(abs(float(spike) - cur_time) < 0.5 for spike in (audio_spikes or []))

        if diff < motion_thresh and not has_audio:
            low_motion_streak += 1
        else:
            low_motion_streak = 0

        if low_motion_streak >= cooldown_frames:
            break
        total_extend += frame_time

    cap.release()
    return float(min(end + total_extend, end + max_extend))

def extract_highlight_clips(
    video_path: str,
    top_k: int = 3,
    min_len: float = 3,
    max_len: float = 12,
    pad_before: float = 0.3,
    early_skip: float = 10.0,
):
    audio_spikes = detect_audio_spikes(video_path)
    scenes = detect_scenes(video_path)
    candidate_scenes = []

    for start, end in scenes:
        try:
            start = float(safe_float(start))
            end = float(safe_float(end))
        except Exception as e:
            print(f"⚠️ Skipping invalid scene times {start}, {end}: {e}")
            continue

        duration = end - start
        if duration < min_len or end < early_skip:
            continue

        extended_end = extend_scene_to_motion_end(
            video_path, start, end, max_extend=max_len - duration,
            motion_thresh=5.0, cooldown_frames=10, audio_spikes=audio_spikes
        )

        seg_start = max(0.0, start - pad_before)
        seg_end = min(extended_end, start + max_len)

        try:
            motion = float(motion_score(video_path, seg_start, seg_end))
            density_data = motion_density(video_path, seg_start, seg_end)
        except Exception as e:
            print(f"⚠️ Skipping scene due to motion/density error: {e}")
            continue

        duration = seg_end - seg_start
        candidate_scenes.append({
            "start": seg_start,
            "end": seg_end,
            "duration": duration,
            "motion_score": motion,
            "avg_density": float(density_data.get("avg_density", 0.0)),
            "has_audio_spike": any(seg_start <= spike <= seg_end for spike in audio_spikes)
        })

    if not candidate_scenes:
        return []

    # LLM selection with safe float parsing
    client = set_gemini_key()
    try:
        system_prompt = "You are an expert at selecting NBA highlight moments from short video clips."
        user_instructions = (
            f"There are {len(candidate_scenes)} candidate segments from a video.\n"
            "Each segment has start/end times, duration, motion_score, avg_density, and has_audio_spike.\n"
            f"Select the top {top_k} segments most likely to contain exciting basketball highlights.\n"
            "Output MUST be a JSON array of objects with 'start' and 'end' keys, where all values must be floats."
        )

        scene_lines = [
            f"{i}. start: {c['start']:.2f}, end: {c['end']:.2f}, "
            f"duration: {c['duration']:.2f}, motion_score: {c['motion_score']:.2f}, "
            f"avg_density: {c['avg_density']:.3f}, has_audio_spike: {c['has_audio_spike']}"
            for i, c in enumerate(candidate_scenes, start=1)
        ]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_instructions + "\n\nCandidates:\n" + "\n".join(scene_lines)}
        ]

        response = client.chat.completions.create(model="gemini-2.5-pro", messages=messages)
        resp_text = getattr(getattr(response.choices[0], "message", {}), "content", str(response))
        import re, json
        m = re.search(r"\[.*\]", resp_text, flags=re.S)
        selected_segments = []
        if m:
            parsed = json.loads(m.group(0))
            for s in parsed:
                try:
                    start = float(safe_float(s.get("start", 0)))
                    end = float(safe_float(s.get("end", 0)))
                    if end > start:
                        selected_segments.append({"start": start, "end": end})
                except Exception as e:
                    print(f"⚠️ Skipping invalid segment {s}: {e}")
    except Exception as e:
        print(f"⚠️ LLM selection failed, fallback to top avg_density segments: {e}")
        candidate_scenes.sort(key=lambda x: x["avg_density"], reverse=True)
        selected_segments = [{"start": float(c["start"]), "end": float(c["end"])} for c in candidate_scenes[:top_k]]

    # Final safety filter: remove any segment with non-float values
    final_segments = []
    for seg in selected_segments:
        try:
            s, e = float(seg["start"]), float(seg["end"])
            if e > s:
                final_segments.append({"start": s, "end": e})
        except Exception:
            continue

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

    for i, seg in enumerate(segments):
        try:
            start = float(seg["start"])
            end = float(seg["end"])
            if end <= start:
                print(f"⚠️ Skipping invalid clip {i}: start >= end")
                continue
            duration = end - start
        except Exception as e:
            print(f"⚠️ Skipping invalid clip {i}: {e}")
            continue

        out_path = os.path.join(output_dir, f"{base}_clip_{i+1}.mp4")
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
# Concatenate clips into final reel
# -------------------------------
def make_final_reel(clips: List[str], output_path: str) -> str:
    if not clips:
        raise ValueError("No clips provided.")

    import ffmpeg
    preprocessed = []

    # Preprocess clips (scale, pad, fix FPS)
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

    # Get durations safely and filter out invalid clips
    durations = []
    valid_preprocessed = []
    for c in preprocessed:
        dur = get_duration(c)
        try:
            dur = float(dur)
        except Exception:
            dur = 0.0
        if dur > 0.0:
            durations.append(dur)
            valid_preprocessed.append(c)

    if not valid_preprocessed:
        raise ValueError("No valid preprocessed clips to merge.")

    preprocessed = valid_preprocessed

    # Calculate xfade offsets safely
    cumulative = durations[0]
    offsets = []
    for d in durations[1:]:
        offsets.append(round(float(cumulative) - 0.5, 3))  # ensure float
        cumulative = float(cumulative) + float(d) - 0.5

    # Build inputs for ffmpeg CLI
    inputs = []
    for clip in preprocessed:
        inputs.extend(["-i", clip])

    # Build filter_complex
    filter_parts = []
    last_v, last_a = "[0:v]", "[0:a]"
    for i in range(1, len(preprocessed)):
        filter_parts.append(
            f"{last_v}[{i}:v]xfade=transition=fade:duration=0.5:offset={offsets[i-1]}[v{i}out];"
            f"{last_a}[{i}:a]acrossfade=d=0.5[a{i}out]"
        )
        last_v, last_a = f"[v{i}out]", f"[a{i}out]"

    filter_complex = ";".join(filter_parts)

    # Run final ffmpeg merge
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
            
def get_duration(video_path: str) -> float:
    """Return video duration in seconds as float, safely."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        stdout = result.stdout.strip()
        if not stdout:
            print(f"⚠️ ffprobe returned empty duration for {video_path}")
            return 0.0
        # Convert safely, fallback to 0.0
        return float(stdout)
    except Exception as e:
        print(f"⚠️ Could not get duration for {video_path}, defaulting to 0.0: {e}")
        return 0.0

# --- Step 4: deduplicate by frame similarity ---
def is_duplicate_clip(clip_a: str, clip_b: str, hash_size=8, threshold=5) -> bool:
    """
    Check if two video clips are duplicates based on their first frame hash similarity.
    Uses manual Hamming distance calculation to avoid ImageHash subtraction issues.
    """
    cap_a = cv2.VideoCapture(clip_a)
    cap_b = cv2.VideoCapture(clip_b)
    
    # Get first frames
    ret_a, frame_a = cap_a.read()
    ret_b, frame_b = cap_b.read()
    
    cap_a.release()
    cap_b.release()
    
    # If either frame couldn't be read, assume not duplicate
    if not (ret_a and ret_b) or frame_a is None or frame_b is None:
        return False

    try:
        # Convert frames to PIL Images
        img_a = Image.fromarray(cv2.cvtColor(frame_a, cv2.COLOR_BGR2RGB))
        img_b = Image.fromarray(cv2.cvtColor(frame_b, cv2.COLOR_BGR2RGB))

        # Generate hashes and immediately convert to hex strings
        hash_a_obj = imagehash.average_hash(img_a, hash_size=hash_size)
        hash_b_obj = imagehash.average_hash(img_b, hash_size=hash_size)
        
        # Convert to hex strings
        hex_a = str(hash_a_obj)
        hex_b = str(hash_b_obj)
        
        # Calculate Hamming distance manually
        if len(hex_a) != len(hex_b):
            return False
            
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hex_a, hex_b))
        return hamming_distance <= threshold
            
    except Exception as e:
        print(f"⚠️ Failed to compute hash similarity for clips {clip_a}, {clip_b}: {e}")
        return False


def deduplicate_clips(clips: List[str]) -> List[str]:
    """
    Remove duplicate clips based on first frame similarity.
    """
    if not clips:
        return []
        
    unique_clips = []
    
    for clip in clips:
        # Check if this clip is a duplicate of any existing unique clip
        is_duplicate = False
        for existing in unique_clips:
            try:
                if is_duplicate_clip(clip, existing):
                    is_duplicate = True
                    break
            except Exception as e:
                print(f"⚠️ Error comparing clips, assuming not duplicate: {e}")
                # If comparison fails, assume not duplicate to be safe
                continue
        
        if not is_duplicate:
            unique_clips.append(clip)
    
    return unique_clips