#!/bin/bash
#SBATCH --mail-user=ssomalra@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --mem=64gb
#SBATCH --time=3-00:00:00
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name=test_N4-Registration
#SBATCH -o N4-Registration_test.out
#SBATCH -A r00270

module load conda
conda activate antspyx

python N4-Registration_test.py

