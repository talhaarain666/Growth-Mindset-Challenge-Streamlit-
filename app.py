import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Setting App
st.set_page_config(page_title="Data sweeper",layout="wide")
st.title("Data sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")
uploaded_files = st.file_uploader("Upload Your Files (CSV / Excel):",type=["csv","xlsx"],accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()

        if file_extension == ".csv":
            data_frame = pd.read_csv(file, encoding="utf-8")
        elif file_extension == ".xlsx":
            data_frame = pd.read_excel(file, engine="openpyxl")
        else: 
            st.error(f"Unsupported File Type: {file_extension}")
            continue

        # File Info
        st.write(f"**File Name**:{file.name}")
        st.write(f"**File Size:** {file.size/1024}")

        # Showing 5 Rows of Dataframe
        st.write("Preview of the Head of Dataframe")
        st.dataframe(data_frame.head())

        # Options for data cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    data_frame.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = data_frame.select_dtypes(include=['number']).columns
                    data_frame[numeric_cols]= data_frame[numeric_cols].fillna(data_frame[numeric_cols].mean())
                    st.write("Missing Values have been Filled!")

        # Choosing Specific Columns to keep or convert
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}",data_frame.columns,default=data_frame.columns)
        data_frame= data_frame[columns]

        # Creating Visualization
        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(data_frame.select_dtypes(include='number').iloc[:,:2])

        # Convert File (CSV -> Excel)
        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:",["CSV","Excel"],key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                data_frame.to_csv(buffer, index=False, encoding="utf-8")
                file_name = os.path.splitext(file.name)[0] + ".csv"
                mime_type = "text/csv"
                
            elif conversion_type == "Excel":
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    data_frame.to_excel(writer, index=False)
                file_name = os.path.splitext(file.name)[0] + ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # Download File
            st.download_button(
                label=f"Download {file_name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("All Files Processed!")