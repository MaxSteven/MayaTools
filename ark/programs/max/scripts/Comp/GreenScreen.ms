GreenMat = standardMaterial diffuse:green selfillumination:100
GreenScreen = sphere radius:50000 material:GreenMat name:"GreenScreen" wirecolor:green
addModifier GreenScreen (Normalmodifier())