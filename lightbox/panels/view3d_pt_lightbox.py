import bpy


class View3D_PT_Lightbox(bpy.types.Panel):
    bl_label = "Lightbox"
    bl_idname = "ARCH_PT_lightbox_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Lightbox'

    def draw(self, context):
        layout = self.layout
        # version = bl_info.get("version", (1, 0, 0))
        display_toggle_clay = str(context.scene.get(
            "clay_material_applied", False)
        )
        
        # toggle clay operator
        row = layout.row()
        row.operator('shader.toggle_clay_operator')
        row.alignment = 'CENTER'
        row.label(text=display_toggle_clay)

        row = layout.row()
        row.operator('view3d.focus_outliner')
        
        row = layout.row()
        row.operator('object.originto_ground')
        row.operator('object.originto_geometry') # text="Ground Object 2"
        
        row = layout.row()
        row.operator('object.append_base_rig')


classes = (
    View3D_PT_Lightbox,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
