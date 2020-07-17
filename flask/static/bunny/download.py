
import os
import subprocess

#if not os.path.exists('bunny.vtk'):
#    subprocess.call(['wget','https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/vtk/bunny.vtk'])
if not os.path.exists('bunny-ctscan.tar.gz'):
    subprocess.call(['wget','https://graphics.stanford.edu/data/voldata/bunny-ctscan.tar.gz'])
if not os.path.exists('bunny'):
    subprocess.call(['tar','-xzvf','bunny-ctscan.tar.gz'])

import numpy as np
import SimpleITK as sitk

if not os.path.exists('bunny.nii.gz'):

    img = np.zeros((512,512,361))
    for i in np.arange(1,362,1):
        tmp = np.fromfile(f'bunny/{i}',dtype='uint16',sep='')
        #Max 16 bit = 65535
        #Max 12 bit = 4095
        tmp = np.round(tmp/65535*4095)
        tmp = tmp.reshape(512,512)
        img[:,:,i-1]=tmp
    img = img.astype(np.uint16)

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

# downn sample !!!
if not os.path.exists('bunny.vtk'):
    import vtk

    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName('bunny.nii.gz')
    reader.Update()


    threshold = vtk.vtkImageThreshold ()
    threshold.SetInputConnection(reader.GetOutputPort())
    threshold.ThresholdByLower(2000)  #th
    threshold.ReplaceInOn()
    threshold.SetInValue(0)  # set all values below th to 0
    threshold.ReplaceOutOn()
    threshold.SetOutValue(1)  # set all values above th to 1
    threshold.Update()

    dmc = vtk.vtkDiscreteMarchingCubes()
    dmc.SetInputConnection(threshold.GetOutputPort())
    dmc.GenerateValues(1, 1, 1)
    dmc.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(dmc.GetOutputPort())
    mapper.Update()

    smooth = vtk.vtkSmoothPolyDataFilter()
    smooth.SetInputConnection(dmc.GetOutputPort())
    smooth.SetNumberOfIterations(100)
    smooth.SetRelaxationFactor(1)
    smooth.Update()

    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData(smooth.GetOutput())
    writer.SetFileName('bunny.vtk')
    writer.Write()

    '''
    writer = vtk.vtkPLYWriter()
    writer.SetInputConnection(dmc.GetOutputPort())
    writer.SetFileName('bunny.ply')
    writer.Write()

    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(dmc.GetOutputPort())
    writer.SetFileTypeToBinary()
    writer.SetFileName("bunny.stl")
    writer.Write()
    '''
#http://vtk.1045678.n5.nabble.com/How-to-write-vtkDelaunay3D-into-vtk-file-td5741818.html
#https://gist.github.com/pangyuteng/facd430d0d9761fc67fff4ff2e5fffc3
