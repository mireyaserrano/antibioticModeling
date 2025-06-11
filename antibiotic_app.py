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
#filters
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
    (df_melted["Gram_Staining"].isin([selected_gram_type])) &
    (df_melted["Genus"].isin(selected_genus))
]

if filtered_df.empty:
    st.warning("No data matches your filters. Try adjusting your selections.")
else:
    if len(filtered_df) < 3:
        st.info("Only a few bacteria match your filters, so the chart may look compressed.")

    base = alt.Chart(filtered_df).properties(height=150)
# Base of faceted bar chart
    bar_chart = base.mark_bar().encode(
        x=alt.X("log_MIC:Q", title="Log MIC)", scale=alt.Scale(domain=[-3, 3])),
        y=alt.Y("Bacteria:N", sort='-x', title="Bacteria"),
        color=alt.Color("Antibiotic:N", title="Antibiotic"),
        tooltip=["Bacteria", "Antibiotic", "MIC", "Gram_Staining", "Genus"]
    )

# Vertical reference line at MIC = 1 (log_MIC = 0)
    center_line = alt.Chart(filtered_df).mark_rule(
        color="black",
        strokeDash=[4, 4]
    ).transform_calculate(
        x="0"
    ).encode(x="x:Q")

# Labels for "<-- More Effective / Less Effective -->"

    if not filtered_df.empty:
        top_bacteria = filtered_df["Bacteria"].iloc[0]

    center_label = alt.Chart(pd.DataFrame({
        "x": [-1, 1],
        "y": [top_bacteria] * 2,
        "label": ["<-- More Effective", "Less Effective -->"],
    })).mark_text(
        align='center',
        baseline="top",
        fontStyle="italic",
        fontSize=11,
        dy=-25
    ).encode(
        x="x:Q",
        y=alt.Y("y:N", sort='-x'),
        text="label"
    )

# line at MIC = 100 (log_MIC = 2)
    resistance_line = alt.Chart(filtered_df).mark_rule(
        strokeDash=[6, 4],
        color="red"
    ).transform_calculate(
        
        x="2"
    ).encode(x="x:Q")


    # Highly effective threshold at log_MIC = -1
    effective_line = alt.Chart(filtered_df).mark_rule(
        strokeDash=[6, 4],
        color="green"
    ).transform_calculate(
        x="-1"
    ).encode(x="x:Q")


# Combining layers
    full_layer = (
        bar_chart +
        center_line +
        center_label +
        resistance_line +
        # resistance_label +
        # effective_label +
        effective_line
    )
    

# Facet by Antibiotic
    faceted_chart = full_layer.facet(
        row=alt.Row("Antibiotic:N", sort=["Penicillin", "Streptomycin", "Neomycin"], title=None)
    ).resolve_scale(
        x="shared",
        y="independent"
    ).properties(
        title="Antibiotic Effectiveness by Bacteria",
        bounds="flush"
    )

# Display all
    st.altair_chart(faceted_chart, use_container_width=True)
    st.markdown("""
    🔹 The red dotted line indicates a high resistancy threshold, the green dotted line indicates a high effectiveness threshold. \n
    """)
    with st.expander("💡 Filter Navigation Tips"):
        st.markdown("""
        - The **Gram Type** toggle helps distinguish between bacteria with different cell wall structures.
        - Use the **Genus selector** to explore specific types of bacteria or narrow your focus.
        - Try starting with all types, then refine based on what stands out!
        """)

    with st.expander("🔬 Understanding MIC & Thresholds"):
        st.markdown("""
        - **MIC (Minimum Inhibitory Concentration)** is the lowest antibiotic concentration that stops bacterial growth, a few lines are constant for convenience.
        - The chart uses **log₁₀(MIC)** to better compare ranges:
            - Values **< 0** → *More effective antibiotic*
            - Values **> 2** → *Possible resistance*
        - Vertical lines in the chart show:
            - `log(MIC) = 0`: baseline effectiveness
            - `log(MIC) = 2`: resistance threshold
        """)

    with st.expander("📊 Key Insight"):
        st.markdown("""
        - **Penicillin** is generally **highly effective** against **Gram-positive** bacteria.
        - **Gram-negative** bacteria often resist Penicillin due to their **outer membrane**.
        - **Streptomycin** and **Neomycin** show broader effectiveness, but vary across genera.\n
        🔹 Notice how **Penicillin** has much **higher MIC values** for **Gram-negative** strains.\n  
        🔹 This suggests it's far less effective due to the extra outer membrane found in Gram-negative bacteria.\n
        🔹 **Neomycin** and **Streptomycin** appear to perform more consistently across both groups.

        """)