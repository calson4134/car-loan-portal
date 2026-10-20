import os
import io
import zipfile
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF for handling form text and signatures

# Page Configuration
st.set_page_config(
    page_title="Car Loan Submission Portal",
    page_icon="🚗",
    layout="wide"
)

# --- SECURITY / PASSWORD LOGIN SCREEN ---
APP_PASSWORD = "metro"

def check_password():
    """Returns `True` if the user entered the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # Show login screen
    st.title("🔒 Car Loan Submission Portal - Login")
    st.markdown("Please enter the team password to access the portal.")
    
    entered_password = st.text_input("Password", type="password")
    if st.button("Login"):
        if entered_password == APP_PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("😕 Incorrect password. Please try again.")
    return False

if not check_password():
    st.stop()  # Halts execution here if not logged in

# --- MAIN APP (Only runs after successful login) ---
st.title("🚗 Car Loan Application Portal - Secure Edition")
st.markdown("Fill out applicant details and auto-stamp signatures directly into Sejda-defined form fields.")

# Path to template files
TEMPLATE_DIR = "templates"
TEST_COMPANIES = {
    "ELK Credit": "ELK_template.pdf",
    "365 Capital": "365_Capital_template.pdf",
    "Capital Temasek": "Capital_Temasek_template.pdf",
    "SMS Credit": "SMS_template.pdf"
}

# --- HELPER FUNCTION TO CONVERT CANVAS DRAWING TO IMAGE & ROTATE ---
def canvas_to_image_bytes(canvas_result, rotate_angle=270):
    if canvas_result and canvas_result.image_data is not None:
        img_array = canvas_result.image_data
        img = Image.fromarray(img_array.astype("uint8"), mode="RGBA")
        
        extrema = img.getextrema()
        if extrema[3][0] == 0:  
            return None

        if rotate_angle != 0:
            img = img.rotate(rotate_angle, expand=True)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr
    return None

# --- INPUT FORM ---
with st.form("loan_application_form"):
    st.subheader("1. Select Credit Companies")
    selected_companies = st.multiselect(
        "Choose targeted credit companies:",
        options=list(TEST_COMPANIES.keys()),
        default=list(TEST_COMPANIES.keys())
    )

    # --- SECTION A: HIRER DETAILS & SIGNATURE ---
    st.markdown("---")
    st.subheader("2. Hirer (Applicant) Details & Signature")
    col1, col2 = st.columns(2)
    
    with col1:
        hirer_name = st.text_input("Hirer Full Name", placeholder="e.g. TAN AH KOW")
        hirer_ic_number = st.text_input("Hirer IC / Passport Number", placeholder="e.g. 900424-10-5555")
        hirer_phone_number = st.text_input("Hirer Phone Number", placeholder="e.g. 012-3456789")
        hirer_email = st.text_input("Hirer Email Address", placeholder="e.g. tan@example.com")
        hirer_marital_status = st.selectbox("Hirer Marital Status", ["Single", "Married", "Divorced", "Widowed"])

    with col2:
        hirer_address_line_01 = st.text_input("Hirer Address Line 01", placeholder="Street Address / Taman")
        hirer_address_line_02 = st.text_input("Hirer Address Line 02", placeholder="Postcode, City, State")
        hirer_employer_name = st.text_input("Hirer Employer / Business Name", placeholder="e.g. AgriPro Hardware")
        hirer_employer_phone_number = st.text_input("Hirer Employer Phone Number", placeholder="e.g. 03-12345678")
        hirer_employer_address = st.text_input("Hirer Employer Address", placeholder="Employer address")

    st.markdown("**Hirer Signature:**")
    canvas_hirer = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=130,
        width=300,
        drawing_mode="freedraw",
        return_image_data=True,
        key="canvas_hirer"
    )

    # --- SECTION B: VEHICLE & LOAN DETAILS ---
    st.markdown("---")
    st.subheader("3. Vehicle & Loan Details")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        carplate_number = st.text_input("Car Registration Number", placeholder="e.g. ABC 1234")
        car_year_made = st.text_input("Car Year Made", placeholder="e.g. 2022")
        car_model = st.text_input("Car Model", placeholder="e.g. Perodua Myvi 1.5 AV")
    
    with col4:
        car_chasis_number = st.text_input("Car Chassis Number", placeholder="Chassis number")
        car_engine_number = st.text_input("Car Engine Number", placeholder="Engine number")
        car_price = st.text_input("Car Price (RM)", placeholder="e.g. 45,000")

    with col5:
        car_hp_amount = st.text_input("Car HP Amount (RM)", placeholder="e.g. 40,000")
        car_tenure = st.text_input("Car Tenure (months)", placeholder="e.g. 60")
        form_date = st.text_input("Application Date", placeholder="e.g. 2026-10-18")
        dealer_contact = st.text_input("Dealer Contact", placeholder="e.g. YB +6014-3627323")

    # --- SECTION C: GUARANTOR 01 DETAILS & SIGNATURE ---
    with st.expander("4. Guarantor 01 Details & Signature (Optional)") :
        g1_col1, g1_col2 = st.columns(2)
        with g1_col1:
            gtor01_name = st.text_input("Gtor 01 Full Name", key="g1_n")
            gtor01_ic_number = st.text_input("Gtor 01 IC / Passport Number", key="g1_ic")
            gtor01_phone_number = st.text_input("Gtor 01 Phone Number", key="g1_ph")
            gtor01_marital_status = st.selectbox("Gtor 01 Marital Status", ["", "Single", "Married", "Divorced", "Widowed"], key="g1_marital")
            gtor01_relationship = st.text_input("Gtor 01 Relationship With Hirer", key="g1_rel")
        with g1_col2:
            gtor01_address_line_01 = st.text_input("Gtor 01 Address Line 01", key="g1_add1")
            gtor01_address_line_02 = st.text_input("Gtor 01 Address Line 02", key="g1_add2")
            gtor01_employer_name = st.text_input("Gtor 01 Employer / Business Name", key="g1_emp")
            gtor01_employer_phone_number = st.text_input("Gtor 01 Employer Phone", key="g1_empph")
            gtor01_employer_address = st.text_input("Gtor 01 Employer Address", key="g1_empadd")

        st.markdown("**Guarantor 01 Signature:**")
        canvas_g1 = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=130,
            width=300,
            drawing_mode="freedraw",
            return_image_data=True,
            key="canvas_g1"
        )
    
    if 'canvas_g1' not in locals():
        canvas_g1 = None

    # --- SECTION D: GUARANTOR 02 DETAILS & SIGNATURE ---
    with st.expander("5. Guarantor 02 Details & Signature (Optional)"):
        g2_col1, g2_col2 = st.columns(2)
        with g2_col1:
            gtor02_name = st.text_input("Gtor 02 Full Name", key="g2_n")
            gtor02_ic_number = st.text_input("Gtor 02 IC / Passport Number", key="g2_ic")
            gtor02_phone_number = st.text_input("Gtor 02 Phone Number", key="g2_ph")
            gtor02_marital_status = st.selectbox("Gtor 02 Marital Status", ["", "Single", "Married", "Divorced", "Widowed"], key="g2_marital")
            gtor02_relationship = st.text_input("Gtor 02 Relationship With Hirer", key="g2_rel")
        with g2_col2:
            gtor02_address_line_01 = st.text_input("Gtor 02 Address Line 01", key="g2_add1")
            gtor02_address_line_02 = st.text_input("Gtor 02 Address Line 02", key="g2_add2")
            gtor02_employer_name = st.text_input("Gtor 02 Employer / Business Name", key="g2_emp")
            gtor02_employer_phone_number = st.text_input("Gtor 02 Employer Phone", key="g2_empph")
            gtor02_employer_address = st.text_input("Gtor 02 Employer Address", key="g2_empadd")

        st.markdown("**Guarantor 02 Signature:**")
        canvas_g2 = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=130,
            width=300,
            drawing_mode="freedraw",
            return_image_data=True,
            key="canvas_g2"
        )

    if 'canvas_g2' not in locals():
        canvas_g2 = None

    submitted = st.form_submit_button("Generate Selected Loan Forms 🚀", use_container_width=True)

# --- PROCESS AND GENERATE ---
if submitted:
    if not hirer_name or not hirer_ic_number:
        st.error("Please enter at least the Hirer's Full Name and IC Number.")
    elif not selected_companies:
        st.warning("Please select at least ONE credit company.")
    else:
        applicant_data = {
            "hirer_name": hirer_name.upper(),
            "hirer_ic_number": hirer_ic_number,
            "hirer_phone_number": hirer_phone_number,
            "hirer_email": hirer_email,
            "hirer_address_line_01": hirer_address_line_01,
            "hirer_address_line_02": hirer_address_line_02,
            "hirer_marital_status": hirer_marital_status,
            "hirer_employer_name": hirer_employer_name,
            "hirer_employer_phone_number": hirer_employer_phone_number,
            "hirer_employer_address": hirer_employer_address,
            
            "gtor01_name": gtor01_name.upper() if 'gtor01_name' in locals() and gtor01_name else "",
            "gtor01_ic_number": gtor01_ic_number if 'gtor01_ic_number' in locals() else "",
            "gtor01_phone_number": gtor01_phone_number if 'gtor01_phone_number' in locals() else "",
            "gtor01_address_line_01": gtor01_address_line_01 if 'gtor01_address_line_01' in locals() else "",
            "gtor01_address_line_02": gtor01_address_line_02 if 'gtor01_address_line_02' in locals() else "",
            "gtor01_marital_status": gtor01_marital_status if 'gtor01_marital_status' in locals() else "",
            "gtor01_employer_name": gtor01_employer_name if 'gtor01_employer_name' in locals() else "",
            "gtor01_employer_phone_number": gtor01_employer_phone_number if 'gtor01_employer_phone_number' in locals() else "",
            "gtor01_employer_address": gtor01_employer_address if 'gtor01_employer_address' in locals() else "",
            "gtor01_relationship": gtor01_relationship if 'gtor01_relationship' in locals() else "",

            "gtor02_name": gtor02_name.upper() if 'gtor02_name' in locals() and gtor02_name else "",
            "gtor02_ic_number": gtor02_ic_number if 'gtor02_ic_number' in locals() else "",
            "gtor02_phone_number": gtor02_phone_number if 'gtor02_phone_number' in locals() else "",
            "gtor02_address_line_01": gtor02_address_line_01 if 'gtor02_address_line_01' in locals() else "",
            "gtor02_address_line_02": gtor02_address_line_02 if 'gtor02_address_line_02' in locals() else "",
            "gtor02_marital_status": gtor02_marital_status if 'gtor02_marital_status' in locals() else "",
            "gtor02_employer_name": gtor02_employer_name if 'gtor02_employer_name' in locals() else "",
            "gtor02_employer_phone_number": gtor02_employer_phone_number if 'gtor02_employer_phone_number' in locals() else "",
            "gtor02_employer_address": gtor02_employer_address if 'gtor02_employer_address' in locals() else "",
            "gtor02_relationship": gtor02_relationship if 'gtor02_relationship' in locals() else "",
            
            "carplate_number": carplate_number.upper(),
            "car_year_made": car_year_made,
            "car_model": car_model,
            "car_chasis_number": car_chasis_number,
            "car_engine_number": car_engine_number,
            "car_price": car_price,
            "car_hp_amount": car_hp_amount,
            "car_tenure": car_tenure,
            "form_date": form_date,
            "dealer_contact": dealer_contact
        }

        canvas_hirer_raw = canvas_to_image_bytes(canvas_hirer, rotate_angle=270)
        canvas_g1_raw = canvas_to_image_bytes(canvas_g1, rotate_angle=270) if canvas_g1 else None
        canvas_g2_raw = canvas_to_image_bytes(canvas_g2, rotate_angle=270) if canvas_g2 else None

        canvas_hirer_straight = canvas_to_image_bytes(canvas_hirer, rotate_angle=0)
        canvas_g1_straight = canvas_to_image_bytes(canvas_g1, rotate_angle=0) if canvas_g1 else None
        canvas_g2_straight = canvas_to_image_bytes(canvas_g2, rotate_angle=0) if canvas_g2 else None

        generated_files = {}
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for company in selected_companies:
                file_name = TEST_COMPANIES[company]
                template_path = os.path.join(TEMPLATE_DIR, file_name)

                if os.path.exists(template_path):
                    # Set signature rotation per company layout
                    if company == "ELK Credit":
                        h_sig = canvas_hirer_raw
                        g1_sig = canvas_g1_raw
                        g2_sig = canvas_g2_raw
                    else:
                        # 365 Capital, Capital Temasek, and SMS Credit get un-rotated signatures
                        h_sig = canvas_hirer_straight
                        g1_sig = canvas_g1_straight
                        g2_sig = canvas_g2_straight

                    doc = fitz.open(template_path)
                    
                    for page in doc:
                        for widget in page.widgets():
                            field_name = widget.field_name
                            rect = widget.rect
                            
                            if field_name in applicant_data and applicant_data[field_name]:
                                widget.field_value = str(applicant_data[field_name])
                                widget.update()
                            
                            if field_name == "hirer_signature" and h_sig:
                                page.insert_image(rect, stream=h_sig.getvalue(), keep_proportion=True)
                            elif field_name == "gtor01_signature" and g1_sig:
                                page.insert_image(rect, stream=g1_sig.getvalue(), keep_proportion=True)
                            elif field_name == "gtor02_signature" and g2_sig:
                                page.insert_image(rect, stream=g2_sig.getvalue(), keep_proportion=True)

                    pdf_bytes = doc.write()
                    doc.close()

                    sanitized_name = hirer_name.replace(" ", "_")
                    output_name = f"{company.replace(' ', '_')}_{sanitized_name}.pdf"

                    generated_files[company] = (output_name, pdf_bytes)
                    zip_file.writestr(output_name, pdf_bytes)
                else:
                    st.warning(f"Template not found: '{file_name}' inside '{TEMPLATE_DIR}/' folder.")

        zip_buffer.seek(0)

        if generated_files:
            st.success(f"Successfully generated {len(generated_files)} loan form(s) securely!")
            st.markdown("---")
            st.subheader("📥 Download Generated Documents")

            cols = st.columns(len(generated_files))
            for idx, (company_name, (file_name, pdf_bytes)) in enumerate(generated_files.items()):
                with cols[idx]:
                    st.download_button(
                        label=f"📄 Download {company_name}",
                        data=pdf_bytes,
                        file_name=file_name,
                        mime="application/pdf",
                        use_container_width=True
                    )