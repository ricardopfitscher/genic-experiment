#!/bin/sh

#$1 is the upper limit for RT
#$2 is the lower Rt
#$3 is the higher throughput
#$4 is the lower throughput

START=0
END=3

echo vm1r,vm2r,vm1c,vm2c,size,gvm1,gvm2,uvm1,uvm2,avm1,avm2,qvm1,qvm2,quvm1,quvm2,rt,thr >> summary.csv

echo 1,1,1,1,128KB,1,1,0.99,0.99,0.99,0.99,150000,150000,0.99,0.99,$1,$4 >> summary.csv
echo 1,1,1,1,128KB,1,1,0.99,0.99,0.99,0.99,150000,150000,0.99,0.99,$1,$4 >> summary.csv
echo 999,999,999,999,128KB,0.01,0.01,0.01,0.01,0.01,0.01,0,0,0.0,0.0,$2,$3 >> summary.csv
echo 999,999,999,999,128KB,0.01,0.01,0.01,0.01,0.01,0.01,0,0,0.0,0.0,$2,$3 >> summary.csv

for vm1r in 5 10 50 100
do 
for vm2r in 5 10 50 100
do 
for vm1c in 5 10 50 100
do 
for vm2c in 5 10 50 100
do 
for size in 128KB
do
for i in `seq $START $END`
do
	gvm1=`cut -f 2 ../logs/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	gvm2=`cut -f 2 ../logs/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	uvm1=`cut -f 3 ../logs/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	uvm2=`cut -f 3 ../logs/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	avm1=`cut -f 4 ../logs/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	avm2=`cut -f 4 ../logs/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	qvm1=`cut -f 5 ../logs/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	qvm2=`cut -f 5 ../logs/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	quvm1=`cut -f 6 ../logs/guiltiness-fw-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	quvm2=`cut -f 6 ../logs/guiltiness-snort-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i.log.dat |./est-media.awk `
	thr=`cut -f 1 -d , ../logs/log-stratos-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i | cut -f 2 -d : | ./est-media.awk `
	rt=`cut -f 2 -d , ../logs/log-stratos-$vm1r-$vm2r-$vm1c-$vm2c-$size-$i | cut -f 2 -d : | ./est-media.awk `
	echo $vm1r,$vm2r,$vm1c,$vm2c,$size,$gvm1,$gvm2,$uvm1,$uvm2,$avm1,$avm2,$qvm1,$qvm2,$quvm1,$quvm2,$rt,$thr >> summary.csv
done
done
done
done
done
done


