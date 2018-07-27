
for obj in getCurrentSelection() do
(
	baseObj = editable_mesh()
	convertto baseObj editable_poly
	baseObj.name = obj.name
	baseObj.pivot = obj.pivot
	baseObj.transform = obj.transform
	baseObj.EditablePoly.attach obj baseObj
)
