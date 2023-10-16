# main-challenge

## Introduction

Repo for main challenge of 2020 blockchain course at Physics Dep. UniMi

> **Goal:** interact and challenge other teams inside a Multi Tokens Exchange deployed on ropsten network (respecting rules)

## Getting started

### Prerequisites

To use these repo the following requirements must be satisfied:

 - `Python > 3.7`
 - `solc == 0.5.17` (installed automatically by brownie)
 
and approximately the version of these packages:

 - `environments.yml` python pkgs (and bins) for conda env or `requirements.txt` for only PyPI pkgs 
 - `nodejs-pkg.txt` nodejs pkgs, pratically only `ganache-cli` for testing purpose
 
 also external smart contracts are used, as specified in depencencies inside `brownie-config.yaml`
 
 ### Structure
 
 Same structure of a brownie project (for now):
 
 ```
.
├── contracts         # source contracts
│   ├── Example.sol
│   └── ...
├── pyscripts         # scripts that can be run: python <path to script>
│   ├── example.py
│   └── ...
├── scripts           # scripts that can be run: brownie run <path to script>
│   ├── example.py
│   └── ...
│ 
 
 ```
 
 ### Setup
 
 After install [Prerequisites](#prerequisites) you're ready to setup your git repo, clone it:
 
 ```
 git clone https://github.com/AMPM-ORG/main-challenge
 ```

 Create missing brownie project directories:
 
 ```
 cd main-challenge
 mkdir {build,interfaces,reports,tests}
 ```
 Now you can compile `contracts` contained in the master branch of the repo:
 
 ```
 brownie compile
 ```
 
 > **Note:** If there isn't a solc compiler (or there is compiler with wrong version) brownie installs it for you and also if there aren't external contracts locally (e.g. Openzeppellin contracts) brownie installs them for you, using built-in package manager. And then compiles all.
 
 
