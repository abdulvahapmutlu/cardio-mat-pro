# scripts/process_ecg.py

import os
import wfdb
import pandas as pd
from scipy.io import savemat
from ast import literal_eval
import numpy as np
import yaml
from utils import find_record_path

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def preprocess_metadata(metadata_file):
    metadata = pd.read_csv(metadata_file)
    metadata['scp_codes'] = metadata['scp_codes'].apply(literal_eval)  # Convert scp_codes column to a dict
    metadata['diagnostic_class'] = metadata['scp_codes'].apply(lambda x: list(x.keys())[0])
    return metadata

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
                    if signal.shape[0] > 5000:
                        signal = signal[:5000, :]
                    elif signal.shape[0] < 5000:
                        padding = np.zeros((5000 - signal.shape[0], signal.shape[1]))
                        signal = np.vstack((signal, padding))
                    
                    # Ensure the signal has 12 channels
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
            chunk_size = chunk_threshold
            for i in range(0, len(signals), chunk_size):
                chunk_signals = signals[i:i + chunk_size]
                mat_file_path = os.path.join(output_folder, f'{safe_class_name}_part_{i//chunk_size + 1}.mat')
                savemat(mat_file_path, {class_name: np.array(chunk_signals)}, do_compression=True)
                print(f'Saved {safe_class_name}_part_{i//chunk_size + 1}.mat with {len(chunk_signals)} records in {output_folder}.')
        else:
            mat_file_path = os.path.join(output_folder, f'{safe_class_name}.mat')
            savemat(mat_file_path, {class_name: np.array(signals)}, do_compression=True)
            print(f'Saved {safe_class_name}.mat with {len(signals)} records in {output_folder}.')

def main():
    # Load configuration
    config = load_config(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml'))
    
    # Preprocess metadata
    metadata = preprocess_metadata(config['metadata_file'])
    
    # Ensure the output directory exists
    os.makedirs(config['output_folder'], exist_ok=True)
    
    # Run the processing function
    save_records_by_class(
        metadata=metadata,
        records_path=config['records_path'],
        output_folder=config['output_folder'],
        chunk_threshold=config.get('chunk_threshold', 3000)
    )

if __name__ == '__main__':
    main()
