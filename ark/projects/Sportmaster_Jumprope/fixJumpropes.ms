ropes = getCurrentSelection()
matRef = Maxwell_Material__Ref FileName: "Q:\\Sportmaster_Jumprope\\Project_Assets\\Materials\\jumprope.mxm" name:"jumpRope"

for rope in ropes do
(
	rope.modifiers[1].V_Tile = 48
	rope.baseObject.optimize = false
	addModifier rope (Turn_to_Poly limitPolySize: true)
	rope.material = matRef
)
