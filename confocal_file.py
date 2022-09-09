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

    CHANNEL_3CRM = 0
    CHANNEL_PPE = 1
    CHANNEL_5CRM = 2
    CHANNEL_ANTIBODY = 3

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
        assert imageInfo['PixelType'] == 'Gray8'
        assert imageInfo['ComponentBitCount'] == 8
        assert imageInfo['SizeT'] == 1
        assert imageInfo['SizeB'] == 1
        assert imageInfo['SizeH'] == 1
        self._sizeX = imageInfo['SizeX']
        self._sizeY = imageInfo['SizeY']
        self._sizeZ = imageInfo['SizeZ']
        self._channels = imageInfo['SizeC']
        image = imread(filepath)
        self._3CRM = image[0, 0, 0, self.CHANNEL_3CRM, :, :, :, 0]
        self._5CRM = image[0, 0, 0, self.CHANNEL_5CRM, :, :, :, 0]
        self._PPE = image[0, 0, 0, self.CHANNEL_PPE, :, :, :, 0]
        self._antibody = image[0, 0, 0, self.CHANNEL_ANTIBODY, :, :, :, 0]

    def channel_3CRM(self):
        return self._3CRM

    def channel_5CRM(self):
        return self._5CRM

    def channel_PPE(self):
        return self._PPE

    def channel_antibody(self):
        return self._antibody

    def get_scale(self):
        return self._scale