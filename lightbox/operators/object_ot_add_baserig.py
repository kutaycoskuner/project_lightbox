import bpy
import os

def menu_func(self, context):
    self.layout.operator(Object_OT_AddBaseRig.bl_idname, text="Lightbox Humanoid Base Rig")

class Object_OT_AddBaseRig(bpy.types.Operator):
    bl_idname = "object.append_base_rig"
    bl_label = "Import Base Rig"
    bl_description = "Adds Lightbox humanoid base rig to your scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Define the path to the blend file inside the addon
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        blend_path = os.path.join(addon_dir, "../_data/", "base-rig.blend")

        object_name  = "lb_armature" 
        directory    = blend_path + "/Armature/"
        
        try:
            bpy.ops.wm.append(
                filepath=blend_path,
                directory=directory,
                filename=object_name,
                link=False  # False means we copy it into the current blend file
            )
            self.report({'INFO'}, f"Added Lightbox Base Skeleton")
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to append skeleton")
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    bpy.utils.register_class(Object_OT_AddBaseRig)
    bpy.types.VIEW3D_MT_armature_add.append(menu_func)  # Adds to Shift + A → Armature
def unregister():
    bpy.types.VIEW3D_MT_armature_add.remove(menu_func)
    bpy.utils.unregister_class(Object_OT_AddBaseRig)
