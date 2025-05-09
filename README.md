# Conference Schedule Maker

### Deployed on Streamlit - https://conference-schedule-maker-app-git-mabxnjmbagengxvdttnhfg.streamlit.app/ 

## Overview
The **Conference Schedule Maker** is a web application developed using Streamlit and Python to assist in generating schedules for academic conferences. The tool allows organizers to upload an Excel file containing presentation details, and based on the provided data, it automatically generates and organizes session schedules for both oral and poster presentations.

## Features
- **Excel File Upload**: Users can upload an Excel file with columns for *Theme*, *Title*, *Presenter(s)*, and *Faculty Mentor*.
  
- **Session Type Selection**: Choose between *Oral Session Maker* or *Poster Session Maker*.
  
- **Customizable Sessions**: Define session durations, maximum presentations per session, and the number of sections (sessions) in a day.
  
- **Automatic Schedule Generation**: The tool sorts presentations by theme, splits them across sections, and assigns time slots based on user inputs.
  
- **Schedule Preview**: View a formatted preview of the generated schedule directly within the app before downloading.
  
- **Downloadable Schedules**: After generating the schedule, users can download it in CSV format.

## Requirements
- Python 3.7 or higher
- Required Libraries:
  - `streamlit`
  - `pandas`
  - `numpy`
  - `openpyxl`
    
## Sample Data
A **sample_file_conference_schedule_maker** is provided in the repository to test the app and understand the required format. 
Use this file to:
- See how the schedule maker works.
- Ensure your input file has correctly formatted column headers.

**Required Column Headers (case-sensitive):**
- Theme
- Title
- Presenter(s)
- Faculty Mentor
  
## How to Use Locally
1. **Clone the repository** or download the code.
2. Install the required dependencies:
   -`pip install -r requirements.txt`
3. Run the Streamlit app locally:
   -`streamlit run app.py`
4. Open your browser and navigate to `http://localhost:8501` to view the app.
