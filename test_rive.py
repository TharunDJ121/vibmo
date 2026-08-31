from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, duration=2.0)

# 1. Rive Animation Node
rive_anim = RiveAnimation(
    src="assets/character.riv",
    state_machine="State Machine 1",
    width=500,
    height=500,
)

rive_anim.at(710, 290)

# Trigger states
rive_anim.fire_trigger("Jump", time=0.5)
rive_anim.set_input("Speed", 2.0, time=1.0)

scene.add(rive_anim)

if __name__ == "__main__":
    scene.storyboard("test_rive_storyboard.png")
