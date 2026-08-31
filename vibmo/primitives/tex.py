import os
import tempfile
import subprocess
from typing import Any, Optional
from vibmo.scene.node import Node
from vibmo.primitives.path import Path
from vibmo.core.vector import Vector2D

class TexMath(Node):
    """
    Renders LaTeX mathematical formulas using system 'latex' and 'dvisvgm'.
    Outputs a highly precise vector graphic that can be scaled and morphed.
    Requires MiKTeX, TeXLive, or MacTeX installed on the system.
    """
    
    def __init__(
        self,
        tex_string: str,
        position: Vector2D = (960, 540),
        scale: float = 3.0,
        **kwargs: Any
    ):
        super().__init__(position=position, **kwargs)
        self.tex_string = tex_string
        self.scale_factor = scale
        self.svg_path = self._compile_tex_to_svg(tex_string)
        
        # Load the compiled SVG as a series of Vibmo Paths
        if self.svg_path and os.path.exists(self.svg_path):
            import svgelements
            try:
                svg = svgelements.SVG.parse(self.svg_path)
                for element in svg.elements():
                    if isinstance(element, svgelements.Path):
                        # Convert each glyph path to a Vibmo animatable Path
                        p = Path(d=element.d(), stroke_width=0, fill="white")
                        p.position.set(0, 0)
                        self.add(p)
            except Exception as e:
                print(f"[TexMath] Failed to parse SVG: {e}")
                
    def _compile_tex_to_svg(self, tex_string: str) -> Optional[str]:
        """
        Writes a standalone LaTeX document, compiles it to DVI, and converts it to SVG.
        """
        temp_dir = tempfile.gettempdir()
        base_name = f"vibmo_tex_{hash(tex_string)}"
        tex_file = os.path.join(temp_dir, f"{base_name}.tex")
        dvi_file = os.path.join(temp_dir, f"{base_name}.dvi")
        svg_file = os.path.join(temp_dir, f"{base_name}.svg")
        
        # Avoid recompiling if cached
        if os.path.exists(svg_file):
            return svg_file
            
        doc = f"""\\documentclass[preview, varwidth]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\begin{{document}}
$ {tex_string} $
\\end{{document}}"""

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(doc)
            
        try:
            # 1. Compile to DVI
            subprocess.run(
                ["latex", "-interaction=batchmode", f"-output-directory={temp_dir}", tex_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            # 2. Convert to SVG
            subprocess.run(
                ["dvisvgm", dvi_file, "-n", "-e", f"-o{svg_file}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return svg_file
        except FileNotFoundError:
            print("[TexMath] Missing 'latex' or 'dvisvgm'. Please install TeXLive or MiKTeX.")
            return None
        except subprocess.CalledProcessError:
            print("[TexMath] LaTeX compilation failed. Check syntax.")
            return None
