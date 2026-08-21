import pytest
import math
from vibmo.product.hardware.hw_cyberdeck_terminal_suite import (
    CyberdeckMechanicalKeyboard,
    PopUpLcdScreen,
    IndustrialBumperCase,
    PatchCablesAndAntenna
)

class MockContext:
    def __init__(self):
        self.operations = []
        self.saved_states = 0
        self.matrix = [(0, 0)]
        self.sources = []
        self.current_path = []
        self.line_width = 1.0

    def save(self):
        self.saved_states += 1
        self.matrix.append(self.matrix[-1])
        self.operations.append("save")

    def restore(self):
        if self.saved_states > 0:
            self.saved_states -= 1
            self.matrix.pop()
        self.operations.append("restore")

    def translate(self, tx, ty):
        curr_tx, curr_ty = self.matrix[-1]
        self.matrix[-1] = (curr_tx + tx, curr_ty + ty)
        self.operations.append(f"translate({tx:.2f}, {ty:.2f})")

    def rotate(self, angle):
        self.operations.append(f"rotate({angle:.2f})")

    def arc(self, xc, yc, radius, angle1, angle2):
        self.operations.append(f"arc({xc:.2f}, {yc:.2f}, {radius:.2f})")

    def rectangle(self, x, y, width, height):
        self.operations.append(f"rectangle({x:.2f}, {y:.2f}, {width:.2f}, {height:.2f})")

    def new_path(self):
        self.current_path = []
        self.operations.append("new_path")

    def move_to(self, x, y):
        self.current_path.append((x, y))
        self.operations.append(f"move_to({x:.2f}, {y:.2f})")

    def line_to(self, x, y):
        self.current_path.append((x, y))
        self.operations.append(f"line_to({x:.2f}, {y:.2f})")

    def close_path(self):
        self.operations.append("close_path")

    def set_source_rgba(self, r, g, b, a):
        self.sources.append((r, g, b, a))
        self.operations.append("set_source_rgba")

    def set_line_width(self, w):
        self.line_width = w
        self.operations.append(f"set_line_width({w:.2f})")

    def fill(self):
        self.operations.append("fill")

    def stroke(self):
        self.operations.append("stroke")


def test_cyberdeck_mechanical_keyboard():
    keyboard = CyberdeckMechanicalKeyboard(width=600, height=200)
    assert keyboard.local_bounds() == (0.0, 0.0, 600.0, 200.0)

    ctx = MockContext()
    keyboard.draw(ctx, time=0.0)

    # Check for chassis and handle base
    rects = [op for op in ctx.operations if op.startswith("rectangle")]
    assert len(rects) > 2 # At least chassis + handle + keys
    assert ctx.operations.count("fill") == len(rects)

    # Calculate expected keys: cols = (600 - 20) / 50 = 11, rows = (200 - 20) / 50 = 3 => 33 keys + 2 (base/handle) = 35 rects
    assert len(rects) == 35


def test_pop_up_lcd_screen():
    screen = PopUpLcdScreen(width=500, height=250)
    assert screen.local_bounds() == (0.0, 0.0, 500.0, 250.0)

    ctx = MockContext()
    screen.draw(ctx, time=0.0)

    rects = [op for op in ctx.operations if op.startswith("rectangle")]
    # 2 hinges, 1 bezel, 1 screen glow
    assert len(rects) == 4
    assert ctx.operations.count("fill") == 4


def test_industrial_bumper_case():
    case = IndustrialBumperCase(width=700, height=400)
    assert case.local_bounds() == (0.0, 0.0, 700.0, 400.0)

    ctx = MockContext()
    case.draw(ctx, time=0.0)

    rects = [op for op in ctx.operations if op.startswith("rectangle")]
    # 1 body, 1 hazard base, 10 hazard stripes, 4 bumpers = 16
    assert len(rects) == 16
    assert ctx.operations.count("fill") == 16


def test_patch_cables_and_antenna():
    cable_antenna = PatchCablesAndAntenna()
    ctx = MockContext()

    # time 0.0
    cable_antenna.draw(ctx, time=0.0)

    # 5 arcs for coiled cable + 1 arc for antenna tip
    arcs = [op for op in ctx.operations if op.startswith("arc")]
    assert len(arcs) == 6

    # 5 strokes for cable
    assert ctx.operations.count("stroke") == 5

    # Rotation test with time > 0
    ctx2 = MockContext()
    cable_antenna.draw(ctx2, time=math.pi / 2) # sin(pi/2) = 1 => 0.5 angle

    rotations1 = [op for op in ctx.operations if op.startswith("rotate")]
    rotations2 = [op for op in ctx2.operations if op.startswith("rotate")]

    assert rotations1 != rotations2
