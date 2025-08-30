bl_info = {
    "name": "Ball Joint Generator (synced offsets)",
    "author": "ChatGPT",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Add > Mesh",
    "description": "Generate male ball joint (visible) and synced socket cutter (boolean preview).",
    "category": "Object",
}

import bpy
import mathutils

class OBJECT_OT_add_socket_and_male(bpy.types.Operator):
    bl_idname = "mesh.add_socket_and_male"
    bl_label = "Add Socket and Male Joint (synced)"
    bl_options = {'REGISTER', 'UNDO'}

    # --- 共通 ---
    clearance: bpy.props.FloatProperty(name="Clearance", default=0.2, min=0.0)
    rotation: bpy.props.FloatVectorProperty(
        name="Rotation (XYZ)", subtype='EULER', default=(0.0, 0.0, 0.0)
    )

    male_offset: bpy.props.FloatVectorProperty(
        name="Male Offset (XYZ)", subtype='TRANSLATION', default=(0.0, 0.0, 0.0)
    )

    # --- オス側 ---
    ball_radius_male: bpy.props.FloatProperty(name="Male Ball Radius", default=1.0, min=0.01)
    ball_shape_male: bpy.props.EnumProperty(
        name="Male Ball Shape",
        items=[
            ('SPHERE', "Sphere", ""),
            ('CYLINDER', "Cylinder", ""),
            ('CUBE', "Cube", ""),
        ],
        default='SPHERE'
    )
    stem_shape_male: bpy.props.EnumProperty(
        name="Male Stem Shape",
        items=[
            ('CYLINDER', "Cylinder", ""),
            ('SPHERE', "Sphere", ""),
            ('CUBE', "Cube", ""),
            ('TRI_CONE', "Triangular Cone", ""),
            ('ROUND_CONE', "Round Cone", ""),
        ],
        default='CYLINDER'
    )
    stem_height_male: bpy.props.FloatProperty(name="Male Stem Height", default=2.0, min=0.01)
    stem_radius_male: bpy.props.FloatProperty(name="Male Stem Radius", default=0.5, min=0.01)
    stem_offset_male: bpy.props.FloatProperty(name="Male Stem Offset (Z)", default=-1.2)

    # --- ソケット側（male_offset と完全同期する） ---
    separate_socket_settings: bpy.props.BoolProperty(name="Use Separate Socket Settings", default=False)
    ball_radius_socket: bpy.props.FloatProperty(name="Socket Ball Radius", default=1.2, min=0.01)
    ball_shape_socket: bpy.props.EnumProperty(
        name="Socket Ball Shape",
        items=[
            ('SPHERE', "Sphere", ""),
            ('CYLINDER', "Cylinder", ""),
            ('CUBE', "Cube", ""),
        ],
        default='SPHERE'
    )
    stem_shape_socket: bpy.props.EnumProperty(
        name="Socket Stem Shape",
        items=[
            ('CYLINDER', "Cylinder", ""),
            ('SPHERE', "Sphere", ""),
            ('CUBE', "Cube", ""),
            ('TRI_CONE', "Triangular Cone", ""),
            ('ROUND_CONE', "Round Cone", ""),
        ],
        default='CYLINDER'
    )
    stem_height_socket: bpy.props.FloatProperty(name="Socket Stem Height", default=2.0, min=0.01)
    stem_radius_socket: bpy.props.FloatProperty(name="Socket Stem Radius", default=0.5, min=0.01)
    stem_offset_socket: bpy.props.FloatProperty(name="Socket Stem Offset (Z)", default=-1.2)

    # --- カットアウト ---
    use_cutout: bpy.props.BoolProperty(name="Add Cutout", default=False)
    cutout_width: bpy.props.FloatProperty(name="Cutout Width", default=0.6, min=0.01)
    cutout_depth: bpy.props.FloatProperty(name="Cutout Depth", default=2.0, min=0.01)
    cutout_z: bpy.props.FloatProperty(name="Cutout Z Position", default=0.0)

    def execute(self, context):
        target = context.active_object
        if target is None or target.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object to cut into (e.g. torso)")
            return {'CANCELLED'}

        cursor_loc = context.scene.cursor.location.copy()
        rot_euler = mathutils.Euler(self.rotation)
        rot_mat = rot_euler.to_matrix()

        # --- オス側作成 ---
        male_origin = cursor_loc + (rot_mat @ mathutils.Vector(self.male_offset))
        male_stem_origin = cursor_loc + (rot_mat @ (mathutils.Vector(self.male_offset) + mathutils.Vector((0, 0, self.stem_offset_male))))

        male_ball = self._create_ball(self.ball_shape_male, self.ball_radius_male, male_origin, self.rotation)
        male_stem = self._create_stem(self.stem_shape_male, self.stem_radius_male, self.stem_height_male, male_stem_origin, self.rotation)
        self._boolean_apply(male_ball, male_stem, 'UNION')
        bpy.data.objects.remove(male_stem, do_unlink=True)

        # --- メス側カッター（male_offset と完全同期） ---
        if self.separate_socket_settings:
            ball_radius_socket = self.ball_radius_socket
            ball_shape_socket = self.ball_shape_socket
            stem_shape_socket = self.stem_shape_socket
            stem_height_socket = self.stem_height_socket
            stem_radius_socket = self.stem_radius_socket
            stem_offset_socket = self.stem_offset_socket
        else:
            ball_radius_socket = self.ball_radius_male + self.clearance
            ball_shape_socket = self.ball_shape_male
            stem_shape_socket = self.stem_shape_male
            stem_height_socket = self.stem_height_male
            stem_radius_socket = self.stem_radius_male + self.clearance
            stem_offset_socket = self.stem_offset_male

        socket_origin = cursor_loc + (rot_mat @ mathutils.Vector(self.male_offset))
        socket_stem_origin = cursor_loc + (rot_mat @ (mathutils.Vector(self.male_offset) + mathutils.Vector((0, 0, stem_offset_socket))))

        cutter_ball = self._create_ball(ball_shape_socket, ball_radius_socket, socket_origin, self.rotation)
        cutter_stem = self._create_stem(stem_shape_socket, stem_radius_socket, stem_height_socket, socket_stem_origin, self.rotation)
        self._boolean_apply(cutter_ball, cutter_stem, 'UNION')
        bpy.data.objects.remove(cutter_stem, do_unlink=True)

        # Boolean preview
        bool_cut = target.modifiers.new(name="SocketCut", type='BOOLEAN')
        bool_cut.object = cutter_ball
        bool_cut.operation = 'DIFFERENCE'
        try: bool_cut.solver = 'FAST'
        except: pass

        cutter_ball.display_type = 'WIRE'
        cutter_ball.hide_set(True)

        # --- カットアウト ---
        if self.use_cutout:
            offset_vec = rot_mat @ mathutils.Vector((0, 0, self.cutout_z))
            cutout_loc = cursor_loc + offset_vec
            bpy.ops.mesh.primitive_cube_add(size=1, location=cutout_loc, rotation=self.rotation)
            cutout = context.active_object
            cutout.name = "Cutter_Cutout"
            cutout.scale[0] = self.cutout_width
            cutout.scale[1] = (ball_radius_socket + stem_radius_socket) * 2
            cutout.scale[2] = self.cutout_depth
            bool_cut2 = target.modifiers.new(name="SocketCutout", type='BOOLEAN')
            bool_cut2.object = cutout
            bool_cut2.operation = 'DIFFERENCE'
            try: bool_cut2.solver = 'FAST'
            except: pass
            cutout.display_type = 'WIRE'
            cutout.hide_set(True)

        return {'FINISHED'}

    # --- primitive helpers ---
    def _create_ball(self, shape, radius, origin, rotation):
        if shape == 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=origin, rotation=rotation)
        elif shape == 'CYLINDER':
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=radius*2, location=origin, rotation=rotation)
        elif shape == 'CUBE':
            bpy.ops.mesh.primitive_cube_add(size=radius*2, location=origin, rotation=rotation)
        return bpy.context.active_object

    def _create_stem(self, shape, radius, height, origin, rotation):
        if shape == 'CYLINDER':
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=origin, rotation=rotation)
        elif shape == 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=origin, rotation=rotation)
        elif shape == 'CUBE':
            bpy.ops.mesh.primitive_cube_add(size=radius*2, location=origin, rotation=rotation)
        elif shape == 'TRI_CONE':
            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=radius, radius2=0, depth=height, location=origin, rotation=rotation)
        elif shape == 'ROUND_CONE':
            bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, radius2=0, depth=height, location=origin, rotation=rotation)
        return bpy.context.active_object

    def _boolean_apply(self, target, cutter, operation):
        mod = target.modifiers.new(name="BoolTemp", type='BOOLEAN')
        mod.object = cutter
        mod.operation = operation
        try: mod.solver = 'FAST'
        except: pass
        prev_active = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target
        try: bpy.ops.object.modifier_apply(modifier=mod.name)
        finally: bpy.context.view_layer.objects.active = prev_active


class OBJECT_OT_apply_balljoint(bpy.types.Operator):
    bl_idname = "mesh.apply_balljoint"
    bl_label = "Apply Ball Joint Modifiers and Remove Cutters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target = context.active_object
        if not target or target.type != 'MESH':
            self.report({'ERROR'}, "Select target mesh")
            return {'CANCELLED'}
        mods = [m.name for m in target.modifiers if m.type == 'BOOLEAN']
        prev_active = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target
        for name in mods:
            try: bpy.ops.object.modifier_apply(modifier=name)
            except: pass
        cutters = [o for o in bpy.data.objects if o.name.startswith("Cutter")]
        for o in cutters:
            try: bpy.data.objects.remove(o, do_unlink=True)
            except: pass
        bpy.context.view_layer.objects.active = prev_active
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_add_socket_and_male.bl_idname, text="Ball & Socket Joint (synced)", icon='MESH_UVSPHERE')


classes = (OBJECT_OT_add_socket_and_male, OBJECT_OT_apply_balljoint)

def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    for c in reversed(classes): bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()