import os
import sys
import SimpleITK as sitk
import tempfile
import vtk
from vtk.util.colors import (
    green,
    red,
    yellow,
    salmon,
    warm_grey,
)
import subprocess
map_list = [
    (1,green,'rul'),
    (2,red,'rml'),
    (3,yellow,'rll'),
    (4,green,'lul'),
    (5,yellow,'lll'),
    (6,red,'vessel'),
    (7,salmon,'airway'),
    (8,warm_grey,'valve')
]

nifti_file = sys.argv[1]
folder = sys.argv[2]

mask_obj = sitk.ReadImage(nifti_file)
mask = sitk.GetArrayFromImage(mask_obj)

with tempfile.TemporaryDirectory() as tmpdir:
    for obj_value,obj_color,obj_abbrv in map_list:
        item_obj = sitk.BinaryThreshold(mask_obj,
            lowerThreshold=obj_value, upperThreshold=obj_value, insideValue=1, outsideValue=0)
        item_file = os.path.join(tmpdir,f'{obj_abbrv}.nii.gz')
        gii_file = os.path.join(folder,f'{obj_abbrv}.gii')
        sitk.WriteImage(item_obj,item_file)
        cmd_str = f'nii2mesh {item_file} -l 0 -p 0 -r 1 {gii_file}'
        subprocess.call(cmd_str,shell=True)
        


