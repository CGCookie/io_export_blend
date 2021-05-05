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
    "version": (0, 9),
    "blender": (2, 83, 0),
    "location": "File > Export > Blender (.blend)/Outliner > Context Menu > Export to .blend",
    "description": "Exports all or some datablocks to a separate .blend file",
    "warning": "",
    "doc_url": "https://github.com/CGCookie/io_export_blend",
    "tracker_url": "https://github.com/CGCookie/io_export_blend/issues",
    "category": "Import-Export",
}


import bpy


def actually_export(export_scene, filepath):
    # Remove all other scenes
    for scn in bpy.data.scenes:
        if scn != export_scene:
            bpy.data.scenes.remove(scn)

    # Save data to desired path
    bpy.ops.wm.save_as_mainfile(filepath=filepath, copy=True)
    
    # Undo the scene deletion stuff
    #XXX Yes, this *is* a kind of kludgey way to put everything back... but it works!
    bpy.ops.ed.undo_push()
    bpy.ops.ed.undo()


def export_blend_objects(context, export_settings):
    print("Exporting objects to .blend...") 
    objects = []
    object_names = []
    if export_settings["export_selected"]:
        for ob in context.selected_objects:
            objects.append(ob)
            object_names.append(ob.name)
    elif export_settings["is_collection"]:
        for ob in bpy.data.collections[export_settings["collection_name"]].objects:
            objects.append(ob)
            object_names.append(ob.name)
    else:
        for ob in bpy.data.objects:
            objects.append(ob)
            object_names.append(ob.name)

    # Create a new empty scene to hold export objects
    export_scene = bpy.data.scenes.new("blend_export")

    # Create a collection if we're exporting the selection as one    
    if export_settings["export_selected"] and export_settings["export_as_collection"]:
        if export_settings["is_collection"] == False:
            export_collection = bpy.data.collections.new(export_settings["collection_name"])
        else:
            export_collection = bpy.data.collections[export_settings["collection_name"]]
        export_scene.collection.children.link(export_collection)

    # Add objects from list to scene
    for ob in objects:
        export_scene.collection.objects.link(ob)
        if export_settings["export_selected"]:
            if export_settings["export_as_collection"] and export_settings["is_collection"] == False:
                export_collection.objects.link(ob)
            elif export_settings["export_as_collection"] == False and export_settings["mark_asset"]:
                ob.asset_mark()

    # If exporting as a collection and marking as an asset, only mark the collection as an asset
    if export_settings["export_selected"] and export_settings["export_as_collection"] and export_settings["mark_asset"]:
        export_collection.asset_mark()

    actually_export(export_scene, export_settings["filepath"])
    
    # If backlinks are activated, replace each object with a link to the exported one
    if export_settings["export_selected"] and export_settings["backlink"]:
        if export_settings["export_as_collection"]:
            linkpath = export_settings["filepath"] + "\\Collection\\" + export_settings["collection_name"]
            linkdir = export_settings["filepath"] + "\\Collection\\"
            linkcol = export_settings["collection_name"]
            for obname in object_names:
                bpy.data.objects.remove(bpy.data.objects[obname], do_unlink=True)
            bpy.ops.wm.link(
                filepath=linkpath,
                directory=linkdir,
                filename = linkcol
            )
        else:
            for obname in object_names:
                linkpath = export_settings["filepath"] + "\\Object\\" + obname
                linkdir = export_settings["filepath"] + "\\Object\\"
                linkob = obname
                bpy.data.objects.remove(bpy.data.objects[obname], do_unlink=True)
                bpy.ops.wm.link(
                    filepath=linkpath,
                    directory=linkdir,
                    filename = linkob
                )

    return {'FINISHED'}


