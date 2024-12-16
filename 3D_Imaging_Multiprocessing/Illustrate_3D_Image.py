import pickle
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import animation
import os

current_dir = os.path.dirname(__file__)
current_dir = f"{current_dir}\\Test-3D"

#Define dynamic range
dynamic_range = 30

#Define settings
save_cuts = True
save_animation = False
z_cut = False
x_cut = False
y_cut = True

with open(r"{0}\Final_3D_Files\final_3D_image.pkl".format(current_dir), 'rb') as file: 
            
       image = pickle.load(file) 

with open(r"{0}\Final_3D_Files\x_axis.pkl".format(current_dir), 'rb') as file: 
            
       x_axis = pickle.load(file) 

with open(r"{0}\Final_3D_Files\y_axis.pkl".format(current_dir), 'rb') as file: 
            
       y_axis = pickle.load(file) 

with open(r"{0}\Final_3D_Files\z_axis.pkl".format(current_dir), 'rb') as file: 
            
       z_axis = pickle.load(file) 

#Normalize image
image_power = image**2
image_norm = image_power/np.max(np.abs(image_power))

#Calculate ticks
start_x = x_axis[0]
end_x = x_axis[len(x_axis)-1]

start_y = y_axis[0]
end_y = y_axis[len(y_axis)-1]

start_z = z_axis[0]
end_z = z_axis[len(z_axis)-1]

x_ticks = np.flip(np.round(np.linspace(start_x, end_x, int(np.round((np.abs(end_x)+np.abs(start_x))/4,0)+1)),1))
x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x)+np.abs(start_x))/4,0)+1))

y_ticks = (np.round(np.linspace(start_y, end_y, int(np.round((np.abs(end_y)-np.abs(start_y))/4,0)+1)),1))
y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y)-np.abs(start_y))/4,0)+1))

z_ticks = (np.round(np.linspace(start_z, end_z, int(np.round(((end_z)-(start_z))/4,0)+1)),1))
z_ticks_location = np.linspace(0, len(z_axis), int(np.round(((end_z)-(start_z))/4,0)+1))

fig = plt.figure()
fig.figsize=(20,20)

size_setting = 10

if y_cut == True:

    if save_cuts == True:
        
        for index in range(0, len(y_axis)):
            print(index)

            filepath = r'{0}\Final_3D_Files\Cuts\y_{1}_cm.png'.format(current_dir,np.round(y_axis[index],2))
            
            if os.path.exists(filepath):
                os.remove(filepath)
            
            fig = plt.figure()
            fig.figsize=(20,20)
            
            slice_image = image_norm[index,:,:]
            ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=True, vmax = 0, vmin = -dynamic_range, cmap = 'jet',cbar_kws={'label': 'Normalized Amplitude (dB)'})
            ax.set_yticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
            ax.set_xticks(z_ticks_location, z_ticks, fontsize = size_setting) 
            ax.set_ylabel("x (cm)", fontsize = size_setting)
            ax.set_xlabel("z (cm)", fontsize = size_setting)
            ax.invert_yaxis()
            ax.set_title("y = {} cm".format(np.round(y_axis[index],2)), fontsize = size_setting, x=0.45, y=1)
            fig.set_tight_layout(True)
            plt.savefig(filepath, format="png")
            plt.clf()
            plt.cla()
            plt.close('all')


    def init():

        slice_image = image_norm[0,:,:]

        size_setting = 10

        ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=True, vmax = 0, vmin = -dynamic_range, cmap = 'jet',cbar_kws={'label': 'Normalized Amplitude (dB)'})
        ax.set_yticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
        ax.set_xticks(z_ticks_location, z_ticks, fontsize = size_setting) 
        ax.set_ylabel("x (cm)", fontsize = size_setting)
        ax.set_xlabel("z (cm)", fontsize = size_setting)
        ax.invert_yaxis()
        ax.set_title("y = {} cm".format(np.round(y_axis[0],2)), fontsize = size_setting, x=0.45, y=1)
        
        
    def animate(i):
        
        print(i)
        
        size_setting = 10
        
        slice_image = image_norm[i,:,:]
        ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=False, vmax = 0, vmin = -dynamic_range, cmap = 'jet')
        ax.set_yticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
        ax.set_xticks(z_ticks_location, z_ticks, fontsize = size_setting) 
        ax.set_ylabel("x (cm)", fontsize = size_setting)
        ax.set_xlabel("z (cm)", fontsize = size_setting)
        ax.invert_yaxis()
        ax.set_title("y = {} cm".format(np.round(y_axis[i],2)), fontsize = size_setting, x=0.45, y=1)

    if save_animation == True:

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(z_axis), repeat = False)

        fig.set_tight_layout(True)

        savefile = r"{0}\Final_3D_Files\y-Cut.gif".format(current_dir)
        pillowwriter = animation.PillowWriter(fps=5)
        anim.save(savefile, writer=pillowwriter)

