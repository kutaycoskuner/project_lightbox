import bpy

def register():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    for data in key_tuples:
        kmi = km.keymap_items.new(
            data[0], data[1], 'PRESS',
            ctrl=data[2], shift=data[3], alt=data[4]
            )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


addon_keymaps = []


key_tuples = (
#    id,                            key,    ctrl,   shift,  alt
    ('view3d.focus_outliner',       'W',    False,  True,   True),
    ('object.ground_object',     'S',    False,  True,   True),
    # ('node.draw_squares',           'S',    False,  True,   True),
)
