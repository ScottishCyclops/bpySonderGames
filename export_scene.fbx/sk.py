import bpy
op = bpy.context.active_operator

op.filepath = '/home/scott/Dropbox/Sonder Games/ASUS-WS/Sister_Locomotion/Export/SK_Sister.fbx'
op.axis_forward = '-Z'
op.axis_up = 'Y'
op.version = 'BIN7400'
op.ui_tab = 'MAIN'
op.use_selection = True
op.global_scale = 1.0
op.apply_unit_scale = True
op.bake_space_transform = False
op.object_types = {'MESH', 'ARMATURE'}
op.use_mesh_modifiers = True
op.mesh_smooth_type = 'OFF'
op.use_mesh_edges = False
op.use_tspace = False
op.use_custom_props = False
op.add_leaf_bones = True
op.primary_bone_axis = 'Y'
op.secondary_bone_axis = 'X'
op.use_armature_deform_only = False
op.armature_nodetype = 'NULL'
op.bake_anim = False
op.bake_anim_use_all_bones = True
op.bake_anim_use_nla_strips = False
op.bake_anim_use_all_actions = False
op.bake_anim_force_startend_keying = True
op.bake_anim_step = 1.0
op.bake_anim_simplify_factor = 0.0
op.use_anim = True
op.use_anim_action_all = True
op.use_default_take = True
op.use_anim_optimize = True
op.anim_optimize_precision = 6.0
op.path_mode = 'AUTO'
op.embed_textures = False
op.batch_mode = 'OFF'
op.use_batch_own_dir = True
