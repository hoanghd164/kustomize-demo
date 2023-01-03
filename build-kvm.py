#!/usr/bin/python3
from common.envs import *
from common.module import *
from kubernetes import *

os.system('clear')

home_dir = '/kvm-volumes-hdd'
node_inerface_name = 'enp6s0f0'
node_bridged_network = 'br0'
node_ipaddr = '192.168.13.229'
node_prefix = 23
node_gateway = '192.168.12.5'
hostname = 'kvm-node01'

def prepareEnv():
    print('\n','-'*30,' Local update system and install packages ','-'*30)
    packagesInstall.updateSystem()
    packagesInstall.installPkgs({'apt': ['sshpass','tree'],'apt-get': ['cloud-image-utils']})
    packagesInstall.pythonModules(['jsonpath-ng==1.5.3', 'paramiko==2.12.0', 'requests==2.22.0'])

def format_disk():
    os.system('mkfs -t ext4 /dev/sdb')

def mount_disk():
    os.system('mkdir -p /kvm-volumes-hdd')
    os.system('mount -t auto /dev/sdb /kvm-volumes-hdd/')
    os.system('echo "/dev/sdb /kvm-volumes-hdd ext4 defaults 0 1" >> /etc/fstab')
    os.system('mount -a')

def os():
    os.system('osinfo-query os | grep -i ubuntu | cut -d ' ' -f -2')

def kvm_install():
    packagesInstall.updateSystem()
    packagesInstall.installPkgs({'apt': ['qemu-kvm','libvirt-clients', 'libvirt-daemon-system', 'bridge-utils', 'virt-manager', 'cloud-image-utils'],'apt-get': ['tree', 'sshpass']})
    hostfile =  '''192.168.13.227 kvm-node01.hoanghd.com
    192.168.13.228 kvm-node02.hoanghd.com
    192.168.13.229 kvm-node03.hoanghd.com'''
    file_option.val_add_to_file('/etc/hosts',hostfile)

def pacemaker_install():
    pacemaker_install = '''#!/bin/bash
        sudo apt install corosync pacemaker pcs -y
        sudo systemctl enable pcsd
        sudo systemctl enable corosync
        sudo systemctl enable pacemaker
        sudo systemctl start pcsd
        echo 'hacluster:Hoanghd164' | chpasswd

        # pcs cluster destroy
        sudo pcs cluster auth
        pcs host auth kvm-node01.hoanghd.com kvm-node02.hoanghd.com kvm-node03.hoanghd.com
        pcs cluster setup ha_cluster kvm-node01.hoanghd.com kvm-node02.hoanghd.com kvm-node03.hoanghd.com  --force
        pcs cluster enable --all
        pcs cluster start --all
        pcs status corosync
        pcs status cluster

        sudo pcs property set stonith-enabled=false
        sudo pcs property set no-quorum-policy=ignore

        rm -rf /usr/local/bin/pacemaker_install.sh'''
    file_option.file_write('/usr/local/bin/pacemaker_install.sh',pacemaker_install)
    os.system('chmod +x /usr/local/bin/pacemaker_install.sh')
    os.system('''screen -dmS "pacemaker_install" sh -c ". /usr/local/bin/pacemaker_install.sh; exec bash"''')

def nfs_server():
    packagesInstall.installPkgs({'apt': ['nfs-kernel-server']})
    file_option.val_add_to_file('/etc/exports','''/kvm-volumes-hdd *(rw,sync,fsid=1,no_subtree_check,no_root_squash)''')
    file_option.val_add_to_file('/etc/exports','''/kvm-volumes-ssd *(rw,sync,fsid=2,no_subtree_check,no_root_squash)''')
    os.system('systemctl restart nfs-kernel-server rpcbind')
    os.system('exportfs -v')

def nfs_client():
    packagesInstall.installPkgs({'apt': ['nfs-common']})
    file_option.val_add_to_file('/etc/fstab','''192.168.13.228:/kvm-volumes-ssd /kvm-volumes-ssd nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0''')
    file_option.val_add_to_file('/etc/fstab','''192.168.13.228:/kvm-volumes-hdd /kvm-volumes-hdd nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0''')
    os.system('mount -a')

