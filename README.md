# Guiltiness: experiments reproduction

To perform guiltiness experiments, some packages are required in the host environment (the one in which the virtual machine runs). These packages can be installed through the following commands: 
```
$ apt-get install git-core vagrant virtualbox
```

# Results reproducibility

After packages installation, the next step is to download, configure and run the SONATA emulation platform (keep in mind that this process may take some time):

```
$ git clone https://github.com/sonata-nfv/son-emu.git
$ cd son-emu
$ vagrant up
```

Configure the VM's memory and CPU capacity according to your environment specifities:

```
$ nano Vagrantfile
# at line 93:
# vb.memory = 8192 
# vb.cpus = 4
$ vagrant reload
```
Sometimes it is necessary to resize disk space.

```
$ VBoxManage clonehd "source.vmdk" "cloned.vdi" --format vdi
$ VBoxManage modifyhd "cloned.vdi" --resize 20480
$ VBoxManage clonehd "cloned.vdi" "resized.vmdk" --format vmdk
```

Next, prepare the virtual environment to run the experiments, for that, we must login into the VM, download the docker images, and copy the .ssh public keys of the docker images to the VM’s authorized_keys file:

```
$ vagrant ssh
$ sudo docker pull rjpfitscher/genic-rubis
$ sudo docker pull rjpfitscher/genic-vnf
$ sudo docker run -t -i rjpfitscher/genic-rubis /bin/bash
# public key is in /root/.ssh/id_rsa.pub
$ exit
# the same for the genic-vnf:
$ sudo docker run -t -i rjpfitscher/genic-vnf /bin/bash
# public key is in /root/.ssh/id_rsa.pub
$ exit
# copy the keys to authorized keys files
# authorized\_keys is at ~/.ssh/authorized\_keys
nano ~/.ssh/authorized\_keys
# also, create logs folder to store results:
$ cd son-emu
$ mkdir logs
```

As soon as the docker images are ready, the next step is to download the experiment scripts and copy the stable version of the SONATA files. SONATA is currently being implemented by third-party developers, therefore some changes on their code can influence our experiments, thus, we mantain a copy of some files in a stable version for our experiment. These files must be copied to the appropriate directory:

```
$ git clone https://github.com/ricardopfitscher/genic-experiment
$ cd genic-experiment
$ cp network.py ../src/emuvim/api/rest/
$ cp rest_api_endpoint.py ../src/emuvim/api/rest/ 
```

Next, one can configure the experimentation setup regarding the number of iterations, VNFs' capacities, and workload. For doing that, one must modify the topology.py file. Once configured, the experiments are ready to run.

```
$ nano topology.py
$ sudo python topology.py
```

When the experiments are finished, we need to summaryze results. We insert reference values to the data, which define the upper and lower bound limits of the end-service performance. These limits are arguments for the summarization script. Furthermore, one should edit the summarize-rubis.sh file to reflect the experiments setup (topology.py).

```
$ nano summarize-rubis.sh
# $1 is the upper limit for RT
# $2 is the lower Rt
# $3 is the higher throughput
# $4 is the lower throughput
$ sh summarize-rubis.sh 8000 1000 60 1
```

One can notice that the summarize-stratos.sh file was also provided. We encourage researchers to replicate the experiments using the workload from the Stratos related work. For doing that, follow the instructions inside the topology.py to select the mentioned workload, and then run appropriate summarization script.   

Finally, the last step to reproduce our plots consists of running the Rscripts. As the the son-emu folder is shared between VM and host environment, this process can be done outside the VM. By running at the host, it helps to visualize and copy the resultant figures. Some additional packages are required to run R and the current implementation of the learning server in Python. To perform the additional installations, run the following commands:

```
$ exit # if one wants to run outside VM
$ sudo apt-get install r-base
$ sudo apt-get install python-pip python-dev build-essential 
$ sudo apt-get install r-cran-plyr r-cran-ggplot2
$ sudo pip install scikit-learn numpy scipy cherrypy matplotlib
$ sudo pip install scikit-neuralnetwork requests
$ Rscript ploter.R
```

# Results repeatability

We also provide our raw data to allow researchers to analyze our results and produce the plots presented in the paper. This content is at the rubis.csv file inside the genic-experiment folder. Run replicate.R to produce the plots:

```
$ cd genic-experiment
$ Rscript replicate.R
```
