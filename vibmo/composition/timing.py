"""
Timing system for transitions and animations.
Inspired by Remotion's springTiming and linearTiming functions.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass

from vibmo.core.easing import Ease

if TYPE_CHECKING:
    from vibmo.core.color import Color


@dataclass
class TimingConfig:
    """Configuration for timing functions."""
    duration: float
    delay: float = 0.0
    ease: str = "linear"  # linear, spring, custom


@dataclass
class SpringConfig:
    """Configuration for spring physics timing."""
    stiffness: float = 100.0
    damping: float = 10.0
    mass: float = 1.0


class TimingFunction:
    """Base class for timing functions."""
    
    def __call__(self, t: float) -> float:
        """Calculate timing value at time t (normalized 0-1)."""
        raise NotImplementedError


class LinearTiming(TimingFunction):
    """
    Linear timing function.
    Provides constant velocity progression.
    """
    
    def __init__(self, config: Optional[TimingConfig] = None):
        self.config = config or TimingConfig(duration=1.0)
    
    def __call__(self, t: float) -> float:
        """Linear progression from 0 to 1."""
        # Normalize time to config duration
        normalized_time = t / self.config.duration
        return max(0.0, min(1.0, normalized_time))


class SpringTiming(TimingFunction):
    """
    Spring physics timing function.
    Provides natural spring motion with overshoot and settling.
    """
    
    def __init__(self, 
                 config: Optional[TimingConfig] = None,
                 spring_config: Optional[SpringConfig] = None):
        self.config = config or TimingConfig(duration=1.0)
        self.spring_config = spring_config or SpringConfig()
    
    def __call__(self, t: float) -> float:
        """Spring-based progression with natural overshoot."""
        # Normalize time to config duration
        normalized_time = t / self.config.duration
        
        # Simplified spring physics calculation
        # Using damped harmonic oscillator equation
        k = self.spring_config.stiffness
        c = self.spring_config.damping
        m = self.spring_config.mass
        
        # Calculate angular frequency
        omega = math.sqrt(k / m)
        
        # Calculate damping ratio
        zeta = c / (2 * math.sqrt(k * m))
        
        if zeta < 1.0:  # Underdamped - oscillatory
            omega_d = omega * math.sqrt(1 - zeta**2)
            envelope = math.exp(-zeta * omega * normalized_time)
            oscillation = math.cos(omega_d * normalized_time)
            position = 1.0 - envelope * oscillation
        elif zeta == 1.0:  # Critically damped
            position = 1.0 - (1.0 + omega * normalized_time) * math.exp(-omega * normalized_time)
        else:  # Overdamped
            r1 = -omega * (zeta + math.sqrt(zeta**2 - 1))
            r2 = -omega * (zeta - math.sqrt(zeta**2 - 1))
            position = 1.0 - (r2 * math.exp(r1 * normalized_time) - r1 * math.exp(r2 * normalized_time)) / (r2 - r1)
        
        return max(0.0, min(1.2, position))  # Allow slight overshoot, clamp to reasonable range


class CubicBezierTiming(TimingFunction):
    """
    Cubic bezier timing function.
    Provides custom easing curves using control points.
    """
    
    def __init__(self, 
                 x1: float, y1: float, 
                 x2: float, y2: float,
                 config: Optional[TimingConfig] = None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.config = config or TimingConfig(duration=1.0)
    
    def __call__(self, t: float) -> float:
        """Cubic bezier progression."""
        normalized_time = t / self.config.duration
        return self._cubic_bezier(normalized_time, self.x1, self.y1, self.x2, self.y2)
    
    def _cubic_bezier(self, t: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate cubic bezier value at time t."""
        # Simplified cubic bezier calculation
        # For production, would use proper subdivision or Newton-Raphson
        return self._lerp(
            self._lerp(self._lerp(0.0, x1, t), self._lerp(x1, x2, t), t),
            self._lerp(self._lerp(x1, x2, t), self._lerp(x2, 1.0, t), t),
            t
        )
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a + (b - a) * t


class EaseInTiming(TimingFunction):
    """Ease-in timing function."""
    
    def __init__(self, config: Optional[TimingConfig] = None):
        self.config = config or TimingConfig(duration=1.0)
    
    def __call__(self, t: float) -> float:
        normalized_time = t / self.config.duration
        return Ease.in_quad(max(0.0, min(1.0, normalized_time)))


class EaseOutTiming(TimingFunction):
    """Ease-out timing function."""
    
    def __init__(self, config: Optional[TimingConfig] = None):
        self.config = config or TimingConfig(duration=1.0)
    
    def __call__(self, t: float) -> float:
        normalized_time = t / self.config.duration
        return Ease.out_quad(max(0.0, min(1.0, normalized_time)))


class EaseInOutTiming(TimingFunction):
    """Ease-in-out timing function."""
    
    def __init__(self, config: Optional[TimingConfig] = None):
        self.config = config or TimingConfig(duration=1.0)
    
    def __call__(self, t: float) -> float:
        normalized_time = t / self.config.duration
        return Ease.in_out_quad(max(0.0, min(1.0, normalized_time)))


class EasingTiming(TimingFunction):
    """
    General easing timing function using any easing function.
    """
    
    def __init__(self, easing_func: callable, config: Optional[TimingConfig] = None):
        self.easing_func = easing_func
        self.config = config or TimingConfig(duration=1.0)
    
    def __call__(self, t: float) -> float:
        normalized_time = t / self.config.duration
        return self.easing_func(max(0.0, min(1.0, normalized_time)))


# Convenience functions for creating timing functions

