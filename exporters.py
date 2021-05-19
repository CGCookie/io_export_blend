import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

# Local imports
from .functions import export_blend_objects, export_blend_nodes


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

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' # Because funky things happen when not in Object Mode

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

    backlink: BoolProperty(
        name="Backlink",
        description="Replace selection with a link to the exported object",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' # Because funky things happen when not in Object Mode

    def execute(self, context):
        export_settings = {
            "is_collection": True,
            "filepath": self.filepath,
            "export_selected": True,
            "export_as_collection": True,
            "collection_name": context.selected_ids[0].name, #XXX Assumes only one collection is selected
            "backlink": self.backlink
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

    backlink: BoolProperty(
        name="Backlink",
        description="Replace selection with a link to the exported node group",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' # Because funky things happen when not in Object Mode

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "export_selected")
        if self.export_selected:
            box = col.box()
            box.prop(self, "export_as_group")
            if self.export_as_group:
                box.prop(self, "group_name", icon="NODETREE", icon_only=True)
                box.prop(self, "backlink")

    def execute(self, context):
        export_settings = {
            "filepath": self.filepath,
            "export_selected": self.export_selected,
            "export_as_group": self.export_as_group,
            "group_name": self.group_name,
            "backlink": self.backlink
        }
        return export_blend_nodes(context, export_settings)
