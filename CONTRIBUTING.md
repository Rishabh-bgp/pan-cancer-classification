# Contributing

Thanks for your interest in **Pan-Cancer Tumour-Type Classification**. This is a research archive that backs a manuscript, so the scientific
results are frozen. Contributions are still welcome in these areas:

* **Reproducibility reports:** if a rerun gives numbers that differ from the files in this repository, open an issue
  with your OS, Python version, `pip freeze` output and the command you ran.
* **Bug fixes** in the code that do not change the published method.
* **Documentation** fixes (typos, unclear steps, broken links).

## Workflow
1. Fork the repository and create a branch: `git checkout -b fix/short-description`.
2. Create a virtual environment and install the pinned requirements (see `docs/reproducing.md`).
3. Run the quick or single-stage commands to check your change.
4. Open a pull request that explains what changed and why.

## Ground rules
* Do not edit the result files by hand. Results must come from the code.
* Do not commit virtual environments, caches, `.DS_Store` files or credentials.
* Large files are stored with Git LFS (`git lfs install` before cloning).
* By contributing you agree that your contribution is released under the MIT licence of this repository.
