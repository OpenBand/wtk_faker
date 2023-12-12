#!/bin/bash

THIS_DIR=$(cd $(dirname ${BASH_SOURCE}) && pwd)
source $THIS_DIR/lib_profiler.sh

echo ">> Without database"
_DB_SET=()
for _NEXT in {1..50}; do
    printf "%0*d:\t" 2 ${_NEXT}
    _STR=$(python ./wfaker.py -c)
    cpu_check_time "$_STR (${#_STR})"
    _DB_SET+=(${_STR})
done

_DB_PATH=$(mktemp -t XXXXXXXX.faker.db)
echo ">> ${_DB_PATH}"
for _NEXT in {1..50}; do
    printf "%0*d:\t" 2 ${_NEXT}
    _STR=$(python ./wfaker.py -c -d ${_DB_PATH})
    cpu_check_time "$_STR (${#_STR})"
    _DB_SET+=(${_STR})
done

_IDX=0
for _STR in "${_DB_SET[@]}"; do
    _IDX=$((_IDX+1))
    printf "%0*d:\t" 2 ${_IDX}
    python ./wfaker.py -t "${_STR}" -d ${_DB_PATH}
    cpu_check_time
done
du -h ${_DB_PATH}
rm -f ${_DB_PATH}

