# pip3.12 install --force-reinstall pandas==2.2.2

# import packages
import sys as sys # no individual installation because is part of the Python Standard Library
import os as os # no individual installation because is part of the Python Standard Library
import datetime as dt # no individual installation because is part of the Python Standard Library
import re as re # no individual installation because is part of the Python Standard Library
import argparse as ap # no individual installation because is part of the Python Standard Library
import pandas as pd

# step control
step1_start = dt.datetime.now()

# set workflow reference
reference = 'Please, site GitHub (https://github.com/Nicolas-Radomski/canSNPtyping) and/or Docker Hub (https://hub.docker.com/r/nicolasradomski/cansnpextractor)'

# get parser arguments
parser = ap.ArgumentParser(
	prog='canSNPextractor.py', 
	description='Extraction of canSNPs based on feht output.',
	epilog=reference
	)
# define parser arguments
parser.add_argument(
	'-i', '--input', 
	dest='feht', 
	action='store', 
	required=True, 
	help='path of tab-separated values (tsv) file from feht output (REQUIRED)'
	)
parser.add_argument(
	'-o', '--output', 
	dest='outputpath', 
	action='store', 
	required=False, 
	default='canSNPextractor',
	help='output path (DEFAULT: canSNPextractor)'
	)
parser.add_argument(
	'-p', '--prefix', 
	dest='prefix', 
	action='store', 
	required=True, 
	help='prefix of output files (REQUIRED)'
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
FEHT=args.feht
OUTPUTPATH=args.outputpath
PREFIX=args.prefix
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
	if re.__version__ != "2.2.1":
		raise Exception('re 2.2.1 version is recommended')
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

# extract canSNPs from all comparisons
## split tables and clean
### open feht output and read lines
feht_output = open(FEHT).readlines()
### set count
c = 0
for line in feht_output:
	### split tables
	if "#-" in line:
		if c == 0:
			new = open(OUTPUTPATH + "/" + PREFIX + "-cansnps-" + "{:02d}".format(c) + ".feht","w")
			c+=1
		else:
			new.close()
			new = open(OUTPUTPATH + "/" + PREFIX + "-cansnps-" + "{:02d}".format(c) + ".feht","w")
			c+=1
	### clean tables
	else:
		if "-#]" not in line and "Done" not in line and line != "" and line[0:3] != "---":
			new.write(line)
new.close()

## clean new tables and combine two first lines
### set output directory
path = os.path.relpath(OUTPUTPATH)
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".feht"):
		### input path
		filepath = os.path.join(path, files)
		### cleaning
		with open(filepath) as openfile:
			s = openfile.read()
			s = s.replace('---', '')
			s = s.replace('\n\n','\n').replace('\n\n','\n')
			s = s.replace('Group1 category: ', '')
			s = s.replace('Group2 category: ', '')
			s = s.replace('\n', 'vs', 1)
			s = s.replace(' ', '')
			s = s.replace('!', 'not')
			s = re.sub("Level_[0-9][0-9]*Group[0-9][0-9]*:", "", s)
			### output path
			outpath = filepath.replace('.feht', '.new')
			### write output
			with open(outpath, "w") as openfile:
				openfile.write(s)

## replace names of new tables
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".new"):
		### input path
		filepath = os.path.join(path, files)
		### extract first line
		with open(filepath) as openfile:
			firstline = openfile.readline().strip()
			### output path
			outpath = path + '/' + PREFIX + '-' + firstline + '.cansnps'
		### rename
		os.rename(filepath, outpath)

## remove intermadiate files
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".feht"):
		### input path
		filepath = os.path.join(path, files)
		### remove
		os.remove(filepath)

# retain canSNPs from comparisons of interest
## identify files corresponding to comparisons of interest
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith(".cansnps") and re.search('vsnot[0-9]', files) or re.search('-1vs2.', files):
		### input path
		filepath = os.path.join(path, files)
		### output path
		outpath = filepath.replace('.cansnps', '.interest')
		### rename
		os.rename(filepath, outpath)

## trash files of disinterest
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".cansnps"):
		### input path
		filepath = os.path.join(path, files)
		### remove
		os.remove(filepath)

