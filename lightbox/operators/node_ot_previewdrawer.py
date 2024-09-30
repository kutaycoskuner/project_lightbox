# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
#               imports
# ----------------------------------------------------------------------------------------


"""
NumPy (short for "Numerical Python") is a fundamental package for scientific computing in Python. It provides support for large, multi-dimensional arrays and matrices, along with a collection of mathematical functions to operate on these arrays efficiently.
"""
import numpy as np

import bpy
import bpy.utils.previews

from ..abstract.nodehasher import NodeHasher
import gpu
from gpu_extras.batch import batch_for_shader

# for defining specific primitive data type arrays instead of list
# import array

"""
The typing module provides support for type hints in Python. Type hints are a way to specify the expected data types of variables, function arguments, and return values. The typing module contains various tools and classes to express complex type relationships.
"""
# import typing



# ----------------------------------------------------------------------------------------
#               variables
# ----------------------------------------------------------------------------------------
instances = []


# ----------------------------------------------------------------------------------------
#               functions
# ----------------------------------------------------------------------------------------
def menu_func(self, context):
    self.layout.operator(Node_OT_PreviewDrawer.bl_idname)


# ----------------------------------------------------------------------------------------
#               register unregister
# ----------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------
#               abstracts
# ----------------------------------------------------------------------------------------
class Node_OT_PreviewDrawer(bpy.types.Operator):
    bl_idname = "node.draw_squares"
    bl_label = "Draw Squares on Nodes"
    # bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.tex_shader = None
        self.col_shader = None
        self.batch = None
        self.texture = None
        self.run_loop = True

        self.texture_extractor = NodeTextureExtractor()

        self._handle = None
        self._timer = None
        self._menu_button = None
        instances.append(self)

        self.node_data = []

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

    def check_space(self, context):
        if context.space_data.type != 'NODE_EDITOR':
            self.report({'WARNING'}, "Active space is not a Node Editor")
            return {'CANCELLED'}

    def invoke(self, context, event):
        self.check_space(context)
        # ____ step 1
        self.col_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        self.tex_shader = gpu.shader.from_builtin('IMAGE')
        # ____ step 2
        self.set_node_positions(context)
        # self.prepare_batch()

        if self._handle is None:
            self._handle = bpy.types.SpaceNodeEditor.draw_handler_add(
                self.draw_callback, (context,), 'WINDOW', 'POST_PIXEL'
            )

        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(
            0.1, window=context.window)

        return {'RUNNING_MODAL'}

    def set_node_positions(self, context):
        if context.space_data.type == 'NODE_EDITOR':
            self.node_data.clear()
            for node in context.space_data.node_tree.nodes:
                if node.location:
                    self.node_data.append({
                        'pos': (node.location.x, node.location.y),
                        'width': node.width,
                        'height': node.height,
                        'instance': node  # Add node instance to the dictionary
                    })

    def get_node_screen_positions(self, context):
        return self.node_data

    def prepare_batch(self):
        self.batch_for_draw_at_position()

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

    def get_zoom_factors(self, view2d, region):
        """Calculate zoom factors based on view2d and region."""
        # Convert region size into view2d rectangle (absolute).
        x1, y1 = view2d.region_to_view(0, 0)
        x2, y2 = view2d.region_to_view(region.width, region.height)

        # Convert to view2d size.
        v2d_width = x2 - x1
        v2d_height = y2 - y1

        # Convert to scale.
        v2d_scale_x = region.width / v2d_width
        v2d_scale_y = region.height / v2d_height

        return v2d_scale_x, v2d_scale_y

    def adjust_position_for_zoom(self, screen_pos, node_width, square_size, zoom_factors):
        """Adjust position based on zoom and node width."""
        y_margin = 80.0

        # Calculate the adjusted position
        adjusted_x = screen_pos[0] + node_width / 2 - square_size / 2
        adjusted_y = screen_pos[1] - square_size / 2 + y_margin
        return adjusted_x, adjusted_y

    # def get_texture_from_node(self, node):
    #     # print(f"Node type: {node}")
    #     if isinstance(node, bpy.types.ShaderNodeTexImage):
    #         if node.image is None:
    #             print("No image assigned to the ShaderNodeTexImage node.")
    #             return None
    #         if not node.image.gl_load():
    #             print("Failed to load image into OpenGL.")
    #             return None
    #         return node.image.bindcode
    #     return None
    # test -------------------------------------------------------------------------------

    def get_texture_from_node(self, node):
        """
        Retrieve the texture bindcode from a shader node if available.
        """
        if isinstance(node, bpy.types.ShaderNode):
            for output in node.outputs:
                print(output.type)
            # return
            if node.image is None:
                print("No image assigned to the ShaderNodeTexImage node.")
                return None
            try:
                node.image.gl_load()
                return node.image.bindcode
            except RuntimeError:
                print("Failed to load image into OpenGL.")
                return None

        if hasattr(node, 'inputs'):
            for input in node.inputs:
                if input.is_linked:
                    for link in input.links:
                        texture_node = link.from_node
                        if isinstance(texture_node, bpy.types.ShaderNodeTexImage):
                            return self.get_texture_from_node(texture_node)

        return None

    # test -------------------------------------------------------------------------------
    def draw_callback(self, context):
        try:
            region = context.region
            view2d = region.view2d
            self.set_node_positions(context)

            # Define base size for the squares and margin
            base_square_size = 100.0
            y_margin = 80.0

            # Calculate zoom factors
            zoom_factors = self.get_zoom_factors(view2d, region)
            zoom_factor_x, zoom_factor_y = zoom_factors
            zoom_factor = (zoom_factor_x + zoom_factor_y) / 2

            # Correct zoom factor calculation for scaling
            for node in self.node_data:
                pos = node['pos']
                width = node['width']

                # Convert node world position to screen position (bottom-left corner)
                screen_pos = view2d.view_to_region(pos[0], pos[1], clip=False)
                square_size = base_square_size * zoom_factor  # Corrected scaling

                adjusted_screen_pos = (
                    # Centering on X, no zoom scaling
                    screen_pos[0] - (square_size / 2) + \
                    ((width * zoom_factor) / 2),
                    # Centering on Y and applying margin
                    screen_pos[1] - (square_size / 2) + \
                    (y_margin * zoom_factor)
                )

                texture = self.texture_extractor.render_node_to_texture(
                    node['instance'])
                # texture = self.get_texture_from_node(node['instance'])
                print("Node dictionary content:", texture)
                if texture:
                    self.tex_shader.bind()

                    # gpu.texture.bind(texture)
                    # gpu.texture.bind(texture.bindcode)
                    self.tex_shader.uniform_sampler("image", texture)

                    # self.draw_textured_rectangle((100, 100), 200)
                    self.draw_textured_rectangle(
                        adjusted_screen_pos, square_size)
                else:
                    self.col_shader.bind()
                    self.col_shader.uniform_float(
                        "color", (1.0, 1.0, 1.0, 1.0))  # White color
                    self.draw_solid_rectangle(adjusted_screen_pos, square_size)

            self.run_loop = False
        except ReferenceError:
            self.cancel(context)

    def draw_textured_rectangle(self, screen_pos, square_size):
        vertices = [
            (screen_pos[0], screen_pos[1]),  # Bottom-left corner
            # Bottom-right corner
            (screen_pos[0] + square_size, screen_pos[1]),
            (screen_pos[0] + square_size, screen_pos[1] + \
                square_size),  # Top-right corner
            (screen_pos[0], screen_pos[1] + square_size)  # Top-left corner
        ]

        # Define corresponding texture coordinates for each vertex
        tex_coords = [
            (0.0, 0.0),  # Bottom-left
            (1.0, 0.0),  # Bottom-right
            (1.0, 1.0),  # Top-right
            (0.0, 1.0)   # Top-left
        ]

        indices = [(0, 1, 2), (2, 3, 0)]

        # Create the batch including positions and texture coordinates
        batch = batch_for_shader(
            self.tex_shader, 'TRIS',
            {"pos": vertices, "texCoord": tex_coords}, indices=indices
        )
        batch.draw(self.tex_shader)

    # def draw_textured_rectangle(self, screen_pos, square_size):
    #     vertices = [
    #         (screen_pos[0],                 screen_pos[1]),
    #         (screen_pos[0] + square_size,   screen_pos[1]),
    #         (screen_pos[0] + square_size,   screen_pos[1] + square_size),
    #         (screen_pos[0],                 screen_pos[1] + square_size)
    #     ]

    #     indices = [(0, 1, 2), (2, 3, 0)]
    #     batch = batch_for_shader(
    #         self.tex_shader, 'TRIS', {"pos": vertices}, indices=indices)
    #     batch.draw(self.tex_shader)

    def draw_solid_rectangle(self, screen_pos, square_size):
        vertices = [
            (screen_pos[0],                 screen_pos[1]),
            (screen_pos[0] + square_size,   screen_pos[1]),
            (screen_pos[0] + square_size,   screen_pos[1] + square_size),
            (screen_pos[0],                 screen_pos[1] + square_size)
        ]

        indices = [(0, 1, 2), (2, 3, 0)]
        batch = batch_for_shader(
            self.col_shader, 'TRIS', {"pos": vertices}, indices=indices)
        batch.draw(self.col_shader)

    def modal(self, context, event):
        if not self.run_loop and event.type in {'ESC'} or context.area is None:
            self.cancel(context)
            return {'CANCELLED'}
        self.check_space(context)
        context.area.tag_redraw()
        return {'PASS_THROUGH'}

    def draw_square(self, shader, screen_pos, square_size):
        """Draw a square at the specified screen position with the given size."""
        vertices = [
            (screen_pos[0],                 screen_pos[1]),
            (screen_pos[0] + square_size,   screen_pos[1]),
            (screen_pos[0] + square_size, screen_pos[1] + square_size),
            (screen_pos[0], screen_pos[1] + square_size)
        ]

        indices = [(0, 1, 2), (2, 3, 0)]
        batch = batch_for_shader(
            shader, 'TRIS', {"pos": vertices}, indices=indices)
        batch.draw(shader)

    def cancel(self, context):
        self.run_loop = False
        self.cleanup()
        context.area.tag_redraw()

    @ staticmethod
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
        self.shader = None
        self.batch = None
        self.node_data = []


