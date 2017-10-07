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
    "version":     (1, 0, 3),
    "blender":     (2, 79, 0),
    "location":    "View3D > Toolshelf > Misc > Sonder Games Tools",
    "description": "Sonder Games utilities for Blender",
    "warning":     "",
    "wiki_url":    "https://github.com/ScottishCyclops/bpySonderGames",
    "tracker_url": "https://github.com/ScottishCyclops/bpySonderGames/issues",
    "category":    "Tools",
}

import math
import bpy
import sys
from os.path import abspath, exists, join, sep


def find(name: str, search_paths: iter) -> any:
    """
    Given a search path, find folder\t
    :param name: the name of the folder to search for\t
    :param search_paths: the list of paths in which to search for it\t
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

# dict containing the custom properties to export an action sequence
as_export_kwargs = dict(apply_unit_scale=True,
                        axis_up="Z",
                        axis_forward="Y",
                        object_types={"ARMATURE"},
                        use_mesh_modifiers=False,
                        mesh_smooth_type="FACE",
                        bake_anim_use_nla_strips=False,
                        bake_anim_use_all_actions=False,
                        bake_anim_simplify_factor=0.0,
                        add_leaf_bones=False,
                        use_mesh_edges=False,
                        use_tspace=False)


# dict containing the custom properties to export a skeletal mesh
sk_export_kwargs = dict(apply_unit_scale=True,
                        axis_up="Z",
                        axis_forward="Y",
                        object_types={"MESH", "ARMATURE"},
                        mesh_smooth_type="FACE",
                        bake_anim=False,
                        add_leaf_bones=False,
                        use_mesh_edges=False,
                        use_tspace=False)


def export_fbx(operator, context, objects, name, kwargs):
    """
    Exports objects to fbx, with the given name and parameters,
    under the scene export path\t\t
    :param operator: the operator though which we report messages\t
    :param context: the context to use\t
    :param objects: the list of objects to include in the exported file\t\t
    :param name: the base name of the file to export\t
    :param kwargs: a dict containing any additional parameters\t
    :returns: nothing
    """

    file_name = str(name) + ".fbx"
    file_path = join(str(context.scene.export_path), file_name)
    file_exists = exists(file_path)

    if file_exists and not operator.overwrite:
        operator.report({"ERROR"}, "File exists: " + file_name)
        return

    export_fbx_bin.save_single(operator, context.scene,
                               filepath=file_path,
                               context_objects=objects,
                               **kwargs)
    operator.report({"INFO"}, "File " +
                    ("overwritten" if file_exists else "exported") +
                    ": " + file_name)


def export_action_sequence(operator, context, action):
    """
    Exports a given action as an action sequence into an fbx file\t
    :param operator: the operator though which we report messages\t
    :param context: the context in which the action resides\t\t
    :param action: the action to export\t
    :return: nothing
    """

    try:
        if not action.name.startswith("AS_"):
            operator.report({"WARNING"}, "Action name should start with 'AS_'")

        export_fbx(operator, context, context.scene.objects,
                   action.name, as_export_kwargs)
    except Exception as e:
        operator.report({"WARNING"}, str(e))


def export_skeletal_mesh(operator, context, objects, name):
    """
    Exports given objects as a skeletal mesh into an fbx file\t
    :param operator: the operator though which we report messages\t
    :param context: the context in which the objects resides\t
    :param objects: the objects to export\t
    :param name: the name of the skeletal mesh asset\t
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
        operator.report({"ERROR"}, "You must select a mesh and an armature")
        return

    try:
        if armature.name != "root":
            operator.report({"WARNING"}, "Armature should be named 'root'")

        export_fbx(operator, context, objects, name, sk_export_kwargs)
    except Exception as e:
        operator.report({"WARNING"}, str(e))


