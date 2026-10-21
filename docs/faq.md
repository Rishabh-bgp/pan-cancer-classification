# FAQ and limitations

**Does this repository propose a new classifier?**  No. It audits what near-perfect accuracy on this dataset can and
cannot show.

**Why can't I see gene names?**  The UCI release uses dummy names (`gene_0 … gene_20530`). Genes are reported only by
index; no biological gene identity is claimed.

**Is the dataset included?**  Yes, in `data/`. `data.csv` is stored with Git LFS — run `git lfs install` before cloning.

**How long does a full run take?**  About 1.5–2 h on an 8-vCPU machine with ~8 GB RAM.

## Limitations (from `code/README.md`)
* No gene identification (dummy gene names).
* No test of generalisation beyond this TCGA subset (no external cohort).
* Timings come from one shared virtual machine and are indicative only.
* Mondrian conformal sets are uninformative at 99% because classes have too few calibration samples.
