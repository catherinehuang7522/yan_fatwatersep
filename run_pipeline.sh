#!/bin/bash

echo "Yan's Water Fat Separation Starting ..."

# Step 1: Run the Python script
python dicom_to_nifti_conv.py
if [ $? -eq 0 ]; then
    echo "Input NIfTI files successfully generated from Scanner DICOMs."
else
    echo "Error: Failed to generate NIfTI files from Scanner DICOMs."
    exit 1
fi

# Step 2: Output the skipping message
echo "[Running Model] - Currently skipping this step."

# Step 3: Check if the most recent Docker container has been pulled
if ! docker images | grep -q "ghcr.io/tomaroberts/nii2dcm"; then
    echo "Pulling the most recent Docker container..."
    docker pull ghcr.io/tomaroberts/nii2dcm:latest
    docker tag ghcr.io/tomaroberts/nii2dcm:latest nii2dcm
else
    echo "Most recent Docker container already pulled."
fi

# Step 4: Run the Docker container with the -v flag
docker run nii2dcm -v

# Step 5: Run the main Docker command
read -p "Please specify the NIfTI file: " nifti_file
read -p "Please specify the DICOM output directory: " dicom_output_dir

docker run nii2dcm "$nifti_file" "$dicom_output_dir" -d MR
if [ $? -eq 0 ]; then
    echo "Final DICOM files successfully generated from output NIfTI files."
else
    echo "Error: Failed to generate DICOM files from NIfTI files."
    exit 1
fi

echo "Yan's Water Fat Separation Completed."
