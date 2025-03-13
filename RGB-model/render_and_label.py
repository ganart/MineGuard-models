import bpy
import sys
import numpy as np
import shutil
import os
import json

# Default settings — change these if you want
default_config = {
    'project_dir': './blender_project',  # Where everything will be saved (relative path)
    'frame_start': 0,                    # First frame to render
    'frame_end': 75,                     # Last frame to render
    'altitude': 3,                       # How high the camera flies
    'tilt_angle': 0,                     # Camera tilt (0 = down, 90 = horizon)
    'FOV': 60,                           # Camera field of view
}

# Mine types with their IDs
MINES = {'mon': 0, 'ozm': 1, 'pfm': 2, 'pmn': 3, 'pmn2': 4, 'pom': 5, 'pomz': 6, 'tm': 7}

# Class for bounding boxes
class Box:
    dim_x = 1
    dim_y = 1

    def __init__(self, min_x, min_y, max_x, max_y, dim_x=dim_x, dim_y=dim_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.dim_x = dim_x
        self.dim_y = dim_y

    @property
    def x(self):
        return round(self.min_x * self.dim_x)

    @property
    def y(self):
        return round(self.dim_y - self.max_y * self.dim_y)

    @property
    def width(self):
        return round((self.max_x - self.min_x) * self.dim_x)

    @property
    def height(self):
        return round((self.max_y - self.min_y) * self.dim_y)

    def to_tuple(self):
        if self.width == 0 or self.height == 0:
            return (0, 0, 0, 0)
        return (self.x, self.y, self.width, self.height)

# Makes box coords fit the frame size
def normalize(data, frame_width, frame_height):
    x_center = (data[0] + data[2] / 2) / frame_width
    y_center = (data[1] + data[3] / 2) / frame_height
    width = data[2] / frame_width
    height = data[3] / frame_height
    return x_center, y_center, width, height

# Finds where an object is in the camera’s view
def camera_view_bounds_2d(scene, cam_ob, me_ob):
    mat = cam_ob.matrix_world.normalized().inverted()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    me = me_ob.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    me.transform(me_ob.matrix_world)
    me.transform(mat)

    camera = cam_ob.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    camera_persp = camera.type != 'ORTHO'

    lx = []
    ly = []

    for v in me.vertices:
        co_local = v.co
        z = -co_local.z
        if camera_persp and z == 0.0:
            lx.append(0.5)
            ly.append(0.5)
        else:
            if camera_persp:
                frame = [(v / (v.z / z)) for v in frame]
            min_x, max_x = frame[1].x, frame[2].x
            min_y, max_y = frame[0].y, frame[1].y
            x = (co_local.x - min_x) / (max_x - min_x)
            y = (co_local.y - min_y) / (max_y - min_y)
            lx.append(x)
            ly.append(y)

    center_x = clamp((max(lx) + min(lx)) / 2, 0., 1.)
    center_y = clamp((max(ly) + min(ly)) / 2, 0., 1.)

    bad_bbox = False
    if center_x in (0., 1.) and center_y in (0., 1.):
        bad_bbox = True
    if min(lx) <= 0 and max(lx) >= 1:
        bad_bbox = True
    if min(ly) <= 0 and max(ly) >= 1:
        bad_bbox = True

    if bad_bbox:
        min_x = max_x = min_y = max_y = 0.
    else:
        min_x = clamp(min(lx), 0.0, 1.0)
        max_x = clamp(max(lx), 0.0, 1.0)
        min_y = clamp(min(ly), 0.0, 1.0)
        max_y = clamp(max(ly), 0.0, 1.0)

    r = scene.render
    fac = r.resolution_percentage * 0.01
    dim_x = r.resolution_x * fac
    dim_y = r.resolution_y * fac
    return Box(min_x, min_y, max_x, max_y, dim_x, dim_y)

# Keeps numbers in range
def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

# Gets box coords for a frame
def write_bounds_2d(scene, cam_ob, me_ob, cur_frame):
    bpy.context.scene.frame_set(cur_frame)
    box = camera_view_bounds_2d(scene, cam_ob, me_ob).to_tuple()
    if np.count_nonzero(np.array(box)) != 0:
        return box
    return None

# Main function to render and label
def main(context, project_dir, frame_start, frame_end, tilt_angle, altitude, FOV):
    # Set up folders
    renders_dir = os.path.join(project_dir, "rendered")
    labels_dir = os.path.join(project_dir, "labels")
    meta_path = os.path.join(project_dir, "meta.json")

    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)
    if os.path.isdir(renders_dir):
        shutil.rmtree(renders_dir)
    if os.path.isdir(labels_dir):
        shutil.rmtree(labels_dir)
    os.mkdir(renders_dir)
    os.mkdir(labels_dir)
    renders_dir = os.path.join(renders_dir, "ILLIA_PMN_1_frame_")

    scene = context.scene
    camera = bpy.data.objects['Camera']
    camera.data.angle = np.deg2rad(FOV)
    camera.data.clip_end = 999999986991104

    # Set scene basics
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.camera = camera

    # Make a flight path
    if "FlightPath" in bpy.data.objects:
        obj = bpy.data.objects["FlightPath"]
        bpy.context.view_layer.objects.active = obj
        obj_collection = obj.users_collection[0]
        obj_collection.objects.unlink(obj)
        bpy.data.objects.remove(obj)

    sphere_path = bpy.data.objects['BezierCurve']
    bpy.context.view_layer.objects.active = sphere_path
    sphere_path.select_set(True)
    bpy.ops.object.duplicate(linked=False)
    sphere_path.select_set(False)

    flight_path = bpy.context.view_layer.objects.active
    flight_path.location.z += altitude
    flight_path.name = "FlightPath"

    # Tilt camera and set target
    depsgraph = bpy.context.evaluated_depsgraph_get()
    path_length = sum(s.calc_length() for s in sphere_path.evaluated_get(depsgraph).data.splines)
    tilt_tang = np.tan(np.deg2rad(tilt_angle))
    target_offset_meters = tilt_tang * altitude
    offset = min(max(target_offset_meters / path_length, 0.001), 0.999)

    for k in camera.constraints:
        camera.constraints.remove(camera.constraints[k])
    camera.animation_data_clear()

    constraint = camera.constraints.new(type='FOLLOW_PATH')
    constraint.target = flight_path
    constraint.use_fixed_location = True
    constraint.use_curve_follow = True
    constraint.offset_factor = 0.0
    constraint.keyframe_insert(data_path="offset_factor", frame=1)
    constraint.offset_factor = 1.0 - offset
    constraint.keyframe_insert(data_path="offset_factor", frame=frame_end)

    # Add a target sphere
    if "SurfSphere" in bpy.data.objects:
        sphere = bpy.data.objects["SurfSphere"]
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
        sphere = bpy.context.object
        bpy.data.collections['Collection'].objects.link(sphere)
        sphere.name = "SurfSphere"

    sphere.hide_render = True
    for k in sphere.constraints:
        sphere.constraints.remove(sphere.constraints[k])
    constraint_target = camera.constraints.new(type='TRACK_TO')
    constraint_target.target = sphere

    constraint_sphere = sphere.constraints.new(type='FOLLOW_PATH')
    constraint_sphere.target = sphere_path
    constraint_sphere.use_fixed_location = True
    constraint_sphere.use_curve_follow = True
    constraint_sphere.offset_factor = offset
    constraint_sphere.keyframe_insert(data_path="offset_factor", frame=1)
    constraint_sphere.offset_factor = 1.0
    constraint_sphere.keyframe_insert(data_path="offset_factor", frame=frame_end)

    # Set up rendering
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = renders_dir
    bpy.ops.render.render(animation=True)

    # Label objects
    google_collection = bpy.data.collections.get("Collection")
    frame_width = scene.render.resolution_x
    frame_height = scene.render.resolution_y

    for frame in range(frame_start, frame_end + 1):
        all_data = ''
        for obj in google_collection.objects:
            label = obj.name.split('.')[0]
            if label in MINES:
                data = write_bounds_2d(scene, camera, bpy.data.objects[obj.name], frame)
                if data:
                    x_center, y_center, width, height = normalize(data, frame_width, frame_height)
                    all_data += f"{MINES[label]} {x_center} {y_center} {width} {height}\n"

        frame_str = str(frame).zfill(4)
        label_file = os.path.join(labels_dir, f'landmine_frame_{frame_str}.txt')
        with open(label_file, 'w') as f:
            f.write(all_data)

    # Save some info
    data = {
        "altitude": altitude, "tilt_angle": tilt_angle, "path_length": path_length,
        "frame_start": frame_start, "frame_end": frame_end
    }
    with open(meta_path, 'w') as json_file:
        json.dump(data, json_file)

# Run it
if __name__ == "__main__":
    if bpy.context.space_data and bpy.context.space_data.type == "TEXT_EDITOR":
        # Use defaults if running in Blender
        config = default_config
    else:
        # Grab settings from command line
        args = sys.argv[sys.argv.index("--") + 1:]
        arg_dict = dict(zip(args[::2], args[1::2]))
        config = {
            'project_dir': str(arg_dict.get("--project_dir", default_config['project_dir'])),
            'frame_start': int(arg_dict.get("--frame_start", default_config['frame_start'])),
            'frame_end': int(arg_dict.get("--frame_end", default_config['frame_end'])),
            'tilt_angle': float(arg_dict.get("--tilt_angle", default_config['tilt_angle'])),
            'altitude': float(arg_dict.get("--altitude", default_config['altitude'])),
            'FOV': float(arg_dict.get("--FOV", default_config['FOV']))
        }

    os.makedirs(project_dir, exist_ok=True)
    old_stdout = sys.stdout
    log_file = open(os.path.join(project_dir, "message.log"), "w")
    sys.stdout = log_file

    main(bpy.context, project_dir, frame_start, frame_end, tilt_angle, altitude, FOV)

    sys.stdout = old_stdout
    log_file.close()