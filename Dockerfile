FROM nvcr.io/nvidia/pytorch:22.02-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y \
    build-essential \
    libglib2.0 \
    curl \
    wget \
    git \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    python3.8 \
    python3-pip \
    && ln -s /usr/bin/python3.8 /usr/local/bin/python

WORKDIR /tmp/unique_for_apex
# uninstall Apex if present, twice to make absolutely sure :)
RUN pip uninstall -y apex || :
RUN pip uninstall -y apex || :
# SHA is something the user can touch to force recreation of this Docker layer,
# and therefore force cloning of the latest version of Apex
RUN SHA=ToUcHMe git clone https://github.com/NVIDIA/apex.git
WORKDIR /tmp/unique_for_apex/apex
RUN pip3 install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" .

WORKDIR f3net

COPY . ./

RUN pip3 install -r requirements.txt

WORKDIR src/

CMD ["python",  "train.py"]
