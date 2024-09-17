#### design kmers from a list of randomly selected positive and negative genotypes of canSNPs and add to SNP positions a digit related to chromosome number 
#### USAGE: kmerDesigner.sh input_path output_prefix positive_genotype_per_node chromosome_GenBank_ID up_downstream_bases additional_digit
#### ex: sh kmerDesigner.sh canSNPextractor/chromoI-genotypes-all-interest-canSNPs.tsv chromoI 4 16 AE014291.4 10000000

# make an output dictionary
mkdir kmerDesigner

# retrieve information to build a kmers schema
## retrieve positive genotypes (PG) of each first group of interest
cat $1 | sed -e '1d' | tr '\t' ',' | awk -F, '$1!="2"' | grep -v 'not' | tr ',' '\t' > kmerDesigner/$2-positive-genotypes-all-interest-canSNPs.tsv
## select randomly positions of positive genotypes (PG) of each first group of interest
random=$3
for PG in `cat kmerDesigner/$2-positive-genotypes-all-interest-canSNPs.tsv | cut -f1 | uniq`
do
 cat kmerDesigner/$2-positive-genotypes-all-interest-canSNPs.tsv | tr '\t' ',' | awk -v var=$PG -F, '$1==var' | shuf -n "$random" | tr ',' '\t' > kmerDesigner/$2-positive-genotypes-${PG}-random.tsv
done
## combine and add header
cat kmerDesigner/$2-positive-genotypes-*-random.tsv | tr '\t' ',' | sort -t ',' -k1,1 -k2,2n | sed '1i Genotype,SNP Location,Positive Base,Negative Base' | tr ',' '\t' > kmerDesigner/$2-positive-genotypes-random.tsv
## add information required to prepare wget commands
### add a kmer numbers
grep -v 'Genotype' kmerDesigner/$2-positive-genotypes-random.tsv | tr '\t' ',' | nl -nln -s, -w1 > kmerDesigner/$2-positive-genotypes-random-modif1.csv
### calculate positions of upstream 5
bases=$4
awk -v var=$bases -F ',' '{print $3-var}' kmerDesigner/$2-positive-genotypes-random-modif1.csv > kmerDesigner/$2-positive-genotypes-random-upstream-5.lst
### calculate positions of upstream 3
awk -F ',' '{print $3-1}' kmerDesigner/$2-positive-genotypes-random-modif1.csv > kmerDesigner/$2-positive-genotypes-random-upstream-3.lst
### calculate positions of downstream 5
awk -F ',' '{print $3+1}' kmerDesigner/$2-positive-genotypes-random-modif1.csv > kmerDesigner/$2-positive-genotypes-random-downstream-5.lst
### calculate positions of downstream 3
awk -v var=$bases -F ',' '{print $3+var}' kmerDesigner/$2-positive-genotypes-random-modif1.csv > kmerDesigner/$2-positive-genotypes-random-downstream-3.lst
### add positions
paste -d "," \
	kmerDesigner/$2-positive-genotypes-random-modif1.csv \
	kmerDesigner/$2-positive-genotypes-random-upstream-5.lst \
	kmerDesigner/$2-positive-genotypes-random-upstream-3.lst \
	kmerDesigner/$2-positive-genotypes-random-downstream-5.lst \
	kmerDesigner/$2-positive-genotypes-random-downstream-3.lst \
	| sed '1i kmer,Genotype,SNP Location,Positive Base,Negative Base,Upstream-5,Upstream-3,Downstream-5,Downstream-3' \
	| tr ',' '\t' \
	> kmerDesigner/$2-positive-genotypes-random-modif2.tsv
## remove potential old downloaded kmer files
rm kmerDesigner/$2-kmer-*.upstream.fasta
rm kmerDesigner/$2-kmer-*.downstream.fasta
## download kmers
### prepare string variables
wget='wget "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id='
wgetCHR=$5
wgetSTART='&seq_start='
wgetSTOP='&seq_stop='
folder='&rettype=fasta" -O kmerDesigner/'
prefix=$2
name='-kmer-'
upstream='.upstream.fasta'
downstream='.downstream.fasta'
### build and run wget commands for upstream kmers
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-modif2.tsv \
	| awk -v v="${wget}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${wgetCHR}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${wgetSTART}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${wgetSTOP}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${folder}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${prefix}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${name}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${upstream}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${downstream}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -F '\t' -v OFS='\t' '{print $10,$11,$12,$6,$13,$7,$14,$15,$16,$1,$17}' \
	| tr '\t' ',' \
	| sed 's@,@@'g \
	> kmerDesigner/$2-cmd-upstream.sh
### run sh
sh kmerDesigner/$2-cmd-upstream.sh
### build and run wget commands for downstream kmers
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-modif2.tsv \
	| awk -v v="${wget}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${wgetCHR}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${wgetSTART}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${wgetSTOP}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${folder}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${prefix}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${name}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${upstream}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -v v="${downstream}" -F '\t' -v OFS='\t' '{ $(NF+1) = v; print }' \
	| awk -F '\t' -v OFS='\t' '{print $10,$11,$12,$8,$13,$9,$14,$15,$16,$1,$18}' \
	| tr '\t' ',' \
	| sed 's@,@@'g \
	> kmerDesigner/$2-cmd-downstream.sh
