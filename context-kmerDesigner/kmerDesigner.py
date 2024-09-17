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
reference = 'Please, site GitHub (https://github.com/Nicolas-Radomski/canSNPtyping) and/or Docker Hub (https://hub.docker.com/r/nicolasradomski/kmerdesigner)'

# get parser arguments
parser = ap.ArgumentParser(
	prog='kmerDesigner.py', 
	description='Build Hansel input schema designing of kmers harboring canSNPs identified by canSNPextractor.',
	epilog=reference
	)
# define parser arguments
parser.add_argument(
	'-i', '--input', 
	dest='canSNPs', 
	action='store', 
	required=True, 
	help='path of tab-separated values (tsv) file from canSNPextractor output (REQUIRED)'
	)
parser.add_argument(
	'-o', '--output', 
	dest='outputpath', 
	action='store', 
	required=False, 
	default='kmerDesigner',
	help='output path (DEFAULT: kmerDesigner)'
	)
parser.add_argument(
	'-p', '--prefix', 
	dest='prefix', 
	action='store', 
	required=True, 
	help='prefix of output files (REQUIRED)'
	)
parser.add_argument(
	'-s', '--selection', 
	dest='random', 
	type=int,
	action='store', 
	required=True, 
	help='number of randomly selected canSNPs per group of interest (REQUIRED)'
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
	'-g', '--GenBank', 
	dest='chromosome', 
	action='store', 
	required=True, 
	help='chromosome GenBank identifier (REQUIRED)'
	)
parser.add_argument(
	'-a', '--additional', 
	dest='additional', 
	type=int,
	action='store', 
	required=False, 
	default=0,
	help='additional digit to allow merging of canSNP schemes from different chromosomes (DEFAULT: 0)'
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
CANSNPS=args.canSNPs
OUTPUTPATH=args.outputpath
PREFIX=args.prefix
RANDOM=args.random
BASES=args.bases
CHROMOSOME=args.chromosome
ADDITIONAL=args.additional
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

# retrieve information to build a kmers schema
## retrieve positive genotypes (PG) of each first group of interest
### read
input_df = pd.read_csv(CANSNPS, sep='\t', index_col=None)
### keep genotypes not (!=) encoded 2
PG_df = input_df[input_df["Genotype"] != '2']
### keep genotypes not (~) harboring the sting "not"
PG_df = PG_df[~PG_df.Genotype.str.contains('not', regex= True)]
### set output directory
path = os.path.relpath(OUTPUTPATH)
#### output path
outpath = path + '/' + PREFIX + '-positive-genotypes-all-interest-canSNPs.tsv'
#### write output
PG_df.to_csv(outpath, sep="\t", index=False, header=True)

## select randomly positions of positive genotypes (PG) of each first group of interest
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith('positive-genotypes-all-interest-canSNPs.tsv'):
		### input path
		filepath = os.path.join(path, files)
		### retrieve dataframe of positive genotypes (PG)
		PG_df = pd.read_csv(filepath, sep='\t', index_col=None)
		### select randomly positions of positive genotypes (PG) of each first group of interest
		#myfunc = lambda x: x.sample(n=RANDOM, replace=False)
		#random_PG_df = PG_df.groupby('Genotype', group_keys=False).apply(myfunc, include_groups=True) # include_groups=True is depreciated > pd 2.2.0
		#random_PG_df = PG_df.groupby('Genotype').apply(pd.DataFrame.sample, n=1).reset_index(drop=True)
		#random_PG_df = PG_df.groupby('Genotype').apply(pd.DataFrame.sample, n=1).reset_index(drop=True)
		random_PG_df = PG_df.groupby('Genotype').sample(n=RANDOM, replace=False)
		### reset index and drop previous one
		random_PG_df.reset_index(inplace=True, drop='index')
		### output path
		outpath = path + '/' + PREFIX + '-positive-genotypes-random.tsv'
		#### write output
		random_PG_df.to_csv(outpath, sep="\t", index=False, header=True)

## remove potential old downloaded kmer files
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".fasta"):
		### input path
		filepath = os.path.join(path, files)
		### remove
		os.remove(filepath)

