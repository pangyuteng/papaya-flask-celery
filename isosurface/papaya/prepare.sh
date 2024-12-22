#!/bin/bash

wget https://github.com/jonclayden/RNifti/raw/master/inst/extdata/example.nii.gz -O static/example.nii.gz
python nii2iso.py