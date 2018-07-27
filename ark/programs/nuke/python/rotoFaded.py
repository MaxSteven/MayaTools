# fix:
# when you restart nuke and reopen a script with the faded rotopaint for some reason
# the feature fade it is disabled you have to enable it in the Fade it tab of the rotopaint node

import nuke

b = nuke.createNode('RotoPaint')
tab = nuke.Tab_Knob('Fade It!')
b.addKnob(tab)
uk = nuke.nuke.Boolean_Knob('Enable', 'Enable',True)
b.addKnob(uk)
uk = nuke.nuke.Int_Knob('duration', 'Duration')
b.addKnob(uk)
b['duration'].setValue(10)
uk = nuke.nuke.Int_Knob('fadeoff', 'FadeOff')
b.addKnob(uk)
b['fadeoff'].setValue(5)
uk = nuke.nuke.PyScript_Knob('apply', 'Apply to selection','faded()')
b.addKnob(uk)
b['knobChanged'].setValue('''
k = nuke.thisKnob()
def faded():
    shps = nuke.thisNode()["curves"].getSelected()
    frame = nuke.frame()
    x = nuke.thisNode()
    duration = int(x["duration"].value())
    fadeoff = int(x["fadeoff"].value())

    for shp in shps:
        if 'Layer object' in str(shp):
            pass
        else:
            if 'Faded' in shp.name:
                pass
            else:
                attrs = shp.getAttributes()
                opacityCurve = attrs.getCurve(attrs.kOpacityAttribute)
                opacityCurve.reset()
                opacityCurve.addKey(frame-duration-fadeoff-5, 0)
                opacityCurve.addKey(frame-duration-fadeoff, 0)
                opacityCurve.addKey(frame-duration, 1)
                opacityCurve.addKey(frame+duration, 1)
                opacityCurve.addKey(frame+duration+fadeoff, 0)
                opacityCurve.addKey(frame+duration+fadeoff+5, 0)
                keyCount = opacityCurve.getNumberOfKeys()
                for i in range(keyCount):
                    opacityCurve.getKey(i).ra = 1
                    opacityCurve.getKey(i).la = 1
                    opacityCurve.getKey(i).lslope = 0
                    opacityCurve.getKey(i).rslope = 0
                shp.getAttributes().set('ltt',4)
                shp.getAttributes().set('ltn',frame-duration-fadeoff)
                shp.getAttributes().set('ltm',frame+duration+fadeoff)
                shp.name = "Faded " + shp.name + "{{fade "+str(fadeoff)+"}}{{duration "+str(duration)+"}}{{at "+str(nuke.frame())+"}} "
                nuke.thisNode()["curves"].changed()

if k.name() == "curves":
    if nuke.thisNode()["Enable"].value() == True:
        faded()
    else:
        shps = nuke.thisNode()["curves"].getSelected()
        for shp in shps:
            if 'Layer object' in str(shp):
                pass
            else:
                if 'Not Faded' in shp.name:
                    pass
                else:
                    shp.name = "Not Faded " + shp.name
                    nuke.thisNode()["curves"].changed()

''')
b.setName('Faded_RotoPaint')
b.knob('tile_color').setValue( 5374207 )
b.knob('note_font_color').setValue( 4294967295L )