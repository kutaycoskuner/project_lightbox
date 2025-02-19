
# ----------------------------------------------------------------------------------------
#               addon info
# ----------------------------------------------------------------------------------------
bl_info = {
    "name": "Lightbox",
    "description": "Various utility functions",
    "author": "Kutay Coskuner",
    "version": (0, 5, 2),  
    "blender": (4, 3, 2),
    "warning": "",
    "location": "View3D > Tool > Lightbox",
    "doc_url": "https://github.com/kutaycoskuner/project_lightbox/",  
    "tracker_url": "https://github.com/kutaycoskuner/project_lightbox/issues",
    "category": "Misc"
}


# ----------------------------------------------------------------------------------------
#               import core
# ----------------------------------------------------------------------------------------
if "lightbox" in globals():
    import importlib
    importlib.reload(globals()["lightbox"])
else:
    from . import core  
    globals()["lightbox"] = core


# ----------------------------------------------------------------------------------------
#               register unregister
# ----------------------------------------------------------------------------------------
def register():
    core.register()  


def unregister():
    core.unregister()  