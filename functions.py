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


def actually_export(export_scene, filepath):
    # Set the export scene as the active scene
    bpy.context.window.scene = export_scene
    # Remove all other scenes
    for scn in bpy.data.scenes:
        if scn != export_scene:
            bpy.data.scenes.remove(scn)

    # Go through and remove all the orphans that've been created
    bpy.data.orphans_purge(do_recursive = True)

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
    if export_settings["export_selected"] and not export_settings["is_collection"]:
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

            # Remove objects from scene so they can be replaced
            for obname in object_names:
                bpy.data.objects.remove(bpy.data.objects[obname], do_unlink=True)

            # Do the actual replacing thing
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


def export_blend_nodes(context, export_settings):
    print("Exporting nodes to .blend...")

    current_nodetree = context.active_node.id_data
    if export_settings["export_selected"]:
        # Remove any nodes that aren't selected
        for node in current_nodetree.nodes:
            if not node.select:
                current_nodetree.nodes.remove(node)

    #XXX Right now forcing compositor nodes to export as group
    if export_settings["export_as_group"] or current_nodetree.type == 'COMPOSITING':
        # Create a node group with the selected nodes
        #XXX Would be nice to do this without operators, but that seems non-trivial
        bpy.ops.node.group_make()
        bpy.ops.node.group_edit(exit=True)
        context.active_node.name = export_settings["group_name"]
        context.active_node.node_tree.name = export_settings["group_name"]

    # Set the current node tree to have a fake user
    current_nodetree.use_fake_user = True

    # Create a new empty scene to hold export objects
    export_scene = bpy.data.scenes.new("blend_export")
    if current_nodetree.type == 'COMPOSITING':
        export_scene.use_nodes = True
        # Remove default Render Layers and Output node
        for node in export_scene.node_tree.nodes:
            export_scene.node_tree.nodes.remove(node)
        #XXX Right now forcing compositor nodes to export as group
        temp_group = export_scene.node_tree.nodes.new("CompositorNodeGroup")
        temp_group.node_tree = bpy.data.node_groups[export_settings["group_name"]]

    actually_export(export_scene, export_settings["filepath"])

    # If backlinks are activated, replace each object with a link to the exported one
    if export_settings["export_selected"] and export_settings["export_as_group"] and export_settings["backlink"]:
        linkpath = export_settings["filepath"] + "\\NodeTree\\" + export_settings["group_name"]
        linkdir = export_settings["filepath"] + "\\NodeTree\\"
        linkcol = export_settings["group_name"]

        # Remove nodes from scene so they can be replaced
        current_nodetree = context.active_node.id_data # Blender needs to be reminded where it is
        for node in current_nodetree.nodes:
            if node.select:
                current_nodetree.nodes.remove(node)

        # Do the actual replacing thing, first link the exported group
        bpy.ops.wm.link(
            filepath=linkpath,
            directory=linkdir,
            filename=linkcol
        )

        # Add the node group to the tree
        #XXX Assumes unique group names
        linked_nodegroup = bpy.data.node_groups[linkcol]
        # Get node group type
        #XXX Assuming here that the node group type for adding is it's self-reported type + "NodeGroup". May break for custom nodes
        if linked_nodegroup.type == 'COMPOSITING':
            nodetree_type = "CompositorNodeGroup"
        else:
            nodetree_type = linked_nodegroup.type.title() + "NodeGroup"
        replacement_group = current_nodetree.nodes.new(nodetree_type)
        replacement_group.node_tree = linked_nodegroup
