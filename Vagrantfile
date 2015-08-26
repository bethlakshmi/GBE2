# -*- mode: ruby -*-
# vi: set ft=ruby :


$bootstrap = <<BOOTSTRAP
  sudo -s -H
  sudo apt-get update -y
  sudo apt-get install -y build-essential
  sudo apt-get install -y aria2 --no-install-recommends
  sudo wget https://raw.githubusercontent.com/ilikenwf/apt-fast/master/apt-fast
  sudo wget https://raw.githubusercontent.com/ilikenwf/apt-fast/master/apt-fast.conf
  sudo cp apt-fast /usr/bin/
  sudo chmod +x /usr/bin/apt-fast
  sudo cp apt-fast.conf /etc
  sudo apt-get install -y cachefilesd
  sudo echo "RUN=yes" > /etc/default/cachefilesd
  sudo apt-get install -y nfs-common portmap
  sudo apt-fast -y install git openssh-server li
  sudo apt-fast -y install git openssh-server libfreetype6-dev pkg-config
  sudo echo "mysql-server-5.5 mysql-server/root_password password root" | debconf-set-selections
  sudo echo "mysql-server-5.5 mysql-server/root_password_again password root" | debconf-set-selections
  sudo apt-fast -y install mysql-server-5.5
  sudo apt-fast -y install libmysqlclient-dev
  sudo apt-fast -y install mysql-client
  sudo useradd -m -g mysql mysql
  sudo chown -R vagrant /var/lib/
  sudo chown -R mysql /var/log/mysql
  sudo chown -R mysql /var/log/mysql


  sudo ssh-keyscan ssh-keygen -t rsa  -H github.com >> ~/.ssh/known_hosts
  sudo chmod 700 ~/.ssh
  # enable ssh agent forwarding
  sudo touch /etc/sudoers.d/root_ssh_agent
  sudo chmod 0440 /etc/sudoers.d/root_ssh_agent
  sudo echo "Defaults    env_keep += \"SSH_AUTH_SOCK\"" > /etc/sudoers.d/root_ssh_agent
  if [ -z "$SSH_AUTH_SOCK" ]; then
    echo "ssh agent not forwarded, aborting" >&2
    exit 1
  fi
  # make these known hosts to ssh
  sudo ssh -T git@bitbucket.org -o StrictHostKeyChecking=no
  sudo ssh -T git@github.com -o StrictHostKeyChecking=no
  sudo sed -i  '/requiretty/s/^/#/'  /etc/sudoers
  echo " 
  [mysqld]
  user=mysql
  server-id=$SERVER_ID
  default-storage-engine=innodb
  log-bin=mysql-bin
  max-allowed-packet=52m
  binlog-format=row
  open-files-limit=65535
  max-connections=500
  port=13306" >> /etc/my.cnf
  sudo chown -R mysql /var/lib/mysql/
  sudo /etc/init.d/mysql start
  #service mysql restart
  mysql -u root -proot -e "CREATE USER django_user IDENTIFIED BY 'secret'"
  mysql -u root -proot -e "DROP DATABASE IF EXISTS gbe_dev"
  mysql -u root -proot  -e "CREATE DATABASE gbe_dev"
  mysql -u root -proot  -e "USE gbe_dev"
  mysql -u root -proot  -e "GRANT ALL ON gbe_dev.* to 'django_user'@'%' IDENTIFIED BY 'secret' WITH GRANT OPTION"
  mysql -u root -proot  -e "GRANT ALL ON gbe_dev.* to 'django_user'@'%' IDENTIFIED BY 'secret'"
  mysql -u root -proot  -e "flush privileges"
 
  echo "your initialization shell scripts go here"
  sudo apt-fast -y install python-dev
  sudo apt-fast -y install python-pip
  sudo pip install --requirement /vagrant/config/requirements.txt
BOOTSTRAP


# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
   
  
 # config.vm.box = "chef/fedora-20"
  config.vm.box = "ubuntu/trusty64"
#  config.vm.box_url = "https://vagrantcloud.com/ubuntu/boxes/trusty64"

  config.vm.hostname = 'blueprint'

  config.ssh.forward_agent = true
  
  config.vm.provision :shell do |shell|
        shell.inline = "touch $1 && chmod 0440 $1 && echo $2 > $1"
            shell.args = %q{/etc/sudoers.d/root_ssh_agent "Defaults env_keep += \"SSH_AUTH_SOCK\""}
  end 
  
  config.vm.network :forwarded_port, guest: 8111, host: 8181, auto_correct: true

  config.vm.network "private_network", ip: "192.168.50.5", auto_config: true
  
  config.vm.synced_folder ".", "/vagrant"  #, type: "nfs", mount_options: ['rw', 'vers=3', 'tcp', 'fsc']  

  # add github.com to the list of known_hosts
  config.vm.provision :shell do |shell|
    shell.inline = "echo \"> SSH: add $2 to the list of known_hosts\" && ssh-keyscan -p $3 -H $2 >> $1 && chmod 600 $1"
    shell.args = %q{/etc/ssh/ssh_known_hosts github.com 22}
  end

  # bypass rsa fingerprint approbation
  config.vm.provision :shell do |shell|
    shell.inline = "echo -e \"Host $2\n\tStrictHostKeyChecking no\n\" >> $1"
    shell.args = %q{/etc/ssh/config *}
  end
  
  config.vm.provider "virtualbox" do |v| 
    host = RbConfig::CONFIG['host_os']
    # Give VM 1/4 system memory & access to all cpu cores on the host
    if host =~ /darwin/
      cpus = `sysctl -n hw.ncpu`.to_i
      # sysctl returns Bytes and we need to convert to MB
      mem = `sysctl -n hw.memsize`.to_i / 1024 / 1024 / 4
    elsif host =~ /linux/
      cpus = `nproc`.to_i
      # meminfo shows KB and we need to convert to MB
      mem = `grep 'MemTotal' /proc/meminfo | sed -e 's/MemTotal://' -e 's/ kB//'`.to_i / 1024 / 4
    else # sorry Windows folks, I can't help you
      cpus = 2
      mem = 1024
    end
    v.customize ["modifyvm", :id, "--vram", "10"]
    v.customize ["modifyvm", :id, "--memory", mem]
    v.customize ["modifyvm", :id, "--cpus", cpus]
  end

  if File.exists?(File.join(Dir.home, ".ssh", "id_rsa"))
      # Read local machine's GitHub SSH Key (~/.ssh/id_rsa)
      github_ssh_key = File.read(File.join(Dir.home, ".ssh", "id_rsa"))
      # Copy it to VM as the /root/.ssh/id_rsa key
      config.vm.provision :shell, :inline => "echo 'Copying local GitHub SSH Key to VM for provisioning...' && mkdir -p /root/.ssh && echo '#{github_ssh_key}' > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa"
  end
  if File.exists?(File.join(Dir.home, ".ssh", "id_rsa.pub"))
      github_ssh_key = File.read(File.join(Dir.home, ".ssh", "id_rsa.pub"))
      # Copy it to VM as the /root/.ssh/id_rsa.pub key
      config.vm.provision :shell, :inline => "echo 'Copying local public SSH Key to VM for provisioning...' && mkdir -p /root/.ssh && echo '#{github_ssh_key}' > /root/.ssh/id_rsa.pub && chmod 600 /root/.ssh/id_rsa.pub"
  end
  config.vm.network "private_network", type: "dhcp"

  config.vm.provision "shell", inline: $bootstrap,  privileged: true


end
