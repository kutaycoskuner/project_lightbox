import bpy
import mathutils
import math
import os

class Object_OT_GenerateControlRig(bpy.types.Operator):
    bl_idname = "object.generate_control_rig"
    bl_label = "Generate Control Rig"
    bl_description = "Generates a control rig from the Lightbox base rig"
    bl_options = {'REGISTER', 'UNDO'}


    def import_control_shapes(self):
        # Check if the control shapes collection already exists at scene root
        if bpy.data.collections.get("control-shapes"):
            self.report({'INFO'}, "Control shapes already imported.")
            return

        # Ensure we are in Object Mode
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Define the path to the blend file inside the addon
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        blend_path = os.path.join(addon_dir, "../_data/", "control-shapes.blend")
        # The imported structure has a top-level collection "_lightbox"
        object_name  = "_lightbox" 
        directory    = os.path.join(blend_path, "Collection")  # Use os.path.join for better compatibility

        try:
            bpy.ops.wm.append(
                filepath=blend_path,
                directory=directory,
                filename=object_name,
                link=False  # False means we copy it into the current blend file
            )
            self.report({'INFO'}, "Added lightbox control shapes")
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to add lightbox control shapes: {str(e)}")
            return {'CANCELLED'}

        # At this point, the file brings in a collection structure:
        # _lightbox
        #   └── control-shapes
        # We want to isolate the control shapes into their own collection at the scene root and hide it.
        self.isolate_subcollection(parent_collection_name="_lightbox", subcollection_name="control-shapes")

    def isolate_subcollection(self, parent_collection_name, subcollection_name):
        """
        Moves the objects from a subcollection (subcollection_name) that is inside a parent (parent_collection_name)
        into a new collection at the scene root (with the same subcollection_name), then hides the new collection.
        """
        parent_col = bpy.data.collections.get(parent_collection_name)
        if parent_col is None:
            self.report({'ERROR'}, f"Parent collection '{parent_collection_name}' not found.")
            return

        source_subcol = parent_col.children.get(subcollection_name)
        if source_subcol is None:
            self.report({'INFO'}, f"Subcollection '{subcollection_name}' not found in '{parent_collection_name}'.")
            return

        # Create a new collection for control shapes at the scene root if it doesn't exist already.
        new_col = bpy.data.collections.get(subcollection_name)
        if new_col is None:
            new_col = bpy.data.collections.new(name=subcollection_name)
            bpy.context.scene.collection.children.link(new_col)

        # Move objects from source_subcol into new_col
        for obj in list(source_subcol.objects):
            # Unlink from the source subcollection
            source_subcol.objects.unlink(obj)
            # Link to the new collection if not already linked
            if obj.name not in new_col.objects:
                new_col.objects.link(obj)

        # Optionally, remove the now-empty source subcollection from the parent.
        if source_subcol.users == 0 or len(source_subcol.objects) == 0:
            parent_col.children.unlink(source_subcol)
            bpy.data.collections.remove(source_subcol)

        # Hide the new collection so that control shapes are not visible in viewport or render.
        new_col.hide_viewport = True
        new_col.hide_render = True
        self.report({'INFO'}, f"Isolated and hidden subcollection '{subcollection_name}' at scene root.")

    def execute(self, context):
        
        #       import control shapes       ----------------------------------------------
        self.import_control_shapes()
                
        #       generate rig       -------------------------------------------------------
        
        base_rig_name = "lightbox_base_humanoid"
        control_rig_prefix = "lb_base_"
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
        control_rig.data =  base_rig.data.copy()
        control_rig.name = control_rig_name
        bpy.context.collection.objects.link(control_rig)

        # bone groups
        ctrl_bone_collection = control_rig.data.collections.new(name='control_bones')
        def_bone_collection = control_rig.data.collections.new(name='deformation_bones')
        mch_bone_collection = control_rig.data.collections.new(name='mechanics_bones')
        

        # Disable base rig visibility
        base_rig.hide_set(True)

        # Select and set active control rig
        bpy.context.view_layer.objects.active = control_rig
        control_rig.select_set(True)

        # Set Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Rename bones in the duplicated rig with a prefix
        control_rig.name = "lb_rig"
        control_rig.data.name = control_rig.name
        for bone in control_rig.data.edit_bones:
            name_parts = bone.name.split("_")  # Split name by underscores
            if len(name_parts) > 1:
                last_part = name_parts.pop()  # Extract the last part
                bone.name = control_rig_prefix + last_part  # Add prefix to the last part
            else:
                bone.name = control_rig_prefix + bone.name  # If no underscores, just add prefix


        def set_bone_parent(child_bone_name, parent_bone_name, inverted=False):
            """Sets the parent of a bone without connecting it."""
            parent_bone = control_rig.data.edit_bones.get(parent_bone_name)
            child_bone  = control_rig.data.edit_bones.get(child_bone_name)
            
            if child_bone and inverted:
                child_bone.use_connect = True   
            elif child_bone: 
                child_bone.use_connect = False   # disconnect means offset
            
            if child_bone and parent_bone:
                child_bone.parent = parent_bone

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
            
            ik_bone.use_deform = False
            ctrl_bone_collection.assign(ik_bone)
            
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
                
                pole_target_bone.use_deform = False
                ctrl_bone_collection.assign(pole_target_bone)

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

        def set_copy_location(control_rig, target_bone_name, source_bone_name, use_tail=False, influence=1.0, use_local_space=False):
            """
            Adds a Copy Location constraint to a target bone, making it follow the source bone's head or tail.

            :param control_rig: The armature object.
            :param source_bone_name: The name of the source bone.
            :param target_bone_name: The name of the target bone.
            :param use_tail: If True, the target will copy the tail location of the source bone.
            :param influence: The influence of the constraint (default is 1.0).
            """
            # Ensure we're in Pose Mode
            bpy.ops.object.mode_set(mode='POSE')

            source_bone = control_rig.pose.bones.get(source_bone_name)
            target_bone = control_rig.pose.bones.get(target_bone_name)

            if not source_bone or not target_bone:
                print(f"Error: One of the bones '{source_bone_name}' or '{target_bone_name}' was not found.")
                return
            

            # Create Copy Location constraint
            copy_location = target_bone.constraints.new(type='COPY_LOCATION')
            copy_location.target = control_rig
            copy_location.subtarget = source_bone_name
            copy_location.use_offset = False  # Ensures exact positioning
            copy_location.influence = influence

            space = 'LOCAL' if use_local_space else 'POSE'
            copy_location.owner_space = space
            copy_location.target_space = space

            # Adjust location based on whether to copy head or tail
            if use_tail:
                copy_location.head_tail = 1.0  # Copy tail location
            else:
                copy_location.head_tail = 0.0  # Copy head location

            # Return to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')
        
    
        def set_copy_rotation(control_rig, target_bone_name, source_bone_name, influence=1.0, use_local_space=False, mix_mode='REPLACE'):
            """
            Adds a Copy Rotation constraint to a target bone, making it follow the source bone's rotation.

            :param control_rig: The armature object.
            :param target_bone_name: The name of the target bone.
            :param source_bone_name: The name of the source bone.
            :param influence: The influence of the constraint (default is 1.0).
            :param use_local_space: Whether to use Local Space instead of Pose Space.
            :param mix_mode: The mix mode for the rotation ('REPLACE', 'ADD', 'AFTER', 'BEFORE').
            """
            bpy.ops.object.mode_set(mode='POSE')
            
            target_bone = control_rig.pose.bones.get(target_bone_name)
            if not target_bone:
                print(f"Error: Target bone '{target_bone_name}' was not found.")
                return
            
            copy_rotation = target_bone.constraints.new(type='COPY_ROTATION')
            copy_rotation.target = control_rig
            copy_rotation.subtarget = source_bone_name
            copy_rotation.influence = influence
            
            space = 'LOCAL' if use_local_space else 'POSE'
            copy_rotation.owner_space = space
            copy_rotation.target_space = space
            copy_rotation.mix_mode = mix_mode

        def stylize_bone(bone_name, shape_key, color_index, shape_scale=1):
            """Stylizes a bone with a custom shape and assigns a color index."""
            bpy.ops.object.mode_set(mode='POSE')

            pose_bone = control_rig.pose.bones.get(bone_name)
            if not pose_bone:
                return

            # Set custom shape
            shape_object = bpy.data.objects.get(shape_key)
            if shape_object:
                pose_bone.custom_shape = shape_object
                pose_bone.custom_shape_scale_xyz[0] = shape_scale
                pose_bone.custom_shape_scale_xyz[1] = shape_scale
                pose_bone.custom_shape_scale_xyz[2] = shape_scale
            
            # Validate and clamp the color index (Blender supports 0–31)
            color_index = max(0, min(color_index, 20))
            # set color to bone
            bpy.context.object.data.bones[bone_name].color.palette = f"THEME{color_index:02d}"
            bpy.context.object.pose.bones[bone_name].color.palette = f"THEME{color_index:02d}"
            
            

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


        def set_limit_rotation(control_rig, target_bone_name, min_x=None, max_x=None, min_y=None, max_y=None, min_z=None, max_z=None, use_local_space=False):
            """
            Adds a Limit Rotation constraint to a target bone with specified limits.

            :param control_rig: The armature object.
            :param target_bone_name: The name of the target bone.
            :param min_x: Minimum X rotation (in degrees) or None to disable.
            :param max_x: Maximum X rotation (in degrees) or None to disable.
            :param min_y: Minimum Y rotation (in degrees) or None to disable.
            :param max_y: Maximum Y rotation (in degrees) or None to disable.
            :param min_z: Minimum Z rotation (in degrees) or None to disable.
            :param max_z: Maximum Z rotation (in degrees) or None to disable.
            :param use_local_space: Whether to use Local Space instead of World Space.
            """
            bpy.ops.object.mode_set(mode='POSE')
            
            target_bone = control_rig.pose.bones.get(target_bone_name)
            if not target_bone:
                print(f"Error: Target bone '{target_bone_name}' was not found.")
                return
            
            limit_rotation = target_bone.constraints.new(type='LIMIT_ROTATION')
            
            if min_x is not None:
                limit_rotation.use_limit_x = True
                limit_rotation.min_x = math.radians(min_x)
            if max_x is not None:
                limit_rotation.use_limit_x = True
                limit_rotation.max_x = math.radians(max_x)
            if min_y is not None:
                limit_rotation.use_limit_y = True
                limit_rotation.min_y = math.radians(min_y)
            if max_y is not None:
                limit_rotation.use_limit_y = True
                limit_rotation.max_y = math.radians(max_y)
            if min_z is not None:
                limit_rotation.use_limit_z = True
                limit_rotation.min_z = math.radians(min_z)
            if max_z is not None:
                limit_rotation.use_limit_z = True
                limit_rotation.max_z = math.radians(max_z)
            
            space = 'LOCAL' if use_local_space else 'WORLD'
            limit_rotation.owner_space = space
            
            bpy.ops.object.mode_set(mode='OBJECT')

        def set_bone_roll(control_rig, bone_name, roll_degrees):
            """
            Sets the roll of a bone in Edit Mode.

            :param control_rig: The armature object.
            :param bone_name: The name of the bone.
            :param roll_degrees: The desired roll in degrees.
            """
            # Ensure we're in Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')

            # Get the bone in edit mode
            bone = control_rig.data.edit_bones.get(bone_name)
            if not bone:
                print(f"Error: Bone '{bone_name}' not found.")
                bpy.ops.object.mode_set(mode='OBJECT')
                return

            # Set the roll (convert degrees to radians)
            bone.roll = math.radians(roll_degrees)

            # Return to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')

        def create_parallel_bone(rig, source_bone_name, parallel_bone, scale=0.5, base_head=True, reverse_direction=False, offset_scale=0, side_offset_scale=0):
            """Creates a foot roller bone in the same direction as the source bone, with optional side offset."""
            if source_bone_name not in rig.data.bones:
                print(f"Bone '{source_bone_name}' not found in rig.")
                return None

            bpy.ops.object.mode_set(mode='EDIT')
            eb = rig.data.edit_bones
            source_bone = eb[source_bone_name]

            # Calculate direction
            bone_direction = source_bone.tail - source_bone.head
            bone_direction.normalize()
            if reverse_direction:
                bone_direction = -bone_direction

            # Compute perpendicular direction for side offset
            reference_axis = mathutils.Vector((0, 0, 1))  # Default reference axis
            if abs(bone_direction.dot(reference_axis)) > 0.99:  # Check if bone is nearly parallel to Z
                reference_axis = mathutils.Vector((0, 1, 0))  # Use Y instead

            side_direction = bone_direction.cross(reference_axis)
            side_direction.normalize()

            # Compute offsets
            offset_move = bone_direction * offset_scale * source_bone.length
            side_offset_move = side_direction * side_offset_scale * source_bone.length

            # Create the parallel bone
            para_bone = eb.new(name=parallel_bone)
            if base_head:
                para_bone.head = source_bone.tail - offset_move + side_offset_move
            else:
                para_bone.head = source_bone.head - offset_move + side_offset_move

            para_bone.tail = para_bone.head + (bone_direction * source_bone.length * scale) 
            para_bone.use_deform = False

            bpy.ops.object.mode_set(mode='OBJECT')

        def assignto_bone_collection(armature, bone_name, collection):
            bpy.ops.object.mode_set(mode='EDIT')
            bone = armature.data.edit_bones[bone_name]
            if not bone:
                print(f"Bone '{bone_name}' not found in armature '{armature.name}'.")
                return
            
            # Assign the bone to the collection
            collection.assign(bone)
            print(f"Bone '{bone_name}' assigned to collection '{collection.name}'.")




        # disable main bone deform
        main_bone = control_rig.data.edit_bones.get(f"{control_rig_prefix}main")
        if main_bone: main_bone.use_deform = False
        stylize_bone(main_bone.name, "base", 12, 6)

        sides = [
            {"side": "L", "color_index": 4},  # Left (Blue)
            {"side": "R", "color_index": 4}   # Right (Red)
        ]
        
        # hand ik
        for data in sides:
            bpy.ops.object.mode_set(mode='EDIT')
            side = data["side"]
            ik_bone_name = f"{control_rig_prefix}ik-hand.{side}"
            pt_bone_name = f"{control_rig_prefix}pt-arm.{side}"
            lower_bone_name = f"{control_rig_prefix}lower-arm.{side}"

            # Create bones
            create_ik_bone(control_rig, lower_bone_name, ik_bone_name, "Z", 0.05)
            create_pole_target_bone(control_rig, lower_bone_name, pt_bone_name, "Y", 1, 0.04, 0.2)
            # Set hierarchy
            set_bone_parent(ik_bone_name, f"{control_rig_prefix}chest")
            set_bone_parent(pt_bone_name, ik_bone_name) 
            # Apply constraints
            set_ik(ik_bone_name, lower_bone_name, chain_length=2)
            set_pole_target(control_rig, lower_bone_name, pt_bone_name, -125)
            # Stylize bones
            stylize_bone(ik_bone_name, "ik_hand", 9)
            stylize_bone(pt_bone_name, "pole_target", 7)
            
        # foot ik
        for data in sides:
            bpy.ops.object.mode_set(mode='EDIT')
            side = data["side"]
            
            lower_leg_bone = f"{control_rig_prefix}lower-leg.{side}"
            foot_bone_name = f"{control_rig_prefix}foot.{side}"
            paw_bone_name = f"{control_rig_prefix}foot-paw.{side}"
            
            ik_bone_name = f"ctrl_lightbox_ik-foot.{side}"
            pt_bone_name = f"ctrl_lightbox_pt-leg.{side}"
            pivot_ik_name = f"ctrl_lightbox_ik-pivot-foot.{side}"
            pivot_paw_name = f"ctrl_lightbox_ik-pivot-paw.{side}"
            pivot_heel_name = f"ctrl_lightbox_ik-pivot-heel.{side}"
            roll_in_name = f"ctrl_lightbox_foot-roll-in.{side}"
            roll_out_name = f"ctrl_lightbox_foot-roll-out.{side}"
            ctrl_foot_name = f"ctrl_lightbox_foot-controller.{side}"
            

            # Create bones
            #  create_ik_bone(control_rig, lower_leg_bone, ik_bone_name, "Y", 0.05)
            create_parallel_bone(control_rig, foot_bone_name, ik_bone_name, 0.5, False)
            create_parallel_bone(control_rig, foot_bone_name, pivot_ik_name, 0.5, True, True)
            create_parallel_bone(control_rig, paw_bone_name, pivot_paw_name, 1.0, True, True)
            create_parallel_bone(control_rig, pivot_paw_name, pivot_heel_name, 0.5, True, True, 1.5) 
            create_parallel_bone(control_rig, pivot_heel_name, roll_in_name, 1.0, False, False, 0, 1.6) 
            create_parallel_bone(control_rig, pivot_heel_name, roll_out_name, 1.0, False, False, 0, -0.6) 
            create_parallel_bone(control_rig, pivot_heel_name, ctrl_foot_name, 2.0, False) 
            create_pole_target_bone(control_rig, lower_leg_bone, pt_bone_name, "Y", -1, 0.04, 0.2)
            # create_parallel_ik(control_rig, foot_bone_name, foot_roller_name)

            # assign bones to collections            
            assignto_bone_collection(control_rig, ik_bone_name,     mch_bone_collection)
            assignto_bone_collection(control_rig, pivot_ik_name,    mch_bone_collection)
            assignto_bone_collection(control_rig, pivot_heel_name,  mch_bone_collection)
            assignto_bone_collection(control_rig, roll_in_name,     mch_bone_collection)
            assignto_bone_collection(control_rig, roll_out_name, mch_bone_collection)
            bpy.context.object.data.collections_all["mechanics_bones"].is_visible = False
            # Set hierarchy
            set_bone_parent(ik_bone_name, control_rig_prefix + 'pelvis')
            set_bone_parent(ik_bone_name, pivot_ik_name)
            set_bone_parent(pivot_ik_name, pivot_paw_name)
            set_bone_parent(pivot_paw_name, roll_in_name)
            set_bone_parent(roll_in_name, roll_out_name)
            set_bone_parent(roll_out_name, pivot_heel_name)
            set_bone_parent(pt_bone_name, ctrl_foot_name)
            # set_bone_parent(foot_bone_name, ik_bone_name)
            # set_bone_parent(pt_bone_name, ik_bone_name)
            # Apply constraints
            set_ik(ik_bone_name, lower_leg_bone, chain_length=2)
            set_ik(pivot_paw_name, paw_bone_name, chain_length=1)
            set_pole_target(control_rig, lower_leg_bone, pt_bone_name, -90)
            # set_copy_location(control_rig, foot_bone_name, ik_bone_name)
            set_copy_rotation(control_rig, foot_bone_name, ik_bone_name)
            
            set_copy_location(control_rig, pivot_heel_name, ctrl_foot_name)
            # set_copy_location(control_rig, pt_bone_name, ctrl_foot_name, use_local_space=True)
            # set_copy_rotation(control_rig, pt_bone_name, ctrl_foot_name, use_local_space=True)
            set_copy_rotation(control_rig, pivot_heel_name, ctrl_foot_name, use_local_space=True, mix_mode="AFTER")
            set_copy_rotation(control_rig, pivot_ik_name, ctrl_foot_name, use_local_space=True, mix_mode="AFTER")
            set_copy_rotation(control_rig, roll_in_name, ctrl_foot_name, use_local_space=True, mix_mode="AFTER")
            set_copy_rotation(control_rig, roll_out_name, ctrl_foot_name, use_local_space=True, mix_mode="AFTER")
            set_limit_rotation(control_rig, pivot_heel_name, 0, 45, use_local_space=True)
            set_bone_roll(control_rig, pivot_ik_name, -180)
            set_limit_rotation(control_rig, pivot_ik_name, -45, 0, use_local_space=True)
            set_limit_rotation(control_rig, roll_in_name, min_y=0, max_y=45, use_local_space=True)
            set_limit_rotation(control_rig, roll_out_name, min_y=-45, max_y=0, use_local_space=True)
            
            bpy.context.object.pose.bones[pivot_ik_name].constraints["Copy Rotation"].use_y = False
            bpy.context.object.pose.bones[pivot_ik_name].constraints["Copy Rotation"].use_z = False
            bpy.context.object.pose.bones[pivot_heel_name].constraints["Copy Rotation"].use_y = False
            bpy.context.object.pose.bones[roll_in_name].constraints["Copy Rotation"].use_x = False
            bpy.context.object.pose.bones[roll_in_name].constraints["Copy Rotation"].use_y = True
            bpy.context.object.pose.bones[roll_in_name].constraints["Copy Rotation"].use_z = False
            bpy.context.object.pose.bones[roll_out_name].constraints["Copy Rotation"].use_x = False
            bpy.context.object.pose.bones[roll_out_name].constraints["Copy Rotation"].use_y = True
            bpy.context.object.pose.bones[roll_out_name].constraints["Copy Rotation"].use_z = False
            
            
            # Stylize bones 
            stylize_bone(ctrl_foot_name, "ik_hand", 9)
            stylize_bone(pivot_paw_name, "end", 9)
            stylize_bone(pt_bone_name, "pole_target", 7)
            
            bpy.ops.object.mode_set(mode='POSE')
            paw_bone = control_rig.pose.bones.get(pivot_paw_name)
            if paw_bone:
                paw_bone.custom_shape_rotation_euler[0] = 2.2340
            heel_bone = control_rig.pose.bones.get(ctrl_foot_name)
            if heel_bone:
                heel_bone.custom_shape_translation[2] = 0.0275

            


            
        # Return to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')
        
        self.report({'INFO'}, "Control rig generated successfully")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(Object_OT_GenerateControlRig)

def unregister():
    bpy.utils.unregister_class(Object_OT_GenerateControlRig)
