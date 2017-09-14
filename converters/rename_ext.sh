#!/usr/bin/env bash

for f in $1/*.gr; do
    mv "$f" "$(dirname "$f")/$(basename "$f" .gml.gr).gr"
    #mv "$f" "$(dirname "$f")/$(basename "$f" .gml.lp.bz2.gr).gr"
    #mv "$f" "$(dirname "$f")/$(basename "$f" .gf).gr"
done
