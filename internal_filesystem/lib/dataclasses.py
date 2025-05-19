# dataclasses.py: Minimal MicroPython compatibility layer for Python's dataclasses
# Implements @dataclass with __init__ and __repr__ generation

def dataclass(cls):
    """Decorator to emulate Python's @dataclass, generating __init__ and __repr__."""
    # Get class annotations and defaults
    annotations = getattr(cls, '__annotations__', {})
    defaults = {}
    for name in dir(cls):
        if not name.startswith('__'):
            attr = getattr(cls, name, None)
            if not callable(attr) and name in annotations:
                defaults[name] = attr

    # Generate __init__ method
    def __init__(self, *args, **kwargs):
        # Positional arguments
        fields = list(annotations.keys())
        for i, value in enumerate(args):
            if i >= len(fields):
                raise TypeError(f"Too many positional arguments")
            setattr(self, fields[i], value)

        # Keyword arguments and defaults
        for name in fields:
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif not hasattr(self, name):
                if name in defaults:
                    setattr(self, name, defaults[name])
                else:
                    raise TypeError(f"Missing required argument: {name}")

    # Generate __repr__ method
    def __repr__(self):
        fields = [
            f"{name}={getattr(self, name)!r}"
            for name in annotations
        ]
        return f"{cls.__name__}({', '.join(fields)})"

    # Attach generated methods to class
    setattr(cls, '__init__', __init__)
    setattr(cls, '__repr__', __repr__)

    return cls
