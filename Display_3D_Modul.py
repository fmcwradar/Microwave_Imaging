import numpy as np
import sys
from vispy import app, scene, io, visuals as vispy_vis, plot as vp
from vispy.visuals.transforms import STTransform, MatrixTransform
from vispy.scene.visuals import Text
import scipy
import os
import pickle

import platform

clim = (-30, 0)
label_color = 'white'
global colorbar_0, view1, plane

class display_3D:
    """
        Class that calculates the image based on the IF spectra measured with an FMCW radar system.

        INPUTS:
            number_of_points_x: (int) number of points along the x_axis.
            number_of_points_y: (int) number of points along the y_axis.
            number_of_points_z: (int) number of points along the z_axis.
            start_x: (float) start value of the x-axis in the image.
            start_y: (float) start value of the y-axis in the image.
            start_z: (float) start value of the z-axis in the image.
            end_x: (float) end value of the x-axis in the image.
            end_y: (float) end value of the y_axis in the image.
            end_z: (float) end value of the z_axis in the image.
            dynamic_range: (float) dynamic range of the image.
            path: (string) path description to the working directory.
        """

    def __init__(self, number_of_points_x, number_of_points_y, number_of_points_z, start_x, start_y,
                 start_z, end_x, end_y, end_z, dynamic_range, path):

        self.number_of_points_x = number_of_points_x
        self.number_of_points_y = number_of_points_y
        self.number_of_points_z = number_of_points_z
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z
        self.end_x = end_x
        self.end_y = end_y
        self.end_z = end_z
        self.dynamic_range = dynamic_range
        self.path = path

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
            tick_line.transform.translate(label_pos)
            tick_label = scene.visuals.Text(str(round(t, 0)), color='white', font_size=5000, anchor_x='right', anchor_y='bottom', parent=view.scene)
            tick_label.transform = MatrixTransform()
            tick_label.transform.translate((t- np.min(ticks)) * (end - start) + label_pos)

    def update_coordinate_system(self):
        # Calculate ticks
        x_ticks = np.flip(np.linspace(self.start_x, self.end_x, 10))
        x_ticks_location = np.linspace(0, len(self.x_axis), int(np.round((np.abs(self.end_x) + np.abs(self.start_x)) / 4, 0) + 1))

        y_ticks = (np.linspace(self.start_y, self.end_y, 6))
        y_ticks_location = np.linspace(0, len(self.y_axis), int(np.round((np.abs(self.end_y) - np.abs(self.start_y)) / 4, 0) + 1))

        z_ticks = (np.linspace(self.start_z, self.end_z, 5))
        z_ticks_location = np.linspace(0, len(self.z_axis), int(np.round(((self.end_z) - (self.start_z)) / 4, 0) + 1))

        # print(x_ticks)
        # print(y_ticks)
        # print(z_ticks)

        # Add the X axis
        self.add_axis(view1, 'x', np.array([0, 0, 0]), np.array([4.5, 0, 0]), x_ticks, np.array([0, -16, 0]))

        # Add the Y axis
        self.add_axis(view1, 'y', np.array([0, 0, 0]), np.array([0, 5, 0]), y_ticks, np.array([-16, 0, 0]))

        # Add the Z axis
        self.add_axis(view1, 'z', np.array([0, 0, 0]), np.array([0, 0, 9]), z_ticks, np.array([-16, -16, 0]))

    def move_plane(self, event):
        if (plane.plane_normal == [1, 0, 0]).all():
            current_plane = plane.plane_position[0]
        elif (plane.plane_normal == [0, 1, 0]).all():
            current_plane = plane.plane_position[1]
        elif (plane.plane_normal == [0, 0, 1]).all():
            current_plane = plane.plane_position[2]
        else:
            current_plane = plane.plane_position[0]
        if current_plane < 0:
            if (plane.plane_normal == [1, 0, 0]).all():
                plane.plane_position = plane.plane_position + [1, 0, 0]
            elif (plane.plane_normal == [0, 1, 0]).all():
                plane.plane_position = plane.plane_position + [0, 1, 0]
            elif (plane.plane_normal == [0, 0, 1]).all():
                plane.plane_position = plane.plane_position + [0, 0, 1]
            else:
                plane.plane_position = plane.plane_position + [0, 0, 0]
        elif 0 < current_plane <= np.shape(self.vol)[np.where(plane.plane_normal == 1)[0][0]]:
            if (plane.plane_normal == [1, 0, 0]).all():
                plane.plane_position = plane.plane_position - [1, 0, 0]
            elif (plane.plane_normal == [0, 1, 0]).all():
                plane.plane_position = plane.plane_position - [0, 1, 0]
            elif (plane.plane_normal == [0, 0, 1]).all():
                plane.plane_position = plane.plane_position - [0, 0, 1]
        else:
            plane.plane_position = (self.plane_start[0], self.plane_start[1], self.plane_start[2])

    def place_slice_plots(self, select_slice):
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
            # Create the volume visual for plane rendering
            plane = scene.visuals.Volume(
                self.vol,
                parent=view1.scene,
                raycasting_mode='plane',
                method='mip',
                plane_thickness=1.0,
                # plane_position=plane.plane_position,
                plane_position=self.plane_start,
                # plane_normal=plane.plane_normal,
                plane_normal=(1, 0, 0),
                cmap='jet',
                clim=clim,
            )
            volume = scene.visuals.Volume(
                self.vol,
                parent=view1.scene,
                raycasting_mode='volume',
                method='mip',
            )
            volume.set_gl_state('additive')
            volume.opacity = 0.25

            view1.camera = self.cam
            colorbar_0 = scene.visuals.ColorBar(label='Measurement in dB', label_color=label_color, cmap='jet', clim=clim, border_width=2.0, border_color='white',
                                                orientation='right', size=(500, 40), parent=view1)
            colorbar_0.label.font_size = 24
            colorbar_0.label.color = 'black'
            colorbar_0.transform = scene.STTransform(translate=(canvas_size[0] * 0.90, canvas_size[1] * 0.45, 0))

        self.colorbars = [colorbar_0]

    def replace_plot(self, select_slice):
        global view1, canvas_size #, colorbars

        if select_slice == None:
            self.place_slice_plots(None)
            self.place_slice_plots("3D")

    # Define the resize callback
    def update_colorbars(self):
        # Get the new canvas size
        canvas_size = canvas.size
        colorbar_width = 400
        colorbar_height = 30  # Scale height to 80% of canvas height

        colorbar_0.transform = scene.STTransform(translate=(canvas_size[0] * 0.9, canvas_size[1] * 0.45, 0))

    # Function to resize plot elements based on canvas size
    def on_canvas_resize(event, self):
        global slice_z, slice_y, slice_x, title_z, title_y, title_x, title_3D
        canvas_width, canvas_height = event.size
        canvas_size = [canvas_width, canvas_height]
        self.update_colorbars(self.colorbars)

    def running(self):
        import numpy as np
        from vispy import app, scene, io, visuals as vispy_vis, plot as vp
        working_dir = self.path
        save_animation = False

        with open(f"{working_dir}\\image_radar.pkl", 'rb') as file:
            # Call load method to deserialze.
            vol2 = pickle.load(file)

        intensity_matrix = vol2 ** 2
        intensity_matrix_norm = np.abs(intensity_matrix) / np.max(np.abs(intensity_matrix))
        intensity_matrix_db = 20 * np.log10(intensity_matrix_norm)

        image_matrix_3D = np.abs(vol2[:, :, :]).astype(np.float32)
        image_matrix_3D_db = intensity_matrix_db[:, :, :].astype(np.float32)

        vol2 = image_matrix_3D_db
        rearranged_vol2 = np.swapaxes(vol2, 0, 2)
        rearranged_vol2 = np.flip(rearranged_vol2, 2)
        rearranged_vol2 = np.swapaxes(rearranged_vol2, 2, 1)
        # rearranged_vol2 = np.flip(rearranged_vol2, 1)
        self.vol = rearranged_vol2
        # vol = vol2

        self.x_axis = np.linspace(self.start_x, self.end_x, self.number_of_points_x)
        self.y_axis = np.linspace(self.start_y, self.end_y, self.number_of_points_y)
        self.z_axis = np.linspace(self.start_z, self.end_z, self.number_of_points_z)

        # Prepare canvas
        canvas = scene.SceneCanvas(keys='interactive', size=(1000, 1000), show=True)
        view1 = canvas.central_widget.add_view()

        texture_format = 'auto'

        self.plane_start = (np.shape(self.vol)[0] - 1, np.shape(self.vol)[1] - 1, np.shape(self.vol)[2] - 1)

        volume = scene.visuals.Volume(
            self.vol,
            parent=view1.scene,
            raycasting_mode='volume',
            method='mip',
        )
        volume.set_gl_state('additive')
        volume.opacity = 0.25

        # Create a camera
        self.cam = scene.cameras.TurntableCamera(
            parent=view1.scene, fov=60.0, azimuth=-42.0, elevation=30.0
        )
        view1.camera = self.cam
        self.update_coordinate_system()

        # Implement key presses
        @canvas.events.key_press.connect
        def on_key_press(event):
            global canvas
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

                # update plot of specific slice
                if (plane.plane_normal == [1, 0, 0]).all():
                    select_slice = "slice_z"
                    self.replace_plot(select_slice)
                if (plane.plane_normal == [0, 1, 0]).all():
                    select_slice = "slice_y"
                    self.replace_plot(select_slice)
                if (plane.plane_normal == [0, 0, 1]).all():
                    select_slice = "slice_x"
                    self.replace_plot(select_slice)
                print(f"plane position: {plane.plane_position}")
            elif event.text == 'x':
                plane.plane_normal = [0, 0, 1]
            elif event.text == 'y':
                plane.plane_normal = [0, 1, 0]
            elif event.text == 'z':
                plane.plane_normal = [1, 0, 0]
            elif event.text == 'o':
                plane.plane_normal = [1, 1, 1]
            elif event.text == ' ':
                if self.timer.running:
                    self.timer.stop()
                    self.replace_plot("None")
                    print(f"plane position: {plane.plane_position}")
                else:
                    self.timer.start()

        timer = app.Timer('auto', connect=self.move_plane, start=True)
        shape = self.vol.shape
        colorbars = []
        canvas.events.resize.connect(self.on_canvas_resize)
        self.place_slice_plots("3D")

        if save_animation == True:
            import numpy as np
            import imageio
            from vispy import scene, app

            # Save video frames
            frames = []
            num_frames = 180  # Number of frames in the loop

            for i in range(int(num_frames / 2)):
                view1.camera.azimuth += 180 / num_frames  # Rotate camera
                canvas.update()  # Update canvas
                frame = canvas.render()  # Capture frame
                frames.append(frame)

            for i in range(int(num_frames / 2)):
                view1.camera.azimuth -= 180 / num_frames  # Rotate camera
                canvas.update()  # Update canvas
                frame = canvas.render()  # Capture frame
                frames.append(frame)

            # Save as MP4 using FFmpeg
            imageio.mimsave(f"Test.mp4", frames, format="FFMPEG", fps=30)

            # Save as GIF (Optional)
            imageio.mimsave(f"Test.gif", frames, duration=1 / 30)  # 30 FPS

            print("MP4 and GIF saved successfully!")

        if __name__ == '__main__':
            canvas.show()
            print(__doc__)
            if sys.flags.interactive == 0:
                app.run()