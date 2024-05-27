
import os
import sys
import numpy as np
import vtk
from jinja2 import Environment

import pdfkit
import PIL
from moviepy import editor

HTML_TEMPLATE = """
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
        self.maskLut = None
        self.setup_mask_lut()
        
    def setup_mask_lut(self,maskLut=None):
        if maskLut is None:
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
        self.maskLut = maskLut

    def gen_isosurface(self,animation=False):

        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(self.mask_file)
        reader.Update()


        threshold = vtk.vtkImageThreshold()
        threshold.SetInputConnection(reader.GetOutputPort())
        threshold.ThresholdBetween(1,8)
        threshold.ReplaceInOn()
        threshold.SetInValue(1)
        threshold.ReplaceOutOn()
        threshold.SetOutValue(0)
        threshold.Update()

        dmc = vtk.vtkDiscreteMarchingCubes()
        dmc.SetInputConnection(threshold.GetOutputPort())
        dmc.GenerateValues(1, 1, 1)
        dmc.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(dmc.GetOutputPort())
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        mapper.ScalarVisibilityOff()
        actor.GetProperty().SetColor((1,1,1))
        actor.GetProperty().SetOpacity(1)
        actor.RotateX(270)
        center = actor.GetCenter()
        
        opq_val = 0.5
        mapper = [
            (1,(1,0,0),opq_val,'1'),
            (2,(0,1,0),opq_val,'2'),
            (3,(0,0,1),opq_val,'3'),
            (4,(1,1,0),opq_val,'4'),
            (5,(0,1,1),opq_val,'5'),
            (6,(1,0,1),opq_val,'6'),
            (7,(0.5,0.5,0),opq_val,'7'),
            (8,(0,0.5,0.5),opq_val,'8'),
        ]
        
        mylist = []
        for int_val,color,opacity,abbrv in mapper:

            threshold = vtk.vtkImageThreshold()
            threshold.SetInputConnection(reader.GetOutputPort())
            threshold.ThresholdBetween(int_val,int_val)
            threshold.ReplaceInOn()
            threshold.SetInValue(0)
            threshold.ReplaceOutOn()
            threshold.SetOutValue(1)
            threshold.Update()

            dmc = vtk.vtkDiscreteMarchingCubes()
            dmc.SetInputConnection(threshold.GetOutputPort())
            dmc.GenerateValues(1, 1, 1)
            dmc.Update()

            smoothing_iterations = 15
            pass_band = 0.001
            feature_angle = 120.0
                
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(dmc.GetOutputPort())
            mapper.Update()

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            mapper.ScalarVisibilityOff()

            actor.GetProperty().SetColor(color)
            actor.GetProperty().SetOpacity(opacity)
            actor.RotateX(270)
            mylist.append(actor)
        
        renderer = vtk.vtkRenderer()
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(self.width,self.height)

        renderWindow.SetOffScreenRendering(1)
        renderWindow.AddRenderer(renderer)

        for actor in mylist:
            renderer.AddActor(actor)

        renderer.SetBackground(self.background)

        camera = renderer.MakeCamera()
        camera.SetPosition(0,0,800)
        camera.SetFocalPoint(center)

        renderer.SetActiveCamera(camera)
        renderWindow.Render()

        print(renderWindow.GetScreenSize())

        focal_point = camera.GetFocalPoint()
        view_up = camera.GetViewUp()
        position = camera.GetPosition() 

        axis = [0,0,0]
        axis[0] = -1*camera.GetViewTransformMatrix().GetElement(0,0)
        axis[1] = -1*camera.GetViewTransformMatrix().GetElement(0,1)
        axis[2] = -1*camera.GetViewTransformMatrix().GetElement(0,2)

        frame_list = []
        for n,q in enumerate([10]*35):

            transform = vtk.vtkTransform()
            transform.Identity()

            transform.Translate(*center)
            transform.RotateWXYZ(q,view_up)
            transform.RotateWXYZ(0,axis)
            transform.Translate(*[-1*x for x in center])

            new_position = [0,0,0]
            new_focal_point = [0,0,0]
            transform.TransformPoint(position,new_position)
            transform.TransformPoint(focal_point,new_focal_point)

            camera.SetPosition(new_position)
            camera.SetFocalPoint(new_focal_point)

            focal_point = camera.GetFocalPoint()
            view_up = camera.GetViewUp()
            position = camera.GetPosition() 

            camera.OrthogonalizeViewUp()
            renderer.ResetCameraClippingRange()
            
            renderWindow.Render()
            windowToImageFilter = vtk.vtkWindowToImageFilter()
            windowToImageFilter.SetInput(renderWindow)
            windowToImageFilter.Update()

            writer = vtk.vtkPNGWriter()
            
            png_file = os.path.join(self.work_dir,f"isosurface-{n}.png")
            png_file = os.path.abspath(png_file)
            writer.SetFileName(png_file)
            writer.SetInputConnection(windowToImageFilter.GetOutputPort())
            writer.Write()

            frame_list.append(png_file)
            if animation is False and n > 0:
                break

        if animation is False:
            return frame_list

        looped_frame_list = []
        loop_count = 3
        for _ in range(loop_count):
            for n,png_file in enumerate(frame_list):
                looped_frame_list.append(png_file)

        duration = 5*loop_count
        fps = 7
        time_list = list(np.arange(0,duration,1./fps))
        img_dict = {a:f for a,f in zip(time_list,looped_frame_list)}

        def make_frame(t):
            fpath= img_dict[t]
            im = PIL.Image.open(fpath)
            arr = np.asarray(im)
            return arr

        gif_path = os.path.join(work_dir,f'ani.gif')
        video_file = os.path.join(work_dir,f"ani.mp4")
        clip = editor.VideoClip(make_frame, duration=duration)
        clip.write_gif(gif_path, fps=fps)
        clip.write_videofile(video_file, fps=fps)

    def setup_2d_slices_pipeline(self):
        
        maskReader = vtk.vtkNIFTIImageReader()
        maskReader.SetFileName(self.mask_file)
        maskReader.Update()

        myPlane = vtk.vtkPlane()

        maskColorMapper = vtk.vtkImageMapToColors()
        maskColorMapper.SetLookupTable(self.maskLut)
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

    def render_2d_slices(self,sliceOrientation,sliceIndex):

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
        return os.path.abspath(png_file)

    def gen_pdf(self):

        iso_file_list = self.gen_isosurface()
        self.setup_2d_slices_pipeline()

        png_dict = {}
        for x in range(3):
            sliceMaxArr = self.maskReader.GetDataExtent()[1::2]
            sliceMax = sliceMaxArr[x]
            png_dict[x]=[]
            for y in np.linspace(0,sliceMax,5):
                png_file = self.render_2d_slices(x,int(y))
                png_dict[x].append(png_file)

        png_list = []
        png_list.append(iso_file_list[0]) # iso
        png_list.append(png_dict[0][1]) # sagittal
        png_list.append(png_dict[0][3]) # sagittal
        png_list.append(png_dict[1][2]) # coronal
        png_list.append(png_dict[2][2]) # axial

        html_file = os.path.join(self.work_dir,'test.html')
        pdf_file = os.path.join(self.work_dir,'test.pdf')

        with open(html_file,'w') as f:
            content = Environment().from_string(HTML_TEMPLATE).render(png_list=png_list)
            f.write(content)
        
        options = {'enable-local-file-access': None}
        pdfkit.from_file(html_file, pdf_file, options=options)


if __name__ == "__main__":
    
    image_file = sys.argv[1]
    mask_file = sys.argv[2]
    work_dir = sys.argv[3]

    os.makedirs(work_dir,exist_ok=True)

    inst = NiftiVisualizer(image_file,mask_file,work_dir)
    inst.gen_pdf()

'''

docker run -it -u $(id -u):$(id -g) -v /mnt:/mnt \
  -w $PWD pangyuteng/dcm:latest bash

python vtk_utils.py \
    /mnt/hd1/papaya-flask-celery/papaya-gii/tlc.nii.gz \
    /mnt/hd1/papaya-flask-celery/papaya-gii/merged.nii.gz tmp

'''