  
import itertools
import json

sqs = [''.join(s) for s in list(itertools.product(*[['0','1']] *12))]
widths = ['0','1','same']
directions = ["right","left","up","down"]
heights = ['2','3','same']

states = {}
for i in widths:
	for j in heights:
		for a in widths:
			for b in heights:
				for d in directions:
					for k in sqs:
						states[str((i,j,a,b,d,k))] = [0,0,0,0]

with open("qvalues.json", "w") as f:
	json.dump(states, f)