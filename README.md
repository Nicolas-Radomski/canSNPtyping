# Source codes will be provided soon
# Usage
The repository canSNPtyping provides three Bash scripts called pointSNPselector.sh, canSNPextractor.sh and kmerDesigner.sh to build schemes of canonical single-nucleotide polymorphisms (canSNPs) based on feht output and compatible with Hansel input.
- pointSNPselector.sh: exclusion of SNP hotspots
- canSNPextractor.sh: extraction of canSNPs
- kmerDesigner.sh: design of kmers harboring selected canSNPs
# Workflow dependencies
The workflow is adapted from recommendations of the hansel tool and implies tools below (https://bio-hansel.readthedocs.io/en/readthedocs/user-docs/genotyping_schemas.html#creating-a-genotyping-schema).
- snippy: variant calling (https://github.com/tseemann/snippy)
- IQtree: phylogenomic inference (http://www.iqtree.org/)
- iTOL: rooted phylogenomic inference (https://itol.embl.de/)
- feht: exhaustive identification of SNPs specific of defined groups (https://github.com/chadlaing/feht)
- hansel: canSNP typing based on schemes organized in the form of kmers (https://github.com/phac-nml/biohansel)
# Case study
The example below aims at building schemes of canSNPs for Brucella chromosomes I (reference: AE014291.4) and/or II (reference: AE014292.2).
# Examples of commands
## pointSNPselector.sh
- arg1: input
- arg2: output prefix
- arg3: chromosome size
- arg4: size of kmer sequences up and downstream of canSNPs
```
sh pointSNPselector.sh snippy/chromoI.tab chromoI 2107794 16
sh pointSNPselector.sh snippy/chromoII.tab chromoII 1207381 16
```
## feht
- -i: input metadata
- -d: input SNPs
- -f: specific SNPs
- -m: SNP mode
- \>: output
```
feht -i feht/metadata.tsv -d pointSNPselector/chromoI-snps-retained-sorted-header.tsv -f 1 -m snp > feht/chromoI-cansnps.tsv
feht -i feht/metadata.tsv -d pointSNPselector/chromoII-snps-retained-sorted-header.tsv -f 1 -m snp > feht/chromoII-cansnps.tsv
```
## canSNPextractor.sh
- arg1: input
- arg2: output prefix
```
sh canSNPextractor.sh feht/chromoI-cansnps.tsv chromoI
sh canSNPextractor.sh feht/chromoII-cansnps.tsv chromoII
```
## kmerDesigner.sh
- arg1: input
- arg2: output prefix
- arg3: randomly selected positive genotypes per node of interest
- arg4: size of kmer sequences up and downstream of canSNPs
- arg5: chromosome GenBank identifier
- arg6: additional digit to position to merge schemes from different chromosomes
```
sh kmerDesigner.sh canSNPextractor/chromoI-genotypes-all-interest-canSNPs.tsv chromoI 4 16 AE014291.4 10000000
sh kmerDesigner.sh canSNPextractor/chromoII-genotypes-all-interest-canSNPs.tsv chromoII 4 16 AE014292.2 20000000
```
## merging of schenes from chromosomes I and II
```
cat kmerDesigner/chromoI-schema.db kmerDesigner/chromoII-schema.db > kmerDesigner/chromoI-II-schema.db
```
## hansel
- -s: input scheme
- --vv: verbosity level
- -t: threads
- -o: typing output
- -O: match output
- -D: input format
```
hansel -s kmerDesigner/chromoI-schema.db -vv -t 20 -o hansel/chromoI-results-fastq.tab -O hansel/chromoI-match_results-fastq.tab -D fastq
hansel -s kmerDesigner/chromoI-schema.db -vv -t 20 -o hansel/chromoI-results-fastq.tab -O hansel/chromoI-match_results-fastq.tab -D fastq
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
**AE014291	4219	T	C		C		C		C		T**
**AE014291	4223	G	C		C		C		C		G**
AE014291	4498	A	C		C		C		C		A
```
## Nucleotide profiles of SNPs for each chromosome excluding hotspots of SNPs (pointSNPselector/chromoI-snps-retained-sorted-header.tsv)
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
## canSNP scheme organized in the form of kmers (kmerDesigner/chromoI-schema.db)
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
# Acknowledgment
The GENPAT-IZSAM Staff for our discussions aiming at designing workflows
# Author
Nicolas Radomski
