#### extract canSNPs from comparisons of interest and count them
#### USAGE: canSNPextractor.sh input_path output_prefix
#### ex: sh canSNPextractor.sh feht/chromoI-cansnps.tsv chromoI

# make an output dictionary
mkdir canSNPextractor

# extract canSNPs from all comparisons
## split the tables
csplit -s -z $1 /#-/ '{*}' -f canSNPextractor/$2-cansnps- -n 2
## clean new tables
for f in canSNPextractor/$2-cansnps-*
do
 grep -v '#' "$f" | sed 's@---@@' | grep -v '^[[:space:]]*$' | sed 's@Group1 category: @@' | sed 's@Group2 category: @@' | sed ':a;N;$!ba;0,/\n/s//vs/' | sed 's@ @@'g | sed 's@\!@not@'g | grep -v 'Done' | sed 's@\(Level_[0-9][0-9]*Group[0-9][0-9]*:\)@@g' > "$f".new
done
## replace names of new tables
for f in canSNPextractor/$2-cansnps-*.new
do
 mv "$f" "canSNPextractor/$2-$(head -1 "$f").cansnps"
done
## remove intermadiate files
rm canSNPextractor/$2-cansnps-*

# retain canSNPs from comparisons of interest
## identify files corresponding to comparisons of interest
ls canSNPextractor/$2-* | grep -v 'NAvsnotNA' | grep '\-1vs2.\|vsnot' > canSNPextractor/$2-comparisons-interest.lst
## rename files corresponding to comparisons of interest
for path in `cat canSNPextractor/$2-comparisons-interest.lst`
do
 mv "$path" "$path.interest"
done
## trash files of disinterest
rm canSNPextractor/$2-*.cansnps

# count positions for each comparisons of interest
## binary and categorical SNPs (i.e. all positions duplicated and unique)
for f in canSNPextractor/$2-*.cansnps.interest
do
  echo "$f"
  sed -e '1,2d' "$f" | tr '_' '\t' | cut -f 1 | sort | uniq | wc -l
done > canSNPextractor/$2-canSNPs-count-all.txt
## categorical SNPs (i.e. only unique positions)
for f in canSNPextractor/$2-*.cansnps.interest
do
  echo "$f"
  sed -e '1,2d' "$f" | tr '_' '\t' | cut -f 1 | sort | uniq -u | wc -l
done > canSNPextractor/$2-canSNPs-count-categorical.txt
## binary SNPs (i.e. only duplicate positions)
for f in canSNPextractor/$2-*.cansnps.interest
do
  echo "$f"
  sed -e '1,2d' "$f" | tr '_' '\t' | cut -f 1 | sort | uniq -D | uniq | wc -l
done > canSNPextractor/$2-canSNPs-count-binary.txt

# combine canSNPs as lists for each comparisons of interest (Genotype, SNP Location, Positive Base, Negative Base)
## retrieve paths of files corresponding to comparisons of interest
sed -i s/$/.interest/ canSNPextractor/$2-comparisons-interest.lst
## list genotypes of the first group
for path in `cat canSNPextractor/$2-comparisons-interest.lst`
do
 export FG=`basename $path | sed "s@$2@@g" | sed "s@-@@g" | sed 's@.cansnps@@'g | sed 's@vs@-@'g | cut -f1 -d"-"`
 sed -e '1,2d' ${path} | tr '_' '\t' | tr '\t' ',' | awk -F, '$8=="1.0"' | tr ',' '\t' | cut -f1,2 | awk '$2 = toupper($2)' | tr ' ' '\t' | sort -k 1b,1 > canSNPextractor/$2-genotypes-first-group-${FG}.tsv
done
## list genotypes of the second group
for path in `cat canSNPextractor/$2-comparisons-interest.lst`
do
 export SG=`basename $path | sed "s@$2@@g" | sed "s@-@@g" | sed 's@.cansnps@@'g | sed 's@vs@-@'g | cut -f2 -d"-" | sed 's@.interest@@'g`
 sed -e '1,2d' ${path} | tr '_' '\t' | tr '\t' ',' | awk -F, '$8=="-1.0"' | tr ',' '\t' | cut -f1,2 | awk '$2 = toupper($2)' | tr ' ' '\t' | sort -k 1b,1 > canSNPextractor/$2-genotypes-second-group-${SG}.tsv
done
## join positive and negative genotypes for both first and second groups
for path in `cat canSNPextractor/$2-comparisons-interest.lst`
do
 export FG=`basename $path | sed "s@$2@@g" | sed "s@-@@g" | sed 's@.cansnps@@'g | sed 's@vs@-@'g | cut -f1 -d"-"`
 export SG=`basename $path | sed "s@$2@@g" | sed "s@-@@g" | sed 's@.cansnps@@'g | sed 's@vs@-@'g | cut -f2 -d"-" | sed 's@.interest@@'g`
 join canSNPextractor/$2-genotypes-first-group-${FG}.tsv canSNPextractor/$2-genotypes-second-group-${SG}.tsv | sed "s@^@${FG} @" | tr ' ' '\t' | sort -n -k 2 > canSNPextractor/$2-genotypes-${FG}-clean.tsv
 join canSNPextractor/$2-genotypes-second-group-${SG}.tsv canSNPextractor/$2-genotypes-first-group-${FG}.tsv | sed "s@^@${SG} @" | tr ' ' '\t' | sort -n -k 2 > canSNPextractor/$2-genotypes-${SG}-clean.tsv
done
## combine clean lists of genotypes
cat canSNPextractor/$2-genotypes-*-clean.tsv | tr '\t' ',' | sort -t ',' -k1,1 -k2,2n | sed '1i Genotype,SNP Location,Positive Base,Negative Base' | tr ',' '\t' > canSNPextractor/$2-genotypes-all-interest-canSNPs.tsv
## remove intermadiate files
rm canSNPextractor/$2-comparisons-interest.lst
rm canSNPextractor/$2-*.cansnps.interest
rm canSNPextractor/$2-genotypes-first-group-*
rm canSNPextractor/$2-genotypes-second-group-*
rm canSNPextractor/$2-*-clean.tsv

# print final messages
echo "The results are ready"
echo "Please, site GitHub (https://github.com/Nicolas-Radomski/canSNPtyping) and/or Docker Hub (https://hub.docker.com/r/nicolasradomski/dispersedsnpselector)"
