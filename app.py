import streamlit as st
import pandas as pd
import os
import io
import zipfile

st.set_page_config(page_title="File Splitter", layout="wide")
st.title("Worksheet/CSV/TXT Splitter")


st.markdown("""
This app allows you to upload an Excel or CSV file and split the data into multiple groups based on a selected column.
Each group is exported as a CSV file, and all files are compressed into a single ZIP file.
""")

# Allow Excel, CSV, and TXT file formats
uploaded_file = st.file_uploader("Upload an Excel, CSV, or TXT file", type=["xlsx", "xls", "csv", "txt"])

if uploaded_file:
    try:
        # Determine file extension and read file accordingly
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(uploaded_file)
        elif file_ext == ".csv":
            df = pd.read_csv(uploaded_file)
        elif file_ext == ".txt":
            st.info("For TXT files, please select the delimiter used in the file.")
            delimiter = st.selectbox("Select the delimiter", options=[",", "\t", ";", "|"], index=0)
            df = pd.read_csv(uploaded_file, delimiter=delimiter)
        else:
            st.error("Unsupported file type.")
            df = None
        
        if df is not None:
            st.subheader("Data Preview")
            st.dataframe(df.head())

            # Let the user select the column to split by
            split_column = st.selectbox("Select the column to split by", options=df.columns)

            if split_column:
                # Group the DataFrame by the selected column
                groups = df.groupby(split_column)

                # Helper function to create an in-memory ZIP archive of CSV files for each group
                def create_zip_buffer():
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for group_name, group_df in groups:
                            # Sanitize group name for a safe filename
                            safe_name = str(group_name).replace(" ", "_")
                            file_name = f"group_{safe_name}.csv"
                            csv_data = group_df.to_csv(index=False)
                            zip_file.writestr(file_name, csv_data)
                    zip_buffer.seek(0)
                    return zip_buffer

                # Create the ZIP archive and provide the first download button (above groups)
                zip_buffer_above = create_zip_buffer()
                st.download_button(
                    label="Export All Groups as ZIP (Above Groups)",
                    data=zip_buffer_above,
                    file_name="split_groups.zip",
                    mime="application/zip"
                )

                st.subheader(f"Data split by '{split_column}'")
                # Display each group
                for group_name, group_df in groups:
                    st.markdown(f"### Group: {group_name}")
                    st.dataframe(group_df)

                # Recreate the ZIP archive for the second download button (below groups)
                zip_buffer_below = create_zip_buffer()
                st.download_button(
                    label="Export All Groups as ZIP (Below Groups)",
                    data=zip_buffer_below,
                    file_name="split_groups.zip",
                    mime="application/zip"
                )
    except Exception as e:
        st.error(f"Error processing the file: {e}")
else:
    st.info("Please upload an Excel, CSV, or TXT file to get started.")