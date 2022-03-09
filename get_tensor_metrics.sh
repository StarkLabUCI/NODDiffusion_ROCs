#!/bin/bash



#PATHS:
config=$1
. $config

#DATA:
id=$2
tensor_data=${der_path}/mrtrix/tensors/sub-${id}/b1500
mkdir -p ${tensor_data}
mkdir -p ${der_path}/dwi_metrics/dwi_space/sub-${id}/tensors/b1500

## GET TENSORS:

# Get b=1500 shells only:
mkdir -p ${der_path}/mrtrix/preprocessed/sub-${id}/b1500

pre=${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif
if [ ! -e ${der_path}/mrtrix/preprocessed/sub-${id}/b1500/sub-${id}_dwi.nii.gz ]; then
dwiextract -shells 0,1500 -export_grad_fsl ${bids_path}/sub-${id}/dwi/sub-${id}_dwi_b1500.bvecs ${bids_path}/sub-${id}/dwi/sub-${id}_dwi_b1500.bvals -fslgrad ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bvec ${bids_path}/sub-${id}/dwi/sub-${id}_dwi.bval ${bids_path}/derivatives/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.nii.gz ${bids_path}/derivatives/mrtrix/preprocessed/sub-${id}/b1500/sub-${id}_dwi.nii.gz
fi

preproc=${der_path}/mrtrix/preprocessed/sub-${id}/b1500/sub-${id}_dwi.nii.gz #only from b=1500 scans,
mask=${der_path}/mrtrix/masks/sub-${id}/sub-${id}_dwi_mask.mif

if [ ! -e ${tensor_data}/sub-${id}_rd.nii.gz ]; then
    dwi2adc ${preproc} -fslgrad /mnt/hippocampus/starkdata1/Hamsi/Lani/BIDS/sub-${id}/dwi/sub-${id}_dwi_b1500.bvecs /mnt/hippocampus/starkdata1/Hamsi/Lani/BIDS/sub-${id}/dwi/sub-${id}_dwi_b1500.bvals ${tensor_data}/sub-${id}_mean_ADC_map.nii.gz # Making ADC maps
    dwi2tensor -fslgrad /mnt/hippocampus/starkdata1/Hamsi/Lani/BIDS/sub-${id}/dwi/sub-${id}_dwi_b1500.bvecs /mnt/hippocampus/starkdata1/Hamsi/Lani/BIDS/sub-${id}/dwi/sub-${id}_dwi_b1500.bvals -mask ${mask} ${preproc} ${tensor_data}/sub-${id}_mean_tensor.nii.gz # Estimating tensors
    tensor2metric ${tensor_data}/sub-${id}_mean_tensor.nii.gz -mask ${mask} -adc ${tensor_data}/sub-${id}_adc.nii.gz -fa ${tensor_data}/sub-${id}_fa.nii.gz -ad ${tensor_data}/sub-${id}_ad.nii.gz -rd ${tensor_data}/sub-${id}_rd.nii.gz # Generating maps of tensor-derived parameters- ADC, FA, AD, RD
fi

## Copy to a nicer place:
for metric in mean_ADC_map mean_tensor adc ad fa rd; do
if [ ! -e ${der_path}/dwi_metrics/dwi_space/sub-${id}/tensors/b1500/sub-${id}_${metric}.nii.gz ]; then
cp ${tensor_data}/sub-${id}_${metric}.nii.gz ${der_path}/dwi_metrics/dwi_space/sub-${id}/tensors/sub-${id}_${metric}.nii.gz
fi
done


