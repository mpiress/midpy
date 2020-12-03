#!/bin/bash
#SBATCH -J Master4c
#SBATCH --ntasks-per-node=1
#SBATCH --ntasks-per-core=1
#SBATCH -t 7-00:00         		# Runtime in D-HH:MM, minimum of 10 minutes
#SBATCH -p medium            		# Partition to submit to
#SBATCH -o logs/master.out      	# File to which STDOUT will be written, %j inserts jobid
#SBATCH -e logs/master.err      	# File to which STDERR will be written, %j inserts jobid
#SBATCH -w compute-0-11     		# Define host for execute job
#SBATCH --qos qos-7d                   # qos type to sixty jobs by experiment

srun python3.6 master.py

exit 0
