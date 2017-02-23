import csv
import requests
import time

#This module is responsible for request monitoring data, process and send it to the adapter.

# First: simulates the monitoring process by reading from the complete set file 



if __name__ == '__main__':

	string_temp = "http://143.54.12.174:9998/api/data" 
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

	with open('TR_Summarized.csv', 'rb') as f:
		lines = f.read().splitlines()[1:]

	for l in lines:
		temp=l.split(',')
		u_vm1 = float(temp[4])
		u_vm2 = float(temp[5])
		q_vm1 = float(temp[0])
		q_vm2 = float(temp[1])
		qu_vm1 = q_vm1/1500000.0
		qu_vm2 = q_vm2/1500000.0
		a_vm1 = float(temp[2])
		a_vm2 = float(temp[3])
		rt = float(temp[6])

		u_sum = (1.0/(1.01-u_vm1)) + (1.0/(1.01-u_vm2))
		q_sum = q_vm1 + q_vm2
		qu_sum = qu_vm1 + qu_vm2
		a_sum = a_vm1 + a_vm2

	
		message = '{"rts":[%f] ,"metrics":[[%f,%f,%f,%f]]}' % (rt,u_sum,a_sum,qu_sum,q_sum)
		print message
		r = requests.post(string_temp,data=message,headers=headers)
		time.sleep(0.1)


	time.sleep(5)
