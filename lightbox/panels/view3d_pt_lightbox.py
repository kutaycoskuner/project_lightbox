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
        return True

    def draw_header_preset(self, context):
        layout = self.layout
        version = bl_info["version"]
        version_str = f"v{version[0]}.{version[1]}.{version[2]}"
        layout.label(text=version_str) 

    def condition_scaled_armature_weight(self):
        armature_exists = any(
            obj.type == 'ARMATURE' and obj.name == "Lightbox Control Rig"
            for obj in bpy.data.objects
        )
        return armature_exists

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        display_toggle_clay = str(scene.get("clay_material_applied", False))

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
        row.operator('object.originto_geometry')

        # Rigging Section
        layout.label(text="Rigging (experimental)")
        row = layout.row()
        row.operator('object.generate_control_rig')
        row = layout.row()
        row.enabled = self.condition_scaled_armature_weight()
        row.prop(scene, "scale_factor", text="Scale Factor")
        row = layout.row()
        row.enabled = self.condition_scaled_armature_weight()
        row.operator('object.scaled_armature_weight')

classes = (
    View3D_PT_Lightbox,
)

def register():
    bpy.types.Scene.scale_factor = bpy.props.FloatProperty(
        name="Scale Factor",
        description="Scale factor for armature weight operation",
        default=1.0,
        min=0.1,
        max=1.0,
    )
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.scale_factor

if __name__ == "__main__":
    register()
