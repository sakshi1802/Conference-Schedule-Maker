import pandas as pd

def clean_excel_data(input_file):
    # Load the Excel file
    df = pd.read_excel(input_file)

    # Select only required columns
    columns_needed = ["Major", "Number Assigned", "Session Assigned", "Time", 
                      "Presenter Name", "Faculty Mentor Name", "Title"]
    df = df[columns_needed]

    # Sort data by session and time
    df = df.sort_values(by=["Session Assigned", "Time"])

    return df

def save_cleaned_data(df, output_file):
    df.to_excel(output_file, index=False)
