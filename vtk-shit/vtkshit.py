
import os
import sys
import numpy as np
import vtk
from jinja2 import Environment

import imageio
import PIL
from moviepy import editor

class NiftiVisualizer(object):
    def __init__(self,image_file,mask_file,work_dir):
        self.image_file = image_file
        self.mask_file = mask_file
        self.work_dir = work_dir
        self.colorWindow = 1500 # lung window 1500 level -600
        self.colorLevel = -600
        self.maskOpacity = 0.5
        self.imageOpacity = 1.0
        self.width = 1000
        self.height = 1000
        self.background = (1.0, 1.0, 1.0)

    def setup_pipeline(self):
        
        maskReader = vtk.vtkNIFTIImageReader()
        maskReader.SetFileName(self.mask_file)
        maskReader.Update()

        myPlane = vtk.vtkPlane()
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
        maskSlice.GetProperty().SetOpacity(self.maskOpacity)

        imageReader = vtk.vtkNIFTIImageReader()
        imageReader.SetFileName(self.image_file)
        imageReader.Update()

        imageColorMapper = vtk.vtkImageMapToWindowLevelColors()
        imageColorMapper.SetWindow(self.colorWindow)
        imageColorMapper.SetLevel(self.colorLevel)
        imageColorMapper.SetInputConnection(imageReader.GetOutputPort())

        imageMapper = vtk.vtkImageResliceMapper()
        imageMapper.SetSlicePlane(myPlane)
        imageMapper.SetInputConnection(imageColorMapper.GetOutputPort())
        
        imageSlice = vtk.vtkImageSlice()
        imageSlice.SetMapper(imageMapper)
        imageSlice.GetProperty().SetInterpolationTypeToNearest()
        imageSlice.GetProperty().SetOpacity(self.imageOpacity)

        imageStack = vtk.vtkImageStack()
        imageStack.AddImage(imageSlice)
        imageStack.AddImage(maskSlice)


        renderer = vtk.vtkRenderer()
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(self.width,self.height)

        renderWindow.SetOffScreenRendering(1)
        renderWindow.AddRenderer(renderer)

        renderer.AddActor(imageStack)

        renderer.SetBackground(self.background)

        camera = renderer.MakeCamera()
        renderer.SetActiveCamera(camera)
        if False:
            print("GetViewUp",camera.GetViewUp())
            print("GetPosition",camera.GetPosition())
            print("GetFocalPoint",camera.GetFocalPoint())
            print("GetSize",renderWindow.GetSize())
            print("GetScreenSize",renderWindow.GetScreenSize())

        renderWindow.Render()
        self.camera = camera
        self.renderWindow = renderWindow
        self.myPlane = myPlane
        self.imageSlice = imageSlice
        self.maskSlice = maskSlice
        self.maskReader = maskReader
        self.imageReader = imageReader

    def render(self,sliceOrientation,sliceIndex):

        extent = np.array(self.maskReader.GetDataSpacing())
        spacing = np.array(self.maskReader.GetDataSpacing())
        origin = np.array(self.maskReader.GetDataOrigin())
        direction = np.array(self.maskReader.GetDataDirection())
        center = np.array(self.imageSlice.GetCenter())
        positionOffset = 1000
        if sliceOrientation == 0:
            sliceNormal = direction[0:3]
            viewup = direction[6:]
        elif sliceOrientation == 1:
            sliceNormal = direction[3:6]
            viewup = direction[6:]
        elif sliceOrientation == 2:
            sliceNormal = direction[6:]
            viewup = direction[3:6]
            viewup = viewup*-1

        #
        # scene location for `vtkImageSlice` is fixed
        # reslicing via `vtkImageResliceMapper` sets other slices to be invisible
        # thus making slice of interest visible
        # therefore, we need to change camera position and focalpoint 
        # so renderwindow have a fixed size of the resizsed image.
        #
        sliceOrigin = origin+sliceNormal*spacing*sliceIndex
        self.myPlane.SetOrigin(sliceOrigin)
        self.myPlane.SetNormal(sliceNormal)

        self.imageSlice.Update()
        self.maskSlice.Update()

        positionOffset = 1000
        if sliceOrientation == 0:
            position = sliceOrigin[0]+positionOffset,center[1],center[2]
            focalPoint = (sliceOrigin[0],center[1],center[2])
        elif sliceOrientation == 1:
            position = center[0],sliceOrigin[1]+positionOffset,center[2]
            focalPoint = (center[0],sliceOrigin[1],center[2])
        elif sliceOrientation == 2:
            position = center[0],center[1],sliceOrigin[2]+positionOffset
            focalPoint = (center[0],center[1],sliceOrigin[2])
        
        self.camera.SetViewUp(viewup)
        self.camera.SetPosition(position)
        self.camera.SetFocalPoint(focalPoint)

        self.renderWindow.Render()
        if False:
            center = self.imageSlice.GetCenter()
            print(viewup,center,position,focalPoint)

        windowToImageFilter = vtk.vtkWindowToImageFilter()
        windowToImageFilter.SetInput(self.renderWindow)
        windowToImageFilter.Update()

        writer = vtk.vtkPNGWriter()
        png_file = os.path.join(work_dir,f"ok-{sliceOrientation}-{sliceIndex}.png")
        writer.SetFileName(png_file)
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        writer.Write()
        return os.path.basename(png_file)

HTML = """
<html>
<head>
</head>
<body>
{% for png_file in png_list %}
<img src="{{ png_file }}"><br>
{{png_file}}<br>
{% endfor %}
</body>
</html>
"""


if __name__ == "__main__":
    
    image_file = sys.argv[1]
    mask_file = sys.argv[2]
    work_dir = sys.argv[3]

    os.makedirs(work_dir,exist_ok=True)

    inst = NiftiVisualizer(image_file,mask_file,work_dir)
    inst.setup_pipeline()

    png_list = []
    for x in range(3):
        sliceMaxArr = inst.maskReader.GetDataExtent()[1::2]
        sliceMax = sliceMaxArr[x]
        for y in np.linspace(0,sliceMax,20):
            png_file = inst.render(x,int(y))
            png_list.append(png_file)

    html_file = os.path.join(work_dir,'test.html')
    with open(html_file,'w') as f:
        content = Environment().from_string(HTML).render(png_list=png_list)
        f.write(content)

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