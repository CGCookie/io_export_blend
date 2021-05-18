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
