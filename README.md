# PyDeX
PyDeX is a minimal search engine and web crawler written in Python. It can be used for quickly indexing small websites and searching through that index, and has a web interface powered by Flask.

<img width="660" height="452" alt="image" src="https://github.com/user-attachments/assets/601d7ffc-6ece-41a6-8f2a-afe3314735b3" />

## Running PyDeX
To run PyDeX, I reccomend the Python Visual Studio Code Plugin. You'll need a installation of Python 3.13, and a couple of pip packages.
To install the dependencies, run the command below:
```
pip install flask beautifulsoup4 requests
```

Then, clone the github repository and open main.py in Visual Studio Code, which is located in the PyDeX folder.
From there, you can hit the run button, and interact with PyDeX through the Visual Studio Code Terminal. You'll be guided through setting up an instance of PyDeX in a CLI.

Once setup is complete, it will automatically try to start a Flask server to host the web interface, which is what you'll use to interact with PyDeX.
You'll be able to access the web interface through http://localhost:80/ when the server is up.
