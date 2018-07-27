from PIL import Image
from PIL import ImageOps

import arkInit
arkInit.init()

import cOS

import Imath
import OpenEXR

import numpy

def loadImage(imagePath):
	ext = cOS.getExtension(imagePath)

	# OpenEXR Linear to RGB: https://gist.github.com/drakeguan/6303065
	if ext == 'exr':
		exr = OpenEXR.InputFile(imagePath)
		pixelType = Imath.PixelType(Imath.PixelType.FLOAT)
		dw = exr.header()['dataWindow']
		size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

		rgbf = [numpy.fromstring(exr.channel(c, pixelType), dtype=numpy.float32) for c in 'RGB']
		for i in range(3):
			rgbf[i] *= 255

		rgb8 = [Image.frombytes('F', size, c.tostring()).convert('L') for c in rgbf]
		return Image.merge('RGB', rgb8)

	return Image.open(imagePath)

def applyGamma(imageClass, gammaValue):
	inverseGamma = 1.0 / gammaValue

	r, g, b = imageClass.split()

	# gamma conversion: http://www.dfstudios.co.uk/articles/programming/image-programming-algorithms/image-processing-algorithms-part-6-gamma-correction/
	def gamma(c):
		return 255 * (float(c) / 255.0) ** inverseGamma

	imageClass = Image.eval(imageClass, gamma)

	return imageClass

def applyColorspace(imageClass, colorSpace):
	# srgb conversion: https://en.wikipedia.org/wiki/SRGB
	def sRGBColorspace(c):
		c = float(c) / 255.0
		c = numpy.where(c <= 0.0031308, (c * 12.92) * 255.0, (1.055 * (c ** (1.0/2.4)) - 0.055) * 255.0)
		return c

	# Rec709 conversion: http://entropymine.com/imageworsener/rec709formula/
	def rec709ColorSpace(c):
		c = float(c) / 255.0
		c = numpy.where(c < 0.02, (c * 4.50) * 255.0, (1.099 * (c **.45) - 0.099) * 255.0)
		return c

	# http://www.vocas.nl/webfm_send/964
	# TO DO
	# def alexaLogC(c):

	if colorSpace.lower() == 'srgb':
		imageClass = Image.eval(imageClass, sRGBColorspace)

	elif colorSpace.lower() == 'rec709':
		imageClass = Image.eval(imageClass, rec709ColorSpace)

	else:
		raise Exception('Unsupported colorspace type!')

	return imageClass

def resizeImage(maxWidth, maxHeight, imageClass, resizeType='fill'):
	return ImageOps.fit(imageClass, [maxWidth, maxHeight])

def saveImage(imageClass, path, quality=75):
	ext = cOS.getExtension(path)
	if ext == 'jpg':
		imageClass.save(path, 'JPEG', quality=quality)

def main():
	# pass
	# loadImage('C:/Users/IE/Desktop/NewFolder/Day_0010_OFFLINE_v05.1012.jpg')

	filepath = 'C:/Users/IE/Desktop/NewFolder/test.exr'
	img = loadImage(filepath)
	colored = applyColorspace(img, 'srgb')
	# # gamma = applyGamma(img, 2.2)
	# resize = resizeImage(150, 150, img)
	saveImage(colored, filepath.replace('.exr','_C.jpg'))
	# saveImage(gamma, filepath.replace('.exr','_G.jpg'))
	# saveImage(gamma, filepath.replace('.exr','_G.jpg'))


if __name__ == '__main__':
	main()
