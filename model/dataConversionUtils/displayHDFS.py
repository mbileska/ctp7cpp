import h5py

def display_hdf5_contents(hdf5_file_path, preview_limit=100):
    """
    Displays the contents of the HDF5 file, including the data within datasets.

    Args:
    hdf5_file_path (str): The path to the HDF5 file.
    preview_limit (int): Maximum number of elements to preview for large datasets.
    """
    # Open the HDF5 file
    with h5py.File(hdf5_file_path, 'r') as file:
        print(f"Contents of the HDF5 file: {hdf5_file_path}\n")

        def print_info(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"Dataset: {name}")
                print(f"  Shape: {obj.shape}")
                print(f"  Data Type: {obj.dtype}")
                if obj.size <= preview_limit:
                    print(f"  Data: {obj[...]}")  # Load all data if small
                else:
                    # Load part of the data for preview if too large
                    preview = obj[:preview_limit] if len(obj.shape) == 1 else obj[:preview_limit, ...]
                    print(f"  Data Preview: {preview}")
            elif isinstance(obj, h5py.Group):
                print(f"Group: {name}")
        
        # Use the visititems method to iterate over every item in the file
        file.visititems(print_info)

if __name__ == "__main__":
    hdf5_file_path = "data.h5"  # Path to your HDF5 file
    display_hdf5_contents(hdf5_file_path)