class SgExportCurrentAction(bpy.types.Operator):
    """Export the active action of the selected object as an fbx file"""

    bl_idname = "sg.export_as"
    bl_label = "Export current action as an action sequence"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)

    def run(self, context):
        active = context.active_object
        if active is None:
            self.report({"ERROR"}, "No active object")
            return

        if active.type != "ARMATURE":
            self.report({"WARNING"}, "You may want to select an armature")

        if active.animation_data is None:
            self.report({"ERROR"}, "Selected object has no animation data")
            return

        if active.animation_data.action is None:
            self.report({"ERROR"}, "Selected object has no active action")
            return

        export_action_sequence(self, context, active.animation_data.action)

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SgExportSkeletalMesh(bpy.types.Operator):
    """Export the selection into a skeletal mesh as an fbx file"""

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


class SgOffsetAction(bpy.types.Operator):
    """Offsets the active action by the given amount of frames"""

    bl_idname = "sg.offset_action"
    bl_label = "Offset active action"
    bl_options = {"REGISTER", "UNDO"}

    offset = bpy.props.IntProperty(name="offset", default=0)

    def run(self, context):
        active = context.active_object

        if active is None:
            self.report({"ERROR"}, "Missing active object")
            return

        if active.animation_data is None:
            self.report({"ERROR"}, "Missing animation data")
            return

        action = active.animation_data.action

        if action is None:
            self.report({"ERROR"}, "Missing active action")
            return

        start, end = action.frame_range
        # not +1 because first and last frame are technicly the same frames
        num_frames = int(end - start)

        if num_frames % 2 != 0:
            self.report({"WARNING"}, "Uneven number of frames")

        offset = 0
        if self.offset == 0:
            # by default, offset by the center
            offset = math.floor(num_frames / 2)
        else:
            offset = self.offset % num_frames

        # copy keyframes before
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                fcurve.keyframe_points.insert(
                    kf.co.x - num_frames, kf.co.y, {"FAST"})
            # from doc: `Ensure keyframes are sorted in chronological order
            # and handles are set correctly`
            fcurve.update()

        # offset all keys and handles
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.co.x += offset
                kf.handle_left.x += offset
                kf.handle_right.x += offset
            fcurve.update()

        # add keys at start and end
        for fcurve in action.fcurves:
            # start
            fcurve.keyframe_points.insert(
                start, fcurve.evaluate(start), {"FAST"})
            # end
            fcurve.keyframe_points.insert(
                end, fcurve.evaluate(end), {"FAST"})
            fcurve.update()

        # remove keys not in range
        for fcurve in action.fcurves:
            # run backwards because we remove elements
            for i in range(len(fcurve.keyframe_points), 0, -1):
                kf = fcurve.keyframe_points[i - 1]
                # if frame out of range
                if kf.co.x < start or kf.co.x > end:
                    fcurve.keyframe_points.remove(kf, True)
            fcurve.update()

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SgToolsUi(bpy.types.Panel):
    """Defines the SonderGames Tools panel located on the left in 3D view"""

    bl_idname = "VIEW_3D_PT_sg_tools"
    bl_label = "Sonder Games Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

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
        row_export_1.operator(SgExportCurrentAction.bl_idname,
                              icon="ACTION", text="Export Active")
        row_export_2_label.label(text="Skeletal Mesh")
        row_export_2.operator(SgExportSkeletalMesh.bl_idname,
                              icon="MESH_MONKEY", text="Export Selected")

        # import box
        self.layout.label(text="Import")
        box_import = self.layout.box()
        col_import = box_import.column(align=True)
        row_import_0 = col_import.row()

        row_import_0.label(text="WIP")


def register():
    bpy.types.Scene.export_path = bpy.props.StringProperty(
        name="Export path",
        default=sep,
        description="Define the export path of fbx files",
        subtype="DIR_PATH"
    )
    bpy.utils.register_class(SgExportCurrentAction)
    bpy.utils.register_class(SgExportSkeletalMesh)
    bpy.utils.register_class(SgToolsUi)
    bpy.utils.register_class(SgOffsetAction)


def unregister():
    bpy.utils.unregister_class(SgOffsetAction)
    bpy.utils.unregister_class(SgToolsUi)
    bpy.utils.unregister_class(SgExportSkeletalMesh)
    bpy.utils.unregister_class(SgExportCurrentAction)
    del bpy.types.Scene.export_path


if __name__ == "__main__":
    register()
