# Export to .blend

A relatively simple exporter to take selected objects, collections, or nodes and export them to their own private .blend file... with a couple neat little bonus features.

Current features:

  * Export selected objects to `.blend` file
  * Export selected objects to `.blend` file from the Outliner
  * Export selected collections to `.blend` file from the Outliner
  * Optionally create a collection of your selected objects prior to export
  * Optionally mark your exported objects or collection as an Asset for the Asset Browser when exporting (Blender 2.93+ only)
  * Optionally "backlink" your exported objects or collection, replacing assets in your current file with a library link to your exported assets
  * Export selected nodes to `.blend` file from an Node Editor

## Installation

Installation follows the same model as most Blender add-ons:

  1. Download the release ZIP.
  2. Open Blender.
  3. Open Preferences (Edit > Preferences)
  4. Navigate to the Add-ons section
  5. Click Install...
  6. Choose the ZIP you downloaded using the File Browser.

## Usage instructions

The most simple usage here is as expected, like most exporter add-ons.

  1. Navigate to File > Export > Blender (.blend)

This is the default behavior, exporting objects from your current 3D scene to a new `.blend` file. The File Browser that appears when executing this operator gives you the following export options:

  * **Export Selected** (enabled by default): Probably smart to just keep this on. Otherwise, you're basically just doing a "Save As" operation.
    * **Export as Collection**: Optionally bundle your selected objects in a collection prior to exporting. (*Note: This collection only exists in your export file. It will not persist in your current file.*)
      * **Collection Name**: If you choose to export your selection as a collection, you can name it here. By default, it has the super-exciting name, `export_collection`.
    * **Mark as Asset**: *Blender 2.93+ only*. Optionally choose to mark your selected objects as assets when exporting. If you export to an Asset folder that Blender recognizes, your export should appear in your Asset Browser. (*Note: If you choose to export your objects as a collection, only that collection will be marked as an asset, not all of the constituent objects in that collection.*)
    * **Backlink**: This is a fun one. If you enable this option, after exporting your objects (or objects bundled in a collection) to a separate .blend file, all of the selected objects in your scene will be replaced with a linked library asset that points to the file you just exported.

### Exporting from the Outliner

This add-on also adds export options to the Outliner's context menu. If you select multiple objects in the Outliner, you can right-click your selection and choose *Export to .blend*. The File Browser will appear as described in the previous section.

Additionally, if you select a collection in the Outliner (currently this add-on only supports exporting one collection at a time), the *Export to .blend* option will also appear in the context menu. In this case, the File Browser options are much more limited. Currently, you can only choose if that collection is to be marked as an Asset when exporting.

### Exporting nodes

This add-on also provides the ability to export selected nodes to a separate `.blend` file. From any Node Editor (Shader Editor, Compositor, Texture Node Editor, Geometry Node Editor), you can navigate to Node > Export to .blend. When activating this operator, you get a File Browser with the following option:

  * **Export Selected** (enabled by default): Keeping this option enabled exports all selected nodes to their own `.blend` file. If you disable this option, the whole active node tree will be exported, but only the node tree in the current Node Editor.

(*Note: In your exported file, you have an empty scene. The node tree you exported has a fake user. In order to see that node tree, you need to add whatever asset would make use of your node tree. For example, if your nodes belong to to a shader, then you need to add an object to the 3D scene and give it the shader you exported.*)

## Known issues

  * You *really* should be in Object mode for any of this to work properly
  * Currently, when enabling the *Mark as Asset* option, the text size of menu items in Blender's UI gets much larger. This is related to [T83896](https://developer.blender.org/T83896) and should [hopefully] be fixed prior to the release of Blender 2.93.
  * If an object is part of multiple collections, that information is retained on export. However, if you backlink and make a proxy, the proxy object doesn't know about other collections.
  * When exporting nodes as a node group, you will likely need to manage input and output sockets yourself.
  * If you try to export a node that is within an existing node group, this add-on doesn't quite function as expected. Currently, it clears out just the other nodes within that group, but nothing in the group's parent tree.
  * Exporting Compositor nodes is not currently supported. Blender crashes as per [T88402](https://developer.blender.org/T88402). Hopefully that's fixed before 2.93's release.
  * When enabled, Compositor nodes will likely only export selected and be forced to be exported as a group.

## Wishlist

  * Add support for exporting multiple collections
