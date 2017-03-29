# ∆Breakpad

## Requirements & Installation
To execute the scripts in this repository we require:
- Python 3.3
- Python modules: pyexcel pyexcel-ods3

Repositories:
- breakpad
- Diablo
- Diablo toolchains
- Diablo regression

## Configuration
The configuration can be done in the config.py file. The things that can be set here are certain parameters for the protections and testing environment, and the paths to repositories and tools that are required.

## Recreating tests
To recreate the tests, run the scripts in this order:
- setup.py: Does some general setup such as creating helper tools and generating seeds.
- setup_sp.py: Build the binaries with stack padding.
- setup_fs.py: Protect the binaries with function shuffling.
- setup_nop.py: Protect the binaries with NOP insertion.
- extract_data.py: Extract all the data (symfiles and others) that is required to generate the patches.
- create_patches.py: Creates the patches for all binaries and different combinations of protections. The patches are immediately tested for correctness.
- create_report.py: Creates a report (ODS format) from the patches.
