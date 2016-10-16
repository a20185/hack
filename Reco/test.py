#-*-coding:utf-8-*-
import sys
sys.path.insert(0, "/Users/zengzhaoyang/Documents/github/caffe_zzy/python")
import caffe

from flask import Flask, request

caffe.set_mode_cpu()
model_def = 'deploy.prototxt'
model = 'simple_googlenet_iter_394.caffemodel'

net = caffe.Net(model_def, model, caffe.TEST)
layer = net.layers[0]
cnt = 0

app = Flask(__name__)
app.debug = True

@app.route('/upload', methods=['POST'])
def upload():
	files = request.files['fileUpload']
	files.save('tmp.png')
	layer.setImgPath('/Users/zengzhaoyang/Downloads/hackfdu/temp/tmp.png', 0)
	net.forward()
	net.forward()

	feature = net.blobs['prob'].data[0]
	q = []
	for i in range(10):
		q.append((feature[i], i))
	q = sorted(q, reverse=True)
	name = ['sheep', 'cat', 'dog', 'fish', 'bird', 'elephant', 'horse', 'rabbit', 'pig', 'iii']
	

	# print q
	temp = [1, 3, 4, 8]
	# global cnt
	# res = name[temp[cnt%4]]
	# cnt += 1
	# return res
	if q[0][1] in temp:
		return name[q[0][1]]
	else:
		import random
		r = random.randint(0, 4)
		return name[temp[r]]
	# return 'pig'


if __name__ == '__main__':
	app.run('0.0.0.0', 8000)

