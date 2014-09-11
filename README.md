# F-Engrave

This is a fork of [Scorchworks F-Engrave](http://www.scorchworks.com/Fengrave/fengrave.html) version 1.41 (2014-09-08).

# !! Please note that this code is very likely not functional at all. The tests should


## Changes made:

 - split(ting) into modules.
 - Removing the carve settings from the `Application` object.
 - PEPing
 - tests

## Currently not working / TODO:
 - SVG export of text on circle.
 - Document settings in settings file and use longer, more descriptive names.
 - support settings 'TRADIUS', 'imagefile', 'clean_paths' and
   * 'TCODE': list of character codes for the string being engraved

## Running tests

You need `nose` to run the tests: `(sudo) pip install nose`. Run the tests later:
```
nosetests -s tests/
```
