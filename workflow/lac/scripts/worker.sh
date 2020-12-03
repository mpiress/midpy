#!/bin/bash
#SBATCH -J Worker4c			# name
#SBATCH --ntasks-per-core=1
#SBATCH -N 4                		# Ensure that all cores are on one machine
#SBATCH -a 1-1				# sbatch array of job replications
#SBATCH -t 7-00:00         		# Runtime in D-HH:MM, minimum of 10 minutes
#SBATCH -p medium            		# Partition to submit to
#SBATCH -o logs/worker-%A_%a.out      	# File to which STDOUT will be written, %j inserts jobid
#SBATCH -e logs/worker-%A_%a.err      	# File to which STDERR will be written, %j inserts jobid
#SBATCH -w compute-0-6,compute-0-7,compute-0-9,compute-0-10
#SBATCH --qos qos-7d                   # qos type to sixty jobs by experiment

srun python3.6 worker.py

exit 0
