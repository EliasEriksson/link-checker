# link-checker
Checks if links are broken.


## Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Usage
### In parallel
This is useful if the link are from different domains. It is many times faster than sequential but can put a load on
the receivers server if it's the same domain.
```bash
python main.py my_input_data_file.csv my_output_data_file.csv
```

### In sequence
This is useful if all the links are from the same domain. Be nice to the server owner!
0 Can be specified to send sequential but with 0 extra downtime.
```bash
python main.py my_input_data_file.csv my_output_data_file.csv 3.1
```



Failed connections are marked with status `502`

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
