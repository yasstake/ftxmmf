FROM ubuntu

RUN apt-get update -y
RUN apt-get install -y git gzip curl wget python lsb-release gnupg apt-utils

RUN apt-get install -y python3.7 python3-distutils python-numpy python-dev cmake \
            zlib1g-dev libjpeg-dev xvfb xorg-dev python-opengl \
            libboost-all-dev libsdl2-dev swig

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

RUN cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && /usr/bin/python3.7 get-pip.py

RUN /usr/bin/python3.7 -m pip install websocket-client
RUN /usr/bin/python3.7 -m pip install tables
RUN /usr/bin/python3.7 -m pip install gym
RUN /usr/bin/python3.7 -m pip install --upgrade google-cloud-storage
RUN /usr/bin/python3.7 -m pip install --upgrade tensorflow

RUN git clone https://github.com/yasstake/ftxmmf.git

ADD ftx2log.sh /ftxmmf
ADD bf2log.sh /ftxmmf

CMD /usr/bin/python3.7









