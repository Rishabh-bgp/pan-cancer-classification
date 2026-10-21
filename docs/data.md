# Data

The dataset is **included** in this repository under `data/`.

| File | Size | Description |
|---|---|---|
| `data/data.csv` | 206,186,150 bytes (stored with **Git LFS**) | 801 samples × 20,531 genes, log-scaled expression; gene columns are dummy names `gene_0 … gene_20530` |
| `data/labels.csv` | 12,713 bytes | cancer type per sample: BRCA, COAD, KIRC, LUAD, PRAD |

## Source
Fiorini S. *Gene expression cancer RNA-Seq* [dataset]. UCI Machine Learning Repository, 2016,
doi:[10.24432/C5R88H](https://doi.org/10.24432/C5R88H) — https://archive.ics.uci.edu/dataset/401
(archive `TCGA-PANCAN-HiSeq-801x20531.tar.gz`). The data derive from the TCGA Pan-Cancer project
(https://www.cancer.gov/tcga). The dataset keeps its original UCI licence; it is not covered by this repository's MIT licence.

## Checksums (SHA-256)
```
data.csv    e3e7eff51f4a5fe5f121fb183c09786c767c755ef10d1c7b3ce3c193a7082ca9
labels.csv  e1653ccf5a630deb3b953ccac5a8b331b89adc5433e5d2d3444c1fc01d79e7aa
```
Verify with `sha256sum data/data.csv data/labels.csv`.

## Getting the large file
`data.csv` is larger than GitHub's 100 MB limit, so it is stored with Git LFS. Run `git lfs install` before cloning,
or `git lfs pull` inside an existing clone. If you see a small text pointer instead of a CSV, LFS was not active.

## Notes
* No gene symbols are included, so the analysis reports genes only by their anonymised index.
* The first run of the pipeline caches the matrix as `code/data/X.npy`.
