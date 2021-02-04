#!/usr/bin/python3

import sys
import getopt
import pandas
import random

#get arguments
optlist, args = getopt.getopt(sys.argv[1:], '', ['max=', 'shade=', 'input=', 'label=', 'rand='])

#default values
#filename default
srcvec = 'plink.eigenvec'
dstbase = 'plink'
#maxcount default
maxcount = 0
#shade default (dark)
colmin = 0.05
colmax = 0.8
#random default
rndamt = 0.2
#label default
lblgrp = ""


#handle arguments
for o,a in optlist:
    if o == "--input":
        srcvec = a
    elif o == "--max":
        maxcount = int(a)
    elif o == "--shade":
        if a == "light":
            colmin = 0.2
            colmax = 1.0
        elif a == "dark":
            colin = 0.05
            colmax = 0.8
    elif o == "--label":
        lblgrp = a
    elif o == "--rand":
        rndamt = float(a)
    else:
        print('unrecognized option {o} {a}')

#dependant vars
dstfile = dstbase + 'eigenvec.csv'
palfile = dstbase + 'palette.csv'

colrng = colmax - colmin

#useful func
def lerp(a,b,f):
    return a + (b - a) * f

#read the eigenvec
print('reading ' + srcvec + '...')

df = pandas.read_csv(srcvec,sep='\s+',header=None)

#how many columns?
ccnt = len(df.columns)

#bail if not enough pcs
if ccnt < 8:
    sys.exit(f"not enough principal components in {srcvec} \n run plink with --pca 6 or higher")

#set column headers
cols = []

for i in range(ccnt):
    if i == 0:
        cols.append('Group')
    elif i == 1:
        cols.append('ID')
    else:
        cols.append(f"PC{i - 1}")

df.columns = cols

#limit count if requested
if maxcount > 0 and maxcount < len(df.index):
    print(f"there are {len(df.index)} rows - restricting to {maxcount} randomly selected rows...")
    df = df.sample(maxcount)
   
#store eigenvector means for groups in means dataframe
groups = df.groupby(by='Group',as_index=False)
means = groups.mean()
means['Label'] = means['Group'].str.replace("AA_Ref_","")

#use first 3 PCs for palette
pcs = means[['PC1','PC2','PC3']]
mins = pcs.min()
maxs = pcs.max()
rngs = maxs - mins
invs = 1.0 / rngs

#map group averages on PC1, PC2 and PC3 to 0-1 range and use as RGB channels
means['Red'] = ((means['PC1'] - mins['PC1']) * invs['PC1'])
means['Green'] = ((means['PC2'] - mins['PC2']) * invs['PC2'])
means['Blue'] = ((means['PC3'] - mins['PC3']) * invs['PC3'])

#mix in some random color (proportion random controlled by rndamt, --rand option
means['Red'] = means['Red'].transform(lambda x: lerp(x,random.random(),rndamt))
means['Green'] = means['Green'].transform(lambda x: lerp(x,random.random(),rndamt))
means['Blue'] = means['Blue'].transform(lambda x: lerp(x,random.random(),rndamt))

#clamp result to 0-1 range just in case
means['Red'] = means['Red'].transform(lambda x: ((x,0.0)[x<0],1.0)[x>1])
means['Green'] = means['Green'].transform(lambda x: ((x,0.0)[x<0],1.0)[x>1])
means['Blue'] = means['Blue'].transform(lambda x: ((x,0.0)[x<0],1.0)[x>1])

#scale to colmin-colmax range for dark/light shading
#then convert to int in range 0-255
#then format as hex string
means['RedHex'] = means['Red'].transform(lambda x: f"{int((x * colrng + colmin) * 255):02X}")
means['GreenHex'] = means['Green'].transform(lambda x: f"{int((x * colrng + colmin) * 255):02X}")
means['BlueHex'] = means['Blue'].transform(lambda x: f"{int((x * colrng + colmin) * 255):02X}")

#combine rgb hex values into single color string
means['Color'] = means.eval('Color = RedHex + GreenHex + BlueHex')['Color']

#set color to black on label group, if it exists
if lblgrp != "":
    lblmask = means['Group'].eq(lblgrp)
    means.loc[lblmask,'Color'] = "000000"
    print(f"setting emphasis label on group {lblgrp}")

#write the output files
print('writing eigenvectors to ' + dstfile)
df.to_csv(dstfile,index=False, columns=['Group','ID','PC1','PC2','PC3','PC4','PC5','PC6'])

print('writing palette to ' + palfile)
means.to_csv(palfile, index=False, columns=['Group','Label','Color'])




