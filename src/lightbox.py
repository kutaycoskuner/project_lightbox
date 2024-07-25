# ----------------------------------------------------------------------------------------
# info
# ----------------------------------------------------------------------------------------
import bpy
bl_info = {
    "name": "Lightbox",
    "author": "lichzelg",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Tool",
    "description": "Overrides a default clay material on Eevee",
    "warning": "",
    "wiki_url": "",
    "category": "Material"
}

# ----------------------------------------------------------------------------------------
# libs
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# abstracts
# ----------------------------------------------------------------------------------------


class AddonPanel(bpy.types.Panel):
    bl_label = "Lightbox"
    bl_idname = "Arch_PT_lightbox_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Lightbox'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
#        row.label(text="Activate Lightbox", icon="SNAP_VERTEX")
        row.operator('view3d.focus_outliner')

        row = layout.row()
#       row.label(text="Activate Lightbox", icon="SNAP_VERTEX")
        row.operator('shader.toggle_clay_operator')


class View3D_OT_FocusOutliner(bpy.types.Operator):
    bl_idname = "view3d.focus_outliner"
    bl_label = "Focus Outliner on Selected"

    def execute(self,   context):
        # Get the active object
        obj = context.active_object

        if obj:
            # Get the Outliner area
            for area in bpy.context.screen.areas:
                if area.type == 'OUTLINER':
                    bpy.ops.outliner.show_active(area=area)
                    break

        return {'FINISHED'}


class Shader_OT_ToggleClay(bpy.types.Operator):
    bl_label = "Toggle Clay Material"
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


# ----------------------------------------------------------------------------------------
# register/unregister
# ----------------------------------------------------------------------------------------
addon_keymaps = []


def register():
    bpy.utils.register_class(AddonPanel)
    bpy.utils.register_class(Shader_OT_ToggleClay)
    bpy.utils.register_class(View3D_OT_FocusOutliner)

    bpy.types.Scene.clay_material_applied = bpy.props.BoolProperty(
        name="Clay Material Applied",
        description="Indicates if the clay material is applied",
        default=False
    )
    bpy.types.Scene.original_materials = bpy.props.PointerProperty(
        name="Original Materials",
        type=bpy.types.PropertyGroup
    )

    # Keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("view3d.focus_outliner",
                            'F', 'PRESS', ctrl=True, shift=True)
    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(AddonPanel)
    bpy.utils.unregister_class(Shader_OT_ToggleClay)
    del bpy.types.Scene.clay_material_applied
    del bpy.types.Scene.original_materials

    # Keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


# ----------------------------------------------------------------------------------------
# initialize
# ----------------------------------------------------------------------------------------
if __name__ == "__main__":
    register()
