import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import wilcoxon, kruskal
import itertools

# ── Hardcoded Paths ───────────────────────────────────────────────────────────

TRAIN_INPUT = "/N/scratch/ssomalra/BMEG_project/synthseg/analysis/train_all_classes_merged.csv"
TRAIN_AI    = "/N/scratch/ssomalra/BMEG_project/synthseg/analysis/train_hippo_amyg_AI.csv"
TRAIN_PLOT  = "/N/scratch/ssomalra/BMEG_project/synthseg/analysis/train_hippo_amyg_AI_boxplot.png"

TEST_INPUT  = "/N/scratch/ssomalra/BMEG_project/synthseg/analysis/test_all_classes_merged.csv"
TEST_AI     = "/N/scratch/ssomalra/BMEG_project/synthseg/analysis/test_hippo_amyg_AI.csv"
TEST_PLOT   = "/N/scratch/ssomalra/BMEG_project/synthseg/analysis/test_hippo_amyg_AI_boxplot.png"

# ── Region Pairs ──────────────────────────────────────────────────────────────

REGION_PAIRS = {
    'AI_hippocampus': ('left hippocampus', 'right hippocampus'),
    'AI_amygdala':    ('left amygdala',    'right amygdala'),
}

MEASURE_LABELS = {
    'AI_hippocampus': 'Hippocampus',
    'AI_amygdala':    'Amygdala',
}

# ── Plot Config ───────────────────────────────────────────────────────────────

GROUP_ORDER = ['CN', 'MCI', 'AD']
COLORS      = {'CN': '#b0b0b0', 'MCI': '#c08080', 'AD': '#8b2252'}

# ── Helper Functions ──────────────────────────────────────────────────────────

def compute_ai(left, right):
    """Asymmetry Index: |L - R| / (L + R) * 100"""
    return (abs(left - right) / (left + right)) * 100


def significance_label(p):
    if p < 2.2e-16:
        return 'p < 2.2e-16'
    elif p < 0.001:
        return f'p = {p:.2e}'
    elif p < 0.05:
        return f'p = {p:.3f}'
    else:
        return f'p = {p:.3f} (ns)'


def compute_ai_dataframe(input_path, output_path):
    """Load raw merged CSV, compute AI for hippocampus & amygdala, save and return."""
    df = pd.read_csv(input_path)

    out = pd.DataFrame()
    out['subject'] = df['subject']
    out['group']   = df['group']

    for measure, (left_col, right_col) in REGION_PAIRS.items():
        out[measure] = compute_ai(df[left_col], df[right_col])

    out.to_csv(output_path, index=False)
    print(f"  AI CSV saved → {output_path}  ({len(out)} subjects)")
    return out


def plot_ai(df, plot_path, split_label):
    """Generate facet boxplot with Wilcoxon pairwise brackets and Kruskal-Wallis in title."""
    counts  = df.groupby('group').size()
    measures = list(REGION_PAIRS.keys())

    fig, axes = plt.subplots(1, len(measures), figsize=(10, 6), sharey=False)
    fig.patch.set_facecolor('white')

    # ensure axes is always iterable even for a single panel
    if len(measures) == 1:
        axes = [axes]

    for ax, measure in zip(axes, measures):
        label         = MEASURE_LABELS[measure]
        data_by_group = [
            df[df['group'] == g][measure].dropna().values
            for g in GROUP_ORDER
        ]

        bp = ax.boxplot(
            data_by_group,
            patch_artist=True,
            widths=0.5,
            medianprops=dict(color='black', linewidth=2),
            whiskerprops=dict(color='#555555', linewidth=1.2, linestyle='--'),
            capprops=dict(color='#555555', linewidth=1.2),
            flierprops=dict(marker='o', markersize=3, alpha=0.5, linestyle='none'),
            boxprops=dict(linewidth=1.2)
        )

        for patch, g in zip(bp['boxes'], GROUP_ORDER):
            patch.set_facecolor(COLORS[g])
            patch.set_alpha(0.85)

        for flier, g in zip(bp['fliers'], GROUP_ORDER):
            flier.set_markerfacecolor(COLORS[g])
            flier.set_markeredgecolor(COLORS[g])

        # ── Kruskal-Wallis overall test ───────────────────────────────────
        kw_stat, kw_p = kruskal(*data_by_group)

        # ── Pairwise Wilcoxon Signed-Rank brackets ────────────────────────
        y_max = max(d.max() for d in data_by_group if len(d) > 0)
        y_min = min(d.min() for d in data_by_group if len(d) > 0)
        step  = (y_max - y_min) * 0.13

        for i, (idx1, idx2) in enumerate(itertools.combinations(range(len(GROUP_ORDER)), 2)):
            g1, g2 = data_by_group[idx1], data_by_group[idx2]
            # Wilcoxon requires equal-length paired samples — trim to shorter group
            min_n  = min(len(g1), len(g2))
            _, p   = wilcoxon(g1[:min_n], g2[:min_n], alternative='two-sided')
            x1, x2 = idx1 + 1, idx2 + 1
            y = y_max + step * (i + 1)
            ax.plot([x1, x1, x2, x2], [y - step * 0.1, y, y, y - step * 0.1],
                    lw=1.2, color='black')
            ax.text((x1 + x2) / 2, y + step * 0.05, significance_label(p),
                    ha='center', va='bottom', fontsize=7.5)

        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(
            [f'{g}\n(n={counts.get(g, 0)})' for g in GROUP_ORDER],
            fontsize=10
        )
        ax.set_title(
            f'{label}\nKW: {significance_label(kw_p)}',
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8e8e8', edgecolor='#aaaaaa')
        )
        ax.set_xlabel('Diagnosis', fontsize=11)
        ax.set_ylabel('Asymmetry Index (%)', fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor('white')
        ax.grid(axis='y', linestyle='--', alpha=0.4)

    legend_patches = [
        mpatches.Patch(facecolor=COLORS[g], label=f'{g} (n={counts.get(g, 0)})', alpha=0.85)
        for g in GROUP_ORDER
    ]
    fig.legend(handles=legend_patches, loc='lower center', ncol=3,
               frameon=False, fontsize=11, bbox_to_anchor=(0.5, -0.04))

    plt.suptitle(
        f'Hippocampus & Amygdala Asymmetry Index by Diagnosis — {split_label}\n'
        f'Brackets: Wilcoxon Signed-Rank  |  Panel header: Kruskal-Wallis (overall)',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig(plot_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Plot saved → {plot_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Processing Train set...")
    train_df = compute_ai_dataframe(TRAIN_INPUT, TRAIN_AI)
    plot_ai(train_df, TRAIN_PLOT, split_label="Train")

    print("Processing Test set...")
    test_df = compute_ai_dataframe(TEST_INPUT, TEST_AI)
    plot_ai(test_df, TEST_PLOT, split_label="Test")

    print("Done.")
