import subprocess
from workflow.lac.scripts.config import config
from multiprocessing import Pool

if __name__ == "__main__":
    line = "python3 worker.py & "
    for _ in range(config.NWORKERS-1):
        line += line
    subprocess.run(line, shell=True)