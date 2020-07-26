import os
import tempfile
import subprocess
import base64
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

import pandas as pd
import numpy as np
import SimpleITK as sitk

from celery import Celery
from celery.result import AsyncResult

celery_config = {
    "broker_url": os.environ["AMQP_URI"],
    "result_backend": os.environ["REDIS_URI"],
    "task_serializer": "pickle", # for passing binary objects
    "result_serializer": "pickle",
    "accept_content": ["pickle"],
}

celery = Celery("mycelery", broker=celery_config["broker_url"])
celery.conf.update(celery_config)

@celery.task()
def long_running_task(start_time):
    time.sleep(6.9)
    end_time = time.time()
    return {"start_time":start_time,"end_time":end_time}

def get_state(project_id):
    from misc.state import get_state_summary
    summary_dict, state_df = get_state_summary(project_id)
    return summary_dict, state_df

def get_bunny():
    ime_file = "bunny/bunny.nii.gz"
    surface_file = "bunny/bunny.vtk"
    return ime_file, surface_file



def get_random_nifti_image(return_base64string=False):

    spacing = (5,5,5)
    origin = (0,0,1)
    direction = (0,1,0,1,0,0,0,0,1)
    arr = (np.random.rand(15,15,5)*255).astype(np.uint8)
    image = sitk.GetImageFromArray(arr)
    image.SetSpacing(spacing)
    image.SetOrigin(origin)
    image.SetDirection(direction)

    #image = sitk.ReadImage(path_to_sitk_image)
    resample = sitk.ResampleImageFilter()
    resample.SetInterpolator(sitk.sitkLinear)
    resample.SetOutputDirection(image.GetDirection())
    resample.SetOutputOrigin(image.GetOrigin())
    new_spacing = [0.5,0.5,0.5]
    resample.SetOutputSpacing(new_spacing)  # needs list of INT!!!

    orig_size = np.array(image.GetSize(), dtype=np.int)
    orig_spacing = image.GetSpacing()
    new_size = orig_size*(orig_spacing/np.array(new_spacing))
    new_size = np.ceil(new_size).astype(np.int)
    new_size = [int(s) for s in new_size] 
    resample.SetSize(new_size) # needs list of INT!!!

    newimage = resample.Execute(image)
    print(new_size)

    use_compression = False

    with tempfile.TemporaryDirectory() as tempdir:

        fpath = os.path.join(tempdir,'img.nii')

        writer = sitk.ImageFileWriter()
        writer.SetFileName(fpath)
        writer.SetUseCompression(use_compression)
        writer.Execute(newimage)
        
        with open(fpath,'rb') as f:
            binary_file_data = f.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_message = base64_encoded_data.decode('utf-8')

    print(new_size)

    imgname = "sample_dicom/img.nii"
    maskname = "sample_dicom/mask.nii"
    tempdir = "static"
    
    imgpath = os.path.join(tempdir,imgname)
    os.makedirs(os.path.dirname(imgpath),exist_ok=True)

    writer = sitk.ImageFileWriter()
    writer.SetFileName(imgpath)
    writer.SetUseCompression(use_compression)
    writer.Execute(newimage)

    maskpath = os.path.join(tempdir,maskname)
    arr = np.zeros(new_size)
    print(arr.shape)
    arr[10:30,25:125,25:125]=255
    arr = arr.astype(np.uint8)
    mask = sitk.GetImageFromArray(arr)
    mask.SetSpacing(new_spacing)
    mask.SetOrigin(origin)
    mask.SetDirection(direction)

    writer = sitk.ImageFileWriter()    
    writer.SetFileName(maskpath)
    writer.SetUseCompression(use_compression)
    writer.Execute(mask)

    return base64_message, imgname, maskname

from skimage import transform
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import pydicom._storage_sopclass_uids

def gen_random_dicom_file_list():
    folder_path = os.path.join(THIS_DIR,"static","sample_dicom")
    os.makedirs(folder_path,exist_ok=True)

    image3d = np.random.rand(20,128,128)*1000-500
    image3d = transform.resize(image3d,(20,512,512),0)
    image3d = image3d.astype(np.uint16)

    return gen_dicom_file_list(image3d,folder_path)

