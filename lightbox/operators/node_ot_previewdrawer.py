import bpy
import gpu
# import mathutils
from gpu_extras.batch import batch_for_shader

instances = []


def menu_func(self, context):
    self.layout.operator(Node_OT_PreviewDrawer.bl_idname)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        cls.access_start()
    # bpy.types.NODE_MT_context_menu.append(menu_func)


def unregister():
    for cls in reversed(classes):
        cls.access_cleanup()
        bpy.utils.unregister_class(cls)
    # bpy.types.NODE_MT_context_menu.remove(menu_func)


class Node_OT_PreviewDrawer(bpy.types.Operator):
    bl_idname = "node.draw_squares"
    bl_label = "Draw Squares on Nodes"
    # bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.shader = None
        self.batch = None

        self._handle = None
        self._timer = None
        self._menu_button = None
        instances.append(self)

        # self.node_positions = []

    @staticmethod
    def access_start():
        for instance in instances:
            instance.init_menu_option()

    def init_menu_option(self):
        if self._menu_button is None:
            bpy.types.NODE_MT_context_menu.append(menu_func)
            self._menu_button = True

    def execute(self, context):
        self.invoke(context, None)
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.space_data.type != 'NODE_EDITOR':
            self.report({'WARNING'}, "Active space is not a Node Editor")
            return {'CANCELLED'}

        self.shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        # self.set_node_positions(context)
        self.prepare_batch()

        if self._handle is None:
            self._handle = bpy.types.SpaceNodeEditor.draw_handler_add(
                self.draw_callback, (context,), 'WINDOW', 'POST_PIXEL'
            )

        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(
            0.1, window=context.window)

        return {'RUNNING_MODAL'}

    # def set_node_positions(self, context):
    #     if context.space_data.type != 'NODE_EDITOR':
    #         for node in context.space_data.node_tree.nodes:
    #             if node.location:
    #                 self.node_positions.append(node.location.xy)

    # def get_node_screen_positions(self, context):
    #     return self.node_positions

    def prepare_batch(self):
        self.batch_for_test()

    def batch_for_test(self):
        vertices = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
        indices = [(0, 1, 2), (2, 3, 0)]
        self.batch = batch_for_shader(
            self.shader, 'TRIS', {"pos": vertices}, indices=indices)

    def batch_for_draw_at_position(self, position):
        size = 10.0  # Size of the square
        vertices = [
            (position[0] - size, position[1] - size),
            (position[0] + size, position[1] - size),
            (position[0] + size, position[1] + size),
            (position[0] - size, position[1] + size),
        ]
        indices = [(0, 1, 2), (2, 3, 0)]
        return batch_for_shader(
            self.shader, 'TRIS', {"pos": vertices}, indices=indices)

    def draw_callback(self, context):
        try:
            self.shader.bind()
            self.shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
            self.batch.draw(self.shader)
            # screen_positions = self.node_positions
            # for pos in screen_positions:
            #     self.batch_for_draw_at_position(pos).draw(self.shader)

        except ReferenceError:
            self.cancel(context)

    def modal(self, context, event):
        if event.type in {'ESC'} or context.area is None:
            self.cancel(context)
            return {'CANCELLED'}
        context.area.tag_redraw()
        return {'PASS_THROUGH'}

    def cancel(self, context):
        self.cleanup()
        context.area.tag_redraw()

    @staticmethod
    def access_cleanup():
        for instance in instances:
            instance.cleanup()
        instances.clear()

    def cleanup(self):
        if self._handle is not None:
            bpy.types.SpaceNodeEditor.draw_handler_remove(
                self._handle, 'WINDOW')
            self._handle = None
        if self._timer is not None:
            bpy.context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if self._menu_button is not None:
            bpy.types.NODE_MT_context_menu.remove(menu_func)
            self._menu_button = None
        if self.shader is not None:
            self.shader = None
        if self.batch is not None:
            self.batch = None
        # if self.node_positions is not None:
        #     self.node_positions = None


classes = (
    Node_OT_PreviewDrawer,
    )
