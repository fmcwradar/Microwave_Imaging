import sys

import numpy as np

from vispy import app, scene, io, visuals as vispy_vis, plot as vp
from vispy.visuals.transforms import STTransform, MatrixTransform
from vispy.scene.visuals import Text
import scipy

# Read volume
# vol = np.load(io.load_data_file('volume/stent.npz'))['arr_0']

import os
import pickle

current_dir = os.path.dirname(__file__)

import platform
pc_name = platform.uname()[1]

if pc_name == "White-Knight":
    processor_number = 7
elif pc_name == "MJ-XMG":
    processor_number = 9

current_dir = os.path.dirname(__file__)
working_dir = r"D:\Microwave_Imaging\Pickle_Files\2025-03-20_11-37-56"
save_animation = False

with open(f"{working_dir}\\image_radar.pkl", 'rb') as file:
# with open(f"{working_dir}\Final_3D_Files\\final_3D_image.pkl", 'rb') as file:
    # Call load method to deserialze.
    vol2 = pickle.load(file)

    intensity_matrix = vol2 ** 2
    intensity_matrix_norm = np.abs(intensity_matrix) / np.max(np.abs(intensity_matrix))
    # print(f"{np.max(np.abs(vol2))}")
    intensity_matrix_db = 20 * np.log10(intensity_matrix_norm)
    print(intensity_matrix_db.dtype)

    image_matrix_3D = np.abs(vol2[:, :, :]).astype(np.float32)
    image_matrix_3D_db = intensity_matrix_db[:, :, :].astype(np.float32)

    vol2 = image_matrix_3D_db
    print(f"{np.max(np.abs(vol2))}")
    rearranged_vol2 = np.swapaxes(vol2, 0, 2)
    rearranged_vol2 = np.flip(rearranged_vol2, 2)
    rearranged_vol2 = np.swapaxes(rearranged_vol2, 2, 1)
    # rearranged_vol2 = np.flip(rearranged_vol2, 1)
    vol = rearranged_vol2
    # vol = vol2

with open(f"{working_dir}\\Settings.txt", "r") as file:
    lines = file.readlines()

    offset = float(lines[14].split("= ")[1])
    start_x = int(lines[15].split(" cm\n")[0].split("start_x = ")[1])
    start_y = int(lines[16].split(" cm\n")[0].split("start_y = ")[1])
    start_z = int(lines[17].split(" cm\n")[0].split("start_z = ")[1])
    end_x = int(lines[18].split(" cm\n")[0].split("end_x = ")[1])
    end_y = int(lines[19].split(" cm\n")[0].split("end_y = ")[1])
    end_z = int(lines[20].split(" cm\n")[0].split("end_z = ")[1])
    number_of_points_x = int(lines[22].split("\n")[0].split("Number of points x = ")[1])
    number_of_points_y = int(lines[23].split("\n")[0].split("Number of points y = ")[1])
    number_of_points_z = int(lines[24].split("\n")[0].split("Number of points z = ")[1])

x_axis = np.linspace(start_x, end_x, number_of_points_x)
y_axis = np.linspace(start_y, end_y, number_of_points_y)
z_axis = np.linspace(start_z, end_z, number_of_points_z)

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(1000, 1000), show=True)
view1 = canvas.central_widget.add_view()

clim = (-30, 0)
texture_format = 'auto'

volume = scene.visuals.Volume(
    vol,
    parent=view1.scene,
    raycasting_mode='volume',
    method='mip',
    cmap='jet',
    clim=clim
)
# volume.set_gl_state('additive')
volume.opacity = 1 # 0.25

# Create a camera
cam = scene.cameras.TurntableCamera(
    parent=view1.scene, fov=60.0, azimuth=-42.0, elevation=30.0
)
view1.camera = cam

data_points_x = np.size(vol, 0)
data_points_y = np.size(vol, 1)
data_points_z = np.size(vol, 2)

