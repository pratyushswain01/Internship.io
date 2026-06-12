import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Fullscreen, LocateControl
import plotly.express as px

# ========================= CONFIG =========================
st.set_page_config(
    page_title="Mineral Resource Finder | India",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3.2rem; 
        color: #1E3A8A; 
        font-weight: 700; 
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        text-align: center;
        color: #475569;
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        width: 100%; 
        height: 3.2rem; 
        font-weight: 600;
        border-radius: 8px;
    }
    .footer {
        text-align: center;
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 2rem;
        padding: 1.5rem;
        border-top: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# ========================= ANIMATED LOGO & BANNER =========================
def display_header():
    # Animated logo using public GIF (you can replace with your own local GIF)
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image(
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdW1pczA5b2h5c3h5b3Z5Z3F3Z2F4Z2F4Z2F4Z2F4Z2F4Z2F4Z2F4Z2F4/a mining pickaxe or mineral animation",
            width=120  # Placeholder - replace URL with real animated GIF
        )
    with col_title:
        st.markdown('<h1 class="main-header">⛏️ Mineral Resource Finder</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Discover • Explore • Analyze India\'s Mineral Wealth</p>', unsafe_allow_html=True)
    
    # Hero Banner (replace with your own image URL)
    st.image(
        "https://source.unsplash.com/1600x400/?india-mines,landscape",
        use_column_width=True
    )

# ========================= LARGE DATASET =========================
@st.cache_data
def load_mineral_data() -> pd.DataFrame:
    data = {
        "Mineral_Name": [
            "Iron Ore", "Iron Ore", "Coal", "Coal", "Bauxite", "Copper Ore", "Gold", 
            "Manganese Ore", "Chromite", "Diamond", "Limestone", "Zinc Ore", 
            "Lead Ore", "Graphite", "Natural Gas", "Uranium", "Mica", "Dolomite",
            # Expanded for larger database
            "Iron Ore", "Coal", "Bauxite", "Copper Ore", "Manganese Ore", "Chromite",
            "Gold", "Limestone", "Zinc Ore", "Diamond", "Petroleum", "Gypsum",
            "Phosphorite", "Kyanite", "Garnet", "Fluorite", "Thorium", "Vermiculite",
        ] * 3,  # Tripling for larger size (~100+ entries)
        "State": [
            "Odisha", "Jharkhand", "Jharkhand", "Odisha", "Odisha", "Rajasthan", "Karnataka",
            "Odisha", "Odisha", "Madhya Pradesh", "Andhra Pradesh", "Rajasthan",
            "Rajasthan", "Jharkhand", "Gujarat", "Jharkhand", "Andhra Pradesh", "Chhattisgarh",
            "Chhattisgarh", "West Bengal", "Chhattisgarh", "Madhya Pradesh", "Karnataka", "Karnataka",
            "Jharkhand", "Rajasthan", "Rajasthan", "Madhya Pradesh", "Assam", "Rajasthan",
            "Rajasthan", "Andhra Pradesh", "Tamil Nadu", "Gujarat", "Kerala", "Andhra Pradesh",
        ] * 3,
        "District": [
            "Keonjhar", "West Singhbhum", "Dhanbad", "Angul", "Koraput", "Udaipur", "Raichur",
            "Keonjhar", "Sukinda", "Panna", "Kurnool", "Zawar", "Zawar", "Palamu", "Surat",
            "East Singhbhum", "Nellore", "Durg", "Dantewada", "Raniganj", "Surguja", "Balaghat",
            "Sandur", "Hassan", "East Singhbhum", "Udaipur", "Zawar", "Panna", "Dibrugarh",
            "Jodhpur", "Banswara", "Anantapur", "Tirunelveli", "Bharuch", "Alappuzha", "Visakhapatnam",
        ] * 3,
        "Latitude": [
            21.85, 22.55, 23.80, 20.85, 18.82, 24.58, 16.20,
            21.85, 20.95, 24.72, 15.83, 24.35, 24.35, 23.45, 21.17,
            22.80, 14.45, 21.20, 18.90, 23.62, 23.05, 21.95,
            15.10, 13.00, 22.80, 24.58, 24.35, 24.72, 27.48,
            26.30, 23.55, 14.68, 8.73, 21.70, 9.50, 17.68,
        ] * 3,
        "Longitude": [
            85.55, 85.82, 86.43, 85.10, 82.72, 73.68, 77.35,
            85.55, 85.92, 80.18, 78.03, 73.75, 73.75, 84.32, 72.83,
            86.20, 79.98, 81.28, 81.35, 87.10, 83.18, 80.75,
            76.55, 76.10, 86.20, 73.68, 73.75, 80.18, 94.92,
            73.05, 74.45, 77.60, 77.70, 73.00, 76.35, 83.30,
        ] * 3,
        "Estimated_Reserve": [
            "Very High", "Very High", "Very High", "High", "High", "Medium", "Low",
            "High", "High", "Low", "High", "Medium", "Medium", "Medium", "High",
            "Low", "Medium", "Medium", "High", "Medium", "Medium", "High",
            "High", "Medium", "Low", "High", "Medium", "Low", "High",
            "Medium", "Low", "Medium", "Medium", "Medium", "Low", "Medium",
        ] * 3,
    }
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
    return df

# ========================= FILTER =========================
def filter_minerals(df: pd.DataFrame, query: str, selected_minerals: list, selected_states: list) -> pd.DataFrame:
    filtered = df.copy()
    if query and query.strip():
        q = query.strip().lower()
        filtered = filtered[
            filtered["State"].str.lower().str.contains(q, na=False) |
            filtered["District"].str.lower().str.contains(q, na=False)
        ]
    if selected_minerals:
        filtered = filtered[filtered["Mineral_Name"].isin(selected_minerals)]
    if selected_states:
        filtered = filtered[filtered["State"].isin(selected_states)]
    return filtered

# ========================= INTERACTIVE MAP =========================
def create_mineral_map(filtered_df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron")
    MarkerCluster().add_to(m)
    Fullscreen().add_to(m)
    LocateControl().add_to(m)
    
    colors = {"Very High": "darkred", "High": "red", "Medium": "orange", "Low": "blue"}
    
    for _, row in filtered_df.iterrows():
        emoji = {
            "Iron Ore": "⛏️", "Coal": "⚒️", "Bauxite": "🪨", "Copper Ore": "🔶",
            "Gold": "✨", "Manganese Ore": "🟫", "Chromite": "⚫", "Diamond": "💎",
            "Limestone": "🏔️", "Zinc Ore": "⚪", "Natural Gas": "🔥"
        }.get(row["Mineral_Name"], "⛏️")
        
        popup_html = f"""
        <div style="font-family: Arial; min-width: 280px;">
            <h4 style="margin:5px 0; color:#1E3A8A;">{emoji} {row['Mineral_Name']}</h4>
            <b>State:</b> {row['State']}<br>
            <b>District:</b> {row['District']}<br>
            <b>Reserve:</b> {row['Estimated_Reserve']}
        </div>
        """
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{emoji} {row['Mineral_Name']} - {row['District']}",
            icon=folium.Icon(color=colors.get(row["Estimated_Reserve"], "gray"), icon="info-sign", prefix="fa")
        ).add_to(m)
    
    if len(filtered_df) > 0:
        m.fit_bounds([
            [filtered_df["Latitude"].min() - 1, filtered_df["Longitude"].min() - 1],
            [filtered_df["Latitude"].max() + 1, filtered_df["Longitude"].max() + 1]
        ])
    return m

# ========================= MAIN APP =========================
def main():
    display_header()
    
    df = load_mineral_data()
    
    # Sidebar Filters
    with st.sidebar:
        st.header("🔍 Advanced Filters")
        search_query = st.text_input("Search State / District", placeholder="Odisha or Dhanbad")
        
        minerals_list = sorted(df["Mineral_Name"].unique())
        selected_minerals = st.multiselect("Select Minerals", options=minerals_list)
        
        states_list = sorted(df["State"].unique())
        selected_states = st.multiselect("Select States", options=states_list)
        
        st.divider()
        st.metric("Total Deposits", len(df))
        st.caption("Comprehensive Indian Mineral Database")
    
    # Apply Filters
    filtered_df = filter_minerals(df, search_query, selected_minerals, selected_states)
    
    if filtered_df.empty and (search_query or selected_minerals or selected_states):
        st.error("❌ No results found. Please adjust your filters.")
    else:
        if filtered_df.empty:
            filtered_df = df.copy()
        
        st.success(f"✅ Displaying **{len(filtered_df)}** mineral deposits")
        
        tab1, tab2, tab3 = st.tabs(["📋 Data Table", "🗺️ Interactive Map", "📊 Analytics"])
        
        with tab1:
            st.dataframe(
                filtered_df[["Mineral_Name", "State", "District", "Estimated_Reserve"]],
                use_container_width=True, 
                hide_index=True
            )
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "mineral_resources.csv", "text/csv")
        
        with tab2:
            st.subheader("🗺️ Interactive Mineral Map")
            m = create_mineral_map(filtered_df)
            st_folium(m, width=900, height=600, returned_objects=[])
        
        with tab3:
            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.bar(filtered_df["State"].value_counts().head(10), 
                             title="Top States by Deposits")
                st.plotly_chart(fig1, use_container_width=True)
            with col_b:
                fig2 = px.pie(filtered_df, names="Estimated_Reserve", title="Reserve Distribution")
                st.plotly_chart(fig2, use_container_width=True)
            
            fig3 = px.bar(filtered_df["Mineral_Name"].value_counts().head(12), 
                         title="Mineral Distribution")
            st.plotly_chart(fig3, use_container_width=True)
    
    # Full Database
    with st.expander("📊 View Complete Database"):
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <strong>Created and Designed by Rudra Narayan Swain</strong><br>
        Mineral Resource Finder • Interactive Web Application<br>
        Built with Streamlit • Folium • Plotly • Pandas<br>
        <em>Data for demonstration and educational purposes only</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()