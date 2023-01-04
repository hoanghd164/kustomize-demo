docker run -it --name=asterisk --hostname=asterisk --network=host centos:centos7
docker run -itd --name=pbx-asterisk --network=host -p 5060:5060/tcp -p 5060:5060/udp -p 10000:30000/udp hoanghd164/asterisk:16pbx bash
docker run -itd --name=pbx-asterisk -p 5060:5060/tcp -p 5060:5060/udp asterisk:latest bash
docker run -itd --name=pbx-asterisk --network=host -p 5060:5060/tcp -p 5060:5060/udp -p 10000:30000/udp asterisk:latest bash

yum  -y install epel-release
yum -y install wget vim net-tools
yum -y groupinstall "Development Tools"
yum -y install libedit-devel sqlite-devel psmisc gmime-devel ncurses-devel libtermcap-devel sox newt-devel libxml2-devel libtiff-devel audiofile-devel gtk2-devel uuid-devel libtool libuuid-devel subversion kernel-devel kernel-devel-$(uname -r) git subversion kernel-devel crontabs cronie cronie-anacron wget vim

cd /usr/src/
git clone https://github.com/akheron/jansson.git
cd jansson
autoreconf  -i
./configure --prefix=/usr/
make && make install
wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-15-current.tar.gz
cd /usr/src/ 
git clone https://github.com/pjsip/pjproject.git
cd pjproject
./configure CFLAGS="-DNDEBUG -DPJ_HAS_IPV6=1" --prefix=/usr --libdir=/usr/lib64 --enable-shared --disable-video --disable-sound --disable-opencore-amr
make dep
make
make install
ldconfig

cd /usr/src/
wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-16-current.tar.gz
tar xvfz asterisk-16-current.tar.gz
rm -f asterisk-16-current.tar.gz
cd asterisk-*
./configure --libdir=/usr/lib64

make menuselect

contrib/scripts/get_mp3_source.sh
make
make install
make samples
make config
ldconfig

groupadd asterisk
useradd -r -d /var/lib/asterisk -g asterisk asterisk
usermod -aG audio,dialout asterisk
chown -R asterisk.asterisk /etc/asterisk
chown -R asterisk.asterisk /var/{lib,log,spool}/asterisk
chown -R asterisk.asterisk /usr/lib64/asterisk

vim /etc/sysconfig/asterisk
AST_USER="asterisk"
AST_GROUP="asterisk"

vim /etc/asterisk/asterisk.conf
runuser = asterisk ; The user to run as.
rungroup = asterisk ; The group to run as.

/etc/init.d/asterisk start

systemctl restart asterisk
systemctl enable asterisk
asterisk -rvv
asterisk -vvvvvr

yum install -y initscripts

docker container commit -m "Comment" faa2b9ec6018 hoanghd164/asterisk:16pbx

docker login -u hoanghd164 -p 'Ho@nghd90'
docker image ls
docker tag centos:centos7 hoanghd164/asterisk:16pbx
docker image ls
docker push hoanghd164/asterisk:16pbx

[100]
username=100
secret=1234
type=friend
host=dynamic
context=test
qualify=yes
directmedia=no
disallow=all
allow=ulaw,alaw

[101]
username=101
secret=1234
type=friend
host=dynamic
context=test
qualify=yes
directmedia=no
disallow=all
allow=ulaw,alaw


[test]
exten => _1XX,1,Dial(SIP/${EXTEN})