#-*-coding:utf-8-*-
import sys
sys.path.insert(0, "/Users/zengzhaoyang/Documents/github/caffe_zzy/python")
import caffe
import json
from flask import Flask, request, jsonify
import requests
import time

caffe.set_mode_cpu()
model_def = 'classifier_template.prototxt'
model = 'classifier_googlenet_25M.caffemodel'

net = caffe.Net(model_def, model, caffe.TEST)
layer = net.layers[0]

namelist = []
f = open('classifier_namelist.txt', 'r')
for line in f:
	namelist.append(line.strip())

app = Flask(__name__)
app.debug = True

@app.route('/reco', methods=['POST'])
def reco():
	imgdata = request.files['file']
	filename = '/Users/zengzhaoyang/Downloads/hackfdu/python/tmp.jpg'
	imgdata.save(filename)

	layer.setImgPath(filename, 0)
	net.forward()
	net.forward()

	feature = net.blobs['prob'].data[0]

	q = []
	for i in range(109):
		q.append((feature[i], i))
	q = sorted(q, reverse=True)

	res = [
		{
			'tag':namelist[q[0][1]],
			'score':int(q[0][0] * 100)
		},
		{
			'tag':namelist[q[1][1]],
			'score':int(q[1][0] * 100)
		},
		{
			'tag':namelist[q[2][1]],
			'score':int(q[2][0] * 100)
		}
	]

	res = json.dumps(res)


	res2 = [
		{
			'tag':q[0][1],
			'score':int(q[0][0] * 100)
		},
		{
			'tag':q[1][1],
			'score':int(q[1][0] * 100)
		},
		{
			'tag':q[2][1],
			'score':int(q[2][0] * 100)
		},
		{
			'tag':q[3][1],
			'score':int(q[3][0] * 100)
		}
	]
	url = 'http://10.221.64.133:8080/change'
	para = {
		'data':json.dumps(res2)
	}
	r = requests.post(url, data=para)
	time.sleep(2)
	return res

# path = '/Users/zengzhaoyang/Downloads/image/0/0.jpg'
# layer.setImgPath(str(path), 0)
# net.forward()
# net.forward()

# print net.blobs['prob'].data[0]

if __name__ == '__main__':
	app.run('0.0.0.0', 5000)
