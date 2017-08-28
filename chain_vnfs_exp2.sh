#/bin/bash

echo chain vnfs
echo client-fw
echo iperfc-fw
son-emu-cli network add -b -src client:client-eth0 -dst fw:input
#son-emu-cli network add -b -src client:iperfc-eth0 -dst fw:input
echo fw-snort
son-emu-cli network add -b -src fw:output -dst snort:input
echo snort-server
son-emu-cli network add -b -src snort:output -dst server:server-eth0

