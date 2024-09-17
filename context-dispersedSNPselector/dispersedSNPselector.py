# pip3.12 install --force-reinstall pandas==2.2.2
# pip3.12 install --force-reinstall numpy==1.26.4

# import packages
import sys as sys # no individual installation because is part of the Python Standard Library
import os as os # no individual installation because is part of the Python Standard Library
import datetime as dt # no individual installation because is part of the Python Standard Library
import argparse as ap # no individual installation because is part of the Python Standard Library
import pandas as pd
import numpy as np

# step control
step1_start = dt.datetime.now()

# set workflow reference
reference = 'Please, site GitHub (https://github.com/Nicolas-Radomski/canSNPtyping) and/or Docker Hub (https://hub.docker.com/r/nicolasradomski/dispersedsnpselector)'

# get parser arguments
parser = ap.ArgumentParser(
	prog='dispersedSNPselector.py', 
	description='Discard SNP hotspots from a vcf-like tab-separated values (tsv) file.',
	epilog=reference
	)
# define parser arguments
parser.add_argument(
	'-i', '--input', 
	dest='profiles', 
	action='store', 
	required=True, 
	help='path of tab-separated values (tsv) file from SNP calling (REQUIRED)'
	)
parser.add_argument(
	'-o', '--output', 
	dest='outputpath', 
	action='store', 
	required=False, 
	default='dispersedSNPselector',
	help='output path (DEFAULT: dispersedSNPselector)'
	)
parser.add_argument(
	'-p', '--prefix', 
	dest='prefix', 
	action='store', 
	required=True, 
	help='prefix of output files (REQUIRED)'
	)
parser.add_argument(
	'-c', '--chromosome', 
	dest='size', 
	type=int,
	action='store', 
	required=True, 
	help='size of chromosome (REQUIRED)'
	)
parser.add_argument(
	'-n', '--nucleotides', 
	dest='bases', 
	type=int,
	action='store', 
	required=True, 
	help='nucleotides up and downstream canSNPs to design kmers (REQUIRED)'
	)
parser.add_argument(
	'-d', '--debug', 
	dest='debug', 
	type=int,
	action='store', 
	required=False, 
	default=0, 
	help='limit of the traceback (DEFAULT: 0)'
	)
parser.add_argument(
	'-nc', '--no-check', 
	dest='nocheck', 
	action='store_true', 
	required=False, 
	default=False, 
	help='do not check versions of Python and packages (DEFAULT: False)'
	)

# print help if there are no arguments in the command
if len(sys.argv)==1:
	parser.print_help()
	sys.exit(1)

# reshape arguments
## extract parser arguments
args = parser.parse_args()
## rename arguments
PROFILES=args.profiles
OUTPUTPATH=args.outputpath
PREFIX=args.prefix
SIZE=args.size
BASES=args.bases
DEBUG=args.debug
NOCHECK=args.nocheck

# set tracebacklimit
sys.tracebacklimit = DEBUG

# control versions
if NOCHECK == False :
    ## control Python version
	if sys.version_info[0] != 3 or sys.version_info[1] != 12 :
		raise Exception("Python 3.12 version is recommended")
		exit()
	# control versions of packages
	if ap.__version__ != "1.1":
		raise Exception('argparse 1.1 (1.4.1) version is recommended')
		exit()
	if pd.__version__ != "2.2.2":
		raise Exception('pandas 2.2.2 version is recommended')
		exit()
	if np.__version__ != "1.26.4":
		raise Exception('numpy 1.26.4 version is recommended')
		exit()
	message_versions = 'The recommended versions of Python and packages were properly controlled'
else:
	message_versions = 'The recommended versions of Python and packages were not controlled'

# print a message about version control
print(message_versions)

# check if the output directory does not exists and make it
if not os.path.exists(OUTPUTPATH):
	os.makedirs(OUTPUTPATH)
	print("The output directory was created successfully")
else:
	print("The output directory already exists")

# read and modify input
## read
input_df = pd.read_csv(PROFILES, sep='\t', index_col=None)
## remove columns 1 and 3
input_df = input_df.drop(columns = ['CHR', 'REF'])

