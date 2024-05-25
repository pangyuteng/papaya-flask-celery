
import os
import sys
import imageio
import numpy as np
import PIL
from moviepy import editor

import vtk
from vtk.util.colors import (
    green,
    red,
    blue,
    yellow,
    pink,
    mint,
)
light_green = (0.8,1.0,0.8)


class NiftiVisualizer(object):
    def __init__(self,image_file,mask_file,work_dir):
        self.image_file = image_file
        self.mask_file = mask_file
        self.work_dir = work_dir

    def setup_pipeline(self):
        
        maskReader = vtk.vtkNIFTIImageReader()
        maskReader.SetFileName(self.mask_file)
        maskReader.Update()

        print("GetDataDirection",maskReader.GetDataDirection())
        print("GetDataOrigin",maskReader.GetDataOrigin())
        print("GetDataSpacing",maskReader.GetDataSpacing())
        print("GetDataExtent",maskReader.GetDataExtent())
        print("----")
        mynormal = list(maskReader.GetDataDirection())[6:]
        myorigin = maskReader.GetDataOrigin()

        myPlane = vtk.vtkPlane()
        mynormal = (0,0,1)
        myPlane.SetOrigin(myorigin)
        myPlane.SetNormal(mynormal)
        print('myorigin',myorigin)        
        print('mynormal',mynormal)

        maskLut = vtk.vtkLookupTable()
        maskLut.SetValueRange(0,8)
        maskLut.SetNumberOfTableValues(9)
        maskLut.SetTableRange(0,8)
        maskLut.SetTableValue(0,0,0,0,0)
        maskLut.SetTableValue(1,1,0,0,1)
        maskLut.SetTableValue(2,0,1,0,1)
        maskLut.SetTableValue(3,0,0,1,1)
        maskLut.SetTableValue(4,1,1,0,1)
        maskLut.SetTableValue(5,0,1,1,1)
        maskLut.SetTableValue(6,1,0,1,1)
        maskLut.SetTableValue(7,0.5,0.5,0,1)
        maskLut.SetTableValue(8,0,0.5,0.5,1)

        maskLut.SetRampToLinear()
        maskLut.Build()

        maskColorMapper = vtk.vtkImageMapToColors()
        maskColorMapper.SetLookupTable(maskLut)
        maskColorMapper.SetInputConnection(maskReader.GetOutputPort())

        if False:
            print(maskColorMapper.GetLookupTable())

        maskMapper = vtk.vtkImageResliceMapper()
        maskMapper.SetSlicePlane(myPlane)
        maskMapper.SetInputConnection(maskColorMapper.GetOutputPort())

        maskSlice = vtk.vtkImageSlice()
        maskSlice.SetMapper(maskMapper)
        maskSlice.GetProperty().SetInterpolationTypeToNearest()
        maskSlice.GetProperty().SetOpacity(0.5)

        imageReader = vtk.vtkNIFTIImageReader()
        imageReader.SetFileName(self.image_file)
        imageReader.Update()
        
        imageColorMapper = vtk.vtkImageMapToWindowLevelColors()
        colorWindow = 1500 # lung window 1500 level -600
        colorLevel = -600
        imageColorMapper.SetWindow(colorWindow)
        imageColorMapper.SetLevel(colorLevel)
        imageColorMapper.SetInputConnection(imageReader.GetOutputPort())

        imageMapper = vtk.vtkImageResliceMapper()
        imageMapper.SetSlicePlane(myPlane)
        imageMapper.SetInputConnection(imageColorMapper.GetOutputPort())
        
        imageSlice = vtk.vtkImageSlice()
        imageSlice.SetMapper(imageMapper)
        imageSlice.GetProperty().SetInterpolationTypeToNearest()
        imageSlice.GetProperty().SetOpacity(1.0)
        center = imageSlice.GetCenter()
        print("center",center)

        imageStack = vtk.vtkImageStack()
        imageStack.AddImage(imageSlice)
        imageStack.AddImage(maskSlice)

    
        width,height = 512,512
        viewer = vtk.vtkImageViewer2() 
        viewer.SetInputConnection(imageReader.GetOutputPort())
        
        viewer.SetSliceOrientation(0)
        viewer.SetSlice(22)
        viewer.SetColorWindow(1500)
        viewer.SetColorLevel(-600)
        viewer.GetRenderWindow().SetSize(width,height)
        viewer.GetRenderer().SetBackground(1.0, 1.0, 1.0)
        
        viewer.GetRenderer().AddActor(maskSlice)

        renderWindow = viewer.GetRenderWindow()
        renderWindow.Render()
        self.viewer = viewer
        
        self.renderWindow = renderWindow
        self.maskReader = maskReader
        self.myPlane = myPlane
        
    def render(self,idx,myorigin,mynormal):

        self.viewer.SetSlice(idx)

        self.renderWindow.Render()
        windowToImageFilter = vtk.vtkWindowToImageFilter()
        windowToImageFilter.SetInput(self.renderWindow)
        windowToImageFilter.Update()

        writer = vtk.vtkPNGWriter()
        fpath = os.path.join(work_dir,f"ok-{idx}.png")
        writer.SetFileName(fpath)
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        writer.Write()

if __name__ == "__main__":
    
    image_file = sys.argv[1]
    mask_file = sys.argv[2]
    work_dir = sys.argv[3]
    os.makedirs(work_dir,exist_ok=True)
    inst = NiftiVisualizer(image_file,mask_file,work_dir)
    inst.setup_pipeline()
    mynormal = (0,0,1)
    inst.render(0,(0,0,0),mynormal)
    inst.render(128,(0,0,100),mynormal)
    inst.render(256,(0,0,150),mynormal)
    inst.render(512,(0,0,300),mynormal)


'''

axial, sagittal rlung, llung, coronal
no overlay
with overlay

docker run -it -u $(id -u):$(id -g) -v /mnt:/mnt \
  -w $PWD pangyuteng/dcm:latest bash

python vtkshit.py \
    /mnt/hd1/papaya-flask-celery/papaya-gii/tlc.nii.gz \
    /mnt/hd1/papaya-flask-celery/papaya-gii/merged.nii.gz tmp

'''