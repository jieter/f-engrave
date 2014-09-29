#!/bin/sh

find . -name "*.pyc" -exec rm '{}' ';'
nosetests -s tests/
