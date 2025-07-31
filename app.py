import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Conference Schedule Maker", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        
        .stRadio>div>label {
            color: white;
        }
        .stDataFrame {
            background-color: #1e1e1e;
            color: white;
        }
        .stSelectbox>div>label {
            color: white;
        }
        .stNumberInput>div>label {
            color: white;
        }
        h1 {
            text-align: center;
            margin-bottom: 50px;
        }
        .column-spacing {
            padding-left: 70px;
            padding-right: 70px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Conference Schedule Maker</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

col1.markdown('<div class="column-spacing"></div>', unsafe_allow_html=True)
col2.markdown('<div class="column-spacing"></div>', unsafe_allow_html=True)

with col1:
    st.markdown("""
    **Welcome to the Conference Schedule Maker!**  
    Please follow the instructions below to ensure smooth processing of your schedule:

    #### Required Columns in the Excel File:
    Your Excel file must include **exactly** the following columns, spelled as shown (case-sensitive) and located in the first row:
    - **Theme**
    - **Title**
    - **Presenter(s)**
    - **Faculty Mentor**

    #### Column Descriptions:
    - **Theme**: Category or department (e.g., Arts, Biology, Computer Science)
    - **Title**: Title of the presentation
    - **Presenter(s)**: The name(s) of the presenter(s), separated by commas if there are multiple presenters
    - **Faculty Mentor**: The name(s) of the faculty mentor(s)

    """)

with col2:
    # Upload Excel File
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    # Read Excel File
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        # Define required columns
        required_columns = ['Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"Missing columns in uploaded file: {missing_cols}")
        else:
            session_type = st.radio("Choose Session Type:", ["Oral Session Maker", "Poster Session Maker"])

            # Oral Session Maker
            if session_type == "Oral Session Maker":
                # Ask user for session details
                slot_duration = st.number_input("Duration per presentation (minutes):", 
                                              min_value=5, max_value=20, value=15)
                max_presentations = st.number_input("Max presentations per session:", 
                                                  min_value=3, max_value=10, value=4)

                # Ask for number of sections
                num_sections = st.number_input("Number of sections(or no. of oral sessions throughout the day):", min_value=1, max_value=3, value=2)

                # Collect section time ranges
                sections = []
                for i in range(num_sections):
                    st.subheader(f"Section {i+1} Time Range")
                    col1, col2 = st.columns(2)
                    with col1:
                        start = st.time_input(f"Start time:", key=f"start_{i}",
                                            value=datetime.strptime("10:00 AM", "%I:%M %p").time() if i == 0 else 
                                            datetime.strptime("2:00 pM", "%I:%M %p").time())
                    with col2:
                        end = st.time_input(f"End time:", key=f"end_{i}",
                                          value=datetime.strptime("11:00 AM", "%I:%M %p").time() if i == 0 else 
                                          datetime.strptime("3:00 PM", "%I:%M %p").time())

                    sections.append({
                        'name': f"Section {i+1}",
                        'start': start,
                        'end': end,
                        'start_dt': datetime.combine(datetime.today(), start),
                        'end_dt': datetime.combine(
                            datetime.today() + timedelta(days=1) if end < start else datetime.today(), 
                            end
                        )
                    })

                if st.button("Generate Schedule"):
                    df = df.sort_values(by="Theme")
                    total_presentations = len(df)
                    split_indices = np.linspace(0, total_presentations, num_sections+1, dtype=int)
                    section_dfs = []
                    for i in range(num_sections):
                        section_dfs.append(df.iloc[split_indices[i]:split_indices[i+1]])

                    df['Session ID'] = None
                    df['Time Slot'] = None
                    df['Section'] = None

                    session_id = 1
                    current_time = [section['start_dt'] for section in sections]
                    section_day = [0] * num_sections

                    for section_idx, section_df in enumerate(section_dfs):
                        # Step 1: Re-categorize themes based on presentation count threshold
                        theme_counts = section_df['Theme'].value_counts()
                        large_themes = theme_counts[theme_counts >= max_presentations].index.tolist()
                        small_themes = theme_counts[theme_counts < max_presentations].index.tolist()

                        # Separate into two dataframes
                        large_theme_df = section_df[section_df['Theme'].isin(large_themes)].copy()
                        small_theme_df = section_df[section_df['Theme'].isin(small_themes)].copy()

                        # Step 2: Group large themes individually
                        theme_groups = []
                        for theme, group_df in large_theme_df.groupby('Theme'):
                            theme_groups.append(group_df)

                        # Step 3: Mix and merge small themes while respecting max_presentations per session
                        small_theme_df = small_theme_df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle to mix
                        for i in range(0, len(small_theme_df), max_presentations):
                            chunk = small_theme_df.iloc[i:i+max_presentations]
                            theme_groups.append(chunk)


                            for presentation_group in theme_groups:
                                required_time = current_time[section_idx] + timedelta(minutes=len(presentation_group)*slot_duration)
                                section_end = datetime.combine(
                                    datetime.today() + timedelta(days=section_day[section_idx]), 
                                    sections[section_idx]['end']
                                )

                                if required_time > section_end:
                                    section_day[section_idx] += 1
                                    current_time[section_idx] = datetime.combine(
                                        datetime.today() + timedelta(days=section_day[section_idx]),
                                        sections[section_idx]['start']
                                    )
                                    required_time = current_time[section_idx] + timedelta(minutes=len(presentation_group)*slot_duration)

                                time_cursor = current_time[section_idx]
                                for idx in presentation_group.index:
                                    df.at[idx, 'Session ID'] = session_id
                                    df.at[idx, 'Time Slot'] = time_cursor.strftime("%I:%M %p")
                                    df.at[idx, 'Section'] = sections[section_idx]['name']
                                    time_cursor += timedelta(minutes=slot_duration)

                                current_time[section_idx] = time_cursor
                                session_id += 1

                    final_df = df[['Section', 'Session ID', 'Time Slot', 'Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']]
                    st.write("**Oral Schedule Preview:**")
                    st.dataframe(final_df.head(20))
                    scheduled = final_df[final_df['Session ID'].notna()]
                    st.write(f"Total scheduled: {len(scheduled)} presentations")
                    st.write(f"Total sessions created: {session_id-1}")

                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Oral Schedule CSV", csv, "oral_presentation_schedule.csv", "text/csv")
                # Poster Session Maker
            elif session_type == "Poster Session Maker":
                # Ask for number of sections  
                num_sections = st.number_input("Number of poster sections(or no. of poster sessions throughout the day) :", min_value=1, max_value=5, value=2)

                # Collect section time ranges
                poster_sections = []
                for i in range(num_sections):
                    st.subheader(f"Poster Section {i+1} Time Range")
                    col1, col2 = st.columns(2)
                    with col1:
                        start = st.time_input(f"Start Time:", key=f"poster_start_{i}",
                                            value=datetime.strptime("10:00 AM", "%I:%M %p").time()  if i == 0 else 
                                            datetime.strptime("1:00 PM", "%I:%M %p").time())
                    with col2:
                        end = st.time_input(f"End Time:", key=f"poster_end_{i}",
                                          value=datetime.strptime("11:30 AM", "%I:%M %p").time() if i == 0 else 
                                           datetime.strptime("2:30 PM", "%I:%M %p").time())
                    poster_sections.append({
                        'name': f"Poster Section {i+1}", 
                        'start': start,
                        'end': end,
                        'start_dt': datetime.combine(datetime.today(), start),
                        'end_dt': datetime.combine(
                            datetime.today() + timedelta(days=1) if end < start else datetime.today(), 
                            end
                        )
                    })

                if st.button("Generate Poster Schedule"):
                    
                    df = df.sort_values(by="Theme")
                   
                    total_presentations = len(df)
                    split_indices = np.linspace(0, total_presentations, num_sections+1, dtype=int)
                    poster_groups = []
                    for i in range(num_sections):
                        poster_groups.append(df.iloc[split_indices[i]:split_indices[i+1]])

                    df['Session ID'] = None
                    df['Time Slot'] = None
                    df['Section'] = None

                    for idx, group in enumerate(poster_groups):
                        start_time = poster_sections[idx]['start_dt']
                        end_time = poster_sections[idx]['end_dt']
                        time_cursor = start_time
                        session_id = 1
                        for i in range(len(group)):
                            if time_cursor >= end_time:
                                time_cursor = start_time + timedelta(days=1)

                            df.at[group.index[i], 'Session ID'] = session_id
                            df.at[group.index[i], 'Time Slot'] = time_cursor.strftime("%I:%M %p")
                            df.at[group.index[i], 'Section'] = poster_sections[idx]['name']
                            time_cursor += timedelta(minutes=10)  # Poster session fixed to 10 mins per poster
                            session_id += 1

                    final_df = df[['Section', 'Session ID', 'Time Slot', 'Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']]
                    st.write("**Poster Schedule Preview:**")
                    st.dataframe(final_df.head(20))
                    scheduled = final_df[final_df['Session ID'].notna()]
                    st.write(f"Total scheduled: {len(scheduled)} posters")
                    st.write(f"Total sessions created: {session_id-1}")

                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Poster Schedule CSV", csv, "poster_presentation_schedule.csv", "text/csv")

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Conference Schedule Maker", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        
        .stRadio>div>label {
            color: white;
        }
        .stDataFrame {
            background-color: #1e1e1e;
            color: white;
        }
        .stSelectbox>div>label {
            color: white;
        }
        .stNumberInput>div>label {
            color: white;
        }
        h1 {
            text-align: center;
            margin-bottom: 50px;
        }
        .column-spacing {
            padding-left: 70px;
            padding-right: 70px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Conference Schedule Maker</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

col1.markdown('<div class="column-spacing"></div>', unsafe_allow_html=True)
col2.markdown('<div class="column-spacing"></div>', unsafe_allow_html=True)

with col1:
    st.markdown("""
    **Welcome to the Conference Schedule Maker!**  
    Please follow the instructions below to ensure smooth processing of your schedule:

    #### Required Columns in the Excel File:
    Your Excel file must include **exactly** the following columns, spelled as shown (case-sensitive) and located in the first row:
    - **Theme**
    - **Title**
    - **Presenter(s)**
    - **Faculty Mentor**

    #### Column Descriptions:
    - **Theme**: Category or department (e.g., Arts, Biology, Computer Science)
    - **Title**: Title of the presentation
    - **Presenter(s)**: The name(s) of the presenter(s), separated by commas if there are multiple presenters
    - **Faculty Mentor**: The name(s) of the faculty mentor(s)

    """)

with col2:
    # Upload Excel File
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    # Read Excel File
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        # Define required columns
        required_columns = ['Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"Missing columns in uploaded file: {missing_cols}")
        else:
            session_type = st.radio("Choose Session Type:", ["Oral Session Maker", "Poster Session Maker"])

            # Oral Session Maker
            if session_type == "Oral Session Maker":
                # Ask user for session details
                slot_duration = st.number_input("Duration per presentation (minutes):", 
                                              min_value=5, max_value=20, value=15)
                max_presentations = st.number_input("Max presentations per session:", 
                                                  min_value=3, max_value=10, value=4)

                # Ask for number of sections
                num_sections = st.number_input("Number of sections(or no. of oral sessions throughout the day):", min_value=1, max_value=3, value=2)

                # Collect section time ranges
                sections = []
                for i in range(num_sections):
                    st.subheader(f"Section {i+1} Time Range")
                    col1, col2 = st.columns(2)
                    with col1:
                        start = st.time_input(f"Start time:", key=f"start_{i}",
                                            value=datetime.strptime("10:00 AM", "%I:%M %p").time() if i == 0 else 
                                            datetime.strptime("2:00 pM", "%I:%M %p").time())
                    with col2:
                        end = st.time_input(f"End time:", key=f"end_{i}",
                                          value=datetime.strptime("11:00 AM", "%I:%M %p").time() if i == 0 else 
                                          datetime.strptime("3:00 PM", "%I:%M %p").time())

                    sections.append({
                        'name': f"Section {i+1}",
                        'start': start,
                        'end': end,
                        'start_dt': datetime.combine(datetime.today(), start),
                        'end_dt': datetime.combine(
                            datetime.today() + timedelta(days=1) if end < start else datetime.today(), 
                            end
                        )
                    })

                if st.button("Generate Schedule"):
                    df = df.sort_values(by="Theme")
                    total_presentations = len(df)
                    split_indices = np.linspace(0, total_presentations, num_sections+1, dtype=int)
                    section_dfs = []
                    for i in range(num_sections):
                        section_dfs.append(df.iloc[split_indices[i]:split_indices[i+1]])

                    df['Session ID'] = None
                    df['Time Slot'] = None
                    df['Section'] = None

                    session_id = 1
                    current_time = [section['start_dt'] for section in sections]
                    section_day = [0] * num_sections

                    for section_idx, section_df in enumerate(section_dfs):
                        theme_groups = section_df.groupby('Theme')

                        for theme, theme_df in theme_groups:
                            for i in range(0, len(theme_df), max_presentations):
                                presentation_group = theme_df.iloc[i:i+max_presentations]
                                required_time = current_time[section_idx] + timedelta(minutes=len(presentation_group)*slot_duration)
                                section_end = datetime.combine(
                                    datetime.today() + timedelta(days=section_day[section_idx]), 
                                    sections[section_idx]['end']
                                )

                                if required_time > section_end:
                                    section_day[section_idx] += 1
                                    current_time[section_idx] = datetime.combine(
                                        datetime.today() + timedelta(days=section_day[section_idx]),
                                        sections[section_idx]['start']
                                    )
                                    required_time = current_time[section_idx] + timedelta(minutes=len(presentation_group)*slot_duration)

                                time_cursor = current_time[section_idx]
                                for idx in presentation_group.index:
                                    df.at[idx, 'Session ID'] = session_id
                                    df.at[idx, 'Time Slot'] = time_cursor.strftime("%I:%M %p")
                                    df.at[idx, 'Section'] = sections[section_idx]['name']
                                    time_cursor += timedelta(minutes=slot_duration)

                                current_time[section_idx] = time_cursor
                                session_id += 1

                    final_df = df[['Section', 'Session ID', 'Time Slot', 'Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']]
                    st.write("**Oral Schedule Preview:**")
                    st.dataframe(final_df.head(20))
                    scheduled = final_df[final_df['Session ID'].notna()]
                    st.write(f"Total scheduled: {len(scheduled)} presentations")
                    st.write(f"Total sessions created: {session_id-1}")

                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Oral Schedule CSV", csv, "oral_presentation_schedule.csv", "text/csv")
                # Poster Session Maker
            elif session_type == "Poster Session Maker":
                # Ask for number of sections  
                num_sections = st.number_input("Number of poster sections(or no. of poster sessions throughout the day) :", min_value=1, max_value=5, value=2)

                # Collect section time ranges
                poster_sections = []
                for i in range(num_sections):
                    st.subheader(f"Poster Section {i+1} Time Range")
                    col1, col2 = st.columns(2)
                    with col1:
                        start = st.time_input(f"Start Time:", key=f"poster_start_{i}",
                                            value=datetime.strptime("10:00 AM", "%I:%M %p").time()  if i == 0 else 
                                            datetime.strptime("1:00 PM", "%I:%M %p").time())
                    with col2:
                        end = st.time_input(f"End Time:", key=f"poster_end_{i}",
                                          value=datetime.strptime("11:30 AM", "%I:%M %p").time() if i == 0 else 
                                           datetime.strptime("2:30 PM", "%I:%M %p").time())
                    poster_sections.append({
                        'name': f"Poster Section {i+1}", 
                        'start': start,
                        'end': end,
                        'start_dt': datetime.combine(datetime.today(), start),
                        'end_dt': datetime.combine(
                            datetime.today() + timedelta(days=1) if end < start else datetime.today(), 
                            end
                        )
                    })

                if st.button("Generate Poster Schedule"):
                    
                    df = df.sort_values(by="Theme")
                   
                    total_presentations = len(df)
                    split_indices = np.linspace(0, total_presentations, num_sections+1, dtype=int)
                    poster_groups = []
                    for i in range(num_sections):
                        poster_groups.append(df.iloc[split_indices[i]:split_indices[i+1]])

                    df['Session ID'] = None
                    df['Time Slot'] = None
                    df['Section'] = None

                    for idx, group in enumerate(poster_groups):
                        start_time = poster_sections[idx]['start_dt']
                        end_time = poster_sections[idx]['end_dt']
                        time_cursor = start_time
                        session_id = 1
                        for i in range(len(group)):
                            if time_cursor >= end_time:
                                time_cursor = start_time + timedelta(days=1)

                            df.at[group.index[i], 'Session ID'] = session_id
                            df.at[group.index[i], 'Time Slot'] = time_cursor.strftime("%I:%M %p")
                            df.at[group.index[i], 'Section'] = poster_sections[idx]['name']
                            time_cursor += timedelta(minutes=10)  # Poster session fixed to 10 mins per poster
                            session_id += 1

                    final_df = df[['Section', 'Session ID', 'Time Slot', 'Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']]
                    st.write("**Poster Schedule Preview:**")
                    st.dataframe(final_df.head(20))
                    scheduled = final_df[final_df['Session ID'].notna()]
                    st.write(f"Total scheduled: {len(scheduled)} posters")
                    st.write(f"Total sessions created: {session_id-1}")

                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Poster Schedule CSV", csv, "poster_presentation_schedule.csv", "text/csv")
