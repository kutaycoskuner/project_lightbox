from . import (
    view3d_pt_lightbox,
    shader_pt_lightbox
)


modules = (
    view3d_pt_lightbox,
    shader_pt_lightbox,
    )


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
