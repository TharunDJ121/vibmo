import math
import os
import subprocess
import concurrent.futures
from typing import List, Optional
from vibmo.scene.scene import Scene

class CloudRenderOrchestrator:
    """
    Simulates a Serverless Cloud Render backend (like @remotion/lambda).
    Chunks the timeline into 1-second segments, distributes them across workers, 
    and stitches the resulting video clips together using FFmpeg.
    """
    def __init__(self, output_dir: str = ".vibmo_cloud_cache"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def chunk_timeline(self, scene: Scene, chunk_duration_sec: float = 1.0) -> List[tuple[float, float]]:
        """Splits the scene into (start_time, end_time) chunks."""
        chunks = []
        num_chunks = math.ceil(scene.duration / chunk_duration_sec)
        for i in range(num_chunks):
            start = i * chunk_duration_sec
            end = min(start + chunk_duration_sec, scene.duration)
            chunks.append((start, end))
        return chunks

    def render_chunk_worker(self, scene: Scene, chunk_idx: int, start: float, end: float, output_path: str) -> str:
        """Simulates an AWS Lambda function rendering a specific chunk of time."""
        # In a real cloud backend, we would serialize the scene state, upload assets to S3,
        # and invoke a remote Docker container. For now, we simulate by invoking the local pipeline
        # restricted to the time range.
        
        # We can simulate rendering by just generating a blank video or calling the actual local renderer.
        # But since we just want the architecture, we will use ffmpeg to create a colored clip with text.
        print(f"[Lambda Worker {chunk_idx}] Rendering {start:.2f}s to {end:.2f}s -> {output_path}")
        
        # Mocking the render: generate a video chunk with ffmpeg
        duration = end - start
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            f"-i", f"color=c=blue:s={scene.width}x{scene.height}:d={duration}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(scene.fps),
            output_path
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path

    def submit_jobs(self, scene: Scene, chunks: List[tuple[float, float]]) -> List[str]:
        """Submits chunks to a ThreadPool/ProcessPool (Simulating Lambda parallelism)."""
        chunk_files = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(chunks))) as executor:
            futures = {}
            for i, (start, end) in enumerate(chunks):
                chunk_path = os.path.join(self.output_dir, f"chunk_{i:04d}.mp4")
                chunk_files.append(chunk_path)
                futures[executor.submit(self.render_chunk_worker, scene, i, start, end, chunk_path)] = i
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    idx = futures[future]
                    print(f"Error rendering chunk {idx}: {e}")
                    
        return chunk_files

    def stitch_video(self, chunk_files: List[str], final_output: str):
        """Concatenates all chunk videos into a single MP4 using ffmpeg concat demuxer."""
        list_file_path = os.path.join(self.output_dir, "concat_list.txt")
        with open(list_file_path, "w") as f:
            for chunk_file in chunk_files:
                # ffmpeg requires forward slashes or escaped backslashes, absolute paths are tricky
                # let's just use relative paths if possible, or format carefully.
                abs_path = os.path.abspath(chunk_file).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
                
        print(f"[Orchestrator] Stitching {len(chunk_files)} chunks into {final_output}...")
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            final_output
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[Orchestrator] Cloud Render Complete! -> {final_output}")

    @classmethod
    def run(cls, scene: Scene, output_path: str):
        print(f"[CloudRender] Initializing Cloud Render for Scene ({scene.duration}s)...")
        orchestrator = cls()
        chunks = orchestrator.chunk_timeline(scene, chunk_duration_sec=1.0)
        print(f"[CloudRender] Scene split into {len(chunks)} serverless chunks.")
        
        chunk_files = orchestrator.submit_jobs(scene, chunks)
        orchestrator.stitch_video(chunk_files, output_path)