# identify SNPs away from n bases upstream and downstream (i.e. (kmers length -1)/2)
## extract all SNPs positions
### retrieve index as a list
positions_lst = input_df['POS'].tolist()
### sort positions
positions_lst.sort(reverse = False)
### filter out the repeated positions
list(set(positions_lst))
## calculate differences with uptream SNPs
### retrieve all positions excluding the first one and adding position of the last one
#### calculate the last position
chromosome = SIZE
first = [positions_lst[0]]
first = np.array(first).astype(int).item()
addlast = chromosome + first
#### exclude the first one and add position of the last one
positions_upstream_lst = positions_lst.copy()
del positions_upstream_lst[0]
positions_upstream_lst.append(addlast)
## calculate differences with downstream SNPs
### retrieve all positions excluding the last one and adding position of the first one
#### calculate the first position
last = positions_lst[-1]
addfirst = (chromosome - last)*(-1)
#### exclude the last one and add position of the first one
positions_downstream_lst = positions_lst.copy()
del positions_downstream_lst[-1]
positions_downstream_lst.insert(0, addfirst)
## combine compared positions
### create a disionary of lists 
positions_dict = {'POS': positions_lst, 'UP': positions_upstream_lst, 'DOWN': positions_downstream_lst} 
### transforme as pandas dataframe
positions_df = pd.DataFrame(positions_dict)
## calculate differences
positions_df['diff_UP'] = positions_df['UP'] - positions_df['POS']
positions_df['diff_DOWN'] = positions_df['POS'] - positions_df['DOWN']
## extract positions with up and downstream differences higher than n or equal (i.e. (kmers length -1)/2)
retained_positions_df = positions_df[positions_df['diff_UP'] > BASES]
retained_positions_df = retained_positions_df[retained_positions_df['diff_DOWN'] > BASES]
retained_positions_lst = retained_positions_df['POS'].tolist()

# remove SNPs less than n bases away from first and last nucleotides of the chromosome
end = SIZE - BASES
retained_positions_trimmed_lst = retained_positions_lst.copy()
for i in retained_positions_trimmed_lst:
   # check whether the current element is lower than the input value
   if i < BASES:
      # remove that current element from the list if the condition is true
      retained_positions_trimmed_lst.remove(i)
for i in retained_positions_trimmed_lst:
   # check whether the current element is lower than the input value
   if i > end:
      # remove that current element from the list if the condition is true
      retained_positions_trimmed_lst.remove(i)

# extract retained SNPs
## joint snp profiles and retained SNPs
### transform a list into a pandas dataframe
retained_positions_trimmed_df = pd.DataFrame(retained_positions_trimmed_lst, columns=['POS'])
### joint pandas dataframes
snps_retained_sorted_df = retained_positions_trimmed_df.set_index('POS').join(input_df.set_index('POS'), on='POS', how='left')
### reset the index
snps_retained_sorted_df.reset_index(inplace=True)

# output results
## retained positions after discarding of hotspot SNPs
output_file_1 = OUTPUTPATH + '/' + PREFIX + '-SNPs-retained.tsv'
retained_positions_df.to_csv(output_file_1, sep='\t', index=False, header=True)
## retained positions after trimming of first and last nucleotides of the chromosome
output_file_2 = OUTPUTPATH + '/' + PREFIX + '-SNPs-retained-trimmed.tsv'
retained_positions_trimmed_df.to_csv(output_file_2, sep='\t', index=False, header=True)
## retained snp profiles
output_file_3 = OUTPUTPATH + '/' + PREFIX + '-SNPs-retained-trimmed-profiles.tsv'
snps_retained_sorted_df.set_index('POS', inplace=True)
snps_retained_sorted_df.index.name = None
snps_retained_sorted_df.to_csv(output_file_3, sep='\t', index=True, header=True)

# step control
step1_end = dt.datetime.now()
step1_diff = step1_end - step1_start
print('The script lasted '+ str(step1_diff.microseconds) + ' μs')

# print final messages
print('The results are ready')
print(reference)