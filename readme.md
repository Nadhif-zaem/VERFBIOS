# 🔐 API Data Fetcher & Visualizer

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

**A powerful, enterprise-ready web application for automated API data fetching and intelligent visualization**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [API Documentation](#-api-documentation)

</div>

---

## 🌟 Overview

The **API Data Fetcher & Visualizer** is a comprehensive Streamlit-based application designed for financial data analysts and developers who need to efficiently fetch, process, and visualize large datasets from REST APIs. Built with enterprise-grade features including automatic pagination, intelligent retry mechanisms, and advanced analytics capabilities.

### 🎯 Key Highlights

- **🔒 Secure Authentication**: Token-based authentication with session management
- **📊 Smart Data Processing**: Automatic pagination and batch processing of large datasets
- **📈 Advanced Analytics**: Real-time transaction coverage analysis and financial metrics
- **🎨 Interactive Visualizations**: Dynamic charts and graphs powered by Plotly
- **💾 Data Export**: Multiple export formats with timestamped file management
- **🔄 Batch Processing**: Handle multiple API endpoints simultaneously

---

## ✨ Features

### 🔐 Authentication System
- **Secure Login**: Token-based authentication with session persistence
- **Multi-Environment Support**: Configurable API endpoints for different environments
- **Session Management**: Automatic token handling and renewal

### 📥 Data Fetching Engine
```python
🚀 Automated pagination across multiple endpoints
⚡ Configurable request delays and rate limiting  
📅 Advanced date range filtering
🔄 Intelligent retry mechanisms
📊 Real-time progress tracking
```

### 📊 Analytics Dashboard
- **Transaction Coverage Analysis**: Comprehensive coverage metrics and insights
- **Financial Metrics**: Saldo analysis, bank distribution, and trend analysis  
- **Data Quality Metrics**: Null value analysis, data type validation
- **Time Series Analysis**: Temporal pattern recognition and visualization

### 🎨 Visualization Suite
- **Interactive Charts**: Bar charts, pie charts, line graphs, and histograms
- **Financial Dashboards**: Specialized views for banking and financial data
- **Real-time Updates**: Dynamic chart updates based on data selection
- **Export Ready**: High-quality chart exports for presentations

---

## 🛠 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/api-data-fetcher-visualizer.git
cd api-data-fetcher-visualizer

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Dependencies
```txt
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.3
plotly>=5.15.0
```

---

## 🚀 Usage

### 1. Authentication
Navigate to the **Login** page and enter your credentials:
```python
Username: your_username
Password: your_password  
API URL: https://your-api-endpoint.com/authenticate
```

### 2. Load Endpoints
**Option A: File Upload**
- Upload your `endpoints.txt` file containing API endpoints
- Supports bulk endpoint loading

**Option B: Manual Entry**
- Add endpoints individually through the interface
- Real-time endpoint validation

### 3. Configure Data Fetching
```python
📅 Date Range: Set from_date and to_date
📝 Parameters: Configure custom request parameters
⚙️ Settings: Set max pages, delays, and output options
```

### 4. Fetch Data
- Click **"🚀 Start Fetching All Data"**
- Monitor real-time progress
- Automatic CSV export with timestamps

### 5. Visualize & Analyze
- Select datasets from dropdown
- View comprehensive analytics
- Generate interactive visualizations
- Export processed data

---

## 📸 Screenshots

### 🔐 Authentication Dashboard
<div align="center">
<img src="https://via.placeholder.com/800x400/FF4B4B/FFFFFF?text=Secure+Login+Interface" alt="Login Interface" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</div>

### 📊 Data Fetching Engine
<div align="center">
<img src="https://via.placeholder.com/800x400/3776AB/FFFFFF?text=Automated+Data+Fetching" alt="Data Fetching" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</div>

### 📈 Analytics Dashboard  
<div align="center">
<img src="https://via.placeholder.com/800x400/150458/FFFFFF?text=Advanced+Analytics+%26+Visualization" alt="Analytics Dashboard" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</div>

---

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set default configurations
export DEFAULT_API_URL="https://your-api.com/api"
export MAX_CONCURRENT_REQUESTS="10"
export DEFAULT_PAGE_SIZE="100"
```

### Custom Parameters
The application supports dynamic parameter configuration:
```python
{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31", 
    "page_size": "100",
    "custom_param": "value"
}
```

---

## 📋 API Documentation

### Expected API Response Format
```json
{
    "status": "MSG20004",
    "message": "Success",
    "data": {
        "datas": [...],
        "total": 1000,
        "size": 100,
        "page": 1
    }
}
```

### Authentication Response
```json
{
    "status": "MSG20004", 
    "message": "Login success",
    "token": "your-jwt-token"
}
```

---

## 🎯 Use Cases

### 💰 Financial Data Analysis
- Bank transaction monitoring
- Saldo tracking and analysis
- Financial reporting automation
- Compliance data collection

### 📊 Business Intelligence
- Multi-source data aggregation
- Automated report generation
- Trend analysis and forecasting  
- Data quality assessment

### 🔍 Data Engineering
- ETL pipeline automation
- API data validation
- Batch processing workflows
- Data warehouse integration

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit Community** for the amazing framework
- **Plotly Team** for powerful visualization tools  
- **Pandas Contributors** for robust data processing capabilities

---

## 📞 Support & Contact

<div align="center">

[![GitHub Issues](https://img.shields.io/github/issues/yourusername/api-data-fetcher-visualizer?style=flat-square)](https://github.com/yourusername/api-data-fetcher-visualizer/issues)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/api-data-fetcher-visualizer?style=flat-square)](https://github.com/yourusername/api-data-fetcher-visualizer/stargazers)

**Found this project helpful? Give it a ⭐ to show your support!**

</div>

---

<div align="center">
<sub>Built with ❤️ by <a href="https://github.com/yourusername">Your Name</a></sub>
</div>