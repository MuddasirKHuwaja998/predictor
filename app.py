import streamlit as st
import joblib
import base64

# Load the trained models (ensure the file paths are correct)
model_left = joblib.load('model_decidera_left.pkl')
model_right = joblib.load('model_decidera_right.pkl')

# Background image setup
def add_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{image_url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to display the logo using URL
def display_logo(logo_url):
    st.markdown(
        f"""
        <div style="text-align: center; padding: 40px; margin-bottom: 40px;">
            <img src="{logo_url}" style="width: 200px;" alt="Logo Otofarma">
        </div>
        """,
        unsafe_allow_html=True
    )

# Add background image
background_image_url = "https://www.otofarmaspa.com/wp-content/uploads/2023/05/Schermata-2023-05-04-alle-12.38.23.png"
add_background_image(background_image_url)

# Display the logo
logo_url = "https://www.otofarmaspa.com/wp-content/uploads/2022/11/cropped-Logo-otofarma-png-1.png"
display_logo(logo_url)

# Title and description in Italian
st.title("Previsione del Test Audiometrico")
st.write("Inserisci i valori delle frequenze per le orecchie sinistra e destra per determinare se l'udito è normale o se ci sono problemi.\n")

# Frequencies for input
frequency_bands = ["250 Hz", "500 Hz", "1000 Hz", "2000 Hz", "4000 Hz", "8000 Hz"]

# File path for the default file
file_path = r"C:\test.txt"

# Function to process the file and populate input fields
def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip().split()  # Read the file content and split by spaces or new lines
            # Ensure there are exactly 12 values, 6 for left ear and 6 for right ear
            if len(content) == 12:
                left_frequencies = list(map(float, content[:6]))
                right_frequencies = list(map(float, content[6:]))
                return left_frequencies, right_frequencies
            else:
                st.error("Il file deve contenere esattamente 12 valori.")
                return None, None
    except FileNotFoundError:
        st.error(f"Il file non è stato trovato nella posizione {file_path}.")
        return None, None

# Process the file automatically
left_frequencies, right_frequencies = process_file(file_path)

# Display the note before input fields
if left_frequencies is not None and right_frequencies is not None:
    st.markdown(
        f"""
        <div style="padding: 10px; background-color: #f2f2f2; border-radius: 8px; font-size: 14px; color: #555;">
            <strong>I valori delle frequenze sono stati estratti automaticamente dal file <code>{file_path}</code> e sono stati inseriti nei campi di input.</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

# If file not found or contains errors, allow manual input
if left_frequencies is None or right_frequencies is None:
    # Input fields for left ear frequencies if the file is not processed
    left_frequencies = [
        st.number_input(f"Orecchio Sinistro {band}", min_value=0.0, step=1.0, value=0.0, key=f"left_{band.replace(' ', '_')}")
        for band in frequency_bands
    ]

    # Input fields for right ear frequencies if the file is not processed
    right_frequencies = [
        st.number_input(f"Orecchio Destro {band}", min_value=0.0, step=1.0, value=0.0, key=f"right_{band.replace(' ', '_')}")
        for band in frequency_bands
    ]
else:
    # Prepopulate the input fields with values from the file
    left_frequencies = [
        st.number_input(f"Orecchio Sinistro {band}", min_value=0.0, step=1.0, value=left_frequencies[i], key=f"left_{band.replace(' ', '_')}")
        for i, band in enumerate(frequency_bands)
    ]


    right_frequencies = [
        st.number_input(f"Orecchio Destro {band}", min_value=0.0, step=1.0, value=right_frequencies[i], key=f"right_{band.replace(' ', '_')}")
        for i, band in enumerate(frequency_bands)
    ]

# Show file path information
st.write(f"### File Caricato Da: {file_path}")

# Button to predict
predict_button = st.button("Prevedi")

if predict_button:
    st.write("### Valori Inseriti:")
    st.write("**Frequenze Orecchio Sinistro:**", left_frequencies)
    st.write("**Frequenze Orecchio Destro:**", right_frequencies)

    # Ideal values for comparison
    ideal_values = [250, 500, 1000, 2000, 4000, 8000]

    # Calculate percentage deviation from ideal values
    def calculate_percentage_diff(input_frequencies):
        diffs = [abs(input_frequencies[i] - ideal_values[i]) for i in range(len(ideal_values))]
        max_deviation = max(ideal_values)  # Max frequency value is 8000
        percentages = [(diff / max_deviation) * 100 for diff in diffs]
        avg_percentage = sum(percentages) / len(percentages)  # Average percentage deviation
        return round(avg_percentage, 2)

    left_percentage_diff = calculate_percentage_diff(left_frequencies)
    right_percentage_diff = calculate_percentage_diff(right_frequencies)

    # Predictions
    prediction_left = model_left.predict([left_frequencies])[0]
    prediction_right = model_right.predict([right_frequencies])[0]

    # Custom result styling
    def result_box(content, is_problem):
        color = "red" if is_problem else "green"
        return f"""
        <div style="margin: 10px; padding: 15px; border-radius: 10px; background-color: {color}; color: white; font-weight: bold;">
            {content}
        </div>
        """

    # Display percentage deviations and predictions
    st.write("### Percentuale del Problema:")
    st.write(f"Orecchio Sinistro: {left_percentage_diff}%")
    st.write(f"Orecchio Destro: {right_percentage_diff}%")

    st.write("### Risultati della Previsione:")
    left_result = "Normale" if prediction_left == 0 else "Problema"
    right_result = "Normale" if prediction_right == 0 else "Problema"

    left_box = result_box(f"Previsione Orecchio Sinistro: {left_result}", prediction_left == 1)
    right_box = result_box(f"Previsione Orecchio Destro: {right_result}", prediction_right == 1)

    # Render results in boxes
    st.markdown(left_box, unsafe_allow_html=True)
    st.markdown(right_box, unsafe_allow_html=True)

# Note Section
with st.expander("Mostra Nota", expanded=False):
    st.markdown(
        """
        <div style="margin-top: 10px; padding: 15px; background-color: rgba(0, 128, 255, 0.1); border: 3px solid #0080FF; 
        border-radius: 15px; font-size: 16px; font-weight: bold; color: black; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
        <p><strong>Nota:</strong> Questo sistema utilizza modelli di machine learning per prevedere la presenza 
        di problemi uditivi in ​​base ai valori di frequenza audiometrica immessi.</p>
        <p>Le differenze rispetto ai valori ideali vengono calcolate per facilitare la diagnosi. Questo modello potrebbe non 
        essere accurato al 100%, inoltre il caricamento dell'app Web potrebbe richiedere alcuni minuti poiché non è a pagamento.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
