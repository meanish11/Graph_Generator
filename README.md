# Graph_Generator# Excel Data Visualizer

A Django-based web application that allows users to upload Excel files and create dynamic, interactive data visualizations with multi-graph comparison capabilities.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-v4.2.7-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 📋 Features

- **Excel File Upload**: Upload and manage Excel files (.xlsx, .xls)
- **Multi-sheet Support**: Handle Excel files with multiple sheets
- **Dynamic Column Detection**: Automatically detect headers and subheaders
- **Interactive Visualizations**: Create line charts, bar charts, and scatter plots
- **Multiple Graph Comparison**: Compare data from multiple files/sheets on a single graph
- **Export Options**: Export graphs as PDF or JPG
- **User Authentication**: Secure login system for file management
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Demo

### For Guest Users (View Only)
- Browse and visualize existing Excel files
- Create and export graphs
- Compare multiple datasets

### For Registered Users
- All guest features plus:
- Upload new Excel files
- Delete your uploaded files
- Manage your data

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Visualization**: Plotly.js
- **File Processing**: Pandas, Openpyxl

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/excel-data-visualizer.git
cd excel-data-visualizer

Step 2: Create Virtual Environment
Windows:

BASH

python -m venv venv
venv\Scripts\activate


excel_visualizer/
├── excel_visualizer/       # Main Django project directory
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py
├── data_analyzer/         # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # App URL configuration
│   ├── forms.py          # Django forms
│   └── utils.py          # Utility functions
├── templates/            # HTML templates
│   ├── base.html
│   ├── upload.html
│   ├── visualize.html
│   ├── login.html
│   └── signup.html
├── static/              # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── media/               # User uploaded files
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script


1. Uploading Excel Files (Registered Users)
Login to your account
Navigate to "Upload Data"
Select your Excel file and provide a name
Click "Upload"
2. Creating Visualizations
Go to "Graph Plot"
Select an Excel file from the dropdown
Choose a sheet
Select X-axis parameter (from first column subcolumns)
Select Y-axis parameters (from remaining columns)
Choose graph type (Line/Bar/Scatter)
Click "Plot Graph"
3. Comparing Multiple Graphs
Create your first graph
Click "Add to Comparison"
Select different file/sheet/parameters
Click "Add to Comparison" again
Click "Compare Graphs" to see all graphs overlaid
4. Exporting Graphs
After creating a graph, export options appear
Choose PDF or JPG format
Graph will be downloaded to your device
📝 Excel File Format
The application supports Excel files with:

Multi-level Headers

| Main Header A  | Main Header B  |
|-------|--------|--------|--------|
| Sub1  | Sub2   | Sub3   | Sub4   |
|-------|--------|--------|--------|
| Data  | Data   | Data   | Data   |
Single-level Headers

| Column A | Column B | Column C |
|----------|----------|----------|
| Data     | Data     | Data     |
⚙️ Configuration
Database Configuration (Production)
For PostgreSQL, update settings.py:

Python

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
File Upload Limits
In settings.py:

Python

# Maximum file size (50MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
🐛 Troubleshooting
Common Issues
"No such table" error

BASH

python manage.py migrate
python manage.py makemigrations data_analyzer
python manage.py migrate data_analyzer
Static files not loading

BASH

python manage.py collectstatic
Excel file reading errors

Ensure your Excel file has proper headers
Check for merged cells in headers
Verify file is not corrupted
Export not working

Install kaleido: pip install kaleido
Check Plotly version compatibility
🤝 Contributing
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Authors
Your Name - GitHub Profile
🙏 Acknowledgments
Django Documentation
Plotly.js for amazing visualization capabilities
Bootstrap for responsive UI components
Pandas for Excel file processing
📞 Support
For support, email your-email@example.com or create an issue in the GitHub repository.

Made with ❤️ by [Your Name]


Collapse

This README includes:

1. **Clear project description**
2. **Feature list**
3. **Installation instructions**
4. **Usage guide**
5. **Project structure**
6. **Configuration options**
7. **Troubleshooting section**
8. **Contributing guidelines**
9. **License information**

You should customize:
- Replace `yourusername` with your GitHub username
- Add your actual email for support
- Add screenshots if available
- Update the license type if different
- Add any specific requirements or notes about your implementation