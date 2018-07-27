--//Automatic Morphers
originalObjs = getCurrentSelection()
c = Bezier_Float()
for o in originalObjs do
(
	o.name = uniqueName "tv_"
	newObj = copy o
	newObj.name = o.name + "_thinBorder"
	newObj.wireColor = o.wireColor
	newObj.pos.y += 200
	m = Morpher()
	addModifier o m	
	m.Autoload_of_targets = 1
	WM3_MC_BuildFromNode m 1 newObj
    WM3_MC_Rebuild m 1
	--m[1].controller = c
)
$morphControl.height.controller = c

originalObjs = getCurrentSelection()
d = Bezier_Float()
for o in originalObjs do
(	
	newObj = copy o
	ConvertTo newObj Editable_Poly
	newObj.name = o.name + "_thickness"
	newObj.wireColor = o.wireColor
	newObj.pos.y += 400	
	m = o.modifiers["Morpher"]
	if m != undefined then
	(
		WM3_MC_BuildFromNode m 2 newObj
		WM3_MC_Rebuild m 2
	)
	--m[1].controller = c
)
$CTRL_thickness.height.controller = d


--//morpher controller instancing
d = Bezier_Float()
for s in $ do
(
	m = s.modifiers["Morpher"]
	m[2].controller = d
)
$CTRL_thickness.height.controller = d

--//birth offsetting
births = for s in $* where classof s == Birth collect s
for b in births do
(
	b.Emit_start += f*ticksperframe
	b.Emit_Stop += 2*ticksperframe
)


for s in $ do
(
	s.modifiers[1][1].controller = $CTRL_border.height.controller
	s.modifiers[1][2].controller = $CTRL_thickness.height.controller
)