from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.naive_bayes import GaussianNB
import threading
import cherrypy
import requests
import csv
import json
import numpy as np
import scipy
from scipy.optimize import curve_fit
DEBUG = True

fitted = False
nn_threshold = 0.8 #threshold for update the learn
metricsNN = [] # metrics for Neural Networks [U,A,Qu,Q,Rt]
coefNN = []  #Coefficients for Neural Networks [c1,c2,c3,c4]
metrics = [] #For nonlinear regression [U,A,Qu,Q]
respTime = [] #For nonlinear regression
monitors = []
currentRsquare = 0.0 # Current best value for Rsquare
currentCoefficients = [0.0025, 0.0025, 0.0025, 0.0025, 0.1] # Current best values for coefficients [c1,c2,c3,c4]
defaultCoefficients = [0.0025, 0.0025, 0.0025, 0.0025, 0.1]
historic = {'c1':[],'c2':[],'c3':[],'c4':[],'c5':[],'rsquared':[]}

clf = MLPRegressor(solver='lbfgs', alpha=1e-5, random_state=1, activation='tanh', hidden_layer_sizes=(100,5), learning_rate = 'adaptive')
#clf = MLPRegressor()

frontpage = """<html>
	<head></head>
	<meta http-equiv="refresh" content="40">
		<body>
			<form method="get" action="addMonitoringData">
				<input type="text" value="" name="name"/>
				<button type="submit">Add a parameter</button>
			</form>
			<table style=\"width:100%\"> 
				<caption>Monitoring Data</caption>
				<tr><td>Normalized Response Time</td><td>Guiltiness</td><td>[U,A,Qu,Q]</td></tr>
			"""

def adjust_coeff(t1,t2,t3,t4,t5,Rt):
	global clf
	global defaultCoefficients
	tmpCoefficients = defaultCoefficients
	tmpEst = guiltiness([t1,t2,t3,t4,t5],tmpCoefficients[0],tmpCoefficients[1],tmpCoefficients[2],tmpCoefficients[3],tmpCoefficients[4])
	ratio = tmpEst/Rt

	while ratio < 0.95:
		tmpCoefficients[1] += 0.01
		tmpCoefficients[0] += 0.01
		tmpEst = guiltiness_computing([t1,t2,t3,t4,t5],tmpCoefficients[0],tmpCoefficients[1],tmpCoefficients[2],tmpCoefficients[3],tmpCoefficients[4])
		ratio = tmpEst/Rt

	while ratio >= 1.05:
		tmpCoefficients[0] -= 0.01
		tmpCoefficients[1] -= 0.01
		tmpEst = guiltiness_computing([t1,t2,t3,t4,t5],tmpCoefficients[0],tmpCoefficients[1],tmpCoefficients[2],tmpCoefficients[3],tmpCoefficients[4])
		ratio = tmpEst/Rt


	return [tmpCoefficients[0],tmpCoefficients[1],tmpCoefficients[2],tmpCoefficients[3],tmpCoefficients[4]]



def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return r_value**2

def guiltiness(x, c1,c2,c3,c4,c5): #for non linear regression
	#return  2*(c1*x[0] + c2*x[1] + c3*x[2] + c4*(x[1]/(1+x[3])))
	return  c1*x[0] + c2*x[1] + c3*x[2]+ c4*x[3] + c5*x[4] 


def guiltiness_computing(x, c1,c2,c3,c4,c5): # for save values
	
	#value = 2*(c1*x[0] + c2*x[1] + c3*x[2] + c4*(x[1]/(1+x[3])))
	value = c1*x[0] + c2*x[1] + c3*x[2]+ c4*x[3] + c5*x[4] 
	if value >= 1:
		return 1.0
	elif value <= 0:
		return 0.0
	else:
		return value


def coeff_average():
	c1 = 0
	c2 = 0
	c3 = 0 
	c4 = 0
	c5 = 0
	for x in coefNN:
		c1 += x[0]
		c2 += x[1]
		c3 += x[2]
		c4 += x[3]
		c5 += x[4]
	tam = len(coefNN)
	return [c1/tam,c2/tam,c3/tam,c4/tam,c5/tam]


