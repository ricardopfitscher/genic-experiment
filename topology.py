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
A simple topology with two PoPs for the y1 demo story board.

        (dc1) <<-->> s1 <<-->> (dc2)
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
    linkopts = dict(delay="10ms",bw=100)
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
    subprocess.call("./init_vnfs.sh",shell=True)
    subprocess.call("./chain_vnfs.sh",shell=True)

    fw, snort, client, server = net.getNodeByName('fw','snort','client','server')
    print "Waiting warmup"
    time.sleep(10)
    #run experiment
    
    for i in range(0,1):
       for fwbw in [10]:#,25,50,75,100]:#20,30,40,50,60,70,80,90,100]:
          for snortbw in [10]:#,25,50,75,100]:#20,30,40,50,60,70,80,90,100]:
             for reqsize in ['2KB','32KB','1024KB','32768KB']:#,'4KB','8KB','16KB','32KB','64KB','128KB','256KB','512KB','1024KB','2048KB','4096KB','8192KB','16384KB','32768KB']: 
                #inputs: fwbw snortbw reqsize iteration
                strcmd = "%s %d %d %s %d &" % ('./start_firewall.sh',fwbw,snortbw,reqsize,i) 
                fw.cmd(strcmd)
                time.sleep(1)    
                strcmd = "%s %d %d %s %d &" % ('./start_snort.sh',fwbw,snortbw,reqsize,i)
                snort.cmd(strcmd)
                strcmd = "%s %d %d %s %d &" % ('./start_server.sh',fwbw,snortbw,reqsize,i)
                server.cmd(strcmd)
                time.sleep(5)
                client.cmd("ping -c 2 10.0.0.50 >> log-ping")
                client.cmd("ping -c 2 10.0.0.50 >> log-ping")
                strcmd = "%s %d %d %s %d &" % ('./start_client.sh',fwbw,snortbw,reqsize,i)
                client.cmd(strcmd)
                strcmd = "%s" % ('./start_iperfc.sh')
                client.cmd(strcmd)
                print "Waiting 90 seconds to experiments to be finished"
                time.sleep(90)
                print "Copy results and cleanup"
                strcmd = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no guiltiness* vagrant@10.0.2.15:/home/vagrant/son-emu/logs/"
                fw.cmd(strcmd)
                snort.cmd(strcmd)
                strcmd = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no log* vagrant@10.0.2.15:/home/vagrant/son-emu/logs/"
                client.cmd(strcmd)
                server.cmd(strcmd)
                fw.cmd("rm guiltiness*")
                snort.cmd("rm guiltiness*")
                client.cmd("rm log*")
                server.cmd("rm log*")
    net.CLI()
    net.stop()


def main():
    setLogLevel('info')  # set Mininet loglevel
    create_topology1()


if __name__ == '__main__':
    main()
