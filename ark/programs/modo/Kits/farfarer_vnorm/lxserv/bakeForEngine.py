#python
 
import lx
import lxifc
import lxu.command
import lxu.select

engines = ('UE4', 'Unity', 'Source')
engines_lower = tuple([x.lower () for x in engines])
engines_len = len (engines)

class OptionPopupEngines (lxifc.UIValueHints):
	def __init__ (self):
		pass

	def uiv_Flags (self):
		return lx.symbol.fVALHINT_POPUPS

	def uiv_PopCount (self):
		global engines_len
		return engines_len

	def uiv_PopUserName (self,index):
		global engines
		return engines[index]

	def uiv_PopInternalName (self,index):
		global engines_lower
		return engines_lower[index]

class BakeForEngine_Cmd(lxu.command.BasicCommand):

#______________________________________________________________________________________________ SETUP AND INITIALISATION

	def __init__(self):
		lxu.command.BasicCommand.__init__(self)
		self.dyna_Add ('engine', lx.symbol.sTYPE_STRING)

	def cmd_UserName (self):
 		return 'Bake For Engine'

 	def cmd_Desc (self):
 		return 'Bake the normal map to sync with the specified engine.'

 	def cmd_Tooltip (self):
 		return 'Bake the normal map to sync with the specified engine.'

 	def cmd_Help (self):
 		return 'http://www.farfarer.com/'

	def basic_ButtonName (self):
		global engines, engines_lower

		engine = ''
		if self.dyna_IsSet (0):
			engine = self.attr_GetString (0).lower ()

		name = 'Bake For '
		if engine in engines_lower:
			name += engines[engines_lower.index (engine)]
		else:
			name += 'Engine...'
		return name
 
	def cmd_Flags (self):
		return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO | lx.symbol.fCMD_SELECT

	def basic_Enable (self, msg):
		return self.valid_normal_selection ()[0]

	def valid_normal_selection (self):
		try:
			sel_scn = lxu.select.SceneSelection ()
			current_scene = sel_scn.current ()
			chan_read = lx.object.ChannelRead (current_scene.Channels (lx.symbol.s_ACTIONLAYER_EDIT, 0.0))

			scn_svc = lx.service.Scene ()
			type_imagemap = scn_svc.ItemTypeLookup (lx.symbol.sITYPE_IMAGEMAP)
			type_texturelayer = scn_svc.ItemTypeLookup (lx.symbol.sITYPE_TEXTURELAYER)
			type_textureloc = scn_svc.ItemTypeLookup (lx.symbol.sITYPE_TEXTURELOC)
			type_videostill = scn_svc.ItemTypeLookup (lx.symbol.sITYPE_VIDEOSTILL)

			sel_item = lxu.select.ItemSelection ()
			shd_graph = lx.object.ItemGraph (current_scene.GraphLookup (lx.symbol.sGRAPH_SHADELOC))
			for imagemap in sel_item.current ():
				if imagemap.Type () == type_imagemap and chan_read.String (imagemap, imagemap.ChannelLookup (lx.symbol.sICHAN_TEXTURELAYER_EFFECT)) == 'normal':
					videostill = None
					texture_loc = None
					uvmap = None

					fwd_count = shd_graph.FwdCount (imagemap)
					for fwd_idx in xrange (fwd_count):
						fwd_item = shd_graph.FwdByIndex (imagemap, fwd_idx)
						fwd_item_type = fwd_item.Type ()
						if fwd_item_type == type_textureloc:
							texture_loc = fwd_item
							if chan_read.Integer (texture_loc, texture_loc.ChannelLookup (lx.symbol.sICHAN_TEXTURELOC_PROJTYPE)) == 6:
								uvmap_name = chan_read.String (texture_loc, texture_loc.ChannelLookup (lx.symbol.sICHAN_TEXTURELOC_UVMAP))
								if uvmap_name != '(none)':
									uvmap = uvmap_name
						elif fwd_item_type == type_videostill:
							videostill = fwd_item

					if videostill != None and texture_loc != None and uvmap != None:
						return (True, imagemap, texture_loc, uvmap, videostill)

		except:
			pass

		return (False, None, None, '', None)

	def morph_selection (self):
		morph_name = ''
		sel_svc = lx.service.Selection ()
		vmap_pkt_trans = lx.object.VMapPacketTranslation (sel_svc.Allocate (lx.symbol.sSELTYP_VERTEXMAP))
		sel_type_vmap = sel_svc.LookupType (lx.symbol.sSELTYP_VERTEXMAP)

		for i in xrange(sel_svc.Count (sel_type_vmap)):
			pkt = sel_svc.ByIndex (sel_type_vmap, i)
			if vmap_pkt_trans.Type (pkt) == lx.symbol.i_VMAP_MORPH:
				morph_name = vmap_pkt_trans.Name (pkt)
				break
		return morph_name

	def select_uvmap (self, uvmap_name):
		sel_svc = lx.service.Selection ()
		vmap_pkt_trans = lx.object.VMapPacketTranslation (sel_svc.Allocate (lx.symbol.sSELTYP_VERTEXMAP))
		sel_type_vmap = sel_svc.LookupType (lx.symbol.sSELTYP_VERTEXMAP)

		needs_selecting = True

		for i in xrange (sel_svc.Count (sel_type_vmap)):
			pkt = sel_svc.ByIndex (sel_type_vmap, i)
			if vmap_pkt_trans.Type (pkt) == lx.symbol.i_VMAP_TEXTUREUV:
				if vmap_pkt_trans.Name (pkt) == uvmap_name:
					needs_selecting = False
				else:
					sel_svc.Deselect (sel_type_vmap, pkt)

		if needs_selecting:
			pkt_s = vmap_pkt_trans.Packet (lx.symbol.i_VMAP_TEXTUREUV, uvmap_name)
			sel_svc.Select (sel_type_vmap, pkt_s)

	def basic_Notifiers (self):
		basic_AddNotify (lx.symbol.sNOTIFIER_SELECT, 'item +d')

	def arg_UIHints (self, index, hints):
		if index == 0:
			hints.Label ('Engine')

	def arg_UIValueHints (self, index):
		if index == 0:
			return OptionPopupEngines ()

	def basic_Execute(self, msg, flags):
		global engines_lower

		engine = ''
		if self.dyna_IsSet (0):
			engine = self.attr_GetString (0).lower ()

		if engine in engines_lower:
			valid, imagemap, texture_loc, uvmap, videostill = self.valid_normal_selection ()

			if not valid:
				return

			sel_scn = lxu.select.SceneSelection ()
			current_scene = sel_scn.current ()
			chan_write = lx.object.ChannelWrite (current_scene.Channels (lx.symbol.s_ACTIONLAYER_EDIT, 0.0))
			chan_write_setup = lx.object.ChannelWrite (current_scene.Channels (lx.symbol.s_ACTIONLAYER_SETUP, 0.0))

	 		# Ensure the UV map is the only one selected.
	 		self.select_uvmap (uvmap)

			# Set image to linear space.
			chan_write_setup.String (videostill, videostill.ChannelLookup ('colorspace'), '(none)')

			# UE4
			if engine == engines_lower[0]:
				# Use per-pixel cross product bitangent.
				chan_write.Integer (texture_loc, texture_loc.ChannelLookup ('tngtType'), 1)
				# Invert green channel.
				chan_write.Integer (imagemap, imagemap.ChannelLookup (lx.symbol.sICHAN_IMAGEMAP_GREENINV), 1)
				lx.eval ('mesh.mikktspacegen')

			# Unity
			elif engine == engines_lower[1]:
				# Don't use per-pixel cross product bitangent.
				chan_write.Integer (texture_loc, texture_loc.ChannelLookup ('tngtType'), 0)
				# No inverted green channel.
				chan_write.Integer (imagemap, imagemap.ChannelLookup (lx.symbol.sICHAN_IMAGEMAP_GREENINV), 0)
				lx.eval ('mesh.tangentbasis.unity')

			# Source
			elif engine == engines_lower[2]:
				# Don't use per-pixel cross product bitangent.
				chan_write.Integer (texture_loc, texture_loc.ChannelLookup ('tngtType'), 0)
				# Invert green channel.
				chan_write.Integer (imagemap, imagemap.ChannelLookup (lx.symbol.sICHAN_IMAGEMAP_GREENINV), 1)
				lx.eval ('mesh.tangentbasis.source')

			# lx.eval ('poly.triple')

			# Default to using the selected morph map as the cage.
			selMorph = self.morph_selection ()
			if len (selMorph) > 0:
				lx.eval ('bake.objToTexture {%s} 0.0' % selMorph)
			else:
				lx.eval ('bake.objToTexture')

lx.bless(BakeForEngine_Cmd, 'ffr.bakeForEngine')