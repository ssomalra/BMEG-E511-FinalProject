import pandas as pd
import argparse
import os

def compute_ai(left, right):
    """Asymmetry Index: |L - R| / (L + R) * 100"""
    return (abs(left - right) / (left + right)) * 100

def main(input_path, output_path):
    df = pd.read_csv(input_path)

    # ── Column pairs ──────────────────────────────────────────────────
    wm_left  = ['left cerebral white matter',  'left cerebellum white matter']
    wm_right = ['right cerebral white matter', 'right cerebellum white matter']

    gm_left  = ['left cerebral cortex',  'left cerebellum cortex',
                'left hippocampus',      'left amygdala']
    gm_right = ['right cerebral cortex', 'right cerebellum cortex',
                'right hippocampus',     'right amygdala']

    all_left  = wm_left  + gm_left
    all_right = wm_right + gm_right

    # ── Compute AIs ───────────────────────────────────────────────────
    out = pd.DataFrame()
    out['subject']         = df['subject']
    out['group']           = df['group']
    out['AI_global']       = compute_ai(df[all_left].sum(axis=1),  df[all_right].sum(axis=1))
    out['AI_white_matter'] = compute_ai(df[wm_left].sum(axis=1),   df[wm_right].sum(axis=1))
    out['AI_grey_matter']  = compute_ai(df[gm_left].sum(axis=1),   df[gm_right].sum(axis=1))

    # ── Save ──────────────────────────────────────────────────────────
    out.to_csv(output_path, index=False)
    print(f"Saved {len(out)} rows to: {output_path}")
    print(out.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute hemispheric Asymmetry Index (AI)")
    parser.add_argument("--input",  default="/N/scratch/ssomalra/BMEG_project/synthseg/analysis/test_all_classes_merged.csv",
                        help="Path to input CSV")
    parser.add_argument("--output", default="/N/scratch/ssomalra/BMEG_project/synthseg/analysis/test_AI.csv",
                        help="Path for output CSV")
    args = parser.parse_args()
    main(args.input, args.output)
