"""
Copyright (c) 2015 SONATA-NFV
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
"""

"""
README for the Who is Guilty? paper reproduction
The configurable parameteres are commented at each line. The following lines contains 
adjustable settings:
at line 86: define if the experiment is for RUBiS or Stratos workload
at line 94: number of cores that were provisioned to the VM
at line 95: range of repetitions 
at line 96: levels of the fw network bandwidth factor
at line 97: levels of the dpi network bandwidth factor
at line 98: requested file sizes for the Stratos workload (no influence to RUBiS)
at line 99: levels of the fw cpu capacity factor
at line 100: levels of the dpi cpu capacity factor
at line 122: waiting time, 180 for RUBiS and 100 for Stratos
"""

import subprocess
import logging
import time
from mininet.log import setLogLevel
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint
from mininet.node import RemoteController

logging.basicConfig(level=logging.INFO)


def create_topology1():
    # create topology
    net = DCNetwork(controller=RemoteController, monitor=False, enable_learning=False)
    dc1 = net.addDatacenter("dc1")
    dc2 = net.addDatacenter("dc2")
    s1 = net.addSwitch("s1")
    linkopts = dict(delay="1ms",bw=100)
    net.addLink(dc1, s1, **linkopts)
    net.addLink(dc2, s1, **linkopts)

    # add the command line interface endpoint to each DC (REST API)
    rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    rapi1.connectDCNetwork(net)
    rapi1.connectDatacenter(dc1)
    rapi1.connectDatacenter(dc2)
    # run API endpoint server (in another thread, don't block)
    rapi1.start()

    # add the SONATA dummy gatekeeper to each DC
    sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000)
    sdkg1.connectDatacenter(dc1)
    sdkg1.connectDatacenter(dc2)
    # run the dummy gatekeeper (in another thread, don't block)
    sdkg1.start()

    # start the emulation platform
    net.start()
    # create hosts and vnfs
    #use ./init_vnfs_rubis for rubis experiments
    #use ./init_vnfs for stratos experiments
    subprocess.call("./init_vnfs_exp3.sh",shell=True)
    subprocess.call("./chain_vnfs_exp3.sh",shell=True)

    vnf1, vnf2, vnf3, client, server = net.getNodeByName('vnf1','vnf2','vnf3','client','server')
    print "Waiting warmup"
    time.sleep(10)
    #run experiment
    #CONFIGURE number of cores
    cores = 4
    for i in range(0,1): #Set here the number of repetitions 
       for reqsize in ['128KB']: #available sizes are: '4KB','8KB','16KB','32KB','64KB','128KB','256KB','512KB','1024KB','2048KB','4096KB','8192KB','16384KB','32768KB']: 
          for vnf1cpu in [10,100]:  # set the cpu capacity for the vnf1
             for vnf2cpu in [10,100]: # set the cpu capacity for the vnf2
                for vnf3cpu in [10,100]: # set the cpu capacity for the vnf3, 5 means 5% of one cpu
                   for vnf1stress in [0,cores]:
                      for vnf2stress in [0,cores]:
		         for vnf3stress in [0,cores]:
			    r=0
			    vnf1.setParam(r,'setCPUFrac',cpu=vnf1cpu/(cores*100))
			    vnf2.setParam(r,'setCPUFrac',cpu=vnf2cpu/(cores*100))
			    vnf3.setParam(r,'setCPUFrac',cpu=vnf3cpu/(cores*100))
			    strcmd = "%s %d %d %d %d %s %d %d %d %d %d %s &" % ('./start_stress.sh',100,vnf1cpu,vnf2cpu,vnf3cpu,reqsize,i,vnf1stress,vnf2stress,vnf3stress,vnf1stress,'vnf1') 
			    vnf1.cmd(strcmd)
			    time.sleep(1)
			    strcmd = "%s %d %d %d %d %s %d %d %d %d %d %s &" % ('./start_stress.sh',100,vnf1cpu,vnf2cpu,vnf3cpu,reqsize,i,vnf1stress,vnf2stress,vnf3stress,vnf2stress,'vnf2') 
			    vnf2.cmd(strcmd)
			    time.sleep(1)
			    strcmd = "%s %d %d %d %d %s %d %d %d %d %d %s &" % ('./start_stress.sh',100,vnf1cpu,vnf2cpu,vnf3cpu,reqsize,i,vnf1stress,vnf2stress,vnf3stress,vnf3stress,'vnf3') 
			    vnf3.cmd(strcmd)
			    time.sleep(1)
			    strcmd = "%s %d %d %d %d %s %d %d %d %d &" % ('./start_server.sh',100,vnf1cpu,vnf2cpu,vnf3cpu,reqsize,i,vnf1stress,vnf2stress,vnf3stress) 
			    server.cmd(strcmd)
			    time.sleep(1)
			    client.cmd("ping -c 2 10.0.0.50 >> log-ping")
			    strcmd = "%s %d %d %d %d %s %d %d %d %d &" % ('./start_client.sh',100,vnf1cpu,vnf2cpu,vnf3cpu,reqsize,i,vnf1stress,vnf2stress,vnf3stress) 
			    client.cmd(strcmd)
			    #the parameter for iperfc is the target bandwidth
			    #strcmd = "%s %d" % ('./start_iperfc.sh',30)
			    #client.cmd(strcmd)
			    print "Waiting to the experiment %d-%d-%d-%d-%s-%d-%d-%d-%d"%(100,vnf1cpu,vnf2cpu,vnf3cpu,reqsize,i,vnf1stress,vnf2stress,vnf3stress) 
			    #use 180 for rubis workload
			    #use 100 for the stratos
			    time.sleep(100)
			    print "Copy results and cleanup"
			    strcmd = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no guiltiness* ubuntu@10.0.2.15:/home/ubuntu/son-emu/logs/"
			    vnf1.cmd(strcmd)
			    vnf2.cmd(strcmd)
    			    vnf3.cmd(strcmd)
			    strcmd = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no log* ubuntu@10.0.2.15:/home/ubuntu/son-emu/logs/"
			    client.cmd(strcmd)
			    server.cmd(strcmd)
			    vnf1.cmd("rm guiltiness*")
			    vnf2.cmd("rm guiltiness*")
    			    vnf3.cmd("rm guiltiness*")
			    client.cmd("rm log*")
			    server.cmd("rm log*")
    net.stop()


def main():
    setLogLevel('info')  # set Mininet loglevel
    create_topology1()


if __name__ == '__main__':
    main()