def add_axis(view, axis, start, end, ticks, label_pos, line_width=1000):
    for t in ticks:
        if axis == 'x':
            tick_color = 'red'
        elif axis == 'y':
            tick_color = 'green'
        elif axis == 'z':
            tick_color = 'blue'
        tick_line = scene.visuals.Line(pos=np.array([start, start + (t - np.min(ticks)) * (end - start)]), color=tick_color, width=10, parent=view.scene)
        tick_line.transform = MatrixTransform()
        # tick_line.transform.translate(start + t * (end - start) + label_pos)
        tick_line.transform.translate(label_pos)
        tick_label = scene.visuals.Text(str(round(t, 0)), color='white', font_size=5000, anchor_x='right', anchor_y='bottom', parent=view.scene)
        tick_label.transform = MatrixTransform()
        # tick_label.transform.translate(start + t * (end - start) + label_pos)
        tick_label.transform.translate((t- np.min(ticks)) * (end - start) + label_pos)

def update_coordinate_system():
    # Calculate ticks
    start_x = x_axis[0]
    end_x = x_axis[len(x_axis) - 1]

    start_y = y_axis[0]
    end_y = y_axis[len(y_axis) - 1]

    start_z = z_axis[0]
    end_z = z_axis[len(z_axis) - 1]

    x_ticks = np.flip(np.linspace(start_x, end_x, 10))
    x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x) + np.abs(start_x)) / 4, 0) + 1))

    y_ticks = (np.linspace(start_y, end_y, 6))
    y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y) - np.abs(start_y)) / 4, 0) + 1))

    z_ticks = (np.linspace(start_z, end_z, 5))
    # z_ticks = [0.0, 3.0, 7.0, 11.0, 15.0, 19.0, 23.0]
    z_ticks_location = np.linspace(0, len(z_axis), int(np.round(((end_z) - (start_z)) / 4, 0) + 1))

    print(x_ticks)
    print(y_ticks)
    print(z_ticks)

    # Add the X axis
    add_axis(view1, 'x', np.array([0, 0, 0]), np.array([4.5, 0, 0]), x_ticks, np.array([0, -16, 0]))

    # Add the Y axis
    add_axis(view1, 'y', np.array([0, 0, 0]), np.array([0, 5, 0]), y_ticks, np.array([-16, 0, 0]))

    # Add the Z axis
    add_axis(view1, 'z', np.array([0, 0, 0]), np.array([0, 0, 9]), z_ticks, np.array([-16, -16, 0]))

# update_axis_visual()
update_coordinate_system()

# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == 's':
        print("Saving view")
        import matplotlib.pyplot as plt
        # Render the canvas to an image
        img = canvas.render(size=(20, 20))
        # Save the image as a PDF
        plt.imshow(img)
        plt.axis('off')  # Remove axes for a clean output
        plt.savefig("3D-output.pdf", bbox_inches='tight', pad_inches=0)
        plt.close()
    if event.text == '1':
        methods = ['mip', 'average']
        method = methods[(methods.index(plane.method) + 1) % 2]
        print("Volume render method: %s" % method)
        plane.method = method
    elif event.text == '2':
        modes = ['volume', 'plane']
        if plane.raycasting_mode == modes[0]:
            plane.raycasting_mode = modes[1]
            print(modes[1])
        else:
            plane.raycasting_mode = modes[0]
            print(modes[0])
    elif event.text != '' and event.text in '{}':
        t = -1 if event.text == '{' else 1
        plane.plane_thickness += t
        plane.plane_thickness += t
        print(f"plane thickness: {plane.plane_thickness}")
    elif event.text != '' and event.text in '[]':
        shift = plane.plane_normal / np.linalg.norm(plane.plane_normal)
        if event.text == '[':
            plane.plane_position -= 1 * shift
        elif event.text == ']':
            plane.plane_position += 1 * shift

        #update plot of specific slice
        if (plane.plane_normal == [1, 0, 0]).all():
            select_slice = "slice_z"
            replace_plot(select_slice)
        if (plane.plane_normal == [0, 1, 0]).all():
            select_slice = "slice_y"
            replace_plot(select_slice)
        if (plane.plane_normal == [0, 0, 1]).all():
            select_slice = "slice_x"
            replace_plot(select_slice)
        print(f"plane position: {plane.plane_position}")
    elif event.text == 'x':
        plane.plane_normal = [0, 0, 1]
        current_plane = 0
    elif event.text == 'y':
        plane.plane_normal = [0, 1, 0]
        current_plane = 1
    elif event.text == 'z':
        plane.plane_normal = [1, 0, 0]
        current_plane = 2
    elif event.text == 'o':
        plane.plane_normal = [1, 1, 1]
        current_plane = 'o'

def replace_plot(select_slice):
    global view1, canvas_size #, colorbars

    if select_slice == None:
        place_slice_plots(None)
        place_slice_plots("3D")

