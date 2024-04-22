import SimpleITK as sitk
import numpy as np
import vtk



rul_file = '/mnt/hd2/data/Totalsegmentator_dataset/s1405/segmentations/lung_upper_lobe_left.nii.gz'
rml_file = '/mnt/hd2/data/Totalsegmentator_dataset/s1405/segmentations/lung_middle_lobe_right.nii.gz'
rll_file = '/mnt/hd2/data/Totalsegmentator_dataset/s1405/segmentations/lung_lower_lobe_right.nii.gz'
lul_file = '/mnt/hd2/data/Totalsegmentator_dataset/s1405/segmentations/lung_upper_lobe_right.nii.gz'
lll_file = '/mnt/hd2/data/Totalsegmentator_dataset/s1405/segmentations/lung_lower_lobe_left.nii.gz'

for abbrv,nifti_file in [
    ('rul',rul_file),
    ('rml',rml_file),
    ('rll',rll_file),
    ('lul',lul_file),
    ('lll',lll_file),
    ]:

    #mask_obj = sitk.ReadImage(nifti_file)

    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(nifti_file)
    reader.Update()

    # threshold = vtk.vtkImageThreshold()
    # threshold.SetInputConnection(reader.GetOutputPort())
    # threshold.ThresholdByUpper(0)  #th
    # threshold.ReplaceInOn()
    # threshold.SetInValue(0)  # set all values below th to 0
    # threshold.ReplaceOutOn()
    # threshold.SetOutValue(1)  # set all values above th to 1
    # threshold.Update()

    dmc = vtk.vtkDiscreteMarchingCubes()
    #dmc.SetInputConnection(threshold.GetOutputPort())
    dmc.SetInputConnection(reader.GetOutputPort())
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

    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(dmc.GetOutputPort())
    writer.SetFileTypeToBinary()
    writer.SetFileName(f"{abbrv}.stl")
    writer.Write()


"""

docker run -it -u $(id -u):$(id -g) -w $PWD -v /mnt:/mnt pangyuteng/dcm:latest bash


"""