import bpy

class Shader_OT_Toggle_Clay(bpy.types.Operator):
    """Toggle a simple Clay Material on all mesh objects"""
    bl_idname = "shader.toggle_clay_operator"
    bl_label = "Clay Material Preset"
    bl_options = {'REGISTER', 'UNDO'}

    material_name: str = "lightbox-clay"

    def execute(self, context):
        scene = context.scene

        # Ensure original_materials storage exists
        if "original_materials" not in scene:
            scene["original_materials"] = {}

        # Remove UV Grid override if active
        if scene.get("uv_material_applied", False):
            bpy.ops.shader.toggle_uvgrid('INVOKE_DEFAULT')

        # Toggle Clay Material
        if scene.get("clay_material_applied", False):
            self.remove_clay_material(context)
        else:
            self.apply_clay_material(context)
            self.set_viewport_to_material()

        # Update toggle state
        scene["clay_material_applied"] = not scene.get("clay_material_applied", False)

        return {'FINISHED'}

    def create_clay_material(self):
        """Create or get the Clay material"""
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
        diffuse_node = nodes.new("ShaderNodeBsdfDiffuse")

        output_node.location = (400, 0)
        diffuse_node.location = (0, 0)

        # Optionally, set a simple gray color for Clay
        diffuse_node.inputs["Color"].default_value = (0.8, 0.8, 0.8, 1.0)

        # Link
        links.new(diffuse_node.outputs["BSDF"], output_node.inputs["Surface"])

        return mat

    def apply_clay_material(self, context):
        """Apply Clay material to all mesh objects and save originals"""
        mat = self.create_clay_material()
        original_materials = {}

        for obj in context.scene.objects:
            if obj.type == 'MESH':
                # Save original material names
                original_materials[obj.name] = [slot.material.name if slot.material else None for slot in obj.material_slots]
                for slot in obj.material_slots:
                    slot.material = mat

        context.scene["original_materials"] = original_materials

    def remove_clay_material(self, context):
        """Restore original materials to all mesh objects"""
        original_materials = context.scene.get("original_materials", {})

        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.name in original_materials:
                for i, slot in enumerate(obj.material_slots):
                    mat_name = original_materials[obj.name][i]
                    slot.material = bpy.data.materials.get(mat_name) if mat_name else None

        context.scene["original_materials"] = {}

    def set_viewport_to_material(self):
        """Set all 3D Viewports to Material preview shading"""
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'


# --- Helper function ---
def remove_clay_material_override(context, material_name):
    """Restore original materials and remove Clay material"""
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
    Shader_OT_Toggle_Clay,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
