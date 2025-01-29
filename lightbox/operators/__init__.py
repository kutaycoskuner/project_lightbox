from . import (
    shader_ot_toggleclay,
    view3d_ot_focusoutliner,
    # node_ot_previewdrawer,
)


modules = (
    shader_ot_toggleclay,
    view3d_ot_focusoutliner,
    # node_ot_previewdrawer,
    )


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
