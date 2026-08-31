"""
✦ Master Cinematic 1:1 Recreation of 'Claude Sonnet 4.6 Adaptive' Teaser (Video-90313.mp4)
Total Duration: 11.6s @ 30 FPS (1276x718)
Featuring Dynamic Camera Zoom/Dolly, Macro Button Framing, Syntax-Highlighted Code Void, and Kinetic Typography.
"""

from motio.agent_api import *

# 1. Initialize Master Scene (1276x718 @ 30 FPS, dark aesthetic)
scene = Scene(
    width=1276,
    height=718,
    fps=30,
    duration=11.6,
    background=Color.from_hex("#090807"),
)

# 2. Dynamic Volumetric Warm Backlight Halo
backlight = Circle(
    radius=500.0,
    position=(638, 360),
    fill=RadialGradient(
        center=(0.0, 0.0),
        radius=500.0,
        stops=[
            (0.0, Color.from_hex("#d97757").with_alpha(0.24)),
            (0.45, Color.from_hex("#d97757").with_alpha(0.08)),
            (1.0, Color.TRANSPARENT),
        ],
    ),
)
scene.add(backlight)

# 3. Post-Processing Pipeline: 4-Octave Bloom, 32-bit Color Grade, Power Vignette & Film Grain
scene.add_post_fx(
    Bloom(threshold=0.50, intensity=0.70, radius=24.0),
    Vignette(intensity=0.40, radius=0.65),
    FilmGrain(amount=0.012, luminance_weighted=True),
    ColorGrade(contrast=1.15, saturation=1.08, temperature=0.14, color_boost=0.10),
)

# =========================================================================
# SCENE 1: Star Logo & Centered "Claude" Intro (0.0s - 1.8s)
# =========================================================================
scene1_group = FlexContainer(direction="row", gap=24, position=(638, 359), anchor=(0.5, 0.5), align_items="center")
star_logo = AnthropicAsterisk(radius=38.0, spokes=12, spoke_width=6.0, color=Color.from_hex("#d97757"))
claude_title = Text("Claude", font_size=68, font_family="Playfair Display", color=Color.from_hex("#f8fafc"))
claude_title.opacity.set(0.0)

scene1_group.add(star_logo, claude_title)
scene.add(scene1_group)

# =========================================================================
# SCENE 2 & 3: "Good morning, Elon" + Chat Box + Typewriter (1.8s - 5.4s)
# =========================================================================
scene2_group = Node(position=(0, 0))
scene2_group.opacity = Signal(0.0, "scene2_group.opacity")

greeting = FlexContainer(direction="row", gap=18, position=(638, 220), anchor=(0.5, 0.5), align_items="center")
star_small = AnthropicAsterisk(radius=22.0, spokes=12, spoke_width=4.0, color=Color.from_hex("#d97757"))
greeting_text = Text("Good morning, Elon", font_size=46, font_family="Playfair Display", color=Color.from_hex("#f8fafc"))
greeting.add(star_small, greeting_text)

# Prominent Dark Slate Chat Input Bar
chat_bar = GlassCard(
    direction="column",
    gap=18,
    padding=24,
    corner_radius=22,
    position=(218, 300),
    width=840,
    height=135,
    fill=Color.from_hex("#171513").with_alpha(0.94),
    stroke=Color.from_hex("#38322d"),
    stroke_width=1.5,
    backdrop_blur=20.0,
    specular_rim=True,
)

prompt_input = TextTypewriter(
    "Help me build an app that prints money",
    font_size=24,
    font_family="Inter",
    color=Color.from_hex("#f1f5f9"),
)

# Chat Bar Footer
chat_footer = FlexContainer(direction="row", justify_content="space_between", align_items="center", width=790)
plus_icon = Text("+", font_size=26, bold=True, color=Color.from_hex("#78716c"))

footer_right = FlexContainer(direction="row", gap=16, align_items="center")
model_badge = Text("Sonnet 4.6 Adaptive  ∨", font_size=15, font_family="Inter", color=Color.from_hex("#a8a29e"))

