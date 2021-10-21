__author__ = "Edwin Dalmaijer"

import os
import numpy
import matplotlib
from matplotlib import pyplot, image
import copy
import itertools
import string

COLS = {	"butter": [	'#fce94f',
					'#edd400',
					'#c4a000'],
		"orange": [	'#fcaf3e',
					'#f57900',
					'#ce5c00'],
		"chocolate": [	'#e9b96e',
					'#c17d11',
					'#8f5902'],
		"chameleon": [	'#8ae234',
					'#73d216',
					'#4e9a06'],
		"skyblue": [	'#729fcf',
					'#3465a4',
					'#204a87'],
		"plum": 	[	'#ad7fa8',
					'#75507b',
					'#5c3566'],
		"scarletred":[	'#ef2929',
					'#cc0000',
					'#a40000'],
		"aluminium": [	'#eeeeec',
					'#d3d7cf',
					'#babdb6',
					'#888a85',
					'#555753',
					'#2e3436'],
		}
# FONT
FONT = {	'family': 'Ubuntu',
		'size': 12}
matplotlib.rc('font', **FONT)

def read_edf(filename, start, stop=None, missing=0.0, debug=False):
	try:
		f = open(filename, 'r')
	except:
		print("Error in read_edf: file '%s' does not exist" % filename)

	raw = f.readlines()[1:]
	f.close()

	data = []
	x = []
	y = []
	trial = {}
	events = {'Efix':[]}
	
	for line in raw:
		line_list = line.split(",")
		dur = int(line_list[4])
		events['Efix'].append(dur)
		x.append(float(line_list[5]))
		y.append(float(line_list[6]))
		if line=="":
			break

	trial['x'] = numpy.array(x)
	trial['y'] = numpy.array(y)
	trial['events'] = copy.deepcopy(events)
	data.append(trial)
	
	return data

def parse_fixations(fixations):
	fix = {
		'x':numpy.zeros(len(fixations)),
		'y':numpy.zeros(len(fixations)),
		'dur':numpy.zeros(len(fixations))
	}
	ex = []
	ey = []
	dur = []
	for fixnr in range(len(fixations)):
		ex.append(fixations[fixnr]['x'])
		ey.append(fixations[fixnr]['y'])
		dur.append(fixations[fixnr]['events']['Efix'])
	
	fix['x'] = numpy.array(list(itertools.chain.from_iterable(ex)))
	fix['y'] = numpy.array(list(itertools.chain.from_iterable(ey)))
	fix['dur'] = numpy.array(list(itertools.chain.from_iterable(dur)))

	return fix

def draw_fixations(fixations, dispsize, imagefile=None, durationsize=True, durationcolour=True, alpha=0.5, savefilename=None):
	fix = parse_fixations(fixations)
	fig, ax = draw_display(dispsize, imagefile=imagefile)
	
	dur = fix['dur']
	if durationsize:
		siz = dur
		# siz = [1* (num / 30.0) for num in dur]
		# siz = 1 * (fix['dur']/30.0)
	else:
		siz = numpy.median(dur)
	col = COLS['chameleon'][2]
	x = fix['x']
	y = fix['y']
	x_scale = numpy.interp(x, (x.min(),x.max()), (-dispsize[0]/2,dispsize[0]/2))
	y_scale = numpy.interp(y, (y.min(),y.max()), (-dispsize[1]/2,dispsize[1]/2))
	# ax.scatter(x,y, s=siz, c=col, marker='o', cmap='jet', alpha=alpha, edgecolors='none')
	ax.scatter(x_scale,y_scale, s=siz, c=col, marker='o', cmap='jet', alpha=alpha, edgecolors='none')
	ax.invert_yaxis()
	if savefilename != None:
		fig.savefig(savefilename)
	return fig

def draw_display(dispsize, imagefile=None):
	_, ext = os.path.splitext(imagefile)
	ext = ext.lower()
	data_type = 'float32' if ext == '.png' else 'uint8'
	screen = numpy.zeros((dispsize[1],dispsize[0],3), dtype=data_type)
	if imagefile != None:
		if not os.path.isfile(imagefile):
			raise Exception("ERROR in draw_display: imagefile not found at '%s'" % imagefile)
		img = image.imread(imagefile)
		img = numpy.flipud(img)
		# w, h = len(img[0]), len(img)
		# x = int(dispsize[0]/2 - w/2)
		# y = int(dispsize[1]/2 - h/2)
		# x = int(dispsize[0]/2 - w/2)
		# y = int(dispsize[1]/2 - h/2)		
		# screen[y:y+h,x:x+w,:] += img
		screen += img
	dpi = 100.0
	figsize = (dispsize[0]/dpi, dispsize[1]/dpi)
	fig = pyplot.figure(figsize=figsize, dpi=dpi, frameon=False)
	ax = pyplot.Axes(fig, [0,0,1,1]) # places a figure in the canvas that is exactly as large as the figure.
	ax.set_axis_off()
	fig.add_axes(ax)
	# ax.axis([-1,dispsize[0],-1,dispsize[1]])
	ax.imshow(screen, extent=(-dispsize[0]/2,dispsize[0]/2,-dispsize[1]/2,dispsize[1]/2))#, origin='upper')
	return fig,ax

def main():
	filename='2D_Processed_Eye_Data_Dining_Room.csv'
	imgname = '2D_Dining_Room.png'

	img = image.imread(imgname)
	width, height = len(img[0]), len(img)

	data = read_edf(filename, start=0, stop=None, missing=0.0, debug=False)
	draw_fixations(data,[width,height],imgname,durationsize=True,durationcolour=True,alpha=0.5,savefilename='test.png')

main()
