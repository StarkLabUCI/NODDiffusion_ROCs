#!/bin/bash

#PATHS:
config=$1

#DATA:
id=$2
. $config
mkdir -p ${der_path}/ANTS/B0_T1/sub-${id}

#Extract B0s for T1 registration:
if [ ! -e ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_meanB0.nii.gz ]; then
    dwiextract ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif - -bzero | mrmath - mean ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_meanB0.nii.gz -axis 3
fi

#Register DWI B0 to T1:
if [ ! -e ${der_path}/ANTS/B0_T1/sub-${id}/sub-${id}_b0t11Warp.nii.gz ]; then
    antsRegistrationSyNQuick.sh -d 3 -n 4 -m ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_meanB0.nii.gz -f ${bids_path}/sub-${id}/anat/sub-${id}_T1w.nii.gz -o ${der_path}/ANTS/B0_T1/sub-${id}/sub-${id}_b0t1
fi

if [ ! -e ${der_path}/ANTS/B0_T1/sub-${id}/sub-${id}_b0_t1wspace.nii.gz ]; then
    antsApplyTransforms -d 3 -i ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi_meanB0.nii.gz -r ${bids_path}/sub-${id}/anat/sub-${id}_T1w.nii.gz -t ${der_path}/ANTS/B0_T1/sub-${id}/sub-${id}_b0t11Warp.nii.gz -t ${der_path}/ANTS/B0_T1/sub-${id}/sub-${id}_b0t10GenericAffine.mat -o ${der_path}/ANTS/B0_T1/sub-${id}/sub-${id}_b0_t1wspace.nii.gz
fi