## add information required to prepare wget commands
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith('positive-genotypes-random.tsv'):
		### input path
		filepath = os.path.join(path, files)
		### retrieve dataframe of positive genotypes (PG)
		random_PG_df = pd.read_csv(filepath, sep='\t', index_col=None)
		### add a kmer numbers
		random_PG_df.insert(0, 'kmer', range(1, 1 + len(random_PG_df)))
		### calculate positions of upstream 5
		random_PG_df['Upstream-5'] = random_PG_df['SNP Location'] - BASES
		### calculate positions of upstream 3
		random_PG_df['Upstream-3'] = random_PG_df['SNP Location'] - 1
		### calculate positions of downstream 5
		random_PG_df['Downstream-5'] = random_PG_df['SNP Location'] + 1
		### calculate positions of downstream 3
		random_PG_df['Downstream-3'] = random_PG_df['SNP Location'] + BASES
		### output path
		outpath = path + '/' + PREFIX + '-positive-genotypes-random-modif2.tsv'
		#### write output
		random_PG_df.to_csv(outpath, sep="\t", index=False, header=True)

## download kmers
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith('positive-genotypes-random-modif2.tsv'):
		### input path
		filepath = os.path.join(path, files)
		### retrieve dataframe of positive genotypes (PG)
		random_PG_df = pd.read_csv(filepath, sep='\t', index_col=None)
		### prepare string variables
		wget='wget "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id='
		wgetCHR=CHROMOSOME
		wgetSTART='&seq_start='
		wgetSTOP='&seq_stop='
		folder='&rettype=fasta" -O ' + OUTPUTPATH + '/'
		prefix=PREFIX
		name='-kmer-'
		upstream='.upstream.fasta'
		downstream='.downstream.fasta'
		### add information into the dataframe
		random_PG_df = random_PG_df.assign(wget=wget)
		random_PG_df = random_PG_df.assign(wgetCHR=wgetCHR)
		random_PG_df = random_PG_df.assign(wgetSTART=wgetSTART)
		random_PG_df = random_PG_df.assign(wgetSTOP=wgetSTOP)
		random_PG_df = random_PG_df.assign(folder=folder)
		random_PG_df = random_PG_df.assign(prefix=prefix)
		random_PG_df = random_PG_df.assign(name=name)
		random_PG_df = random_PG_df.assign(upstream=upstream)
		random_PG_df = random_PG_df.assign(downstream=downstream)
		### build and run wget commands for upstream kmers
		#### select columns of interest
		cmd_upstream_df = random_PG_df.iloc[:, [9,10,11,5,12,6,13,14,15,0,16]]
		#### convert dataframe to string
		cmd_upstream_txt = cmd_upstream_df.to_string(index=False, header=False)
		#### replace spaces by nothing and add spaces arround 'wget' and '-o'
		cmd_upstream_txt = cmd_upstream_txt.replace(' ', '').replace('-O', ' -O ').replace('wget', 'wget ')
		#### output path
		outpath = path + '/' + PREFIX + '-cmd-upstream.sh'
		#### write output
		with open(outpath, "w") as openfile:
			openfile.write(cmd_upstream_txt)
		#### run sh
		cmd_upstream = 'sh ' + OUTPUTPATH + '/' + PREFIX + '-cmd-upstream.sh'
		os.system(cmd_upstream)
		### build and run wget commands for downstream kmers
		#### select columns of interest
		cmd_downstream_df = random_PG_df.iloc[:, [9,10,11,7,12,8,13,14,15,0,17]]
		#### convert dataframe to string
		cmd_downstream_txt = cmd_downstream_df.to_string(index=False, header=False)
		#### replace spaces by nothing and add spaces arround 'wget' and '-o'
		cmd_downstream_txt = cmd_downstream_txt.replace(' ', '').replace('-O', ' -O ').replace('wget', 'wget ')
		#### output path
		outpath = path + '/' + PREFIX + '-cmd-downstream.sh'
		#### write output
		with open(outpath, "w") as openfile:
			openfile.write(cmd_downstream_txt)
		#### run sh
		cmd_downstream = 'sh ' + OUTPUTPATH + '/' + PREFIX + '-cmd-downstream.sh'
		os.system(cmd_downstream)

