# Reframe report generator

A python script to generate performance reports for reframe json outputs, to be used when making changes to a system.

# Usage

Run with 

```bash
python generate_report my_report.json
```

Available options can be obtained with the command `python generate_report -h`.

In order to generate a report in markdown comparing the performance of three different reports in a markdown file called `report.md` one ca use

```bash
python generate_report.py --compare --aggregate --type=performance --format=markdown report1.json  report2.json report3.json > report.md
```

## Usage on Archer2

On first usage, install with 

```bash
bash install.sh
```

You can setup the environment from the root directory by sodurcing the environment setup script.

```bash
source env.sh
```