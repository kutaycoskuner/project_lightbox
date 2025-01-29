import bpy
import mathutils

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


class Object_OT_GroundObject(bpy.types.Operator):
    bl_idname = "object.ground_object"
    bl_label = "Ground Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object is not a mesh.")
            return {'CANCELLED'}
        
        # Find the lowest Z vertices
        lowest_z = float('inf')
        lowest_z_vertices = []

        for vertex in obj.data.vertices:
            if vertex.co.z < lowest_z:
                # Found a new lower Z, reset the vector and add this vertex
                lowest_z = vertex.co.z
                lowest_z_vertices = [vertex.co]
            elif vertex.co.z == lowest_z:
                # Add to the vector if the Z value is the same or similar
                lowest_z_vertices.append(vertex.co)

        # If no lowest vertices found, exit
        if not lowest_z_vertices:
            self.report({'ERROR'}, "No vertices found.")
            return {'CANCELLED'}

        # Calculate the midpoint of the lowest Z vertices
        midpoint = sum(lowest_z_vertices, mathutils.Vector((0.0, 0.0, 0.0))) / len(lowest_z_vertices)

        # Set the 3D cursor to the midpoint
        context.scene.cursor.location = midpoint

        # # Switch to object mode to set the origin
        bpy.ops.object.mode_set(mode='OBJECT')

        # # Set the object origin to the bounding box minimum Z point
        # # bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                
        # Reset the 3D cursor to the world origin (0, 0, 0)
        context.scene.cursor.location = mathutils.Vector((0.0, 0.0, 0.0))

        # self.report({'INFO'}, f"Origin set to lowest Z point: {bounding_box_min}")
        return {'FINISHED'}


classes = (
    Object_OT_GroundObject,
    )
