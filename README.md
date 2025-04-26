# SSN Optimization - Environment and Agents

python -m scripts.drafts.driver2.py

## Setting up Virtual Environment

1. `micromamba create -n ssn-v0 -c conda-forge -y python=3.10`

2. `micromamba activate ssn-v0`

the following steps may or may not be necessary:

i. `eval "$(micromamba shell hook --shell zsh)"`

ii. `micromamba install -c conda-forge ipykernel`

3. `pip install -r requirements.txt`



## Notes

- poliastro==0.17.0

- had to uninstall matplotlib and install matplotlib==3.7 for plotting to work 

- wouldn't plot without installing nbformat==5.10.4
