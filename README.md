# F-Engrave

This is a fork of [Scorchworks F-Engrave](http://www.scorchworks.com/Fengrave/fengrave.html) version 1.41 (2014-09-08).

# !! Please note that this code is very likely not functional at all. The tests should work though.

## Changes (being) made:

 - split(ting) into modules.
 - Decouple the Gui from the actual processing.
 - Work towards a clean, consitent coding style, by using flake.
 - Tests.

## TODOs
 - [ ] SVG export of text on circle.
 - [ ] Document settings in settings file and use longer, more descriptive names.
 - [ ] Clean up settings: support settings 'TRADIUS', 'imagefile', 'clean_paths',  'TCODE' (list of character codes for the string being engraved)
 - [ ] Compare some newly generated gcode files to the output of the f-engrave 1.41
 - [ ] Font preview


## Running tests

You need `nose` to run the tests: `(sudo) pip install nose`. Run the tests later:
```
./testrunner.sh
```
