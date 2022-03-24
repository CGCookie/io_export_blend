# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Export .blend",
    "author": "Jason van Gumster (Fweeb)",
    "version": (1, 1),
    "blender": (2, 83, 0),
    "location": "File > Export > Blender (.blend)/Outliner > Context Menu > Export to .blend",
    "description": "Exports all or some datablocks to a separate .blend file",
    "warning": "",
    "doc_url": "https://github.com/CGCookie/io_export_blend",
    "tracker_url": "https://github.com/CGCookie/io_export_blend/issues",
    "category": "Import-Export",
}


import bpy


# Local imports
from .exporters import ExportBlenderObjects, ExportBlenderCollection, ExportBlenderNodes


# UI
def menu_func_export(self, context):
    if self.bl_label == "Export":
        self.layout.operator(ExportBlenderObjects.bl_idname, text="Blender (.blend)")
    elif self.bl_label == "Collection":
        if len(context.selected_ids) == 1 and isinstance(context.selected_ids[0], bpy.types.Collection):
            self.layout.operator_context = "INVOKE_DEFAULT"
            self.layout.operator(ExportBlenderCollection.bl_idname, text="Export to .blend")
    elif self.bl_label == "Object":
        self.layout.operator_context = "INVOKE_DEFAULT"
        self.layout.operator(ExportBlenderObjects.bl_idname, text="Export to .blend")


def menu_func_export_nodes(self, context):
    self.layout.operator_context = "INVOKE_DEFAULT"
    #XXX Disabling for Compositor nodes until bugfix for T88402
    if context.active_node.id_data.type != 'COMPOSITING':
        op = self.layout.operator(ExportBlenderNodes.bl_idname, text="Export to .blend")
    #if context.active_node.id_data.type == 'COMPOSITING':
    #    op.is_compositor = True


def register():
    bpy.utils.register_class(ExportBlenderObjects)
    bpy.utils.register_class(ExportBlenderCollection)
    bpy.utils.register_class(ExportBlenderNodes)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.OUTLINER_MT_object.append(menu_func_export)
    bpy.types.OUTLINER_MT_collection.append(menu_func_export)
    bpy.types.NODE_MT_node.append(menu_func_export_nodes)


def unregister():
    bpy.utils.unregister_class(ExportBlenderObjects)
    bpy.utils.unregister_class(ExportBlenderCollection)
    bpy.utils.unregister_class(ExportBlenderNodes)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.OUTLINER_MT_object.remove(menu_func_export)
    bpy.types.OUTLINER_MT_collection.remove(menu_func_export)
    bpy.types.NODE_MT_node.remove(menu_func_export_nodes)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_scene.blend('INVOKE_DEFAULT')
