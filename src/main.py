# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
#               libs
# ----------------------------------------------------------------------------------------
import bpy
import importlib
import sys
import os
import re

# ----------------------------------------------------------------------------------------
#               info
# ----------------------------------------------------------------------------------------
bl_info = {
    "name": "Lightbox",
    "description": "Various utility functionalities",
    "author": "lichzelg",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Tool",
    "warning": "",
    "wiki_url": "",
    "category": "Material"
}

# ----------------------------------------------------------------------------------------
#               variables
# ----------------------------------------------------------------------------------------
is_devmode    = True
is_registered = False  # Add a flag to track if the addon is registered
is_timereload = False 

addon_keymaps = []

# ----- file paths -----
addon_filepath = os.path.realpath(__file__)
addon_filepath = re.sub(r'[^\\]+\.blend\\', '', addon_filepath)
script_filename = os.path.basename(__file__).split('.')[0]

last_modified_time = None
if addon_filepath and os.path.exists(addon_filepath):
    last_modified_time = os.path.getmtime(addon_filepath)

# ----------------------------------------------------------------------------------------
#               functions
# ----------------------------------------------------------------------------------------
def reload_addon():
    global is_registered
    addon_name = os.path.basename(__file__).split('.')[0]
    print('reloading..')  
    if addon_name in sys.modules:  
        unregister()
        importlib.reload(sys.modules[addon_name]) 
        reload_addon_script() 
    else:
        unregister()
        importlib.import_module(addon_name) 
        reload_addon_script() 


def check_for_updates():
    global last_modified_time
    current_modified_time = os.path.getmtime(addon_filepath)
    if current_modified_time != last_modified_time:
        last_modified_time = current_modified_time
        print(f"{addon_filepath} has been modified, reloading addon...") 
        reload_addon() 
    return 1.0  # Check every 1 second


def get_text_editor_area():
    for screen in bpy.data.screens:
        for area in screen.areas: 
            if area.type == "TEXT_EDITOR":
                return area


def reload_addon_script():
    area = get_text_editor_area()
    if area: 
        with bpy.context.temp_override(area=area):
            for t in bpy.data.texts:
                if t.is_modified and not t.is_in_memory:
                    context_override = {}
                    context_override["edit_text"] = bpy.data.texts["main.py"]
                    with bpy.context.temp_override(**context_override):
                        bpy.ops.text.resolve_conflict(resolution='RELOAD')
                        bpy.ops.text.run_script() 
                    break


def register():
    global is_registered, last_modified_time, addon_filepath
    if not is_registered:
        # ----- addon modules -----
        bpy.utils.register_class(Object_OT_ReloadAndRun)
        bpy.utils.register_class(AddonPanel)
        bpy.utils.register_class(Shader_OT_ToggleClay)
        # Register other classes here
        bpy.utils.register_class(View3D_OT_FocusOutliner)

        # ----- keymap -----
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new(Object_OT_ReloadAndRun.bl_idname, 'W', 'PRESS', ctrl=False, shift=True, alt=True)
        addon_keymaps.append((km, kmi))

        # ----- register state -----
        is_registered = True  # Set the flag to true
        
        # ----- addon reloading -----
        if is_devmode: 
            if is_timereload:
                bpy.app.timers.register(check_for_updates)
            addon_filepath = os.path.realpath(__file__)
            addon_filepath = re.sub(r'[^\\]+\.blend\\', '', addon_filepath)
            last_modified_time = os.path.getmtime(addon_filepath)
            print('lightbox is running in development mode.')

def unregister(): 
    global is_registered
    if is_registered:
        # ----- addon modules -----
        bpy.utils.unregister_class(Object_OT_ReloadAndRun)
        bpy.utils.unregister_class(AddonPanel)
        bpy.utils.unregister_class(Shader_OT_ToggleClay)
        # Unregister other classes here
        bpy.utils.unregister_class(View3D_OT_FocusOutliner)
        
        # ----- keymap -----
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()
        
        # ----- register state -----
        is_registered = False  # Set the flag to false
        
        # ----- addon reloading -----  
        if is_devmode: 
            if is_timereload:
                bpy.app.timers.unregister(check_for_updates)


# ----------------------------------------------------------------------------------------
#               abstracts
# ----------------------------------------------------------------------------------------
class Object_OT_ReloadAndRun(bpy.types.Operator):
    bl_idname = "object.reload_and_run"
    bl_label = "Reload and Run Addon"

    def execute(self, context):
        reload_addon()
        return {'FINISHED'}


class AddonPanel(bpy.types.Panel):
    bl_label = "Lightbox"
    bl_idname = "ARCH_PT_lightbox_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Lightbox'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        # row.label(text="Activate Lightbox", icon="SNAP_VERTEX")
        row.operator('shader.toggle_clay_operator')
        
        row = layout.row() 
        # row.label(text="Activate Lightbox a ", icon="SNAP_VERTEX")
        row.operator('view3d.focus_outliner') 


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


class View3D_OT_FocusOutliner(bpy.types.Operator):
    bl_idname = "view3d.focus_outliner"
    bl_label = "Focus Outliner on Selected"

    def execute(self, context):
        # Get the active object
        obj = context.active_object

        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        print(obj) 
        #                 # override = {'area': area, 'region': region}
        #                 bpy.ops.outliner.show_active()
                        break

        # with bpy.context.temp_override(area=bpy.context.area):

        return {'FINISHED'}

# ----------------------------------------------------------------------------------------
#               initialize
# ----------------------------------------------------------------------------------------
if __name__ == "__main__":
    register() 
