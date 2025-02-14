import bpy
import mathutils
import math

class Object_OT_GenerateControlRig(bpy.types.Operator):
    bl_idname = "object.generate_control_rig"
    bl_label = "Generate Control Rig"
    bl_description = "Generates a control rig from the Lightbox base rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base_rig_name = "lightbox_base_humanoid"
        control_rig_prefix = "ctrl_"
        control_rig_name = control_rig_prefix + base_rig_name

        # Ensure Object Mode
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Delete existing control rig if it exists
        existing_control_rig = bpy.data.objects.get(control_rig_name)
        if existing_control_rig:
            bpy.data.objects.remove(existing_control_rig, do_unlink=True)

        # Ensure base rig exists
        base_rig = bpy.data.objects.get(base_rig_name)
        if not base_rig or base_rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Base rig not found")
            return {'CANCELLED'}

        # Duplicate the base rig
        control_rig = base_rig.copy()
        control_rig.data = base_rig.data.copy()
        control_rig.name = control_rig_name
        bpy.context.collection.objects.link(control_rig)

        # Disable base rig visibility
        base_rig.hide_set(True)

        # Select and set active control rig
        bpy.context.view_layer.objects.active = control_rig
        control_rig.select_set(True)

        # Set Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Rename bones in the duplicated rig with a prefix
        for bone in control_rig.data.edit_bones:
            bone.name = control_rig_prefix + bone.name

        def set_bone_parent(child_bone_name, parent_bone_name):
            """Sets the parent of a bone without connecting it."""
            parent_bone = control_rig.data.edit_bones.get(parent_bone_name)
            child_bone  = control_rig.data.edit_bones.get(child_bone_name)
            if child_bone and parent_bone:
                child_bone.parent = parent_bone
                child_bone.use_connect = False  # Prevent automatic connection
                
        def create_ik_bone(control_rig, source_bone_name, ik_bone_name, extension_axis="Z", extension_factor=0.05):
            """
            Creates an IK bone based on a source bone.
            
            :param control_rig: The armature object.
            :param source_bone_name: The name of the source bone to extend from.
            :param ik_bone_name: The name of the new IK bone.
            :param extension_axis: The axis to extend on ("X", "Y", or "Z").
            :param extension_factor: The percentage of the rig height to extend.
            :return: The created IK bone (or None if failed).
            """
            source_bone = control_rig.data.edit_bones.get(source_bone_name)
            if not source_bone:
                return None

            z_size = control_rig.dimensions.z  # Use rig height as a reference
            ik_length = z_size * extension_factor  # Extend based on rig height

            # Create the new IK bone
            ik_bone = control_rig.data.edit_bones.new(ik_bone_name)
            ik_bone.head = source_bone.tail

            # Extend the IK bone along the chosen axis
            extension_vector = mathutils.Vector((0, 0, 0))
            if extension_axis == "X":
                extension_vector.x = ik_length
            elif extension_axis == "Y":
                extension_vector.y = ik_length
            elif extension_axis == "Z":
                extension_vector.z = ik_length

            ik_bone.tail = source_bone.tail + extension_vector

            return ik_bone


        def create_pole_target_bone(control_rig, source_bone_name, pole_target_bone_name, direction_axis, direction=1, distance_fraction=0.04, distance_of_bone=0.2):
            """
            Creates a pole target bone based on the given IK bone, with a customizable distance from the source bone,
            and ensures the pole target is unparented after creation.

            :param control_rig: The armature object.
            :param source_bone_name: The name of the source bone (typically an IK bone).
            :param pole_target_bone_name: The name of the new pole target bone.
            :param direction_axis: The axis (X, Y, or Z) along which the pole target will be placed.
            :param direction: The direction of the movement along the axis (1 for positive, -1 for negative).
            :param distance_fraction: Fraction of the armature's size to determine the distance for the pole target placement (default is 0.04).
            :param distance_of_bone: The distance from the source bone to place the pole target, in the given direction (default is 0.2).
            """
            bpy.ops.object.mode_set(mode='EDIT')  # Ensure we're in Edit Mode
            source_bone = control_rig.data.edit_bones.get(source_bone_name)
            
            if source_bone:
                # Get the total size of the armature (for distance calculation)
                z_size = control_rig.dimensions.z  # Use rig height as a reference
                
                # Calculate the distance to move in the given direction based on distance_fraction and distance_of_bone
                pole_target_distance = z_size * distance_fraction * direction  # Apply direction to the distance
                pole_target_offset = z_size * distance_of_bone * direction  # Apply direction to the offset

                # Define the direction for movement (based on axis)
                direction_vector = mathutils.Vector((0, 0, 0))
                offset_vector = mathutils.Vector((0, 0, 0))

                if direction_axis == "X":
                    direction_vector.x = pole_target_distance
                    offset_vector.x = pole_target_offset
                elif direction_axis == "Y":
                    direction_vector.y = pole_target_distance
                    offset_vector.y = pole_target_offset
                elif direction_axis == "Z":
                    direction_vector.z = pole_target_distance
                    offset_vector.z = pole_target_offset

                # Create the pole target bone
                pole_target_bone = control_rig.data.edit_bones.new(pole_target_bone_name)

                # Set the head of the pole target to the head of the source bone
                pole_target_bone.head = source_bone.head

                # Set the tail of the pole target to the head plus the calculated direction and offset
                pole_target_bone.tail = source_bone.head + direction_vector + offset_vector
                pole_target_bone.head = source_bone.head + offset_vector

                # Unparent the pole target to ensure it's not connected to any other bones
                pole_target_bone.parent = None
                pole_target_bone.use_connect = False

                return pole_target_bone
            return None


        def set_ik(ik_bone_name, constraint_bone_name, chain_length):
            """Adds an IK constraint to a bone."""
            bpy.ops.object.mode_set(mode='POSE')  # Switch to Pose Mode
            
            ik_bone = control_rig.pose.bones.get(ik_bone_name)
            constraint_bone = control_rig.pose.bones.get(constraint_bone_name)

            if ik_bone and constraint_bone:
                ik_constraint = constraint_bone.constraints.new(type='IK')
                ik_constraint.target = control_rig
                ik_constraint.subtarget = ik_bone.name
                ik_constraint.chain_count = chain_length

            bpy.ops.object.mode_set(mode='OBJECT')  # Return to Object Mode

        def stylize_bone(bone_name, shape_key, color_index):
            """Stylizes a bone with a custom shape and assigns a color index."""
            bpy.ops.object.mode_set(mode='POSE')

            pose_bone = control_rig.pose.bones.get(bone_name)
            if not pose_bone:
                return

            # Set custom shape
            shape_object = bpy.data.objects.get(shape_key)
            if shape_object:
                pose_bone.custom_shape = shape_object
            
            # Validate and clamp the color index (Blender supports 0–31)
            color_index = max(0, min(color_index, 20))
            # set color to bone
            bpy.context.object.data.bones[bone_name].color.palette = f"THEME{color_index:02d}"

            bpy.ops.object.mode_set(mode='OBJECT')

        def set_pole_target(control_rig, ik_bone_name, pole_target_bone_name, pole_angle=0):
            """
            Adds a pole target constraint to the given IK bone, setting the specified pole target bone.
            If the constraint already exists, it modifies it instead of creating a new one.

            :param control_rig: The armature object.
            :param ik_bone_name: The name of the IK bone to add the pole target to.
            :param pole_target_bone_name: The name of the pole target bone.
            """
            # Ensure Pose Mode before applying constraints
            bpy.ops.object.mode_set(mode='POSE')

            ik_bone = control_rig.pose.bones.get(ik_bone_name)
            if ik_bone:
                # Check if an existing IK constraint already exists
                existing_ik_constraint = None
                for constraint in ik_bone.constraints:
                    if constraint.type == 'IK':
                        existing_ik_constraint = constraint
                        break
                
                if not existing_ik_constraint:
                    # If no IK constraint exists, create one
                    existing_ik_constraint = ik_bone.constraints.new(type='IK')
                
                # Set or update the pole target
                existing_ik_constraint.pole_target = control_rig
                existing_ik_constraint.pole_subtarget = pole_target_bone_name
                existing_ik_constraint.pole_angle = math.radians(pole_angle)
                
                return True
            return False


        sides = [
            {"side": "L", "color_index": 4},  # Left (Blue)
            {"side": "R", "color_index": 4}   # Right (Red)
        ]
        
        # foot ik
        for data in sides:
            bpy.ops.object.mode_set(mode='EDIT')
            side = data["side"]
            ik_bone_name = f"ctrl_lightbox_ik-hand.{side}"
            pt_bone_name = f"ctrl_lightbox_pt-arm.{side}"
            lower_arm_bone = f"ctrl_lightbox_lower-arm.{side}"

            # Create IK Bone
            create_ik_bone(control_rig, lower_arm_bone, ik_bone_name, "Z", 0.05)
            create_pole_target_bone(control_rig, lower_arm_bone, pt_bone_name, "Y", 1, 0.04, 0.2)
            # Set Parent
            set_bone_parent(ik_bone_name, "ctrl_lightbox_chest")
            # Apply IK Constraints
            set_ik(ik_bone_name, lower_arm_bone, chain_length=2)
            set_pole_target(control_rig, lower_arm_bone, pt_bone_name, -90)
            # Stylize IK Bone
            stylize_bone(ik_bone_name, "ik_handle_shape", data["color_index"])
        
        # foot ik
        for data in sides:
            bpy.ops.object.mode_set(mode='EDIT')
            side = data["side"]
            ik_bone_name = f"ctrl_lightbox_ik-foot.{side}"
            pt_bone_name = f"ctrl_lightbox_pt-leg.{side}"
            lower_leg_bone = f"ctrl_lightbox_lower-leg.{side}"

            # Create IK Bone
            create_ik_bone(control_rig, lower_leg_bone, ik_bone_name, "Y", 0.05)
            create_pole_target_bone(control_rig, lower_leg_bone, pt_bone_name, "Y", -1, 0.04, 0.2)
            # Set Parent
            set_bone_parent(ik_bone_name, "ctrl_lightbox_pelvis")
            # Apply IK Constraints
            set_ik(ik_bone_name, lower_leg_bone, chain_length=2)
            set_pole_target(control_rig, lower_leg_bone, pt_bone_name)
            # Stylize IK Bone
            stylize_bone(ik_bone_name, "ik_handle_shape", data["color_index"])    
            
        # Return to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Control rig generated successfully")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(Object_OT_GenerateControlRig)

def unregister():
    bpy.utils.unregister_class(Object_OT_GenerateControlRig)
