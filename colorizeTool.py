###################################################################
#   The colorize tool allows for quick recoloring of shape nodes  #
#  Just select the obj(s) you need to color and then run the tool #
#              author : Vijay (mcvijay@gmail.com                  #
#                  lastUpdated : 06/13/2015                       #
###################################################################

import maya.cmds as cmds
from functools import partial

# colorShape
def colorShape():
    '''
    Calls the UI
    '''
    colorShapeUI()
# end of def colorShape
#******************************************************


# colorShapeUI
def colorShapeUI():
    '''
    This block brings up the UI
    '''
    loadColorShapeUI()    
    # Any subsequent UI needed will be added in this function
    
# end of colorShapeUI
#******************************************************


# loadColorShapeUI()
def loadColorShapeUI():
    '''
    Brings up a window and user can select the color needed
    '''
        
    # delete UI if it already exists
    colorShpWindow = "Colorize"
    if cmds.window(colorShpWindow, exists=True):
        cmds.deleteUI(colorShpWindow)
        
    colorShpWindow = cmds.window(colorShpWindow, title = 'Colorize', widthHeight=(100, 30), rtf = 1)
    
    cmds.columnLayout()
    
    cmds.frameLayout( label='Colors' )
    cmds.columnLayout()
    colorCollection = cmds.radioCollection()
    
    #RED color
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 80)] )
    redButt = cmds.radioButton( label='Red' )
    redLightButt = cmds.radioButton( label='Lighter' )
    redDarkButt = cmds.radioButton( label='Darker' )
    cmds.setParent( '..' )
    
    #BLUE color
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 80)] )
    blueButt = cmds.radioButton( label='Blue' )
    blueLightButt = cmds.radioButton( label='Lighter' )
    blueDarkButt = cmds.radioButton( label='Darker' )
    cmds.setParent( '..' )

    #GREEN color
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 80)] )
    greenButt = cmds.radioButton( label='Green' )
    greenLightButt = cmds.radioButton( label='Lighter' )
    greenDarkButt = cmds.radioButton( label='Darker' )
    cmds.setParent( '..' )
    
    #PINK color
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 80)] )
    pinkButt = cmds.radioButton( label='Pink' )
    pinkLightButt = cmds.radioButton( label='Lighter' )
    pinkDarkButt = cmds.radioButton( label='Darker' )
    cmds.setParent( '..' )
    
    #Yellow color
    cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 80), (2, 80)] )
    yellowButt = cmds.radioButton( label='Yellow' )
    yellowLightButt = cmds.radioButton( label='Lighter' )
    cmds.setParent( '..' )

    cmds.setParent( '..' )
    cmds.frameLayout( label='Mode' )
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 80)] )
    NormalButt = cmds.radioButton( label='Normal', select = True )
    ReferenceButt = cmds.radioButton( label='Reference' )
    TemplateButt = cmds.radioButton( label='Template' )
    cmds.setParent( '..' )

    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 80)] )
    cmds.button(label='Colorize', command = partial(colButtonEval,redButt,redLightButt,redDarkButt,blueButt,blueLightButt,blueDarkButt,greenButt,greenLightButt,greenDarkButt,pinkButt,pinkLightButt,pinkDarkButt,yellowButt,yellowLightButt))
    cmds.button(label='Set Mode', command = partial(modeButtonEval,NormalButt,ReferenceButt,TemplateButt))
    cmds.button(label='show/Hide', command = shapeShowHide)
    cmds.setParent( '..' )
    
    resetButt = cmds.button( label='Reset All', command = resetAll )

    cmds.showWindow( colorShpWindow )
    
# END of function loadColorShapeUI    
# ****************************************************************************


