import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

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
df_melted["log_MIC"] = np.log10(df_melted["MIC"]) # base-10 logarithm of the MIC values column

st.title("Exploring Antibiotic Resistance")
st.header("Burtin's Antibiotic Dataset!")

# overview introduction
st.markdown("""
    In 1951, Robert Burtin tested the power of three antibiotics against 16 types of bacteria:\n
    :sparkles: ***Penicillin***, ***Streptomycin***, and ***Neomycin*** :sparkles:
            
    This dataset captures their effectiveness using **MIC (Minimum Inhibitory Concentration)** values.\n\n
    Note a bacteria's  **Gram stain classification** — either **positive** or **negative** — and how it plays a major role in how well antibiotics work.\n
    Use the filters to start exploring :)
""")

# filter options
selected_antibiotics = st.multiselect(
    "*Choose an antibiotic(s) to start analyzing:*",
    options = df_melted["Antibiotic"].unique(),
    default = ["Penicillin", "Streptomycin", "Neomycin"]
    )
selected_gram_type = st.radio(
    "Select Gram Type", ["positive", "negative"]
)
selected_genus = st.multiselect(
    "Select Bacterial Genus",
    options = sorted(df_melted["Genus"].unique()),
    default = df_melted["Genus"].unique()
)

# filtering applications
filtered_df = df_melted[
    (df_melted["Antibiotic"].isin(selected_antibiotics)) &
    (df_melted["Gram_Staining"].isin([selected_gram_type])) &
    (df_melted["Genus"].isin(selected_genus))
]

# visual rendering

if not filtered_df.empty:
    main_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X(
            "Bacteria:N",
            sort="-y", #highest y-axis values (MIC) appear most->least resistant
            title="Bacteria"
        ),
        y=alt.Y(
            "log_MIC:Q",
            title="log₁₀(MIC μg/mL)"
        ),
        color=alt.Color(
            "log_MIC:Q",
            scale=alt.Scale(scheme="spectral", reverse=True), #darker = more potent
            legend=alt.Legend(title="log(MIC)")
        ),
        tooltip=["Bacteria", "Antibiotic", "MIC", "Gram_Staining", "Genus"]
    ).facet(
        column=alt.Column("Antibiotic:N", title="Antibiotic")
    ).properties(
        width=220,
        height=400,
        title="Success of Antibiotics"
    )

# line of refrence for negative MIC values

reference_line=alt.Chart(pd.DataFrame({"log_MIC": [0]})).mark_rule(
    color="black", strokeDash=[4, 4]
).encode(y='y:Q')
