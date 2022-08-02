[![CC BY 4.0][cc-by-shield]][cc-by]
# FormulaNet

FormulaNet is a new large-scale Mathematical Formula Detection dataset. It consists of 46'672 pages of STEM documents from [arXiv](arxiv.org) and has 
13 types of labels. The dataset is split into a [train](Dataset/train) set of 44'338 pages and a [validation](Dataset/val) set of 2'334 pages. Due to 
copyrights reasons, we can only provide the [list](urls.txt) of papers, which must be downloaded and processed.

## Labels

* inline formulae
* display formulae
* headers
* tables
* figures
* paragraphs
* captions
* footnotes
* lists
* bibliographies
* display formulae reference number
* display formulae with reference number
* footnote reference number

## Get FormulaNet
**Prerequisites**
* Linux or macOS is recommended
* A LaTeX installation is required
* Clone the repository
```shell
    git clone ...
```
* Pull the git lfs
```shell
    git lfs pull
```
**Install the python environment (recommended Python 3.8)**
```shell
    pip install requirements.txt 
```
**run the script**
```shell
    python download.py 
```


## Baseline Model

Model | mAP        | mAP@50     | mAP@75     | mAP@inline | mAP@display
---|------------|------------|------------|------------|--- 
FCOS-50 | 0.754±0.03 | 0.921±0.02 | 0.84±0.02  | 0.752±0.02 | 0.755±0.02
FCOS-101 | 0.755±0.03 | 0.920±0.02 | 0.841±0.02 | 0.756±0.02 | 0.749±0.03

The results can be reproduced by using these config files ([FCOS-50](Baseline/FCOS-50.py), [FCOS-101](Baseline/FCOS-101.py)) and the github repo [Yuxiang1995/ICDAR2021_MFD](https://github.com/Yuxiang1995/ICDAR2021_MFD).

## License
This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
## Citation

FormulaNet: A Benchmark Dataset for Mathematical Formula Detection

Felix Schmitt-Koopmann, Elaine Huang, Hans-Peter Hutter, Thilo Stadelmann, Alireza Darvishy