# count positions for each comparisons of interest
## binary and categorical SNPs (i.e. without duplicated positions)
### prepare empty output files
total_file = open(path +"/" + PREFIX + "-canSNPs-count-all.txt","w")
unique_file = open(path +"/" + PREFIX + "-canSNPs-count-categorical.txt","w")
duplicate_file = open(path +"/" + PREFIX + "-canSNPs-count-binary.txt","w")
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith(".interest"):
		### input path
		filepath = os.path.join(path, files)
		### add positions into distinct lists
		with open(filepath) as openfile:
			### create empty lists
			total = []
			unique = []
			duplicate = []
			### reads from the second lines (excluded)
			tables = openfile.readlines()[2:]
			for line in tables:
				### retrieve positions
				position = line.split("_")[0]
				### add positions in the total list if not in the total list
				if position not in total:
					total.append(position)
				### add positions in the duplicate list if in the total list
				else:
					duplicate.append(position)
			for value in total:
				### add positions in the unique list if in the duplicate list
				if value not in duplicate:
					unique.append(position)
			### write into output
			total_file.write(path+"/"+files+"\n"+str(len(total))+"\n")
			unique_file.write(path+"/"+files+"\n"+str(len(unique))+"\n")
			duplicate_file.write(path+"/"+files+"\n"+str(len(duplicate))+"\n")
### close into output
total_file.close()
unique_file.close()
duplicate_file.close()

# combine canSNPs as lists for each comparisons of interest (Genotype, SNP Location, Positive Base, Negative Base)
## list genotypes of the first group
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith(".interest"):
		### input path
		filepath = os.path.join(path, files)
		### first compared group
		FG = files.replace('.interest', '').replace(PREFIX+'-', '').split('vs')[0]
		### transform tables
		with open(filepath) as openfile:
			#### read as pandas
			df = pd.read_csv(openfile, sep='\t', index_col=None, skiprows=[0])
			#### split column
			df[['Position', 'Genotype']] = df['Name'].str.split('_', n=1, expand=True)
			#### drop column
			df.drop(columns=['Name'], inplace=True)
			#### rearrange column
			df = df[['Position', 'Genotype', 'GroupOne(+)', 'GroupOne(-)', 'GroupTwo(+)', 'GroupTwo(-)', 'pValue', 'Ratio']]
			#### filter column
			df = df[(df['Ratio'] == 1.0)]
			#### drop column
			df.drop(columns=['GroupOne(+)',  'GroupOne(-)',  'GroupTwo(+)',  'GroupTwo(-)',  'pValue',  'Ratio'], inplace=True)
			#### transform lowercase to uppercase
			df['Genotype'] = df['Genotype'].str.upper()
			#### transform as interger
			df['Position'] = df['Position'].astype(int)
			#### sort column and reset index
			df = df.sort_values(by='Position', ascending=True).reset_index(drop = True)
			#### drop header
			df.columns = range(df.shape[1])
			#### output path
			outpath = path + '/' + PREFIX + '-genotypes-first-group-' + FG + '.tab'
			#### write output
			df.to_csv(outpath, sep="\t", index=False, header=False)
## list genotypes of the second group
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith(".interest"):
		### input path
		filepath = os.path.join(path, files)
		### second compared group
		SG = files.replace('.interest', '').replace(PREFIX+'-', '').split('vs')[1]
		### transform tables
		with open(filepath) as openfile:
			#### read as pandas
			df = pd.read_csv(openfile, sep='\t', index_col=None, skiprows=[0])
			#### split column
			df[['Position', 'Genotype']] = df['Name'].str.split('_', n=1, expand=True)
			#### drop column
			df.drop(columns=['Name'], inplace=True)
			#### rearrange columns
			df = df[['Position', 'Genotype', 'GroupOne(+)', 'GroupOne(-)', 'GroupTwo(+)', 'GroupTwo(-)', 'pValue', 'Ratio']]
			#### filter column
			df = df[(df['Ratio'] == -1.0)]
			#### drop column
			df.drop(columns=['GroupOne(+)',  'GroupOne(-)',  'GroupTwo(+)',  'GroupTwo(-)',  'pValue',  'Ratio'], inplace=True)
			#### transform lowercase to uppercase
			df['Genotype'] = df['Genotype'].str.upper()
			#### transform as interger
			df['Position'] = df['Position'].astype(int)
			#### sort column
			df = df.sort_values(by='Position', ascending=True).reset_index(drop = True)
			#### drop header
			df.columns = range(df.shape[1])
			#### output path
			outpath = path + '/' + PREFIX + '-genotypes-second-group-' + SG + '.tab'
			#### write output
			df.to_csv(outpath, sep="\t", index=False, header=False)