# Terracotta Up-Arrow Submit Button
submit_btn = RoundedRect(
    width=40,
    height=40,
    corner_radius=10,
    fill=Color.from_hex("#d97757"),
    position=(0, 0),
)
arrow_icon = Text("↑", font_size=22, bold=True, color=Color.WHITE, position=(13, 4))
submit_btn.add(arrow_icon)

footer_right.add(model_badge, submit_btn)
chat_footer.add(plus_icon, footer_right)
chat_bar.add(prompt_input, chat_footer)

scene2_group.add(greeting, chat_bar)
scene.add(scene2_group)

# =========================================================================
# SCENE 4: Macro Button Framing & Vector Hand Cursor (5.4s - 6.6s)
# =========================================================================
hand_cursor = Cursor(position=(980, 480), size=44.0, style="hand")
hand_cursor.opacity = Signal(0.0, "hand_cursor.opacity")

click_ripple = ClickIndicator(position=(992, 388), color=Color.from_hex("#d97757"), max_radius=60.0)
click_ripple.opacity = Signal(0.0, "click_ripple.opacity")

scene.add(hand_cursor, click_ripple)

# =========================================================================
# SCENE 5: Cinematic Syntax-Highlighted Streaming Code Void (6.6s - 9.0s)
# =========================================================================
code_group = Node(position=(240, 140))
code_group.opacity = Signal(0.0, "code_group.opacity")

c_code_text = (
    "struct User {\n"
    "    var sec[40], char name[50];\n"
    "    int score;\n"
    "};\n\n"
    "int generateScore() {\n"
    "    return rand() % 100 + 1;\n"
    "    users[currentProcessingIndex].Processed += 1;\n"
    "    printf(\"Transaction Completed For User\\n\");\n"
    "}\n\n"
    "void displayUsers(struct User users[], int count) {\n"
    "    printf(\"\\n=== USER LIST ===\\n\");\n"
    "    for (int i = 0; i < count; i++) {\n"
    "        printf(\"Id: %d, Name: %s | Score: %d\\n\",\n"
    "            i + 1, users[i].name, users[i].score);\n"
    "    }\n"
    "}\n\n"
    "void findTopUser(struct User users[], int count) {\n"
    "    int maxIndex = 0;\n"
    "    for (int i = 1; i < count; i++) {\n"
    "        if (users[i].score > users[maxIndex].score) {\n"
    "            maxIndex = i;\n"
    "        }\n"
    "    }\n"
    "}"
)

code_block = SyntaxHighlightCode(
    c_code_text,
    font_size=20.0,
    font_family="Consolas",
    line_height=1.45,
)
code_group.add(code_block)
scene.add(code_group)

# =========================================================================
# SCENE 6: Kinetic Hero Typography ("Code" -> "faster") (9.0s - 10.4s)
# =========================================================================
hero_code = TextTypewriter("Code", font_size=110, font_family="Playfair Display", color=Color.from_hex("#f8fafc"), position=(638, 359), anchor=(0.5, 0.5))
hero_code.opacity = Signal(0.0, "hero_code.opacity")

hero_faster = Text("faster", font_size=88, font_family="Playfair Display", italic=True, color=Color.from_hex("#f8fafc"), position=(638, 359), anchor=(0.5, 0.5))
hero_faster.opacity = Signal(0.0, "hero_faster.opacity")

scene.add(hero_code, hero_faster)

# =========================================================================
# SCENE 7: Outro Anthropic Star Lockup (10.4s - 11.6s)
# =========================================================================
outro_star = AnthropicAsterisk(radius=46.0, spokes=12, spoke_width=7.0, color=Color.from_hex("#d97757"), position=(638, 359))
outro_star.opacity = Signal(0.0, "outro_star.opacity")
scene.add(outro_star)

