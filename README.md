Credit Card Statement Parser

This project helps you parse credit card statements in PDF format. You can use it in two ways:

Via the HTML interface (no installation needed)

Via the command line (requires Python)

Getting Started
1. Run Using index.html (Graphical Interface)
Step 1: Download or clone this repository to your local machine.

Step 2: Open the folder where you saved the repository.

Step 3: Double-click on the index.html file.

This will open the parser UI in your default web browser.

<img width="1914" height="914" alt="Screenshot 2025-10-15 232846" src="https://github.com/user-attachments/assets/d0f64d08-d281-42b7-bfd5-f00d039bd1c9" />

Follow the on-screen instructions to upload and parse your credit card statements.
<img width="1919" height="912" alt="Screenshot 2025-10-15 232920" src="https://github.com/user-attachments/assets/bce45edd-b3af-40e1-ac02-5fcd4de212a2" />
step 4: download the cvs file and open in excel
<img width="1919" height="1019" alt="Screenshot 2025-10-15 233006" src="https://github.com/user-attachments/assets/7f7aa219-925a-451f-9651-0c6623ee50d7" />

2. Run Using Command Prompt (Python Script)
Requirements
Python 3.x installed on your system

Steps
Open a terminal or command prompt.

Navigate to the directory where the repository files are located.

Run the following command (replace the filename with your PDF):

python parse.py

if u want direct result

python parse.py.py <your-statement.pdf>

python parse.py.py SBI.pdf
The script will process your PDF and display or save the results as programmed.

Repository Contents
index.html — Main HTML UI for the project

parse.py.py — Python script to parse credit card statements

Sample statement PDFs: SBI.pdf, HDFC .pdf, ICICI .pdf, AMEX.pdf, AXIS.pdf

LICENSE — Project license

License
This project is licensed under the MIT License.
