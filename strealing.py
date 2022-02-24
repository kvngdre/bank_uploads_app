from pathlib import Path
import pandas as pd
from datetime import datetime
import streamlit as st
from pytz import timezone

pd.options.display.float_format = "{:,}".format
localtz = timezone('Africa/Lagos')

st.set_page_config(page_title="Disbursement app", page_icon="⚙", menu_items={'About': "## This is a header"})

bank_sort_codes = {
    'ACCESS BANK': '000014', 'ACCESS BANK PLC (DIAMOND)': '000005', 'ECO BANK': '000010', 'ECOBANK': '000010', 'FCMB': '000003', 'FIDELITY BANK': '000007',
    'FIRST BANK OF NIGERIA': '000016', 'FIRST CITY MONUMENT BANK': '000003', 'GTBANK PLC': '000013', 'GTBANK': '000013', 'HERITAGE BANK': '000020', 'JAIZ BANK': '000006',
    'KEYSTONE BANK': '000002', 'POLARIS BANK': '000008', 'PROVIDUS BANK': '000023', 'STANBICIBTC BANK': '000012', 'STANDARDCHARTERED': '000021',
    'STERLING BANK': '000001', 'UNION BANK': '000018', 'UNITED BANK FOR AFRICA': '000004', 'UBA': '000004', 'UNITY BANK': '000011', 'WEMA BANK': '000017',
    'ZENITH BANK': '000015'
    }

st.title('Bank Transfer Bulk Upload')

uploaded_file = st.file_uploader('Upload disbursement schedule.', ['csv', 'xlsx'])


def run():
    if uploaded_file is not None:
        file_extension = Path(uploaded_file.name).suffix

        # Validating the file extension
        if file_extension == ".csv":
            df = pd.read_csv(uploaded_file, dtype={'BVN': str, 'Account Number': str, 'Net Value': float})
        elif file_extension == ".xlsx":
            df = pd.read_excel(uploaded_file, dtype={'BVN': str, 'Account Number': str, 'Net Value': float})
        else:
            st.error('Unsupported file format.')
            st.stop()

        st.text('\n')
        with st.container():
            # Drop-down for the dataframe
            with st.expander('Click to view dataframe'):
                st.write(df)

            # Calculate net value
            try:
                net_value = round(df.iloc[:-1]['Net Value'].sum())
                sheet_net_value = df.loc[df.shape[0] - 1, 'Net Value']

                if sheet_net_value != net_value:
                    st.warning(f'Incorrect net value sum {"{:,}".format(round(sheet_net_value))}')

                st.success(f'Total to be disbursed  ₦{"{:,}".format(net_value)}')
            except KeyError as err:
                st.error(f'⚠ Error: Could not find column {err}')
                st.stop()

        df.dropna(inplace=True)  # deleting the last row.
        upload_df = df.loc[:, ['Account Number', 'Net Value', 'Bank Name']]

        # Inserting the bank sort codes
        bank_codes = []
        for bank_name in upload_df['Bank Name'].str.upper():
            bank_codes.append(bank_sort_codes.get(bank_name))
        upload_df['bank_code'] = bank_codes

        # Renaming the columns
        upload_df.rename(columns={'Account Number': 'account_number', 'Net Value': 'tra_amt'}, inplace=True)
        st.text('\n')

        # state = st.text_input('Individual remark or collective?')
        remark = st.text_input("Enter the remark/desc for the disbursement upload file.")
        upload_df.insert(2, 'remarks', remark)

        with st.expander('Click to view dataframe.'):
            st.info('Column "Bank Name" would be deleted on download.')
            st.write(upload_df)

        @st.cache
        def convert_df(df_):
            df_2 = df_.drop(columns='Bank Name')
            df_2['tra_amt'].astype(float)
            df_2['account_number'] = '="' + df_2['account_number'] + '"'
            df_2['bank_code'] = '="' + df_2['bank_code'] + '"'
            return df_2.to_csv(index=False).encode('utf-8')

        csv = convert_df(upload_df)
        file_name = "bank_upload_" + datetime.now(tz=localtz).strftime('%d-%b-%Y %H:%M') + ".csv"

        st.download_button(label='Download csv file',
                           data=csv,
                           file_name=file_name,
                           mime='text/csv')


run()
