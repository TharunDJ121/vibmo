from vibmo.agent_api import *
from vibmo.render.export import Exporter

scene = Scene(width=1280, height=720, duration=4.5, fps=30)
box = Rect(width=400, height=400, fill=colors.EMERALD)
box.at(640, 360)
scene.add(box)

# Export using lambda engine
output_file = "cloud_render_output.mp4"
Exporter.export(scene, output_path=output_file, quality="preview", engine="lambda")

print("Test script finished. Verify the output MP4 was built successfully.")