if z_cut == True:

    if save_cuts == True:
        
        for index in range(0, len(z_axis)):
            print(index)

            filepath = r'{0}\Final_3D_Files\Cuts\z_{1}_cm.png'.format(current_dir,np.round(z_axis[index],2))
            
            if os.path.exists(filepath):
                os.remove(filepath)
            
            fig = plt.figure()
            fig.figsize=(20,20)
            
            slice_image = image_norm[:,:,index]
            ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=True, vmax = 0, vmin = -dynamic_range, cmap = 'jet',cbar_kws={'label': 'Normalized Amplitude (dB)'})
            ax.set_xticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
            ax.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
            ax.set_xlabel("x (cm)", fontsize = size_setting)
            ax.set_ylabel("y (cm)", fontsize = size_setting)
            ax.invert_yaxis()
            ax.set_title("z = {} cm".format(np.round(z_axis[index],2)), fontsize = size_setting, x=0.45, y=1)
            fig.set_tight_layout(True)
            plt.savefig(filepath, format="png")
            plt.clf()
            plt.cla()
            plt.close('all')


    def init():

        slice_image = image_norm[:,:,0]

        size_setting = 10

        ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=True, vmax = 0, vmin = -dynamic_range, cmap = 'jet',cbar_kws={'label': 'Normalized Amplitude (dB)'})
        ax.set_xticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
        ax.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
        ax.set_xlabel("x (cm)", fontsize = size_setting)
        ax.set_ylabel("y (cm)", fontsize = size_setting)
        ax.invert_yaxis()
        
        
    def animate(i):
        
        print(i)
        
        size_setting = 10
        
        slice_image = image_norm[:,:,i]
        ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=False, vmax = 0, vmin = -dynamic_range, cmap = 'jet')
        ax.set_xticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
        ax.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
        ax.set_xlabel("x (cm)", fontsize = size_setting)
        ax.set_ylabel("y (cm)", fontsize = size_setting)
        ax.invert_yaxis()
        
        ax.set_title("z = {} cm".format(np.round(z_axis[i],2)), fontsize = size_setting, x=0.45, y=1)

    if save_animation == True:

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(z_axis), repeat = False)

        fig.set_tight_layout(True)

        savefile = r"{0}\Final_3D_Files\z-Cut.gif".format(current_dir)
        pillowwriter = animation.PillowWriter(fps=5)
        anim.save(savefile, writer=pillowwriter)

if x_cut == True:

    if save_cuts == True:
        
        for index in range(0, len(x_axis)):
            print(index)

            filepath = r'{0}\Final_3D_Files\Cuts\x_{1}_cm.png'.format(current_dir,np.round(x_axis[index],2))
            
            if os.path.exists(filepath):
                os.remove(filepath)
            
            fig = plt.figure()
            fig.figsize=(20,20)
            
            slice_image = image_norm[:,index,:]
            ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=True, vmax = 0, vmin = -dynamic_range, cmap = 'jet',cbar_kws={'label': 'Normalized Amplitude (dB)'})
            ax.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
            ax.set_xticks(z_ticks_location, z_ticks, fontsize = size_setting) 
            ax.set_ylabel("y (cm)", fontsize = size_setting)
            ax.set_xlabel("z (cm)", fontsize = size_setting)
            ax.invert_yaxis()
            ax.set_title("x = {} cm".format(np.round(x_axis[index],2)), fontsize = size_setting, x=0.45, y=1)
            fig.set_tight_layout(True)
            plt.savefig(filepath, format="png")
            plt.clf()
            plt.cla()
            plt.close('all')


    def init():

        slice_image = image_norm[:,0,:]

        size_setting = 10

        ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=True, vmax = 0, vmin = -dynamic_range, cmap = 'jet',cbar_kws={'label': 'Normalized Amplitude (dB)'})
        ax.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
        ax.set_xticks(z_ticks_location, z_ticks, fontsize = size_setting) 
        ax.set_ylabel("y (cm)", fontsize = size_setting)
        ax.set_xlabel("z (cm)", fontsize = size_setting)
        ax.invert_yaxis()
        
        
    def animate(i):
        
        print(i)
        size_setting = 10
        slice_image = image_norm[:,i,:]
        ax = sns.heatmap(10*np.log10(np.abs(slice_image)), square=True, cbar=False, vmax = 0, vmin = -dynamic_range, cmap = 'jet')
        ax.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
        ax.set_xticks(z_ticks_location, z_ticks, fontsize = size_setting) 
        ax.set_ylabel("y (cm)", fontsize = size_setting)
        ax.set_xlabel("z (cm)", fontsize = size_setting)
        ax.invert_yaxis()
        ax.set_title("x = {} cm".format(np.round(x_axis[i],2)), fontsize = size_setting, x=0.45, y=1)

    if save_animation == True:

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(z_axis), repeat = False)

        fig.set_tight_layout(True)

        savefile = r"{0}\Final_3D_Files\x-Cut.gif".format(current_dir)
        pillowwriter = animation.PillowWriter(fps=5)
        anim.save(savefile, writer=pillowwriter)