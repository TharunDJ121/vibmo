"""
FastAPI Router and WebSocket Protocol for Vibmo Studio Pro.
Supports running without scripts, in-studio script creation & execution, and AI prompt generation.
"""

from __future__ import annotations
import json
import os
import threading
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from vibmo.studio.state import StudioState, DEFAULT_STARTER_SCRIPT
from vibmo.studio.frame_server import FrameServer
from vibmo.studio.audio_server import AudioServer
from vibmo.studio.pages.fusion import FusionGraph
from vibmo.studio.pages.fairlight import FAIRLIGHT_FOLEY_SOUNDBOARD
from vibmo.studio.pages.deliver import EXPORT_PRESETS


class KeyUpdateRequest(BaseModel):
    provider: str
    key: str


class AiEditRequest(BaseModel):
    prompt: str
    code: Optional[str] = None
    target_scene: Optional[int] = None


class AiGenerateRequest(BaseModel):
    prompt: str


STUDIO_STARTER_TEMPLATES = [
    {
        "id": "saas_launch",
        "name": "🚀 SaaS Metric Launch",
        "description": "Dark-mode product card with $148K MRR counter, sparkles, and area chart.",
        "code": DEFAULT_STARTER_SCRIPT,
    },
    {
        "id": "kinetic_typography",
        "name": "✨ Kinetic Typography Reveal",
        "description": "Dynamic character and word wave animations with spring deceleration.",
        "code": '''from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, duration=3.5, background=colors.SLATE_950)

title = KineticText("ACCELERATE YOUR VISION", font_size=56, bold=True, color=colors.CYAN)
title.at(300, 480)
subtitle = KineticText("High-performance Motion Design in Python", font_size=28, color=colors.SLATE_400)
subtitle.at(300, 560)

scene.add(title, subtitle)
scene.add_post_fx(Vignette(intensity=0.3), FilmGrain(amount=0.02))

@scene.animate
def main():
    yield title.reveal_characters(stagger=0.03)
    yield subtitle.fade_up(offset=25, duration=0.6)
    yield scene.wait(1.5)
''',
    },
    {
        "id": "product_dashboard",
        "name": "📊 Product KPI Dashboard",
        "description": "Multi-card KPI dashboard with growing bar charts and timeline views.",
        "code": '''from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, duration=4.0, background=colors.DARK_NAVY)

# KPI Stat Card
card1 = StatCard(title="Active Nodes", value="1,420", change="+24.8%", is_positive=True, position=(180, 180), width=360)
card2 = StatCard(title="Latency (p99)", value="4.2ms", change="-18.2%", is_positive=True, position=(580, 180), width=360)

# Bar Chart
chart = BarChart(data=[45, 62, 85, 92, 110, 145], labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"], width=760, height=320, position=(180, 380), color=colors.INDIGO)

scene.add(card1, card2, chart)

@scene.animate
def main():
    yield scene.all(card1.pop_in(), card2.pop_in(delay=0.15))
    yield chart.grow_bars(duration=1.2, stagger=0.08)
    yield scene.wait(1.5)
''',
    },
    {
        "id": "blank_canvas",
        "name": "🎨 Blank Creative Canvas",
        "description": "Clean canvas ready for custom design primitives.",
        "code": '''from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=3.0, background=colors.DARK_NAVY)

# Add your layers and semantic components here
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(400, 300))
title = KineticText("Hello Motion Graphics", font_size=36, bold=True)
card.add(title)
scene.add(card)

@scene.animate
def main():
    yield card.pop_in()
    yield scene.wait(1.5)
''',
    },
]


class RunScriptRequest(BaseModel):
    code: str


class SaveScriptRequest(BaseModel):
    code: str
    path: Optional[str] = None


class PromptGenerateRequest(BaseModel):
    prompt: str
    duration: float = 4.0


