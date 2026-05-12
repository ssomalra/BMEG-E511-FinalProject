import ants
from pathlib import Path
from collections import defaultdict
import gc

input_dir = Path("/N/scratch/ssomalra/BMEG_project/nifti_files/train")
output_dir = Path("/N/scratch/ssomalra/BMEG_project/registered_nifti_files/train")

transform_type = "Affine"

# group .nii.gz scans by (diagnosis, subjectID_visit) to collect repeated scans per visit
def group_scans(input_dir):
    groups = defaultdict(list)

    for path in input_dir.rglob("*.nii.gz"):
        # extract diagnosis (AD, MCI, CN)
        diagnosis = path.parent.name

        # get file name by removing .nii.gz from file
        name = path.name
        stem = name.replace(".nii.gz", "") if name.endswith(".nii.gz") else path.stem

        # extract subjectID_visit
        parts = stem.split("_")
        subject_visit = "_".join(parts[:4])

        key = (diagnosis, subject_visit)
        groups[key].append(path)

    return groups

groups = group_scans(input_dir)

# run N4 bias correction and intra-patient registration
for (diagnosis, subject_visit), scan_paths in groups.items():
    scan_paths = sorted(scan_paths)

    print(f"\nProcessing {diagnosis}/{subject_visit}")
    print(f"Found {len(scan_paths)} scan(s)")

    # always run N4 bias correction on the first scan
    fixed_raw = ants.image_read(str(scan_paths[0]))
    fixed = ants.n4_bias_field_correction(fixed_raw)

    aligned = [fixed]

    # if there are repeated scans, then run N4 bias correction on repeated scans and register them to the first scan
    for moving_path in scan_paths[1:]:
        print(f"  Registering {moving_path.name}")

        moving_raw = ants.image_read(str(moving_path))
        moving = ants.n4_bias_field_correction(moving_raw)

        # ANTs registration
        reg = ants.registration(fixed=fixed, moving=moving, type_of_transform=transform_type, singleprecision=True)

        aligned.append(reg["warpedmovout"])

        del moving_raw, moving, reg
        gc.collect()

    # if there's only 1 scan, below code just saves the N4-corrected image
    # if there are 2+ scans, below code averages the aligned scans to get a single representative scan for the patient visit
    print(f"Aligning {diagnosis}/{subject_visit} Images")
    avg = ants.average_images(aligned, normalize=False)

    diagnosis_output_dir = output_dir / diagnosis

    output_path = diagnosis_output_dir / f"{subject_visit}_avg.nii.gz"
    ants.image_write(avg, str(output_path))

    print(f"Saved: {output_path}")

    # to free memory
    del fixed_raw, fixed, aligned, avg
    gc.collect()
