# mumcl
There are two programs here:
- `muprog1.py` is a python3 program that accepts PlexDB affymetrix RMA processed column files. It is used to selectively combine individual or range of columns together to create another tab-separated ouput file with those combined columns.

```
usage: muprog1.py [-h] -i EXPRFILE [EXPRFILE ...] -o OUTPUTFILE [-s] [-f]

IMPORTANT: all the .expr files MUST have column title row as first row, and row names as first column. The column and row title columns will be automatically included in the output file.

optional arguments:
  -h, --help            show this help message and exit
  -i EXPRFILE [EXPRFILE ...], --infiles EXPRFILE [EXPRFILE ...]
                        .expr files and columns to combine. See NOTE below.
  -o OUTPUTFILE, --outfile OUTPUTFILE
                        file where output will be written. If the file already
                        exists, the file will be overwritten
  -s, --sortinput       sort the probeset names before combining files
  -f, --filecheck       perform expression file verification before processing
                        files to make sure files are formatted correctly for
                        this program.

NOTE: How to provide input files?
General format: FileName:[<column_number_1>,<column_number_2>,...]
To provide a range of columns, you can use [<start_column_number>:<stop_column_number>]
Example:
- to combine (columns 1,3 of file1.expr) and (columns 9,20,21,22 of file2.expr)
  # muprog1.py -i file1.expr:[1,3] file2.expr:[9,20:22] ...
```

- `performMagic.sh` is a shell script that performs clustering using ![mcl](http://micans.org/mcl/) and provides reports on the stdout of current shell.
```
usage: performMagic.sh <expression file> <output file name> <tab file name> <correlation cutoff in (0,1] range>
```