## compile uptream bases
### create empty lists
#### for sequences
seq_upstream = []
#### for kmer numbers
kmer_numbers_upstream = []
### iterate for each file
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith('.upstream.fasta'):
		### input path
		filepath = os.path.join(path, files)
		### retrieve the sequences into the empty list
		with open(filepath, "r") as openfile:
			seq_upstream.append(openfile.readlines()[1].rstrip())
		### retrieve the kmer numbers into the empty list
		kmer_numbers_upstream.append(int(files.split("-kmer-")[1].split(".")[0]))
### create a dictionnary with kmer numbers and sequences
kmers_upstream_data = {'kmer': kmer_numbers_upstream,'sequence': seq_upstream}
### transform the dictionnary 
kmers_upstream_df = pd.DataFrame(kmers_upstream_data).sort_values('kmer', ascending=True).reset_index().drop(columns=['index'])
### output path
outpath = path + '/' + PREFIX + '-kmers.upstream.tsv'
#### write output
kmers_upstream_df.to_csv(outpath, sep="\t", index=False, header=True)

## compile downstream bases
### create empty lists
#### for sequences
seq_downstream = []
#### for kmer numbers
kmer_numbers_downstream = []
### iterate for each file
for files in os.listdir(path):
	### select files of interest
	if files.startswith(PREFIX + '-') and files.endswith('.downstream.fasta'):
		### input path
		filepath = os.path.join(path, files)
		### retrieve the sequences into the empty list
		with open(filepath, "r") as openfile:
			seq_downstream.append(openfile.readlines()[1].rstrip())
		### retrieve the kmer numbers into the empty list
		kmer_numbers_downstream.append(int(files.split("-kmer-")[1].split(".")[0]))
### create a dictionnary with kmer numbers and sequences
kmers_downstream_data = {'kmer': kmer_numbers_downstream,'sequence': seq_downstream}
### transform the dictionnary 
kmers_downstream_df = pd.DataFrame(kmers_downstream_data).sort_values('kmer', ascending=True).reset_index().drop(columns=['index'])
### output path
outpath = path + '/' + PREFIX + '-kmers.downstream.tsv'
#### write output
kmers_downstream_df.to_csv(outpath, sep="\t", index=False, header=True)

## combine genotype informations and kmers
### input path
filepath = path + '/' + PREFIX + '-positive-genotypes-random-modif2.tsv'
### retrieve dataframe of positive genotypes (PG)
random_PG_df = pd.read_csv(filepath, sep='\t', index_col=None)
### with upstream sequences
random_PG_upstream_df = random_PG_df.set_index('kmer').join(kmers_upstream_df.set_index('kmer'), 
	on='kmer', 
	how='inner').rename(columns = {'sequence':'Upstream'}).reset_index(drop = False)
### with downstream sequences
random_PG_updownstream_df = random_PG_upstream_df.set_index('kmer').join(kmers_downstream_df.set_index('kmer'), 
	on='kmer', 
	how='inner').rename(columns = {'sequence':'Downstream'}).reset_index(drop = False)
### output path
outpath = path + '/' + PREFIX + '-positive-genotypes-random-modif5.tsv'
#### write output
random_PG_updownstream_df.to_csv(outpath, sep="\t", index=False, header=True)

