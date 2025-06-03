# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from datetime import datetime
import os
import io

class PrescriptionFiller:
    def __init__(self):
        self.template_path = None
        self.font_path = None
        self.coordinates = {
            'name': (140, 228),    # ಹೆಸರು field
            'age': (620, 220),     # ವಯಸ್ಸು field
            'date': (530, 190),    # ದಿನಾಂಕ field
            'sex': (400, 220),     # ವ್ಯಕ್ತಿ field
            'disease': (390, 320)  # ರೋಗ/ಲಕ್ಷಣಗಳು field
        }
        
    def load_template(self, template_path):
        """Load the prescription template image"""
        self.template_path = template_path
        try:
            return Image.open(template_path)
        except Exception as e:
            st.error(f"Error loading template: {str(e)}")
            return None

    def load_font(self, font_path, size=32):
        """Load the Kannada font"""
        self.font_path = font_path
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            st.error(f"Error loading font: {str(e)}")
            return None

    def fill_prescription(self, patient_data, template=None, font=None, coordinates=None):
        """Fill the prescription with patient data"""
        if template is None:
            template = self.load_template(self.template_path)
        if font is None:
            font = self.load_font(self.font_path)
            
        if template is None or font is None:
            return None

        # Use provided coordinates if available, otherwise use default
        current_coordinates = coordinates if coordinates is not None else self.coordinates

        # Create a copy of the template
        img = template.copy()
        draw = ImageDraw.Draw(img)
        
        # Debug: Draw coordinate markers
        marker_color = 'red'
        for field, coords in current_coordinates.items():
            x, y = coords
            # Draw small crosshair at each coordinate
            draw.line((x-5, y, x+5, y), fill=marker_color, width=1)
            draw.line((x, y-5, x, y+5), fill=marker_color, width=1)

        # Fill in the details
        for field, value in patient_data.items():
            if field in current_coordinates:
                draw.text(
                    current_coordinates[field],
                    str(value),
                    font=font,
                    fill='black'
                )

        return img

    def save_as_pdf(self, image, output_path):
        """Save the filled prescription as PDF"""
        try:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PDF')
            with open(output_path, 'wb') as f:
                f.write(image_bytes.getvalue())
            return True
        except Exception as e:
            st.error(f"Error saving PDF: {str(e)}")
            return False

