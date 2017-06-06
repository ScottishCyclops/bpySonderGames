import bpy
op = bpy.context.active_operator

op.filepath = '/home/scott/Dropbox/Sonder Games/ASUS-WS/Sister_Locomotion/Export/SK_Sister.fbx'
op.axis_forward = '-Z'
op.axis_up = 'Y'
op.directory = '/home/scott/Dropbox/Sonder Games/ASUS-WS/Sister_Locomotion/Export/'
op.ui_tab = 'MAIN'
op.use_manual_orientation = False
op.global_scale = 1.0
op.bake_space_transform = False
op.use_custom_normals = True
op.use_image_search = False
op.use_alpha_decals = False
op.decal_offset = 0.0
op.use_anim = True
op.anim_offset = 1.0
op.use_custom_props = True
op.use_custom_props_enum_as_string = True
op.ignore_leaf_bones = False
op.force_connect_children = False
op.automatic_bone_orientation = True
op.primary_bone_axis = 'Y'
op.secondary_bone_axis = 'X'
op.use_prepost_rot = False
