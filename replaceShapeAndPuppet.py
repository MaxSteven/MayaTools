import maya.cmds as mc



selection = mc.ls(sl=True)
for ob in selection:
    import maya.cmds as mc

    mc.group(ob, n = ob + '_GRP')
    objName = mc.duplicate(ob, n = ob + '_puppet')[0]
    mc.select(clear=True)
    mc.select([ objName + '.f[9452]',  objName + '.f[9455:9456]',  objName + '.f[9459:9460]',  objName + '.f[9463:9464]',  objName + '.f[9467:9468]',  objName + '.f[9471:9472]',  objName + '.f[9475:9476]',  objName + '.f[9479:9480]',  objName + '.f[9483]',  objName + '.f[9485:9486]',  objName + '.f[9489:9490]',  objName + '.f[9493:9494]',  objName + '.f[9497:9498]',  objName + '.f[9688:9689]',  objName + '.f[9734:9735]',  objName + '.f[18628:18629]',  objName + '.f[18634:18635]',  objName + '.f[18638:18641]',  objName + '.f[18644:18645]',  objName + '.f[18648:18649]',  objName + '.f[18652]',  objName + '.f[18655:18657]',  objName + '.f[18712]',  objName + '.f[18715]',  objName + '.f[18989:18990]',  objName + '.f[18992]',  objName + '.f[18995]',  objName + '.f[19233:19234]',  objName + '.f[19236]',  objName + '.f[19239:19240]',  objName + '.f[19243]',  objName + '.f[19245:19246]',  objName + '.f[24312:24313]',  objName + '.f[24592:24593]',  objName + '.f[24844:24845]',  objName + '.f[25046:25047]',  objName + '.f[25848:25849]',  objName + '.f[37100:37101]',  objName + '.f[37104:37105]',  objName + '.f[37108:37109]',  objName + '.f[37112:37113]',  objName + '.f[37116:37117]',  objName + '.f[37120:37121]',  objName + '.f[37124:37125]',  objName + '.f[37128:37129]',  objName + '.f[37134:37135]',  objName + '.f[37138:37139]',  objName + '.f[37142:37143]',  objName + '.f[37146:37147]',  objName + '.f[37336]',  objName + '.f[37339]',  objName + '.f[37381:37382]',  objName + '.f[46276]',  objName + '.f[46279]',  objName + '.f[46281:46282]',  objName + '.f[46285:46286]',  objName + '.f[46288]',  objName + '.f[46291:46292]',  objName + '.f[46295:46296]',  objName + '.f[46299:46301]',  objName + '.f[46304]',  objName + '.f[46307]',  objName + '.f[46360:46361]',  objName + '.f[46638:46641]',  objName + '.f[46882:46885]',  objName + '.f[46888:46889]',  objName + '.f[46894:46895]',  objName + '.f[51960]',  objName + '.f[51963]',  objName + '.f[52240]',  objName + '.f[52243]',  objName + '.f[52492]',  objName + '.f[52495]',  objName + '.f[52693:52694]',  objName + '.f[53496]',  objName + '.f[53499]'], add=True);
    mc.delete()

    mc.select([ objName + '.f[0:9259]',  objName + '.f[9404:9451]',  objName + '.f[9572:9643]',  objName + '.f[9666:9705]',  objName + '.f[9784:18455]',  objName + '.f[18560:18599]',  objName + '.f[18616:18655]',  objName + '.f[18660:18667]',  objName + '.f[18670:18673]',  objName + '.f[18678:18693]',  objName + '.f[18698:18909]',  objName + '.f[18934:18941]',  objName + '.f[18946:19117]',  objName + '.f[19166:19181]',  objName + '.f[19190:19213]',  objName + '.f[19446:23937]',  objName + '.f[24050:24225]',  objName + '.f[24256:24503]',  objName + '.f[24534:24753]',  objName + '.f[24784:24979]',  objName + '.f[25010:25777]',  objName + '.f[25784:26791]',  objName + '.f[26808:36839]',  objName + '.f[36984:37031]',  objName + '.f[37152:37223]',  objName + '.f[37246:37285]',  objName + '.f[37364:46035]',  objName + '.f[46140:46179]',  objName + '.f[46196:46235]',  objName + '.f[46240:46247]',  objName + '.f[46250:46253]',  objName + '.f[46258:46273]',  objName + '.f[46278:46489]',  objName + '.f[46514:46521]',  objName + '.f[46526:46697]',  objName + '.f[46746:46761]',  objName + '.f[46770:46793]',  objName + '.f[47026:51517]',  objName + '.f[51630:51805]',  objName + '.f[51836:52083]',  objName + '.f[52114:52333]',  objName + '.f[52364:52559]',  objName + '.f[52590:53357]',  objName + '.f[53364:54371]',  objName + '.f[54388:55159]'], add=True)
    mc.delete()

	newObject = ob
	newSelectionShape = mc.listRelatives(newObject, children=True)[0]
	oldObject = ob.replace('_Group40435', '')
	if not mc.objExists(oldObject):
		continue

	oldObjectChildren = mc.listRelatives(oldObject, children=True)
	origShape = None
	for shape in oldObjectChildren:
	    if 'Orig' in shape:
	        origShape = shape
	        break

	if origShape:
		mc.setAttr(origShape + '.intermediateObject', 0)

		mc.transferAttributes(newSelectionShape, origShape, transferPositions=True, transferNormals=True, transferUVs=False, transferColors=False, sampleSpace=4, searchMethod=3, flipUVs=0, colorBorders=1)

		mc.delete(origShape, constructionHistory=True)

		mc.setAttr(origShape + '.intermediateObject', 1)

	elif len(oldObjectChildren) == 1:
		origShape = oldObjectChildren[0]

		mc.transferAttributes(newSelectionShape, origShape, transferPositions=True, transferNormals=True, transferUVs=False, transferColors=False, sampleSpace=4, searchMethod=3, flipUVs=0, colorBorders=1)

		mc.delete(origShape, constructionHistory=True)
