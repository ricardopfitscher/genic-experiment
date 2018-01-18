#!/bin/sh

#$1 is the upper limit for RT
#$2 is the lower Rt
#$3 is the higher throughput
#$4 is the lower throughput

#define here the range of values to summarize, please use the same than topology.py
START=0
END=3

#define here the path to logs
path=`/tmp/logs`

echo vm1r,vm2r,vm1c,vm2c,size,gvm1,gvm2,uvm1,uvm2,avm1,avm2,qvm1,qvm2,quvm1,quvm2,rt,thr >> summary.csv

echo 1,1,1,1,128KB,1,1,0.99,0.99,0.99,0.99,150000,150000,0.99,0.99,$1,$4 >> summary.csv
echo 1,1,1,1,128KB,1,1,0.99,0.99,0.99,0.99,150000,150000,0.99,0.99,$1,$4 >> summary.csv
echo 999,999,999,999,128KB,0.01,0.01,0.01,0.01,0.01,0.01,0,0,0.0,0.0,$2,$3 >> summary.csv
echo 999,999,999,999,128KB,0.01,0.01,0.01,0.01,0.01,0.01,0,0,0.0,0.0,$2,$3 >> summary.csv

for vm1r in 5 50 100 # set here the network bandwidth range for the firewall
do 
for vm2r in 5 50 100 # set here the network bandwidth range for the dpi
do 
for vm1c in 5 50 100 # set here the cpu capacity range for the firewall, 5 means 5% of one cpu
do 
for vm2c in 5 50 100 # set here the cpu capacity range for the dpi, 5 means 5% of one cpu
do 
for size in 128KB # set here the file sizes you configured 
do
for i in `seq $START $END`
do
	gvm1=`cut -f 2 $path/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	gvm2=`cut -f 2 $path/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	uvm1=`cut -f 3 $path/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	uvm2=`cut -f 3 $path/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	avm1=`cut -f 4 $path/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	avm2=`cut -f 4 $path/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	qvm1=`cut -f 5 $path/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	qvm2=`cut -f 5 $path/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	quvm1=`cut -f 6 $path/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	quvm2=`cut -f 6 $path/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	thr=`cat $path/log-rubis-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.html | sed -n 62'p' | awk {'print $5'} | tr '<B>' ' '| awk {'print $2'}`
	rt=`cat $path/logs/log-rubis-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.html | sed -n 61'p' | awk {'print $9'} | tr '<B>' ' '| awk {'print $2'}`
	echo $vm1r,$vm2r,$vm1c,$vm2c,$size,$gvm1,$gvm2,$uvm1,$uvm2,$avm1,$avm2,$qvm1,$qvm2,$quvm1,$quvm2,$rt,$thr >> summary.csv
done
done
done
done
done
done


