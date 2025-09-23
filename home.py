import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime, date, timedelta
import json

st.set_page_config(page_title="🔐 API Data Fetcher & Visualizer", layout="wide")

# Initialize session state
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "form_fields" not in st.session_state:
    st.session_state.form_fields = [{"key": "", "value": ""}]
if "fetched_data" not in st.session_state:
    st.session_state.fetched_data = {}
if "endpoints" not in st.session_state:
    st.session_state.endpoints = []

st.title("🔐 API Data Fetcher & Visualizer")

# Sidebar menu
menu = st.sidebar.radio("Menu", ["Login", "Load Endpoints", "Fetch Data", "Visualize Data"])

# --- LOGIN PAGE ---
if menu == "Login":
    st.subheader("🔑 Login Form")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        api_url = st.text_input("API URL", value="https://bios.kemenkeu.go.id/api2/authenticate")
    
    with col2:
        if st.session_state.auth_token:
            st.success("✅ Already logged in!")
            st.code(st.session_state.auth_token[:50] + "...", language="text")
        else:
            st.info("Please login to continue")

    if st.button("🚀 Login", type="primary"):
        if username and password:
            try:
                with st.spinner("Authenticating..."):
                    response = requests.post(api_url, json={"username": username, "password": password})

                if response.status_code == 200:
                    try:
                        data = response.json()
                    except ValueError:
                        st.error("❌ Server did not return JSON")
                        st.text(response.text)
                        data = {}

                    if data.get("status") == "MSG20004":
                        st.success(f"✅ {data.get('message', 'Login success')}")
                        st.session_state.auth_token = data.get("token")
                        st.rerun()
                    else:
                        st.warning("⚠️ Login response not in expected format.")
                        st.json(data)
                else:
                    st.error(f"❌ Login failed: {response.status_code}")
                    st.text(response.text)

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
        else:
            st.warning("⚠️ Please enter both username and password.")

# --- LOAD ENDPOINTS PAGE ---
elif menu == "Load Endpoints":
    st.subheader("📂 Load Endpoints from File")
    
    # File uploader for keuangan.txt
    uploaded_file = st.file_uploader("Upload keuangan.txt", type=['txt'])
    
    if uploaded_file is not None:
        content = str(uploaded_file.read(), "utf-8")
        endpoints = [line.strip() for line in content.split('\n') if line.strip()]
        st.session_state.endpoints = endpoints
        
        st.success(f"✅ Loaded {len(endpoints)} endpoints")
        
        with st.expander("📋 View Loaded Endpoints"):
            for i, endpoint in enumerate(endpoints, 1):
                st.write(f"{i}. `{endpoint}`")
    
    # Manual endpoint input
    st.markdown("### Or Add Endpoints Manually")
    manual_endpoint = st.text_input("Enter endpoint URL:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Endpoint"):
            if manual_endpoint and manual_endpoint not in st.session_state.endpoints:
                st.session_state.endpoints.append(manual_endpoint)
                st.success("✅ Endpoint added!")
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All Endpoints"):
            st.session_state.endpoints = []
            st.success("✅ All endpoints cleared!")
            st.rerun()
    
    if st.session_state.endpoints:
        st.info(f"📊 Total endpoints loaded: {len(st.session_state.endpoints)}")

