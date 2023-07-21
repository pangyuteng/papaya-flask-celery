
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

import numpy as np
import SimpleITK as sitk
from skimage.transform import resize
import time

MIN_VAL,MAX_VAL = -1000,1000
def downsample(image_path):
    logging.info("reading image")
    s=time.time()
    img_obj = sitk.ReadImage(image_path)
    e=time.time()
    logging.info(f"{e-s}")
    s=time.time()
    img = sitk.GetArrayFromImage(img_obj)
    logging.info(f"img.shape {img.shape}")
    logging.info(img.dtype)
    img = img.astype(np.float16)
    logging.info(img.dtype)
    img = (img-(MIN_VAL))/(MAX_VAL-MIN_VAL)*100
    img = img.clip(0,100)
    og_shape = list(img.shape)
    img = resize(img, (og_shape[0] // 2, og_shape[1] // 2, og_shape[2] // 2),anti_aliasing=True)
    img = resize(img,og_shape)
    img = img.astype(np.uint8)
    new_obj = sitk.GetImageFromArray(img)
    new_obj.CopyInformation(img_obj)
    sitk.WriteImage(new_obj,'downsampled.nii.gz')
    e=time.time()
    logging.info(f"{e-s}")

    


if __name__ == "__main__":
    image_path = sys.argv[1]
    downsample(image_path)
    
"""
cp /mnt/hd2/data/ct-org/images/volume-88.nii.gz raw.nii.gz
python utils.py raw.nii.gz
"""