classes = (Node_OT_PreviewDrawer, )


# ----------------------------------------------------------------------------------------
#               helper classes
# ----------------------------------------------------------------------------------------

class NodeTextureExtractor:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        self.bake_image = None
        self.offscreen = gpu.types.GPUOffScreen(self.width, self.height)
        self.test_image = None  # Add this to store the test image

        self.load_test_image()

    def load_test_image(self):

        image_path = (
            "C:\\Users\\kutay\\OneDrive\\Documents\\GitHub\\project_lightbox\\lightbox"
            "\\_data\\textures\\test_texture01.jpg"
            )  # Update this path
        try:
            self.test_image = bpy.data.images.load(image_path)
        except Exception as e:
            print(f"Failed to load test image: {e}")
            self.test_image = None

    def render_node_to_texture(self, node):
        """Render the output of the given node to a texture using baking."""
        # Ensure the current object is selected and active for baking
        if not bpy.context.object or bpy.context.object.type != 'MESH':
            print("No active mesh object to bake.")
            return None

        # Create a temporary material
        temp_material = bpy.data.materials.new(name="TempMaterial")
        temp_material.use_nodes = True
        node_tree = temp_material.node_tree

        # Find an appropriate output socket
        output_socket = None
        if isinstance(node, bpy.types.ShaderNode):
            for output in node.outputs:
                if output.type in {'RGBA', 'VECTOR', 'VALUE'}:
                    output_socket = output
                    break

        if not output_socket:
            print("No valid output socket found for the node.")
            bpy.data.materials.remove(temp_material)
            return None

        # Create a temporary node and copy properties
        temp_node = node_tree.nodes.new(type=node.bl_idname)
        for prop in node.bl_rna.properties:
            if not prop.is_readonly:
                setattr(temp_node, prop.identifier,
                        getattr(node, prop.identifier))

        output_node = node_tree.nodes.new('ShaderNodeOutputMaterial')
        node_tree.links.new(temp_node.outputs[0], output_node.inputs[0])

        # Assign the temporary material to the active object
        active_object = bpy.context.object
        active_object.active_material = temp_material

        # Create an image for baking
        self.bake_image = bpy.data.images.new("BakeImage", width=self.width, height=self.height)

        # Create a new texture node in the node tree to hold the baked texture
        tex_image_node = node_tree.nodes.new('ShaderNodeTexImage')
        tex_image_node.image = self.bake_image

        # Connect the node output to the texture for baking
        node_tree.links.new(tex_image_node.outputs[0], output_node.inputs[0])

        # Set up the bake settings
        bpy.context.scene.cycles.bake_type = 'COMBINED'  # You can set bake type based on your needs

        # Bake the image
        bpy.ops.object.bake(image=self.bake_image)

        # Unlink and cleanup
        bpy.data.materials.remove(temp_material)

        return self.bake_image

    # def render_node_to_texture(self, node):
    #     """Render the output of the given node to a texture."""
    #     # Create a temporary material
    #     temp_material = bpy.data.materials.new(name="TempMaterial")
    #     temp_material.use_nodes = True
    #     node_tree = temp_material.node_tree

    #     # Find an appropriate output socket
    #     output_socket = None
    #     if isinstance(node, bpy.types.ShaderNode):
    #         if hasattr(node, 'outputs'):
    #             for output in node.outputs:
    #                 if output.type in {'RGBA', 'VECTOR', 'VALUE'}:
    #                     output_socket = output
    #                     break

    #     if not output_socket:
    #         print("No valid output socket found for the node.")
    #         bpy.data.materials.remove(temp_material)
    #         return None

    #     # Create a temporary node and copy properties
    #     temp_node = node_tree.nodes.new(type=node.bl_idname)
    #     for prop in node.bl_rna.properties:
    #         if not prop.is_readonly:
    #             setattr(temp_node, prop.identifier,
    #                     getattr(node, prop.identifier))

    #     output_node = node_tree.nodes.new('ShaderNodeOutputMaterial')
    #     node_tree.links.new(temp_node.outputs[0], output_node.inputs[0])

    #     # Render the node output to a texture
    #     with self.offscreen.bind():
    #         # Set up GPU state
    #         gpu.state.blend_set('ALPHA')
    #         gpu.state.depth_test_set('NONE')
    #         gpu.state.face_culling_set('NONE')
            
            

    #         print(output_socket)
    #         print(dir(output_socket))
    #         return
    #         # Clear the offscreen buffer
    #         # gpu.state.clear_color(1.0, 1.0, 1.0, 1.0)
    #         # gpu.state.clear()

    #         # Draw the scene or material to the offscreen buffer
    #         # Note: Actual drawing code is needed here
            
    #         # test testing
    #         # Bind and draw the test image
    #         # self.test_image.gl_load()  # Load the image into OpenGL
    #         # texture = gpu.texture.from_image(self.test_image)

    #         # return texture
    #         # test testing end

    #         # Get the texture data from the color buffer
    #         color_texture = self.offscreen.color_texture
    #         buffer = np.frombuffer(color_texture.read(), dtype=np.float32).reshape((self.height, self.width, 4))


    #         # # Read pixels from the offscreen buffer
    #         # buffer = np.frombuffer(gpu.texture.from_image(
    #         #     color_texture), dtype=np.float32).reshape((self.height, self.width, 4))
    #         # pixels = np.array(color_texture.read_pixels(), dtype=np.float32)

    #         # Create an image from the pixels
    #         image = bpy.data.images.new(
    #             "TempImage", width=self.width, height=self.height)
    #         image.pixels = pixels.flatten().tolist()
    #         image.update()

    #     # Clean up
    #     bpy.data.materials.remove(temp_material)

    #     print('Image created:', type(image), image)
    #     return image

    def free(self):
        self.offscreen.free()
