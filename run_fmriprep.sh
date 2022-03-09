#!/bin/bash
# Setup qsub options
#SBATCH --partition=standard
#SBATCH --job-name=run_fmriprep
#SBATCH -o mnt/starkdata1/Hamsi/Lani/BIDS/gridlog


umask 002

echo Job ID: $SLURM_JOB_ID
echo Job name: $SLURM_JOB_NAME
echo Submit host: $SLURM_SUBMIT_HOST
echo "Node(s) used": $SLURM_JOB_NODELIST

echo Using $SLURM_NPROCS slots
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=$SLURM_NPROCS
export OMP_NUM_THREADS=$SLURM_NPROCS


# Log some useful stuff into that log file 
echo Started at `date` 
echo Running on $subject in `pwd` 
echo Running on $HOSTNAME 
echo FSL is in `which fsl`
# echo $FSLDIR
# export FSLDIR=${FSLDIR}
export FSLOUTPUTTYPE=NIFTI_GZ
# export ANTSPATH=/usr/local/ants
echo topup is `which fsl5.0-topup`
echo $OMP_NUM_NTHREADS

config=$1
. ${config}

id=$2

#singularity build fmriprep-20-2-1.simg docker://nipreps/fmriprep:20.2.1
singularity_image=fmriprep-20-2-1.simg #https://fmriprep.org/en/20.2.1/


time singularity run \
	-B /mnt/hippocampus:/mnt/hippocampus \
    -B /run/shm:/run/shm \
    fmriprep-20-2-1.simg \
    ${bids_path}/ ${bids_path}/derivatives \
    participant -w ${bids_path} \
    --skip_bids_validation \
    --participant-label sub-$id \
    --anat-only --verbose

