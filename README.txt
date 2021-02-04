
pca_world.html will show 3D PCA viewer for a plink.eigenvec file using Plot.ly plotting library, you can select any combination of 3 PCs from the first 6 to view at a time.

extract all the files to some directory already being served by a webserver, put a plink.eigenvec file in same directory, run 'python3 dataconvert.py' to generate reformatted data and a color palette, then view pca_world.html in a browser (url depends on how your webserver is set up)

has to be run under a webserver as it tries to load two files - plinkeigenvec.csv and plinkpalette.csv - from the local directory via HTTP GET requests using the default Plot.ly data loading functions. could probably rewrite this to use the javascript local file picker function to load the datafiles and avoid the webserver requirement.

run the python script dataconvert.py in local dir to generate plinkeigenvec.csv and plinkpalette.csv from a local plink.eignevec file. requires python 3 with pandas module ('pip install pandas'). see below for command line options.

should work on any plink.eigenvec file with at least 6 PCs, but the palette algorithm only looks good if there are lots of groups which are spread out a bit on the PC axes

the palette algorithm calculates an average eigenvector for each group, then converts the first 3 PCs of that average into an RGB color (normalized over the range present on each axis in the eigenvector file), adds some noise to disambiguate close groups, then rescales a little to make it look better.

ripped from my personal website so the loading message is specific to that

commandline options for dataconvert.py:

--input [file]
    specify a different input file than plink.eigenvec in local dir
    
--max [int]
    specifiy a max number of samples to plot, will randomly sample n rows from input file
    
--rand [float 0 - 1]
    by default palette rgb is generated from first 3 PCs mixed with 20% random color to disambiguate close groups. use --rand to change random proportion, e.g. --rand 0.4 will change this proportion to 40%, if you want more disambiguation (look less pretty with more randomness)
    
--label [grpname]
    can specify one group in plink.eigenvec to highlight - will show with 'x' marker in black color and with a text label above each sample. maybe don't combine with --max as --max makes no attempt to preserve samples from --label group
    
--shade [light or dark]
    defaults to 'dark' - modifies the generated colors a little to work with a white plot background. 'light' would generate color palette better for a black background plot.
    

