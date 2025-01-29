
# ----------------------------------------------------------------------------------------
#               addon info
# ----------------------------------------------------------------------------------------
bl_info = {
    "name": "Lightbox",
    "description": "Various utility functionalities",
    "author": "Kutay Coskuner",
    "version": (0, 2, 1),  
    "blender": (4, 3, 2),
    "location": "View3D > Tool > Lightbox",
    "warning": "",
    "wiki_url": "https://example.com/docs",  
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