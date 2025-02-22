import bpy

# Define the operator
class OT_ToggleSidebarTab(bpy.types.Operator):
    """Toggle Sidebar and switch between Item and Addon tabs"""
    bl_idname = "view3d.toggle_sidebar_tab"
    bl_label = "Toggle Sidebar Tab"

    def execute(self, context):
        toggle_sidebar_tab()
        return {'FINISHED'}

def toggle_sidebar_tab():
    """Toggles the Sidebar and switches between 'Item' and addon's tab."""
    areas = bpy.context.screen.areas
    area = [a for a in areas if a.type == 'VIEW_3D'][0]

    with bpy.context.temp_override(area=area):
        sidebar_tab = area.regions[5].active_panel_category
        area.regions[5].active_panel_category = 'Lightbox'
        # if sidebar_tab != 'Lightbox':
        #     area.regions[5].active_panel_category = 'Lightbox'
        # elif len(bpy.context.selected_objects) > 0: 
        #     area.regions[5].active_panel_category = 'Item'

        # bpy.context.object.hide_render = bpy.context.object.hide_render

def register():
    bpy.utils.register_class(OT_ToggleSidebarTab)

def unregister():
    bpy.utils.unregister_class(OT_ToggleSidebarTab)

classes = (OT_ToggleSidebarTab,)

if __name__ == "__main__":
    register()