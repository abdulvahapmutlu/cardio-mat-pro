# CardioMatPro

This project processes ECG (Electrocardiography) data from the dataset. It preprocesses metadata, reads ECG records, and saves them into `.mat` files categorized by diagnostic classes.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository:**
    ```
    git clone https://github.com/abdulvahapmutlu/cardio-mat-pro.git
    cd cardio-mat-pro
    ```

2. **Create a virtual environment (optional but recommended):**
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the required packages:**
    ```
    pip install -r requirements.txt
    ```

## Usage
Run the main processing script:
```
python scripts/process_ecg.py
```
This will process the ECG records and save the .mat files in the specified output directory.

This project is licensed under the MIT License.
