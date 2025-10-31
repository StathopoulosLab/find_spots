# System requirements: 
Github 2.37.1 or greater

Python 3.11 or less

Does not require GPU

Software uses 13 GB of memory, recommended for laptop with memory of >20GB or above.  

# Installation: 
git clone https://github.com/StathopoulosLab/find_spots

The initial detection and find spots pipeline to detect and calculate distances between three spots of three different colors is stored in the algorithms folder. The pipeline is built upon a GUI and once cloned and download the pipeline to a destination repository run the following command to open up the GUI: 

python3 findSpotsTool.py 

If your environment lack any python packages, follow the instructions in the terminal to download the packages for the GUI. Once all packages are loaded and available, GUI will pop up for usage. 

Examples download commands to have all the dependencies: 
1. pip install qtpy
2. conda install -c conda-forge pyside6 qtpy
3. python -m pip install opencv-python
4. python -m pip install scikit-image
5. python -m pip install matplotlib
6. python -m pip install czifile
7. python -m pip install pyyaml
8. python -m pip install qimage2ndarray
   

Run python3 findSpotsTool.py for instructions to install the above dependencies/modules. 

To access the sample image file you need Git LFS. In order to get that run the following commands: 
1. conda install -c conda-forge git-lfs
2. git lfs install
3. git pull
 

Runtime 32 cores machine using 4 cores with an AMD implementation of Intel instruction run time is 21 minutes 25 seconds. 

Runtime on 12 cores machine using 3 cores with an Apple Silicon M4, 24 GB memory run time is <30 minutes. 


# Usage/ Demo 

GUI is currently formatted below: 

<img width="1161" height="802" alt="Screenshot 2025-08-04 at 2 20 59 PM" src="https://github.com/user-attachments/assets/5bc57a09-e608-4d37-b0f0-2f12ea7a6a3b" />

Spot detection settings and Resolution Limit should be altered based on chosen microscope of choice. Maximum distance threshold should be determined based on your organism of interest based on Supplemental Figure 1. However, we recommend 2um if you are working with Drosophila embryos at early development, similar to the system chosen for this study. 

We recommend checking "Save spot image" to verify your spot detection threshold and "Also Find Doublets" similar desired analysis as this study. 
Sample image stack is included in Sample Image folder containing the original Zen file, the individual spot detection for each channel, the CSV distance files for post-processing analysis data structure. The spots_rgb file are useful for batch_process pipeline of overlaying the detected and measured CSV files against detected spots and nuclear lamin channel. When running through the program, there are other outputs produced such as .txt files for triplets, leftDoublets.txt, rightDoublets.txt, doublets_rgb.tiff, 2D_rgb.tiff, 3D_rgb.tiff that we had previously used for troubleshooting purposes but later disregard for final analyses. You may find those helpful for your data interpretation. However the main files you need to move forward into post-processing tools are: 

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
