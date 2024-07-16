import h5py

def extract_and_write_data(h5_file_path, output_file_path, num_events=100):
    # Open the h5 file
    with h5py.File(h5_file_path, 'r') as f:
        # Extract data from the file
        cregions = f['cregions'][:num_events]
        genEta = f['genEta_1'][:num_events]
        genPhi = f['genPhi_1'][:num_events]
        genId = f['genId'][:num_events]
    
    # Write the data to a text file
    with open(output_file_path, 'w') as file:
        for i in range(num_events):
            file.write(f"Event {i+1}:\n")
            file.write(f"cregions: {cregions[i]}\n")
            file.write(f"genId: {genId[i]}\n")
            file.write(f"genEta: {genEta[i]}\n")
            file.write(f"genPhi: {genPhi[i]}\n")
            file.write("\n")

# Specify the path to your h5 file and the output text file
h5_file_path = 'data.h5'
output_file_path = 'output.txt'

# Extract and write data to the text file
extract_and_write_data(h5_file_path, output_file_path)
