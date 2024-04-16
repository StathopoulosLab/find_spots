# confocal_file.py

"""
Provide access to contents of Zeiss Confocal Microscope image files.

Input:
    .czi file produced by a Zeiss Confocal Microscope

Results:
    TODO: describe results
"""

from czifile import CziFile, imread

class ConfocalFile(object):
    """
    Object representing a .czi file from the Stathopoulos lab's Zeiss confocal microcscope
    """

    CHANNEL_647 = 0
    CHANNEL_555 = 1
    CHANNEL_488 = 2
    CHANNEL_NUCLEUS = 3

    def __init__(self, filepath: str):
        _path = filepath
        czi = CziFile(filepath)
        meta = czi.metadata(raw=False)
        imageInfo = meta['ImageDocument']['Metadata']['Information']['Image']
        distances = meta['ImageDocument']['Metadata']['Scaling']['Items']['Distance']
        assert len(distances) == 3
        self._scale = {}
        for dist in distances:
            self._scale[dist['Id']] = dist['Value'] * 1.0e06    # convert from meters to uM
        assert imageInfo['PixelType'] == 'Gray8' or imageInfo['PixelType'] == 'Gray16'
        assert imageInfo['ComponentBitCount'] == 8 or imageInfo['ComponentBitCount'] == 16
        assert imageInfo['SizeH'] == 1
        self._sizeX = imageInfo['SizeX']
        self._sizeY = imageInfo['SizeY']
        self._sizeZ = imageInfo['SizeZ']
        self._channels = imageInfo['SizeC']
        image = czi.asarray().squeeze()
        assert len(image.shape) == 4
        self._647 = image[self.CHANNEL_647, :, :, :]
        self._555 = image[self.CHANNEL_555, :, :, :]
        self._488 = image[self.CHANNEL_488, :, :, :]
        self._nucleus = image[self.CHANNEL_NUCLEUS, :, :, :]

    def channel_647(self):
        return self._647

    def channel_555(self):
        return self._555

    def channel_488(self):
        return self._488

    def channel_nucleus(self):
        return self._nucleus

    def get_scale(self):
        return self._scale