def export_blend_nodes(context, export_settings):
    print("Exporting nodes to .blend...")
    current_nodetree = context.active_node.id_data
    nodes = []
    if export_settings["export_selected"]:
        for node in current_nodetree.nodes:#context.selected_nodes:
            if not node.select:
                current_nodetree.nodes.remove(node)

    # Create a new empty scene to hold export objects
    export_scene = bpy.data.scenes.new("blend_export")
    
    # Set the current node tree to have a fake user
    current_nodetree.use_fake_user = True

    actually_export(export_scene, export_settings["filepath"])

    return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportBlenderObjects(Operator, ExportHelper):
    """Export some or all of your Blender scene to a .blend file"""
    bl_idname = "export_scene.blend"  
    bl_label = "Export Blender"

    filename_ext = ".blend"

    filter_glob: StringProperty(
        default="*.blend",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # Operator properties
    export_selected: BoolProperty(
        name="Export Selected",
        description="Export selected objects to .blend file",
        default=True
    )

    export_as_collection: BoolProperty(
        name="Export as Collection",
        description="Bundle selected objects in a collection before exporting",
        default=False
    )

    collection_name: StringProperty(
        name="Collection Name",
        description="Name of exported collection",
        default="export_collection"
    )

    if bpy.app.version >= (2, 93, 0):
        mark_asset: BoolProperty(
            name="Mark as Asset",
            description="Mark selected objects as assets for visibility in the Asset Browser",
            default=False
        )

    backlink: BoolProperty(
        name="Backlink",
        description="Replace selection with a link to the exported object",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        
        col.prop(self, "export_selected")
        if self.export_selected:
            box = col.box()
            box.prop(self, "export_as_collection")
            if self.export_as_collection:
                box.prop(self, "collection_name", icon="COLLECTION_NEW", icon_only=True)
            if bpy.app.version >= (2, 93, 0):
                box.prop(self, "mark_asset")
            box.prop(self, "backlink")

    def execute(self, context):
        export_settings = {
            "is_collection": False,
            "filepath": self.filepath,
            "export_selected": self.export_selected,
            "export_as_collection": self.export_as_collection,
            "collection_name": self.collection_name,
            "backlink": self.backlink
        }
        if bpy.app.version >= (2, 93, 0):
            export_settings["mark_asset"] = self.mark_asset
        else:
            export_settings["mark_asset"] = False

        return export_blend_objects(context, export_settings)


class ExportBlenderCollection(Operator, ExportHelper):
    """Export a selected collection to a separate .blend file"""
    bl_idname = "export_collection.blend"  
    bl_label = "Export Blender Collection"

    filename_ext = ".blend"

    filter_glob: StringProperty(
        default="*.blend",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # Operator properties
    if bpy.app.version >= (2, 93, 0):
        mark_asset: BoolProperty(
            name="Mark as Asset",
            description="Mark selected collection as an asset for visibility in the Asset Browser",
            default=False
        )

    def execute(self, context):
        export_settings = {
            "is_collection": True,
            "filepath": self.filepath,
            "export_selected": True,
            "export_as_collection": True,
            "collection_name": context.selected_ids[0].name, #XXX Assumes only one collection is selected
            "backlink": False
        }
        if bpy.app.version >= (2, 93, 0):
            export_settings["mark_asset"] = self.mark_asset
        else:
            export_settings["mark_asset"] = False

        return export_blend_objects(context, export_settings)


class ExportBlenderNodes(Operator, ExportHelper):
    """Export selected nodes to a separate .blend file"""
    bl_idname = "export_nodes.blend"
    bl_label = "Export Blender Nodes"

    filename_ext = ".blend"

    filter_glob: StringProperty(
        default="*.blend",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # Operator properties
    export_selected: BoolProperty(
        name="Export Selected",
        description="Export selected nodes to .blend file. Otherwise, export the active node tree.",
        default=True
    )

    def execute(self, context):
        export_settings = {
            "filepath": self.filepath,
            "export_selected": self.export_selected
        }
        return export_blend_nodes(context, export_settings)


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
    self.layout.operator(ExportBlenderNodes.bl_idname, text="Export to .blend")


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
    bpy.utils.ynregister_class(ExportBlenderNodes)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.OUTLINER_MT_object.remove(menu_func_export)
    bpy.types.OUTLINER_MT_collection.remove(menu_func_export)
    bpy.types.NODE_MT_node.remove(menu_func_export_nodes)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_scene.blend('INVOKE_DEFAULT')
