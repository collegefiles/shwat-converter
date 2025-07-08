import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import os
import uuid
import io
import json

# --- CONFIGURATION ---
ENCRYPTION_KEY = b'SGWATMODDERSECRETKEY'

# --- FIREBASE INITIALIZATION using Streamlit Secrets ---
try:
    # Check if the app is already initialized
    if not firebase_admin._apps:
        # Load credentials from st.secrets
        creds_json_str = st.secrets["firebase_credentials"]
        creds_dict = json.loads(creds_json_str)
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': f"https://{creds_dict['project_id']}-default-rtdb.firebaseio.com"
        })
    firebase_initialized = True
except Exception as e:
    firebase_initialized = False
    st.error(f"Firebase initialization failed. Ensure your secrets are set correctly. Error: {e}")

# --- CORE LOGIC ---
def xor_crypt(data, key):
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))

# --- STREAMLIT UI ---
st.set_page_config(page_title="SHWAT Converter", layout="centered")
st.title("PDF to .shwat Converter")

st.header("1. Upload your PDF file")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None and firebase_initialized:
    st.success(f"File '{uploaded_file.name}' uploaded successfully.")

    pdf_data = uploaded_file.getvalue()
    encrypted_data = xor_crypt(pdf_data, ENCRYPTION_KEY)
    
    original_filename = uploaded_file.name
    shwat_filename = os.path.splitext(original_filename)[0] + '.shwat'
    
    st.header("2. Download your encrypted file")
    st.info(f"The file will be downloaded as: **{shwat_filename}**")
    
    encrypted_file_stream = io.BytesIO(encrypted_data)

    st.download_button(
       label="Download .shwat file",
       data=encrypted_file_stream,
       file_name=shwat_filename,
       mime="application/octet-stream"
    )

    try:
        with st.spinner('Registering file in Firebase...'):
            file_id = str(uuid.uuid4())
            file_info = {
                'filename': shwat_filename,
                'original_name': original_filename,
                'id': file_id
            }
            # Use db.reference with the official SDK
            ref = db.reference(f"files/{shwat_filename.replace('.', '_')}")
            ref.set(file_info)
        st.success("File successfully registered in Firebase.")
    except Exception as e:
        st.error(f"Could not register file in Firebase. Error: {e}")
