"""
Vibmo Extensibility & Plugin Registry.
Allows third-party libraries and users to register custom semantic components, shaders, and verbs.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Type


class PluginRegistry:
    """Central registry for custom Vibmo components, shaders, and templates."""

    _components: Dict[str, Type[Any]] = {}
    _filters: Dict[str, Type[Any]] = {}
    _verbs: Dict[str, Callable[..., Any]] = {}

    @classmethod
    def register_component(cls, name: Optional[str] = None) -> Callable[[Type[Any]], Type[Any]]:
        """Decorator to register a custom Node/Component class in the global ecosystem."""
        def decorator(target_cls: Type[Any]) -> Type[Any]:
            reg_name = name or target_cls.__name__
            cls._components[reg_name] = target_cls
            return target_cls
        return decorator

    @classmethod
    def register_filter(cls, name: Optional[str] = None) -> Callable[[Type[Any]], Type[Any]]:
        """Decorator to register a custom Post-FX filter."""
        def decorator(target_cls: Type[Any]) -> Type[Any]:
            reg_name = name or target_cls.__name__
            cls._filters[reg_name] = target_cls
            return target_cls
        return decorator

    @classmethod
    def get_component(cls, name: str) -> Optional[Type[Any]]:
        return cls._components.get(name)

    @classmethod
    def list_components(cls) -> List[str]:
        return list(cls._components.keys())

    @classmethod
    def list_filters(cls) -> List[str]:
        return list(cls._filters.keys())


# Top-level helper decorator
register_component = PluginRegistry.register_component
register_filter = PluginRegistry.register_filter
