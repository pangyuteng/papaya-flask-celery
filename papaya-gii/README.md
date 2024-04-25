

```
docker run -it -u $(id -u):$(id -g) -v /mnt:/mnt nii2gii bash

cd /mnt/hd1/papaya-flask-celery/papaya-gii
/opt/nii2mesh/src/nii2mesh lung_vessels.nii.gz -l 0 -p 0 -r 1 vsl.gii.gz

# above is too much work trying below

docker run -it -u $(id -u):$(id -g) -v /mnt:/mnt pangyuteng/dcm:latest bash
python nii2gii.py merged.nii.gz .




```