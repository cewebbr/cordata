#!/usr/bin/env bash
# To run on locaweb VPS.

# Hard-coded:
bkp_prefix=usecases_bkp_
bkp_suffix=.json
src=/home/admin/ceweb/projetos/cordata/codigo/data/usecases_temp.json
target=/home/admin/ceweb/projetos/cordata/dados/backups

# Get current date:
current_date=`date +'%Y-%m-%d'`

# Make the copy (backup):
echo "cp $src $target/$bkp_prefix$current_date$bkp_suffix"
cp $src $target/$bkp_prefix$current_date$bkp_suffix
