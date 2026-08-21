"""
✦ Generated Motion Graphics Sequence: create a example saas dashboard animatio
Generated via Motio LangGraph Motion Engine.
"""

from motio.agent_api import *

# 1. Scene 1: High-Impact Entrance
s1 = Scene(width=720, height=1280, fps=60, duration=1.8, background=Color.WHITE)
card = ModelCard(title="Launch 2.0", subtitle="Next-Gen AI", preview_text="L a u n", position=(80, 560), shimmer=True)
s1.add(GradientBackdrop.sunset(), card)
s1.action(card.pop_in(delay=0.04, duration=0.45), card.bounce(amplitude=1.06, count=1, delay=0.95, duration=0.35))

# 2. Scene 2: Interactive Prompt Pill with Live Typing Stream
s2 = Scene(width=720, height=1280, fps=60, duration=2.0, background=Color.WHITE)
pill = ChatInputBar(text="create a example saas dashboard anim", variant="smooth", typing_start=0.20, typing_speed=28.0, position=(40, 596), shimmer=True)
s2.add(pill)
s2.action(pill.pop_in(duration=0.35))

# 3. Scene 3: Kinetic Typography Punch
s3 = Scene(width=720, height=1280, fps=60, duration=1.8, background=Color.WHITE)
kt = KineticSnapText(base_word="Think", word_a="faster", word_b="smarter", color_a="#8b5cf6", color_b="#f97316", switch_time=0.85)
s3.add(kt)
s3.action(kt.pop_in(duration=0.35), kt.bounce(amplitude=1.14, count=1, delay=0.85, duration=0.35))

# 4. Scene 4: Call to Action Pill Button with Specular Shimmer
s4 = Scene(width=720, height=1280, fps=60, duration=1.6, background=Color.WHITE)
cta = PillLaunchButton("Get Started", position=(130, 592), shimmer=True)
s4.add(GradientBackdrop.aurora(), cta)
s4.action(cta.pop_in(delay=0.04, duration=0.5), cta.bounce(amplitude=1.08, count=1, delay=0.55, duration=0.35))

# Assemble Master Sequence with Sound Design
seq = Sequence(s1, s2, s3, s4, transition=CrossFade(0.08))
seq.add_bg_music("tech_ambient_pulse", volume=0.20)
seq.add_sfx("whoosh_cinematic", time=0.04, volume=0.35)
seq.add_sfx("ui_click_mechanical", time=0.60, volume=0.50)
seq.add_sfx("freesound_community-keyboard-typing-5997.mp3", time=1.85, volume=0.70, duration=1.6)
seq.add_sfx("success_bell_chime", time=4.80, volume=0.75)

if __name__ == "__main__":
    seq.storyboard("storyboard.png")
    seq.render("output.mp4", quality="high")
