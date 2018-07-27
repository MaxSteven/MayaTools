dummyTexture = @"Q:\ASSETS\TEXTURES\dummyTexture.png"
bitmapsArr = getClassInstances BitmapTexture asTrackViewPick:on

for tx in bitmapsArr where doesFileExist tx.anim.filename != true do
(
	print "not Valid"
	tx.anim.filename = dummyTexture
)