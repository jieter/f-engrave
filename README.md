# OOF-Engrave

This is a fork of [jieter/f-engrave](https://github.com/jieter/f-engrave) (2015)
which in turn was a fork of [Scorchworks F-Engrave](http://www.scorchworks.com/Fengrave/fengrave.html) version 1.41 (2014-09-08).

Refactored the original code to get a better understanding of it. As often in life, one action led to another. Hence this fork of Jieter's code.
The repo name was changed into OOF-Engrave to avoid confusion with the original. This after having consulted Scorch, the F-Engrave author.

## Changes (being) made
 - aligned with F-Engrave version 1.65 (2017)
 - split into modules
 - decoupled the GUI from the actual processing
 - automated testing (using [nose](http://pythontesting.net/framework/nose/nose-introduction))
 - work towards a clean, consistent coding style (using [flake](http://flake8.pycqa.org/en/latest/user/index.html))
 - document settings in settings file and use longer, more descriptive names.
 
## TODO's
 - Circle around
 - Fix newlines in text in .ngc comments
 - Clean up settings: support settings 'TRADIUS', 'imagefile', 'clean_paths',  'TCODE' (list of character codes for the string being engraved)
 - Testing:
 	- Compare some newly generated gcode files to the output of F-Engrave 1.65
 	- More coverage on geometry functions
 - GUI
 	- Font preview
 	- settings with documentation

## Running tests

You need `nose` to run the tests: `(sudo) pip install nose`. On OS X, install with macports: `sudo port install py-nose py-flake8`.
Run the tests later:
```
./testrunner.sh
```
