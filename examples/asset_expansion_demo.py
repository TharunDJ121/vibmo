"""
Comprehensive demo showcasing the new asset expansion features.
Demonstrates transitions, patterns, asset library, and timing system.
"""

import numpy as np

# Import new transition features
from vibmo.composition import (
    Slide, PushCut, Fade, Dissolve, Iris, Wipe, ZoomBlur, Ripple, Flip, BookFlip,
    SlideDirection, IrisShape, WipeDirection,
    slide, push_cut, fade, dissolve, iris, wipe, zoom_blur, ripple, flip, book_flip,
    spring_timing, linear_timing, ease_in_out_timing, get_timing_preset
)

# Import pattern effects
from vibmo.fx import (
    Checkerboard, Gridlines, Rings, Starburst, Pattern, Tile, Zigzag,
    checkerboard, gridlines, rings, starburst, pattern, tile, zigzag
)

# Import asset library
from vibmo.assets import (
    get_asset_library, create_gradient_preset, get_popular_gradients,
    AssetType
)


def demo_transitions():
    """Demonstrate the new transition system."""
    print("=== Transition System Demo ===")
    
    # Create test images for transitions
    import numpy as np
    img_a = np.zeros((1080, 1920, 4), dtype=np.uint8)
    img_a[:, :, 0] = 255  # Red
    img_a[:, :, 3] = 255  # Full opacity
    
    img_b = np.zeros((1080, 1920, 4), dtype=np.uint8)
    img_b[:, :, 2] = 255  # Blue
    img_b[:, :, 3] = 255  # Full opacity
    
    # Test various transitions
    transitions = [
        ("Slide", slide(direction=SlideDirection.FROM_LEFT)),
        ("PushCut", push_cut(direction=SlideDirection.FROM_RIGHT)),
        ("Fade", fade()),
        ("Dissolve", dissolve()),
        ("Iris", iris(shape=IrisShape.CIRCLE)),
        ("Wipe", wipe(direction=WipeDirection.LEFT_TO_RIGHT)),
        ("ZoomBlur", zoom_blur()),
        ("Ripple", ripple()),
        ("Flip", flip()),
        ("BookFlip", book_flip())
    ]
    
    for name, transition in transitions:
        print(f"Testing {name} transition...")
        result = transition.blend(img_a, img_b, 0.5)
        print(f"  Result shape: {result.shape}")
        print(f"  Transition duration: {transition.duration}s")


def demo_patterns():
    """Demonstrate the new pattern effects."""
    print("\n=== Pattern Effects Demo ===")
    
    # Test various patterns
    patterns = [
        ("Checkerboard", checkerboard(square_size=50)),
        ("Gridlines", gridlines(spacing=100)),
        ("Rings", rings(ring_spacing=50)),
        ("Starburst", starburst(ray_count=12)),
        ("Zigzag", zigzag(wavelength=100))
    ]
    
    for name, pattern in patterns:
        print(f"Testing {name} pattern...")
        result = pattern.render(time=0.0)
        print(f"  Result shape: {result.shape}")
        print(f"  Pattern dimensions: {pattern.width}x{pattern.height}")


def demo_asset_library():
    """Demonstrate the asset library system."""
    print("\n=== Asset Library Demo ===")
    
    library = get_asset_library()
    
    # Get library statistics
    stats = library.get_statistics()
    print(f"Total assets: {stats['total_assets']}")
    print(f"Assets by type: {stats['by_type']}")
    print(f"Assets by category: {stats['by_category']}")
    print(f"Total tags: {stats['total_tags']}")
    
    # Search for gradients
    print("\nSearching for gradient assets...")
    gradients = library.search_assets(asset_type=AssetType.GRADIENT)
    for gradient in gradients:
        print(f"  - {gradient.name}: {gradient.description}")
    
    # Get popular gradients
    print("\nPopular gradients:")
    for gradient_id in get_popular_gradients():
        gradient_data = library.get_gradient(gradient_id)
        if gradient_data:
            print(f"  - {gradient_id}: {gradient_data}")


def demo_timing_system():
    """Demonstrate the timing system."""
    print("\n=== Timing System Demo ===")
    
    # Test various timing functions
    timing_functions = [
        ("Linear", linear_timing(duration=1.0)),
        ("Spring", spring_timing(duration=1.0, stiffness=150, damping=10)),
        ("EaseInOut", ease_in_out_timing(duration=1.0)),
        ("Preset: Bouncy", get_timing_preset("bouncy")),
        ("Preset: Smooth", get_timing_preset("smooth"))
    ]
    
    for name, timing in timing_functions:
        print(f"Testing {name} timing...")
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            progress = timing(t)
            print(f"  t={t:.2f}: progress={progress:.3f}")
        print()


def demo_transition_with_timing():
    """Demonstrate transitions with timing functions."""
    print("\n=== Transitions with Timing Demo ===")
    
    import numpy as np
    
    # Create test images
    img_a = np.zeros((1080, 1920, 4), dtype=np.uint8)
    img_a[:, :, 1] = 255  # Green
    img_a[:, :, 3] = 255
    
    img_b = np.zeros((1080, 1920, 4), dtype=np.uint8)
    img_b[:, :, 0] = 255  # Red
    img_b[:, :, 3] = 255
    
    # Test slide transition with spring timing
    print("Slide transition with spring timing:")
    spring = spring_timing(duration=1.0, stiffness=120, damping=12)
    slide_trans = slide(direction=SlideDirection.FROM_LEFT)
    
    for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        progress = spring(t)
        result = slide_trans.blend(img_a, img_b, progress)
        print(f"  t={t:.2f}: timing={progress:.3f}, result_shape={result.shape}")


if __name__ == "__main__":
    print("Vibmo Asset Expansion Demo")
    print("=" * 50)
    
    # Run all demos
    demo_transitions()
    demo_patterns()
    demo_asset_library()
    demo_timing_system()
    demo_transition_with_timing()
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print("\nNext steps:")
    print("1. Test the transitions in actual scenes")
    print("2. Integrate patterns into your compositions")
    print("3. Use the asset library for gradients and textures")
    print("4. Apply timing functions to animations")