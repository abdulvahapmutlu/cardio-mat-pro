import os
import wfdb
import pandas as pd
from scipy.io import savemat
from ast import literal_eval
import numpy as np

# Step 1: Load the metadata
metadata_file = '/path/to/file'
metadata = pd.read_csv(metadata_file)

# Step 2: Preprocess the metadata (extract relevant columns and map diagnostic classes)
metadata['scp_codes'] = metadata['scp_codes'].apply(literal_eval)  # Convert scp_codes column to a dict
# Extract the primary diagnostic class (main diagnostic class)
metadata['diagnostic_class'] = metadata['scp_codes'].apply(lambda x: list(x.keys())[0])

# Step 3: Define the path to the folder where ECG records are stored and where you want to save the .mat files
records_path = '/path/to/folder'
output_folder = '/path/to/folder'

# Ensure the output directory exists, if not, create it
os.makedirs(output_folder, exist_ok=True)

# Function to search the subdirectories in records500 to find the correct file
def find_record_path(records_path, record_name):
    for subdir, _, files in os.walk(records_path):
        for file in files:
            if file.startswith(record_name):  # Match the record name exactly, without any suffix
                return os.path.join(subdir, file.rsplit('.', 1)[0])  # Return the file path without extension
    return None

# Step 4: Create a function to process and save records to .mat files by class, with 5000x12 format and flexible chunking
def save_records_by_class(metadata, records_path, output_folder, chunk_threshold=3000):
    # Group metadata by diagnostic class
    grouped = metadata.groupby('diagnostic_class')
    
    # Loop over each diagnostic class and save the records into .mat files
    for class_name, group in grouped:
        print(f'Processing class: {class_name}')
        signals = []
        
        for _, row in group.iterrows():
            # Extract the path to the ECG signal
            record_name = str(row['ecg_id']).zfill(5)
            record_path = find_record_path(records_path, record_name)
            
            if record_path:
                try:
                    # Read the ECG signal using wfdb
                    record = wfdb.rdrecord(record_path)
                    signal = record.p_signal
                    
                    # Ensure the signal is 5000 samples long
                    # If it's longer, truncate; if shorter, pad with zeros
                    if signal.shape[0] > 5000:
                        signal = signal[:5000, :]
                    elif signal.shape[0] < 5000:
                        padding = np.zeros((5000 - signal.shape[0], signal.shape[1]))
                        signal = np.vstack((signal, padding))
                    
                    # Ensure the signal has 12 channels (some records might have fewer channels)
                    if signal.shape[1] < 12:
                        padding = np.zeros((signal.shape[0], 12 - signal.shape[1]))
                        signal = np.hstack((signal, padding))
                    
                    signals.append(signal)
                except Exception as e:
                    print(f"Error reading record {record_name}: {e}")
                    continue
            else:
                print(f"Record {record_name} not found. Skipping.")
        
        # Replace any invalid characters in the class name
        safe_class_name = class_name.replace('/', '_').replace('\\', '_')
        
        # Save in chunks if the signals list exceeds the chunk_threshold
        if len(signals) > chunk_threshold:
            chunk_size = chunk_threshold  # Save records in batches of the chunk_threshold size
            for i in range(0, len(signals), chunk_size):
                chunk_signals = signals[i:i + chunk_size]
                mat_file_path = os.path.join(output_folder, f'{safe_class_name}_part_{i//chunk_size + 1}.mat')
                savemat(mat_file_path, {class_name: np.array(chunk_signals)}, do_compression=True)
                print(f'Saved {safe_class_name}_part_{i//chunk_size + 1}.mat with {len(chunk_signals)} records in {output_folder}.')
        else:
            mat_file_path = os.path.join(output_folder, f'{safe_class_name}.mat')
            savemat(mat_file_path, {class_name: np.array(signals)}, do_compression=True)
            print(f'Saved {safe_class_name}.mat with {len(signals)} records in {output_folder}.')
    
# Step 5: Run the function to save .mat files for each diagnostic class
save_records_by_class(metadata, records_path, output_folder, chunk_threshold=2500)
