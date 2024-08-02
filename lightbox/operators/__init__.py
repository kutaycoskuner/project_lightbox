import bpy


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


class Shader_OT_ToggleClay(bpy.types.Operator):
    bl_label = "Toggle Clay Override"
    bl_idname = "shader.toggle_clay_operator"
    clay_material_name = "lightbox_clay"

    def execute(self, context):
        scene = context.scene

        if not scene.get("original_materials"):
            scene["original_materials"] = {}

        if scene.get("clay_material_applied", False):
            self.remove_clay_material(context)
        else:
            self.apply_clay_material(context)

        scene["clay_material_applied"] = not scene.get(
            "clay_material_applied", False)

        return {'FINISHED'}

    def create_clay_material(self):
        material_clay = bpy.data.materials.get(self.clay_material_name)
        if material_clay is None:
            material_clay = bpy.data.materials.new(
                name=self.clay_material_name)
            material_clay.use_nodes = True
        else:
            material_clay.use_nodes = True
            nodes = material_clay.node_tree.nodes
            nodes.clear()

        nodes = material_clay.node_tree.nodes
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        base01_node = nodes.new('ShaderNodeBsdfPrincipled')

        # Set the location of the nodes
        material_output.location = (400, 0)
        base01_node.location = (-200, 0)

        # Set the properties of the Glass BSDF node
        base01_node.inputs[0].default_value = (1, 1, 1, 1)  # Color

        material_clay.node_tree.links.new(
            base01_node.outputs[0], material_output.inputs[0])

        return material_clay

    def apply_clay_material(self, context):
        material_clay = self.create_clay_material()
        scene = context.scene

        original_materials = {}
        for obj in context.scene.objects:
            if obj.type == 'MESH':
                original_materials[obj.name] = [
                    slot.material for slot in obj.material_slots]
                for slot in obj.material_slots:
                    slot.material = material_clay

        scene["original_materials"] = original_materials

    def remove_clay_material(self, context):
        scene = context.scene 

        original_materials = scene["original_materials"]
        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.name in original_materials:
                for i, slot in enumerate(obj.material_slots):
                    slot.material = original_materials[obj.name][i]
        scene["original_materials"] = {}


class View3D_OT_FocusOutliner(bpy.types.Operator):
    bl_idname = "view3d.focus_outliner"
    bl_label = "Focus Selected on Outliner"

    def execute(self, context):
        # Get the active object
        if bpy.context.screen.areas:
            for area in bpy.context.screen.areas:
                if area.type == 'OUTLINER':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            with bpy.context.temp_override(
                                area=area, region=region):
                                bpy.ops.outliner.show_active()
                                break
                    break
        return {'FINISHED'}


classes = (
    View3D_OT_FocusOutliner,
    Shader_OT_ToggleClay,
    )
