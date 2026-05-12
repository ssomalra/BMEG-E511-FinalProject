#!/bin/bash
#SBATCH --mail-user=vgutta@iu.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --job-name=synthseg_full
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16gb
#SBATCH --time=04:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH -A c02024
#SBATCH -o /N/scratch/ssomalra/BMEG_project/synthseg/logs/synthseg_full_%A_%a.out
#SBATCH -e /N/scratch/ssomalra/BMEG_project/synthseg/logs/synthseg_full_%A_%a.err
#SBATCH --array=1-99

set -eo pipefail

export FREESURFER_HOME=/N/soft/rhel8/freesurfer/8.1.0-1
set +e
source $FREESURFER_HOME/SetUpFreeSurfer.sh
set -e

LIST="/N/scratch/ssomalra/BMEG_project/synthseg/samples_list.txt"
INPUT=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LIST")

if [ -z "$INPUT" ]; then
  echo "No input for task ${SLURM_ARRAY_TASK_ID}"
  exit 1
fi

REL=${INPUT#/N/scratch/ssomalra/BMEG_project/skull_stripped_files/}
SPLIT=$(echo "$REL" | cut -d/ -f1)
GROUP=$(echo "$REL" | cut -d/ -f2)

OUT_DIR="/N/scratch/ssomalra/BMEG_project/synthseg/outputs/full/${SPLIT}/${GROUP}"
mkdir -p "$OUT_DIR"

BASE=$(basename "$INPUT" .nii.gz)

echo "TASK=${SLURM_ARRAY_TASK_ID}"
echo "INPUT=$INPUT"
echo "OUT=$OUT_DIR"
echo "DATE=$(date)"
which mri_synthseg

mri_synthseg \
  --i "$INPUT" \
  --o "$OUT_DIR/${BASE}_synthseg.nii.gz" \
  --vol "$OUT_DIR/${BASE}_volumes.csv"

echo "Done: $(date)"
