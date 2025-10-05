import bpy
import json


class Shader_OT_Toggle_Clay(bpy.types.Operator):
    """Toggle a Clay Material on all mesh objects"""
    bl_idname = "shader.toggle_clay_operator"
    bl_label = "Clay Material Preset"
    bl_options = {'REGISTER', 'UNDO'}

    material_name: str = "lightbox-clay"

    def execute(self, context):
        scene = context.scene

        # Remove UV Grid if active
        if scene.get("uv_material_applied", False):
            bpy.ops.shader.toggle_uvgrid('INVOKE_DEFAULT')

        # Toggle Clay
        if scene.get("clay_material_applied", False):
            self.remove_clay_material(context)
            scene["clay_material_applied"] = False
        else:
            self.apply_clay_material(context)
            self.set_viewport_to_material()
            scene["clay_material_applied"] = True
            self.warn_override_active(self.material_name)

        return {'FINISHED'}
    
    def warn_override_active(self, material_name):
        def draw(self, context):
            self.layout.label(text=f"{material_name} override active!")
            self.layout.label(text="Remember to restore original materials before closing.")
        bpy.context.window_manager.popup_menu(draw, title="Override Warning", icon='INFO')


    def create_clay_material(self):
        """Create or get Clay material, clean nodes, and build preset"""
        mat = bpy.data.materials.get(self.material_name)
        if mat is None:
            mat = bpy.data.materials.new(self.material_name)
            
        mat.use_nodes = True
        mat.node_tree.nodes.clear()

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Only one Output + Principled
        output_node = nodes.new("ShaderNodeOutputMaterial")
        principled_node = nodes.new("ShaderNodeBsdfPrincipled")

        output_node.location = (400, 0)
        principled_node.location = (0, 0)

        # Set inputs safely
        if "Base Color" in principled_node.inputs:
            principled_node.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
        if "Roughness" in principled_node.inputs:
            principled_node.inputs["Roughness"].default_value = 0.7
        if "Specular" in principled_node.inputs:
            principled_node.inputs["Specular"].default_value = 0.2

        links.new(principled_node.outputs[0], output_node.inputs[0])

        return mat


    def apply_clay_material(self, context):
        """Apply Clay material to all mesh objects and save originals"""
        scene = context.scene
        mat = self.create_clay_material()
        original_materials = {}

        for obj in scene.objects:
            if obj.type == 'MESH':
                # Save original material names
                mats = [slot.material.name if slot.material else "" for slot in obj.material_slots]
                original_materials[obj.name] = mats

                # Apply clay material
                for slot in obj.material_slots:
                    slot.material = mat

        # Store JSON-encoded data in the scene
        scene["clay_original_materials_json"] = json.dumps(original_materials)

    def remove_clay_material(self, context):
        """Restore original materials to all mesh objects"""
        scene = context.scene
        original_materials = {}

        if "clay_original_materials_json" in scene:
            try:
                original_materials = json.loads(scene["clay_original_materials_json"])
            except Exception:
                pass

        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.name in original_materials:
                mat_names = original_materials[obj.name]

                # Ensure same number of slots
                while len(obj.material_slots) < len(mat_names):
                    obj.data.materials.append(None)

                for i, slot in enumerate(obj.material_slots):
                    # Safe check in case original materials are missing
                    if i < len(mat_names):
                        name = mat_names[i]
                        slot.material = bpy.data.materials.get(name) if name else None
                    else:
                        slot.material = None

        # Clear JSON after restore
        if "clay_original_materials_json" in scene:
            del scene["clay_original_materials_json"]

        # Optionally remove temporary clay material
        clay_mat = bpy.data.materials.get(self.material_name)
        if clay_mat:
            bpy.data.materials.remove(clay_mat, do_unlink=True)

    def set_viewport_to_material(self):
        """Set all 3D Viewports to Material preview shading"""
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'


# ----- free functions
def restore_override_materials_on_exit(dummy):
    scene = bpy.context.scene
    # Check UV Grid
    if scene.get("uv_material_applied", False):
        bpy.ops.shader.toggle_uvgrid('INVOKE_DEFAULT')
    # Check Clay
    if scene.get("clay_material_applied", False):
        bpy.ops.shader.toggle_clay_operator('INVOKE_DEFAULT')
        

# --- Registration ---
classes = (
    Shader_OT_Toggle_Clay,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        

