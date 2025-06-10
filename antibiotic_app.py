import streamlit as st
import pandas as pd
import altair as alt

# loading in all data:
data_url = "https://cdn.jsdelivr.net/npm/vega-datasets@1/data/burtin.json"
data = pd.read_json(data_url)

df = pd.DataFrame(data)
df_melted = df.melt(
    id_vars=["Bacteria", "Gram_Staining", "Genus"],
    value_vars=["Penicillin", "Streptomycin", "Neomycin"],
    var_name="Antibiotic",
    value_name="MIC"
)

st.header("🔎 How Effective Are These Antibiotics?")

st.title("Exploring Burtin's Antibiotic Dataset!")
# overview introduction
st.markdown("""
    Antibiotic Resistance: A Visual Data Story. \n
    In 1951, Robert Burtin tested the power of three antibiotics against 16 types of bacteria:\n
    :sparkles: ***Penicillin***, ***Streptomycin***, and ***Neomycin*** :sparkles:
            
    This dataset captures their effectiveness using **MIC (Minimum Inhibitory Concentration)** values.\n\n
    The lower MIC, the more potent the antibiotic!
    Note a bacteria's  **Gram stain classification** — either **positive** or **negative** — and how it plays a major role in how well antibiotics work.\n
    Use the filters to start exploring :)
""")




