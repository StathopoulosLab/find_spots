This is the updated version of post processing tools. 
Post-processing tools:

Figure3-6_distances_cleaned:

This code allow the creation of PDF from Gaussian KDE for all three distances, developmental times and phenotypes.

This code also generate the comparison heatmap using the K-S test on the previously generated PDF.

This code also created the contour plots resulting from the multiplication of two distances scaled by the weight of the third distance.

Instructions:

Feed in the csv outputs from find_spots pipeline
Follow the rest of code to generate pairwise interaction analyses and modeling for PDF, contour plots etc.
For any questions about either post-processing or find spots, please direct it to mle2@caltech.edu

BATCH PROCESS: Code that allows overlay of measured spots (from csv) on top of produced TIFF images both from the find_spots tool pipeline.
Use the following output to create the overlay:

_distances.csv
_spots_rgb.tiff

TWIST COMPARISON: Figure_7_twist_vs_no_twist_no_legacy that allows D-V comparisons between twist and non-twist regions.

Follow instructions similar to FINAL code using .csv outputs.
