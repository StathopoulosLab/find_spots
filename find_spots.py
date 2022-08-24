# find_spots.py

"""
Highest level python script to find triplets of tagged spots from microscope images.

This code can take processing parameters in the form of a YAML file specified on the
command line, but also has reasonable default parameters if none are specified.

command line:  python find_spots.py input_image_file output_image_file
"""

from confocal_file import ConfocalFile
from denoise import Denoise
import detect_spots as ds
import tripletDetection as td
import touchingAnalysis as ta
import yaml
import numpy as np
import sys

default_params = {
    "first_slice": 0,
    "last_slice": -1,    # -1 indicates last available slice.  -11 would skip the last 10
    "sigma": 15,
    "alpha_sharp": 1.3,
    "spot_detect_threshold": -0.02,
    'x_scale': 0.065,
    'y_scale': 0.065,
    'z_scale': 0.1,
    'touching_threshold': 0.2
}

def get_param(key, params):
    if key in params:
        return params[key]
    elif key in default_params:
        return default_params[key]
    else:
        return None

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
    x_scale = get_param('x_scale', params)
    y_scale = get_param('y_scale', params)
    z_scale = get_param('z_scale', params)
    touching_threshold = get_param('touching_threshold', params)

    denoiser = Denoise()

    #TODO: make these steps concurrent
    denoised_3CRM = denoiser.denoise(cf.channel_3CRM()[first_slice:last_slice], sigma, alpha_sharp)
    spots_3CRM = ds.detect_spots(denoised_3CRM, spot_detect_thresh)

    denoised_5CRM = denoiser.denoise(cf.channel_5CRM()[first_slice:last_slice], sigma, alpha_sharp)
    spots_5CRM = ds.detect_spots(denoised_5CRM, spot_detect_thresh)

    denoised_PPE = denoiser.denoise(cf.channel_PPE()[first_slice:last_slice], sigma, alpha_sharp)
    spots_PPE = ds.detect_spots(denoised_PPE, spot_detect_thresh)
    #TODO: end of potentially concurrent block
    print(f"Found {len(spots_3CRM)} 3CRM, {len(spots_5CRM)} 5CRM and {len(spots_PPE)} PPE spots")

    triplets, max_lim = td.find_best_triplets(spots_3CRM, spots_5CRM, spots_PPE, x_scale, y_scale, z_scale)
    print(f"Identified {len(triplets)} with max_lim {max_lim}")
    points, conformations = ta.analyze_inner(triplets, touching_threshold)
    print(f"analyze_inner identified {len(points)} points")

    ta.write_output(points, out_name)

if __name__ == "__main__":
    inputFile = str(sys.argv[1])
    outputFile = str(sys.argv[2])

    paramsFile = None
    if len(sys.argv) > 3:
        paramsFile = str(sys.argv[3])
    find_spots(inputFile, outputFile, paramsFile)