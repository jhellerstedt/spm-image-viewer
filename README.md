# spm-image-viewer
python/bokeh based spm image viewer

this is for viewing directories of sxm files simultaneously in real space

install anaconda because it comes with bokeh:
http://bokeh.pydata.org/en/latest/

install "nanonispy" library:
https://github.com/underchemist/nanonispy

invoke a bokeh server using either "all_file_viewer" or "single_file_viewer":

from your terminal:
-> bokeh serve --show all_file all_file_viewer.py

or, as another example:
-> bokeh serve --port 5007 single_file_viewer.py --log-level=debug

all_file_viewer and single_file_viewer are just two instances of invoking the "widgets" and functionality assembled in "core_functions".  

"nanonispyfit" contains fitting functions that can be applied to entire images; functions defined there are auto-populated into the all_file_viewer and single_file_viewer gui instances.
