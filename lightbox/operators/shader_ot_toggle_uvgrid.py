import bpy

class Shader_OT_Toggle_UVGrid(bpy.types.Operator):
    """Toggle a UV Test Grid Material on all mesh objects"""
    bl_idname = "shader.toggle_uvgrid"
    bl_label = "UV Grid Preset"
    bl_options = {'REGISTER', 'UNDO'}

    material_name: str = "lightbox-uvgrid"

    def execute(self, context):
        scene = context.scene

        # Ensure original_materials storage exists
        if "original_materials" not in scene:
            scene["original_materials"] = {}

        # Remove Clay override if active
        if scene.get("clay_material_applied", False):
            bpy.ops.shader.toggle_clay_operator('INVOKE_DEFAULT')

        # Toggle UV Grid
        if scene.get("uv_material_applied", False):
            self.remove_uv_material(context)
        else:
            self.apply_uv_material(context)
            self.set_viewport_to_material()

        # Update toggle state
        scene["uv_material_applied"] = not scene.get("uv_material_applied", False)

        return {'FINISHED'}

    def create_uv_material(self):
        """Create or get the UV grid material"""
        mat = bpy.data.materials.get(self.material_name)
        if mat is None:
            mat = bpy.data.materials.new(self.material_name)
            mat.use_nodes = True
        else:
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
        mat = self.create_uv_material()
        original_materials = {}

        for obj in context.scene.objects:
            if obj.type == 'MESH':
                # Save original material names
                original_materials[obj.name] = [slot.material.name if slot.material else None for slot in obj.material_slots]
                for slot in obj.material_slots:
                    slot.material = mat

        context.scene["original_materials"] = original_materials

    def remove_uv_material(self, context):
        """Restore original materials to all mesh objects"""
        original_materials = context.scene.get("original_materials", {})

        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.name in original_materials:
                for i, slot in enumerate(obj.material_slots):
                    mat_name = original_materials[obj.name][i]
                    slot.material = bpy.data.materials.get(mat_name) if mat_name else None

        # Clear saved originals
        context.scene["original_materials"] = {}

    def set_viewport_to_material(self):
        """Set all 3D Viewports to Material preview shading"""
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'


# --- Helper function ---
def remove_override_material(context, material_name):
    """Restore original materials and remove override material"""
    scene = context.scene
    original_materials = scene.get("original_materials", {})

    for obj in context.scene.objects:
        if obj.type == 'MESH' and obj.name in original_materials:
            for i, slot in enumerate(obj.material_slots):
                mat_name = original_materials[obj.name][i]
                slot.material = bpy.data.materials.get(mat_name) if mat_name else None

    scene["original_materials"] = {}

    # Remove the override material
    mat = bpy.data.materials.get(material_name)
    if mat:
        bpy.data.materials.remove(mat)


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
