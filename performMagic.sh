#! /bin/bash

# make sure enough parameters are provided
if [ $# -lt 4 ]
then
	echo "not enough parameters provided. provided all the necessary values"
	echo "usage: performMagic.sh <expression file> <output file name> <tab file name> <correlation cutoff in (0,1] range>"
        exit 1;
fi

#make sure input file actually exists
if [ ! -f $1 ]
then
	echo "input expression file doesn't exist. provide a file I can use."
        exit 2;
fi

# number of cores on this machine
NUM_CORES=4

# if user asked for the LONG RUN with all the various inflations and distances
# run those, otherwise just run default ones.
LONG_RUN=0
if [ $LONG_RUN -gt 0 ]
then
  echo "Long run requested. This'll take a while. Go make some tea and take a nap."
fi

# step 1*: show a table of various correlation cutoff choices.
#         eventually I'd run this with low value of correlation
#         and parse the resulting table to pick a good cutoff value
#         and re-create a matrix with that good cutoff.
#echo "Preparing to show table from results of varying correlation values."
#mcxarray -t 2 -data $1 -skipr 1 -skipc 1 -o $2 -write-tab $3 --spearman -co $4 -tf "abs()"
#mcx query -imx $2 --vary-correlation

# step 1: use mcxarray to get the native matrix format
if [ -f $2 ]
then
  echo "Given output file already exists. I'll be using that!"
  echo "Give a different output name or rename the old one if you want to do this analysis from scratch."
else
  echo "Starting mcxarray to prepare network matrix"
  mcxarray -t $NUM_CORES -data $1 -skipr 1 -skipc 1 -o $2 -write-tab $3 --spearman -co $4 -tf "abs(),add(-$4)"
fi

# step 2: perform clustering with various inflation
echo "Starting clustering using mcl" 
mcl $2 -I 1.8 -te $NUM_CORES #default run with inflation 1.8
if [ $LONG_RUN -gt 0 ]
then
  mcl $2 -I 1.4 -use-tab $3 -te $NUM_CORES 
  mcl $2 -I 1.6 -use-tab $3 -te $NUM_CORES 
  mcl $2 -I 1.9 -use-tab $3 -te $NUM_CORES 
  mcl $2 -I 2.0 -use-tab $3 -te $NUM_CORES 
  mcl $2 -I 2.4 -use-tab $3 -te $NUM_CORES 
  mcl $2 -I 4.0 -use-tab $3 -te $NUM_CORES 
fi

# step 3: collect the results into readable format
echo "Starting to collect the results into readable format"
mcxdump -icl out.$2.I18 -tabr $3 -o dump.$2.I18 #default run
if [ $LONG_RUN -gt 0 ]
then
  mcxdump -icl out.$2.I14 -tabr $3 -o dump.$2.I14
  mcxdump -icl out.$2.I16 -tabr $3 -o dump.$2.I16
  mcxdump -icl out.$2.I19 -tabr $3 -o dump.$2.I19
  mcxdump -icl out.$2.I20 -tabr $3 -o dump.$2.I20
  mcxdump -icl out.$2.I24 -tabr $3 -o dump.$2.I24
  mcxdump -icl out.$2.I40 -tabr $3 -o dump.$2.I40
fi

# step 4: gauge distance between various clustering results
if [ $LONG_RUN -gt 0 ]
then
  echo "Starting to gauge distance between various clustering results"
  clm dist --chain --sort -o clmdist.$2.out -mode sj out.$2.I{14,16,18,19,20,24,40}
fi