def add_data(t1,t2,t3,t4,t5,Rt):
	global currentRsquare
	global currentCoefficients
	global clf
	global fitted
	metrics.append([t1,t2,t3,t4,t5])
	if DEBUG: print "METRICS:", metrics
	respTime.append(Rt)
	nn_rsquared = 0.0
	ann_rsquared = 0.0

	if len(metricsNN) > 10:
		nnPrediction = clf.predict([[t1,t2,t3,t4,t5,Rt]])
		fitted = True

	if fitted:	
	# Neural Networks R-squared
		estimated = []
		for value in metrics:
			tmp = guiltiness_computing(value,nnPrediction[0][0],nnPrediction[0][1],nnPrediction[0][2],nnPrediction[0][3],nnPrediction[0][4])
			estimated.append(tmp)
		nn_rsquared = rsquared(estimated,respTime)
		if DEBUG: print "NN rsquared: ", nn_rsquared
	
	# Averaged NN coefficients R-Squared:
		estimated = []
		tmpCoefficients = coeff_average()
		for value in metrics:
			tmp = guiltiness_computing(value,tmpCoefficients[0],tmpCoefficients[1],tmpCoefficients[2],tmpCoefficients[3],tmpCoefficients[4])
			estimated.append(tmp)
		ann_rsquared = rsquared(estimated,respTime)
		if DEBUG: print "ANN rsquared: ", ann_rsquared

	#LINEAR REGRESSION TESTING:
	popt, pcov = linear_regression()
	estimated = []
	for value in metrics:
		tmp = guiltiness_computing(value,popt[0],popt[1],popt[2],popt[3],popt[4])
		estimated.append(tmp)
	lr_rsquared = rsquared(estimated,respTime)
	if DEBUG: print "LR rsquared: ", lr_rsquared

	#CURRENT VALUE TESTING:
	estimated = []
	for value in metrics:
		if DEBUG: print "Current_Coefficients: ", currentCoefficients
		tmp = guiltiness_computing(value,currentCoefficients[0],currentCoefficients[1],currentCoefficients[2],currentCoefficients[3],currentCoefficients[4])
		if DEBUG: print "TMP line 151:",tmp
		estimated.append(tmp)
	cc_rsquared = rsquared(estimated,respTime)
	if DEBUG: print "Previous coefficients rsquared: ", cc_rsquared

	#Default VALUE TESTING:
	estimated = []
	for value in metrics:
		tmp = guiltiness_computing(value,defaultCoefficients[0],defaultCoefficients[1],defaultCoefficients[2],defaultCoefficients[3],defaultCoefficients[4])
		estimated.append(tmp)
	de_rsquared = rsquared(estimated,respTime)
	if DEBUG: print "Default coefficients rsquared: ", de_rsquared

	if lr_rsquared > nn_rsquared and lr_rsquared > ann_rsquared and lr_rsquared > cc_rsquared:
		currentRsquare = lr_rsquared
		currentCoefficients = [popt[0],popt[1],popt[2],popt[3],popt[4]]
	elif nn_rsquared > lr_rsquared and nn_rsquared > ann_rsquared and nn_rsquared > cc_rsquared: #nn_rsquared > lr_rsquared and
		currentRsquare = nn_rsquared
		currentCoefficients = [nnPrediction[0][0],nnPrediction[0][1],nnPrediction[0][2],nnPrediction[0][3],nnPrediction[0][4]] 
	elif ann_rsquared > lr_rsquared and ann_rsquared > nn_rsquared and ann_rsquared > cc_rsquared: #ann_rsquared > lr_rsquared and 
		currentRsquare = ann_rsquared
		currentCoefficients = [tmpCoefficients[0],tmpCoefficients[1],tmpCoefficients[2],tmpCoefficients[3],tmpCoefficients[4]]
	else:
		currentRsquare = cc_rsquared


	#If the rsquared of linear regression is greater than a threshold, than this value is inserted into the neural network base
	if lr_rsquared >= 0.8:
		metricsNN.append([t1,t2,t3,t4,t5,Rt])
		coefNN.append([popt[0],popt[1],popt[2],popt[3],popt[4]])
		clf.fit(metricsNN,coefNN)

	if nn_rsquared >= 0.8:
		metricsNN.append([t1,t2,t3,t4,t5,Rt])
		coefNN.append([nnPrediction[0][0],nnPrediction[0][1],nnPrediction[0][2],nnPrediction[0][3],nnPrediction[0][4]])
		clf.fit(metricsNN,coefNN)


	if DEBUG: print "Current rsquared:", currentRsquare
	if DEBUG: print "Current Coefficients:", currentCoefficients

	historic['c1'].append(currentCoefficients[0])
	historic['c2'].append(currentCoefficients[1])
	historic['c3'].append(currentCoefficients[2])
	historic['c4'].append(currentCoefficients[3])
	historic['c5'].append(currentCoefficients[4])
	historic['rsquared'].append(currentRsquare)
	tam = len(historic['rsquared'])

	with open('historic.csv', 'w') as csvfile:
		fieldnames = ['c1', 'c2', 'c3', 'c4', 'c5', 'rsquared']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writerow({'c1':currentCoefficients[0], 'c2':currentCoefficients[1], 'c3':currentCoefficients[2], 'c4':currentCoefficients[3], 'c5':currentCoefficients[4], 'rsquared':currentRsquare})
	
	for m in monitors:
		m.update(currentCoefficients[0],currentCoefficients[1],currentCoefficients[2],currentCoefficients[3],currentCoefficients[4])

	

