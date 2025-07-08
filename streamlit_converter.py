import streamlit as st
import pyrebase
import os
import uuid
import io

# --- CONFIGURATION ---
ENCRYPTION_KEY = b'SGWATMODDERSECRETKEY'

firebase_config = {
    "apiKey": "AIzaSyAe9HSedJRzbc1PLvDU4kL2Mh_Sprg1ZpM",
    "authDomain": "shwat-protection-sys.firebaseapp.com",
    "databaseURL": "https://shwat-protection-sys-default-rtdb.firebaseio.com",
    "storageBucket": "shwat-protection-sys.firebasestorage.app"
}

try:
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    firebase_initialized = True
except Exception as e:
    firebase_initialized = False
    st.error(f"Firebase initialization failed. Check your config. Error: {e}")

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
    
    # Process the file in memory
    pdf_data = uploaded_file.getvalue()
    encrypted_data = xor_crypt(pdf_data, ENCRYPTION_KEY)
    
    original_filename = uploaded_file.name
    shwat_filename = os.path.splitext(original_filename)[0] + '.shwat'
    
    st.header("2. Download your encrypted file")
    st.info(f"The file will be downloaded as: **{shwat_filename}**")
    
    # Use an in-memory byte stream for the download button
    encrypted_file_stream = io.BytesIO(encrypted_data)

    st.download_button(
       label="Download .shwat file",
       data=encrypted_file_stream,
       file_name=shwat_filename,
       mime="application/octet-stream"
    )

    # Register the file in Firebase after processing
    # This ensures the button is ready when the user sees it
    try:
        with st.spinner('Registering file in Firebase...'):
            file_id = str(uuid.uuid4())
            file_info = {
                'filename': shwat_filename,
                'original_name': original_filename,
                'id': file_id
            }
            db.child("files").child(shwat_filename.replace('.', '_')).set(file_info)
        st.success("File successfully registered in Firebase.")
    except Exception as e:
        st.error(f"Could not register file in Firebase. Error: {e}")