import os
import tempfile
import base64

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
def get_random_nifti_image_as_base64string():

    with tempfile.TemporaryDirectory() as tempdir:

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
        fpath = os.path.join(tempdir,'img.nii')

        writer = sitk.ImageFileWriter()    
        writer.SetFileName(fpath)
        writer.SetUseCompression(use_compression)
        writer.Execute(newimage)

        with open(fpath,'rb') as f:
            binary_file_data = f.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_message = base64_encoded_data.decode('utf-8')
            return base64_message


from skimage import transform
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import pydicom._storage_sopclass_uids

def gen_random_dicom_file_list():

    print("gen_random_dicom_file_list...")
    StudyInstanceUID = pydicom.uid.generate_uid()
    SeriesInstanceUID = pydicom.uid.generate_uid()
    FrameOfReferenceUID = pydicom.uid.generate_uid()
    os.makedirs("static/sample_dicom",exist_ok=True)
    file_list = []
    for index in range(20):
        
        instance_number = index+1

        # not so random image
        image2d = np.random.rand(128,128)*1000-500
        image2d = transform.resize(image2d,(512,512),0)
        image2d = image2d.astype(np.uint16)

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
        basename = f"sample_dicom/{index}.dcm"
        ds.save_as(os.path.join("static",basename))
        file_list.append(basename)

    return file_list
    
if __name__ == "__main__":
    pass