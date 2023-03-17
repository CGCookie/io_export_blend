import bpy

def get_default_path():
    asset_libraries = bpy.context.preferences.filepaths.asset_libraries
    if asset_libraries and asset_libraries[0].path:
        return asset_libraries[0].path
    else:
        return "//assets/"

def mode_toggle(context, switch_to):
    prev_mode = context.mode
    switch = {
        'EDIT_MESH': bpy.ops.object.editmode_toggle,
        'SCULPT': bpy.ops.sculpt.sculptmode_toggle,
        'PAINT_VERTEX': bpy.ops.paint.vertex_paint_toggle,
        'PAINT_WEIGHT': bpy.ops.paint.weight_paint_toggle,
        'PAINT_TEXTURE': bpy.ops.paint.texture_paint_toggle
    }
    if prev_mode != 'OBJECT':
        switch[prev_mode]()
    elif switch_to != 'OBJECT':
        switch[switch_to]()
    return prev_mode