#!/usr/bin/python3
from common.envs import *
from common.module import *

#Docker hub information
ci_registry = 'hoanghd164'
ci_registry_user = 'hoanghd164'
ci_registry_password = 'Ho@nghd90'

#Docker image information
image_name = 'build-infra'
image_version = 'latest'

def docker_build():
    Dockerfile = '''FROM ubuntu:20.04
    RUN apt-get update -y && apt-get install -y python3.8 python-setuptools snmp screen vim psmisc tree git tmux cron net-tools
    RUN apt install -y python3-pip iputils-ping traceroute

    RUN pip3 install --upgrade pip paramiko jsonpath-ng requests

    WORKDIR /home

    RUN echo 'set number' > ~/.vimrc && echo 'syntax on' >> ~/.vimrc && echo 'highlight Comment ctermfg=LightCyan' >> ~/.vimrc && echo 'set relativenumber' >> ~/.vimrc && echo 'set shiftwidth=2' >> ~/.vimrc
    ENTRYPOINT echo 'Hà Đăng Hoàng' && /bin/bash'''

    file_option.file_write('Dockerfile',Dockerfile)
    os.system('docker build -t %s:%s --force-rm -f Dockerfile .' %(image_name,image_version))
    file_option.file_remove('Dockerfile')

def docker_push_image():
    os.system('docker login -u %s -p %s' %(ci_registry_user,ci_registry_password))
    os.system('docker tag %s:%s %s/%s:%s' %(image_name,image_version,ci_registry,image_name,image_version))
    os.system('docker push %s/%s:%s' %(ci_registry,image_name,image_version))

docker_build()
docker_push_image()