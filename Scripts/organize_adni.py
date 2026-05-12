import pandas as pd
import os
import glob

# --- Settings ---
EXCEL_FILE = 'Data_Final.xlsx'
BASE_DIR = '/N/scratch/ssomalra/BMEG_project'
SOURCE_DIR = os.path.join(BASE_DIR, 'ADNI')
TARGET_DIR = os.path.join(BASE_DIR, 'organized_samples')

def run_organization():
    print(f"Loading {EXCEL_FILE}...")
    try:
        # Load the sheet
        df = pd.read_excel(os.path.join(BASE_DIR, EXCEL_FILE))
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # Create main output folder
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    count = 0
    missing = 0

    for _, row in df.iterrows():
        # Get data from columns
        sub = str(row['Subject']).strip()
        img_id = str(row['Image Data ID']).strip()
        dx_group = str(row['Group']).strip() # CN, MCI, or AD
        visit = str(row['Visit']).strip().replace(" ", "_")
        desc = str(row['Description']).strip().replace(" ", "_").replace("/", "-")

        # Define the target path: organized_samples/Group/Subject/Visit
        # Example: organized_samples/AD/002_S_0413/sc/
        folder_path = os.path.join(TARGET_DIR, dx_group, sub, visit)
        os.makedirs(folder_path, exist_ok=True)

        # Search for that Image ID folder in the raw ADNI tree
        search_pattern = os.path.join(SOURCE_DIR, sub, "**", img_id)
        found_folders = glob.glob(search_pattern, recursive=True)

        if found_folders:
            src = os.path.abspath(found_folders[0])
            # descriptive link name inside the visit folder
            dst = os.path.join(folder_path, f"{desc}_{img_id}")
            
            if not os.path.exists(dst):
                try:
                    os.symlink(src, dst)
                    count += 1
                except Exception as e:
                    print(f"Link error for {img_id}: {e}")
        else:
            missing += 1

    print("-" * 30)
    print(f"Organization Complete!")
    print(f"Scans successfully linked: {count}")
    print(f"Scans not found in ADNI folder: {missing}")
    print(f"Your data is ready in: {TARGET_DIR}")

if __name__ == "__main__":
    run_organization()