## add to SNP positions a digit related to chromosome number 
### modify the dataframe
random_PG_updownstream_df['SNP Location'] = random_PG_updownstream_df['SNP Location'] + ADDITIONAL
### output path
outpath = path + '/' + PREFIX + '-positive-genotypes-random-info.tsv'
#### write output
random_PG_updownstream_df.to_csv(outpath, sep="\t", index=False, header=True)

# build a schema
## build a schema with "Positive Base"
### select the columns of interest
schema_positive_df = random_PG_updownstream_df.iloc[:, [2,1,9,3,10]]
### silence SettingWithCopyWarning
pd.options.mode.chained_assignment = None
### add string to each value in a column
schema_positive_df.loc[schema_positive_df.index, 'Genotype'] = '-' + schema_positive_df['Genotype'].astype(str) + ':'
### add a column
schema_positive_df.insert(0, 'fasta', '>')
### convert dataframe to string
schema_positive_txt = schema_positive_df.to_string(index=False, header=False)
### replace spaces by nothing
schema_positive_txt = schema_positive_txt.replace(' ', '')
### replace strings by hard returns
schema_positive_txt = schema_positive_txt.replace(':', '\n')

## build a schema with "Negative Base"
### for first nodes (i.e. genotype 2)
#### select the columns of interest
schema_first_node_df = random_PG_updownstream_df.iloc[:, [2,1,9,4,10]]
#### select the genotype 1
schema_first_node_df = schema_first_node_df.loc[schema_first_node_df["Genotype"] == '1']
#### replace genotype 1 by 2
schema_first_node_df = schema_first_node_df.replace('1', '2')
#### add string to each value in a column
schema_first_node_df.loc[schema_first_node_df.index, 'Genotype'] = '-' + schema_first_node_df['Genotype'].astype(str) + ':'
### add a column
schema_first_node_df.insert(0, 'fasta', '>')
#### convert dataframe to string
schema_first_node_txt = schema_first_node_df.to_string(index=False, header=False)
#### replace spaces by nothing
schema_first_node_txt = schema_first_node_txt.replace(' ', '')
#### replace strings by hard returns
schema_first_node_txt = schema_first_node_txt.replace(':', '\n')

### for intermediate nodes (i.e. other than genotypes 1 and 2)
#### select the columns of interest
schema_intermediate_nodes_df = random_PG_updownstream_df.iloc[:, [2,1,9,4,10]]
#### select the intermediate genotypes (other than 1)
schema_intermediate_nodes_df = schema_intermediate_nodes_df.loc[schema_intermediate_nodes_df["Genotype"] != '1']
#### add string to each value in a column
schema_intermediate_nodes_df.loc[schema_intermediate_nodes_df.index, 'Genotype'] = '-' + schema_intermediate_nodes_df['Genotype'].astype(str) + ':'
### add a column
schema_intermediate_nodes_df.insert(0, 'fasta', '>negative')
#### convert dataframe to string
schema_intermediate_nodes_txt = schema_intermediate_nodes_df.to_string(index=False, header=False)
#### replace spaces by nothing
schema_intermediate_nodes_txt = schema_intermediate_nodes_txt.replace(' ', '')
#### replace strings by hard returns
schema_intermediate_nodes_txt = schema_intermediate_nodes_txt.replace(':', '\n')

### combine first and intermediate nodes
schema_negative_txt = schema_first_node_txt + '\n' + schema_intermediate_nodes_txt

## build schema with "Positive Base" and "Negative Base"
### concatenate
schema_txt = schema_positive_txt + '\n' + schema_negative_txt + '\n'
### output path
outpath = path + '/' + PREFIX + '-schema.db'
### write output
with open(outpath, "w") as openfile:
	openfile.write(schema_txt)

## remove intermadiate files
### from files in output directory
for files in os.listdir(path):
	### select files
	if files.startswith(PREFIX + '-') and files.endswith(".sh") or files.endswith(".fasta") or files.endswith("-clean.tsv") or files.endswith("-modif2.tsv") or files.endswith("-modif5.tsv") or files.endswith(".upstream.tsv") or files.endswith(".downstream.tsv"):
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