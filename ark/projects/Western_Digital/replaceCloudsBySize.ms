smallest = 100000000
largest = 0
userSel = getCurrentSelection()

clouds = #($cloud01_v003_001,$cloud02_v003_001,$cloud03_v003_001,$cloud05_v003_001,$cloud04_v003_001,$cloud06_v003_001)

for obj in userSel do
(
	select obj
	boxSize = length ($.max - $.min)


	cloudIndex = ((ceil (boxSize * .0005)) as integer)
	print cloudIndex
	newCloud = instance clouds[cloudIndex]
	newCloud.transform = obj.transform
	newCloud.scale = [1,1,1]

	if cloudIndex > largest then
		largest = boxSize
	if cloudIndex < smallest then
		smallest = boxSize
)


print "largest"
print largest

print "smallest"
print smallest

select userSel
