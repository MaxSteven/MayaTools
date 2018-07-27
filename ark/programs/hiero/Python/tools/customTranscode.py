
import hiero.core
# from hiero.exporters import FnTranscodeExporter, FnTranscodeExporterUI

# class ArkTranscodeUI(FnTranscodeExporterUI.TranscodeExporterUI):
# 	def __init__(self, preset):
# 		FnTranscodeExporterUI.TranscodeExporterUI.__init__(self, preset)
# 		self._displayName = "Ingenuity Transcode"
# 		self._taskType = ArkTranscodeExporter

# class ArkTranscodeExporter(FnTranscodeExporter.TranscodeExporter):
# 	def buildScript(self):
# 		"""
# 		Override the default buildScript functionality to also output a temp movie
# 		file if needed for uploading to Shotgun
# 		"""
# 		FnTranscodeExporter.TranscodeExporter.buildScript(self)

# 		# override write nodes
# 		for writeNode in self._script.getNodes():
# 			help(writeNode)
# 			if 'decoder' in writeNode.knobs():
# 				writeNode['decoder'].setValue('mov32')
# 				writeNode['mov32_pixel_format'].setValue('RGBA  16-bit (b64a)')

# class ArkTranscodePreset(FnTranscodeExporter.TranscodePreset):
# 	def __init__(self, name, properties):
# 		FnTranscodeExporter.TranscodePreset.__init__(self, name, properties)
# 		self._parentType = ArkTranscodeExporter

# # Register this CustomTask and its associated Preset
# def setup():
# 	hiero.core.taskRegistry.registerTask(ArkTranscodePreset, ArkTranscodeExporter)
# 	hiero.ui.taskUIRegistry.registerTaskUI(ArkTranscodePreset, ArkTranscodeUI)
