import re
import pandas as pd
from io import BytesIO, StringIO
import streamlit as st
from pypdf import PdfReader
import datetime
import hashlib
import uuid

# Set page config
st.set_page_config(
    page_title="Credit Card Statement Parser", 
    layout="centered",
    page_icon="💳"
)

# Title
st.title("Credit Card Statement Parser")
st.markdown("---")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF"""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        text_pages = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
        return "\n".join(text_pages)
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def identify_card_issuer(text: str) -> dict:
    """Enhanced bank detection"""
    text_upper = text.upper()

    if "SBI CREDIT CARD" in text_upper or "SBI CARD" in text_upper:
        return {"name": "SBI Card", "color": "#1C4A90", "icon": "🏪"}
    elif "ICICI BANK CREDIT" in text_upper or "ICICI BANK" in text_upper:
        return {"name": "ICICI Bank", "color": "#FF6600", "icon": "🏦"}
    elif "HDFC BANK CREDIT" in text_upper or "HDFC BANK" in text_upper:
        return {"name": "HDFC Bank", "color": "#004C8F", "icon": "🏛️"}
    elif "AXIS BANK CREDIT" in text_upper or "AXIS BANK" in text_upper:
        return {"name": "Axis Bank", "color": "#800080", "icon": "🏢"}
    elif "AMEX CREDIT CARD" in text_upper or "AMEX" in text_upper or "AMERICAN EXPRESS" in text_upper:
        return {"name": "American Express", "color": "#006FCF", "icon": "💎"}
    else:
        return {"name": "Unknown Bank", "color": "#666666", "icon": "❓"}

def clean_amount_for_csv(amount_str: str) -> str:
    """Clean amount string for proper CSV formatting"""
    if amount_str == "Not Found":
        return "Not Found"

    # Remove extra spaces and normalize
    cleaned = re.sub(r'\s+', '', amount_str)

    # Handle different currency formats
    if '₹' in cleaned:
        number_part = cleaned.replace('₹', '').replace(',', '')
        if '.' not in number_part and number_part.isdigit():
            number_part += '.00'
        return f"₹{number_part}"
    elif '$' in cleaned:
        number_part = cleaned.replace('$', '').replace(',', '')
        if '.' not in number_part and number_part.isdigit():
            number_part += '.00'
        return f"${number_part}"
    else:
        number_part = cleaned.replace(',', '')
        if '.' not in number_part and number_part.isdigit():
            number_part += '.00'
        return f"₹{number_part}"

def extract_key_data(text: str) -> dict:
    """Extract key data points"""
    data = {
        "card_issuer": "Not Found",
        "card_last4": "Not Found", 
        "statement_date": "Not Found",
        "due_date": "Not Found",
        "total_amount": "Not Found"
    }

    # Card Issuer
    issuer_info = identify_card_issuer(text)
    data["card_issuer"] = issuer_info["name"]

    # Card Last 4 Digits
    card_patterns = [
        r"Card Number[:\s]*(?:XXXX[\s-]*){3}(\d{4})",
        r"(?:XXXX[\s-]*){3}(\d{4})",
        r"ending\s+(?:in\s+)?(\d{4})",
    ]

    for pattern in card_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["card_last4"] = match.group(1)
            break

    # Statement Date
    date_patterns = [
        r"Statement Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"Bill Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["statement_date"] = match.group(1)
            break

    # Payment Due Date
    due_patterns = [
        r"Payment Due Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"Due Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    ]

    for pattern in due_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["due_date"] = match.group(1)
            break

    # Total Amount Due
    amount_patterns = [
        r"Total Amount Due[:\s]*([₹$£€¥]?[\s]*[\d,]+\.?\d*)",
        r"Outstanding Balance[:\s]*([₹$£€¥]?[\s]*[\d,]+\.?\d*)",
        r"Amount Due[:\s]*([₹$£€¥]?[\s]*[\d,]+\.?\d*)",
    ]

    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_amount = match.group(1).strip()
            if raw_amount and any(char.isdigit() for char in raw_amount):
                data["total_amount"] = clean_amount_for_csv(raw_amount)
                break

    return data

def display_results(data: dict, issuer_info: dict, filename: str):
    """Display results with SINGLE reliable download"""

    # Bank header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {issuer_info['color']}, #f8f9fa); 
                padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: {issuer_info['color']}; margin: 0;">
            {issuer_info['icon']} {issuer_info['name']}
        </h2>
        <p style="margin: 5px 0 0 0; color: #666;">File: {filename}</p>
    </div>
    """, unsafe_allow_html=True)

    # Results display
    st.markdown("### Results")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Card Issuer:** {data['card_issuer']}")
        st.markdown(f"**Card Last 4 Digits:** {'XXXX XXXX XXXX ' + data['card_last4'] if data['card_last4'] != 'Not Found' else 'Not Found'}")
        st.markdown(f"**Statement Date:** {data['statement_date']}")

    with col2:
        st.markdown(f"**Payment Due Date:** {data['due_date']}")
        st.markdown(f"**Total Amount Due:** {data['total_amount']}")

    # Data table
    st.markdown("---")
    table_data = {
        "Information": [
            "Card Issuer", 
            "Card Last 4 Digits", 
            "Statement Date", 
            "Payment Due Date", 
            "Total Amount Due"
        ],
        "Value": [
            data['card_issuer'],
            data['card_last4'], 
            data['statement_date'],
            data['due_date'],
            data['total_amount']
        ]
    }

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # SINGLE RELIABLE CSV download
    st.markdown("---")
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bank_name = issuer_info["name"].replace(" ", "_").replace("Card", "")

    # Create optimized CSV content
    csv_rows = []
    csv_rows.append("Information,Value")
    csv_rows.append(f"Card Issuer,{data['card_issuer']}")
    csv_rows.append(f"Card Last 4 Digits,{data['card_last4']}")
    csv_rows.append(f"Statement Date,{data['statement_date']}")
    csv_rows.append(f"Payment Due Date,{data['due_date']}")
    csv_rows.append(f'Total Amount Due,"{data['total_amount']}"')  # Quote the amount field

    csv_content = "\n".join(csv_rows)
    csv_bytes = csv_content.encode('utf-8')

    # SINGLE download button with optimized parameters
    st.download_button(
        label="📥 Download Results",
        data=csv_bytes,
        file_name=f"{bank_name}_{timestamp}.csv",
        mime="text/csv",
        use_container_width=False,
        help="Download extracted data as CSV file"
    )

def main():
    # Reset functionality
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄", help="Reset"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Generate unique upload key
    if "upload_key" not in st.session_state:
        st.session_state.upload_key = str(uuid.uuid4())

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Credit Card Statement PDF",
        type=["pdf"],
        key=f"uploader_{st.session_state.upload_key}"
    )

    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        try:
            pdf_bytes = uploaded_file.read()
            text = extract_text_from_pdf(pdf_bytes)

            if text:
                data = extract_key_data(text)
                issuer_info = identify_card_issuer(text)

                st.markdown("---")
                display_results(data, issuer_info, uploaded_file.name)

            else:
                st.error("Could not extract text from PDF")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    else:
        # Information display
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### Supported Banks
            🏪 SBI Card  
            🏦 ICICI Bank  
            🏛️ HDFC Bank  
            🏢 Axis Bank  
            💎 American Express
            """)

        with col2:
            st.markdown("""
            ### What We Extract
            • Card Issuer  
            • Card Last 4 Digits  
            • Statement Date  
            • Payment Due Date  
            • Total Amount Due
            """)

if __name__ == "__main__":
    main()
