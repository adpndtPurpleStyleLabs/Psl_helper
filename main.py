import os
import pandas as pd
from PyPDF2 import PdfReader

pdf_folder_path = '/Users/administrator/PycharmProjects/SR_Algo/Creditors Ledger'
data = []
for filename in os.listdir(pdf_folder_path):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder_path, filename)
        # pdf_path = '/Users/administrator/PycharmProjects/SR_Algo/Creditors Ledger/HOUSE TO HOMES INTERIOR PRODUCTS LLP.pdf'
        reader = PdfReader(pdf_path)
        # print(len(reader.pages))
        page = reader.pages[0]
        last_page = reader.pages[len(reader.pages)-1]
        text = page.extract_text()
        textArr = text.split("\n")
        length = len(text.split("\n"))

        last_page_text = last_page.extract_text()
        last_page_text_Arr = last_page_text.split("\n")
        last_page_text_length = len(last_page_text_Arr)


        starting_line = 0
        for index, line in enumerate(textArr):
            if "CIN: " in line:
                starting_line = index
                break

        closing_balances = last_page_text_Arr[last_page_text_length-2]
        closing_balances_arr = closing_balances.split(" ")
        data.append({'Filename': filename, 'L1': textArr[starting_line+1], 'L2': textArr[starting_line+2], 'L3': textArr[starting_line+3], 'Closing Balance (Debit)': closing_balances_arr[len(closing_balances_arr)-1]})

df = pd.DataFrame(data)
df.to_csv('extracted_data.csv', index=False)