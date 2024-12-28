
FROM tensorflow/tensorflow:2.10.0-gpu-jupyter
#FROM python:3.10-bullseye

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 build-essential make vim curl wget -yq

RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb && \
    apt install ./wkhtmltox_0.12.6-1.focal_amd64.deb -yq

WORKDIR /opt

RUN /usr/bin/python3 -m pip install --upgrade pip
COPY requirements.txt /opt
RUN pip install -r /opt/requirements.txt
RUN pip install vtk-osmesa --extra-index-url https://gitlab.kitware.com/api/v4/projects/13/packages/pypi/simple

# RUN wget https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_linux_amd64 && \
#     mv frpc_linux_amd64 /usr/local/lib/python3.8/dist-packages/gradio/frpc_linux_amd64_v0.2 && \
#     chmod 777 /usr/local/lib/python3.8/dist-packages/gradio/frpc_linux_amd64_v0.2

# ENV HF_HOME=/opt/.cache
# RUN mkdir -p ${HF_HOME} && chmod -R 777 ${HF_HOME}
# WORKDIR /opt
#RUN mkdir -p /.cache/pip && chmod -R 777 /.cache/pip

ENV BATCH_SIZE=1
RUN mkdir -p /opt/fi && chmod -R 777 /opt/fi
COPY --chmod=777 . /opt/fi
WORKDIR /opt/fi/flask
CMD ["python","app.py"]