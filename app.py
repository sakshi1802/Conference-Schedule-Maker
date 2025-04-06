import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Web App Title
st.title("Conference Scheduler Maker")

# Upload Excel File
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Define required columns
    required_columns = ['Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"Missing columns in uploaded file: {missing_cols}")
    else:
        # Ask user for session details
        slot_duration = st.number_input("Duration per presentation (minutes):", 
                                      min_value=5, max_value=60, value=15)
        max_presentations = st.number_input("Max presentations per session:", 
                                          min_value=3, max_value=10, value=5)
        
        # Ask for number of sections
        num_sections = st.number_input("Number of sections:", min_value=1, max_value=3, value=2)
        
        # Collect section time ranges
        sections = []
        for i in range(num_sections):
            st.subheader(f"Section {i+1} Time Range")
            col1, col2 = st.columns(2)
            with col1:
                start = st.time_input(f"Start time:", key=f"start_{i}",
                                    value=datetime.strptime("2:45 PM", "%I:%M %p").time() if i == 0 else 
                                    datetime.strptime("4:30 PM", "%I:%M %p").time())
            with col2:
                end = st.time_input(f"End time:", key=f"end_{i}",
                                  value=datetime.strptime("2:00 AM", "%I:%M %p").time() if i == 0 else 
                                  datetime.strptime("6:00 PM", "%I:%M %p").time())
            
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
            # 1. Sort by theme first
            df = df.sort_values(by="Theme")
            
            # 2. Split dataframe into roughly equal sections
            total_presentations = len(df)
            split_indices = np.linspace(0, total_presentations, num_sections+1, dtype=int)
            section_dfs = []
            for i in range(num_sections):
                section_dfs.append(df.iloc[split_indices[i]:split_indices[i+1]])
            
            # Initialize columns
            df['Session ID'] = None
            df['Time Slot'] = None
            df['Section'] = None
            
            # 3. Assign sessions and time slots
            session_id = 1
            current_time = [section['start_dt'] for section in sections]
            section_day = [0] * num_sections  # Track days for each section
            
            for section_idx, section_df in enumerate(section_dfs):
                theme_groups = section_df.groupby('Theme')
                
                for theme, theme_df in theme_groups:
                    # Split theme into sessions
                    for i in range(0, len(theme_df), max_presentations):
                        presentation_group = theme_df.iloc[i:i+max_presentations]
                        
                        # Calculate required time
                        required_time = current_time[section_idx] + timedelta(minutes=len(presentation_group)*slot_duration)
                        section_end = datetime.combine(
                            datetime.today() + timedelta(days=section_day[section_idx]), 
                            sections[section_idx]['end']
                        )
                        
                        # Check if we need to move to next day
                        if required_time > section_end:
                            section_day[section_idx] += 1
                            current_time[section_idx] = datetime.combine(
                                datetime.today() + timedelta(days=section_day[section_idx]),
                                sections[section_idx]['start']
                            )
                            required_time = current_time[section_idx] + timedelta(minutes=len(presentation_group)*slot_duration)
                        
                        # Assign time slots
                        time_cursor = current_time[section_idx]
                        for idx in presentation_group.index:
                            df.at[idx, 'Session ID'] = session_id
                            df.at[idx, 'Time Slot'] = time_cursor.strftime("%I:%M %p")
                            df.at[idx, 'Section'] = sections[section_idx]['name']
                            time_cursor += timedelta(minutes=slot_duration)
                        
                        # Update time for next session in this section
                        current_time[section_idx] = time_cursor
                        session_id += 1
            
            # Prepare final output
            final_df = df[['Section', 'Session ID', 'Time Slot', 'Theme', 'Title', 'Presenter(s)', 'Faculty Mentor']]
            
            # Show results
            st.write("📊 **Schedule Preview:**")
            st.dataframe(final_df.head(20))
            
            # Show summary stats
            scheduled = final_df[final_df['Session ID'].notna()]
            st.write(f"Total scheduled: {len(scheduled)} presentations")
            st.write(f"Total sessions created: {session_id-1}")
            
            # Download
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Schedule CSV", csv, "oral_presentation_schedule.csv", "text/csv")