def linear_timing(duration: float = 1.0, delay: float = 0.0) -> LinearTiming:
    """Create a linear timing function."""
    config = TimingConfig(duration=duration, delay=delay, ease="linear")
    return LinearTiming(config)


def spring_timing(duration: float = 1.0, 
                 delay: float = 0.0,
                 stiffness: float = 100.0,
                 damping: float = 10.0,
                 mass: float = 1.0) -> SpringTiming:
    """Create a spring timing function with physics."""
    config = TimingConfig(duration=duration, delay=delay, ease="spring")
    spring_config = SpringConfig(stiffness=stiffness, damping=damping, mass=mass)
    return SpringTiming(config, spring_config)


def cubic_bezier_timing(x1: float, y1: float, x2: float, y2: float,
                       duration: float = 1.0, delay: float = 0.0) -> CubicBezierTiming:
    """Create a cubic bezier timing function."""
    config = TimingConfig(duration=duration, delay=delay, ease="cubic-bezier")
    return CubicBezierTiming(x1, y1, x2, y2, config)


def ease_in_timing(duration: float = 1.0, delay: float = 0.0) -> EaseInTiming:
    """Create an ease-in timing function."""
    config = TimingConfig(duration=duration, delay=delay, ease="ease-in")
    return EaseInTiming(config)


def ease_out_timing(duration: float = 1.0, delay: float = 0.0) -> EaseOutTiming:
    """Create an ease-out timing function."""
    config = TimingConfig(duration=duration, delay=delay, ease="ease-out")
    return EaseOutTiming(config)


def ease_in_out_timing(duration: float = 1.0, delay: float = 0.0) -> EaseInOutTiming:
    """Create an ease-in-out timing function."""
    config = TimingConfig(duration=duration, delay=delay, ease="ease-in-out")
    return EaseInOutTiming(config)


def easing_timing(easing_func: callable, 
                duration: float = 1.0, 
                delay: float = 0.0) -> EasingTiming:
    """Create a custom easing timing function."""
    config = TimingConfig(duration=duration, delay=delay, ease="custom")
    return EasingTiming(easing_func, config)


# Alias
bezier_timing = cubic_bezier_timing


# Preset timing configurations for common use cases

TIMING_PRESETS = {
    "fast": linear_timing(duration=0.3),
    "normal": linear_timing(duration=0.5),
    "slow": linear_timing(duration=0.8),
    "bouncy": spring_timing(duration=0.6, stiffness=150, damping=8),
    "smooth": ease_in_out_timing(duration=0.5),
    "dramatic": cubic_bezier_timing(0.68, -0.55, 0.265, 1.55, duration=0.7),
    "gentle": spring_timing(duration=0.8, stiffness=80, damping=12),
    "snappy": spring_timing(duration=0.4, stiffness=200, damping=15),
}


def get_timing_preset(preset_name: str) -> Optional[TimingFunction]:
    """Get a timing preset by name."""
    return TIMING_PRESETS.get(preset_name)


def calculate_progress(timing: TimingFunction, 
                     current_time: float, 
                     start_time: float = 0.0) -> float:
    """Calculate progress (0-1) using a timing function."""
    elapsed_time = current_time - start_time
    return timing(elapsed_time)


def interpolate_value(start: float, end: float, progress: float) -> float:
    """Interpolate between two values based on progress."""
    return start + (end - start) * progress


def interpolate_position(start_pos: Tuple[float, float], 
                       end_pos: Tuple[float, float], 
                       progress: float) -> Tuple[float, float]:
    """Interpolate between two positions based on progress."""
    x = interpolate_value(start_pos[0], end_pos[0], progress)
    y = interpolate_value(start_pos[1], end_pos[1], progress)
    return (x, y)


def interpolate_color(start_color: Union['Color', str], 
                     end_color: Union['Color', str], 
                     progress: float) -> 'Color':
    """Interpolate between two colors based on progress."""
    from vibmo.core.color import Color
    
    # Convert strings to Color objects if needed
    if isinstance(start_color, str):
        start_color = Color.from_any(start_color)
    if isinstance(end_color, str):
        end_color = Color.from_any(end_color)
    
    r = interpolate_value(start_color.r, end_color.r, progress)
    g = interpolate_value(start_color.g, end_color.g, progress)
    b = interpolate_value(start_color.b, end_color.b, progress)
    a = interpolate_value(start_color.a, end_color.a, progress)
    return Color(r, g, b, a)


class AnimationTimeline:
    """
    Timeline for managing multiple animations with different timing functions.
    """
    
    def __init__(self, duration: float = 1.0):
        self.duration = duration
        self.animations: list = []
    
    def add_animation(self, 
                     name: str,
                     timing: TimingFunction,
                     start_time: float = 0.0,
                     end_time: Optional[float] = None):
        """Add an animation to the timeline."""
        if end_time is None:
            end_time = start_time + timing.config.duration
        
        self.animations.append({
            "name": name,
            "timing": timing,
            "start_time": start_time,
            "end_time": end_time
        })
    
    def get_progress(self, name: str, current_time: float) -> float:
        """Get progress for a specific animation."""
        for anim in self.animations:
            if anim["name"] == name:
                if current_time < anim["start_time"]:
                    return 0.0
                elif current_time > anim["end_time"]:
                    return 1.0
                else:
                    local_time = current_time - anim["start_time"]
                    return anim["timing"](local_time)
        return 0.0
    
    def get_all_progress(self, current_time: float) -> dict:
        """Get progress for all animations."""
        return {
            anim["name"]: self.get_progress(anim["name"], current_time)
            for anim in self.animations
        }