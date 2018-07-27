'''
Operating instructions

Basics
- ensure internet is on and working
- Applications > Utilities > Tweak Tool
	- set global dark theme to ON
- File browser > Preferences
	- view new folders using: list view
	- sort folders before files
	- show hidden and backup files

Command Line
- Open terminal, su to root
- wget -O linuxSetup.py http://caretaker.ingenuitystudios.com/dev/linuxSetup.py
- python linuxSetup.py all
- wait for ~45 min
- ensure command says "Ark Installation complete!"
- enter computer name at prompt, ex: grant_IE401
- log out, log back in, ready to go
'''


import os
import sys


# import argparse

def run(command):
	print command
	os.system(command)

def nvidia():

	# nVidia Drivers
	run('yum install kmod-nvidia -y')

def software():
	# VLC

# vlc.x86_64                            1:2.2.2-5.el7.nux              @nux-dextop
# vlc-core.x86_64                       1:2.2.2-5.el7.nux              @nux-dextop
	# General updates
	run('yum update -y')

	# Additional Repos
	run('yum -y install epel-release')
	run('rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org')
	run('rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm')
	run('yum -y install http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm')
	run('yum -y install http://linuxdownload.adobe.com/linux/x86_64/adobe-release-x86_64-1.0-1.noarch.rpm')

	run('yum -y install vlc')

	# Tiger VNC
	run('yum -y install tigervnc')

	# Open ssl stuff
	run('yum install openssl -y')
	run('yum install openssl-devel -y')

	# Mac drive support
	run('yum install kmod-hfsplus -y')

	# python stuff
	run('cd ~/Downloads')
	run('wget https://bootstrap.pypa.io/get-pip.py')
	run('python get-pip.py')
	run('yum install -y python-devel')
	run('pip install psutil')

	# Install compilers
	run('yum install -y make automake gcc gcc-c++ kernel-devel')

	# Sublime
	run('cd ~/Downloads')
	run('wget https://download.sublimetext.com/sublime_text_3_build_3126_x64.tar.bz2')
	run('tar -vxjf sublime_text_3_build_3126_x64.tar.bz2 /usr')
	run('ln -s /usr/sublime_text_3/sublime_text /usr/bin/sublime3')

def network():
	# Mount network drives
	run('yum -y install autofs')

	# make directory
	run('mkdir zfs')
	run('ln -s /zfs/ramburglar /ramburglar')
	run('ln -s /zfs/raidcharles /raidcharles')
	run('ln -s /zfs/footage /footage')
	run('ln -s /zfs/deadlinedata /deadlinedata')
	run('systemctl enable autofs')

# this bit of script is now handled below
	'''
nano /etc/auto.master

add a line like:

/zfs /etc/auto.zfs

nano /etc/auto.zfs

add:

ramburglar -fstype=cifs,rw,noperm,user=smb,pass=123456 ://172.16.0.10/ramburglar_work
raidcharles -fstype=cifs,rw,noperm,user=smb,pass=123456 ://172.16.0.12/raidcharles_work/work
footage -fstype=cifs,rw,noperm,user=ie,pass=123456 ://172.16.0.14/armory
deadlinedata -fstype=cifs,rw,noperm,user=smb,pass=a123456! ://172.16.0.54/repo

run:

service autofs restart
	'''

	# add /zfs /etc/auto.zfs to /etc/auto.master
	zfsMaster = '/etc/auto.master'
	found = False
	lines = []
	try:
		with open(zfsMaster) as f:
			lines = f.readlines()

		for line in lines:
			if '/zfs /etc/auto.zfs' in line:
				found = True
	except:
		# raise err
		pass

	if not found:
		lines.append('/zfs /etc/auto.zfs\n')

	with open(zfsMaster, 'w') as f:
		for line in lines:
			f.write(line)

	# add drive entries to /etc/auto.zfs
	driveEntries = {
		'ramburglar': 'ramburglar -fstype=cifs,rw,noperm,user=smb,pass=123456 ://172.16.0.10/ramburglar_work',
		'raidcharles': 'raidcharles -fstype=cifs,rw,noperm,user=smb,pass=123456 ://172.16.0.12/raidcharles_work/work',
		'footage': 'footage -fstype=cifs,rw,noperm,user=ie,pass=123456 ://172.16.0.14/armory',
		'deadlinedata': 'deadlinedata -fstype=cifs,rw,noperm,user=smb,pass=a123456! ://172.16.0.54/repo'
	}
	zfsAuto = '/etc/auto.zfs'
	lines = []
	try:
		with open(zfsAuto) as f:
			lines = f.readlines()

		keepers = []
		for line in lines:
			if line.split(' ')[0] not in driveEntries.keys():
				keepers.append(line)
		lines = keepers
	except:
		# raise err
		pass

	for driveEntry in driveEntries.values():
		lines.append(driveEntry + '\n')

	with open(zfsAuto, 'w') as f:
		for line in lines:
			f.write(line)

	# restart autofs
	run('service autofs restart')

