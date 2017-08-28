#/bin/bash

echo chain vnfs
echo client-fw
echo iperfc-fw
son-emu-cli network add -b -src client:client-eth0 -dst vnf1:input
#son-emu-cli network add -b -src client:iperfc-eth0 -dst fw:input
echo vnf1-vnf2
son-emu-cli network add -b -src vnf1:output -dst vnf2:input
echo vnf2-vnf3
son-emu-cli network add -b -src vnf2:output -dst vnf3:input
echo vnf3-server
son-emu-cli network add -b -src vnf3:output -dst server:server-eth0

