#!/usr/bin/env bash

trap 'ret=$?; printf "%s\n" "$ERR_MSG" >&2; exit "$ret"' ERR

for file in $(find $1 -name \*.lp.bz2) ; do
    echo $file
    outputname="../gr/subgraphs/$(basename $file).gr"
    ./lp2dgf.py -f $file > $outputname
    if [ $? -ne 0 ]; then
	echo 'ERROR stopping...'
	exit 1
    fi
done