def blackmagic():
	# Black magic drivers
	run('yum -y --enablerepo epel install dkms')
	os.chdir('/ramburglar/Assets/Software/Blackmagic/Blackmagic_Desktop_Video_Linux_10.8.2/rpm/x86_64/')
	run('yum install -y --nogpgcheck desktopvideo-10*.rpm desktopvideo-gui-*.rpm mediaexpress-*.rpm')
	# run('yum -y install -nogpgcheck ramburglar/Assets/Software/Blackmagic/Blackmagic_Desktop_Video_Linux_10.8.1/rpm/x86_64/desktopvideo-10.8.1-a2.x86_64.rpm')
	# run('yum -y install -nogpgcheck ramburglar/Assets/Software/Blackmagic/Blackmagic_Desktop_Video_Linux_10.8.1/rpm/x86_64/desktopvideo-gui-10.8.1-a2.x86_64.rpm')
	# run('yum -y install -nogpgcheck ramburglar/Assets/Software/Blackmagic/Blackmagic_Desktop_Video_Linux_10.8.1/rpm/x86_64/mediaexpress-3.5.2-a2.x86_64.rpm')


def bootConfig():
	run('yum install ntfs-3g -y')
	run('grub2-mkconfig -o /boot/grub2/grub.cfg')

def tools():
	run('bash /ramburglar/Assets/Tools/install/ie/ark/setup/installLinux')


def main(mode=None):

	if len(sys.argv) < 2:
		print 'Pick a mode, choices:'
		print 'all, nvidia, software, network, blackmagic, tools, boot'
		return

	if not mode:
		mode = sys.argv[1]

	mode = mode.lower()

	if mode == 'nvidia':
		nvidia()
	elif mode == 'software':
		software()
	elif mode == 'network':
		network()
	elif mode == 'blackmagic':
		blackmagic()
	elif mode == 'tools':
		tools()
	elif mode == 'boot':
		bootConfig()
	elif mode == 'all':
		software()
		nvidia()
		network()
		blackmagic()
		bootConfig()
		tools()
	else:
		print 'Invalid mode:', mode

if __name__ == '__main__':
	main()















# # Make the web user
# useradd -mrU web

# # Make the www directory where we'll put stuff
# mkdir /var/www
# chgrp web /var/www
# chown -R :web /var/www
# chmod -R g+w /var/www
# find /var/www -type d -exec chmod g+s '{}' \;

# # Install node.js and switch to the latest stable version
# yum install -y nodejs npm which
# npm install -g n
# n stable

# # setup up the Mongo rep
# echo -e "[mongodb]\nname=MongoDB Repository\nbaseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/\ngpgcheck=0\nenabled=1\n" > /etc/yum.repos.d/mongodb.repo

# # install mongo
# yum -y install mongodb-org

# # mongo settings
# ulimit -n 20480

# # mongo folder permissions
# mkdir -p /var/log/mongodb
# chown -R :web /var/log/mongodb
# chmod -R g+w /var/log/mongodb
# find /var/log/mongodb -type d -exec chmod g+s '{}' \;
# mkdir -p /var/lib/mongo
# chown -R :web /var/lib/mongo
# chmod -R g+w /var/lib/mongo
# find /var/lib/mongo -type d -exec chmod g+s '{}' \;

# # install git
# yum install -y git

# git config --global user.email "blented@gmail.com"
# git config --global user.name "Grant Miller"

# # install perl (typically already installed)
# yum install -y perl

# # copy ssh keys to web user
# mkdir -p /home/web/.ssh
# cp ~/.ssh/authorized_keys /home/web/.ssh/authorized_keys
# chown -R :web /home/web/.ssh
# chmod -R g+w /home/web/.ssh
# find /home/web/.ssh -type d -exec chmod g+s '{}' \;
# systemctl reload sshd

# # set up the swap file
# swapoff -a
# sudo dd if=/dev/zero of=/swapfile bs=1024 count=1024k
# sudo mkswap /swapfile
# sudo swapon /swapfile
# sudo printf '\n%s\n' '/swapfile       none    swap    sw      0       0 ' >> /etc/fstab
# echo 10 | sudo tee /proc/sys/vm/swappiness
# echo vm.swappiness = 10 | sudo tee -a /etc/sysctl.conf
# sudo chown root:root /swapfile
# sudo chmod 0600 /swapfile



