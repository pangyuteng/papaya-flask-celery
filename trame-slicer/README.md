
```

https://github.com/KitwareMedical/trame-slicer

https://github.com/Slicer/SlicerDocker/tree/main

cd tram-slicer
git checkout docker
wget https://github.com/KitwareMedical/trame-slicer/releases/download/v1.4.0/vtk_mrml-9.4.0-cp310-cp310-manylinux_2_35_x86_64.whl

docker build -t trame-slicer -f docker/Dockerfile .

docker run -p 8080:8080 --runtime=nvidia -it -e VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow trame-slicer bash

cd ..
docker build -t trame-slicer-diy -f Dockerfile .

docker run -p 8080:8080 --runtime=nvidia -it -e VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow \
    -w $PWD -v /mnt:/mnt trame-slicer-diy bash

cd trame-slicer/examples

python medical_viewer_app.py --host 0.0.0.0

```