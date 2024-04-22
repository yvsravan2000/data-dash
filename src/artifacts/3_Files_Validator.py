# Import packages and modules | External
import time
import warnings
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

# Import packages and modules | Internal
from validata_package import config as cfg
from validata_package.validation_ops import readDataFrameFromCSV, readDataFrameFromExcel, getDataFrameHash, compareDataFrames, readFile, writeFile, getCurrentDateTimeAsString, getCurrentDayDateTimeAsString

# Function to update cell with mismatch values
def updateMismatchCells(value):
    if(str(value) == "nan" or str(value) == "Source" or str(value) == "Target"):
        return value
    else:
        return f":red{value}"

# Information tab function
def showInformationTabContent() -> None:
    # Show content
    st.markdown("##### 😃 Hey, Welcome!")
    st.write("I am designed to streamline the process of comparing source and target files, ensuring data integrity and accuracy.")
    st.markdown("""How it Works:

1.   Upload Files: Simply upload your source and target files using the provided form below. Our tool supports various file formats, making it easy for you to validate your data regardless of its structure.
2.   Comparison: Once your files are uploaded, our tool will swiftly analyze them, identifying any discrepancies or differences between the source and target data.
3.   Validation Report: After the comparison process is complete, you'll receive a comprehensive validation report detailing the results. This report will highlight any inconsistencies found, allowing you to take necessary actions to rectify them.
                
Tips for Uploading Files:

-   Ensure that your source and target files are in a compatible format.
-   Double-check the files you upload to guarantee accuracy in the validation process.
-   If you have any questions or encounter issues during the process, don't hesitate to reach out to our support team for assistance.
                
Thank you for choosing our Data Validation Tool. Let's ensure your data is accurate and reliable together!

Happy validating! 🚀
""")
    
