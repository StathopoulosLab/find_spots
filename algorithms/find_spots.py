# find_spots.py

"""
Highest level python script to find triplets of tagged spots from microscope images.

This code can take processing parameters in the form of a YAML file specified on the
command line, but also has reasonable default parameters if none are specified.

command line:  python find_spots.py input_image_file output_image_file
"""

from matplotlib.pyplot import xscale
from algorithms.confocal_file import ConfocalFile
# from algorithms.denoise import Denoise, DenoiseBM4D
from algorithms.denoise import DenoiseBM4D
import algorithms.detect_spots as ds
import algorithms.tripletDetection as td
import algorithms.touchingAnalysis as ta
import yaml
import numpy as np
from os.path import splitext
import sys
import tifffile as tiff
from PIL import Image
from matplotlib import cm

default_params = {
    "first_slice": 0,
    "last_slice": -1,    # -1 indicates last available slice.  -11 would skip the last 10
    "sigma": 15,
    "alpha_sharp": 1.3,
    "nucleus_mask_threshold": 16,
    "spot_detect_threshold": -0.02,
    'touching_threshold': 0.2,
    'use_denoise3d': False,
    # 'use_bm4d': True,
    'save_after_denoise': False,
    'save_spots': True
}

def get_param(key, params):
    if key in params:
        return params[key]
    elif key in default_params:
        return default_params[key]
    else:
        return None

def save_components(img: np.ndarray, save_name: str):
    """
    Save each z-plane slice as a separate tiff file
    """
    for z in range(img.shape[0]):
        tiff.imsave(save_name + f"_{z:02d}.tiff", img[z,:,:])

