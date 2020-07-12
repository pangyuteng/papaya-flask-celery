
import os
import subprocess

if not os.path.exists('bunny.vtk'):
    subprocess.call(['wget','https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/vtk/bunny.vtk'])
if not os.path.exists('bunny-ctscan.tar.gz'):
    subprocess.call(['wget','https://graphics.stanford.edu/data/voldata/bunny-ctscan.tar.gz'])
if not os.path.exists('bunny'):
    subprocess.call(['tar','-xzvf','bunny-ctscan.tar.gz'])

import numpy as np
import SimpleITK as sitk

if not os.path.exists('bunny.nii.gz'):

    img = np.zeros((512,512,361))
    for i in np.arange(1,362,1):
        tmp = np.fromfile(f'bunny/{i}',dtype='int16',sep='')
        tmp = tmp.reshape(512,512)
        img[:,:,i-1]=tmp
    img = img.astype(np.int16)

    image = sitk.GetImageFromArray(img)

    direction = (0,1,0,1,0,0,0,0,1)
    origin = (0,0,1)
    spacing = (1,1,1)

    image.SetSpacing(spacing)
    image.SetOrigin(origin)
    image.SetDirection(direction)

    writer = sitk.ImageFileWriter()
    writer.SetFileName('bunny.nii.gz')
    writer.SetUseCompression(True)
    writer.Execute(image)

