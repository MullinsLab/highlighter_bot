# highlighter_bot
Automates [LANL's HIV mutation-highlighting tool](https://www.hiv.lanl.gov/content/sequence/HIGHLIGHT/highlighter_top.html?choice=mismatches)

## Requirements
In a virtual Python 3 environment:
```
pip3 install robobrowser
pip3 install lxml
pip3 install wget
```
## Usage
In a directory containing pairs of FASTA files and Newick .tre files, run:
```
python3 highlighter_bot.py [-a (if amino acid sequences)]
```
