import csv
import requests
import time

#This module is responsible for request monitoring data, process and send it to the adapter.

# First: simulates the monitoring process by reading from the complete set file 



if __name__ == '__main__':

	string_temp = "http://127.0.0.1:9998/api/data" 
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

	with open('TR_Summarized.csv', 'rb') as f:
		lines = f.read().splitlines()[1:]

	for l in lines:
		temp=l.split(',')
		t1 = float(temp[0])
		t2 = float(temp[1])
		t3 = float(temp[2])
		t4 = float(temp[3])
		t5 = float(temp[4])
		rt = float(temp[5])


		message = '{"rts":[%f] ,"metrics":[[%f,%f,%f,%f,%f]]}' % (rt,t1,t2,t3,t4,t5)
		print message
		r = requests.post(string_temp,data=message,headers=headers)
		time.sleep(1)


	time.sleep(5)
