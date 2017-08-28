#/bin/bash

echo instantiate vnfs
echo client
son-emu-cli compute start -d dc1 -n client -i rjpfitscher/genic-rubis --net '(id=client-eth0,ip=10.0.0.10/24)'

echo vnf1
son-emu-cli compute start -d dc2 -n vnf1 -i rjpfitscher/genic-vnf --net '(id=input,ip=10.0.0.30/24),(id=output,ip=10.0.0.31/24)'

echo vnf2
son-emu-cli compute start -d dc2 -n vnf2 -i rjpfitscher/genic-vnf --net '(id=input,ip=10.0.0.40/24),(id=output,ip=10.0.0.41/24)'

echo vnf3
son-emu-cli compute start -d dc2 -n vnf3 -i rjpfitscher/genic-vnf --net '(id=input,ip=10.0.0.60/24),(id=output,ip=10.0.0.61/24)'


echo web
son-emu-cli compute start -d dc2 -n server -i rjpfitscher/genic-rubis --net '(id=server-eth0,ip=10.0.0.50/24)'
