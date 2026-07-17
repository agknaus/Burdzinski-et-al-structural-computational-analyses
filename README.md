# Activin–receptor redocking [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21415539.svg)](https://doi.org/10.5281/zenodo.21415539)

Boltz structure prediction → Rosetta constrained relax → Rosetta global docking.

## Software

| Tool | Version |
|------|---------|
| Boltz | 2.1.1 (`conda` env `boltz-2`) |
| Rosetta | 2023.45+release (r362) |

MSAs: ColabFold server (`--use_msa_server`, default `https://api.colabfold.com`).

Boltz inference flags used with the example inputs:

| Flag | Value |
|------|-------|
| `--recycling_steps` | 3 |
| `--sampling_steps` | 200 |
| `--diffusion_samples` | 5 |
| `--use_msa_server` | (set) |

(`sampling_steps` is the diffusion sampler length; `recycling_steps` is trunk recycling.)

## Pipeline

```
boltz predict  →  relax_cst.xml  →  ParaRosetta.py + Docking.xml
   (.cif)            (_0001.pdb)         (docking.fasc + .pdb)
```

## Boltz inputs

Example YAMLs are in `scripts/boltz/`, each a 6-chain homodimeric complex of Activin A (chains C, D), the type I receptor ECD under study — ALK2/ACVR1 or ALK4/ACVR1B (chains A, B) — and the type II receptor ACVR2B ECD (chains E, F).

## Commands

Example for a six-chain ALK2–receptor complex:

```bash
# 1. Predict
conda activate boltz-2
boltz predict scripts/boltz/ALK2-complex.yaml --use_msa_server \
  --recycling_steps 3 --sampling_steps 200 --diffusion_samples 5
# → boltz_results_ALK2-complex/predictions/ALK2-complex/ALK2-complex_model_0.cif

# 2. Relax
rosetta_scripts.static.linuxgccrelease \
  -parser:protocol scripts/rosetta/relax_cst.xml \
  -s ALK2-complex_model_0.cif \
  -nstruct 3
# → ALK2-complex_model_0_0001.pdb

# 3. Dock
python scripts/rosetta/ParaRosetta.py \
  scripts/rosetta/Docking.xml \
  ALK2-complex_model_0_0001.pdb 600 100 ALK2-complex_out \
  "-docking:partners B_ACDEF -docking:dock_pert 3 8 \
   -docking:dock_mcm_trans_magnitude 0.1 \
   -docking:dock_mcm_rot_magnitude 5.0 \
   -use_input_sc -scorefile docking.fasc"
```

Replace `ALK2-complex` with `ALK4-complex` (and paths) for the second system.

### `ParaRosetta.py`

```
python ParaRosetta.py <xml> <input.pdb> <nstruct> <total_jobs> <output_dir> "<extra_flags>"
```

Spawns `total_jobs` parallel processes; each writes `nstruct` models. Total structures ≈ `nstruct × total_jobs`.

### Docking partners

Rosetta flag `-docking:partners` uses `MOVING_FIXED` chain notation (underscore-separated).

Set **one moving chain** and **all others fixed**. In the example above, `B_ACDEF` moves chain B while A, C, D, E, F stay fixed. Match chain letters to your Boltz YAML / relaxed PDB.

## Files

```
scripts/
├── README.md
├── boltz/
│   ├── ALK2-complex.yaml
│   └── ALK4-complex.yaml
└── rosetta/
    ├── ParaRosetta.py   # parallel launcher
    ├── Docking.xml      # global docking protocol (ref2015)
    └── relax_cst.xml    # constrained relax (ref2015_cst)
```

