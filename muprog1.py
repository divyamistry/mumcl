#! /usr/bin/env python3

import sys
import re
from datetime import datetime
from textwrap import dedent
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# function that verifies each of the given .expr file has
# the correct matrix like structure.
def verifyFile(fileName):
    # expected format is as follows:
    # 
    # \tcolumn1Name\tcolumn2Name\tcolumn3Name\t...\tcolumnXName\n
    # row1Name\tvalue1\tvalue2\tvalue3\t...\tvalueX\n
    # row2Name\tvalue1\tvalue2\tvalue3\t...\tvalueX\n
    # ...
    # rowYName\tvalue1\tvalue2\tvalue3\t...\tvalueX\n
    #
    f = open(fileName,'r')
    # first title line processing
    if re.match("\s*?(?:\t\w+)+",f.readline()):
        # now process rest of the file
        for currLine in f:
            if not re.match('.+?(\t\d+\.\d+)+',currLine):
                f.close()
                return False
    else:
        f.close()
        return False
    # everything matched as needed. expression file is in correct format
    f.close()
    return True 

# function to merge files as needed. Uses mergeColumns as a helper function
def mergeFiles(args,outputFileName):
    exprFileNames=[]
    exprCols=[]
    for exprs in args:
        # get experiment name and columns
        bbexprNum = re.match("(.+\.expr)\:\[(.+)?\]",exprs)
        # keep list of all the files in order they are given
        exprFileNames.append(bbexprNum.group(1))
        # keep list of all the columns corresponding to given files
        exprCols.append(parseColumns(bbexprNum.group(2)))
    # we only want the row names to appear once, so we'll get those from
    # the first file's 0th column. I add that as the column index manually
    exprCols[0].insert(0,0)
    return mergeColumns(exprFileNames, exprCols, outputFileName)

# function that combines all the columns from each of the
# .expr files and creates a new file from it
def mergeColumns(fNames, colsList, outputFileName):
    fh = [] #list to hold all the file handlers.
    outf = open(outputFileName, 'w')
    #open all the files for reading
    for f in fNames:
        fh.append(open(f,'r'))
    #
    # read all the lines of files. All the files are assumed to have same 
    # number of lines. While this little code can optimized by reading the
    # first file here, and reading rest of them in the subroutine, to cleanly
    # separate the code, I am counting the lines here, and then reading all
    # files in subrouting. A little bit of overhead in the computation, but the
    # code looks much cleaner. Maybe the code can be split further to avoid this
    # overhead as well.
    #
    numberOfLines = sum(1 for line in fh[0])
    fh[0].seek(0) #reset the reading position in first file
    
    # now on to processing all lines
    while numberOfLines > 0: 
        # write the values in tab-separted format
        outf.write('\t'.join(getColumnsInList(fh,colsList))+'\n')
        numberOfLines -= 1
    #close all the opened files
    outf.close()
    for f in fh:
        f.close()

    #that's it!
    return True

# function to pick correct columns for given line and return them
def getColumnsInList(fh,colsList):
    # for each of the input file, get corresponding columns for new file
    outputLine = []
    for f in range(0,len(fh)):
        currLine = fh[f].readline().rstrip()
        splotLine = re.split('\t', currLine)
        for g in colsList[f]:
            outputLine.append(splotLine[g])
    return outputLine


# function to parse given text (from command line) into a list
# of numbers corresponding to columns of expression.
# The column number will start from "1", not "0". Zero-th column
# is the gene names, and I'd like to keep it that way.
def parseColumns(colText):
    # get all the user provided columns and column ranges
    colListStr = re.split(',', colText)
    li=[]
    for col in colListStr:
        # if extended range is provided, expand the range and add to the list
        colSplot = re.match('(\d+):(\d+):(\d+)',col)
        if colSplot:
            li.extend(range(int(colSplot.group(1)),int(colSplot.group(2))+1,int(colSplot.group(3))))
        else:
          # if any ranges are provided, expand the range and add to the list
          colSplot = re.match('(\d+):(\d+)',col)
          if colSplot:
              li.extend(range(int(colSplot.group(1)),int(colSplot.group(2))+1))
          else:
              li.append(int(col))

        # and that's it for now!
        li = sorted(li)
    return li


# function to check whether given files are in correct matrix format
# that can be read and column referenced later.
def doFileCheck(args):
    #variable to track if any of the experiment files were unverified
    unverifiedFiles = False
    #for every expression file given, run verification 
    for exprs in args:
        #first matched group is the filename, second are the columns
        bbexprNum = re.match("(.+\.expr)\:\[.+?\]",exprs)
        #if command line had at least one file
        if(bbexprNum):
            #open the file and verify that it is in valid format
            print("verifying structure of", bbexprNum.group(1), "...", end="")
            if(verifyFile(bbexprNum.group(1))):
                #get the columns
                print("verified")
            else:
                print("unverified")
                unverifiedFiles = True
        else:
            print("Error parsing .expr (expression file) input criteria.\
                   Please refer to help.")
            sys.exit(1)
        
    # at this point, if there were unverified files, suggest user to fix the issue
    if(unverifiedFiles):
        print("There were unverified files. Please fix the files and try again.")
        sys.exit(1)

# END OF METHOD DEFINTIONS

# BEGIN MAIN PROGRAM
# parse the cla for all the .expr files, columns, output files, and file check verification flag
parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, 
                        description="IMPORTANT: all the .expr files MUST have column title row as first row, and row names as first column. The column and row title columns will be automatically included in the output file.",
                        epilog=dedent('''\
                        NOTE: How to provide input files? 
                        General format: FileName:[<column_number_1>,<column_number_2>,...]
                        To provide a range of columns, you can use [<start_column_number>:<stop_column_number>]
                        Example:
                        - to combine (columns 1,3 of file1.expr) and (columns 9,20,21,22 of file2.expr)
                          # muprog1.py -i file1.expr:[1,3] file2.expr:[9,20:22] ...'''))
parser.add_argument("-i", "--infiles", dest="exprfile", nargs="+", required=True, help=".expr files and columns to combine. See NOTE below.")
parser.add_argument("-o", "--outfile", dest="outputfile", required=True, help="file where output will be written. If the file already exists, the file will be overwritten")
parser.add_argument("-s", "--sortinput", action="store_true", dest="filesunsorted", help="sort the probeset names before combining files", default=False)
parser.add_argument("-f", "--filecheck", action="store_true", default=False, dest="filecheck", help="perform expression file verification before processing files to make sure files are formatted correctly for this program.")
args = parser.parse_args()

# if expression files had probesets in different order in different files
# then the rows of the expression files need to be ordered before they
# can be correctly combined
if(args.filesunsorted):
    print('Sorting feature is unimplemented. Please sort files manually outside this program.')
    print('You may use the following commands to sort your file:')
    print('$\thead -n 1 yourfile.expr > sortedfile.expr')
    print('$\ttail -n +2 yourfile.expr | sort >> sortedfile.expr')
    sys.exit(1)

# if file format check requested, perform the check before going further.
if(args.filecheck):
    doFileCheck(args.exprfile)

# now merge all the requested columns from various files
# and output the result to given filename.
mergeFiles(args.exprfile, args.outputfile)
t=datetime.now()
print("Done at ", t.year,'-',t.month,'-',t.day,' ',t.hour,':',t.minute,':',t.second,sep='')

