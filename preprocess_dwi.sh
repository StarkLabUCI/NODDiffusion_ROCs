#!/bin/bash


#PATHS:
config=$1
. $config

#DATA:
id=$2
mkdir -p ${der_path}/mrtrix/{preprocessed,masks}
mkdir -p ${der_path}/mrtrix/preprocessed/sub-${id}
mkdir -p ${der_path}/mrtrix/masks/sub-${id}


if [ ! -e ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvals ]; then
cp ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bval ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvals
cp ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvec ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvecs
fi

# Conversion:
if [ ! -e ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.mif ]; then
    mrconvert ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.nii.gz ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.mif -fslgrad ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvecs ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvals
fi

# Denoising and unringing:
if [ ! -e ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_dn_ur.mif ]; then 
    dwidenoise ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.mif ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_dn.mif #Remove thermal noise
    mrdegibbs ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_dn.mif ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_dn_ur.mif #Remove Gibbs Ringing Artifacts
fi

# Eddy and motion correct:
if [ ! -e ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dn_ur_edd.mif ]; then
    dwifslpreproc ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_dn_ur.mif -rpe_all -pe_dir AP ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dn_ur_edd.mif #Perform Eddy current and motion correction
fi


# Bias field correct
if [ ! -e ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif ]; then
    dwibiascorrect ants ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dn_ur_edd.mif ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif #Bias field correction
fi

# Make brain mask
if [ ! -e ${der_path}/mrtrix/masks/sub-${id}/sub-${id}_dwi_mask.mif ]; then
    dwi2mask ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif ${der_path}/mrtrix/masks/sub-${id}/sub-${id}_dwi_mask.mif #Make diffusion mask
fi

# Nifti conversions for other programs :)
if [ ! -e ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.nii.gz ]; then 
    mrconvert ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.nii.gz
    mrconvert ${der_path}/mrtrix/masks/sub-${id}/sub-${id}_dwi_mask.mif ${der_path}/mrtrix/masks/sub-${id}/sub-${id}_dwi_mask.nii.gz
fi