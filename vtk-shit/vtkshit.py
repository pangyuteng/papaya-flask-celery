
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

'''
def gen_frames(nifti_file,width,height,prefix):

    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(nifti_file)
    reader.Update()

    threshold = vtk.vtkImageThreshold()
    threshold.SetInputConnection(reader.GetOutputPort())
    threshold.ThresholdBetween(1,5)
    threshold.ReplaceInOn()
    threshold.SetInValue(0)
    threshold.ReplaceOutOn()
    threshold.SetOutValue(1)
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

    actor.GetProperty().SetColor(green)
    actor.GetProperty().SetOpacity(1)
    actor.RotateX(270)

    center = actor.GetCenter()
    print(center)

    opq_val_1 = 0.5

    mapper = [
        (1,light_green,opq_val_1,'BV5'),
        (2,blue,opq_val_1,'BV5-10'),
        (3,yellow,opq_val_1,'BV10'),
    ]
    mylist = []
    for int_val,color,opacity,abbrv in mapper:
        print(abbrv,int_val,color,opacity)

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
        
        # https://gist.github.com/pangyuteng/0493816e0398cdb59fde48a946745b31
        # https://examples.vtk.org/site/Python/Meshes/Decimation/
        writer = vtk.vtkSTLWriter()
        if False:
            if abbrv in ['NL','FB','GG','HC','CONS']:
                reduction = 0.9
                decimate = vtk.vtkDecimatePro()
                decimate.SetInputConnection(dmc.GetOutputPort())
                decimate.SetTargetReduction(reduction)
                decimate.PreserveTopologyOn()
                decimate.Update()
                writer.SetInputConnection(decimate.GetOutputPort())
            else:
                writer.SetInputConnection(dmc.GetOutputPort())
            writer.SetFileTypeToBinary()
            writer.SetFileName(f"{prefix}-{abbrv}.stl")
            writer.Write()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        mapper.ScalarVisibilityOff()

        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(opacity)
        actor.RotateX(270)
        mylist.append(actor)

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(width,height)

    renderWindow.SetOffScreenRendering(1)
    renderWindow.AddRenderer(renderer)

    for actor in mylist:
        renderer.AddActor(actor)

    renderer.SetBackground(1.0, 1.0, 1.0)

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

    print(position,focal_point,view_up,)

    print(camera.GetViewTransformMatrix())
    print(camera.GetViewTransformMatrix().GetElement(0,0))
    print(camera.GetViewTransformMatrix().GetElement(0,1))
    print(camera.GetViewTransformMatrix().GetElement(0,2))

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
        
        fpath = f"tmp/{prefix}-isosurface-{n}.png"
        writer.SetFileName(fpath)
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        writer.Write()

        frame_list.append(fpath)
    return frame_list


def main(baseline_nifti_file,output_folder,prefix):

    gif_path = os.path.join(output_folder,f'{prefix}-ani.gif')
    video_file = os.path.join(output_folder,f"{prefix}-movie.mp4")

    width, height = 1080,1080
    usecache = False
    if usecache:
        baseline_frame_list = []
        for n,q in enumerate([10]*35):
            fpath = f"tmp/{prefix}-isosurface-{n}.png"
            baseline_frame_list.append(fpath)
    else:
        baseline_frame_list = gen_frames(baseline_nifti_file,width,height,f'{prefix}')

    frame_list = []
    loop_count = 3
    for _ in range(loop_count):
        for n,png_file in enumerate(baseline_frame_list):
            frame_list.append(png_file)

    duration = 5*loop_count
    fps = 7
    time_list = list(np.arange(0,duration,1./fps))
    img_dict = {a:f for a,f in zip(time_list,frame_list)}

    def make_frame(t):
        fpath= img_dict[t]
        im = PIL.Image.open(fpath)
        arr = np.asarray(im)
        return arr

    clip = editor.VideoClip(make_frame, duration=duration)
    clip.write_gif(gif_path, fps=fps)
    clip.write_videofile(video_file, fps=fps)
'''

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
        self.maskReader = maskReader
        self.imageReader = imageReader

    def render(self,sliceOrientation,sliceIndex):
        """
        print(sliceOrientation,'----')
        print(dir(self.maskReader))
        
        print("GetDataDirection",self.maskReader.GetDataDirection())
        print("GetDataOrigin",self.maskReader.GetDataOrigin())
        print("GetDataSpacing",self.maskReader.GetDataSpacing())
        print("GetDataExtent",self.maskReader.GetDataExtent())
        print("GetInformation",self.maskReader.GetInformation())
        #print("center",center)
        """
        positionOffset = 0
        if sliceOrientation == 0:
            mynormal = list(self.maskReader.GetDataDirection())[0:3]
            myorigin = np.array(self.maskReader.GetDataOrigin())+np.array(mynormal)*sliceIndex
            center = self.imageSlice.GetCenter()
            viewup = list(self.maskReader.GetDataDirection())[6:]
            position = myorigin[0]+positionOffset,center[1],center[2]
        elif sliceOrientation == 1:
            mynormal = list(self.maskReader.GetDataDirection())[3:6]
            myorigin = np.array(self.maskReader.GetDataOrigin())+np.array(mynormal)*sliceIndex
            center = self.imageSlice.GetCenter()
            viewup = list(self.maskReader.GetDataDirection())[6:]
            position = center[0],myorigin[1]+positionOffset,center[2]
        elif sliceOrientation == 2:
            mynormal = list(self.maskReader.GetDataDirection())[6:]
            myorigin = np.array(self.maskReader.GetDataOrigin())+np.array(mynormal)*sliceIndex
            center = self.imageSlice.GetCenter()
            viewup = (0,-1,0)
            position = center[0],center[1],myorigin[2]+positionOffset
        else:
            raise ValueError()
        
        self.myPlane.SetOrigin(myorigin)
        self.myPlane.SetNormal(mynormal)
        self.camera.SetViewUp(viewup)
        self.camera.SetPosition(position)
        self.camera.SetFocalPoint(center)

        self.renderWindow.Render()
        windowToImageFilter = vtk.vtkWindowToImageFilter()
        windowToImageFilter.SetInput(self.renderWindow)
        windowToImageFilter.Update()

        writer = vtk.vtkPNGWriter()
        fpath = os.path.join(work_dir,f"ok-{sliceOrientation}-{sliceIndex}.png")
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
    for x in range(3):
        sliceMaxArr = inst.maskReader.GetDataExtent()[1::2]
        sliceMax = sliceMaxArr[x]
        for y in np.linspace(0,sliceMax,20):
            inst.render(x,float(int(y)))

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