import bpy

# Define the operator
class Render_OT_Preset_Cel(bpy.types.Operator):
    """Sets Render Preset for Cel Shading"""
    bl_idname = "render.preset_cel_shading"
    bl_label = "Preset Cel Shading"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.custom_function()
        return {'FINISHED'}

    def custom_function(self):
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        bpy.context.scene.render.filter_size = 0.0
        bpy.context.scene.render.resolution_x = 384
        bpy.context.scene.render.resolution_y = 216
        bpy.context.scene.render.dither_intensity = 0.0


# Registration
def register():
    bpy.utils.register_class(Render_OT_Preset_Cel)

def unregister():
    bpy.utils.unregister_class(Render_OT_Preset_Cel)

if __name__ == "__main__":
    register()
