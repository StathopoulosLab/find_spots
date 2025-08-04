# find_spots
The initial detection and find spots pipeline to detect and calculate distances between three spots of three different colors is stored in the algorithms folder. The pipeline is built upon a GUI and once cloned and download the pipeline to a destination repository run the following command to open up the GUI: 
python3 findSpotsTool.py 
If your environment lack any python packages, follow the instructions in the terminal to download the packages for the GUI. Once all packages are loaded and available, GUI will pop up for usage. 
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
Desired analysis such as PDF generation, heatmap comparisons or contour plots generations are shown in the code and highlighted throughout the paper. 
