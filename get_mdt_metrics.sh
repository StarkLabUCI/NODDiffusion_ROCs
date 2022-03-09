#!/bin/bash

config=$1
. $config
id=$2

# SET UP NODDI DIRECTORY
mdt_path=${der_path}/mdt
mkdir -p ${mdt_path}/sub-${id}

if [ ! -e ${mdt_path}/sub-${id}/sub-${id}_dwi.nii ]; then
mrconvert ${der_path}/mrtrix/preprocessed/sub-${id}/sub-${id}_dwi.mif ${mdt_path}/sub-${id}/sub-${id}_dwi.nii -force #because noddi doesn't like compressed files. Notice preprocessed. 
mrconvert ${der_path}/mrtrix/masks/sub-${id}/sub-${id}_dwi_mask.mif ${mdt_path}/sub-${id}/sub-${id}_mask.nii -force
fi 

cd  ${mdt_path}/sub-${id}
if [ ! -e sub-${id}_dwi.prtcl ]; then
echo Creating Protocol File

#Copying over BVECS and BVALS:
bvec=${mdt_path}/sub-${id}/sub-${id}_dwi.bvecs
bval=${mdt_path}/sub-${id}/sub-${id}_dwi.bvals
if [ ! -e $bvec ]; then
    cp ${bids_path}/sub-${id}/dwi/sub-${id}_dwi_AP.bvec $bvec 
fi
if [ ! -e $bval ]; then
    cp ${bids_path}/sub-${id}/dwi/sub-${id}_dwi_AP.bval $bval 
fi

echo Creating Protocol File
echo bvec is $bvec
echo bval is $bval
echo Protocol file saved as sub-${id}_dwi.prtcl
mdt-create-protocol ${bvec} ${bval}
fi

echo Running NODDI pipeline-MDT on ${id} from ${bids_path} in ${mdt_path}

if [ ! -e ${mdt_path}/sub-${id}/output/sub-${id}_mask/NODDI/NDI.nii.gz ]; then
mdt-model-fit NODDI sub-${id}_dwi.nii sub-${id}_dwi.prtcl sub-${id}_mask.nii
fi

# Copy:
mkdir -p ${der_path}/dwi_metrics/dwi_space/sub-${id}/NODDI
rm ${der_path}/dwi_metrics/dwi_space/sub-${id}/NODDI/*.nii.gz
for metric in NDI ODI w_csf.w; do
    if [ ! -e ${der_path}/dwi_metrics/dwi_space/sub-${id}/NODDI/sub-${id}_${metric}.nii.gz ]; then
        cp ${mdt_path}/sub-${id}/output/sub-${id}_mask/NODDI/${metric}.nii.gz ${der_path}/dwi_metrics/dwi_space/sub-${id}/NODDI/sub-${id}_${metric}.nii.gz
    fi
done

echo Ended at `date` 