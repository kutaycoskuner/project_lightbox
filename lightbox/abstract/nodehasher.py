import hashlib
import bpy

class NodeHasher:
    def __init__(self, node_tree: bpy.types.NodeTree):
        if not isinstance(node_tree, bpy.types.NodeTree):
            raise TypeError("expected bpy.types.NodeTree instance")

        self.node_tree = node_tree

        self._max_depth = 10
        self._link_cache_dict = None

        self._hash_cache = {}

        def _create_hash_obj(self) -> hashlib._hashlib.HASH:
            return hashlib.sha1()

    # def hash_input_sockets(self, node_tree: bpy.types.NodeTree):
    #     """
    #     Generate a hash for the given node's input sockets.
    #     The hash is based on the connected values or the default values of the inputs.
    #     """
    #     hasher = hashlib.sha256()

    #     # Iterate over the node's input sockets
    #     for socket in node.inputs:
    #         # If the socket is linked, get the linked socket's value
    #         if socket.is_linked:
    #             for link in socket.links:
    #                 from_socket = link.from_socket
    #                 hasher.update(str(from_socket.default_value).encode('utf-8'))
    #         else:
    #             # If the socket is not linked, get the default value
    #             hasher.update(str(socket.default_value).encode('utf-8'))

    #     # Return the hexadecimal digest of the hash
    #     return hasher.hexdigest()
