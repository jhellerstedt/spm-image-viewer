#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 22:42:40 2016

@author: jack
"""

import core_functions as cf

cf.set_single_file_viewer_flag(False)

### set up layout

widgets = cf.column(
                    cf.message_text_output, 
                    cf.data_directory_text_input,
                    cf.refresh_directory_button,
                    cf.select_all_button, 
                    cf.grid_view_button, 
                    cf.select_channel, 
                    cf.fwd_bwd_button, 
                    cf.apply_filters_menu, 
                    cf.color_palette_menu, 
                    cf.update_resolution, 
                    cf.update_button, 
                    cf.max_slider, 
                    cf.min_slider,
                    )
main_row = cf.row(cf.select_file_CBG, cf.p, widgets)
layout = cf.column(main_row)



cf.curdoc().add_root(layout)
cf.curdoc().title = "all file viewer"