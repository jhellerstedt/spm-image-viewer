#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 22:56:47 2016

@author: jack
"""


import os
import numpy as np
import time

#import NanonisAFM
import nanonispy as nap

import nanonispyfit

import matplotlib.pyplot as plt
#import matplotlib.cm as cm
from matplotlib.colors import rgb2hex

from scipy.misc import imrotate, imresize

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.widgets import (
    Slider,  
    Select, 
    TextInput,  
    MultiSelect, 
    Button, 
    DataTable, 
    TableColumn, 
    CheckboxGroup, 
    Toggle
    )

##set single file viewer instance True/False
global using_single_file_viewer
using_single_file_viewer = False

def set_single_file_viewer_flag(arg):
    global using_single_file_viewer
    using_single_file_viewer = arg

### initial variable values

## default directory:
global directory
directory = os.getcwd()

global files_list, active_files_list, files_list_CBG
files_list_CBG=["none"]
files_list = []
active_files_list = []  
global chosen_file
chosen_file = "none chosen"
global channel_list
channel_list = []
global chosen_channel
chosen_channel = " "
global fwdbwdstring
fwdbwdstring = 'forward'
global header_source
header_source = ColumnDataSource(dict(first=[],second=[]))
global file_metadata_dict
file_metadata_dict = dict()
global enable_grid_view
enable_grid_view = True
global contrast_high, contrast_low, first_update, max_slider_initial, min_slider_initial
max_slider_initial = 1
min_slider_initial = 1
first_update = False
contrast_high = -1e9
contrast_low = 1e9

### populate palettes dictionary from matplotlib

palette_list = sorted(m for m in plt.cm.datad) # if not m.endswith("_r"))
## initialize colomapper variable to default of Blues_r
colormap = plt.get_cmap("Blues_r") #choose any matplotlib colormap here
bokehpalette = [rgb2hex(m) for m in colormap(np.arange(colormap.N))]
colormapper = LinearColorMapper(palette=bokehpalette, high=contrast_high, low=contrast_low)

### populate filter functions menu options

funcnames = [fn for fn in dir(nanonispyfit) if not fn.startswith('_')]
funclist = [getattr(nanonispyfit, fn) for fn in funcnames]

filter_dictionary = dict()

for name, func in zip(funcnames,funclist):
    filter_dictionary[name] = func






#### core functions/ handler functions:
    
def update():
    global chosen_file, chosen_channel, channel_list, chosen_palette, temp_nanonis, fwdbwdstring, t0
    global file_metadata_dict, enable_grid_view, active_files, active_files_dict
    global contrast_high, contrast_low, first_update, max_slider_initial, min_slider_initial
    
    
    message_text_output.value = "working ..."
    t0 = time.time()
      
    active_files = [select_file_CBG.labels[x] for x in select_file_CBG.active]

    grid = np.floor(np.sqrt(len(active_files)))

    active_files_dict = dict()
    
    for index, x in enumerate(active_files, start=0):
        
        temp = dict()
        
        temp_nanonis = file_metadata_dict[x]
        
        try:        
            if temp_nanonis.header['scan_dir'] == 'down':
                if fwdbwdstring == 'forward':
                    scan_image = np.flipud(temp_nanonis.signals[select_channel.value][fwdbwdstring])
                else:
                    scan_image = np.fliplr(np.flipud(temp_nanonis.signals[select_channel.value][fwdbwdstring]))
            else:
                if fwdbwdstring == 'forward':
                    scan_image = temp_nanonis.signals[select_channel.value][fwdbwdstring]
                else:
                    scan_image = np.fliplr(temp_nanonis.signals[select_channel.value][fwdbwdstring])
        except e:
            print(e)
            scan_image = np.zeros(temp_nanonis.header['scan_pixels'])
        
        ### remove NaNs from the image
        scan_image[np.isnan(scan_image)] = np.mean(scan_image[~np.isnan(scan_image)])
        
        ### apply filters in this for loop:
        for i in apply_filters_menu.value:
            scan_image = filter_dictionary[i](scan_image)
        
        #get the image scan angle (degrees)
        angle = -float(temp_nanonis.header['scan_angle'])
        
        #don't rotate the image if working in grid mode/ only looking at one image:
        if enable_grid_view == True or len(active_files) < 2:
            angle = 0
        
        scan_image = imrotate(scan_image,angle)
        
        temp['image'] = [scan_image]

        ##get contrast maxima
        if first_update == True:
            contrast_high = np.max(scan_image)
            contrast_low = np.min(scan_image)
            first_update = False
        else:
            if np.max(scan_image)>contrast_high:
                contrast_high = np.max(scan_image)
            if np.min(scan_image)<contrast_low:
                contrast_low = np.min(scan_image)

	 #get the image height/width
        width, height = temp_nanonis.header['scan_range']
        temp['dw'] = [width*1e9]
        temp['dh'] = [height*1e9]
                
        #get the center for the image, nm
        xc, yc = temp_nanonis.header['scan_offset']
        temp['x'] = [(xc-width/2)*1e9]
        temp['y'] = [(yc-height/2)*1e9]

        if enable_grid_view == True and len(active_files) > 1:
            temp['x'] = [125*np.mod(index,grid)]
            temp['y'] = [125*(np.floor(index/grid))]

        if len(active_files) < 2:
            temp['x'] = [0.]
            temp['y'] = [0.]
    


        if enable_grid_view == True and len(active_files) > 1:
            temp['dw'] = [100]
            temp['dh'] = [height/width*100]
        
        temp['filename'] = [x]
        active_files_dict[x] = temp
        
        t1 = time.time()
        message_text_output.value = "still working... " + str(t1-t0)
        
        
        #create duplicate rect glyphs that the hover tool works on: 

        circ_temp = dict()
        circ_temp['x'] = [temp['x'][0]+temp['dw'][0]/2]
        circ_temp['width'] = temp['dw']
        circ_temp['y'] = [temp['y'][0]+temp['dh'][0]/2]
        circ_temp['height'] = temp['dh']
        circ_temp['angle'] = [angle]
        circ_temp['filename'] = [x]

        if using_single_file_viewer == False:
            circ_data.stream(circ_temp,rollover=len(active_files))
        else:
            circ_data.stream(circ_temp,rollover=1)
    
    max_slider.start = contrast_low - .5*(contrast_high-contrast_low)
    max_slider.end = contrast_high + .5*(contrast_high-contrast_low)
    max_slider_initial = contrast_high
    max_slider.step = (max_slider.end - max_slider.start)/100

    min_slider.start = contrast_low - .5*(contrast_high-contrast_low)
    min_slider.end = contrast_high + .5*(contrast_high-contrast_low)
    min_slider_initial = contrast_low
    min_slider.step = (max_slider.end - max_slider.start)/100
    
            
    t1 = time.time()
    message_text_output.value = "chammel data is update: " + str(t1-t0)
    
    update_plot_ranges()   
    
    
def update_plot_ranges():
    global old_x_range, old_y_range, temp_nanonis
    
    if not p.x_range.start:
        message_text_output.value = "change filename for update"
        return  
   
    image_callback((p.x_range.start,p.x_range.end), (p.y_range.start, p.y_range.end), p.plot_width, p.plot_height)
    
    
    
def image_callback(x_range, y_range, w, h):
    
    
    global colormap, active_files_dict, active_files, chosen_channel
    global using_single_file_viewer, contrast_high, contrast_low
    
    message_text_output.value = "downscaling..."
    
    new_changed_files = list()
    
    try:
        unchanged_files
    except NameError:
        unchanged_files = list()
    try:
        old_channel
    except NameError:
        old_channel = select_channel.value
    
    for (key,temp) in active_files_dict.items():
        new_temp = dict()
        dont_resend = False
        if using_single_file_viewer == False:
            ## downsample the image to only push necessary pixels to plot: 
            if (temp['x'][0]-temp['dw'][0]/2 <= x_range[1] and 
                temp['x'][0]+temp['dw'][0]/2 >= x_range[0] and 
                temp['y'][0]-temp['dh'][0]/2 <= y_range[1] and 
                temp['y'][0]+temp['dh'][0]/2 >= y_range[0]):
                
                if (temp['dw'][0]<np.abs(x_range[1]-x_range[0]) and 
                    temp['dh'][0]<np.abs(y_range[1]-y_range[0])):
                    
                    xpixels = np.floor(temp['dw'][0]*w/np.abs(x_range[1]-x_range[0]))
                    ypixels = np.floor(temp['dh'][0]*h/np.abs(y_range[1]-y_range[0]))
                    if xpixels<2 and ypixels < 2:
                        xpixels, ypixels = 2,2
                    new_temp['image'] = [imresize(temp['image'][0],(int(xpixels), int(ypixels)))]
                else:
                    new_temp['image'] = temp['image']
                    if select_channel.value == old_channel:
                        if key in unchanged_files:
                            dont_resend = True
                        else:
                            new_changed_files.append(key)
            else:
                dont_resend = True
        else:
            new_temp['image'] = temp['image']
        
        unchanged_files = new_changed_files
        
        old_channel = select_channel.value

        if dont_resend == False:
            for i in list(temp.keys()):
                if i is not 'image':
                    new_temp[i] = temp[i]
            
            ds.stream(new_temp,rollover=len(active_files))
            

  
    message_text_output.value = "plot resolution is update"
    
    
    
    
    
    
    
    
def data_directory_text_handler(attr, old, new):
    global directory, files_list, chosen_file, channel_list, file_metadata_dict
    global chosen_channel, t0, files_list_CBG, using_single_file_viewer, first_update
    
    first_update = True
    
    message_text_output.value = "working ..."
    t0 = time.time()
    
    ##check if a real directory:
    if not os.path.exists(new):
        message_text_output.value = "I can't find that directory"
        return
    
    temp_files_list = os.listdir(new)
    full_list = [os.path.join(new,i) for i in temp_files_list]
    time_sorted_list = sorted(full_list, key=os.path.getmtime)
    temp_files_list = [os.path.basename(i) for i in time_sorted_list]
                       
    files_list_CBG = list()
    for i in temp_files_list:
        if i.endswith(".sxm"):
            files_list_CBG.append(i)
    select_file_CBG.labels = files_list_CBG
    select_file_CBG.active = list(range(len(files_list_CBG)))
    
    select_file.options = files_list_CBG
        
    ##read sxm images into memory:
    
    file_metadata_dict = dict()
    
    select_channel.options = []
    
    for i in files_list_CBG:
        
        filename = new + "/" + i
        file_metadata_dict[i] = nap.read.Scan(filename)
        
        for j in list(file_metadata_dict[i].signals.keys()):
            if not (j in select_channel.options):
                select_channel.options.append(j)
    
    select_channel.value = select_channel.options[0]

        
    t1 = time.time()
    message_text_output.value = "data ready: " + str(t1-t0)
    
    if using_single_file_viewer == True:
        select_file.value = select_file.options[0]
    
    update()
    
    

def select_file_handler(attr,old,new):
    global temp_nanonis, t0, header_source, first_update
    if new.endswith(".sxm") == False:
        return
    else:
        
        first_update = True
        
        message_text_output.value = "working ..."
        t0 = time.time()
        
        temp_nanonis = file_metadata_dict[new]
        
        select_channel.options = list(temp_nanonis.signals.keys())
        
        entries_list = np.array(list(temp_nanonis.header.keys()))
        entries_values = [temp_nanonis.header[x] for x in entries_list]
        header_source = ColumnDataSource(dict(first=entries_list, second=entries_values))
        header_display.source = header_source
        
        select_file_CBG.active = []

        for index, x in enumerate(select_file_CBG.labels, start=0):
            if x == new:
                select_file_CBG.active = [index]

        
        if select_channel.value in select_channel.options:
            update()
        else:
            select_channel.value = select_channel.options[0]
            update()
    
    
    
    
    

def select_palette_handler(attr,old,new):
    global colormapper
    colormap = plt.get_cmap(new) #choose any matplotlib colormap here
    bokehpalette = [rgb2hex(m) for m in colormap(np.arange(colormap.N))]
    colormapper.palette = bokehpalette
    
def fwd_bwd_handler():
    global fwdbwdstring
    if fwdbwdstring == 'forward':
        fwdbwdstring = 'backward'
    else:
        fwdbwdstring = 'forward'
    fwd_bwd_button.label = fwdbwdstring
    update()
    
def button_change_all(arg):
    if arg == False:
        select_file_CBG.active = []
    else:
        if len(select_file_CBG.labels)>0:
            select_file_CBG.active = list(np.arange(0,len(select_file_CBG.labels),1))
        else: return
        
def button_change_index(pmone):
        temp = select_file.options[np.mod(select_file.options.index(select_file.value)+pmone,len(select_file.options))]
        select_file.value = temp
        select_file_handler(" "," ",temp)
        
def grid_view_handler(arg):
    global enable_grid_view
    enable_grid_view = arg
    update()
 
    
def slider_callback_high(attr,old,new):
    global contrast_high
#    colormapper.high = np.multiply(contrast_high, new)
    colormapper.high = new
    
def slider_callback_low(attr,old,new):
    global contrast_low
#    colormapper.low = np.multiply(contrast_low, new)
    colormapper.low = new
    
def refresh_directory():
    global files_list_CBG
#    data_directory_text_handler("value", old=data_directory_text_input.value, new=data_directory_text_input.value)
    temp_files_list = os.listdir(data_directory_text_input.value)
    full_list = [os.path.join(data_directory_text_input.value,i) for i in temp_files_list]
    time_sorted_list = sorted(full_list, key=os.path.getmtime)
    temp_files_list = [os.path.basename(i) for i in time_sorted_list]
    
    select_channel.options = []
    
    for i in temp_files_list:
        if i.endswith(".sxm"):
            if not (i in files_list_CBG):
                files_list_CBG.append(i)
                filename = data_directory_text_input.value + "/" + i
                file_metadata_dict[i] = nap.read.Scan(filename)
        
                for j in list(file_metadata_dict[i].signals.keys()):
                    if not (j in select_channel.options):
                        select_channel.options.append(j)
        
    select_file_CBG.labels = files_list_CBG

    
    
    
####widgets defined here:
    
message_text_output = TextInput(title="messages displayed here:",value="nothing yet")

data_directory_text_input = TextInput(value=os.getcwd(), title="directory to read data:", width=800)

#button to update directory

refresh_directory_button = Button(label="refresh files", button_type="default")

    
#select input of which file to display

select_file_CBG = CheckboxGroup(name="Select file to display:", labels=files_list_CBG, active=active_files_list)

select_file = Select(title="Select file to display:", value="none", options=files_list_CBG)

#button for selecting all/no files

select_all_button = Toggle(label="select all/none", button_type="default",active=False)

#buttons for browsing files

file_forward_button = Button(label="next file", button_type="default", width=100)
file_backward_button = Button(label="last file", button_type="default", width=100)



#update button

update_button = Button(label="update", button_type="default")
update_resolution = Button(label="update resolution", button_type="default")

    
#select which channel to display

select_channel = Select(title="Select channel to display", value='none chosen', options=channel_list)

    
#select a color palette

color_palette_menu = Select(title="Color Palette:", value="Blues_r",options=palette_list)

# filters menu

apply_filters_menu = MultiSelect(title="Filters:", options=funcnames)

#contrast sliders

#slider_dict = dict(start=0, end=1, value=1, step=.01)

max_slider = Slider(start=.5, end=1.5, value=max_slider_initial, step=.01,
                    title="% contrast max")

min_slider = Slider(start=.5, end=1.5, value=min_slider_initial, step=.01,
                    title="% contrast min")

#button to switch between fwd/bwd scan

fwd_bwd_button = Button(label="Fwd/Bwd", button_type="default")

#button to enable grid view of images

grid_view_button = Toggle(label="enable grid view", button_type="default", active=True)


#datatable with header information of selected file

header_columns = [TableColumn(field="first",title="name"),TableColumn(field="second",title="value")]
header_display = DataTable(source=header_source, columns=header_columns, fit_columns=True)







### set up callbacks

##all_image

data_directory_text_input.on_change("value", data_directory_text_handler)

refresh_directory_button.on_click(refresh_directory)

#select_channel.on_change('value', select_channel_handler)

color_palette_menu.on_change('value', select_palette_handler)

fwd_bwd_button.on_click(fwd_bwd_handler)

select_all_button.on_click(button_change_all)

grid_view_button.on_click(grid_view_handler)

update_button.on_click(update)

update_resolution.on_click(update_plot_ranges)

max_slider.on_change("value", slider_callback_high)
min_slider.on_change("value", slider_callback_low)

## single image viewer

select_file.on_change('value',select_file_handler)

file_forward_button.on_click(lambda: button_change_index(1))
file_backward_button.on_click(lambda: button_change_index(-1))





### set up plots

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"

p = figure(tools=TOOLS, webgl=True) # , lod_factor=16, lod_threshold=10

r = p.image(image=[],x=[], y=[], dw=[], dh=[], color_mapper=colormapper)
r_circ = p.rect(x=[],y=[], width=[], height=[], angle=[], alpha=0)


ds = r.data_source
ds.add([],name='filename')

## add glyphs for hover tool with filename (can't hover over images)
circ_data = r_circ.data_source
circ_data.add([],name='filename')


p.add_tools(HoverTool(tooltips=[("index", "$index"),("filename","@filename")]))

