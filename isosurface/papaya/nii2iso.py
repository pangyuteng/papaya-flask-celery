# https://gist.github.com/pangyuteng/facd430d0d9761fc67fff4ff2e5fffc3

import vtk
import SimpleITK as sitk

ireader = sitk.ImageFileReader()
ireader.SetFileName('static/example.nii.gz')

imgobj = ireader.Execute()
writer = sitk.ImageFileWriter()    
writer.SetFileName('static/example.nii')
writer.SetUseCompression(False)
writer.Execute(imgobj)

reader = vtk.vtkNIFTIImageReader()
reader.SetFileName('static/example.nii.gz')
reader.Update()

for val in [100,900]:
    threshold = vtk.vtkImageThreshold ()
    threshold.SetInputConnection(reader.GetOutputPort())
    threshold.ThresholdByLower(val)  #th
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
    smooth.SetNumberOfIterations(500)
    smooth.SetRelaxationFactor(0.1)
    smooth.FeatureEdgeSmoothingOff()
    smooth.BoundarySmoothingOn()
    smooth.Update()
    
    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData(smooth.GetOutput())
    writer.SetFileName(f'static/example_{val}.vtk')
    writer.Write()
