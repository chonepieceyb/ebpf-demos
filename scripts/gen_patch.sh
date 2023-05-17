#!/bin/bash 

# ./gen_patch.sh patch_dir [git-format path parameters]

source $(cd "$(dirname "$0")"; pwd)"/"common.sh 

if [ $# -lt 1 ]
then 
    echo "usage: ./gen_patch.sh patch_dir [git-format path parameters]" 
    exit -1
fi 

PATCH_PATH=$PATCH_DIR$1

rm -rf $PATCH_PATH

cd $PROJECT_DIR"/"$LINUX

shift

args=('-o' $PATCH_PATH $@) 

git format-patch ${args[@]}

