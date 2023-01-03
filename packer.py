#!/usr/bin/python3
from common.envs import *
from common.module import *

os.system('clear')

rootDir = '/volumes-hdd/packer'
homeImage = '/volumes-hdd/images'

class packerDeploy():
    def config(projectName,homeImage):
        cpu = 4
        memory = 4096
        disk_size = 8192
        username = 'ubuntu'
        passwd = 'Hoanghd164'
        userdataDir = '%s/userdata.cfg' %(rootDir)
        userdataImage = '%s/cloud-init.img' %(rootDir)

        imageInfo = {
            'ubuntu-20.04': {
                'image_url': 'https://cloud-images.ubuntu.com/minimal/releases/focal/release/ubuntu-20.04-minimal-cloudimg-amd64.img',
                'image_checksum': '49b7325603f92b9160d373ed1433f636622f9fa5cd4cb96567c64e35ab6eec6d',
                'image_checksum_type': 'sha256'
            },
            'ubuntu-18.04': { 
                'minimal':{
                    'image_url': 'https://cloud-images.ubuntu.com/minimal/releases/bionic/release/ubuntu-18.04-minimal-cloudimg-amd64.img',
                    'image_checksum': '2f8c35d32e9c0e09efe75759e1c1b9c3dbd8f41392051e6c4220d2b689dc85b4',
                    'image_checksum_type': 'sha256'
                    },
                'bionic':{
                    'image_url': 'https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img',
                    'image_checksum': 'a90ab7fa64b554bc8381397c4807d610d4b96d992fbfbac188687cba29168f1a',
                    'image_checksum_type': 'sha256'
                    },
                }
            }
        image_url = imageInfo['ubuntu-18.04']['bionic']['image_url']
        image_checksum = imageInfo['ubuntu-18.04']['bionic']['image_checksum']
        image_checksum_type = imageInfo['ubuntu-18.04']['bionic']['image_checksum_type']

        projectConfig = '''{
            "builders":[
                {
                    "type": "qemu",
                    "iso_url": "{{ user `image_url` }}",
                    "iso_checksum": "{{ user `image_checksum` }}",
                    "iso_checksum_type": "{{ user `image_checksum_type` }}",
                    "format": "qcow2",
                    "disk_image": true,
                    "disk_size": "{{ user `disk_size` }}",
                    "output_directory": "build",
                    "disk_compression": true,
                    "headless": true,
                    "boot_command": [
                        "<enter>"
                    ],
                    "accelerator": "kvm",
                    "ssh_username": "{{ user `ssh_username` }}",
                    "ssh_password": "{{ user `ssh_password` }}",
                    "ssh_port": 22,
                    "ssh_wait_timeout": "300s",
                    "vm_name": "{{ user `vm_name` }}",
                    "use_default_display": false,
                    "qemuargs": [
                        ["-m", "{{ user `memory` }}"],
                        ["-smp", "cpus={{ user `cpus` }}"],
                        ["-cdrom", "{{ user `cloud_init_image` }}"],
                        ["-serial", "mon:stdio"]
                    ]
            }
            ],
            "provisioners": [
            {
                "execute_command": "echo '{{ user `ssh_password` }}' | {{.Vars}} sudo -E -S bash -x '{{.Path}}'",
                "scripts": [
                "setup.sh"
                ],
                "type": "shell"
            },
            {
                "scripts": [
                "cloudinit.sh"
                ],
                "type": "shell"
            },
            {
                "type": "shell",
                "inline": [
                    "sudo sync"
                ]
            }
            ],
            "variables": {
            "cpus": "%s",
            "image_checksum": "%s",
            "image_checksum_type": "%s",
            "image_url" : "%s",
            "cloud_init_image": "%s",
            "disk_size": "%s",
            "memory": "%sM",
            "ssh_username": "%s",
            "ssh_password": "%s",
            "vm_name": "%s-packer-image.qcow2"
            }
        }''' %(cpu,image_checksum,image_checksum_type,image_url,userdataImage,disk_size,memory,username,passwd,projectName)

        timestamp = subprocess.check_output('date "+%H%M%S%d%m%y"', shell=True).decode("utf-8").strip('\n')
        if os.path.exists('%s/build' %(rootDir)):
            os.system('mv %s/build %s/build-%s.bak' %(rootDir,rootDir,timestamp))
        folder_option.maker_folder(rootDir)

        userdataConfig = '#cloud-config\nautoinstall:\n  version: 1\n  locale: en_US\n  keyboard:\n    layout: fr\n  ssh:\n    install-server: true\n    allow-pw: true\n  packages:\n    - qemu-guest-agent\n\npassword: %s\nssh_pwauth: true\nchpasswd:\n  expire: false\n\nlocale: en_US.UTF-8\nlocale_configfile: /etc/default/locale' %(passwd)
        file_option.file_write(userdataDir,userdataConfig)
        os.system('cd %s && cloud-localds %s/cloud-init.img %s' %(rootDir,rootDir,userdataDir))

        scriptSetup = '''#!/bin/bash -x\napt update && apt-get install ca-certificates curl gnupg lsb-release -y\ncurl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg\necho "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list\ncurl -s https://packages.cloud.google.com/apt/dists/kubernetes-xenial/main/binary-amd64/Packages | grep Version | tail -5\ncurl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -  && \ \necho 'deb http://apt.kubernetes.io/ kubernetes-xenial main' | tee /etc/apt/sources.list.d/kubernetes.list  && \ \napt update && apt-get upgrade -y\napt-get install containerd.io -y\napt-get install -y kubelet=1.23.8-00 kubectl=1.23.8-00 kubeadm=1.23.8-00\napt-get install keepalived -y\napt-get install haproxy -y\ntee /etc/sysctl.d/kubernetes.conf<<EOF\nnet.bridge.bridge-nf-call-ip6tables = 1\nnet.bridge.bridge-nf-call-iptables = 1\nnet.ipv4.ip_forward = 1\nEOF\necho "net.netfilter.nf_conntrack_max=1000000" >> /etc/sysctl.conf\nsysctl --system\ntee /etc/modules-load.d/containerd.conf <<EOF\noverlay\nbr_netfilter\nEOF\nmodprobe overlay\nmodprobe br_netfilter\nsysctl --system\nsed -i "/ swap / s/^\(.*\)$/#\\1/g" /etc/fstab || sed -i '/swap/d' /etc/fstab\nswapoff -a\nmkdir -p /etc/containerd\ncontainerd config default > /etc/containerd/config.toml\nsystemctl enable containerd\nsystemctl restart containerd\nkubeadm config images pull\napt install iputils-ping -y\napt install traceroute -y\napt install vim -y\napt install tree -y'''
        scriptsetupDir = '%s/setup.sh' %(rootDir)
        file_option.file_write(scriptsetupDir,scriptSetup)

        scriptCloudinit = '''#!/bin/bash -x\nsudo apt update\nsudo apt install qemu-guest-agent -y\nsudo systemctl start qemu-guest-agent\nsudo systemctl enable qemu-guest-agent\nsudo cloud-init clean'''
        scriptcloudinitDir = '%s/cloudinit.sh' %(rootDir)
        file_option.file_write(scriptcloudinitDir,scriptCloudinit)

        projectconfigDir = '%s/%s.json' %(rootDir,projectName)
        file_option.file_write(projectconfigDir,projectConfig)

        json.dumps(file_json.json_read('%s/%s.json' %(rootDir,projectName)), sort_keys=True, indent=2)

        os.system('cd %s && sudo packer validate %s' %(rootDir,projectconfigDir))
        os.system('cd %s && sudo packer build %s' %(rootDir,projectconfigDir))
        
        source = '%s/build/%s-packer-image.qcow2' %(rootDir,projectName)
        destination = '%s/%s-packer-image.qcow2' %(homeImage,projectName)
        if os.path.exists(source):
            os.system('mv %s %s' %(source,destination))

packagesInstall.updateSystem()
packagesInstall.installPkgs({'apt': ['tree', 'tmux', 'python3-pip'],'apt-get': ['cloud-image-utils']})
packagesInstall.pythonModules(['jsonpath-ng==1.5.3', 'paramiko==2.12.0', 'requests==2.22.0'])