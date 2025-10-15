# PyDeX
PyDeX is a minimal web crawler written in Python. It can be used for finding hidden pages in websites, and quickly indexing small sites.

<img width="660" height="452" alt="image" src="https://github.com/user-attachments/assets/601d7ffc-6ece-41a6-8f2a-afe3314735b3" />

## Running PyDeX
To run PyDeX, I reccomend the Python Visual Studio Code Plugin. You'll need a installation of Python 3.13, and a couple of pip packages.
To install the dependencies, run the command below:
```
pip install flask beautifulsoup4 requests
```

Then, clone the github repository and open main.py in Visual Studio Code, which is located in the PyDeX folder.
From there, you can hit the run button, and it will start the web interface through Flask. Once the server has started, you can access the web interface at http://localhost:80/.

## Usage
To interact with PyDeX, you will probably be using the web interface provided by Flask. Open http://localhost:80/ in your browser (Not https!) once the Flask server has started. Then, click on the Control Panel tab to interact with PyDeX.
Once you have created an index, you can search that index by clicking on the PyDeX logo to return to the home screen and using the search bar.

<img width="799" height="578" alt="image" src="https://github.com/user-attachments/assets/7ba21098-4998-4b6f-8f28-7d93f999a0d7" />
