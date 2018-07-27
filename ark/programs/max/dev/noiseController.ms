objs = getCurrentSelection()
for s = 1 to objs.count do
(
	oPos = objs[s].pos
	str = oPos.z / 30 + 80
	objs[s].position.controller = noise_position frequency:.02 fractal:false noise_strength:[str,str,str] seed:s
	d = dummy name:(objs[s].name + "_offset")
	objs[s].parent = d
	d.pos = oPos	
	freeze d
	hide d
)