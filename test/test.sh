#!/bin/bash
set -euo pipefail

set -x

ORI=ori.xml
TESTURL='https://www.nasdaq.com/feed/rssoutbound?category=Cryptocurrencies'
#TESTURL='https://www.ncdc.noaa.gov/cag/global/time-series/globe/land_ocean/1/9/1880-2019/data.xml'

curl -o $ORI $TESTURL

for OUTER in xml json yaml ; do
    python3 ../manyio.py $ORI to${OUTER}.${OUTER}
    for INNER in xml json yaml ; do
        python3 ../manyio.py to${OUTER}.${OUTER} to${OUTER}to${INNER}.${INNER}
    done
done

echo "Same file endings should be the same size"

ls -l * | grep -v ori.xml | grep -v test.sh | sort -k 5

for OUTER in xml json yaml ; do
    for INNER in xml json yaml ; do
        cmp to${OUTER}.${OUTER} to${INNER}to${OUTER}.${OUTER}
    done
done

