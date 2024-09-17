#### discard SNP hotspots
#### USAGE: dispersedSNPselector.sh input_path output_prefix chromosome_size bases_updown
#### ex: sh dispersedSNPselector.sh snippy/chromoI.tab chromoI 2107794 16

# make an output dictionary
mkdir dispersedSNPselector

# modify snippy tab file
cut --complement -f1,3 $1 | tr '\t' ',' | sed 's@POS,@,@' | tr ',' '\t' > dispersedSNPselector/$2-snps.tsv

# identify SNPs away from n bases upstream and downstream (i.e. (kmers length -1)/2)
## extract all SNPs positions
cat dispersedSNPselector/$2-snps.tsv | tail -n +2 | cut -f 1 | sort -n | uniq > dispersedSNPselector/$2-positions.lst
## calculate differences with uptream SNPs
### retrieve all positions excluding the first one and adding position of the last one
#### calculate the last position
chromosome=$3
first=$(head -n 1 dispersedSNPselector/$2-positions.lst)
addlast=$(echo "$chromosome+$first" | bc )
#### exclude the first one and add position of the last one
tail -n +2 dispersedSNPselector/$2-positions.lst | sed '$a '$addlast'' > dispersedSNPselector/$2-positions-upstream.lst
## calculate differences with downstream SNPs
### retrieve all positions excluding the last one and adding position of the first one
#### calculate the first position
last=$(tail -n 1 dispersedSNPselector/$2-positions.lst)
addfirst=$(echo "($chromosome-$last)*(-1)" | bc)
#### exclude the last one and add position of the first one
head -n -1 dispersedSNPselector/$2-positions.lst | sed '1i '$addfirst'' > dispersedSNPselector/$2-positions-downstream.lst
## combine compared positions
paste dispersedSNPselector/$2-positions.lst dispersedSNPselector/$2-positions-upstream.lst dispersedSNPselector/$2-positions-downstream.lst > dispersedSNPselector/$2-positions.tsv
## calculate differences
awk -F'\t' -v OFS="\t" '{$4=$2-$1}1' dispersedSNPselector/$2-positions.tsv > dispersedSNPselector/$2-differences-upstream.tsv
awk -F'\t' -v OFS="\t" '{$5=$1-$3}1' dispersedSNPselector/$2-differences-upstream.tsv > dispersedSNPselector/$2-differences-upstream-downstream.tsv
## extract positions with up and downstream differences higher than n or equal (i.e. (kmers length -1)/2)
bases=$4
cat dispersedSNPselector/$2-differences-upstream-downstream.tsv | awk -v var=$bases -F'\t' '$4>var' | awk -v var=$bases -F'\t' '$5>var' | cut -f1 > dispersedSNPselector/$2-retained-positions.lst

# remove SNPs less than n bases away from first and last nucleotides of the chromosome
end=$(echo "$chromosome-$bases" | bc )
cat dispersedSNPselector/$2-retained-positions.lst | awk -v var=$bases -F'\t' '$1>var'  | awk -v var=$end -F'\t' '$1<var'  > dispersedSNPselector/$2-retained-positions-trimmed.lst

# extract retained SNPs
## joint snp profiles and retained SNPs
cat dispersedSNPselector/$2-retained-positions-trimmed.lst | sort -k 1b,1 > dispersedSNPselector/$2-retained-positions-trimmed-sorted.lst
cat dispersedSNPselector/$2-snps.tsv | sed '1d' | sort -k 1b,1 > dispersedSNPselector/$2-snps-sorted.tsv
join -t "$(printf '\t')" -1 1 -2 1 \
    dispersedSNPselector/$2-retained-positions-trimmed-sorted.lst \
    dispersedSNPselector/$2-snps-sorted.tsv \
    -a 1 > dispersedSNPselector/$2-snps-retained.tsv
cat dispersedSNPselector/$2-snps-retained.tsv | sort -n > dispersedSNPselector/$2-snps-retained-sorted.tsv
## add header
sed -n 1p dispersedSNPselector/$2-snps.tsv > dispersedSNPselector/$2-header-snps.tsv
cat dispersedSNPselector/$2-header-snps.tsv dispersedSNPselector/$2-snps-retained-sorted.tsv > dispersedSNPselector/$2-snps-retained-sorted-header.tsv

# rename output
cat dispersedSNPselector/$2-differences-upstream-downstream.tsv | tr '\t' ',' | sed '1i POS,UP,DOWN,diff_UP,diff_DOWN' | tr ',' '\t' > dispersedSNPselector/$2-SNPs-retained.tsv
cat dispersedSNPselector/$2-retained-positions-trimmed-sorted.lst | sort -n | sed '1i POS' > dispersedSNPselector/$2-SNPs-retained-trimmed.tsv
mv dispersedSNPselector/$2-snps-retained-sorted-header.tsv dispersedSNPselector/$2-SNPs-retained-trimmed-profiles.tsv

# remove intermadiate files
rm dispersedSNPselector/$2-*-upstream.tsv
rm dispersedSNPselector/$2-*-downstream.tsv
rm dispersedSNPselector/$2-header-snps.tsv
rm dispersedSNPselector/$2-*-positions.lst
rm dispersedSNPselector/$2-positions.lst
rm dispersedSNPselector/$2-positions.tsv
rm dispersedSNPselector/$2-*-upstream.lst
rm dispersedSNPselector/$2-*-downstream.lst
rm dispersedSNPselector/$2-*-trimmed.lst
rm dispersedSNPselector/$2-*-trimmed-sorted.lst
rm dispersedSNPselector/$2-snps.tsv
rm dispersedSNPselector/$2-snps-retained.tsv
rm dispersedSNPselector/$2-*-retained-sorted.tsv
rm dispersedSNPselector/$2-snps-sorted.tsv

# print final messages
echo "The results are ready"
echo "Please, site GitHub (https://github.com/Nicolas-Radomski/canSNPtyping) and/or Docker Hub (https://hub.docker.com/r/nicolasradomski/dispersedsnpselector)"
