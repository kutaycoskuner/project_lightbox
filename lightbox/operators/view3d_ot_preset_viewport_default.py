import bpy

# Define the operator
class View3D_OT_Preset_Viewport_Default(bpy.types.Operator):
    """Preset for viewport cavity"""
    bl_idname = "view3d.preset_viewport_default"
    bl_label = "Default Viewport Preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.custom_function()
        return {'FINISHED'}

    def custom_function(self):
        bpy.context.space_data.shading.show_cavity = False

# Registration
def register():
    bpy.utils.register_class(View3D_OT_Preset_Viewport_Default)

def unregister():
    bpy.utils.unregister_class(View3D_OT_Preset_Viewport_Default)

if __name__ == "__main__":
    register()
 