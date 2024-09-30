from . import (
    nodehasher,
)


modules = (
    nodehasher,
    )


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
