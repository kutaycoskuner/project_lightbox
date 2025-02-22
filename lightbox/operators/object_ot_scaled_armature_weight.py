import bpy

class Object_OT_ScaledArmature_Weight(bpy.types.Operator):
    """Apply scaled armature weight to selected meshes.
    
    Steps:
      1. Ensure object mode.
      2. For each selected mesh:
         - Enter edit mode.
         - Select all.
         - Set transform pivot point to individual origins.
         - Scale by the given factor (currently 0.5).
         - Return to object mode.
      3. For each mesh:
         - Select the mesh and the armature (named "Lightbox Control rig")
         - Parent with automatic weights.
      4. For each mesh:
         - Enter edit mode again.
         - Select all.
         - Scale by the inverse factor (2.0) to restore original size.
         - Return to object mode.
    """
    bl_idname = "object.scaled_armature_weight"
    bl_label = "Scaled Armature Weight"
    bl_description = ("Select meshes to apply.\n"
                      "Set scale of weighted rigging.\n"
                      "Click this button to perform the operations.")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.custom_function()
        return {'FINISHED'}

    def custom_function(self):
        # 1. Ensure object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Gather selected mesh objects
        meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        if not meshes:
            self.report({'WARNING'}, "No mesh objects selected.")
            return

        scale_factor = 0.5  # scaling factor
        inverse_scale = 1.0 / scale_factor
        
        # 2. Scale down each mesh in edit mode
        for mesh in meshes:
            bpy.context.view_layer.objects.active = mesh
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # 3. Set pivot to individual origins
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            # 4. Scale everything by scale_factor
            bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
            # 5. Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # 6. Find the armature named "Lightbox Control rig"
        armature_name = "Lightbox Control Rig"
        arm_obj = bpy.data.objects.get(armature_name)
        if arm_obj is None:
            self.report({'WARNING'}, f"Armature '{armature_name}' not found!")
            return
        
        # 7. Parent each mesh to the armature using automatic weights
        for mesh in meshes:
            bpy.ops.object.select_all(action='DESELECT')
            mesh.select_set(True)
            arm_obj.select_set(True)
            # The armature must be the active object for ARMATURE_AUTO parenting
            bpy.context.view_layer.objects.active = arm_obj
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        # 8. Return each mesh to its original scale by scaling up in edit mode
        for mesh in meshes:
            bpy.context.view_layer.objects.active = mesh
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.resize(value=(inverse_scale, inverse_scale, inverse_scale))
            bpy.ops.object.mode_set(mode='OBJECT')

# Registration
def register():
    bpy.utils.register_class(Object_OT_ScaledArmature_Weight)

def unregister():
    bpy.utils.unregister_class(Object_OT_ScaledArmature_Weight)

if __name__ == "__main__":
    register()
