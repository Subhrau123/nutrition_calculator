import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Nutritional Value Calculator",
    page_icon="🍽️",
    layout="wide",
)

# ---------- DARK MODE CUSTOM THEME ----------
st.markdown(
    """
    <style>
    /* Main background */
    .main {
        background-color: #121212;
    }

    /* Content / card container */
    .block-container {
        background-color: #1E1E1E !important;
        padding-top: 1rem;
        padding-bottom: 2rem;
        border-radius: 14px;
    }

    /* Text colors */
    h1, h2, h3, h4, h5, h6, label, p, span, .stMarkdown, .stDataFrame {
        color: #E0E0E0 !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #181818 !important;
        border-right: 1px solid #333;
    }

    /* Metrics card */
    .metric-card {
        padding: 12px;
        background-color: #262626;
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.5);
    }

    /* Dropdown and input boxes */
    .stSelectbox, .stTextInput, .stSlider {
        background-color: #262626 !important;
        color: #E0E0E0 !important;
    }

    /* Buttons (if added later) */
    .stButton>button {
        background-color: #BB86FC;
        color: #1E1E1E;
        font-weight: bold;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "dishes.csv"


@st.cache_data
def load_dishes():
    """Load dishes and their nutritional values from CSV."""
    df = pd.read_csv(DATA_PATH)
    df["dish_lower"] = df["Dish"].str.lower()
    return df


def main():
    st.title("🍽️ Nutritional Value Calculator")

    st.write(
        """
        A simple **food nutrition lookup tool**.  
        Choose a dish or search by name to see **Calories, Protein, Carbs, and Fat**.  
        Use the slider to see values for multiple servings.
        """
    )

    try:
        dishes_df = load_dishes()
    except FileNotFoundError:
        st.error(
            "Error: 'dishes.csv' not found.\n\n"
            "Make sure it is inside: `nutrition_calculator/data/dishes.csv`"
        )
        return

  
    st.sidebar.header("⚙️ Controls")

    serving_count = st.sidebar.slider(
        "Number of servings", min_value=1, max_value=5, value=1, step=1
    )

    st.sidebar.markdown("---")
    st.sidebar.write(
        "**Tip:**\n- Use the text box to search by keyword like `biryani`, `paneer`, `rice`.\n"
        "- Use the slider to see nutrition for multiple servings."
    )

 
    st.subheader("1️⃣ Choose Your Dish")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        dish_list = sorted(dishes_df["Dish"].tolist())
        selected_dish = st.selectbox("Select from list:", dish_list)

    with col2:
        text_input_dish = st.text_input("Or type part of a dish name:")

   
    if text_input_dish.strip():
        query = text_input_dish.strip().lower()
        result_df = dishes_df[dishes_df["dish_lower"].str.contains(query)]
    else:
        query = selected_dish.lower()
        result_df = dishes_df[dishes_df["dish_lower"] == query]

    if result_df.empty:
        st.warning("⚠️ No matching dish found. Try a different name.")
        return

  
    display_df = result_df.drop(columns=["dish_lower"])

    st.subheader("2️⃣ Nutritional Table (per serving)")

    st.dataframe(
        display_df.set_index("Dish"),
        use_container_width=True,
    )

   
    row = result_df.iloc[0]

  
    nutrient_labels = ["Calories", "Protein_g", "Carbs_g", "Fat_g"]
    per_serving_values = [
        float(row["Calories"]),
        float(row["Protein_g"]),
        float(row["Carbs_g"]),
        float(row["Fat_g"]),
    ]

    total_values = [value * serving_count for value in per_serving_values]

    st.subheader(f"3️⃣ Nutrient Summary for {serving_count} serving(s) of {row['Dish']}")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔥 Calories", f"{total_values[0]:.1f} kcal", f"{per_serving_values[0]:.1f} / serving")
        st.markdown("</div>", unsafe_allow_html=True)

    with m2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💪 Protein", f"{total_values[1]:.1f} g", f"{per_serving_values[1]:.1f} / serving")
        st.markdown("</div>", unsafe_allow_html=True)

    with m3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🍚 Carbs", f"{total_values[2]:.1f} g", f"{per_serving_values[2]:.1f} / serving")
        st.markdown("</div>", unsafe_allow_html=True)

    with m4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🥑 Fat", f"{total_values[3]:.1f} g", f"{per_serving_values[3]:.1f} / serving")
        st.markdown("</div>", unsafe_allow_html=True)

 
    st.subheader("4️⃣ Interactive Nutrient Breakdown")

    plot_df = pd.DataFrame(
        {
            "Nutrient": nutrient_labels,
            "Amount": total_values,
        }
    )

    fig_plotly = px.bar(
        plot_df,
        x="Nutrient",
        y="Amount",
        text="Amount",
        title=f"Nutrients for {serving_count} serving(s) of {row['Dish']}",
    )
    fig_plotly.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_plotly.update_layout(yaxis_title="Amount", xaxis_title="Nutrient")

    st.plotly_chart(fig_plotly, use_container_width=True)

  
    with st.expander("Show static Matplotlib chart (for syllabus)"):
        fig, ax = plt.subplots()
        ax.bar(nutrient_labels, per_serving_values)
        ax.set_ylabel("Amount per serving")
        ax.set_title(f"Nutrients for 1 serving of {row['Dish']}")
        st.pyplot(fig)

 
    with st.expander("Explanation (for viva/teacher)"):
        st.write(
            """
            **Concepts used:**
            - Variables, data types, expressions (Unit I)
            - Functions (`load_dishes`, `main`), `if` conditions, loops (Unit II)
            - String operations (`lower`, `contains`) and list-like behaviour in Pandas (Unit III)
            - Pandas + CSV → tabular data handling (Unit V)
            - Matplotlib → static bar chart (Unit V, shown in expander)
            - Plotly + Streamlit → interactive, real-world style web UI (Unit VI)
            """
        )


if __name__ == "__main__":
    main()


