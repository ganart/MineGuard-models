import bpy
import random 

# Render settings
render = bpy.context.scene.render
render.engine = 'BLENDER_EEVEE'  # Set render engine to Eevee
render.resolution_x = 1920  # Set resolution width to 1920px
render.resolution_y = 1920  # Set resolution height to 1920px


# Function to generate images with randomized grass settings
def generate_image(frame_number, output_dir="D:/blender_tm/grass/"):
    """
    Generate a single image with randomized grass seed and density.

    Args:
        frame_number (int): The frame number to set and use in the filename.
        output_dir (str): Directory where the rendered image will be saved.
    """
    # Set the current frame
    bpy.context.scene.frame_set(frame_number)

    # Random seed for grass distribution
    bpy.data.node_groups["Distribute On Faces.001"].nodes["effect"].inputs[5].default_value = random.randint(-1000,
                                                                                                             1000)
    bpy.data.node_groups["Distribute On Faces.002"].nodes["effect"].inputs[5].default_value = random.randint(-1000,
                                                                                                             1000)
    bpy.data.node_groups["Distribute On Faces.003"].nodes["effect"].inputs[5].default_value = random.randint(-1000,
                                                                                                             1000)
    bpy.data.node_groups["Distribute On Faces"].nodes["effect"].inputs[5].default_value = random.randint(-1000, 1000)

    # Random density for grass
    bpy.data.node_groups["Distribute On Faces"].nodes["effect"].inputs[3].default_value = random.randint(1, 15)
    bpy.data.node_groups["Distribute On Faces.001"].nodes["effect"].inputs[3].default_value = random.randint(10, 15)
    bpy.data.node_groups["Distribute On Faces.002"].nodes["effect"].inputs[3].default_value = random.randint(50, 75)
    bpy.data.node_groups["Distribute On Faces.003"].nodes["effect"].inputs[3].default_value = random.randint(15, 25)

    # Set the output filepath for the rendered image
    render.filepath = f"{output_dir}image_{frame_number}.png"
    # Render the image and save it
    bpy.ops.render.render(write_still=True)


# Generate 3 images
output_directory = "D:/blender_tm/grass/"  # Change this to your preferred output directory
for frame_number in range(3):
    generate_image(frame_number, output_directory)
