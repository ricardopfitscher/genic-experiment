#/bin/bash

echo instantiate vnfs
echo client
son-emu-cli compute start -d dc1 -n client -i rjpfitscher/genic-rubis --net '(id=client-eth0,ip=10.0.0.10/24)'

echo firewall
son-emu-cli compute start -d dc2 -n fw -i rjpfitscher/genic-vnf --net '(id=input,ip=10.0.0.30/24),(id=output,ip=10.0.0.31/24)'

echo snort
son-emu-cli compute start -d dc2 -n snort -i rjpfitscher/genic-vnf --net '(id=input,ip=10.0.0.40/24),(id=output,ip=10.0.0.41/24)'

echo web
son-emu-cli compute start -d dc2 -n server -i rjpfitscher/genic-rubis --net '(id=server-eth0,ip=10.0.0.50/24)'
