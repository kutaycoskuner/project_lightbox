import bpy


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


class View3D_OT_FocusOutliner(bpy.types.Operator):
    bl_idname           = "view3d.focus_outliner"
    bl_description      = "Focuses selected object on the outliner. Useful for complex scenes."
    bl_label            = "Focus Selected on Outliner"

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
    )