def create_studio_app(scene: Optional[Any] = None, script_path: Optional[str] = None) -> FastAPI:
    """Factory creating the complete Vibmo Studio Pro application."""
    app = FastAPI(title="Vibmo Studio Pro", version="3.1.0")

    state = StudioState(scene=scene, script_path=script_path)
    frame_server = FrameServer(state.scene)
    audio_server = AudioServer(state.scene)

    active_websockets: List[WebSocket] = []
    ws_lock = threading.Lock()

    # Prewarm timeline in background
    frame_server.prewarm_timeline(scale=0.5, max_frames=240)

    # Static assets directory
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    async def broadcast_ws(payload: Dict[str, Any]):
        msg = json.dumps(payload)
        with ws_lock:
            sockets = list(active_websockets)
        for ws in sockets:
            try:
                await ws.send_text(msg)
            except Exception:
                pass

    @app.get("/", response_class=HTMLResponse)
    async def get_index():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Vibmo Studio Pro — Static files missing</h1>"

    @app.get("/api/meta")
    async def get_metadata(time: float = 0.0):
        return state.get_metadata(current_time=time)

    # In-Studio Script Management API
    @app.get("/api/script")
    async def get_script():
        return {
            "code": state.current_code,
            "script_path": state.script_path,
        }

    @app.post("/api/script/run")
    async def run_script(req: RunScriptRequest):
        ok, err, meta = state.execute_python_code(req.code)
        if not ok:
            return JSONResponse(status_code=400, content={"success": False, "error": err})

        frame_server.update_scene(state.scene)
        audio_server.update_scene(state.scene)
        await broadcast_ws(meta)
        return {"success": True, "meta": meta}

    @app.post("/api/script/save")
    async def save_script(req: SaveScriptRequest):
        target_path = req.path or state.script_path or "scene.py"
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(req.code)
            state.script_path = os.path.abspath(target_path)
            state.current_code = req.code
            return {"success": True, "path": state.script_path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/templates")
    async def get_templates():
        return {"templates": STUDIO_STARTER_TEMPLATES}

    @app.post("/api/prompt/generate")
    async def generate_from_prompt(req: PromptGenerateRequest):
        try:
            from vibmo.ai.agent_scene import AgentSceneGenerator
            gen_scene = AgentSceneGenerator.generate_from_prompt(req.prompt, duration=req.duration)
            # Reconstruct clean code representation
            state.scene = gen_scene
            frame_server.update_scene(state.scene)
            audio_server.update_scene(state.scene)
            meta = state.get_metadata(current_time=0.0)
            await broadcast_ws(meta)
            return {
                "success": True,
                "meta": meta,
                "prompt": req.prompt,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/audio")
    async def get_audio_stream():
        from fastapi.responses import Response
        import wave
        import io
        
        audio_path = audio_server.get_audio_filepath()
        if audio_path and os.path.exists(audio_path):
            media_type = "audio/wav" if audio_path.endswith(".wav") else "audio/mpeg"
            return FileResponse(audio_path, media_type=media_type)
            
        # Return a generated silent 100ms WAV file so HTML5 Audio player remains happy
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b'\x00\x00' * 4410)
            
        return Response(content=buf.getvalue(), media_type="audio/wav")

    @app.get("/api/waveform")
    async def get_waveform():
        peaks = audio_server.extract_waveform_peaks(num_points=400)
        return {"peaks": peaks, "duration": state.scene.duration}

    @app.get("/api/sfx/play/{sound_name}")
    async def get_sfx_stream(sound_name: str):
        from vibmo.audio.sfx import ProceduralSFX
        from scipy.io import wavfile
        import io
        import numpy as np
        from fastapi.responses import Response

        try:
            samples = ProceduralSFX.generate(sound_name)
            samples_int = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
            buf = io.BytesIO()
            wavfile.write(buf, 48000, samples_int)
            return Response(content=buf.getvalue(), media_type="audio/wav")
        except Exception:
            raise HTTPException(status_code=404, detail=f"Unknown sound: {sound_name}")

    @app.get("/api/fusion")
    async def get_fusion_graph():
        return FusionGraph.serialize_scene(state.scene)

    @app.get("/api/soundboard")
    async def get_soundboard():
        return {"sounds": FAIRLIGHT_FOLEY_SOUNDBOARD}

    @app.get("/api/presets")
    async def get_presets():
        return {"presets": EXPORT_PRESETS}

    @app.get("/api/export_code")
    async def get_export_code():
        return {"code": state.export_python_code()}

    # =========================================================================
    # AI DIRECTOR & API KEY ATTACHMENT ENDPOINTS (LANGGRAPH POWERED)
    # =========================================================================

    @app.get("/api/settings/keys")
    async def get_settings_keys():
        from vibmo.ai.keys import get_all_keys
        return {"providers": get_all_keys()}

    @app.post("/api/settings/keys")
    async def update_settings_key(req: KeyUpdateRequest):
        from vibmo.ai.keys import save_key, test_key_connection
        success, msg = test_key_connection(req.provider, req.key)
        if success:
            save_key(req.provider, req.key)
            return {"status": "ok", "message": msg}
        else:
            # Still allow saving if user confirms
            save_key(req.provider, req.key)
            return {"status": "warning", "message": msg}

    @app.post("/api/ai/edit")
    async def ai_surgical_edit(req: AiEditRequest):
        from vibmo.ai.graph import run_motion_edit
        current_code = req.code or state.export_python_code() or DEFAULT_STARTER_SCRIPT
        result = run_motion_edit(prompt=req.prompt, current_code=current_code)
        
        updated_code = result.get("updated_code", current_code)
        if updated_code:
            state.load_python_code(updated_code)
            frame_server.clear_cache()
            
        return {
            "status": "ok" if result.get("is_valid", True) else "error",
            "message": result.get("response_message", "Edit applied"),
            "code": updated_code,
            "logs": result.get("execution_log", []),
            "errors": result.get("validation_errors", []),
        }

    @app.post("/api/ai/generate")
    async def ai_generate_story(req: AiGenerateRequest):
        from vibmo.ai.graph import run_motion_edit
        result = run_motion_edit(prompt=req.prompt, current_code="")
        
        updated_code = result.get("updated_code", "")
        if updated_code:
            state.load_python_code(updated_code)
            frame_server.clear_cache()
            
        return {
            "status": "ok" if result.get("is_valid", True) else "error",
            "message": result.get("response_message", "Sequence generated"),
            "code": updated_code,
            "logs": result.get("execution_log", []),
        }

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        with ws_lock:
            active_websockets.append(websocket)
        try:
            while True:
                msg_text = await websocket.receive_text()
                try:
                    data = json.loads(msg_text)
                except Exception:
                    continue

                msg_type = data.get("type")

                try:
                    if msg_type == "init":
                        meta = state.get_metadata(current_time=0.0)
                        await websocket.send_text(json.dumps(meta))

                    elif msg_type == "get_frame":
                        t = float(data.get("time", 0.0))
                        scale = float(data.get("scale", 0.5))
                        quality = int(data.get("quality", 70))
                        
                        b64_str = frame_server.get_frame_base64(time=t, scale=scale, quality=quality)
                        
                        await websocket.send_text(json.dumps({
                            "type": "frame",
                            "time": t,
                            "image": b64_str,
                        }))

                    elif msg_type == "run_script":
                        code = data.get("code", "")
                        ok, err, meta = state.execute_python_code(code)
                        if ok:
                            frame_server.update_scene(state.scene)
                            audio_server.update_scene(state.scene)
                            await broadcast_ws(meta)
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "script_error",
                                "error": err,
                            }))

                    elif msg_type == "set_param":
                        p_name = data.get("name")
                        p_val = data.get("value")
                        state.set_param(p_name, p_val)
                        frame_server.clear_cache()
                        await websocket.send_text(json.dumps({
                            "type": "param_updated",
                            "name": p_name,
                            "value": p_val,
                        }))

                    elif msg_type == "set_node_prop":
                        node_id = data.get("node_id")
                        prop = data.get("prop")
                        val = data.get("value")
                        state.set_node_property(node_id, prop, val)
                        frame_server.clear_cache()

                    elif msg_type == "set_color_grade":
                        state.set_color_grade(
                            lift=data.get("lift"),
                            gamma=data.get("gamma"),
                            gain=data.get("gain"),
                            exposure=data.get("exposure"),
                            contrast=data.get("contrast"),
                            saturation=data.get("saturation"),
                            temperature=data.get("temperature"),
                            tint=data.get("tint"),
                        )
                        frame_server.clear_cache()
                        await websocket.send_text(json.dumps({
                            "type": "color_grade_updated",
                            "status": "ok",
                        }))

                    elif msg_type == "start_render":
                        preset_id = data.get("preset", "mp4_high")
                        out_name = f"export_{preset_id}.mp4"
                        quality = "high" if "high" in preset_id else "fast"
                        
                        def _do_render():
                            try:
                                state.scene.render(output_path=out_name, quality=quality, show_progress=False)
                            except Exception as render_err:
                                print(f"[Studio Render Error] {render_err}")
                        
                        threading.Thread(target=_do_render, daemon=True).start()
                        await websocket.send_text(json.dumps({
                            "type": "render_started",
                            "output": out_name,
                        }))


                except Exception as inner_err:
                    # Never let individual message errors crash the websocket
                    print(f"[Studio WS Error] {inner_err}")

        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[Studio WS Disconnected] {e}")
        finally:
            with ws_lock:
                if websocket in active_websockets:
                    active_websockets.remove(websocket)


    return app


def launch_studio(
    scene: Optional[Any] = None,
    script_path: Optional[str] = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Launches the interactive Vibmo Studio Pro server in default browser."""
    import webbrowser
    import uvicorn
    app = create_studio_app(scene=scene, script_path=script_path)
    webbrowser.open(f"http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="warning")
