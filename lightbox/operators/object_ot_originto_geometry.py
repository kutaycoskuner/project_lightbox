import bpy
import mathutils

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


class Object_OT_GroundObject(bpy.types.Operator):
    bl_idname      = "object.originto_geometry"
    bl_description = "Sets selected object origin to geometry center"
    bl_label       = "Origin to Geometry"
    bl_options     = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get all selected objects
        selected_objects = context.selected_objects

        # Check if any objects are selected
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected.")
            return {'CANCELLED'}

        # Loop through each selected object
        for obj in selected_objects:
            # Check if the object is a mesh
            if obj.type != 'MESH':
                self.report({'WARNING'}, f"Skipping non-mesh object: {obj.name}")
                continue

            # Switch to object mode (if not already in object mode)
            bpy.ops.object.mode_set(mode='OBJECT')

            # Select the current object and make it active
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Set the object origin to the 3D cursor location
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

            self.report({'INFO'}, f"Origin set to geometry for object: {obj.name}")

        # Restore the original selection
        for obj in selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = selected_objects[0]

        return {'FINISHED'}


classes = (
    Object_OT_GroundObject,
    )
