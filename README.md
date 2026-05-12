# MRI-Based Quantification of Hemispheric Asymmetry in Alzheimer’s Disease
This repository contains the code for the BMEG-E511 Biomedical Image Processing Final Project, titled '_MRI-Based Quantification of Hemispheric Asymmetry in Alzheimer’s Disease_'. In this project, T1-weighted MRI scans from the ADNI database were used to investigate whether MRI-derived hemispheric asymmetry indices could serve as interpretable imaging biomarkers for classifying Alzheimer’s disease progression.

<img width="1800" alt="SegmentedFigure_Panel" src="https://github.com/user-attachments/assets/50e4ecd2-732f-4abe-80a9-39939a93baec" />

*Representative axial and coronal MRI slices together with corresponding SynthSeg segmentation outputs and hemispheric asymmetry index measurements for CN, MCI, and AD subjects.*

## Dataset
The dataset used in this study consisted of whole-brain T1-weighted (T1W) Magnetic Resonance Imaging (MRI) scans downloaded from the Alzheimer’s Disease Neuroimaging Initiative (ADNI) database. A total of 209 MRI scans were obtained through the ADNI search interface. Participants were grouped into three diagnostic categories for analysis: cognitively normal (CN), mild cognitive impairment (MCI), and Alzheimer’s disease (AD). The dataset included 31 unique subjects consisting of 14 females and 17 males, ranging in age from 60 to 93 years. For this project, the unit of analysis was defined as a subject-visit sample, representing one processed scan per subject per visit.

## Project Contents
- `ADNI_Metadata.csv`: metadata corresponding to the raw MRI scans downloaded from the ADNI database, including subject and visit information.
- `SynthSeg_train_volumes.csv` and `SynthSeg_test_volumes.csv`: Region-wise volumetric summary tables for the training and test datasets containing estimated volumes for each segmented brain structure generated from the SynthSeg outputs.
- `Asymmetry_Scores_Train.csv` and `Asymmetry_Scores_Test.csv`: Contain the calculated hemispheric asymmetry scores for total matter, white matter, gray matter, hippocampus, and amygdala for the training and test datasets.
- **`Scripts`**:
  1. `organize_adni.py`: Organizes downloaded ADNI MRI data into diagnostic group folders (CN, MCI, AD) using subject metadata.
  2. `split_subjects.py`: Creates subject-level train/test splits stratified by diagnostic group to prevent data leakage.
  3. `dicom_to_nifti_conversion.sh`: Converts raw MRI scans from DICOM format to compressed NIfTI (.nii.gz) format
  4. `N4-Registration_train.py` and `N4-Registration_train.sh`: Perform N4 bias correction, affine registration, and scan averaging on the training MRI dataset. 
  5. `N4-Registration_test.py` and `N4-Registration_test.sh`: Apply N4 bias correction, affine registration, and scan averaging to the test MRI dataset.
  6. `skull_stripping.sh`: Performs skull stripping on preprocessed MRI scans using FreeSurfer’s mri_synthstrip.
  7. `synthseg_full.sh`: Runs SynthSeg on skull-stripped MRI scans to generate segmentation maps and region-wise volume CSV files.
  8. `AI_compute.py`:
  9. `AI_compute_assymetry_plot.py`:
  10. `AI_compute_assymetry_plot.py`:
  11. `asymmetry_index_kruskal_welch.py` and `assymetry_index_wilcox.py`:

> [!NOTE]
> **The raw MRI data, preprocessing outputs, and downstream analysis files are stored on the institutional high-performance computing (HPC) system at the following directory path: `/N/scratch/ssomalra/BMEG_project`**
- `Scripts`: Contains Python and shell scripts used for data organization, preprocessing, segmentation, asymmetry analysis, and statistical testing workflows
- `ADNI/`: Contains the original ADNI-downloaded MRI data organized by subject ID. Each subject folder contains T1-weighted acquisition folders such as MP-RAGE, MPRAGE, and repeat scans used as the source imaging data for preprocessing
- `data/`: Contains project metadata and organized sample information
  - `Data_Final.xlsx` stores subject and diagnostic information
  - `organized_samples/`separates subjects into AD, CN, and MCI folders before preprocessing
- `splits/`: Contains subject-level train/test split files used for analysis and machine learning. Includes train/test subject lists, split_summary.json, and train/ and test/ folders organized into AD, CN, and MCI subfolders to prevent data leakage across repeated scans or visits.
- `nifti_files/`: Contains MRI scans converted from DICOM format to compressed NIfTI (.nii.gz) format
- `registered_nifti_files/`: Contains N4 bias-corrected and affine-registered MRI scans used for downstream preprocessing and analysis.
- `skull_stripped_files/`: Contains skull-stripped MRI scans generated using FreeSurfer’s `mri_synthstrip.`
- `synthseg/`: Contains SynthSeg segmentation outputs, including segmentation maps, region-wise volumetric summary tables, merged analysis files, and downstream asymmetry analysis results.
- `asymmetry_scores/`: Contains calculated hemispheric asymmetry score files, statistical analysis outputs, and asymmetry visualization plots