def gen_dicom_file_list(image3d,folder_path):

    sizez = image3d.shape[0]

    print("gen_random_dicom_file_list...")
    StudyInstanceUID = pydicom.uid.generate_uid()
    SeriesInstanceUID = pydicom.uid.generate_uid()
    FrameOfReferenceUID = pydicom.uid.generate_uid()

    file_list = []
    for index in range(sizez):
        
        instance_number = index+1
        image2d = image3d[index,:,:].squeeze()

        # Populate required values for file meta information
        meta = pydicom.Dataset()
        meta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
        meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian  

        ds = Dataset()
        ds.file_meta = meta

        ds.is_little_endian = True
        ds.is_implicit_VR = False

        ds.SOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
        ds.PatientName = "Test^Firstname"
        ds.PatientID = "123456"

        ds.Modality = "CT"
        ds.SeriesInstanceUID = SeriesInstanceUID
        ds.StudyInstanceUID = StudyInstanceUID
        ds.FrameOfReferenceUID = FrameOfReferenceUID

        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.SamplesPerPixel = 1
        ds.HighBit = 15

        #ds.ImagesInAcquisition = "1"

        ds.Rows = image2d.shape[0]
        ds.Columns = image2d.shape[1]
        ds.InstanceNumber = f"{instance_number}"
        ds.SliceLocation = f"{index}"
        ds.ImagePositionPatient = r"0\0\{}".format(index)
        ds.ImageOrientationPatient = r"1\0\0\0\1\0\0\0\1"
        ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"

        ds.RescaleIntercept = "-1024"
        ds.RescaleSlope = "1"
        ds.PixelSpacing = r"1\1"
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelRepresentation = 1

        pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)

        ds.PixelData = image2d.tobytes()

        file_path = os.path.join(folder_path,f"{index}.dcm")
        print(file_path)

        ds.save_as(file_path)

        STATIC_FOLDER = os.path.join(THIS_DIR,"static")
        rel_path = os.path.relpath(file_path,STATIC_FOLDER)

        file_list.append(rel_path)

    return file_list

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def gen_rabbit_dicom_file_list():
    p_list = []
    for i in range(361):
        p = os.path.join('bunny','dcm',f'{i+1}.dcm')
        p_list.append(p)
    return p_list

@celery.task()
def download_bunny():

    tempdir = os.path.join(THIS_DIR,'static','bunny')
    os.makedirs(tempdir,exist_ok=True)
    with cd(tempdir):

        if not os.path.exists('bunny-ctscan.tar.gz'):
            subprocess.call(['wget','https://graphics.stanford.edu/data/voldata/bunny-ctscan.tar.gz'])
        if not os.path.exists('bunny'):
            subprocess.call(['tar','-xzvf','bunny-ctscan.tar.gz'])
        print('here')
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

    print('download done')
    # save as dcm
    dcm_folder_path = os.path.join(THIS_DIR,"static","bunny","dcm")
    os.makedirs(dcm_folder_path,exist_ok=True)

    folder_path = os.path.join(THIS_DIR,"static","bunny")
    img = np.zeros((512,512,361))
    for i in np.arange(1,362,1):
        filepath = os.path.join(folder_path,"bunny",f'{i}')
        tmp = np.fromfile(filepath,dtype='uint16',sep='')
        #Max 16 bit = 65535
        #Max 12 bit = 4095
        tmp = np.round(tmp/65535*4095)
        tmp = tmp.reshape(512,512)
        img[:,:,i-1]=tmp
    img = img.astype(np.uint16)
    
    img_list = gen_dicom_file_list(img,dcm_folder_path)
    return {"img_list":img_list}

@celery.task()
def render_bunny_isosurface():

    tempdir = os.path.join(THIS_DIR,'static','bunny')
    os.makedirs(tempdir,exist_ok=True)
    with cd(tempdir):

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


if __name__ == "__main__":
    #download_bunny()
    #gen_rabbit_dicom_file_list()
    pass