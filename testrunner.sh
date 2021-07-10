#!/bin/sh

# clean temporary files
find ./tmp -name "*.ngc" -exec rm '{}' ';'
find ./tmp -name "*.svg" -exec rm '{}' ';'

# run the tests
find . -name "*.pyc" -exec rm '{}' ';'
nosetests -s tests/