# --- FETCH DATA PAGE ---
elif menu == "Fetch Data":
    st.subheader("📥 Fetch Data from All Endpoints")
    
    if not st.session_state.auth_token:
        st.error("❌ Please login first!")
        st.stop()
    
    if not st.session_state.endpoints:
        st.error("❌ Please load endpoints first!")
        st.stop()
    
    st.success("✅ Ready to fetch data")
    st.info(f"📊 {len(st.session_state.endpoints)} endpoints loaded")
    
    # Date range configuration
    st.markdown("### 📅 Date Range Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        from_date = st.date_input(
            "From Date",
            value=date.today() - timedelta(days=30),
            max_value=date.today()
        )
    
    with col2:
        to_date = st.date_input(
            "To Date", 
            value=date.today(),
            max_value=date.today()
        )
    
    # Convert dates to strings
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    
    st.info(f"📅 Date range: {from_date_str} to {to_date_str}")
    
    # Form fields configuration
    st.markdown("### 📝 Configure Request Parameters")
    
    # Add default date fields if they don't exist
    date_fields_exist = any(field["key"] in ["from_date", "to_date"] for field in st.session_state.form_fields)
    if not date_fields_exist:
        # Remove empty fields first
        st.session_state.form_fields = [f for f in st.session_state.form_fields if f["key"] or f["value"]]
        # Add date fields
        st.session_state.form_fields.extend([
            {"key": "from_date", "value": from_date_str},
            {"key": "to_date", "value": to_date_str}
        ])
    else:
        # Update existing date fields
        for field in st.session_state.form_fields:
            if field["key"] == "from_date":
                field["value"] = from_date_str
            elif field["key"] == "to_date":
                field["value"] = to_date_str
    
    new_fields = []
    for i, field in enumerate(st.session_state.form_fields):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            key = st.text_input(f"Key {i+1}", value=field["key"], key=f"key_{i}")
        with col2:
            value = st.text_input(f"Value {i+1}", value=field["value"], key=f"value_{i}")
        with col3:
            if st.button("❌", key=f"del_{i}") and len(st.session_state.form_fields) > 1:
                continue
        new_fields.append({"key": key, "value": value})
    
    st.session_state.form_fields = new_fields
    
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("➕ Add Field"):
            st.session_state.form_fields.append({"key": "", "value": ""})
            st.rerun()
    with col_clear:
        if st.button("🗑️ Reset Fields"):
            st.session_state.form_fields = [
                {"key": "from_date", "value": from_date_str},
                {"key": "to_date", "value": to_date_str}
            ]
            st.rerun()
    
    # Fetch settings
    col1, col2 = st.columns(2)
    with col1:
        max_pages = st.number_input("Max pages per endpoint", min_value=1, max_value=1000, value=100)
        delay_seconds = st.number_input("Delay between requests (seconds)", min_value=0.1, max_value=10.0, value=1.0)
    
    with col2:
        save_csv = st.checkbox("💾 Save to CSV files", value=True)
        csv_folder = st.text_input("CSV folder name", value="fetched_data")
    
    # Start fetching
    if st.button("🚀 Start Fetching All Data", type="primary"):
        
        def fetch_all_pages(endpoint_url, form_data, headers, max_pages=100):
            """Fetch all pages from an endpoint"""
            all_data = []
            current_page = 0
            
            while current_page <= max_pages:
                try:
                    # Update page in form data
                    current_form_data = form_data.copy()
                    current_form_data['page'] = str(current_page)
                    
                    response = requests.post(endpoint_url, headers=headers, data=current_form_data)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            if isinstance(data, dict) and "data" in data:
                                if "datas" in data["data"]:
                                    page_data = data["data"]["datas"]
                                    if not page_data:  # No more data
                                        break
                                    
                                    all_data.extend(page_data)
                                    
                                    # Check if we have more pages
                                    total = int(data["data"].get("total", 0))
                                    page_size = int(data["data"].get("size", 20))
                                    total_pages = (total + page_size - 1) // page_size
                                    
                                    if current_page >= total_pages:
                                        break
                                        
                                else:
                                    break
                            else:
                                break
                                
                        except ValueError:
                            break
                    else:
                        break
                    
                    current_page += 1
                    time.sleep(delay_seconds)
                    
                except Exception as e:
                    st.error(f"Error on page {current_page}: {e}")
                    break
            
            return all_data
        
        # Prepare request data
        form_data = {f["key"]: f["value"] for f in st.session_state.form_fields if f["key"]}
        
        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
        
        # Create CSV folder
        if save_csv and not os.path.exists(csv_folder):
            os.makedirs(csv_folder)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_endpoints = len(st.session_state.endpoints)
        
        for idx, endpoint in enumerate(st.session_state.endpoints):
            status_text.text(f"Fetching from endpoint {idx + 1}/{total_endpoints}: {endpoint}")
            
            try:
                # Fetch all pages for this endpoint
                endpoint_data = fetch_all_pages(endpoint, form_data, headers, max_pages)
                
                if endpoint_data:
                    # Create DataFrame
                    df = pd.DataFrame(endpoint_data)
                    
                    # Store in session state
                    endpoint_name = endpoint.split('/')[-1] or f"endpoint_{idx + 1}"
                    st.session_state.fetched_data[endpoint_name] = df
                    
                    # Save to CSV
                    if save_csv:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        csv_filename = f"{csv_folder}/{endpoint_name}_{timestamp}.csv"
                        df.to_csv(csv_filename, index=False)
                    
                    st.success(f"✅ {endpoint_name}: {len(endpoint_data)} records fetched")
                else:
                    st.warning(f"⚠️ No data found for: {endpoint}")
                    
            except Exception as e:
                st.error(f"❌ Error fetching {endpoint}: {e}")
            
            # Update progress
            progress_bar.progress((idx + 1) / total_endpoints)
        
        status_text.text("✅ All endpoints processed!")
        st.balloons()

