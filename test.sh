#!/bin/bash

THIS_DIR=$(cd $(dirname ${BASH_SOURCE}) && pwd)
source $THIS_DIR/lib_profiler.sh

echo ">> Without database"
_DB_SET=()
for _NEXT in {1..50}; do
    printf "%0*d:\t" 3 ${_NEXT}
    _STR=$(python3 ./wfaker.py -c)
    cpu_check_time "$_STR (${#_STR})"
    _DB_SET+=(${_STR})
done
_DB_SET_B58=()
for _NEXT in {1..50}; do
    printf "%0*d:\t" 3 ${_NEXT}
    _STR=$(python3 ./wfaker.py -cr)
    cpu_check_time "$_STR (${#_STR})"
    _DB_SET_B58+=(${_STR})
done


_DB_PATH=$(mktemp -t XXXXXXXX.faker.db)
echo ">> ${_DB_PATH}"
for _NEXT in {1..50}; do
    printf "%0*d:\t" 3 ${_NEXT}
    _STR=$(python3 ./wfaker.py -cd ${_DB_PATH})
    cpu_check_time "$_STR (${#_STR})"
    _DB_SET+=(${_STR})
done
for _NEXT in {1..50}; do
    printf "%0*d:\t" 3 ${_NEXT}
    _STR=$(python3 ./wfaker.py -crd ${_DB_PATH})
    cpu_check_time "$_STR (${#_STR})"
    _DB_SET_B58+=(${_STR})
done

_IDX=0
for _STR in "${_DB_SET[@]}"; do
    _IDX=$((_IDX+1))
    printf "%0*d:\t" 3 ${_IDX}
    python3 ./wfaker.py -t "${_STR}" -d ${_DB_PATH}
    cpu_check_time
done
_IDX=0
for _STR in "${_DB_SET_B58[@]}"; do
    _IDX=$((_IDX+1))
    printf "%0*d:\t" 3 ${_IDX}
    python3 ./wfaker.py -rt "${_STR}" -d ${_DB_PATH}
    cpu_check_time
done
du -h ${_DB_PATH}
rm -f ${_DB_PATH}

