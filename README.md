# Resume Parsing using NLP

## 🚀 Overview
This project is a Resume Parsing application built using Natural Language Processing (NLP) techniques. It helps automate resume screening by extracting key details, reducing manual effort in recruitment. It can extract:
- **Candidate Name**
- **Phone Number**
- **Email Address**
- **Extracted Skills**
- **Education Details**

The extracted data is displayed on a simple web interface built using Flask.

## 🎯 Why This Project?
- **Automates resume screening**, saving recruiters time.
- **Ensures accuracy** in extracting crucial details.
- **Can be extended into an AI-powered hiring tool.**

## 🌟 Features
- Supports **PDF and text** file uploads.
- Extracts and displays key resume details in a structured format.
- Deletes uploaded files immediately after processing.
- User-friendly web UI for easy interaction.
- Uses `pdfminer.six` for PDF text extraction.
- Implements regex and NLP techniques for accurate information retrieval.
- **Potential to integrate into ATS (Applicant Tracking Systems).**

## 🛠️ Tech Stack
- **Python** (Core logic and model implementation)
- **Flask** (Web framework for deployment)
- **pdfminer.six** (PDF text extraction)
- **Regex** (Pattern matching for extracting phone numbers, emails, etc.)
- **NLP Libraries** (For skill extraction and text processing)
- **HTML, CSS** (Basic UI for file upload and result display)

## 📷 Demo
![Resume Parsing UI](https://your-demo-screenshot-link.png)
_(Example screenshot of the web interface)_

🎥 **Live Demo** (If hosted): [Click Here](https://resume-parsing-using-nlp-1.onrender.com)

## ⚡ Installation
### Prerequisites
Ensure you have Python installed (>=3.8). Install dependencies using:
```sh
pip install -r requirements.txt
```

### Run the Application
```sh
python app.py
```
This will start a Flask web server. Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

## 🏗️ How It Works
1. Upload a resume file (PDF or text format).
2. The backend processes the document and extracts relevant details.
3. The extracted information is displayed on the web UI.
4. The uploaded file is deleted immediately after processing.

## 📂 File Structure
```
resume-parser/
│── app.py             # Flask application
│── parser.py          # Resume parsing logic
│── templates/
│   ├── index.html     # Web UI template
│── static/
│   ├── styles.css     # CSS for UI
│── requirements.txt   # Required dependencies
│── README.md          # Project documentation
```

## 🚀 Future Improvements
- Enhance skill extraction using Named Entity Recognition (NER).
- Add support for extracting work experience and achievements.
- Implement a database to store parsed resume details.
- Deploy as a cloud-based API.
- Train a machine learning model for better skill classification.

## 🤝 Contributing
Feel free to fork this repository, make enhancements, and submit a pull request!

## 📜 License
This project is licensed under the MIT License.

---
Made with ❤️ by Prathamesh Ugle
