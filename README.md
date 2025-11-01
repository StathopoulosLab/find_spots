# System requirements: 
Github 2.37.1 or greater

Python 3.11 or less

Does not require GPU

For the example data, 15-16 GB of memory, recommended for laptop with memory of >20GB or above. 

# Installation: 
git clone https://github.com/StathopoulosLab/find_spots
pip install -r requirements.txt

Installation should take <10 minutes

The initial detection and find spots pipeline to detect and calculate distances between three spots of three different colors is stored in the algorithms folder. The pipeline is built upon a GUI and once cloned and download the pipeline to a destination repository run the following command to open up the GUI: 

python3 findSpotsTool.py 

## Sample files and Demo

Demo files storage : https://doi.org/10.22002/3jvmr-1b914
The folder contains the following sets of files for each of the 4 developmental stages and 2 phenotypes WT and deltaPPE: 
1. Original .czi file to load 
2. csv files example output of the find_spots program
3. html example output of the batch process program

On Linux machine running Ubuntu 22.04.5 LTS on AMD EPYC 7542 CPU (32 cores) with 128 GB memory using 4 cores, run time is 21 minutes 25 seconds. 

On MacBookPro running MacOS Sequoia on Apple Silicon M4 Pro (12 cores) with 24 GB memory using 4  cores, run time is <30 minutes. 

The software should also run on Windows with similar machine capabilities, but this configuration has not been tested.


# Usage/ Demo 

GUI is currently formatted below: 

<img width="1108" height="844" alt="Screenshot 2025-10-31 at 6 38 40 PM" src="https://github.com/user-attachments/assets/90e895c8-b824-4c39-8805-ea0958e056ee" />


Spot detection settings and Resolution Limit should be altered based on chosen microscope of choice. Maximum distance threshold should be determined based on your organism of interest based on Supplemental Figure 1. However, we recommend 2um if you are working with Drosophila embryos at early development, similar to the system chosen for this study. 

We recommend checking "Save spot image" to verify your spot detection threshold and "Also Find Doublets" similar desired analysis as this study. The following files are going to be outputted from the program given the above instructions: 

1. _2D_rgb.tiff
2. _3D_rgb.tiff
3. _ch0_spots.tiff
4. _ch1_spots.tiff
5. _distances.csv
6. _doublets_rgb.tiff
7. _leftDoublets.txt
8. _results.txt
9. _rightDoublets.txt
10. _spots_rgb.tiff


Example czi images and examples outputs are included in above demo folder. The spots_rgb file are useful for batch_process pipeline of overlaying the detected and measured CSV files against detected spots and nuclear lamin channel. There are other outputs produced such as .txt files for triplets, leftDoublets.txt, rightDoublets.txt, doublets_rgb.tiff, 2D_rgb.tiff, 3D_rgb.tiff that we had previously used for troubleshooting purposes but later disregard for final analyses. You may find those helpful for your data interpretation. However the main files you need to move forward into post-processing tools are: 

1. _distances.csv
2. _spots_rgb.tiff
3. ch0_spots.tiff
4. ch1_spots.tiff
5. ch2_spots.tiff

   
In order to verify all dots are within the lamin channel, we utilize the post_processing_tools batch_process.ipynb. For an image, place the _spots_rgb.tiff and _distances.csv in the same directory, then run the following line to generate the overlay html file to do verification:

python3 batch_process.py --directory "your created directory".

The main analyses including PDF construction, contour plots constructions are in post_processing_tools Final_code_github.ipynb. In order to have the correct python environment, we find it most helpful to use this setup created by Dr. Justin Bois at Caltech since it has many built in Bokeh Features. Bokeh are widely used in the graphical generation of this pipeline. You can access and download the bootcamp.yml environment here: https://justinbois.github.io/bootcamp/2023/lessons/l00_configuring_your_computer.html#

Desired analysis such as PDF generation, heatmap comparisons or contour plots generations are shown and outlined in the Final_code_github.ipynb and highlighted throughout the paper. The structure of the _distances.csv files are below: 

<img width="776" height="47" alt="Screenshot 2025-08-04 at 2 57 50 PM" src="https://github.com/user-attachments/assets/34f527f4-8aa6-405e-9715-5c52e5afc429" />


The provided code will take the Xleft, Yleft, Zleft and 3 positional information of the other 2 dots (dependent on which channel you set as left, middle and right on the GUI) and subjected this to the resolution limit threshold so any recorded distances that is less than the resolution limit will be converted to 0nm. Please alter this line in the Final_code_github if utilizing a different microscope with different resolution limit: 

res_squared = [0.12**2, 0.12**2, 0.35**2]

0.12 is the x-y resolution limit 

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

0.35 is the z resolution limit

The code will then proceed comparisons for individual distances PDF first before combining them into a 3D contour for positional information comparison. 
