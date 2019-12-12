FROM tensorflow/tensorflow:1.14.0-py3

RUN apt-get -y update && apt-get install libsm6 libxrender1 libxext-dev openssh-server -y
RUN pip install imageio==2.5.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install imutils==0.5.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install kiwisolver==1.1.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install matplotlib==3.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install networkx==2.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install numpy==1.14.6 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install opencv-python==3.4.3.18 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install pillow==6.1.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install pyparsing==2.4.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install pywavelets==1.0.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install torch==1.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install keras==2.2.4 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install pandas==0.25.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install Flask==1.1.1 -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install Werkzeug==0.16.0 -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install jupyter -i https://mirrors.aliyun.com/pypi/simple/

RUN mkdir  /root/scripts
COPY start.sh /root/scripts/

RUN mkdir /root/.jupyter
RUN echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && echo "c.NotebookApp.base_url = '/'" >> /root/.jupyter/jupyter_notebook_config.py

WORKDIR /root/ccpd

CMD /root/scripts/start.sh