def find_spots(image_file: str, out_name: str, params_yaml_file: str = None):
    params = {}
    if params_yaml_file:
        try:
            with open(params_yaml_file, 'r') as params_file:
                params = yaml.load(params_file)
        except Exception as e:
            print(f"Couldn't open params file {params_yaml_file} because of {e}")
            print("Using default params")

    try:
        cf = ConfocalFile(image_file)
    except Exception as e:
        print(f"Image file {image_file} could not be opened.  Error was: {e}")
        exit(-1)

    first_slice = get_param('first_slice', params)
    last_slice = get_param('last_slice', params)
    sigma = get_param('sigma', params)
    alpha_sharp = get_param('alpha_sharp', params)
    spot_detect_thresh = get_param('spot_detect_threshold', params)
    scale = cf.get_scale()
    touching_threshold = get_param('touching_threshold', params)
    use_denoise3d = get_param('use_denoise3d', params)
    # use_bm4d = get_param('use_bm4d', params)
    save_after_denoise = get_param('save_after_denoise', params)
    save_spots = get_param('save_spots', params)

    if save_after_denoise:
        stem, _ = splitext(inputFile)
        save_name = stem + "_antibody"
        save_components(cf.channel_antibody()[first_slice:last_slice], save_name)

    denoiser = DenoiseBM4D()
    # if use_bm4d:
    #     print("Using native Python BM4D")
    #     denoiser = DenoiseBM4D()
    # else:
    #     print("Using MatLab BM3D")
    #     denoiser = Denoise()

    #TODO: make these steps concurrent
    print("Denoising 3'CRM")
    if use_denoise3d:
        denoised_3CRM = denoiser.denoise3d(cf.channel_3CRM()[first_slice:last_slice], sigma, alpha_sharp)
    else:
        denoised_3CRM = denoiser.denoise(cf.channel_3CRM()[first_slice:last_slice], sigma, alpha_sharp)
    if save_after_denoise:
        stem, _ = splitext(inputFile)
        save_name = stem + "_3CRM_denoised"
        save_components(denoised_3CRM, save_name)
    print("Detecting spots in 3'CRM")
    spots_3CRM = ds.detect_spots(denoised_3CRM, spot_detect_thresh)
    if save_spots:
        stem, _ = splitext(inputFile)
        ds.write_output(spots_3CRM, stem + "_3CRM_spots.txt")

    print("Denoising 5'CRM")
    if use_denoise3d:
        denoised_5CRM = denoiser.denoise3d(cf.channel_5CRM()[first_slice:last_slice], sigma, alpha_sharp)
    else:
        denoised_5CRM = denoiser.denoise(cf.channel_5CRM()[first_slice:last_slice], sigma, alpha_sharp)
    if save_after_denoise:
        stem, _ = splitext(inputFile)
        save_name = stem + "_5CRM_denoised"
        save_components(denoised_5CRM, save_name)
    print("Detecting spots in 5'CRM")
    spots_5CRM = ds.detect_spots(denoised_5CRM, spot_detect_thresh)
    if save_spots:
        stem, _ = splitext(inputFile)
        ds.write_output(spots_5CRM, stem + "_5CRM_spots.txt")

    print("Denoising PPE")
    if use_denoise3d:
        denoised_PPE = denoiser.denoise3d(cf.channel_PPE()[first_slice:last_slice], sigma)
    else:
        denoised_PPE = denoiser.denoise(cf.channel_PPE()[first_slice:last_slice], sigma, alpha_sharp)
    if save_after_denoise:
        stem, _ = splitext(inputFile)
        save_name = stem + "_PPE_denoised"
        save_components(denoised_PPE, save_name)
    print("Detecting spots in PPE")
    spots_PPE = ds.detect_spots(denoised_PPE, spot_detect_thresh)
    if save_spots:
        stem, _ = splitext(inputFile)
        ds.write_output(spots_PPE, stem + "_PPE_spots.txt")

    #TODO: end of potentially concurrent block
    print(f"Found {len(spots_3CRM)} 3CRM, {len(spots_5CRM)} 5CRM and {len(spots_PPE)} PPE spots")
    triplets, max_lim = td.find_best_triplets(spots_3CRM, spots_5CRM, spots_PPE, scale['X'], scale['Y'], scale['Z'])
    print(f"Identified {len(triplets)} triplets with max_lim {max_lim}")
    triplets, conformations = ta.analyze_inner(triplets, touching_threshold)
    print(f"analyze_inner identified {len(triplets)} triplets")

    output = ta.generate_output(triplets)
    ta.write_output(output, out_name)

    # construct a new rgb version of the antibody image volume
    gray_colormap = cm.get_cmap('gray', 256)
    antibody_rgb = gray_colormap(cf.channel_antibody(), bytes=True)[:,:,:,0:3]

    # Now plot each of the triplets into the image stack, colored by conformation
    colors = {
        '000': (255,   0,   0),     # red
        '100': (  0,   0, 255),     # blue
        '010': (  0, 255,   0),     # green
        '001': (  0, 255, 255),     # cyan
        '110': (255, 255,   0),     # yellow
        '101': (  0,   0,   0),     # black
        '011': (255, 255, 255),     # white
        '111': (255,   0, 255)      # magenta
        }

    for triplet in output:
        x = round(triplet[0] / scale['X'])
        y = round(triplet[1] / scale['Y'])
        z = round(triplet[2] / scale['Z'])
        color = colors[triplet[3]]
        for dx in range(-6,7):
            if x + dx < 0 or x + dx >= antibody_rgb.shape[1]:
                continue
            for dy in range(-6, 7):
                if y + dx < 0 or y + dy >= antibody_rgb.shape[2]:
                    continue
                for dz in range(-2, 3):
                    if z + dz < 0 or z + dz >= antibody_rgb.shape[0]:
                        continue
                    antibody_rgb[z+dz][x+dx][y+dy] = color
    outStem, _ = splitext(out_name)
    tiff.imwrite(outStem + "_rgb.tiff", antibody_rgb)


if __name__ == "__main__":
    inputFile = str(sys.argv[1])
    outputFile = str(sys.argv[2])

    paramsFile = None
    if len(sys.argv) > 3:
        paramsFile = str(sys.argv[3])
    find_spots(inputFile, outputFile, paramsFile)