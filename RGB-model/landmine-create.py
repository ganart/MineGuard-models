import bpy
import random
import math

# Path to the .fbx file (replace with your own path)
fbx_path = r"path\to\your\pomz.fbx"

# Import the .fbx model once
bpy.ops.import_scene.fbx(filepath=fbx_path)
original_obj = bpy.context.selected_objects[-1]

for _ in range(60):
    # Duplicate the original object
    bpy.ops.object.duplicate()
    obj = bpy.context.selected_objects[-1]

    # Move the object along the X axis by a random distance from -10 to 10 meters
    obj.location.x = random.uniform(-10, 10)

    # Move the object along the Y axis by a random distance from -10 to 10 meters
    obj.location.y = random.uniform(-10, 10)

    # Move the object along the Z axis by a random distance from 0.1207 to 0.2007 meters
    obj.location.z = random.uniform(0.1207, 0.2007)

    t_f = random.choice([0, 1])

    if t_f == 1:
        # Add a random tilt along the X axis in degrees
        obj.rotation_euler.x = math.radians(random.uniform(0, 15))

        # Add a random tilt along the Y axis in degrees
        obj.rotation_euler.y = math.radians(random.uniform(0, 15))
