FROM nvidia/cuda:11.4.0-runtime-ubuntu20.04

RUN apt-get update && apt-get install -y libglib2.0-0

RUN apt-get update \
    && apt-get install -y \
    build-essential \
    curl \
    wget \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    python3.8 \
    python3-pip \
    && ln -s /usr/bin/python3.8 /usr/local/bin/python

WORKDIR f3net

COPY . ./

RUN pip3 install -r requirements.txt

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \/bin/bash ~/miniconda.sh -b -p /opt/conda
# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda install -c conda-forge nvidia-apex

WORKDIR f3net

CMD ["python",  "src/train.py"]
