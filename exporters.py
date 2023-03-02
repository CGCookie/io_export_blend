'''
Copyright (C) 2021-2022 Orange Turbine
https://orangeturbine.com
orangeturbine@cgcookie.com

Created by Jason van Gumster

    This file is part of Export to .blend.

    Export to .blend is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org/licenses/>.

'''


import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

# Local imports
from .functions import export_blend_objects, export_blend_nodes
from .utilities import mode_toggle


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

    directory: StringProperty(
        default="//"
    )

    filename: StringProperty(
        default=""
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

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' # Because funky things happen when not in Object Mode

    def invoke(self, context, event):
        preferences = context.preferences.addons[__package__].preferences
        self.directory = preferences.filepath
        self.filename = context.active_object.name
        self.export_as_collection = preferences.export_as_collection
        self.backlink = preferences.backlink
        self.collection_name = context.active_object.name
        if bpy.app.version > (2, 93, 0):
            self.mark_asset = preferences.mark_asset
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "export_selected")
        if self.export_selected:
            box = col.box()
            box.prop(self, "export_as_collection")
            if self.export_as_collection:
                box.prop(self, "collection_name", icon="COLLECTION_NEW", icon_only=True)
            if bpy.app.version > (2, 93, 0):
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

        if bpy.app.version > (2, 93, 0):
            export_settings["mark_asset"] = self.mark_asset
        else:
            export_settings["mark_asset"] = False

        # switching to object mode prevents unexpected behavior
        prev_mode = mode_toggle(context, 'OBJECT')

        export_blend_objects(context, export_settings)

        mode_toggle(context, prev_mode)

        return {'FINISHED'}

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

    directory: StringProperty(
        default="//"
    )

    filename: StringProperty(
        default=""
    )

    # Operator properties
    mark_asset: BoolProperty(
        name="Mark as Asset",
        description="Mark selected collection as an asset for visibility in the Asset Browser",
        default=False
    )

    backlink: BoolProperty(
        name="Backlink",
        description="Replace selection with a link to the exported object",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' # Because funky things happen when not in Object Mode

    def invoke(self, context, event):
        preferences = context.preferences.addons[__package__].preferences
        self.directory = preferences.filepath
        self.filename = context.collection.name
        self.backlink = preferences.backlink
        if bpy.app.version > (2, 93, 0):
            self.mark_asset = preferences.mark_asset
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        export_settings = {
            "is_collection": True,
            "filepath": self.filepath,
            "export_selected": True,
            "export_as_collection": True,
            "collection_name": context.selected_ids[0].name, #XXX Assumes only one collection is selected
            "backlink": self.backlink
        }
        if bpy.app.version > (2, 93, 0):
            export_settings["mark_asset"] = self.mark_asset
        else:
            export_settings["mark_asset"] = False

        # switching to object mode prevents unexpected behavior
        prev_mode = mode_toggle(context, 'OBJECT')

        export_blend_objects(context, export_settings)

        mode_toggle(context, prev_mode)

        return {'FINISHED'}


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

    directory: StringProperty(
        default="//"
    )

    filename: StringProperty(
        default=""
    )

    # Operator properties
    export_selected: BoolProperty(
        name="Export Selected",
        description="Export selected nodes to .blend file. Otherwise, export the active node tree",
        default=True
    )

    export_as_group: BoolProperty(
        name="Export as Node Group",
        description="Bundle selected objects in a node group before exporting",
        default=False
    )

    group_name: StringProperty(
        name="Group Name",
        description="Name of exported node group",
        default="export_group"
    )

    is_compositor: BoolProperty(
        name="Is Compositor",
        description="Should be True if exporting Compositor nodes",
        default=False
    )

    backlink: BoolProperty(
        name="Backlink",
        description="Replace selection with a link to the exported node group",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' # Because funky things happen when not in Object Mode

    def invoke(self, context, event):
        preferences = context.preferences.addons[__package__].preferences
        self.directory = preferences.filepath
        self.export_as_group = preferences.export_as_group
        self.backlink = preferences.backlink
        if bpy.app.version > (2, 93, 0):
            self.mark_asset = preferences.mark_asset
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        if self.is_compositor:
            self.export_selected = True
            self.export_as_group = True
            col.enabled = False

        col.prop(self, "export_selected")
        if self.export_selected:
            box = col.box()
            box.prop(self, "export_as_group")
            if self.export_as_group and not self.is_compositor:
                box.prop(self, "group_name", icon="NODETREE", icon_only=True)
                box.prop(self, "backlink")
        if self.is_compositor:
            col = layout.column()
            col.prop(self, "group_name", icon="NODETREE", icon_only=True)
            col.prop(self, "backlink")

    def execute(self, context):
        export_settings = {
            "filepath": self.filepath,
            "export_selected": self.export_selected,
            "export_as_group": self.export_as_group,
            "group_name": self.group_name,
            "backlink": self.backlink
        }

        # switching to object mode prevents unexpected behavior
        prev_mode = mode_toggle(context, 'OBJECT')

        export_blend_nodes(context, export_settings)

        mode_toggle(context, prev_mode)

        return {'FINISHED'}