# =========================================================================
# 🎬 MASTER CHOREOGRAPHY WITH CAMERA DOLLY & BEAT SYNC
# =========================================================================
@scene.animate
def main():
    # --- SCENE 1: Intro Logo & Title (0.0s - 1.8s) ---
    star_logo.scale.set(Vector2D(0.2, 0.2))
    yield scene.all(
        star_logo.scale.to(Vector2D(1.0, 1.0), duration=0.8, ease=Ease.spring(stiffness=150, damping=11)),
        claude_title.opacity.to(1.0, duration=0.6, delay=0.4),
    )
    yield scene.wait(0.5)
    yield scene1_group.opacity.to(0.0, duration=0.2)

    # --- SCENE 2: Chat UI Pop-In (1.8s - 3.4s) ---
    chat_bar.position.set(Vector2D(218, 380))
    prompt_input.type_progress.set(0.0)
    yield scene.all(
        scene2_group.opacity.to(1.0, duration=0.35),
        chat_bar.position.to(Vector2D(218, 300), duration=0.75, ease=Ease.spring(stiffness=130, damping=13)),
    )

    # --- SCENE 3: Typewriter Prompt (3.4s - 4.6s) ---
    yield prompt_input.type_out(duration=1.4)
    yield scene.wait(0.2)

    # --- SCENE 4: Dynamic Camera Dolly into Macro Submit Button (4.6s - 6.6s) ---
    # Camera pushes from wide view into macro close-up on the orange submit button!
    submit_center_x = 218 + 790 - 20
    submit_center_y = 300 + 75
    
    yield scene.all(
        # Camera zoom & pan directly to submit button
        scene.camera.zoom.to(2.6, duration=0.75, ease=Ease.in_out_cubic),
        scene.camera.position.to(Vector2D(submit_center_x - 638, submit_center_y - 359), duration=0.75, ease=Ease.in_out_cubic),
        backlight.position.to(Vector2D(submit_center_x, submit_center_y), duration=0.75, ease=Ease.in_out_cubic),
        # Hand cursor glides into button center
        hand_cursor.opacity.to(1.0, duration=0.2),
        hand_cursor.position.to(Vector2D(988, 396), duration=0.7, ease=Ease.out_expo, delay=0.1),
    )

    # Tactile Button Click Slam & Bloom Shockwave at t = 5.8s
    yield scene.all(
        hand_cursor.click(duration=0.3),
        submit_btn.scale.to(Vector2D(0.78, 0.78), duration=0.12, ease=Ease.in_quad),
        click_ripple.trigger(duration=0.45),
    )
    yield submit_btn.scale.to(Vector2D(1.0, 1.0), duration=0.22, ease=Ease.spring(stiffness=220, damping=9))
    yield scene.wait(0.25)

    # Transition out Scene 2 & Reset Camera
    yield scene.all(
        scene2_group.opacity.to(0.0, duration=0.15),
        hand_cursor.opacity.to(0.0, duration=0.15),
        scene.camera.zoom.to(1.0, duration=0.2, ease=Ease.out_expo),
        scene.camera.position.to(Vector2D(0.0, 0.0), duration=0.2, ease=Ease.out_expo),
        backlight.position.to(Vector2D(638, 360), duration=0.2),
    )

    # --- SCENE 5: High-Speed Streaming Code Void (6.6s - 9.0s) ---
    yield code_group.opacity.to(1.0, duration=0.01)
    yield code_block.scroll_to(target_y=160.0, duration=2.2, ease=Ease.linear)
    yield code_group.opacity.to(0.0, duration=0.15)

    # --- SCENE 6: Kinetic Hero Typography (9.0s - 10.4s) ---
    yield hero_code.opacity.to(1.0, duration=0.01)
    yield hero_code.type_out(duration=0.45)
    yield scene.wait(0.25)
    yield hero_code.opacity.to(0.0, duration=0.01)

    yield hero_faster.opacity.to(1.0, duration=0.01)
    yield hero_faster.scale.to(Vector2D(1.04, 1.04), duration=0.55, ease=Ease.out_expo)
    yield hero_faster.opacity.to(0.0, duration=0.01)

    # --- SCENE 7: Outro Anthropic Star Lockup (10.4s - 11.6s) ---
    yield outro_star.opacity.to(1.0, duration=0.01)
    yield outro_star.scale.to(Vector2D(1.08, 1.08), duration=0.95, ease=Ease.in_out_sine)
    yield outro_star.opacity.to(0.0, duration=0.25)

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    scene.storyboard("output/recreated_claude_teaser_storyboard.png")
    print("[+] Generated output/recreated_claude_teaser_storyboard.png successfully!")
    scene.render("output/recreated_claude_teaser.mp4", quality="high")
    print("[+] Master video rendered to output/recreated_claude_teaser.mp4!")
