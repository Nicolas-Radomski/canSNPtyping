# Usage
The repository canSNPtyping provides Python (recommended version 3.12) or Bash (tested with Ubuntu 20.04) scripts called dispersedSNPselector, canSNPextractor and kmerDesigner to build schemes of canonical single-nucleotide polymorphisms (canSNPs) based on feht output and compatible with hansel input.
- dispersedSNPselector: exclusion of SNP hotspots
- canSNPextractor: extraction of canSNPs
- kmerDesigner: design of kmers harboring selected canSNPs
# Case study
The example below aims at building schemes of canSNPs for Brucella chromosomes I (reference: AE014291.4) and/or II (reference: AE014292.2).
# Background
## Workflow dependencies
The workflow is adapted from recommendations of the hansel tool and implies tools below (https://bio-hansel.readthedocs.io/en/readthedocs/user-docs/genotyping_schemes.html#creating-a-genotyping-scheme).
- snippy: variant calling (https://github.com/tseemann/snippy)
- IQtree: phylogenomic inference (http://www.iqtree.org/)
- iTOL: rooted phylogenomic inference (https://itol.embl.de/)
- feht: exhaustive identification of SNPs specific of defined groups (https://github.com/chadlaing/feht)
- hansel: canSNP typing based on schemes organized in the form of kmers (https://github.com/phac-nml/biohansel)
## Recommended python environment
### update
```
sudo apt update -y
sudo apt upgrade -y
```
### install Ubuntu packages
```
sudo apt install -y software-properties-common build-essential libffi-dev libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev libssl-dev
```
### install python 3.12
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
```
### install pip 3.12
```
sudo apt install python3.12-distutils 
wget https://bootstrap.pypa.io/get-pip.py 
sudo python3.12 get-pip.py 
```
### install python libraries
```
# pip3.12 install pandas==2.2.2
# pip3.12 install numpy==1.26.4
```
## Recommended docker environment
```
docker pull nicolasradomski/dispersedsnpselector
docker pull nicolasradomski/cansnpextractor
docker pull nicolasradomski/kmerdesigner
docker pull nicolasradomski/kmerdesignerfast
```
# Examples of commands
## Program dispersedSNPselector
### arguments
- arg1 (-i): input
- optional python arg (-o): output path
- arg2 (-p): output prefix
- arg3 (-c): chromosome size
- arg4 (-n): size of kmer sequences up and downstream of canSNPs
- optional python arg (-nc): no checking of the versions of Python libraries
### run with Python
```
python dispersedSNPselector.py -i snippy/chromoI.tab -p chromoI -c 2107794 -n 16 -nc
python dispersedSNPselector.py -i snippy/chromoII.tab -p chromoII -c 1207381 -n 16 -nc
```
### run with Bash
```
sh dispersedSNPselector.sh snippy/chromoI.tab chromoI 2107794 16
sh dispersedSNPselector.sh snippy/chromoII.tab chromoII 1207381 16
```
### run with Docker
```
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/dispersedsnpselector -i snippy/chromoI.tab -p chromoI -c 2107794 -n 16
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/dispersedsnpselector -i snippy/chromoII.tab -p chromoII -c 1207381 -n 16
```
## Program feht
### arguments
- arg1 (-i): input metadata
- arg2 (-d): input SNPs
- arg3 (-f): specific SNPs
- arg4 (-m): SNP mode
### run
```
feht -i feht/metadata.tsv -d dispersedSNPselector/chromoI-SNPs-retained-trimmed-profiles.tsv -f 1 -m snp > feht/chromoI-cansnps.tsv
feht -i feht/metadata.tsv -d dispersedSNPselector/chromoII-SNPs-retained-trimmed-profiles.tsv -f 1 -m snp > feht/chromoII-cansnps.tsv
```
## Program canSNPextractor
### arguments
- arg1 (-i): input
- optional python arg (-o): output path
- arg2 (-p): output prefix
- optional python arg (-nc): no checking of the versions of Python libraries
### run with Python
```
python canSNPextractor.py -i feht/chromoI-cansnps.tsv -p chromoI -nc
python canSNPextractor.py -i feht/chromoII-cansnps.tsv -p chromoII -nc
```
### run with Bash
```
sh canSNPextractor.sh feht/chromoI-cansnps.tsv chromoI
sh canSNPextractor.sh feht/chromoII-cansnps.tsv chromoII
```
### run with Docker
```
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/cansnpextractor -i feht/chromoI-cansnps.tsv -p chromoI
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/cansnpextractor -i feht/chromoII-cansnps.tsv -p chromoII
```
## Program kmerDesigner
### arguments
- arg1 (-i): input
- optional python arg (-o): output path
- arg2 (-p): output prefix
- arg3 (-s): randomly selected positive genotypes per node of interest
- arg4 (-n): size of kmer sequences up and downstream of canSNPs
- arg5 (-f or -g): chromosome fasta file path or chromosome GenBank identifier
- arg6 (-a): additional digit to position to merge schemes from different chromosomes
- optional python arg (-nc): no checking of the versions of Python libraries
### run with Python dependently of a reference fasta file
```
python kmerDesignerFast.py -i canSNPextractor/chromoI-genotypes-all-interest-canSNPs.tsv -p chromoI -s 4 -n 16 -f reference/AE014291.4.fasta -a 10000000 -nc
python kmerDesignerFast.py -i canSNPextractor/chromoII-genotypes-all-interest-canSNPs.tsv -p chromoII -s 4 -n 16 -f reference/AE014292.2.fasta -a 20000000 -nc
```
### run with Python dependently of a reference GenBank identifier
```
python kmerDesigner.py -i canSNPextractor/chromoI-genotypes-all-interest-canSNPs.tsv -p chromoI -s 4 -n 16 -g AE014291.4 -a 10000000 -nc
python kmerDesigner.py -i canSNPextractor/chromoII-genotypes-all-interest-canSNPs.tsv -p chromoII -s 4 -n 16 -g AE014292.2 -a 20000000 -nc
```
### run with Bash dependently of a reference GenBank identifier
```
sh kmerDesigner.sh canSNPextractor/chromoI-genotypes-all-interest-canSNPs.tsv chromoI 4 16 AE014291.4 10000000
sh kmerDesigner.sh canSNPextractor/chromoII-genotypes-all-interest-canSNPs.tsv chromoII 4 16 AE014292.2 20000000
```
### run with Docker dependently of a reference GenBank identifier
```
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/kmerdesigner -i docker-cansnpextractor/chromoI-genotypes-all-interest-canSNPs.tsv -p chromoI -s 4 -n 16 -g AE014291.4 -a 10000000
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/kmerdesigner -i docker-cansnpextractor/chromoII-genotypes-all-interest-canSNPs.tsv -p chromoII -s 4 -n 16 -g AE014292.2 -a 20000000
```
### run with Docker dependently of a reference fasta file
```
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/kmerdesignerfast -i docker-cansnpextractor/chromoI-genotypes-all-interest-canSNPs.tsv -p chromoI -s 4 -n 16 -f reference/AE014291.4.fasta -a 10000000
docker run --rm --name nicolas -u $(id -u):$(id -g) -v $(pwd):/wd nicolasradomski/kmerdesignerfast -i docker-cansnpextractor/chromoII-genotypes-all-interest-canSNPs.tsv -p chromoII -s 4 -n 16 -f reference/AE014292.2.fasta -a 20000000
```
## Merging of schemes from chromosomes I and II
```
cat kmerDesigner/chromoI-schema.db kmerDesigner/chromoII-schema.db > kmerDesigner/chromoI-II-schema.db
```
## Program hansel
### arguments
- arg1 (-s): input schema
- arg2 (--vv): verbosity level
- arg3 (-t): threads
- arg4 (-o): typing output
- arg5 (-O): match output
- arg6 (-D): input format
### run
```
hansel -s kmerDesigner/chromoI-schema.db -vv -t 20 -o hansel/chromoI-results-fastq.tab -O hansel/chromoI-match_results-fastq.tab -D fastq
hansel -s kmerDesigner/chromoII-schema.db -vv -t 20 -o hansel/chromoII-results-fastq.tab -O hansel/chromoII-match_results-fastq.tab -D fastq
hansel -s kmerDesigner/chromoI-II-schema.db -vv --threads 20 -o hansel/chromoI-II-results-fastq.tab -O hansel/chromoI-II-match_results-fastq.tab -D fastq
```
# Expected input and output
## Nucleotide profiles of SNPs for each chromosome (snippy/chromoI.tab)
```
CHR		POS	REF	SRR1371301	SRR1371327	SRR1371373	SRR1371384	SRR5207310
AE014291	23	C	C		C		C		C		C
AE014291	330	T	T		T		T		T		T
AE014291	398	G	A		A		A		A		G
AE014291	524	G	G		G		G		G		G
AE014291	813	A	A		A		A		A		A
AE014291	1167	C	T		T		T		T		C
AE014291	2061	A	G		G		G		G		A
AE014291	2253	C	T		T		T		T		C
AE014291	2425	C	C		C		C		C		C
AE014291	2956	C	C		C		C		C		C
AE014291	3256	G	A		A		A		A		G
AE014291	3609	C	C		C		C		C		C
AE014291	3871	C	C		C		C		C		C
AE014291	3934	C	T		T		T		T		C
AE014291	4219	T	C		C		C		C		T
AE014291	4223	G	C		C		C		C		G
AE014291	4498	A	C		C		C		C		A
```
## Nucleotide profiles of SNPs for each chromosome excluding hotspots of SNPs (dispersedSNPselector/chromoI-SNPs-retained-trimmed-profiles.tsv)
```
	SRR1371301	SRR1371327	SRR1371373	SRR1371384	SRR5207310
23	C		C		C		C		C
330	T		T		T		T		T
398	A		A		A		A		G
524	G		G		G		G		G
813	A		A		A		A		A
1167	T		T		T		T		C
2061	G		G		G		G		A
2253	T		T		T		T		C
2425	C		C		C		C		C
2956	C		C		C		C		C
3256	A		A		A		A		G
3609	C		C		C		C		C
3871	C		C		C		C		C
3934	T		T		T		T		C
4498	C		C		C		C		A
```
## Metadata defining groups of interest (feht/metadata.tsv)
```
Strain_name	Level_0	Level_1	Level_2
SRR5207310	1	1.1	NA
SRR5207315	1	1.1	NA
SRR5207320	1	1.1	NA
SRR5207321	1	1.1	NA
SRR5207328	1	1.1	NA
SRR8550474	1	1.2	1.2.2
SRR8550491	1	1.2	1.2.2
SRR8550496	1	1.2	1.2.2
SRR8550507	1	1.2	1.2.2
SRR8550514	1	1.2	1.2.1
SRR1371301	2	2.1	2.1.1
SRR1371327	2	2.1	2.1.1
SRR1371373	2	2.1	2.1.1
SRR1371384	2	2.1	2.1.1
SRR8423077	2	2.1	2.1.2
SRR6957988	2	2.2	NA
SRR6958002	2	2.2	NA
SRR6958007	2	2.2	NA
SRR6958009	2	2.2	NA
SRR6957952	2	2.2	NA
```
## Tables of all specific SNPs of each defined groups (feht/chromoI-cansnps.tsv)
```
[#-
Group1 category: Level_2 Group1: 2.1.1
Group2 category: Level_2 Group2: 2.1.2
---
Name	GroupOne (+)	GroupOne (-)	GroupTwo (+)	GroupTwo (-)	pValue	Ratio
624756_g	4	0	0	1	1.0	1.0
1169661_g	4	0	0	1	1.0	1.0
1557985_g	4	0	0	1	1.0	1.0
1296954_c	0	4	1	0	1.0	-1.0
1230711_t	4	0	0	1	1.0	1.0
```
## Positive and negative genotypes of all canSNPs (canSNPextractor/chromoI-genotypes-all-interest-canSNPs.tsv)
```
Genotype	SNP Location	Positive Base	Negative Base
1	1167	C	T
1	2061	A	G
1	5089	C	T
1	5656	T	C
1	6936	C	T
1	11784	G	A
1	12528	G	C
1	14062	T	G
1	15047	G	C
...
not2.2	2082770	G	A
not2.2	2086716	G	A
not2.2	2086861	G	A
not2.2	2089793	C	T
not2.2	2090087	T	C
not2.2	2096542	C	T
not2.2	2099716	G	T
not2.2	2101069	G	A
not2.2	2106119	T	C
not2.2	2106619	T	C
```
## canSNP schema organized in the form of kmers (kmerDesigner/chromoI-schema.db)
```
Genotype	SNP Location	Positive Base	Negative Base
>10186337-1
CCGGGTCTCAAAGGCCGCCGTTTTCGGCCCACC
>11329515-1
CTTCGATCTCGTCTATGACCAGCTTGTAGCAAA
>11357841-1
TGTGGCCAGGGACGAGCCGAACTTCCCTCTCCT
>11814018-1
CAGCACGCTGCATCCAGCGCGCCATCCATGGCG
>10321604-1.1
GCGAGGTTCCGGTGCGAAATCGTGGAGGAGAAA
...
>negative11298681-2.1.2
TCACGGCTGCTGGCCTGTCAACAAAGTCGTCCA
>negative10241192-2.2
GTTTCAAGGCGACGCCGGGTTCAGCCCATGTCT
>negative10727253-2.2
GTGCAGCAGCATCCGCCGGATTTGTCGACTCTA
>negative11438156-2.2
TCACCAGGCTTGCCACACAGAACCTCACTGATT
>negative11915898-2.2
GAAAACGTGGTGATGACGCGCACTTTCTCGAAG
```
## canSNP typing (hansel/chromoI-results-fastq.tab)
```
						prediction	prediction	prediction
sample		brucella	expectation	chromosome I	chromosome II	chromosome I and II
SRR6957988	melitensis	2; 2.2		2; 2.2		2; 2.2		2; 2.2
SRR6958007	melitensis	2; 2.2		2; 2.2		2; 2.2		2; 2.2
SRR6958009	melitensis	2; 2.2		2; 2.2		2; 2.2		2; 2.2
SRR6957952	melitensis	2; 2.2		2; 2.2		2; 2.2		2; 2.2
SRR6958002	melitensis	2; 2.2		2; 2.2		2; 2.2		2; 2.2
SRR8423077	abortus		2; 2.1; 2.1.2	2; 2.1; 2.1.2	2; 2.1; 2.1.2	2; 2.1; 2.1.2
SRR1371373	abortus		2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1
SRR1371384	abortus		2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1
SRR1371301	abortus		2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1
SRR1371327	abortus		2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1	2; 2.1; 2.1.1
SRR8550507	suis biovar 2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2
SRR8550491	suis biovar 2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2
SRR8550474	suis biovar 2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2
SRR8550496	suis biovar 2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2	1; 1.2; 1.2.2
SRR8550514	suis biovar 2	1; 1.2; 1.2.1	1; 1.2; 1.2.1	1; 1.2; 1.2.1	1; 1.2; 1.2.1
SRR5207320	suis biovar 1	1; 1.1		1; 1.1		1; 1.1		1; 1.1
SRR5207328	suis biovar 1	1; 1.1		1; 1.1		1; 1.1		1; 1.1
SRR5207321	suis biovar 1	1; 1.1		1; 1.1		1; 1.1		1; 1.1
SRR5207315	suis biovar 1	1; 1.1		1; 1.1		1; 1.1		1; 1.1
SRR5207310	suis biovar 1	1; 1.1		1; 1.1		1; 1.1		1; 1.1
```
# Illustration
![workflow figure](https://github.com/Nicolas-Radomski/canSNPtyping/blob/main/illustration.png)
# Reference
Labbé G, Kruczkiewicz P, Robertson J, Mabon P, Schonfeld J, Kein D, Rankin MA, Gopez M, Hole D, Son D, Knox N, Laing CR, Bessonov K, Taboada EN, Yoshida C, Ziebell K, Nichani A, Johnson RP, Van Domselaar G, Nash JHE. Rapid and accurate SNP genotyping of clonal bacterial pathogens with BioHansel. Microb Genom. 2021 Sep;7(9):000651. doi: 10.1099/mgen.0.000651. PMID: 34554082; PMCID: PMC8715432.
# Please site
https://github.com/Nicolas-Radomski/canSNPtyping
https://hub.docker.com/r/nicolasradomski/dispersedsnpselector
https://hub.docker.com/r/nicolasradomski/cansnpextractor
https://hub.docker.com/r/nicolasradomski/kmerdesigner
https://hub.docker.com/r/nicolasradomski/kmerdesignerfast
# Acknowledgment
The GENPAT-IZSAM Staff for our discussions aiming at designing workflows, especially Iolanda Mangone and Pierluigi Castelli for our discussions about the Python syntax.
# Author
Nicolas Radomski
