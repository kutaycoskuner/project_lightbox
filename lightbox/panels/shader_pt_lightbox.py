import bpy


# Define the Boolean property
bpy.types.Scene.my_checkbox = bpy.props.BoolProperty(
    name="Enable Node Previews",
    description="Enabling small previews on each node",
    default=False
)


class Shader_PT_Lightbox(bpy.types.Panel):
    bl_label = "Lightbox"
    bl_idname = "SHADER_PT_lightbox_panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = 'Lightbox'

    def draw(self, context):
        layout = self.layout
        layout.operator("node.draw_squares")
        # scene = context.scene

        row = layout.row()
        row.label(text='Control: Preview Size')

        row = layout.row()
        row.label(text='Control: y margin')

        row = layout.row()
        row.label(text='Control: preview border radius')
        # row.prop(scene, "my_checkbox")


classes = (
    Shader_PT_Lightbox,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
