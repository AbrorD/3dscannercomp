import streamlit as st
import pandas as pd
import json
import os
import subprocess
import time

# Set Page Config
st.set_page_config(
    page_title="3D Scanner Tech Specs Aggregator & Scraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (HSL Palette & Glassmorphism)
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, .title-text {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Metric Cards Custom Styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #00F2FE;
        box-shadow: 0 8px 30px rgba(0, 242, 254, 0.2);
    }
    .metric-title {
        color: #8A99AD;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .metric-val {
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 5px;
    }
    
    /* Product Detail Cards */
    .product-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Badge styling */
    .badge-metrology {
        background-color: #00F2FE;
        color: #0F172A;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        margin-right: 5px;
    }
    .badge-wireless {
        background-color: #38EF7D;
        color: #0F172A;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        margin-right: 5px;
    }
    .badge-brand {
        background-color: rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        margin-right: 5px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

DATA_FILE = "scanners_data.json"
LOG_FILE = "scraper_log.txt"

# Load Scanners Function
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# App Initialization
scanners = load_data()
df = pd.DataFrame(scanners)

# Sidebar Header
st.sidebar.markdown("<h2 style='margin-bottom:5px;'>⚙️ Controls & Filters</h2>", unsafe_allow_html=True)
st.sidebar.write("Configure details for scraping & dashboard filtering.")

# Sidebar Scraper Trigger Action
st.sidebar.markdown("---")
st.sidebar.subheader("🕷️ Web Scraper Engine")
if st.sidebar.button("Run Scraper / Scrape Ulang", key="run_scraper"):
    log_area = st.empty()
    status_box = st.sidebar.info("Running crawling script in background...")
    
    # Run the scraping engine script
    try:
        process = subprocess.Popen(["python", "scraper.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Read scraper log periodically to show in UI
        for i in range(25):
            time.sleep(1)
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as lf:
                    logs = lf.read()
                log_area.code(logs[-1500:], language="bash")
            
            # Check if finished
            if process.poll() is not None:
                break
        
        process.wait()
        status_box.empty()
        
        # Reload database
        scanners = load_data()
        df = pd.DataFrame(scanners)
        st.sidebar.success("Scraper executed successfully! Data refreshed.")
        st.rerun()
        
    except Exception as e:
        st.sidebar.error(f"Error starting scraper: {str(e)}")

# Sidebar filter for price range
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Filter Harga (Rupiah)")
if len(df) > 0:
    min_p = int(df['price_idr'].min())
    max_p = int(df['price_idr'].max())
    price_range = st.sidebar.slider(
        "Pilih rentang harga:",
        min_value=min_p,
        max_value=max_p,
        value=(min_p, max_p),
        step=500000
    )
    formatted_min = f"Rp {price_range[0]:,}".replace(",", ".")
    formatted_max = f"Rp {price_range[1]:,}".replace(",", ".")
    st.sidebar.caption(f"Terpilih: **{formatted_min}** s/d **{formatted_max}**")

# Sidebar instruction for Google Sheets
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Google Sheets Export Guide")
st.sidebar.markdown(
    """
    1. Click the **Export to CSV** or **Excel** button below the table.
    2. Go to **[Google Sheets](https://sheets.google.com)**.
    3. Create a blank spreadsheet.
    4. Click **File -> Import -> Upload**.
    5. Choose the downloaded file and select **Replace spreadsheet**.
    """
)

# Header Section
col_head_1, col_head_2 = st.columns([4, 1])
with col_head_1:
    st.markdown("<h1>3D SCANNER INTELLIGENCE HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.15rem; color:#8A99AD; margin-top:-10px;'>Automated Spec Tracker & Marketing Intelligence Dashboard for 3D Scanners</p>", unsafe_allow_html=True)
with col_head_2:
    # Metadata info
    last_mod = "Unknown"
    if os.path.exists(DATA_FILE):
        last_mod = time.strftime('%d %b %Y, %H:%M:%S', time.localtime(os.path.getmtime(DATA_FILE)))
    st.write(f"**Database Last Update:**\n`{last_mod}`")

# Telemetry Overview Cards
st.markdown("### 📊 Market Snapshot")
col1, col2, col3, col4 = st.columns(4)

total_models = len(df)
metrology_grade = df['metallurgy_certificate'].apply(lambda x: 'yes' in str(x).lower()).sum()
wireless_capable = df['wireless_support'].apply(lambda x: 'yes' in str(x).lower()).sum()
unique_brands = df['brand'].nunique() if total_models > 0 else 0

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total Scanner Models</div>
            <div class="metric-val">{total_models}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Metrology / Certified Scanners</div>
            <div class="metric-val">{metrology_grade}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Wireless Scanners</div>
            <div class="metric-val">{wireless_capable}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Active Brands Tracked</div>
            <div class="metric-val">{unique_brands}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main Dashboard Content Area
tab_table, tab_explorer, tab_compare = st.tabs(["📋 Specifications Database", "🔍 Product Details Explorer", "⚖️ Side-by-Side Comparison"])

with tab_table:
    st.markdown("### 🔍 Technical Specifications Database")
    
    # Filter Row
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        search_query = st.text_input("🔍 Search model or keyword...", "")
    with col_f2:
        brand_list = ["All"] + list(df['brand'].unique()) if total_models > 0 else ["All"]
        filter_brand = st.selectbox("Filter by Brand", brand_list)
    with col_f3:
        filter_metrology = st.selectbox("Metrology Certificate", ["All", "Yes (Certified)", "No"])
    with col_f4:
        filter_wireless = st.selectbox("Wireless Capability", ["All", "Yes (Wireless support)", "No"])

    # Applying filters
    filtered_df = df.copy()
    
    # Filter by price range from sidebar
    if len(df) > 0:
        filtered_df = filtered_df[
            (filtered_df['price_idr'] >= price_range[0]) & 
            (filtered_df['price_idr'] <= price_range[1])
        ]
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['model'].str.contains(search_query, case=False) |
            filtered_df['scanning_mode'].str.contains(search_query, case=False) |
            filtered_df['marketing_focus'].str.contains(search_query, case=False)
        ]
        
    if filter_brand != "All":
        filtered_df = filtered_df[filtered_df['brand'] == filter_brand]
        
    if filter_metrology == "Yes (Certified)":
        filtered_df = filtered_df[filtered_df['metallurgy_certificate'].str.contains("yes|certified|VDI/VDE|ISO", case=False)]
    elif filter_metrology == "No":
        filtered_df = filtered_df[~filtered_df['metallurgy_certificate'].str.contains("yes|certified|VDI/VDE|ISO", case=False)]
        
    if filter_wireless == "Yes (Wireless support)":
        filtered_df = filtered_df[filtered_df['wireless_support'].str.contains("yes|built-in", case=False)]
    elif filter_wireless == "No":
        filtered_df = filtered_df[~filtered_df['wireless_support'].str.contains("yes|built-in", case=False)]

    # Sort by price ascending and format currency
    if len(filtered_df) > 0:
        filtered_df = filtered_df.sort_values(by="price_idr", ascending=True)
        filtered_df['Harga (Rupiah)'] = filtered_df['price_idr'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

    # Rename Columns for Indonesian/Indo-English layout readability in UI
    display_df = filtered_df.rename(columns={
        "brand": "Brand",
        "model": "Model",
        "price_source": "Sumber Harga",
        "scanning_mode": "Scanning Mode",
        "accuracy": "Accuracy",
        "scanning_speed": "Scanning Speed",
        "resolution": "Resolution",
        "metallurgy_certificate": "Metrology Certificate",
        "min_scanning_volume": "Min Scan Volume",
        "working_distance": "Working Distance",
        "texture_mapping": "Color Mapping",
        "size_weight": "Volume / Size & Weight",
        "min_spec": "Min Device Spec (PC/Mac)",
        "wireless_support": "Wireless Support",
        "marketing_focus": "Marketing Focus",
        "source_url": "Source URL"
    })

    # Reorder columns to show Brand, Model, Harga, and Sumber Harga first
    if len(display_df) > 0:
        cols_order = [
            "Brand", "Model", "Harga (Rupiah)", "Sumber Harga", "Scanning Mode", "Accuracy", 
            "Scanning Speed", "Resolution", "Metrology Certificate", "Min Scan Volume", 
            "Working Distance", "Color Mapping", "Volume / Size & Weight", 
            "Min Device Spec (PC/Mac)", "Wireless Support", "Marketing Focus", "Source URL"
        ]
        cols_to_use = [c for c in cols_order if c in display_df.columns]
        display_df = display_df[cols_to_use]

    # Render interactive table
    st.dataframe(display_df, use_container_width=True)

    # Export Section
    st.markdown("### 📥 Export Options")
    col_ex1, col_ex2, _ = st.columns([1.5, 1.5, 5])
    
    # Export to CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    with col_ex1:
        st.download_button(
            label="📄 Export to Google Sheets (CSV)",
            data=csv_data,
            file_name="3d_scanners_specs_data.csv",
            mime="text/csv",
            help="Download as CSV file. You can import this file directly into Google Sheets."
        )
        
    # Export to Excel
    try:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='3D Scanners Specs')
        excel_data = buffer.getvalue()
        with col_ex2:
            st.download_button(
                label="📊 Export to Excel (.xlsx)",
                data=excel_data,
                file_name="3d_scanners_specs_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download as formatted Excel Spreadsheet."
            )
    except Exception as e:
        with col_ex2:
            st.error("Excel module not installed or error generating Excel file.")

with tab_explorer:
    st.markdown("### 🔍 Product Details & Marketing Insights Explorer")
    
    if len(df) > 0:
        # Selection of product
        selected_model = st.selectbox("Select a Scanner Model to Analyze", df['model'].unique())
        
        # Get product details
        prod = df[df['model'] == selected_model].iloc[0]
        
        is_metrology = 'yes' in str(prod['metallurgy_certificate']).lower() or 'certified' in str(prod['metallurgy_certificate']).lower()
        is_wireless = 'yes' in str(prod['wireless_support']).lower() or 'built-in' in str(prod['wireless_support']).lower()
        
        metrology_badge = '<span class="badge-metrology">Metrology Grade</span>' if is_metrology else '<span class="badge-brand" style="opacity: 0.6">Consumer Grade</span>'
        wireless_badge = '<span class="badge-wireless">Wireless Support</span>' if is_wireless else '<span class="badge-brand" style="opacity: 0.6">Wired Only</span>'
        brand_badge = f'<span class="badge-brand">{prod["brand"]}</span>'
        
        price_formatted = f"Rp {prod['price_idr']:,.0f}".replace(",", ".")
        
        # Beautiful layout for detail cards
        st.markdown(
            f"""
            <div class="product-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <div style="font-size:1.8rem; font-weight:700; color:#FFFFFF;">
                        {prod['model']} 
                        <span style="color:#00F2FE; font-size:1.3rem; font-weight:400; margin-left: 10px;">({price_formatted} - Sumber: {prod['price_source']})</span>
                    </div>
                    <div>
                        {brand_badge}
                        {metrology_badge}
                        {wireless_badge}
                    </div>
                </div>
                <div style="font-size:1.05rem; color:#A5B4FC; margin-bottom: 20px; line-height:1.6;">
                    <strong>🎯 Apa yang Dimarketingkan (USP):</strong><br>
                    {prod['marketing_focus']}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        col_det1, col_det2 = st.columns(2)
        with col_det1:
            st.markdown("#### ⚙️ Technical Specifications")
            specs_table = {
                "Specification": [
                    "Harga Estimasi", "Sumber Harga", "Scanning Mode", "Accuracy", "Scanning Speed", "Resolution", 
                    "Working Distance", "Minimum Scan Volume", "Color/Texture Mapping"
                ],
                "Value": [
                    price_formatted, prod['price_source'], prod['scanning_mode'], prod['accuracy'], prod['scanning_speed'], prod['resolution'],
                    prod['working_distance'], prod['min_scanning_volume'], prod['texture_mapping']
                ]
            }
            st.table(pd.DataFrame(specs_table))
            
        with col_det2:
            st.markdown("#### 💻 Physical & Device Requirements")
            req_table = {
                "Parameter": [
                    "Physical Size / Weight", "Min Device Specification (PC/Mac)", "Wireless Support Details", "Metrology Certificate Details"
                ],
                "Value": [
                    prod['size_weight'], prod['min_spec'], prod['wireless_support'], prod['metallurgy_certificate']
                ]
            }
            st.table(pd.DataFrame(req_table))
            
            st.markdown(f"🔗 **Official Product Link:** [Visit Brand Website]({prod['source_url']})")
    else:
        st.info("No scanner products found in database. Run the scraper first.")

with tab_compare:
    st.markdown("### ⚖️ Side-by-Side Comparison Matrix")
    
    if len(df) > 1:
        selected_compare = st.multiselect(
            "Select 2 or more Scanners to Compare", 
            df['model'].unique(),
            default=list(df['model'].unique()[:2])
        )
        
        if len(selected_compare) >= 2:
            compare_df = df[df['model'].isin(selected_compare)].copy()
            
            # Format price and rename columns before transposing
            compare_df['price_idr'] = compare_df['price_idr'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            compare_df = compare_df.rename(columns={
                "brand": "Brand",
                "price_idr": "Harga Estimasi (Rupiah)",
                "price_source": "Sumber Harga",
                "scanning_mode": "Scanning Mode",
                "accuracy": "Accuracy",
                "scanning_speed": "Scanning Speed",
                "resolution": "Resolution",
                "metallurgy_certificate": "Metrology Certificate",
                "min_scanning_volume": "Min Scan Volume",
                "working_distance": "Working Distance",
                "texture_mapping": "Color Mapping",
                "size_weight": "Volume / Size & Weight",
                "min_spec": "Min Spec Device (PC/Mac)",
                "wireless_support": "Wireless Support",
                "marketing_focus": "Marketing Focus",
                "source_url": "Source URL"
            })
            
            # Pivot table for comparison
            compare_df = compare_df.set_index('model').T
            
            # Display comparison matrix
            st.dataframe(compare_df, use_container_width=True)
        else:
            st.warning("Please select at least 2 scanner models to compare.")
    else:
        st.info("Insufficient data for comparison. Run the scraper first.")