def colButtonEval(rButt,rButtL,rButtD,bButt,bButtL,bButtD,gButt,gButtL,gButtD,pButt,pButtL,pButtD,yButt,yButtL,*_cb_val):
    '''
    finds out which button has been selected
    '''
    colorChoice = 0 
    
    rb = cmds.radioButton(rButt,q = True, sl = True)
    rbL = cmds.radioButton(rButtL,q = True, sl = True)
    rbD = cmds.radioButton(rButtD,q = True, sl = True)
    
    bb = cmds.radioButton(bButt,q = True, sl = True)
    bbL = cmds.radioButton(bButtL,q = True, sl = True)
    bbD = cmds.radioButton(bButtD,q = True, sl = True)
    
    gb = cmds.radioButton(gButt,q = True, sl = True)
    gbL = cmds.radioButton(gButtL,q = True, sl = True)
    gbD = cmds.radioButton(gButtD,q = True, sl = True)
    
    pb = cmds.radioButton(pButt,q = True, sl = True)
    pbL = cmds.radioButton(pButtL,q = True, sl = True)
    pbD = cmds.radioButton(pButtD,q = True, sl = True)
    
    yb = cmds.radioButton(yButt,q = True, sl = True)
    ybL = cmds.radioButton(yButtL,q = True, sl = True)
    

    if(rb == True):
        colorChoice = 13
    elif(rbL == True):
        colorChoice = 20
    elif(rbD == True):
        colorChoice = 12
        
    elif(bb == True):
        colorChoice = 6
    elif(bbL == True):
        colorChoice = 18
    elif(bbD == True):
        colorChoice = 5

    elif(gb == True):
        colorChoice = 14
    elif(gbL == True):
        colorChoice = 19
    elif(gbD == True):
        colorChoice = 7

    elif(pb == True):
        colorChoice = 31
    elif(pbL == True):
        colorChoice = 9
    elif(pbD == True):
        colorChoice = 30


    elif(yb == True):
        colorChoice = 17
    else:
        colorChoice = 22
   
    # now call the colorize function
    colorize(colorChoice)
        
# END of colButtonEval    
# ****************************************************************************

def modeButtonEval(nButt,rButt,tButt,*_mb_val):
    '''
    finds out which button has been selected
    '''    
    
    nb = cmds.radioButton(nButt,q = True, sl = True)
    rb = cmds.radioButton(rButt,q = True, sl = True)
    tb = cmds.radioButton(tButt,q = True, sl = True)
    

    if(nb == True):
        modeChoice = 0
    elif(rb == True):
        modeChoice = 2
    else:
        modeChoice = 1
   
    # now call the colorize function
    modeSet(modeChoice)
        
# END of modeButtonEval   
# ****************************************************************************


def colorize(colorChoice):
    '''
    This func will select the shape nodes of the selection and then color them
    '''
    
    objList = cmds.ls(sl=True)
    for each in objList:
        objShape = retShape(each)
        # If there are multiple shape nodes then color each of them
        for eachShp in objShape:
            overridEn = eachShp+".overrideEnabled";
            overCol = eachShp+".overrideColor";
        
            cmds.select(objShape)
            cmds.setAttr(overridEn, 1)
            
            cmds.setAttr(overCol, colorChoice)
        
    cmds.select(cl=True)

# end of def colorize
# ****************************************************************************


def shapeShowHide(self):
    '''
    hides/shows the shape node of selected objets
    '''
    
    objList = cmds.ls(sl=True)
    if not objList:
        cmds.error('Select the control first')
    
    
    for each in objList:
        objShape = cmds.listRelatives(each, type='shape')
        for allShapes in objShape:
            shapeVis = cmds.getAttr(allShapes+'.visibility')
            if shapeVis:
                shapeVis = 0;
            else:
                shapeVis = 1;
            
            objShapeVis = allShapes+'.visibility'
            cmds.setAttr(objShapeVis, shapeVis)
            
    cmds.select(cl=True)
    
# END of function shapeHide    
# ****************************************************************************
 
 
def modeSet(modeChoice):
    '''
    sets the mode of selected shapes
    '''
    objList = cmds.ls(sl=True)
    for obj in objList:
        objShape = retShape(obj)
        # If there are multiple shape nodes then color each of them
        for eachShp in objShape: 
            shapeType =  eachShp + '.overrideDisplayType'        
            cmds.setAttr(shapeType, modeChoice)
            
    cmds.select(cl=True)
# end of def modeSet
# ****************************************************************************


def retShape(obj):
    '''
    returns the shapeNode of obj
    '''
    ##Find the Shape node of the selection
    cmds.select(obj)
    findShp = cmds.listRelatives(shapes=True)
    return(findShp)
# end of def retShape
# ****************************************************************************


def resetAll(self):
    '''
    Resets the color and mode to default
    '''
    objList = cmds.ls(sl=True)
    for obj in objList:
        objShape = retShape(obj)
        # If there are multiple shape nodes then color each of them
        for eachShp in objShape:
            overridEn = eachShp + '.overrideEnabled'
            overridCol = eachShp + '.overrideColor'
            cmds.setAttr(overridEn, 0);
            cmds.setAttr(overridCol, 5);
            
    cmds.select(cl=True)
# end of def resetAll()   


colorShape()
# ****************************************************************************