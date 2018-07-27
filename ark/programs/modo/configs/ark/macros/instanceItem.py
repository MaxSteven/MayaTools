# python

import lx

itemType = lx.eval1('item.setType ?type')
lx.eval('item.name type:{0}'.format(itemType))
# item.duplicate true all:false mods:true
