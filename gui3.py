import streamlit as st
import pandas as pd
from data_provider1 import process_pdf
import matplotlib.pyplot as plt

# Path for saving the updated data
Path_data = 'New.xlsx'

# Function to save updated DataFrame to CSV
def save_to_file(df, filename="updated_data.csv"):
    df.to_csv(filename, index=False)
    st.success(f"Data saved to {filename}")

# Initialize unique labels and categories in session state
if 'unique_labels' not in st.session_state:
    st.session_state['unique_labels'] = []

if 'unique_categories' not in st.session_state:
    st.session_state['unique_categories'] = []

# Streamlit app layout
st.title("Data Processing and Visualization App")

# Tabs for PDF Processing and Data Visualization
tab1, tab2 = st.tabs(["PDF Processing", "Data Visualization"])

# PDF Processing Tab
with tab1:
    st.header("PDF Data Processing")

    # Upload PDF
    pdf_file = st.file_uploader("Upload your PDF file", type=["pdf"])

    if pdf_file is not None:
        # Process the PDF into DataFrame
        df = process_pdf(pdf_file)

        # Show extracted data from the PDF
        st.write("Extracted Data", df)

        # Filter rows where either Label or Category fields are blank
        blank_rows = df[df['Label'].isna() | df['Category'].isna()]

        if not blank_rows.empty:
            # Update unique labels and categories based on current DataFrame
            st.session_state['unique_labels'] = list(set(df['Label'].dropna().unique().tolist() + st.session_state['unique_labels']))
            st.session_state['unique_categories'] = list(set(df['Category'].dropna().unique().tolist() + st.session_state['unique_categories']))

            # Add "Add new..." option to dropdown lists
            unique_labels = st.session_state['unique_labels'] + ["Add new..."]
            unique_categories = st.session_state['unique_categories'] + ["Add new..."]

            with st.form(key="data_form"):
                for index, row in blank_rows.iterrows():
                    formatted_row = f"{str(row['Date'])} {str(row['Time'])} {str(row['Transaction Type'])} {str(row['Amount'])} {str(row['Vendor'])}"

                    # Dropdown for Label with "Add new..." option
                    selected_label = st.selectbox(
                        f"Select or Add Label for {formatted_row}", 
                        options=unique_labels, 
                        key=f"dropdown_label_{index}"
                    )

                    # Conditionally show text input if "Add new..." is selected
                    if selected_label == "Add new...":
                        new_label = st.text_input(f"Enter new Label for {formatted_row}", key=f"new_label_{index}")
                        if new_label:
                            # Add the new label to session state for future dropdowns
                            st.session_state['unique_labels'].append(new_label)
                            selected_label = new_label  # Use new value as selection

                    # Dropdown for Category with "Add new..." option
                    selected_category = st.selectbox(
                        f"Select or Add Category for {formatted_row}", 
                        options=unique_categories, 
                        key=f"dropdown_category_{index}"
                    )

                    # Conditionally show text input if "Add new..." is selected
                    if selected_category == "Add new...":
                        new_category = st.text_input(f"Enter new Category for {formatted_row}", key=f"new_category_{index}")
                        if new_category:
                            # Add the new category to session state for future dropdowns
                            st.session_state['unique_categories'].append(new_category)
                            selected_category = new_category  # Use new value as selection

                    # Update DataFrame with user input
                    df.at[index, 'Label'] = selected_label
                    df.at[index, 'Category'] = selected_category

                    # Add a separator line between rows for visual clarity
                    st.markdown("---")

                # Submit button for saving changes
                submit_button = st.form_submit_button(label='Submit Changes')
                
                if submit_button:
                    st.write("Updated Data", df)
                    # Save updated data to an Excel file and CSV
                    df.to_excel(Path_data, index=False)
                    save_to_file(df)
        else:
            st.write("No blank rows left to fill.")
    else:
        st.write("Please upload a PDF file to start processing.")

# Data Visualization Tab
with tab2:
    st.header("Data Visualization")

    # Load data from the Excel file
    try:
        data = pd.read_excel(Path_data)
        # st.write("Data from Excel", data)

        # Filter by year and month
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            
            # Add Year filter
            year_filter = st.selectbox("Select Year", options=data['Date'].dt.year.unique())
            
            # Add Month filter based on year
            month_filter = st.selectbox("Select Month", options=pd.to_datetime(data[data['Date'].dt.year == year_filter]['Date']).dt.month_name().unique())
            
            filtered_data = data[(data['Date'].dt.year == year_filter) & (data['Date'].dt.month_name() == month_filter)]

            if not filtered_data.empty:
                # Create a bar chart for 'Label' counts, sorted in descending order
                st.subheader(f"Bar Chart of Labels Amount for {month_filter} {year_filter}")

                # Calculate the total amount spent per label and sort in descending order
                label_amount_sum = filtered_data.groupby('Label')['Amount'].sum().sort_values(ascending=False)

                # Calculate the total amount spent in the selected month and year
                total_amount_spent = label_amount_sum.sum()

                # Display total amount spent above the bar chart
                st.markdown(f"### Total Amount Spent in {month_filter} {year_filter}: **{total_amount_spent:.2f}**")

                # Create the bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = label_amount_sum.plot(kind='bar', ax=ax, color='skyblue')

                # Add data labels to each bar
                for bar in bars.patches:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f}', 
                                xy=(bar.get_x() + bar.get_width() / 2, height), 
                                xytext=(0, 5),  # 5 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

                ax.set_title(f"Total Amount by Label for {month_filter} {year_filter}")
                ax.set_ylabel("Total Amount")
                ax.set_xlabel("Label")
                ax.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig)

                # Bar Chart for 'Amount' by Date (using day of the month as x-axis)
                st.subheader(f"Bar Chart of 'Amount' by Date for {month_filter} {year_filter}")
                
                # Format the 'Date' to only show the day of the month (1, 2, 3, ...)
                filtered_data['Day'] = filtered_data['Date'].dt.day

                # Calculate total amount by day of the month
                amount_by_day = filtered_data.groupby('Day')['Amount'].sum()

                # Create bar chart and add data labels
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = amount_by_day.plot(kind='bar', ax=ax, color='lightgreen')

                # Add data labels to each bar
                for bar in bars.patches:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f}', 
                                xy=(bar.get_x() + bar.get_width() / 2, height), 
                                xytext=(0, 5),  # 5 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

                ax.set_title(f"Total Amount by Date for {month_filter} {year_filter}")
                ax.set_ylabel("Total Amount")
                ax.set_xlabel("Day of the Month")
                ax.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig)

                # Example of a line chart for a numerical column (if applicable)
                # if 'Amount' in filtered_data.columns:
                #     st.subheader(f"Line Chart for 'Amount' in {month_filter} {year_filter}")
                #     fig, ax = plt.subplots(figsize=(10, 6))
                #     filtered_data.groupby('Date')['Amount'].sum().plot(ax=ax, color='green')
                #     ax.set_title(f"Amount Trend for {month_filter} {year_filter}")
                #     ax.set_ylabel("Amount")
                #     ax.set_xlabel("Date")
                #     ax.grid(True)
                #     st.pyplot(fig)

            else:
                st.write(f"No data available for {month_filter} {year_filter}.")

        else:
            st.write("No 'Date' column found in the data for filtering.")
    except FileNotFoundError:
        st.write("The Excel file with processed data does not exist. Please upload a PDF first.")
    except Exception as e:
        st.write(f"An error occurred: {e}")
