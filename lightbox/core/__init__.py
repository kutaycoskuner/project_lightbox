from .. import (
    keybindings,
    operators,
    panels,
    utils,
)


modules = (
    keybindings,
    operators,
    panels,
    # utils,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()