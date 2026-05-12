#!/bin/bash
#SBATCH --mail-user=ssomalra@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --time=1-23:59:00
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name=dicom_to_nifti_conversion
#SBATCH -o dicom_to_nifti_conversion.out
#SBATCH -A r00270

module load dcm2niix

INPUT_ROOT="/N/scratch/ssomalra/BMEG_project_test/raw_ADNI_data"
OUTPUT_ROOT="/N/scratch/ssomalra/BMEG_project_test/nifti_files"

splits=("train" "test")
classes=("AD" "MCI" "CN")

for split in "${splits[@]}"; do
	for cls in "${classes[@]}"; do
		BASE_PATH="$INPUT_ROOT/$split/$cls"

		for patient in "$BASE_PATH"/*; do
			patient_id=$(basename "$patient")

			for visit in "$patient"/*; do
				visit_id=$(basename "$visit")
				
				for scan in "$visit"/*; do
					scan_name=$(basename "$scan")

					echo "Processing: $patient_id $visit_id $scan_name"
					OUT_DIR="$OUTPUT_ROOT/$split/$cls"
					dcm2niix -z y -b n -o "$OUT_DIR" -f "${patient_id}_${visit_id}_${scan_name}" "$scan"

				done
			done
		done
	done
done
