# Reproducing the results

## Requirements
Python 3.13 on Linux x86-64 was used for the paper. Pinned versions (`code/requirements.txt`): numpy 2.5.4,
pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1, lightgbm 4.7.0, matplotlib 3.11.2, joblib 1.6.0.

## Steps
```bash
git lfs install
git clone https://github.com/Rishabh-bgp/pan-cancer-classification.git
cd pan-cancer-classification/code
cp ../data/data.csv ../data/labels.csv data/
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

| Command | What it does |
|---|---|
| `python run_all.py` | full run: main benchmark (~18 min on one thread) then revision analyses (~1 h with `--jobs 8`) |
| `python run_all.py --quick` | 2-repeat smoke test |
| `python run_all.py --revision-only` | only the revision analyses, reusing `results/` |
| `python run_all.py --revision-only --extension-only` | only the extension analyses (~5 min) |
| `python run_all.py --jobs 4` | parallel workers for revision analyses (default 8) |
| `python run_all.py --allgenes-jobs 2` | workers for the all-genes benchmark (default 4, capped by RAM) |

## Memory
One all-genes worker peaks at about 1.4 GB; the code budgets 2 GB per worker and never exceeds 80% of available RAM.
Default 4 workers need about 8 GB; 8 workers about 16 GB.

## Alternative
The same code is also archived as `supplementary/PanCancer_code_S1.zip` (Supplementary File S1).

Small numerical differences are possible on other platforms or library versions (e.g. MLP, LightGBM).
