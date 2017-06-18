"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

bl_info = {
    "name":        "Sonder Games",
    "author":      "Scott Winkelmann <scottlandart@gmail.com>",
    "version":     (1, 0, 0),
    "blender":     (2, 78, 0),
    "location":    "View3D > Toolshelf > Misc > Sonder Games Tools",
    "description": "Sonder Games utilities for Blender",
    "warning":     "",
    "wiki_url":    "https://github.com/ScottishCyclops/bpySonderGames",
    "tracker_url": "https://github.com/ScottishCyclops/bpySonderGames/issues",
    "category":    "Import-Export",
}

import bpy
import sys
from os.path import abspath, exists, join, sep


def find(name: str, search_paths: iter) -> any:
    """
    Given a search path, find folder
    :param name: the name of the folder to search for
    :param search_paths: the list of paths in which to search for it
    :return: the found absolute path to the folder, or None if not found
    """

    for path in search_paths:
        test = join(path, name)
        if exists(test):
            return abspath(test)
    return None


fbx_folder = find("addons" + sep + "io_scene_fbx", bpy.utils.script_paths())
if fbx_folder is not None:
    sys.path.append(fbx_folder)
else:
    raise RuntimeError("Could not find export_fbx_bin folder")

from io_scene_fbx import export_fbx_bin


def get_as_export_kwargs() -> dict:
    """
    returns a dict containing the custom properties to export an action sequence
    :return: the dict containing the properties
    """

    return dict(apply_unit_scale=True,
                axis_up="Y",
                axis_forward="-Z",
                context_objects={},
                object_types={"ARMATURE"},
                use_mesh_modifiers=False,
                mesh_smooth_type="FACE",
                bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False,
                bake_anim_simplify_factor=0.0,
                add_leaf_bones=False,
                use_mesh_edges=False,
                use_tspace=False)


def get_sk_export_kwargs() -> dict:
    """
    returns a dict containing the custom properties to export a skeletal mesh
    :return: the dict containing the properties
    """

    return dict(apply_unit_scale=True,
                axis_up="Y",
                axis_forward="-Z",
                context_objects={},
                object_types={"MESH", "ARMATURE"},
                mesh_smooth_type="FACE",
                bake_anim=False,
                add_leaf_bones=False,
                use_mesh_edges=False,
                use_tspace=False)


def export_action_sequence(operator, context, action):
    """
    Exports a given action into a fbx file, using custom properties
    :param operator: the operator though which we report messages
    :param context: the context in which the action resides
    :param action: the action to export
    :return: nothing
    """

    try:
        if not action.name.startswith("AS_"):
            operator.report({"WARNING"}, "Action name should start with 'AS_'")

        file_name = str(action.name) + ".fbx"
        file_path = join(str(context.scene.export_path), file_name)
        if exists(file_path) and not operator.overwrite:
            operator.report({"WARNING"}, "File exists: " + file_name)
        else:
            export_fbx_bin.save_single(operator, context.scene, filepath=file_path, **get_as_export_kwargs()
                                       )
            operator.report({"INFO"}, "File exported: " + file_name)
    except Exception as e:
        operator.report({"WARNING"}, str(e))


def export_skeletal_mesh(operator, context, objects, name):
    """
    Exports given objects as a skeletal mesh into a fbx file, using custom properties
    :param operator: the operator though which we report messages
    :param context: the context in which the objects resides
    :param objects: the objects to export
    :param name: the name of the skeletal mesh asset
    :return: nothing
    """

    mesh = None
    armature = None

    for obj in objects:
        if obj.type == "MESH":
            mesh = obj
        elif obj.type == "ARMATURE":
            armature = obj

    if mesh is None or armature is None:
        operator.report({"ERROR"}, "Selection does not contain a mesh and armature")
    else:
        try:
            if armature.name != "root":
                operator.report({"WARNING"}, "Armature should be named 'root'")

            file_name = str(name) + ".fbx"
            file_path = join(str(context.scene.export_path), file_name)
            if exists(file_path) and not operator.overwrite:
                operator.report({"WARNING"}, "File exists: " + file_name)
            else:
                export_fbx_bin.save_single(operator, context.scene, filepath=file_path, **get_sk_export_kwargs()
                                           )
                operator.report({"INFO"}, "File exported: " + file_name)
        except Exception as e:
            operator.report({"WARNING"}, str(e))


