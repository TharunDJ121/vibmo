from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, duration=2.0, background=colors.DARK_NAVY)

# 1. Flex Wrap Test
flex_container = FlexContainer(
    direction="row",
    wrap=True,
    width=600,
    gap=20,
    padding=20,
    fill=colors.SLATE_800,
    corner_radius=20,
    align_items="center",
    justify_content="space_between"
)

# Add 8 boxes to flex container (should wrap after 3 boxes if width=600)
for i in range(8):
    box = Rect(width=150, height=80, fill=colors.INDIGO, corner_radius=10)
    flex_container.add(box)

flex_container.at(100, 100)

# 2. Grid Container Test
grid_container = GridContainer(
    columns=3,
    gap=(20, 30),
    padding=40,
    width=800,
    fill=colors.SLATE_900,
    corner_radius=24
)

for i in range(7):
    box = Rect(width=200, height=100 if i % 2 == 0 else 150, fill=colors.EMERALD, corner_radius=10)
    grid_container.add(box)

grid_container.at(900, 100)

scene.add(flex_container, grid_container)

if __name__ == "__main__":
    scene.storyboard("test_layout_storyboard.png")
