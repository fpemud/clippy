#!/bin/bash

FILES="./clippy"
FILES="${FILES} $(find ./lib -name '*.py' | tr '\n' ' ')"

autopep8 -ia --ignore=E501 ${FILES}
