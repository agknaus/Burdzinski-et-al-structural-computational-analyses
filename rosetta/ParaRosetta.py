import subprocess
import multiprocessing
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROSETTA_EXEC = os.environ.get("ROSETTA_EXEC", "rosetta_scripts.static.linuxgccrelease")


def run_command(script, pdb, iterator, output_dir, extra_flags, nstruct):
    protocol = SCRIPT_DIR / script
    os.makedirs(output_dir, exist_ok=True)
    command = (
        f"{ROSETTA_EXEC} -parser:protocol {protocol} "
        f"-nstruct {nstruct} -s {pdb} -suffix {iterator} "
        f"-out:path:all {output_dir} {extra_flags}"
    )
    subprocess.run(command, shell=True)


def main(script, pdb, nstruct, total_jobs, output_dir, extra_flags):
    processes = []
    for i in range(total_jobs):
        p = multiprocessing.Process(
            target=run_command,
            args=(script, pdb, i, output_dir, extra_flags, nstruct),
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(
            "Usage: python ParaRosetta.py <script_name> <pdb_filename> "
            "<nstruct> <total_jobs> <output_dir> <extra_flags>"
        )
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6])