## join positive and negative genotypes for both first and second groups
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith(".interest"):
		### first compared group
		FG = files.replace('.interest', '').replace(PREFIX+'-', '').split('vs')[0]
		### second compared group
		SG = files.replace('.interest', '').replace(PREFIX+'-', '').split('vs')[1]
		### input path
		filepathFG = path + '/' + PREFIX + '-genotypes-first-group-' + FG + '.tab'
		filepathSG = path + '/' + PREFIX + '-genotypes-second-group-' + SG + '.tab'
		### read dataframe
		dfFG = pd.read_csv(filepathFG, sep='\t', names = ['POS','Genotype'])
		dfSG = pd.read_csv(filepathSG, sep='\t', names = ['POS','Genotype'])
		### join positive and negative genotypes for the first groups
		dfFGSG = dfFG.set_index('POS').join(dfSG.set_index('POS'), 
															on='POS', 
															how='inner', 
															lsuffix='Pos', 
															rsuffix='Neg').assign(Group = FG).reindex(columns=['Group', 'GenotypePos', 'GenotypeNeg']).reset_index(drop = False)
		### join positive and negative genotypes for the second groups
		dfSGFG = dfSG.set_index('POS').join(dfFG.set_index('POS'), 
															on='POS', 
															how='inner', 
															lsuffix='Pos', 
															rsuffix='Neg').assign(Group = SG).reindex(columns=['Group', 'GenotypePos', 'GenotypeNeg']).reset_index(drop = False)
		#### rearrange columns
		dfFGSG = dfFGSG[['Group', 'POS', 'GenotypePos', 'GenotypeNeg']]
		dfSGFG = dfSGFG[['Group', 'POS', 'GenotypePos', 'GenotypeNeg']]
		### outpout paths
		outpathFGSG = path + '/' + PREFIX + '-genotypes-' + FG + '-clean.tsv'
		outpathSGFG = path + '/' + PREFIX + '-genotypes-' + SG + '-clean.tsv'
		#### write output
		dfFGSG.to_csv(outpathFGSG, sep="\t", index=False, header=False)
		dfSGFG.to_csv(outpathSGFG, sep="\t", index=False, header=False)
## combine clean dataframes of genotypes into one dataframe of genotypes
### create a empty list
lst = []
### iterate for each clean dataframes
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith("-clean.tsv"):
		### input path
		filepath = os.path.join(path, files)
		### read dataframes
		dfClean = pd.read_csv(filepath, sep='\t', names = ['Genotype','SNP Location','Positive Base','Negative Base'])
		### expand the list with each new dataframe
		lst.append(dfClean)
### concatenate dataframes into one dataframe
dfFinal = pd.concat(lst, ignore_index=True)
### sort columns
dfFinal = dfFinal.sort_values(['Genotype', 'SNP Location'], ascending=[True, True])
### outpout path
outpath = path + '/' + PREFIX + '-genotypes-all-interest-canSNPs.tsv'
#### write output
dfFinal.to_csv(outpath, sep="\t", index=False, header=True)

## remove intermadiate files
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".interest") or files.endswith(".tab") or files.endswith("-clean.tsv"):
		### input path
		filepath = os.path.join(path, files)
		### remove
		os.remove(filepath)

# step control
step1_end = dt.datetime.now()
step1_diff = step1_end - step1_start
print('The script lasted '+ str(step1_diff.microseconds) + ' μs')

# print final messages
print('The results are ready')
print(reference)