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
    main = alt.Chart(filtered_df).mark_bar().encode(
        y=alt.Y(
            "Bacteria:N",
            sort="-x", #order by MIC hi-lo
            title="Bacteria"
        ),
        x=alt.X(
            "log_MIC:Q",
            title="log₁₀(MIC μg/mL)"
        ),
        color=alt.Color(
            "log_MIC:Q",
            scale=alt.Scale(scheme="spectral", reverse=True), #darker = more potent
            legend=alt.Legend(title="log(MIC)")
        ),
        tooltip=["Bacteria", "Antibiotic", "MIC", "Gram_Staining", "Genus"]
    )

    bars = main.mark_bar()    

# line of refrence for negative MIC values

    reference_line=alt.Chart(pd.DataFrame({"log_MIC": [0]})).mark_rule(
        color="black",
        strokeDash=[4, 4]
    ).encode(x="x:Q")

    #resistance zone
    high_resistance = alt.Chart(pd.DataFrame({
        "x": [2],  # = log10(100)
    })).mark_rule(
        strokeDash=[6, 4],
        color="black"
        ).encode(x="x:Q")

    final = alt.layer(bars, reference_line, high_resistance).properties(
        width=700,
        height=600,
        title="Antibiotic Potency Against Bacterial Species"
    )

    st.altair_chart(final, use_container_width=True)
else:
    st.warning("No data matches the selected filters.")






# Surrounding explanation
st.markdown("""
🔹 Notice how **Penicillin** has much **higher MIC values** for **Gram-negative** strains.  
🔹 This suggests it's far less effective due to the extra outer membrane found in Gram-negative bacteria.

Meanwhile, **Neomycin** and **Streptomycin** appear to perform more consistently across both groups.
""")



# final comments: 
# The lower MIC, the more potent the antibiotic!

#Add highlight Penicillin's high MIC in Gram-negative) ?
# highlight = alt.Chart(pd.DataFrame({
#     "Antibiotic": ["Penicillin"],
#     "Gram_Staining": ["negative"],
#     "MIC": [850]
# })).mark_point(
#     shape="triangle", size=100, color="crimson"
# ).encode(
#     x=alt.X("Antibiotic", type="nominal"), #needed to manually specify type here.
#     y=alt.Y("MIC:Q")
# )

# st.altair_chart(overview_chart + highlight, use_container_width=True)


