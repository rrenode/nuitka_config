import sys

def export(obj):
    """Decorator that adds the object's name to __all__ of the caller module."""
    frame = sys._getframe(1)  # Get the caller's frame
    module = frame.f_globals

    if "__all__" not in module:
        module["__all__"] = []

    module["__all__"].append(obj.__name__)
    return obj