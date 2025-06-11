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

# # filter options
# selected_antibiotics = st.multiselect(
#     "*Choose an antibiotic(s) to start analyzing:*",
#     options = df_melted["Antibiotic"].unique(),
#     default = ["Penicillin", "Streptomycin", "Neomycin"]
#     )
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
    # (df_melted["Antibiotic"].isin(selected_antibiotics)) &
    (df_melted["Gram_Staining"].isin([selected_gram_type])) &
    (df_melted["Genus"].isin(selected_genus))
]

if filtered_df.empty:
    st.warning("No data matches your filters. Try adjusting your selections.")
else:
    base = alt.Chart(filtered_df) 
    # Base faceted bar chart
    bar_chart = base.mark_bar().encode(
        x=alt.X("log_MIC:Q", title="Log MIC)", scale=alt.Scale(domain=[-3, 3])),
        y=alt.Y("Bacteria:N", sort='-x', title="Bacteria"),
        color=alt.Color("Antibiotic:N", legend=None),
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
    center_label = alt.Chart(pd.DataFrame({
        "x": [-1, 1],
        "y": [filtered_df["Bacteria"].iloc[0]] * 2,
        "label": ["<-- More Effective", "Less Effective -->"]
    })).mark_text(
        align='center',
        baseline="bottom",
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

    # Label for high resistance 
    top_bacteria = filtered_df["Bacteria"].iloc[0]
    resistance_label = alt.Chart(pd.DataFrame({
        "x": [2],
        "y": [top_bacteria],
        "label": ["→ High Resistancy"]
    })).mark_text(
        align='left',
        baseline='middle',
        dx=6,
        dy=120,
        color="red",
        fontWeight="bold"
    ).encode(
        x="x:Q",
        y=alt.Y("y:N", sort='-x'),
        text="label:N"
    )

    # Combine layers
    full_layer = (
        bar_chart +
        center_line +
        center_label +
        resistance_line +
        resistance_label
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

    # Display
    st.altair_chart(faceted_chart, use_container_width=True)





#
# 1st rendering

# if not filtered_df.empty:
#     main = alt.Chart(filtered_df).mark_bar().encode(
#         x=alt.X("log_MIC:Q", title="log₁₀(MIC μg/mL)"),
        
#         y=alt.Y("Bacteria:N", sort="-x", #order by MIC hi-lo
#             title="Bacteria"),

#         color=alt.Color(
#             "Antibiotic:N",
#             scale=alt.Scale(scheme="set1"),
#             legend=alt.Legend(title="Antibiotic")
#         ),
#         tooltip=["Bacteria", "Antibiotic", "MIC", "Gram_Staining", "Genus"]
#     )  

#     center_line = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(
#         color="black",
#         strokeDash=[4, 4]
#     ).encode(x="x:Q")

#     #label center
#     center_label = alt.Chart(pd.DataFrame({
#         "x": [-1, 1],
#         "y": [filtered_df["Bacteria"].iloc[0]] * 2, #anchor at top bar
#         "label": ["<-- More Effective", "Less Effective -->"],
#         "dx": [-70, 70] #shift to format
#     })).mark_text(
#         align='center',
#         baseline="bottom",
#         fontStyle="italic",
#         fontSize=11,
#         dy=-25,
#     ).encode(
#         x="x:Q",
#         y=alt.Y("y:N", sort="-x"),
#         text="label"
#         # dx="dx:Q"
#     )

# #resistance zone
#     high_resistance = alt.Chart(pd.DataFrame({
#         "x": [2],  # = log10(100)
#     })).mark_rule(
#         strokeDash=[6, 4],
#         color="red"
#         ).encode(x="x:Q")
    
#     #label

#     resistant_label = alt.Chart(pd.DataFrame({
#         "x": [2],
#         "y": [filtered_df["Bacteria"].iloc[0]],  # Place near top bacterium in current view
#         "label": ["→ High Resistancy"]
#     })).mark_text(
#         align='left',
#         baseline='middle',
#         dx=6,  # shift text to the right
#         dy=120,
#         color="red",
#         fontWeight="bold"
#     ).encode(
#         x="x:Q",
#         y=alt.Y("y:N", sort="-x"),  # ensure y is interpreted as categorical
#         text="label"
#     )


#     final = alt.layer(main, high_resistance, resistant_label, center_line, center_label).properties(
#         width=700,
#         height=600,
#         title="Antibiotic Potency Against Bacteria"
#     )

#     st.altair_chart(final, use_container_width=True)
# else:
#     st.warning("No data matches the selected filters.")






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