### run sh
sh kmerDesigner/$2-cmd-downstream.sh
### compile uptream bases
grep . kmerDesigner/$2-*.upstream.fasta | sed "s@kmerDesigner/$2-kmer-@@" | sed 's@.upstream.fasta@@' | tr ':' '\t' | grep -v '>' | sort -n -k 1 > kmerDesigner/$2-kmers.upstream.tsv
### compile downstream bases
grep . kmerDesigner/$2-*.downstream.fasta | sed "s@kmerDesigner/$2-kmer-@@" | sed 's@.downstream.fasta@@' | tr ':' '\t' | grep -v '>' | sort -n -k 1 > kmerDesigner/$2-kmers.downstream.tsv
### combine genotype informations and kmers
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-modif2.tsv > kmerDesigner/$2-positive-genotypes-random-modif3.tsv
join kmerDesigner/$2-positive-genotypes-random-modif3.tsv kmerDesigner/$2-kmers.upstream.tsv > kmerDesigner/$2-positive-genotypes-random-modif4.tsv
join kmerDesigner/$2-positive-genotypes-random-modif4.tsv kmerDesigner/$2-kmers.downstream.tsv \
	| sed 's@ @,@'g \
	| sed '1i kmer,Genotype,SNP Location,Positive Base,Negative Base,Upstream-5,Upstream-3,Downstream-5,Downstream-3,Upstream,Downstream' \
	| tr ',' '\t' \
	> kmerDesigner/$2-positive-genotypes-random-modif5.tsv
### add to SNP positions a digit related to chromosome number 
digit=$6
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-modif5.tsv | awk -v var=$digit -F'\t' -v OFS="\t" '{$3=$3+var}1' | sed '1i kmer,Genotype,SNP Location,Positive Base,Negative Base,Upstream-5,Upstream-3,Downstream-5,Downstream-3,Upstream,Downstream' | tr ',' '\t' > kmerDesigner/$2-positive-genotypes-random-info.tsv

# build a schema
## build a schema with "Positive Base"
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-info.tsv \
	| awk -F '\t' -v OFS='\t' '{print $3,$2,$10,$4,$11}' \
	| tr '\t' ',' \
	| sed 's@,@-@' \
	| sed 's@,@:@' \
	| sed 's@,@@' \
	| sed 's@,@@' \
	| sed -e 's@^@>@' \
	| tr ':' '\n' > kmerDesigner/$2-schema-positive.db
## build a schema with "Negative Base"
### for first node (i.e. genotype 2)
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-info.tsv \
	| tr '\t' ',' \
	| grep ',1,' \
	| sed 's@,1,@,2,@' \
	| tr ',' '\t' \
	| awk -F '\t' -v OFS='\t' '{print $3,$2,$10,$5,$11}' \
	| tr '\t' ',' \
	| sed 's@,@-@' \
	| sed 's@,@:@' \
	| sed 's@,@@' \
	| sed 's@,@@' \
	| sed -e 's@^@>@' \
	| tr ':' '\n' > kmerDesigner/$2-schema-first-node.db
### for intermediate nodes (i.e. other than genotypes 1 and 2)
grep -v 'kmer' kmerDesigner/$2-positive-genotypes-random-info.tsv \
	| tr '\t' ',' \
	| grep -v ',1,' \
	| tr ',' '\t' \
	| awk -F '\t' -v OFS='\t' '{print $3,$2,$10,$5,$11}' \
	| tr '\t' ',' \
	| sed 's@,@-@' \
	| sed 's@,@:@' \
	| sed 's@,@@' \
	| sed 's@,@@' \
	| sed -e 's@^@negative@' \
	| sed -e 's@^@>@' \
	| tr ':' '\n' > kmerDesigner/$2-schema-intermediate-nodes.db
### combine first and intermediate nodes
cat kmerDesigner/$2-schema-first-node.db kmerDesigner/$2-schema-intermediate-nodes.db > kmerDesigner/$2-schema-negative.db
## build schema with "Positive Base" and "Negative Base"
cat kmerDesigner/$2-schema-positive.db kmerDesigner/$2-schema-negative.db > kmerDesigner/$2-schema.db

# remove intermadiate files
rm kmerDesigner/*-cmd-*.sh
rm kmerDesigner/*-positive-genotypes-random-modif*
rm kmerDesigner/*-schema-*.db
rm kmerDesigner/*.lst
rm kmerDesigner/*-positive-genotypes-*-random.tsv
rm kmerDesigner/*.upstream.tsv
rm kmerDesigner/*.downstream.tsv
rm kmerDesigner/*.fasta

# print final messages
echo "The results are ready"
echo "Please, site GitHub (https://github.com/Nicolas-Radomski/canSNPtyping) and/or Docker Hub (https://hub.docker.com/r/nicolasradomski/dispersedsnpselector)"
