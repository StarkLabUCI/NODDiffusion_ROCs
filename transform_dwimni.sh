#!/bin/bash

config=$1
id=$2

. $config

subfield_template=${code_path}/ModelROIs_May2016_wEllipseRule_MNI152.nii #hippocampal subfield template
mni2t1=${der_path}/fmriprep/sub-${id}/anat/sub-${id}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5
t12mni=${der_path}/fmriprep/sub-${id}/anat/sub-${id}_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5
mkdir -p ${der_path}/dwi_metrics/MNI-direct_space/sub-${id}/tensors/b1500

#Get template in T1w space:
reference=${bids_path}/sub-${id}/anat/sub-${id}_T1w.nii.gz
mkdir -p ${der_path}/ANTS/transformed_templates/sub-${id}
if [ ! -e ${der_path}/ANTS/transformed_templates/sub-${id}/ModelROIs-subfields_T1wspace.nii.gz ]; then
antsApplyTransforms -d 3 -i ${subfield_template} -o ${der_path}/ANTS/transformed_templates/sub-${id}/ModelROIs-subfields_T1wspace.nii.gz -r ${reference} -t ${mni2t1} -n NearestNeighbor -v
fi

#Get diffusion metrics in MNI space:
mkdir -p ${der_path}/dwi_metrics/MNI_space/sub-${id}/{NODDI,tensors}

for metric in NDI ODI w_csf.w; do
if [ ! -e ${der_path}/dwi_metrics/MNI_space/sub-${id}/NODDI/sub-${id}_${metric}.nii.gz ]; then
    antsApplyTransforms -d 3 -i ${der_path}/dwi_metrics/T1w_space/sub-${id}/NODDI/sub-${id}_${metric}.nii.gz -r ${der_path}/fmriprep/sub-${id}/anat/sub-${id}_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz -t ${t12mni} -o ${der_path}/dwi_metrics/MNI_space/sub-${id}/NODDI/sub-${id}_${metric}.nii.gz
fi
done

for metric in ad adc fa rd; do
if [ ! -e ${der_path}/dwi_metrics/MNI_space/sub-${id}/tensors/sub-${id}_${metric}.nii.gz ]; then
    antsApplyTransforms -d 3 -i ${der_path}/dwi_metrics/T1w_space/sub-${id}/tensors/sub-${id}_${metric}.nii.gz -r ${der_path}/fmriprep/sub-${id}/anat/sub-${id}_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz -t ${t12mni} -o ${der_path}/dwi_metrics/MNI_space/sub-${id}/tensors/sub-${id}_${metric}.nii.gz
fi
done
