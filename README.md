# Carnation tag generator for AXO HRW

A simple script to generate a formatted, printable PDF of carnation tags from Google form responses. The PDF is designed to be printable double-sided (messsage on one side, sender/recipient info on the other).

# Installation (macOS)

Clone this repository:
```sh
$ git clone git@github.com:rweinberger/hrw_carnation_tag_generator.git
$ cd hrw_carnation_tag_generator
```

Create a `virtualenv` and install the required packages:
```sh
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Make sure the script runs correctly on the included example responses:
```sh
$ python3 create_pdf.py
Loading pages (1/6)
Warning: Failed to load file:///var/folders/vt/jmy88g7d1v1_1p6hvz7x5fs40000gn/T/style.css (ignore)
Counting pages (2/6)
Resolving links (4/6)
Loading headers and footers (5/6)
Printing pages (6/6)
Done
Loading pages (1/6)
Warning: Failed to load file:///var/folders/vt/jmy88g7d1v1_1p6hvz7x5fs40000gn/T/style.css (ignore)
Counting pages (2/6)
Resolving links (4/6)
Loading headers and footers (5/6)
Printing pages (6/6)
Done
```

You can ignore the warnings about failing to find a CSS file. This command will generate an example  PDF, `out/finished_<timestamp>`, based on the example responses included in this repo, `csv/example_respones.csv`.

# Usage

This script assumes that carnation orders are collected via Google Forms. To generate tags for the current year, first download the form responses as a `.csv`, and put that file in the `csv/` directory. In `create_pdf.py`, update the `RESPONSES_CSV` parameter:

```python3
RESPONSES_CSV = "csv/<your_responses_file>.csv"
```

Depending on how the format of the Google form changes from year to year, you may have to adjust other parameters that describe the columns of the downloaded `.csv`.

Finally, generate the tags PDF, which will be located in `out/finished_<timestamp>.pdf`:
```sh
$ python3 create_pdf.py
```
