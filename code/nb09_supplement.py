# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# ![SkeideLab and MPI CBS logos](../misc/header_logos.png)
#
# # Notebook #09: Supplement
#
# *Created July 2021 by Alexander Enge* ([enge@cbs.mpg.de](mailto:enge@cbs.mpg.de))
#
# Blablabla
#
# We start by loading the relevant packages.

# %%
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nilearn import plotting
from scipy.stats import norm

from nb01_ale import run_ale, write_peaks_to_sleuth
from nb02_subtraction import run_subtraction

# %% [markdown]
# Blablabla

# %%
# Read table of experiments from ALE analysis
exps = pd.read_json("../results/exps.json")

# %% Define ALE analyses based on presentation and response modalities
ales = dict(
    {
        "../results/ale/visual.txt": 'modality_pres == "visual"',
        "../results/ale/nvisual.txt": 'modality_pres != "visual"',
        "../results/ale/manual.txt": 'modality_resp == "manual"',
        "../results/ale/nmanual.txt": 'modality_resp != "manual"',
        "../results/ale/spm.txt": 'software == "SPM"',
        "../results/ale/nspm.txt": 'software != "SPM"',
    }
)

# Write the relevant experiments to Sleuth text files
for key, value in zip(ales.keys(), ales.values()):
    write_peaks_to_sleuth(text_file=key, df=exps, query=value)

# %%
# Compute the ALE for each Sleuth file
for key in ales.keys():
    run_ale(
        text_file=key,
        voxel_thresh=0.001,
        cluster_thresh=0.01,
        random_seed=1234,
        n_iters=1000,
        output_dir="../results/supplement/",
    )

# %%
# Define subraction analyses
subtrs = dict(
    {
        "../results/ale/nvisual.txt": "../results/ale/visual.txt",
        "../results/ale/nmanual.txt": "../results/ale/manual.txt",
        "../results/ale/spm.txt": "../results/ale/nspm.txt",
    }
)

# Run subtraction analyses
for key, value in zip(subtrs.keys(), subtrs.values()):
    run_subtraction(
        text_file1=key,
        text_file2=value,
        voxel_thresh=0.001,
        cluster_size_mm3=200,
        random_seed=1234,
        n_iters=20000,
        output_dir="../results/supplement",
    )

# %%
# Shared figure parameters
scaling = 2 / 30
figsize = (90 * scaling, 101 * scaling)
margins = {
    "left": 0,
    "bottom": 0,
    "right": 1 - 0.1 * scaling / figsize[0],
    "top": 1 - 0.1 * scaling / figsize[1],
}
vmin = 0
vmax = 5

# Create empty figure with subplots
fig = plt.figure(figsize=figsize)
gs = fig.add_gridspec(85, 90)
ax1 = fig.add_subplot(gs[1:26, :])
ax2 = fig.add_subplot(gs[26:51, :])
ax3 = fig.add_subplot(gs[51:76, :])
_ = fig.subplots_adjust(**margins)

# Plot subtraction maps
basedir = "../results/subtraction/"
for condition, ax in zip(["visual", "manual", "spm"], [ax1, ax2, ax3]):
    ncondition = f"n{condition}"
    fname_unthresh = f"{basedir}{condition}_minus_{ncondition}_z.nii.gz"
    p = plotting.plot_glass_brain(
        fname_unthresh,
        display_mode="lyrz",
        axes=ax,
        cmap="RdYlBu_r",
        vmin=vmin,
        vmax=vmax,
        plot_abs=False,
        symmetric_cbar=True,
    )
    # # Voxel-level thresholding
    # thresh_voxel_p = 0.001
    # thresh_voxel_z = norm.ppf(thresh_voxel_p)
    # fname_thresh = f"{basedir}{condition}_minus_{ncondition}_z_thresh.nii.gz"
    # p.add_contours(fname_thresh, threshold=thresh_voxel_z, colors="black")

# Add subplot labels
_ = ax1.annotate("A", xy=(0, 0.96), xycoords="axes fraction", weight="bold")
_ = ax2.annotate("B", xy=(0, 0.96), xycoords="axes fraction", weight="bold")
_ = ax3.annotate("C", xy=(0, 0.96), xycoords="axes fraction", weight="bold")
_ = ax1.annotate(
    "Visual > auditory/audiovisual stimuli", xy=(0.035, 0.96), xycoords="axes fraction"
)
_ = ax2.annotate(
    "Manual > varbal/no response", xy=(0.035, 0.96), xycoords="axes fraction"
)
_ = ax3.annotate(
    "SPM > other analysis software", xy=(0.035, 0.96), xycoords="axes fraction"
)

# Add colorbar
ax_cbar = fig.add_subplot(gs[75:78, 36:54])
cmap = plt.get_cmap("RdYlBu_r")
norm = mpl.colors.Normalize(vmin=-vmax, vmax=vmax)
mpl.colorbar.ColorbarBase(
    ax_cbar,
    cmap=cmap,
    norm=norm,
    orientation="horizontal",
    ticks=np.arange(-vmax, vmax + 1, 2),
    label="$\it{z}$ score",
)
# plt.axvline(x=-thresh_voxel_z, color="black", linewidth=1)
# plt.axvline(x=thresh_voxel_z, color="black", linewidth=1)

# Save to PDF
fig.savefig("../results/figures/figsupp.pdf")
