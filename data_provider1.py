import io
from PyPDF2 import PdfReader
import pandas as pd
import streamlit as st
##### Previous Data for Dashboard ##############

# Function to process the PDF
def process_pdf(pdf_file):
    # Read the Excel file where previous data is stored
    Previous_data = pd.read_excel('New.xlsx')

    # Read the PDF from the uploaded file object
    pdf_reader = PdfReader(pdf_file)
    
    # Initialize an empty list to store words
    pdf_words = []
    
    # Iterate through each page in the PDF and extract text
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        words = page_text.split()
        pdf_words.extend(words)

    # List of months
    months = {'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'}

    # Words to remove from the word list
    words_to_remove = ['Date', 'Transaction', 'Details', 'Type', 'Amount', 'Page', 
                        'This', 'is', 'a', 'system', 'generated', 'statement.', 
                        'For', 'any', 'queries,', 'contact', 'us', 'at', 
                        'https://support.phonepe.com/statement.', 'Statement', 'for', 
                        '9887159559', 'an', 'automatically', 'Customer(s)', 'are', 
                        'requested', 'to', 'immediately', 'notify', 'PhonePe', 
                        'in', 'errors', 'in', 'the', 'statement', 
                        'https://support.phonepe.com/statement', 'and', 'visit', 
                        'https://www.phonepe.com/', 'terms-conditions/', 'PhonePe', 
                        'Terms', '&', 'Conditions', 'and', 'Privacy', 'Policy.', 
                        'Disclaimer', ':', 'Do', 'not', 'fall', 'prey', 'to', 
                        'fictitious', 'prizes,', 'money', 'circulation', 'schemes', 
                        'and', 'cheap', 'funds,', 'etc.', 'through', 'SMS,', 
                        'emails', 'and', 'calls.', 'The', 'email', 'and', 'document', 
                        'are', 'confidential', 'and', 'intended', 'the', 'recipient', 
                        'specified', 'in', 'this', 'document.', 'If', 'you', 'received', 
                        'this', 'message', 'by', 'mistake,', 'please', 'inform', 'PhonePe', 
                        'https://support.phonepe.com/statement', 'so', 'that', 'we', 
                        'can', 'ensure', 'the', "recipient's", 'details', 'are', 'corrected.']

    # Filter out the words to remove
    word_list = [word for word in pdf_words if word not in words_to_remove]

    # Remove the first 7 elements of the list (initial setup)
    word_list = word_list[7:]

    # Initialize an empty list to store DataFrames
    dfs = []
    current_section = []

    # Iterate through the filtered word list
    for word in word_list:
        if word in months:
            if current_section:
                current_section.insert(0, word)
                data_list = current_section[1:]

                # Check if the section has enough elements
                if len(data_list) >= 10:
                    date = ' '.join(data_list[:3])
                    time = ' '.join(data_list[3:5])
                    transaction_type = data_list[5]
                    amount = data_list[6][1:]  # Removing the currency symbol ₹

                    # Remove commas from the amount
                    amount = amount.split(".")[0].strip()
                    amount = amount.replace(',', '')

                    # Ensure that the amount is valid
                    if amount.isdigit():
                        amount_numeric = float(amount)
                        vendor_index = data_list.index('ID') 
                        vendor = ' '.join(data_list[8:vendor_index])
                        id1 = data_list[vendor_index + 1]
                        bank_account = data_list[-1]

                        # Create DataFrame
                        df = pd.DataFrame({
                            'Date': [date],
                            'Time': [time],
                            'Transaction Type': [transaction_type],
                            'Amount': [amount_numeric],
                            'Vendor': [vendor],
                            'ID1': [id1],
                            'Bank Account': [bank_account]
                        })
                        dfs.append(df)

                # Reset current_section for the next block
                current_section = []
            current_section.append(word)
        else:
            current_section.append(word)

    # Concatenate all DataFrames in the list if dfs is not empty
    if dfs:
        result = pd.concat(dfs, ignore_index=True)

        # Clean up the result DataFrame
        if not result.empty:
            result = result.drop(result.index[-1])
            result['Amount'] = pd.to_numeric(result['Amount'], errors='coerce')
            result['Date'] = pd.to_datetime(result['Date'], format='%b %d, %Y')
        else:
            print("No valid data found.")
    else:
        print("No sections found.")

    # Merge with previous data
    merged_data = result.merge(Previous_data, on='ID1', how='left')
    merged_data = merged_data.drop(columns=[col for col in merged_data.columns if col.endswith('_y')])

    # Remove the '_x' suffix from remaining columns
    merged_data.columns = [col.replace('_x', '') for col in merged_data.columns]
    merged_data = merged_data[['Date', 'Time', 'Transaction Type', 'Amount', 'Vendor', 'ID1', 'Bank Account', 'Label','Category']]

    # Filter for dates after November 1, 2024
    merged_data['Date'] = pd.to_datetime(merged_data['Date'], errors='coerce')
    merged_data = merged_data[merged_data['Date'] > '2024-11-01']
    merged_data = merged_data[merged_data['Transaction Type'] == 'DEBIT']

    # Save the final merged data to Excel
    merged_data.to_excel('new_data.xlsx', index=False)

    return merged_data
