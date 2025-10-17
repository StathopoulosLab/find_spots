Post-processing tools: 

FINAL CODE: 

This code allow the creation of PDF from Gaussian KDE for all three distances, developmental times and phenotypes.

This code also generate the comparison heatmap using the K-S test on the previously generated PDF. 

This code also created the contour plots resulting from the multiplication of two distances scaled by the weight of the third distance. 

Instructions: 
1. Feed in the csv outputs from find_spots pipeline
2. Follow the rest of code to generate pairwise interaction analyses and modeling for PDF, contour plots etc. 

For any questions about either post-processing or find spots, please direct it to mle2@caltech.edu

BATCH PROCESS: 
Code that allows overlay of measured spots (from csv) on top of produced TIFF images both from the find_spots tool pipeline.  
Use the following output to create the overlay: 
1. _distances.csv
2. _spots_rgb.tiff

TWIST COMPARISON: 
Code that allows D-V comparisons between twist and non-twist regions. 
- Follow instructions similar to FINAL code using .csv outputs. 