# Validator tab function
def showValidatorTabContent() -> None:
    with st.container(border=True):
        # List of columns to be dropped
        columns_to_be_dropped_str = st.text_input(label="Columns to Drop :green[(optional)]", placeholder="dcol1[,dcol2,....]")

        # List of key columns
        key_columns_str = st.text_input(label="Key Columns :green[(optional)]", placeholder="kcol1[,kcol2,....]")

        # Create columns section for source and target
        source_container, target_container = st.columns(2)

        # Source container
        with source_container:
            source_data_file = st.file_uploader(label="Choose Source Data File", type=["csv", "xlsx"], accept_multiple_files=False, key="source_data_file")

        # Target container
        with target_container:
            target_data_file = st.file_uploader(label="Choose Source Data File", type=["csv", "xlsx"], accept_multiple_files=False, key="target_data_file")

    # Process inputs
    drop_cols_list = [] if columns_to_be_dropped_str=="" else columns_to_be_dropped_str.split(",")
    key_cols_list = [] if key_columns_str=="" else key_columns_str.split(",")

    # Display source information
    if(source_data_file is not None):
        with st.spinner(text="Loading source data..."):
            with source_container:
                st.divider()
                st.write(f"Source[{source_data_file.name}] - Sample records")
                if(source_data_file.name.endswith(".csv")):
                    source_data = readDataFrameFromCSV(source_data_file)
                elif(source_data_file.name.endswith(".xlsx")):
                    source_data = readDataFrameFromExcel(source_data_file)
                
                # Check for drop columns
                source_data = source_data.drop(drop_cols_list, axis=1)
                st.dataframe(data=source_data.head(5), use_container_width=True, hide_index=True)
        
    # Display target information
    if(target_data_file is not None):
        with st.spinner(text="Loading target data..."):
            with target_container:
                st.divider()
                st.write(f"Target[{target_data_file.name}] - Sample records")
                if(target_data_file.name.endswith(".csv")):
                    target_data = readDataFrameFromCSV(target_data_file)
                elif(target_data_file.name.endswith(".xlsx")):
                    target_data = readDataFrameFromExcel(target_data_file)

                # Check for drop columns
                target_data = target_data.drop(drop_cols_list, axis=1)
                st.dataframe(data=target_data.head(5), use_container_width=True, hide_index=True)

    # Analyze data
    if(source_data_file is None or target_data_file is None):
        pass
    elif(source_data.shape != target_data.shape and key_cols_list==[]):
        st.error("The dimensionality of the source and target data are not matching, please check and try again.")
        st.info("Hint: By giving key column(s) input, this error can be avoided.")
    elif(len(source_data.columns) != len(target_data.columns)):
        st.error("The count of columns from the source and target data are not matching, please check and try again.")
    elif((source_data.dtypes != target_data.dtypes).any()):
        st.error("The data type of columns from the source and target data are not matching, please check and try again.")
    else:
        # Record start time
        comparision_start_time = time.time()

        # Fetch hash result
        hash_result = getDataFrameHash(source_data) == getDataFrameHash(target_data)

        # Validate data
        if(key_cols_list==[]):
            validation_result_df = compareDataFrames(source_data, target_data, list(source_data.columns))
        else:
            validation_result_df = compareDataFrames(source_data, target_data, key_cols_list)

        # Analyze result data
        if(key_cols_list == []): # No key column process
            # Seggregate the valdiation result dataframe
            matching_records_source_df = validation_result_df[validation_result_df['_merge'] == 'both']
            matching_records_target_df = validation_result_df[validation_result_df['_merge'] == 'both']
            source_non_matched_records_df = validation_result_df[validation_result_df['_merge'] == 'left_only']
            target_non_matched_records_df = validation_result_df[validation_result_df['_merge'] == 'right_only']

            # Drop indicator column from data sets
            matching_records_source_df = matching_records_source_df.drop(columns=['_merge'])
            matching_records_target_df = matching_records_target_df.drop(columns=['_merge'])
            source_non_matched_records_df = source_non_matched_records_df.drop(columns=['_merge'])
            target_non_matched_records_df = target_non_matched_records_df.drop(columns=['_merge'])

            # Sort data records to start comparision
            source_non_matched_records_df = source_non_matched_records_df.sort_values(by=source_non_matched_records_df.columns.tolist()).reset_index(drop=True)
            target_non_matched_records_df = target_non_matched_records_df.sort_values(by=target_non_matched_records_df.columns.tolist()).reset_index(drop=True)

            # Adding an index column with values "Source" and "Target" at the first position
            matching_records_source_df.insert(0, 'Data Origin', 'Source')
            matching_records_target_df.insert(0, 'Data Origin', 'Target')
            source_non_matched_records_df.insert(0, 'Data Origin', 'Source')
            target_non_matched_records_df.insert(0, 'Data Origin', 'Target')
            matching_records_source_df = matching_records_source_df.reset_index()
            matching_records_source_df = matching_records_source_df.rename(columns={"index":"Index"})
            matching_records_source_df['Index'] = matching_records_source_df.index + 1
            matching_records_target_df = matching_records_target_df.reset_index()
            matching_records_target_df = matching_records_target_df.rename(columns={"index":"Index"})
            matching_records_target_df['Index'] = matching_records_target_df.index + 1
            source_non_matched_records_df = source_non_matched_records_df.reset_index()
            source_non_matched_records_df = source_non_matched_records_df.rename(columns={"index":"Index"})
            source_non_matched_records_df['Index'] = source_non_matched_records_df.index + len(matching_records_source_df) + 1
            target_non_matched_records_df = target_non_matched_records_df.reset_index()
            target_non_matched_records_df = target_non_matched_records_df.rename(columns={"index":"Index"})
            target_non_matched_records_df['Index'] = target_non_matched_records_df.index + len(matching_records_target_df) + 1

            # Compare key matched records : Mismatches only
            difference_count = len(source_non_matched_records_df.drop(columns=['Data Origin', 'Index']).compare(target_non_matched_records_df.drop(columns=['Data Origin', 'Index']), align_axis=0, keep_shape=False, keep_equal=False))
            
            # Compare key matched records : Mismatched Values
            only_mismatch_records_df = source_non_matched_records_df.compare(target_non_matched_records_df, align_axis=0, keep_shape=True, keep_equal=False).rename(index={'self': "Source", 'other': "Target"}, level=-1)

            # Compare key matched records : All values
            equal_and_mismatch_records_df = source_non_matched_records_df.compare(target_non_matched_records_df, align_axis=0, keep_shape=True, keep_equal=True).rename(index={'self': "Source", 'other': "Target"}, level=-1)

            # Apply the function to each cell in the dataframe
            only_mismatch_records_df = only_mismatch_records_df.applymap(updateMismatchCells)
            differences_df = only_mismatch_records_df.fillna(equal_and_mismatch_records_df)

            # Record end time
            comparision_end_time = time.time()

            # Add mismatches confirmation column to report data
            differences_df.insert(len(list(differences_df.columns)), 'Has Mismatch?', 'Yes')
            matching_records_source_df.insert(len(list(matching_records_source_df.columns)), 'Has Mismatch?', 'No')
            matching_records_target_df.insert(len(list(matching_records_target_df.columns)), 'Has Mismatch?', 'No')

            # Fetch data statistics
            total_source_records = len(source_data)
            total_target_records = len(target_data)
            total_errors = difference_count
            total_differences = difference_count
            total_records_only_in_source = 0
            total_records_only_in_target = 0
            total_time_taken_in_secs = comparision_end_time - comparision_start_time

            # Create report file
            final_differences_df = pd.concat([differences_df, matching_records_source_df, matching_records_target_df])
            differences_html = final_differences_df.to_html(index=False, classes=['table', 'table-striped', 'table-hover'])

            html_page = readFile(cfg.artifacts_path + cfg.raw_report_file_name)
            html_page = html_page.replace('#current_date_and_time#', getCurrentDayDateTimeAsString())
            html_page = html_page.replace('#source_file_name#', source_data_file.name)
            html_page = html_page.replace('#target_file_name#', target_data_file.name)
            html_page = html_page.replace('#total_source_records#', str(total_source_records))
            html_page = html_page.replace('#total_target_records#', str(total_target_records))
            html_page = html_page.replace('#total_errors#', str(total_errors))
            html_page = html_page.replace('#total_differences#', str(total_differences))
            html_page = html_page.replace('#total_records_only_in_source#', str(total_records_only_in_source))
            html_page = html_page.replace('#total_records_only_in_target#', str(total_records_only_in_target))
            html_page = html_page.replace('#differences_df#', differences_html)
            html_page = html_page.replace('#source_only_records_df#', "<p>No data found</p>")
            html_page = html_page.replace('#target_only_records_df#', "<p>No data found</p>")
            html_page = html_page.replace('#total_time_taken_in_mins#', str(round(total_time_taken_in_secs/60, 4)))
            if(total_errors > 0):
                html_page = html_page.replace('#status_class#', "status-component-failed")
                html_page = html_page.replace('#status#', "Comparision Failed")
            else:
                html_page = html_page.replace('#status_class#', "status-component-success")
                html_page = html_page.replace('#status#', "Comparision Successful")
            html_page = html_page.replace('<td>:red', '<td style="background-color: #FF0000; color: white;">')
            # writeFile(html_page, "test.html")
        else: # Has key column process
            # Seggregate the valdiation result dataframe
            key_matched_source_records_df = validation_result_df[validation_result_df['_merge'] == 'both']
            key_matched_target_records_df = validation_result_df[validation_result_df['_merge'] == 'both']
            source_only_records_df = validation_result_df[validation_result_df['_merge'] == 'left_only']
            target_only_records_df = validation_result_df[validation_result_df['_merge'] == 'right_only']

            # Drop indicator and dulpicate columns from data sets
            key_matched_source_records_df = key_matched_source_records_df.drop(columns=['_merge'])
            key_matched_target_records_df = key_matched_target_records_df.drop(columns=['_merge'])
            source_only_records_df = source_only_records_df.drop(columns=['_merge'])
            target_only_records_df = target_only_records_df.drop(columns=['_merge'])

            for column in list(key_matched_source_records_df.columns):
                if(column in key_cols_list):
                    continue
                elif(column.endswith("_source")):
                    new_column_name = str(column)[:-7]
                    key_matched_source_records_df.rename(columns = {column:new_column_name}, inplace = True)
                elif(column.endswith("_target")):
                    key_matched_source_records_df = key_matched_source_records_df.drop(columns=[column])

            for column in list(key_matched_target_records_df.columns):
                if(column in key_cols_list):
                    continue
                elif(column.endswith("_source")):
                    key_matched_target_records_df = key_matched_target_records_df.drop(columns=[column])
                elif(column.endswith("_target")):
                    new_column_name = str(column)[:-7]
                    key_matched_target_records_df.rename(columns = {column:new_column_name}, inplace = True)
            
            for column in list(source_only_records_df.columns):
                if(column in key_cols_list):
                    continue
                elif(column.endswith("_source")):
                    new_column_name = str(column)[:-7]
                    source_only_records_df.rename(columns = {column:new_column_name}, inplace = True)
                elif(column.endswith("_target")):
                    source_only_records_df = source_only_records_df.drop(columns=[column])

            for column in list(target_only_records_df.columns):
                if(column in key_cols_list):
                    continue
                elif(column.endswith("_source")):
                    target_only_records_df = target_only_records_df.drop(columns=[column])
                elif(column.endswith("_target")):
                    new_column_name = str(column)[:-7]
                    target_only_records_df.rename(columns = {column:new_column_name}, inplace = True)
            
            # Replace empty/entirely space cells with NaN
            key_matched_source_records_df = key_matched_source_records_df.replace(r'^\s*$', np.nan, regex=True)
            key_matched_target_records_df = key_matched_target_records_df.replace(r'^\s*$', np.nan, regex=True)

            # Sort data records to start comparision
            key_matched_source_records_df = key_matched_source_records_df.sort_values(by=key_matched_source_records_df.columns.tolist()).reset_index(drop=True)
            key_matched_target_records_df = key_matched_target_records_df.sort_values(by=key_matched_target_records_df.columns.tolist()).reset_index(drop=True)

            # Adding an index column with values "Source" and "Target" at the first position
            key_matched_source_records_df.insert(0, 'Data Origin', 'Source')
            key_matched_target_records_df.insert(0, 'Data Origin', 'Target')
            key_matched_source_records_df = key_matched_source_records_df.reset_index()
            key_matched_source_records_df = key_matched_source_records_df.rename(columns={"index":"Index"})
            key_matched_source_records_df['Index'] = key_matched_source_records_df.index + 1
            key_matched_target_records_df = key_matched_target_records_df.reset_index()
            key_matched_target_records_df = key_matched_target_records_df.rename(columns={"index":"Index"})
            key_matched_target_records_df['Index'] = key_matched_target_records_df.index + 1
            
            # Compare key matched records : Mismatches only
            difference_count = len(key_matched_source_records_df.drop(columns=['Data Origin', 'Index']).compare(key_matched_target_records_df.drop(columns=['Data Origin', 'Index']), align_axis=0, keep_shape=False, keep_equal=False))
            
            # Compare key matched records : Mismatched Values
            only_mismatch_records_df = key_matched_source_records_df.compare(key_matched_target_records_df, align_axis=0, keep_shape=True, keep_equal=False).rename(index={'self': "Source", 'other': "Target"}, level=-1)

            # Compare key matched records : All values
            equal_and_mismatch_records_df = key_matched_source_records_df.compare(key_matched_target_records_df, align_axis=0, keep_shape=True, keep_equal=True).rename(index={'self': "Source", 'other': "Target"}, level=-1)

            # Apply the function to each cell in the dataframe
            only_mismatch_records_df = only_mismatch_records_df.applymap(updateMismatchCells)
            differences_df = only_mismatch_records_df.fillna(equal_and_mismatch_records_df)

            # Add mismatches confirmation column to report data
            # differences_df.insert(len(list(differences_df.columns)), 'Has Mismatch?', 'Yes')

            # Record end time
            comparision_end_time = time.time()

            # Fetch data statistics
            total_source_records = len(source_data)
            total_target_records = len(target_data)
            total_errors = difference_count + len(source_only_records_df) + len(target_only_records_df)
            total_differences = difference_count
            total_records_only_in_source = len(source_only_records_df)
            total_records_only_in_target = len(target_only_records_df)
            total_time_taken_in_secs = comparision_end_time - comparision_start_time

            # Create report file
            differences_html = differences_df.to_html(index=False, classes=['table', 'table-striped', 'table-hover'])
            source_only_html = source_only_records_df.to_html(index=False, classes=['table', 'table-striped', 'table-hover'])
            target_only_html = target_only_records_df.to_html(index=False, classes=['table', 'table-striped', 'table-hover'])

            html_page = readFile(cfg.artifacts_path + cfg.raw_report_file_name)
            html_page = html_page.replace('#current_date_and_time#', getCurrentDayDateTimeAsString())
            html_page = html_page.replace('#source_file_name#', source_data_file.name)
            html_page = html_page.replace('#target_file_name#', target_data_file.name)
            html_page = html_page.replace('#total_source_records#', str(total_source_records))
            html_page = html_page.replace('#total_target_records#', str(total_target_records))
            html_page = html_page.replace('#total_errors#', str(total_errors))
            html_page = html_page.replace('#total_differences#', str(total_differences))
            html_page = html_page.replace('#total_records_only_in_source#', str(total_records_only_in_source))
            html_page = html_page.replace('#total_records_only_in_target#', str(total_records_only_in_target))
            html_page = html_page.replace('#differences_df#', differences_html)
            html_page = html_page.replace('#source_only_records_df#', source_only_html)
            html_page = html_page.replace('#target_only_records_df#', target_only_html)
            html_page = html_page.replace('#total_time_taken_in_mins#', str(round(total_time_taken_in_secs/60, 4)))
            if(total_errors > 0):
                html_page = html_page.replace('#status_class#', "status-component-failed")
                html_page = html_page.replace('#status#', "Comparision Failed")
            else:
                html_page = html_page.replace('#status_class#', "status-component-success")
                html_page = html_page.replace('#status#', "Comparision Successful")
            html_page = html_page.replace('<td>:red', '<td style="background-color: #FF0000; color: white;">')
            # writeFile(html_page, "test.html")
        # components.html(html_page, width=1080, height=720)
        # Show button to download the data comparision report
        if(total_errors > 0):
            st.download_button(label="❌ :red[Comparision Failed] | ⬇️ Download Comparision Report", data=html_page, file_name=f"Validata_Comparision_Report_{getCurrentDateTimeAsString()}.html", use_container_width=True)
        else:
            st.download_button(label="✅ :green[Comparision Successful] | ⬇️ Download Comparision Report", data=html_page, file_name=f"Validata_Comparision_Report_{getCurrentDateTimeAsString()}.html", use_container_width=True)


