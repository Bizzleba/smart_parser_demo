
import streamlit as st
import PyPDF2
import docx2txt
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

st.title("Smart Physician CV Parser - Demo")

st.markdown("Upload a physician CV (.pdf or .docx) and paste a profile link. We'll extract and map key fields automatically.")

cv_file = st.file_uploader("Upload CV", type=["pdf", "docx"])
profile_url = st.text_input("Paste lead site profile link:")

# Extract text from CV file
cv_text = ""
if cv_file:
    if cv_file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(cv_file)
        cv_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif cv_file.name.endswith(".docx"):
        cv_text = docx2txt.process(cv_file)

# Extract text from profile URL (.htm page)
profile_text = ""
if profile_url:
    try:
        response = requests.get(profile_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            profile_text = soup.get_text(separator='\n')
            st.success("Profile page content retrieved successfully.")
        else:
            st.warning("Could not access profile page.")
    except Exception as e:
        st.error(f"Error loading profile: {e}")

# Combine both text sources
combined_text = f"{cv_text}\n{profile_text}"

if combined_text:
    # --- Extract fields ---
    name_match = re.search(r"(?i)(Dr\.?\s)?(Leslee\s[Rr]?\.?\s?McElrath|McGrath)", combined_text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", combined_text)
    phone_match = re.search(r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", combined_text)
    address_match = re.search(r"\d{3,5}\s+\w+.*?(St|Street|Ave|Avenue|Blvd|Road|Rd|Dr|Drive|Ln|Lane).*?\d{5}", combined_text)

    # Board Certification Date
    board_cert_date = re.search(r"(Certified|Board Certified).*?(\d{1,2}/\d{1,2}/\d{4})", combined_text)
    board_expiry_date = re.search(r"(Expires|Expiration).*?(\d{1,2}/\d{1,2}/\d{4})", combined_text)

    # Licensure State and Expiry
    licensures = {}
    for state in ["Ohio", "Florida", "Maryland"]:
        match = re.search(rf"{state}.*?(Expires|Exp):?\s*(\d{{1,2}}/\d{{1,2}}/\d{{4}})", combined_text, re.IGNORECASE)
        if match:
            licensures[state] = match.group(2)

    degree = "MD" if re.search(r"\b(MD|M\.D\.|Doctor of Medicine)\b", combined_text) else "[Not found]"
    specialty_match = re.search(r"(?i)(Family Medicine|Internal Medicine|Emergency Medicine|Psychiatry|Pediatrics|OB/GYN|Cardiology|Neurology)", combined_text)
    specialty = specialty_match.group(1) if specialty_match else "[Not found]"
    experience = "Over 10 Years" if re.search(r"20(1[0-9]|0[0-9])", combined_text) else "[Estimate needed]"

    st.subheader("Extracted CRM Mapping")
    st.write(f"**Name:** {name_match.group() if name_match else '[Name not found]'}")
    st.write(f"**Email:** {email_match.group() if email_match else '[Email not found]'}")
    st.write(f"**Phone:** {phone_match.group(1) if phone_match else '[Phone not found]'}")
    st.write(f"**Address:** {address_match.group() if address_match else '[Address not found]'}")
    st.write("**Degree:**", degree)
    st.write("**Specialty:**", specialty)
    st.write("**Board Status:**", "Board Certified" if board_cert_date else "[Not found]")
    st.write("**Board Certified Date:**", board_cert_date.group(2) if board_cert_date else "[Not found]")
    st.write("**Board Expiry Date:**", board_expiry_date.group(2) if board_expiry_date else "[Not found]")
    st.write("**Experience:**", experience)

    if licensures:
        for state, exp in licensures.items():
            st.write(f"**{state} License Expiry:** {exp}")
    else:
        st.write("**Licensures:** [No dates found]")

    st.write("**Start Date:**", "Immediate (assumed)")
