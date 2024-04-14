# link-checker
Checks if links are broken.


## Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Usage
```bash
python main.py my_input_data_file.csv my_output_data_file.csv
```
### Input file format
The input data file should be a CSV file with no headers and all links in the first column.
```csv
http://example.com/
http://example.com/other
```
### Output file format
The output file: 
* Uses `,` as delimiter.
* Have one header row `Link` and `Status`.