# Streamlit page content function
def showPageContent() -> None:
    # Display page title
    colored_header(
        label="Files Validator",
        description="",
        color_name="gray-70",
    )

    # Show tabs
    files_validator_page_tabs = st.tabs(["ℹ️ Information", "🔍 Validator"])

    # Information tab
    with files_validator_page_tabs[0]:
        showInformationTabContent()

    # Validator tab
    with files_validator_page_tabs[1]:
        showValidatorTabContent()

# Streamlit sidebar function
def showSidebarContent() -> None:
    # Display sidebar title
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "🔍 Validata";
                display: block;
                padding: 20px;
                padding-top: 40px;
                font-size: 28px;
                font-weight: bold;
                position: static;
                margin-right: 6px;
                margin-bottom: -60px;
                backdrop-filter: blur(100px);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display version details (MAJOR.MINOR.PATCH-IDENTIFIER)
    st.sidebar.info(f"App version: {cfg.app_version}")

    # Display maintainance details if not empty
    if(cfg.maintainance_message!=""):
        st.sidebar.warning(f"Maintainance update: -\n\n{cfg.maintainance_message}")

# Streamlit page function
def fileValidatorPage() -> None:
    # Set-up streamlit page configuration
    st.set_page_config(
        page_title = "Validata: File Validator",
        page_icon = ":mag:",
        layout = "wide",
        initial_sidebar_state = "auto" # -> "auto" or "expanded" or "collapsed"
    )
    
    # Hide default streamlit menu and footer
    hide_default_st_style = "<style> #MainMenu {visibility: hidden;s} footer {visibility: hidden;} </style>"
    st.markdown(body=hide_default_st_style, unsafe_allow_html=True)

    # Initialize streamlit session variables
    if("init_var" not in st.session_state):
        st.session_state['init_var'] = False
    
    # Show sidebar content
    showSidebarContent()

    # Show page content
    showPageContent()

# Main function
def main() -> None:
    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Call Streamlit page function
    fileValidatorPage()

# Main handler
if __name__ == '__main__':
    main()