import os
import sys
import json
import uuid
import shutil
import tempfile
import pydicom
import SimpleITK as sitk
from huggingface_hub import snapshot_download

import gradio as gr
from gradio_pdf import PDF


HF_ACCESS_TOKEN = os.environ.get("HF_ACCESS_TOKEN")

model_folder = snapshot_download(repo_id="pangyuteng/test-model",repo_type='model',token=HF_ACCESS_TOKEN)

core_folder = os.path.join(model_folder,"mymodel")
sys.path.append(core_folder)
from inference import inference

sys.path.append(os.path.join(model_folder,"report"))
from report_utils import NiftiVisualizer

weight_file = os.path.join(core_folder,"weights.h5")
example_nifti_path = "img.nii.gz"


def imread(file_list):
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(file_list)
    img_obj = reader.Execute()
    return img_obj

def main_func(input_file_list):
    with tempfile.TemporaryDirectory() as tempdir:
        image_file = os.path.join(tempdir,f"image.nii.gz")
        first_file = input_file_list[0].name
        if first_file.endswith(".dcm"):
            file_list = []
            for x in input_file_list:
                file_path = x.name
                ds = pydicom.dcmread(file_path,stop_before_pixels=True)
                item = dict(
                    file_path=file_path,
                    instance_number=int(ds.InstanceNumber)
                )
                file_list.append(item)
            file_list = sorted(file_list,key=lambda x:x['instance_number'])
            file_list = [x['file_path'] for x in file_list]
            img_obj = imread(file_list)
        elif first_file.endswith(".nii.gz") or first_file.endswith(".nii"):
            img_obj = sitk.ReadImage(first_file)
        else:
            raise ValueError("only accept .nii.gz file or .dcm files!")

        sitk.WriteImage(img_obj,image_file)
        
        inference(image_file,tempdir,weight_file)

        mask_file = os.path.join(tempdir,"output.nii.gz")
        json_file = os.path.join(tempdir,"output.json")
        my_uid = uuid.uuid4().hex
        output_pdf_file = os.path.join('/tmp',f'{my_uid}.pdf')
        output_json_file = os.path.join('/tmp',f'{my_uid}.json')

        inst = NiftiVisualizer("NA",image_file,mask_file,json_file,tempdir)
        tmp_pdf_file = inst.gen_pdf()
        assert(os.path.exists(tmp_pdf_file))

        with open(json_file,'r') as f:
            output_json = json.loads(f.read())

        shutil.copy(tmp_pdf_file,output_pdf_file)
        shutil.copy(json_file,output_json_file)

        return output_pdf_file, output_json, output_pdf_file, output_json_file

with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown(
        """
        # demo title 
        + note 1
        + note 2
        """)
    with gr.Row():
        with gr.Column():
            in_file = gr.File(label="upload dicom files here",file_count='multiple')
            btn = gr.Button("process")
        with gr.Column():
            pdf = PDF(label="Upload a PDF", interactive=True)
            gr_json = gr.Json()
            download_button_pdf = gr.DownloadButton("Download report pdf", visible=True)
            download_button_json = gr.DownloadButton("Download report json", visible=True)
    btn.click(fn=main_func, 
        inputs=[in_file],
        outputs=[pdf,gr_json,download_button_pdf,download_button_json],
    )#example=[example_nifti_path],cache_examples=True


if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        debug=True,
        show_api=True,
        share=False,
    )

"""

docker run -it -u $(id -u):$(id -g) -p 7860:7860 \
    -v $PWD:/opt/demo -w /opt/demo --env-file=.env \
    ok bash

python app.py

"""
