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

COPY apex.sh /
RUN chmod +x /apex.sh

WORKDIR f3net

CMD ["python",  "src/train.py"]
