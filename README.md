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

## Get FormulaNet (Docker option recommended)

### Docker option
**Prerequisites**
* Docker
* Clone the repository
```shell
    git clone https://github.com/felix-schmitt/FormulaNet.git
```
* Get the annotation files with git lfs or [Dropbox](https://www.dropbox.com/sh/9yjb1lkv9dnmdev/AABBH7QFVA888scAu4Rgj1sja?dl=0)
```shell
    cd FormulaNet
    git lfs pull
```
The file structure should look like this:

    .
    ├── ...
    ├── Dataset
    │   ├── train
    │   │     ├── img   # empty folder
    │   │     └── train_coco.json
    │   └── test
    │         ├── img   # empty folder
    │         └── test_coco.json
    └── ...

**build dockerfile (amd64 and arm64 supported)**
```shell
    docker build -t formulanet --build-arg Platform='amd64' .
```

**run the container with mounting the FormulaNet Folder**
```shell
    docker run -v ~/<path to FormulaNet folder>/Dataset:/FormulaNet/Dataset formulanet
```

### Classic option

**Prerequisites**
* Ubuntu 20.04.5 LTS is recommended
* A LaTeX installation with texlive-full (2019 is recommended) is required
* Clone the repository
```shell
    git clone https://github.com/felix-schmitt/FormulaNet.git
```
* Get the annotation files with git lfs or [Dropbox](https://www.dropbox.com/sh/9yjb1lkv9dnmdev/AABBH7QFVA888scAu4Rgj1sja?dl=0)
```shell
    cd FormulaNet
    git lfs pull
```
The file structure should look like this:

    .
    ├── ...
    ├── Dataset
    │   ├── train
    │   │     ├── img   # empty folder
    │   │     └── train_coco.json
    │   └── test
    │         ├── img   # empty folder
    │         └── test_coco.json
    └── ...

**Install the python environment (recommended Python 3.8)**
```shell
    pip install -r requirements.txt 
```
**run the script**
```shell
    python download.py 
```

## Baseline Model

| Model    | mAP        | mAP@50     | mAP@75     | mAP@inline | mAP@display |
|----------|------------|------------|------------|------------|-------------|
| FCOS-50  | 0.754±0.03 | 0.921±0.02 | 0.84±0.02  | 0.752±0.02 | 0.755±0.02  |
| FCOS-101 | 0.755±0.03 | 0.920±0.02 | 0.841±0.02 | 0.756±0.02 | 0.749±0.03  |

The results can be reproduced by using these config files ([FCOS-50](Baseline/FCOS-50.py), [FCOS-101](Baseline/FCOS-101.py)) and the github repo [Yuxiang1995/ICDAR2021_MFD](https://github.com/Yuxiang1995/ICDAR2021_MFD).

## License
This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
## Citation

### FormulaNet: A Benchmark Dataset for Mathematical Formula Detection

Felix M. Schmitt-Koopmann, Elaine M. Huang, Hans-Peter Hutter, Thilo Stadelmann, Alireza Darvishy

[https://ieeexplore.ieee.org/document/9869643](https://ieeexplore.ieee.org/document/9869643)

```
@ARTICLE{9869643,
    author={Schmitt-Koopmann, Felix M. and Huang, Elaine M. and Hutter, Hans-Peter and 
    Stadelmann, Thilo and Darvishy, Alireza},  
    journal={IEEE Access},   
    title={FormulaNet: A Benchmark Dataset for Mathematical Formula Detection},   
    year={2022},  
    volume={10},  
    number={},  
    pages={91588-91596},  
    doi={10.1109/ACCESS.2022.3202639}}
```
