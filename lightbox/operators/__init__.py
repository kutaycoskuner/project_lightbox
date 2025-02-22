from . import (
    object_ot_add_baserig,
    object_ot_generate_controlrig,
    object_ot_originto_geometry,
    object_ot_originto_ground,
    object_ot_scaled_armature_weight,
    ot_toggle_sidebar_tab,
    shader_ot_toggleclay,
    view3d_ot_focus_outliner,
    # node_ot_previewdrawer,
)


modules = (
    object_ot_add_baserig,
    object_ot_generate_controlrig,
    object_ot_originto_geometry,
    object_ot_originto_ground,
    object_ot_scaled_armature_weight,
    ot_toggle_sidebar_tab,
    shader_ot_toggleclay,
    view3d_ot_focus_outliner,
    # node_ot_previewdrawer,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
