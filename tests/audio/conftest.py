import sys
import typing
import builtins

# Ensure common typing symbols exist in builtins for cross-module collection resiliency
for sym in ['Union', 'Optional', 'List', 'Dict', 'Tuple', 'Any', 'Callable']:
    if not hasattr(builtins, sym):
        setattr(builtins, sym, getattr(typing, sym, None))
