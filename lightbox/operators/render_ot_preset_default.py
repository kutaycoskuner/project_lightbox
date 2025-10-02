import bpy

# Define the operator
class Render_OT_Preset_Default(bpy.types.Operator):
    """Sets Render Preset for Blender Default"""
    bl_idname = "render.preset_default_shading"
    bl_label = "Preset Default Shading"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.custom_function()
        return {'FINISHED'}

    def custom_function(self):
        bpy.context.scene.view_settings.view_transform = 'AgX'
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        bpy.context.scene.render.filter_size = 0.2
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.render.dither_intensity = 1.0


# Registration
def register():
    bpy.utils.register_class(Render_OT_Preset_Default)

def unregister():
    bpy.utils.unregister_class(Render_OT_Preset_Default)

if __name__ == "__main__":
    register()
