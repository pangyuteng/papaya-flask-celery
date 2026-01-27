FROM nvidia/opengl:1.2-glvnd-devel-ubuntu22.04

WORKDIR /app

# Avoid buffering the server URL
ENV PYTHONUNBUFFERED=1

# Prevent apt from prompting us about various decisions
ENV DEBIAN_FRONTEND=noninteractive

# Allow driver to do rendering
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV NVIDIA_VISIBLE_DEVICES=all

ENV VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow

# Install trame-slicer dependencies and pyenv build dependencies
RUN apt-get update && apt-get install -y libturbojpeg \
    make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Install Pyenv
ENV HOME=/root
ENV PYENV_DIR="${HOME}/.pyenv"
RUN curl -fsSL https://pyenv.run | bash && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
ENV PATH="${PYENV_DIR}/shims:${PYENV_DIR}/bin:${PATH}"

# Install SHARED Python3.10
RUN PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.18 && \
    pyenv global 3.10.18 && \
    python -m pip install --upgrade pip


RUN pip install trame-slicer==1.7.2
COPY trame-slicer/vtk_mrml-9.4.0-cp310-cp310-manylinux_2_35_x86_64.whl /tmp
RUN pip install /tmp/vtk_mrml-9.4.0-cp310-cp310-manylinux_2_35_x86_64.whl