# --- VISUALIZE DATA PAGE ---
elif menu == "Visualize Data":
    st.subheader("📊 Data Visualization")
    
    if not st.session_state.fetched_data:
        st.error("❌ No data available. Please fetch data first!")
        st.stop()
    
    # Dataset selection
    dataset_names = list(st.session_state.fetched_data.keys())
    selected_dataset = st.selectbox("📋 Select Dataset", dataset_names)
    
    if selected_dataset:
        df = st.session_state.fetched_data[selected_dataset]
        
        # Calculate transaction coverage for this specific endpoint
        transaction_coverage = {}
        date_col = None
        for col in df.columns:
            if 'tgl_transaksi' in col.lower():
                date_col = col
                break
        
        if date_col:
            try:
                # Convert to datetime
                df_temp = df.copy()
                df_temp[f'{date_col}_dt'] = pd.to_datetime(df_temp[date_col], errors='coerce')
                
                # Remove null dates
                valid_dates = df_temp[f'{date_col}_dt'].dropna()
                
                if len(valid_dates) > 0:
                    # Get unique transaction days
                    unique_days = valid_dates.dt.date.nunique()
                    
                    # Calculate coverage percentage (based on 365 days)
                    year_coverage = (unique_days / 365) * 100
                    
                    # Get date range
                    min_date = valid_dates.min().date()
                    max_date = valid_dates.max().date()
                    date_range_days = (max_date - min_date).days + 1
                    
                    # Coverage within actual date range
                    range_coverage = (unique_days / date_range_days) * 100 if date_range_days > 0 else 0
                    
                    transaction_coverage = {
                        'unique_days': unique_days,
                        'year_coverage': year_coverage,
                        'range_coverage': range_coverage,
                        'min_date': min_date,
                        'max_date': max_date,
                        'date_range_days': date_range_days
                    }
                else:
                    transaction_coverage = {
                        'unique_days': 0,
                        'year_coverage': 0,
                        'range_coverage': 0,
                        'min_date': None,
                        'max_date': None,
                        'date_range_days': 0
                    }
            except Exception as e:
                st.warning(f"⚠️ Error calculating coverage: {e}")
                transaction_coverage = {
                    'unique_days': 0,
                    'year_coverage': 0,
                    'range_coverage': 0,
                    'min_date': None,
                    'max_date': None,
                    'date_range_days': 0
                }
        
        # Display basic info with transaction coverage
        if date_col and transaction_coverage:
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("📊 Total Records", len(df))
            with col2:
                st.metric("📋 Total Columns", len(df.columns))
            with col3:
                st.metric("💾 Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            with col4:
                st.metric("📅 Unique Transaction Days", transaction_coverage['unique_days'])
            with col5:
                year_cov = transaction_coverage['year_coverage']
                color = "normal"
                if year_cov >= 80:
                    color = "normal"
                elif year_cov >= 50:
                    color = "normal" 
                else:
                    color = "inverse"
                st.metric("📈 Year Coverage", f"{year_cov:.1f}%", delta_color=color)
            with col6:
                range_cov = transaction_coverage['range_coverage'] 
                st.metric("📊 Range Coverage", f"{range_cov:.1f}%")
            
            # Additional transaction info
            if transaction_coverage['min_date'] and transaction_coverage['max_date']:
                st.info(f"📅 Transaction Period: {transaction_coverage['min_date']} to {transaction_coverage['max_date']} ({transaction_coverage['date_range_days']} days)")
            
            # Coverage status indicator
            year_cov = transaction_coverage['year_coverage']
            if year_cov >= 80:
                st.success(f"🟢 Excellent transaction coverage! This endpoint has transactions on {transaction_coverage['unique_days']} unique days ({year_cov:.1f}% of year)")
            elif year_cov >= 50:
                st.warning(f"🟡 Good transaction coverage. This endpoint has transactions on {transaction_coverage['unique_days']} unique days ({year_cov:.1f}% of year)")
            elif year_cov >= 20:
                st.warning(f"🟠 Moderate transaction coverage. This endpoint has transactions on {transaction_coverage['unique_days']} unique days ({year_cov:.1f}% of year)")
            else:
                st.error(f"🔴 Low transaction coverage. This endpoint has transactions on {transaction_coverage['unique_days']} unique days ({year_cov:.1f}% of year)")
        
        else:
            # Default display when no transaction date column
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Records", len(df))
            with col2:
                st.metric("📋 Total Columns", len(df.columns))
            with col3:
                st.metric("💾 Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            if not date_col:
                st.info("ℹ️ No 'tgl_transaksi' column found. Transaction coverage analysis not available for this endpoint.")
        
        # Data preview
        with st.expander("🔍 Data Preview"):
            st.dataframe(df.head(10))
        
        # Column analysis
        with st.expander("📈 Column Information"):
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.dataframe(col_info)
        
        # Visualizations
        st.markdown("### 📊 Visualizations")
        
        # Numeric columns for analysis
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols:
            # Saldo analysis (if available)
            if 'saldo_akhir' in df.columns:
                st.markdown("#### 💰 Saldo Analysis")
                
                # Convert to numeric
                df['saldo_akhir_numeric'] = pd.to_numeric(df['saldo_akhir'], errors='coerce')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top 10 highest saldo
                    top_saldo = df.nlargest(10, 'saldo_akhir_numeric')
                    if 'nmsatker' in df.columns:
                        fig = px.bar(top_saldo, x='saldo_akhir_numeric', y='nmsatker', 
                                   title='Top 10 Highest Saldo', orientation='h')
                    else:
                        fig = px.bar(top_saldo, x='saldo_akhir_numeric', 
                                   title='Top 10 Highest Saldo')
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Saldo distribution
                    fig = px.histogram(df, x='saldo_akhir_numeric', 
                                     title='Saldo Distribution', nbins=30)
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Bank analysis
                if 'kdbank' in df.columns:
                    st.markdown("#### 🏦 Bank Analysis")
                    
                    bank_summary = df.groupby('kdbank').agg({
                        'saldo_akhir_numeric': ['count', 'sum', 'mean']
                    }).round(2)
                    
                    bank_summary.columns = ['Count', 'Total Saldo', 'Average Saldo']
                    bank_summary = bank_summary.reset_index()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.pie(bank_summary, values='Count', names='kdbank',
                                   title='Distribution by Bank (Count)')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(bank_summary, x='kdbank', y='Total Saldo',
                                   title='Total Saldo by Bank')
                        st.plotly_chart(fig, use_container_width=True)
            
            # General numeric analysis
            if len(numeric_cols) > 0:
                st.markdown("#### 📈 Numeric Data Analysis")
                
                selected_numeric = st.selectbox("Select numeric column", numeric_cols)
                
                if selected_numeric:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.box(df, y=selected_numeric, title=f'{selected_numeric} Box Plot')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.histogram(df, x=selected_numeric, title=f'{selected_numeric} Distribution')
                        st.plotly_chart(fig, use_container_width=True)
        
        # Categorical analysis
        if categorical_cols:
            st.markdown("#### 📊 Categorical Data Analysis")
            
            selected_categorical = st.selectbox("Select categorical column", categorical_cols)
            
            if selected_categorical:
                value_counts = df[selected_categorical].value_counts().head(15)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(x=value_counts.index, y=value_counts.values,
                               title=f'Top 15 {selected_categorical}')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.pie(values=value_counts.values, names=value_counts.index,
                               title=f'{selected_categorical} Distribution')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Time series analysis (if date columns exist)
        date_cols = [col for col in df.columns if 'tgl' in col.lower() or 'date' in col.lower()]
        if date_cols:
            st.markdown("#### 📅 Time Series Analysis")
            
            selected_date_col = st.selectbox("Select date column", date_cols)
            
            if selected_date_col:
                # Convert to datetime
                df[f'{selected_date_col}_dt'] = pd.to_datetime(df[selected_date_col], errors='coerce')
                
                # Group by date
                date_counts = df.groupby(df[f'{selected_date_col}_dt'].dt.date).size().reset_index()
                date_counts.columns = ['date', 'count']
                
                fig = px.line(date_counts, x='date', y='count',
                            title=f'Records by {selected_date_col}')
                st.plotly_chart(fig, use_container_width=True)
        
        # Download processed data
        st.markdown("### 💾 Download Data")
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{selected_dataset}_processed.csv",
            mime="text/csv"
        )

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Status")
    
    if st.session_state.auth_token:
        st.success("✅ Authenticated")
    else:
        st.error("❌ Not authenticated")
    
    st.info(f"📂 Endpoints: {len(st.session_state.endpoints)}")
    st.info(f"📊 Datasets: {len(st.session_state.fetched_data)}")
    
    if st.session_state.fetched_data:
        total_records = sum(len(df) for df in st.session_state.fetched_data.values())
        st.info(f"📈 Total Records: {total_records:,}")
        
        # Quick coverage summary in sidebar
        coverage_summary = []
        for dataset_name, df in st.session_state.fetched_data.items():
            date_col = None
            for col in df.columns:
                if 'tgl_transaksi' in col.lower():
                    date_col = col
                    break
            
            if date_col:
                try:
                    df_temp = df.copy()
                    df_temp[f'{date_col}_dt'] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    valid_dates = df_temp[f'{date_col}_dt'].dropna()
                    
                    if len(valid_dates) > 0:
                        unique_days = valid_dates.dt.date.nunique()
                        coverage_percentage = (unique_days / 365) * 100
                        coverage_summary.append(coverage_percentage)
                except:
                    pass
        
        if coverage_summary:
            avg_coverage = sum(coverage_summary) / len(coverage_summary)
            if avg_coverage >= 80:
                st.success(f"🟢 Avg Coverage: {avg_coverage:.1f}%")
            elif avg_coverage >= 50:
                st.warning(f"🟡 Avg Coverage: {avg_coverage:.1f}%")
            else:
                st.error(f"🔴 Avg Coverage: {avg_coverage:.1f}%")
    
    st.markdown("---")
    if st.button("🔄 Clear All Data"):
        st.session_state.fetched_data = {}
        st.session_state.endpoints = []
        st.success("✅ All data cleared!")
        st.rerun()
