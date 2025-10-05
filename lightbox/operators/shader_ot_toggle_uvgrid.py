import bpy
import json


class Shader_OT_Toggle_UVGrid(bpy.types.Operator):
    """Toggle a UV Test Grid Material on all mesh objects"""
    bl_idname = "shader.toggle_uvgrid"
    bl_label = "UV Grid Preset"
    bl_options = {'REGISTER', 'UNDO'}

    material_name: str = "lightbox-uvgrid"

    def execute(self, context):
        scene = context.scene

        # Remove Clay if active
        if scene.get("clay_material_applied", False):
            bpy.ops.shader.toggle_clay_operator('INVOKE_DEFAULT')

        # Toggle UV Grid
        if scene.get("uv_material_applied", False):
            self.remove_uv_material(context)
            scene["uv_material_applied"] = False
        else:
            self.apply_uv_material(context)
            self.set_viewport_to_material()
            scene["uv_material_applied"] = True
            self.warn_override_active(self.material_name)

        return {'FINISHED'}

    def warn_override_active(self, material_name):
        def draw(self, context):
            self.layout.label(text=f"{material_name} override active!")
            self.layout.label(text="Remember to restore original materials before closing.")
        bpy.context.window_manager.popup_menu(draw, title="Override Warning", icon='INFO')

    def create_uv_material(self):
        """Create or get the UV grid material"""
        mat = bpy.data.materials.get(self.material_name)
        if mat is None:
            mat = bpy.data.materials.new(self.material_name)
            
        mat.use_nodes = True
        mat.node_tree.nodes.clear()

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Nodes
        output_node = nodes.new("ShaderNodeOutputMaterial")
        emission_node = nodes.new("ShaderNodeEmission")
        tex_node = nodes.new("ShaderNodeTexImage")

        output_node.location = (400, 0)
        emission_node.location = (0, 0)
        tex_node.location = (-400, 0)

        # Create UV Grid Image
        img_name = "tex-uv_grid01"
        img = bpy.data.images.get(img_name)
        if img is None:
            img = bpy.data.images.new(img_name, width=2048, height=2048)
            img.generated_type = 'UV_GRID'
        tex_node.image = img

        # Links
        links.new(tex_node.outputs["Color"], emission_node.inputs["Color"])
        links.new(emission_node.outputs["Emission"], output_node.inputs["Surface"])

        return mat

    def apply_uv_material(self, context):
        """Apply UV material to all mesh objects and save originals"""
        scene = context.scene
        mat = self.create_uv_material()
        original_materials = {}

        for obj in scene.objects:
            if obj.type == 'MESH':
                mats = [slot.material.name if slot.material else "" for slot in obj.material_slots]
                original_materials[obj.name] = mats

                for slot in obj.material_slots:
                    slot.material = mat

        # Store JSON-encoded data in the scene
        scene["shader_original_materials_json"] = json.dumps(original_materials)

    def remove_uv_material(self, context):
        """Restore original materials to all mesh objects"""
        scene = context.scene
        original_materials = {}

        if "shader_original_materials_json" in scene:
            try:
                original_materials = json.loads(scene["shader_original_materials_json"])
            except Exception:
                pass

        for obj in scene.objects:
            if obj.type == 'MESH' and obj.name in original_materials:
                mat_names = original_materials[obj.name]

                # Ensure same number of slots
                while len(obj.material_slots) < len(mat_names):
                    obj.data.materials.append(None)

                for i, name in enumerate(mat_names):
                    obj.material_slots[i].material = bpy.data.materials.get(name) if name else None

        # Clear data from scene
        if "shader_original_materials_json" in scene:
            del scene["shader_original_materials_json"]

    def set_viewport_to_material(self):
        """Set all 3D Viewports to Material preview shading"""
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'




# --- Registration ---
classes = (
    Shader_OT_Toggle_UVGrid,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