def main():
    st.title("ಕನ್ನಡ OPD Prescription Auto-Filler")
    
    # Initialize session state for coordinates if not already present
    if 'name_x' not in st.session_state:
        st.session_state.name_x = 140
        st.session_state.name_y = 228
        st.session_state.age_x = 620
        st.session_state.age_y = 220
        st.session_state.sex_x = 400
        st.session_state.sex_y = 220
        st.session_state.disease_x = 390
        st.session_state.disease_y = 320
        st.session_state.date_x = 530
        st.session_state.date_y = 190
        st.session_state.font_size = 32  # Default font size

    filler = PrescriptionFiller()
    
    # File uploaders
    template_file = st.file_uploader(
        "Upload Prescription Template (Image)",
        type=['png', 'jpg', 'jpeg']
    )
    
    font_file = st.file_uploader(
        "Upload Kannada Font File (TTF)",
        type=['ttf']
    )
    
    # Input method selection
    input_method = st.radio(
        "Choose Input Method",
        ["Single Entry", "Batch Upload (CSV)"]
    )
    
    if input_method == "Single Entry":
        with st.form("patient_form"):
            name = st.text_input("Patient Name (ರೋಗಿಯ ಹೆಸರು)")
            age = st.number_input("Age (ವಯಸ್ಸು)", min_value=0, max_value=150)
            sex = st.selectbox("Sex (ಲಿಂಗ)", ["ಪುರುಷ", "ಮಹಿಳೆ", "ಇತರೆ"])
            disease = st.text_area("Disease/Symptoms (ರೋಗ/ಲಕ್ಷಣಗಳು)")
            date = st.date_input("Date (ದಿನಾಂಕ)")
            
            st.subheader("Adjust Text Properties (Single Entry)")
            font_size = st.number_input("Font Size", value=32, min_value=1, step=1)

            st.subheader("Adjust Text Coordinates (Single Entry)")
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.name_x = st.number_input("Name X", value=st.session_state.name_x, step=1, key='name_x_input')
                st.session_state.age_x = st.number_input("Age X", value=st.session_state.age_x, step=1, key='age_x_input')
                st.session_state.sex_x = st.number_input("Sex X", value=st.session_state.sex_x, step=1, key='sex_x_input')
                st.session_state.disease_x = st.number_input("Disease X", value=st.session_state.disease_x, step=1, key='disease_x_input')
                st.session_state.date_x = st.number_input("Date X", value=st.session_state.date_x, step=1, key='date_x_input')
            with col2:
                st.session_state.name_y = st.number_input("Name Y", value=st.session_state.name_y, step=1, key='name_y_input')
                st.session_state.age_y = st.number_input("Age Y", value=st.session_state.age_y, step=1, key='age_y_input')
                st.session_state.sex_y = st.number_input("Sex Y", value=st.session_state.sex_y, step=1, key='sex_y_input')
                st.session_state.disease_y = st.number_input("Disease Y", value=st.session_state.disease_y, step=1, key='disease_y_input')
                st.session_state.date_y = st.number_input("Date Y", value=st.session_state.date_y, step=1, key='date_y_input')

            submit_button = st.form_submit_button("Generate Prescription")
        
        if submit_button:
            if template_file and font_file:
                patient_data = {
                    'name': name,
                    'age': age,
                    'sex': sex,
                    'disease': disease,
                    'date': date.strftime("%d/%m/%Y")
                }

                current_coordinates = {
                    'name': (st.session_state.name_x, st.session_state.name_y),
                    'age': (st.session_state.age_x, st.session_state.age_y),
                    'sex': (st.session_state.sex_x, st.session_state.sex_y),
                    'disease': (st.session_state.disease_x, st.session_state.disease_y),
                    'date': (st.session_state.date_x, st.session_state.date_y)
                }

                # Load template and font with adjustable size
                template = Image.open(template_file)
                font = ImageFont.truetype(font_file, font_size)
                
                # Generate prescription
                filled_prescription = filler.fill_prescription(
                    patient_data, template, font, coordinates=current_coordinates
                )
                
                if filled_prescription:
                    # Display preview
                    st.image(filled_prescription, caption="Preview")
                    
                    # Convert to PDF and offer download
                    pdf_bytes = io.BytesIO()
                    filled_prescription.save(pdf_bytes, format='PDF')
                    pdf_bytes.seek(0)
                    st.download_button(
                        "Download PDF",
                        pdf_bytes.getvalue(),
                        f"prescription_{name}_{date}.pdf",
                        "application/pdf"
                    )
            else:
                st.warning("Please upload both template and font files.")
    
    else:  # Batch Upload
        csv_file = st.file_uploader(
            "Upload CSV file with patient details",
            type=['csv']
        )
        
        if csv_file and template_file and font_file:
            df = pd.read_csv(csv_file)
            if st.button("Process Batch"):
                # Use the coordinates and font size set in Single Entry mode for batch processing
                batch_coordinates = {
                    'name': (st.session_state.name_x, st.session_state.name_y),
                    'age': (st.session_state.age_x, st.session_state.age_y),
                    'sex': (st.session_state.sex_x, st.session_state.sex_y),
                    'disease': (st.session_state.disease_x, st.session_state.disease_y),
                    'date': (st.session_state.date_x, st.session_state.date_y)
                }

                template = Image.open(template_file)
                font = ImageFont.truetype(font_file, st.session_state.get('font_size', 32))
                
                progress_bar = st.progress(0)
                processed_images = []
                
                for idx, row in df.iterrows():
                    patient_data = {
                        'name': row.get('name', ''),
                        'age': row.get('age', ''),
                        'sex': row.get('sex', 'ಪುರುಷ'),
                        'disease': row.get('disease', ''),
                        'date': row.get('date', datetime.now().strftime("%d/%m/%Y"))
                    }
                    
                    filled_prescription = filler.fill_prescription(
                        patient_data, template, font, coordinates=batch_coordinates
                    )
                    
                    if filled_prescription:
                        processed_images.append(filled_prescription)
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                # Save all images as a multi-page PDF
                if processed_images:
                    pdf_bytes = io.BytesIO()
                    # Save the first image
                    processed_images[0].save(
                        pdf_bytes,
                        format='PDF',
                        save_all=True,
                        append_images=processed_images[1:]  # Append the rest
                    )
                    pdf_bytes.seek(0)
                    
                    st.download_button(
                        "Download Combined PDF",
                        pdf_bytes.getvalue(),
                        "batch_prescriptions.pdf",
                        "application/pdf"
                    )

if __name__ == "__main__":
    main()
