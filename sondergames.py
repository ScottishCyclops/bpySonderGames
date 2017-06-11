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

bl_info = \
    {
        "name":        "Sonder Games",
        "author":      "Scott Winkelmann <scottlandart@gmail.com>",
        "version":     (1, 0, 0),
        "blender":     (2, 78, 0),
        "location":    "ah",
        "description": "Sonder Games utilities for Blender",
        "warning":     "",
        "wiki_url":    "",
        "tracker_url": "",
        "category":    "Import-Export",
    }

'''
class SgSelectedActionsList(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="")
    value = bpy.props.IntProperty(name="value", default=42)
'''


def export_action(operator, context, action):
    try:
        file_name = str(action.name) + ".fbx"
        file_path = join(str(context.scene.export_path), file_name)
        if exists(file_path) and not operator.overwrite:
            operator.report({"WARNING"}, "File exists: " + file_name)
        else:
            export_fbx_bin.save_single(operator, context.scene,
                                       filepath=file_path,
                                       apply_unit_scale=True,
                                       axis_up="Y",
                                       axis_forward="-Z",
                                       context_objects={},
                                       object_types={"ARMATURE"},
                                       use_mesh_modifiers=False,
                                       mesh_smooth_type="OFF",
                                       bake_anim_use_nla_strips=False,
                                       bake_anim_use_all_actions=False,
                                       bake_anim_simplify_factor=0.0,
                                       add_leaf_bones=False,
                                       use_mesh_edges=False,
                                       use_tspace=False,
                                       )
            operator.report({"INFO"}, "File exported: " + file_name)
    except Exception as e:
        operator.report({"WARNING"}, str(e))


class SgToolsUi(bpy.types.Panel):
    """
    Defines the SonderGames Tools panel
    located on the left panel in the 3D view
    """

    bl_idname = "VIEW_3D_PT_tools_sonder_games"
    bl_label = "Sonder Games Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    #bl_context = "object"

    def draw(self, context):
        layout = self.layout
        #ob = context.active_object

        #box = layout.box()
        col = layout.column(align=True)
        #row = col.row()

        #col.label(text="Export path")
        col.prop(context.scene, "export_path")


class SgExportAllActions(bpy.types.Operator):
    """
    Export selected actions as FBX files
    """

    bl_idname = "sg.export_all_actions"
    bl_label = "Export actions as FBX files"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)

    def run(self, context):

        #active = bpy.context.active_object
        #if active.type == "ARMATURE":
        #    current_action = active.animation_data.action
        #    if current_action != None:

        all_actions = bpy.data.actions
        for action in all_actions:
            export_action(self, context, action)

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):

        #self.run(context)
        #return {"FINISHED"}

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SgExportCurrentAction(bpy.types.Operator):
    """
    Export the current action as an FBX file
    """

    bl_idname = "sg.export_action"
    bl_label = "Export actions as FBX files"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)

    def run(self, context):
        active = bpy.context.active_object
        if active.type != "ARMATURE":
            self.report({"WARNING"}, "You may want to select an armature")

        action = active.animation_data.action
        if action is not None:
            export_action(self, context, action)
        else:
            self.report({"WARNING"}, "Selected object has no active action")

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):

        #self.run(context)
        #return {"FINISHED"}

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def append_ui(self, context):
    self.layout.operator(SgExportAllActions.bl_idname, icon="EXPORT")


def register():
    #bpy.utils.register_class(SgSelectedActionsList)
    bpy.utils.register_class(SgToolsUi)
    bpy.utils.register_class(SgExportAllActions)
    bpy.types.VIEW_3D_PT_tools_sonder_games.append(append_ui)
    bpy.types.Scene.export_path = bpy.props.StringProperty(
            name="Export path",
            default="/",
            description="Define the export path of FBX files",
            subtype="DIR_PATH"
    )


def unregister():
    #bpy.utils.unregister_class(SgSelectedActionsList)
    bpy.utils.unregister_class(SgToolsUi)
    bpy.utils.unregister_class(SgExportAllActions)
    bpy.types.VIEW_3D_PT_tools_sonder_games.remove(append_ui)
    del bpy.types.Scene.export_path


if __name__ == "__main__":
    register()
