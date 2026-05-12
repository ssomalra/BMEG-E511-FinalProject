#!/bin/bash
#SBATCH --mail-user=ssomalra@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --mem=64gb
#SBATCH --time=2-00:00:00
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name=skull_stripping
#SBATCH -o skull_stripping.out
#SBATCH -A r00270

module load freesurfer

INPUT_BASE="/N/scratch/ssomalra/BMEG_project/registered_nifti_files"
OUTPUT_BASE="/N/scratch/ssomalra/BMEG_project/skull_stripped_files"

for SPLIT in train test; do
	for DIAG in AD MCI CN; do
	INPUT_DIR="${INPUT_BASE}/${SPLIT}/${DIAG}"
	OUTPUT_DIR="${OUTPUT_BASE}/${SPLIT}/${DIAG}"

		for FILE in "${INPUT_DIR}"/*_avg.nii.gz; do
			BASENAME=$(basename "$FILE" .nii.gz)
			OUTPUT_FILE="${OUTPUT_DIR}/${BASENAME/_avg/_skull_stripped}.nii.gz"

			echo "Processing $FILE"
			mri_synthstrip -i "$FILE" -o "$OUTPUT_FILE"

		done
  	done
done