def network_base_config():
    os.system('hostnamectl set-hostname kvm-node01')
    basic_config = '''#!/bin/bash
        hostnamectl set-hostname %s

        sudo sed -i 's|#group = "root"|group = "root"|' /etc/libvirt/qemu.conf
        sudo sed -i 's|#user = "root"|user = "root"|' /etc/libvirt/qemu.conf
        systemctl restart libvirtd

        echo """net.bridge.bridge-nf-call-ip6tables = 0
        net.bridge.bridge-nf-call-iptables = 0
        net.bridge.bridge-nf-call-arptables = 0""" >> /etc/sysctl.conf

        modprobe br_netfilter
        sysctl -p /etc/sysctl.conf

        rm -rf /usr/local/bin/basic_config.sh''' %(hostname)
    
    file_option.file_write('/usr/local/bin/basic_config.sh',basic_config)
    os.system('''screen -dmS "basic_config" sh -c ". /usr/local/bin/basic_config.sh; exec bash"''')
    
    netplan_filename = subprocess.check_output('''cat /etc/netplan/$(ls '/etc/netplan/' | grep '.yaml')''', shell=True).decode("utf-8").strip('\n')
    bridge_config = '''
        network:
        version: 2
        renderer: networkd

        ethernets:
            %s:
            dhcp4: false 
            dhcp6: false 

        bridges:
            $node_bridged_network:
            interfaces: [ %s ]
            addresses: [ %s/%s ]
            gateway4: %s
            mtu: 1500
            nameservers:
                addresses: [ 8.8.8.8, 1.1.1.1 ]
            parameters:
                stp: true
                forward-delay: 4
            dhcp4: no
            dhcp6: no''' %(node_inerface_name,node_inerface_name,node_ipaddr,node_prefix,node_gateway)
    file_option.file_write(netplan_filename,bridge_config)
    os.system('sudo netplan generate && sudo netplan --debug apply')

def default_subnet():
    default_network = subprocess.check_output('''virsh net-info default   || (echo 1)''', shell=True).decode("utf-8").strip('\n')
    default_status_network = subprocess.check_output("""virsh net-info default | grep 'Active:' | awk '{print $2}'""", shell=True).decode("utf-8").strip('\n')
    if int(default_network) == 1:
        if default_status_network == 'yes':
            os.system('virsh net-undefine default')

def nat_subnet_config():
    default_subnet()
    subnet_name = 'nat-network-sub172'
    bridge_name = 'virbr172'
    bridge_gw = '172.16.1.254'
    bridge_netmask = '255.255.255.0'
    dhcp_start_ipaddr = '172.16.1.2'
    dhcp_end_ipaddr = '172.16.1.253'
    net_folder = '/root/network_xml/nat-network-sub172.xml'

    nat_config = '''<network>
        <name>%s</name>
        <forward mode='nat'/>
        <bridge name='%s' stp='on' delay='0'/>
        <ip address='%s' netmask='%s'>
            <dhcp>
            <range start='%s' end='%s'/>
            </dhcp>
        </ip>
        </network>''' %(subnet_name,bridge_name,bridge_gw,bridge_netmask,dhcp_start_ipaddr,dhcp_end_ipaddr)

    file_option.file_write(net_folder,nat_config)
    return net_folder

def bridge_subnet_config():
    default_subnet()
    net_folder = '/root/network_xml/bridge-network.xml'

    bridge_config = '''<network>
    <name>bridged-network</name>
        <forward mode='bridge' />
        <bridge name='%s' />
    </network>''' %(node_bridged_network)

    file_option.file_write(net_folder,bridge_config)

def define_subnet():
    os.system('virsh net-define %s' %(nat_subnet_config()))
    os.system('virsh net-start %s' %(nat_subnet_config()))
    os.system('virsh net-autostart %s' %(nat_subnet_config()))
    os.system('virsh net-list --all')

prepareEnv()