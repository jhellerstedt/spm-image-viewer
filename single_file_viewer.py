#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 22:45:06 2016

@author: jack
"""

import core_functions as cf
cf.set_single_file_viewer_flag(True)


index_buttons = cf.row(cf.file_forward_button, cf.file_backward_button)

widgets = cf.column(
                    cf.message_text_output, 
                    cf.data_directory_text_input, 
                    cf.select_file, 
                    index_buttons, 
                    cf.select_channel, 
                    cf.fwd_bwd_button, 
                    cf.apply_filters_menu, 
                    cf.color_palette_menu, 
                    cf.update_button,
                    )
main_row = cf.row(cf.p, widgets, cf.header_display)
layout = cf.column(main_row)

### initialize

#cf.update()

cf.curdoc().add_root(layout)
cf.curdoc().title = "scan inspector"