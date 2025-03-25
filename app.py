import streamlit as st
import pandas as pd
from process import clean_excel_data, save_cleaned_data

st.title("Research Conference Schedule Maker 🎓")

# Upload Excel file
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Process the file
    df = clean_excel_data(uploaded_file)

    # Save cleaned data
    output_file = "cleaned_schedule.xlsx"
    save_cleaned_data(df, output_file)

    # Display DataFrame
    st.write("### Cleaned Data Preview:")
    st.dataframe(df)

    # Download button
    with open(output_file, "rb") as file:
        st.download_button(label="Download Cleaned Excel File",
                           data=file,
                           file_name="cleaned_schedule.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
