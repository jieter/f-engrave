# F-Engrave

This is a fork of [Scorchworks F-Engrave](http://www.scorchworks.com/Fengrave/fengrave.html) version 1.41 (2014-09-08).

# !! Please note that this code is very likely not functional at all. The tests should work though.

## Changes (being) made:

 - split(ting) into modules.
 - Decouple the GUI from the actual processing.
 - Work towards a clean, consitent coding style, by using flake.
 - Tests.

## TODOs
 - Fix text on radius
 	- SVG export
 	- Circle around

 - Fix newlines in text in .ngc comments
 - Document settings in settings file and use longer, more descriptive names.
 - Clean up settings: support settings 'TRADIUS', 'imagefile', 'clean_paths',  'TCODE' (list of character codes for the string being engraved)
 - Testing:
 	- Compare some newly generated gcode files to the output of the f-engrave 1.41
 	- More coverage on geometry functions
 - TTF importing
 - Batch processing
 - GUI
 	- Font preview
 	- settings with documentation



## Running tests

You need `nose` to run the tests: `(sudo) pip install nose`. Run the tests later:
```
./testrunner.sh
```
