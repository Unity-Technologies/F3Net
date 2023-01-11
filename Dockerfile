FROM nvcr.io/nvidia/pytorch:22.02-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y \
    build-essential \
    libglib2.0 \
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

WORKDIR src/

CMD ["python",  "train.py"]
