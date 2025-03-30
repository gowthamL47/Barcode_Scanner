# Barcode Scanner

A simple barcode scanner using Python. This project supports barcode and QR code scanning using `pyzbar` and `OpenCV`.

## Features
- Scans barcodes and QR codes from images and live video
- Uses `pyzbar` for barcode decoding
- Supports alternative `zxing` library if `pyzbar` fails
- Compatible with Windows, Mac, and Linux

## Installation
### Prerequisites
Ensure you have Python installed (version 3.6 or higher).

### Step 1: Clone the Repository
```sh
git clone https://github.com/your-username/barcode-scanner.git
cd barcode-scanner
```

### Step 2: Create a Virtual Environment (Recommended)
```sh
python -m venv venv
```
Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```

## Usage
### Scan a Barcode from an Image
```sh
python barcode_scanner.py --image path/to/image.png
```

### Scan a Barcode from Webcam
```sh
python barcode_scanner.py --webcam
```

## Troubleshooting
### Missing `libzbar-64.dll` or `libiconv.dll`
1. Download the DLLs from a trusted source:
   - [ZBar Windows Build](https://github.com/mchehab/zbar)
   - Place them in your Python `site-packages/pyzbar/` directory.
2. Alternatively, use `zxing` instead:
```sh
pip install pyzxing
```
Modify your script:
```python
from pyzxing import BarCodeReader
reader = BarCodeReader()
results = reader.decode('barcode_image.png')
print(results)
```

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to your branch (`git push origin feature-branch`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.

## Author
Gowtham L

