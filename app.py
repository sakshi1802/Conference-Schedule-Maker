import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Web App Title
st.title("Excel Data Cleaner & Session Assigner")
st.write("Upload an Excel file, specify session details, and get a cleaned, session-assigned file!")

# Upload Excel File
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Define required columns
    required_columns = ['Major', 'Presenters', 'Faculty Mentor', 'Title']
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"Missing columns in uploaded file: {missing_cols}")
    else:
        # Select session type
        session_type = st.radio("Select Session Type:", ["Oral Session", "Poster Session"])

        if session_type == "Oral Session":
            # Inputs for Oral Session
            start_time = st.time_input("Enter start time for first presentation:", value=datetime.strptime("09:00 AM", "%I:%M %p").time())
            presentations_per_session = st.number_input("Presentations per session:", min_value=1, max_value=20, value=5)
            time_gap = st.number_input("Time gap between presentations (minutes):", min_value=5, max_value=60, value=15)

            if st.button("Generate Oral Sessions"):
                # Convert start time to datetime
                current_time = datetime.combine(datetime.today(), start_time)
                session_number = 1
                df['Session'] = None
                df['Time Assigned'] = None

                # Assign sessions and times
                for index, row in df.iterrows():
                    if index % presentations_per_session == 0 and index != 0:
                        session_number += 1  # Move to next session

                    df.at[index, 'Session'] = session_number
                    df.at[index, 'Time Assigned'] = current_time.strftime("%I:%M %p")

                    # Increment time for next presentation
                    current_time += timedelta(minutes=time_gap)

                # Reorder columns
                final_df = df[['Major', 'Number Assigned', 'Time Assigned', 'Session', 'Presenter Name', 'Faculty Mentor Name', 'Title']]

                # Show preview
                st.write("📊 **Preview of Cleaned CSV:**")
                st.dataframe(final_df.head(10))  # Show first 10 rows

                # Convert dataframe to CSV
                csv = final_df.to_csv(index=False).encode('utf-8')

                # Download cleaned file
                st.download_button("⬇️ Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv")

        elif session_type == "Poster Session":
            # Dynamic poster session input
            num_sessions = st.number_input("Number of Poster Sessions:", min_value=1, value=2)
            session_details = []

            for i in range(num_sessions):
                st.write(f"**Session {i+1} Details:**")
                session_start = st.time_input(f"Start time for Poster Session {i+1}:", value=datetime.strptime("12:00 PM", "%I:%M %p").time())
                poster_count = st.number_input(f"Number of posters in Session {i+1}:", min_value=1, max_value=200, value=50)
                session_details.append((session_start, poster_count))

            if st.button("Generate Poster Sessions"):
                session_number = 1
                df['Session'] = None
                df['Time Assigned'] = None
                index = 0

                # Assign posters to sessions
                for session_start, poster_count in session_details:
                    current_time = datetime.combine(datetime.today(), session_start)

                    for _ in range(poster_count):
                        if index >= len(df):
                            break
                        df.at[index, 'Session'] = session_number
                        df.at[index, 'Time Assigned'] = current_time.strftime("%I:%M %p")
                        index += 1

                    session_number += 1  # Move to next session

                # Reorder columns
                final_df = df[['Major', 'Number Assigned', 'Time Assigned', 'Session', 'Presenter Name', 'Faculty Mentor Name', 'Title']]

                # Show preview
                st.write("📊 **Preview of Cleaned CSV:**")
                st.dataframe(final_df.head(10))  # Show first 10 rows

                # Convert dataframe to CSV
                csv = final_df.to_csv(index=False).encode('utf-8')

                # Download cleaned file
                st.download_button("⬇️ Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv")
