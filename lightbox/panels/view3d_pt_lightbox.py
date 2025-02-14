import bpy
from .. import bl_info

class View3D_PT_Lightbox(bpy.types.Panel):
    bl_label = "Lightbox" 
    bl_idname = "ARCH_PT_lightbox_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Lightbox'

    @classmethod
    def poll(cls, context):
        # the panel is always displayed
        return True

    def draw_header_preset(self, context):
        """ This method modifies the right side of the panel header """
        layout = self.layout
        version = bl_info["version"]
        version_str = f"v{version[0]}.{version[1]}.{version[2]}"
        layout.label(text=version_str) 


    def draw(self, context):
        layout = self.layout
        display_toggle_clay = str(context.scene.get("clay_material_applied", False))

        # Rendering Section
        layout.label(text="Rendering")
        row = layout.row()
        row.operator('shader.toggle_clay_operator')
        row.alignment = 'CENTER'
        row.label(text=display_toggle_clay)

        # Viewport Control Section
        layout.label(text="Ease of Access")
        row = layout.row()
        row.operator('view3d.focus_outliner')

        row = layout.row()
        row.operator('object.originto_ground')
        row.operator('object.originto_geometry') # text="Ground Object 2"

        # Rigging Section
        layout.label(text="Rigging")
        row = layout.row()
        row.operator('object.generate_control_rig')

classes = (
    View3D_PT_Lightbox,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)