# timer = app.Timer('auto', connect=move_plane, start=True)
label_color = 'white'
shape = vol.shape
colorbars = []

def place_slice_plots(select_slice):
    global colorbar_0, view1, plane

    canvas_size = canvas.size
    if select_slice == None:
        title_3D = Text(f'{plane.plane_position}', parent=view1, color='green')
        title_3D.font_size = 18
        title_3D.pos = canvas_size[0] * 0.25, canvas_size[1] * 0.05, 0

        # Add a colorbar to the right of the volume
        colorbar_0 = scene.visuals.ColorBar(label='Measurement in dB', label_color=label_color, cmap='jet', clim=clim,
                                            orientation='right', size=(500, 40), parent=view1)

        canvas_size = canvas.size
        # Resize and move the colorbars
        colorbar_0.transform = scene.STTransform(translate=(canvas_size[0] * 0.45, canvas_size[1] * 0.25, 0))

        colorbars = [colorbar_0]

        # Resize and move the 2D plots
        slice_z.transform = scene.STTransform(scale=(np.min(canvas_size) * 0.0025, np.min(canvas_size) * 0.0025, 1),
                                              translate=(canvas_size[0] * 0.1, canvas_size[1] * 0.1, 0))
        slice_y.transform = scene.STTransform(scale=(np.min(canvas_size) * 0.0015, np.min(canvas_size) * 0.0015, 1),
                                              translate=(canvas_size[0] * 0.1, canvas_size[1] * 0.1, 0))
        slice_x.transform = scene.STTransform(scale=(np.min(canvas_size) * 0.0015, np.min(canvas_size) * 0.0015, 1),
                                              translate=(canvas_size[0] * 0.1, canvas_size[1] * 0.1, 0))
    if select_slice == "3D":
        volume = scene.visuals.Volume(
            vol,
            parent=view1.scene,
            raycasting_mode='volume',
            method='mip',
        )
        volume.set_gl_state('additive')
        volume.opacity = 0.25

        view1.camera = cam
        colorbar_0 = scene.visuals.ColorBar(label='Measurement in dB', label_color=label_color, cmap='jet', clim=clim, border_width=2.0, border_color='white',
                                            orientation='right', size=(500, 40), parent=view1)
        colorbar_0.label.font_size = 24
        colorbar_0.label.color = 'black'
        colorbar_0.transform = scene.STTransform(translate=(canvas_size[0] * 0.90, canvas_size[1] * 0.45, 0))

    colorbars = [colorbar_0]

# Define the resize callback
def update_colorbars(colorbars):
    # Get the new canvas size
    canvas_size = canvas.size
    colorbar_width = 400
    colorbar_height = 30  # Scale height to 80% of canvas height

    colorbar_0.transform = scene.STTransform(translate=(canvas_size[0] * 0.9, canvas_size[1] * 0.45, 0))

# Function to resize plot elements based on canvas size
def on_canvas_resize(event):
    global slice_z, slice_y, slice_x, title_z, title_y, title_x, title_3D
    canvas_width, canvas_height = event.size
    canvas_size = [canvas_width, canvas_height]
    update_colorbars(colorbars)

canvas.events.resize.connect(on_canvas_resize)

place_slice_plots("3D")

if save_animation == True:
    import numpy as np
    import imageio
    from vispy import scene, app

    # Save video frames
    frames = []
    num_frames = 180  # Number of frames in the loop

    for i in range(int(num_frames/2)):
        view1.camera.azimuth += 180 / num_frames  # Rotate camera
        canvas.update()  # Update canvas
        frame = canvas.render()  # Capture frame
        frames.append(frame)

    for i in range(int(num_frames/2)):
        view1.camera.azimuth -= 180 / num_frames  # Rotate camera
        canvas.update()  # Update canvas
        frame = canvas.render()  # Capture frame
        frames.append(frame)

    # ✅ Save as MP4 using FFmpeg
    imageio.mimsave(f"Test.mp4", frames, format="FFMPEG", fps=30)

    # ✅ Save as GIF (Optional)
    imageio.mimsave(f"Test.gif", frames, duration=1/30)  # 30 FPS

    print("MP4 and GIF saved successfully!")

if __name__ == '__main__':
    canvas.show()
    print(__doc__)
    if sys.flags.interactive == 0:
        # plane.plane_position = plane_start
        app.run()