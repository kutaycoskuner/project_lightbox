import bpy


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


class View3D_PT_Lightbox(bpy.types.Panel):
    bl_label = "Lightbox"
    bl_idname = "ARCH_PT_lightbox_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Lightbox'

    def draw(self, context):
        layout = self.layout
        display_toggle_clay = str(context.scene.get(
            "clay_material_applied", False)
        )

        row = layout.row()
        row.operator('shader.toggle_clay_operator')
        row.label(text=display_toggle_clay)

        row = layout.row()
        row.operator('view3d.focus_outliner')


classes = (
    View3D_PT_Lightbox,
    )
