import os
import time

from contextlib import contextmanager


@contextmanager
def timer(name):
    t0 = time.time()
    yield
    print(f'[{name}] done in {time.time() - t0:.0f} s')

USE_APEX = True

if USE_APEX:
    with timer('install Nvidia apex'):
        # Installing Nvidia Apex
        os.system('git clone https://github.com/NVIDIA/apex; cd apex; pip install -v --no-cache-dir' +
                  ' --global-option="--cpp_ext" --global-option="--cuda_ext" ./')
        os.system('rm -rf apex/.git') # too many files, Kaggle fails
