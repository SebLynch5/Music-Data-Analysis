## Music Data Analysis
This project performs interactive analysis on music data between 1998–2020. Using ipywidgets in a Jupyter environment, it enables genre analysis, artist insights, and discovery of top artists across time.

# Contents
`main.ipynb` – Jupyter Notebook with the full interactive interface.

`artist.py, genres.py, top5.py, preprocessing.py` – Python modules supporting each functionality.

`songs.csv` – The core dataset used for analysis.

`MusicDatabase.db` – Created during execution to store and query processed data.

`environment.yml` – Conda environment definition to ensure all dependencies are met.

`desktop.ini` – Configuration file used by the scripts.

# Features
GUI featuring 3 different analysis’.

All components are modular, enabling reuse or extension of logic for future projects.

# Setup Instructions
To run this project locally:

1. Install Conda (if not already installed)
Miniconda: https://docs.conda.io/en/latest/miniconda.html

2. Create the environment
bash
Copy
Edit
conda env create -f environment.yml
conda activate music-analysis
3. Launch Jupyter Notebook
bash
Copy
Edit
jupyter notebook
Open main.ipynb and run all cells.

# Note:
The notebook creates MusicDatabase.db from songs.csv on first run.

# Dependencies
All dependencies are defined in environment.yml, including:

pandas

ipywidgets

matplotlib

sqlite3

jupyterlab or notebook (ensure widgets display properly)

If widgets fail to display, make sure ipywidgets is enabled and correctly installed.

# Notes
Built using Jupyter Notebook, tested via Anaconda on Python 3.10.

If your Jupyter interface does not render widgets, try using JupyterLab 3+ or updating ipywidgets.
