import os
import numpy as np
import pydicom
import nibabel as nib
import matplotlib.pyplot as plt

def get_root_directory():
    root = input("Please enter the root directory: ")
    if not os.path.isdir(root):
        print("Invalid directory. Please try again.")
        return get_root_directory()
    return root

def make_nii(input_image):
    return nib.Nifti1Image(input_image, np.eye(4))

def save_nii(nii_image, dest):
    nib.save(nii_image, dest)
    print(f'Saved NIfTI file to {dest}')

def main():
    root = get_root_directory()
    
    input_nii_dir = os.path.join(root, 'nifti_test/')
    data_dir = os.path.join(root, 'dicom/')
    phase_dirs = ['in_phase', 'out_of_phase']

    # Gather all unique patient numbers
    patients = set()
    for phase in phase_dirs:
        phase_dir = os.path.join(data_dir, phase)
        files = os.listdir(phase_dir)
        for file in files:
            parts = file.split('_')
            if len(parts) > 1:
                patient_num = parts[1].split('.')[0]
                patients.add(patient_num)

    # Loop through each patient number
    for pt in patients:
        ip_mag_list = sorted([f for f in os.listdir(os.path.join(data_dir, 'in_phase')) if f'Sec_{pt}.ip.mag' in f])
        ip_ph_list = sorted([f for f in os.listdir(os.path.join(data_dir, 'in_phase')) if f'Sec_{pt}.ip.ph' in f])
        op_mag_list = sorted([f for f in os.listdir(os.path.join(data_dir, 'out_of_phase')) if f'Sec_{pt}.op.mag' in f])
        op_ph_list = sorted([f for f in os.listdir(os.path.join(data_dir, 'out_of_phase')) if f'Sec_{pt}.op.ph' in f])
        
        num_slices = len(ip_mag_list)
        
        # Loop through each slice
        for sl in range(num_slices):
            print(f'Processing slice {sl+1} of patient {pt}')
            input_image = np.zeros((512, 512, 6), dtype=np.int16)  # Adjust size based on your images
            
            # Get in-phase image
            ip_mag_file = ip_mag_list[sl]
            input_image[:, :, 0] = pydicom.dcmread(os.path.join(data_dir, 'in_phase', ip_mag_file)).pixel_array
            ip_ph_file = ip_ph_list[sl]
            input_image[:, :, 1] = pydicom.dcmread(os.path.join(data_dir, 'in_phase', ip_ph_file)).pixel_array
            
            # Get out-of-phase image
            op_mag_file = op_mag_list[sl]
            input_image[:, :, 2] = pydicom.dcmread(os.path.join(data_dir, 'out_of_phase', op_mag_file)).pixel_array
            op_ph_file = op_ph_list[sl]
            input_image[:, :, 3] = pydicom.dcmread(os.path.join(data_dir, 'out_of_phase', op_ph_file)).pixel_array
            
            # Get TEs
            hdr1 = pydicom.dcmread(os.path.join(data_dir, 'in_phase', ip_mag_file))
            input_image[:, :, 4] = int(hdr1.EchoTime * 1000)
            hdr2 = pydicom.dcmread(os.path.join(data_dir, 'out_of_phase', op_mag_file))
            input_image[:, :, 5] = int(hdr2.EchoTime * 1000)
            
            # Display images (optional)
            for ii in range(6):
                plt.figure()
                plt.imshow(input_image[:, :, ii], cmap='gray')
                plt.colorbar()
                plt.show()
            
            # Create NIfTI image and save
            input_image_nii = make_nii(input_image)
            dest_dir = os.path.join(input_nii_dir, pt)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest = os.path.join(dest_dir, f'{pt}-{sl+1}-input-images-iTEs.nii')
            save_nii(input_image_nii, dest)

if __name__ == '__main__':
    main()