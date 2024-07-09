import os
import numpy as np
import pydicom
import nibabel as nib
import matplotlib.pyplot as plt

# Define the root directory and input/output directories
root = '/home/chuang/yan_nifti/'
input_nii_dir = os.path.join(root, 'nifti_test/')
data_dir = os.path.join(root, 'dicom/')
pt_list = os.listdir(data_dir)
print(pt_list)

def make_nii(input_image):
    return nib.Nifti1Image(input_image, np.eye(4))

def save_nii(nii_image, dest):
    nib.save(nii_image, dest)
    print(f'Saved NIfTI file to {dest}')

# Loop through each patient directory
for jj in range(len(pt_list)):
    pt_data_dir = os.path.join(data_dir, pt_list[jj])
    if not os.path.isdir(pt_data_dir):
        continue
    
    series = pt_list[jj][:4]
    
    ip_dir = os.path.join(pt_data_dir, 'in_phase')
    op_dir = os.path.join(pt_data_dir, 'out_of_phase')
    
    if not os.path.exists(ip_dir) or not os.path.exists(op_dir):
        continue
    
    ip_mag_list = sorted([f for f in os.listdir(ip_dir) if 'mag' in f])
    ip_ph_list = sorted([f for f in os.listdir(ip_dir) if 'ph' in f])
    op_mag_list = sorted([f for f in os.listdir(op_dir) if 'mag' in f])
    op_ph_list = sorted([f for f in os.listdir(op_dir) if 'ph' in f])
    
    num_slices = len(ip_mag_list)
    
    # Loop through each slice
    for sl in range(num_slices):
        print(f'Processing slice {sl+1} of series {series}')
        input_image = np.zeros((512, 512, 6), dtype=np.int16)  # Adjust size based on your images
        
        # Get in-phase image
        ip_mag_file = ip_mag_list[sl]
        input_image[:, :, 0] = pydicom.dcmread(os.path.join(ip_dir, ip_mag_file)).pixel_array
        ip_ph_file = ip_ph_list[sl]
        input_image[:, :, 1] = pydicom.dcmread(os.path.join(ip_dir, ip_ph_file)).pixel_array
        
        # Get out-of-phase image
        op_mag_file = op_mag_list[sl]
        input_image[:, :, 2] = pydicom.dcmread(os.path.join(op_dir, op_mag_file)).pixel_array
        op_ph_file = op_ph_list[sl]
        input_image[:, :, 3] = pydicom.dcmread(os.path.join(op_dir, op_ph_file)).pixel_array
        
        # Get TEs
        hdr1 = pydicom.dcmread(os.path.join(ip_dir, ip_mag_file))
        input_image[:, :, 4] = int(hdr1.EchoTime * 1000)
        hdr2 = pydicom.dcmread(os.path.join(op_dir, op_mag_file))
        input_image[:, :, 5] = int(hdr2.EchoTime * 1000)
        
        # Display images (optional)
        for ii in range(6):
            plt.figure()
            plt.imshow(input_image[:, :, ii], cmap='gray')
            plt.colorbar()
            plt.show()
        
        # Create NIfTI image and save
        input_image_nii = make_nii(input_image)
        dest_dir = os.path.join(input_nii_dir, series)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest = os.path.join(dest_dir, f'{series}-{sl+1}-input-images-iTEs.nii')
        save_nii(input_image_nii, dest)