class SgExportAllActions(bpy.types.Operator):
    """Export all actions in the scene as FBX files"""

    bl_idname = "sg.export_all_as"
    bl_label = "Export all actions as action sequences"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)

    def run(self, context):
        all_actions = bpy.data.actions
        for action in all_actions:
            export_action_sequence(self, context, action)

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SgExportCurrentAction(bpy.types.Operator):
    """Export the active action of the selected object as an FBX file"""

    bl_idname = "sg.export_as"
    bl_label = "Export current action as an action sequence"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)

    def run(self, context):
        active = bpy.context.active_object
        if active.type != "ARMATURE":
            self.report({"WARNING"}, "You may want to select an armature")

        if active.animation_data is not None:
            if active.animation_data.action is not None:
                export_action_sequence(self, context, active.animation_data.action)
            else:
                self.report({"WARNING"}, "Selected object has no active action")
        else:
            self.report({"WARNING"}, "Selected object has no animation data")

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SgExportSkeletalMesh(bpy.types.Operator):
    """Export the selection into a skeletal mesh as an FBX file"""

    bl_idname = "sg.export_sk"
    bl_label = "Export selection as a Skeletal mesh"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)
    name = bpy.props.StringProperty(name="name", default="SK_Untitled")

    def run(self, context):
        objects = context.selected_objects
        export_skeletal_mesh(self, context, objects, self.name)

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SgToolsUi(bpy.types.Panel):
    """Defines the SonderGames Tools panel located on the left panel in the 3D view"""

    bl_idname = "VIEW_3D_PT_sg_tools"
    bl_label = "Sonder Games Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    # bl_context = "object"

    def draw(self, context):

        # export box
        self.layout.label(text="Export")
        box_export = self.layout.box()
        col_export = box_export.column(align=True)
        row_export_0_label = col_export.row()
        row_export_0 = col_export.row()
        row_export_1_label = col_export.row()
        row_export_1 = col_export.row()
        row_export_2_label = col_export.row()
        row_export_2 = col_export.row()

        row_export_0_label.label(text="Global Settings")
        row_export_0.prop(context.scene, "export_path")
        row_export_1_label.label(text="Action Sequence")
        row_export_1.operator(SgExportAllActions.bl_idname, icon="ACTION", text="Export All")
        row_export_1.operator(SgExportCurrentAction.bl_idname, icon="ACTION", text="Export Active")
        row_export_2_label.label(text="Skeletal Mesh")
        row_export_2.operator(SgExportSkeletalMesh.bl_idname, icon="MESH_MONKEY", text="Export Selected")

        # import box
        self.layout.label(text="Import")
        box_import = self.layout.box()
        col_import = box_import.column(align=True)
        row_import_0 = col_import.row()

        row_import_0.label(text="WIP")


def register():
    bpy.types.Scene.export_path = bpy.props.StringProperty(
            name="Export path",
            default="/",
            description="Define the export path of FBX files",
            subtype="DIR_PATH"
    )
    bpy.utils.register_class(SgExportAllActions)
    bpy.utils.register_class(SgExportCurrentAction)
    bpy.utils.register_class(SgExportSkeletalMesh)
    bpy.utils.register_class(SgToolsUi)


def unregister():
    bpy.utils.unregister_class(SgToolsUi)
    bpy.utils.unregister_class(SgExportSkeletalMesh)
    bpy.utils.unregister_class(SgExportCurrentAction)
    bpy.utils.unregister_class(SgExportAllActions)
    del bpy.types.Scene.export_path


if __name__ == "__main__":
    register()
