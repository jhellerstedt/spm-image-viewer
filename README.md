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
