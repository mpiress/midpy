#Sistema Operacional
FROM tensorflow/tensorflow:latest-devel-gpu

#update cmake
RUN DEBIAN_FRONTEND="noninteractive" apt-get install wget
RUN DEBIAN_FRONTEND="noninteractive" wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | apt-key add
RUN DEBIAN_FRONTEND="noninteractive" apt-add-repository 'deb https://apt.kitware.com/ubuntu/ bionic main'

#Dependências do sistema
#RUN DEBIAN_FRONTEND="noninteractive" apt-get install software-properties-common
#RUN DEBIAN_FRONTEND="noninteractive" add-apt-repository ppa:deadsnakes/ppa
RUN DEBIAN_FRONTEND="noninteractive" apt-get update -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get upgrade -y
#RUN DEBIAN_FRONTEND="noninteractive" apt-get install python3.8 python3.8-dev python3.8-minimal libpython3.8-minimal libpython3.8-stdlib python3-pip -y

#RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

RUN DEBIAN_FRONTEND="noninteractive" apt-get install build-essential cmake git apt-utils pkg-config libgtk-3-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
    gfortran openexr libatlas-base-dev libboost-python-dev\
    libtbb2 libtbb-dev libdc1394-22-dev libopenexr-dev \
    libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev htop nano cmake-curses-gui gnuplot\
    libboost-dev libboost-all-dev python3-pip libpython3-dev python3-numpy -y

RUN apt-get install -y gcc-7 g++-7 \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 1 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 1

#Pacotes do Python
COPY requirements.txt /requirements.txt 
RUN python3 -m pip install --upgrade pip #Atualização do gerenciador de pacotes
RUN python3 -m pip install -r requirements.txt  #Instalação dos pacotes listados

#Diretório do usuário docker
WORKDIR /home/michel
