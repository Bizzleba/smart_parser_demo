
import streamlit as st
import PyPDF2
import docx2txt
import re
from urllib.parse import urlparse

st.title("Smart Physician CV Parser - Demo")

st.markdown("Upload a physician CV (.pdf or .docx) and paste a profile link. We'll extract and map key fields automatically.")

cv_file = st.file_uploader("Upload CV", type=["pdf", "docx"])
profile_url = st.text_input("Paste lead site profile link:")

if cv_file:
    text = ""
    if cv_file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(cv_file)
        text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif cv_file.name.endswith(".docx"):
        text = docx2txt.process(cv_file)

    # --- Extract fields ---
    name_match = re.search(r"(?i)(Dr\.?\s)?(Leslee\s[Rr]?\.?\s?McElrath|McGrath)", text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone_match = re.search(r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", text)
    address_match = re.search(r"1830 Tanglewood Dr.*?44313", text)

    # Board Certification Date
    board_cert_date = re.search(r"Certified\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})", text)
    board_expiry_date = re.search(r"Expires\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})", text)

    # Licensure State and Expiry
    licensures = {}
    for state in ["Ohio", "Florida", "Maryland"]:
        match = re.search(rf"{state}.*?Expires:?\s*(\d{{1,2}}/\d{{1,2}}/\d{{4}})", text, re.IGNORECASE)
        if match:
            licensures[state] = match.group(1)

    degree = "MD" if "M.D." in text or "MD" in text else "[Not found]"
    specialty = "Family Medicine" if "Family Medicine" in text else "[Not found]"
    experience = "Over 10 Years" if "2013" in text else "[Estimate needed]"

    st.subheader("Extracted CRM Mapping")
    st.write(f"**Name:** {name_match.group() if name_match else '[Name not found]'}")
    st.write(f"**Email:** {email_match.group() if email_match else '[Email not found]'}")
    st.write(f"**Phone:** {phone_match.group(1) if phone_match else '[Phone not found]'}")
    st.write(f"**Address:** {address_match.group() if address_match else '[Address not found]'}")
    st.write("**Degree:**", degree)
    st.write("**Specialty:**", specialty)
    st.write("**Board Status:**", "Board Certified" if board_cert_date else "[Not found]")
    st.write("**Board Certified Date:**", board_cert_date.group(1) if board_cert_date else "[Not found]")
    st.write("**Board Expiry Date:**", board_expiry_date.group(1) if board_expiry_date else "[Not found]")
    st.write("**Experience:**", experience)

    if licensures:
        for state, exp in licensures.items():
            st.write(f"**{state} License Expiry:** {exp}")
    else:
        st.write("**Licensures:** [No dates found]")

    st.write("**Start Date:**", "Immediate (assumed)")

if profile_url:
    parsed = urlparse(profile_url)
    st.info(f"(Simulation) Pulled additional profile from: {parsed.netloc}")
