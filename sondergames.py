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

bl_info = \
{
    "name"        : "Sonder Games",
    "author"      : "Scott Winkelmann <scottlandart@gmail.com>",
    "version"     : (1,0,0),
    "blender"     : (2,78,0),
    "location"    : "ah",
    "description" : "Sonder Games utilities for Blender",
    "warning"     : "",
    "wiki_url"    : "",
    "tracker_url" : "",
    "category"    : "Import-Export",
}

""" IMPORT """

import os
import sys
from os.path import abspath, exists, join

def search(name, search_paths):
    """Given a search path, find folder"""
    for path in search_paths:
        test = join(path, name)
        if exists(test): return abspath(test)
    return None

fbx_folder = search("addons/io_scene_fbx",bpy.utils.script_paths())
if fbx_folder != None:
    sys.path.append(fbx_folder)
else:
    raise RuntimeError("Could not find export_fbx_bin folder")

import bpy
from io_scene_fbx import export_fbx_bin

""" END IMPORT """

""" METHODS """


""" END METHODS """

""" EXAMPLES """

''' END EXAMPLES '''


class SelectedActionsList(bpy.types.PropertyGroup):
    custom_1 = bpy.props.FloatProperty(name="My Float", default=10.2)
    custom_2 = bpy.props.IntProperty(name="My Int", default=42)

class SonderGamesUI(bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_SonderGames"
    bl_label = "Sonder Games Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'TOOLS'
    #bl_context = "object"

    def draw(self, context):
        layout = self.layout 
        ob = context.active_object
     
        #box = layout.box()
        col = layout.column(align=True)
        row = col.row()

        col.label(text="Export path")
        col.prop(context.scene, "export_path")

#operator
class ExportAS(bpy.types.Operator):
    """Export selected actions as FBX files"""
    bl_idname = "sg.export_actions"
    bl_label = "Export actions as FBX files"
    bl_options = {"REGISTER"}

    overwrite = bpy.props.BoolProperty(name="overwrite", default=False)
    selected = bpy.props.CollectionProperty(type=SelectedActionsList, name="selected")

    def run(self,context):
        
        '''
        if active.type == "ARMATURE":
            current_action = active.animation_data.action
            if current_action != None:
        '''

        active = bpy.context.active_object
        all_actions = bpy.data.actions
        for action in all_actions:
            try:
                file_name = str(action.name)+'.fbx'
                file_path = join(str(context.scene.export_path),file_name)
                if exists(file_path) and not self.overwrite:
                    self.report({"WARNING"}, "File exists: "+str(file_name))
                else:
                    export_fbx_bin.save_single(self, context.scene,
                        filepath                  = file_path,
                        apply_unit_scale          = True,
                        axis_up                   = "Y",
                        axis_forward              = "-Z",
                        context_objects           = {active},
                        object_types              = {'ARMATURE'},
                        use_mesh_modifiers        = False,
                        mesh_smooth_type          = "OFF",
                        bake_anim_use_nla_strips  = False,
                        bake_anim_use_all_actions = False,
                        bake_anim_simplify_factor = 0.0,
                        add_leaf_bones            = False,
                        use_mesh_edges            = False,
                        use_tspace                = False,
                    )
                    self.report({"INFO"},"File exported: "+str(file_name))
            except Exception(e):
                self.report({"WARNING"}, str(e))

    def execute(self, context):
        self.run(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        '''
        self.run(context)
        return {"FINISHED"}
        '''
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def add_ui(self, context) :
    self.layout.operator(ExportAS.bl_idname, icon = "TRIA_RIGHT")

def register():
    bpy.utils.register_class(SelectedActionsList)
    bpy.utils.register_class(ExportAS)
    bpy.utils.register_class(SonderGamesUI)
    bpy.types.VIEW3D_PT_tools_animation.append(add_ui)
    bpy.types.Scene.export_path = bpy.props.StringProperty \
      (
      name = "Export path",
      default = "/",
      description = "Define the export path of FBX files",
      subtype = 'DIR_PATH'
      )


def unregister():
    bpy.utils.unregister_class(SelectedActionsList)
    bpy.utils.unregister_class(ExportAS)
    bpy.utils.unregister_class(SonderGamesUI)
    bpy.types.VIEW3D_PT_tools_animation.remove(add_ui)
    del bpy.types.Scene.export_path

if __name__ == "__main__":
    register()