def linear_regression():
	x0    = np.array([0.0,0.0,0.0,0.0,0.0])
	xdata = np.array(metrics)
	xdata = np.transpose(xdata)
	ydata = np.array(respTime)
	param_bounds=([0,0,0,0,0],[1.,1.,1.,1.,1.])
	return curve_fit(guiltiness, xdata, ydata,  bounds=param_bounds)


def learning_phase():
	return clf.fit(metricsNN,coefNN) 


def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

class Monitor():
	def __init__(self, url):
		self.url = url #"http://143.54.12.174:9999/api/data"
		self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

	def update(self,c1,c2,c3,c4,c5):
		message = '{"c1":%f, "c2":%f, "c3":%f, "c4":%f, "c5":%f}' % (c1,c2,c3,c4,c5)
		r = requests.post(self.url,data=message,headers=self.headers)

	def collect(self):
		r = requests.get(self.url)
		if DEBUG: print json.dumps(r.text)


class Data:
	exposed = True
	@cherrypy.tools.json_out()
	def GET(self):
		returnData = {'rts':[],'metrics':[]}
		for line in range(len(metrics)):
			returnData['rts'].append(respTime[line]),
			returnData['metrics'].append(metrics[line])
		return returnData

	#add_data(0.24,0.66,0.0043645545,6546,0.94) [0.24,0.66,0.0043645545,6546,0.94]
	#curl -H "Content-Type: application/json" -X POST -d '{"rts":[rt] ,"metrics":[[U,A,Qu,Q]]}' http://143.54.12.174:9999/api/data
	#curl -H "Content-Type: application/json" -X POST -d '{"rts":[0.94] ,"metrics":[[0.24,0.66,0.0043645545,6546]]}' http://143.54.12.174:9999/api/data
	@cherrypy.tools.json_in()
	def POST(self):
		data = cherrypy.request.json
		inputData = {'rts':[],'metrics':[]}
		inputData = data
		if DEBUG: print "webserver inputed data:", inputData
		for line in range(len(inputData['rts'])):
			add_data(inputData['metrics'][line][0],inputData['metrics'][line][1],inputData['metrics'][line][2],inputData['metrics'][line][3],inputData['metrics'][line][4],inputData['rts'][line])


class Agent:
	exposed = True
	@cherrypy.tools.json_out()
	def GET(self):
		returnData = {'rts':[],'metrics':[]}
		for line in range(len(metrics)):
			returnData['rts'].append(respTime[line]),
			returnData['metrics'].append(metrics[line])
		return returnData

	#curl -d url='http://host:9999/api/data'  -X POST 'http://host:9998/api/agent'
	def POST(self, url):
		try:
			if DEBUG: print url
			m = Monitor(url)
			monitors.append(m)
			return 'Ok'
		except:
			return 'Error'

class AgentInterface(object):

	@cherrypy.expose
	def index(self):

		temp = ''
		g_value = 0.0 #temp guiltiness value
		for line in range(len(metrics)):
			g_value = guiltiness_computing(metrics[line],currentCoefficients[0],currentCoefficients[1],currentCoefficients[2],currentCoefficients[3],currentCoefficients[4])
			temp+="<tr><td>"+str(respTime[line])+"</td>"+"<td>"+str(g_value)+"</td>"+"<td>"+str(metrics[line])+"</td>"+"</tr>"
		temp += "</table>"
		modelInfo = """	<table style=\"width:100%\"> 
				        <caption>Guiltiness Model Info</caption>
						<tr><td>R-Squared</td><td>Coefficients</td></tr>"""	
		modelInfo+= "<tr><td>"+str(currentRsquare)+"</td><td>"+str(currentCoefficients)+"</td></tr></table>"		

		return frontpage+temp+modelInfo+"</body></html>"


if __name__ == '__main__':

	conf = {
		'/': {
		'tools.sessions.on': True
		}
	}

	cherrypy.tree.mount(
    	Data(), '/api/data',
		{'/':
			{'request.dispatch': cherrypy.dispatch.MethodDispatcher(),'tools.CORS.on': True}
		}
	)

	cherrypy.tree.mount(
    	Agent(), '/api/agent',
		{'/':
			{'request.dispatch': cherrypy.dispatch.MethodDispatcher(),'tools.CORS.on': True}
		}
	)

	with open('historic.csv', 'w') as csvfile:
		fieldnames = ['c1', 'c2', 'c3', 'c4', 'rsquared']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()

	cherrypy.tree.mount(AgentInterface(), '/', conf)
	cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
	cherrypy.config.update({'server.socket_host': '127.0.0.1','server.socket_port': 9998}) 
	cherrypy.engine.start()
	cherrypy.engine.block()

	
	


