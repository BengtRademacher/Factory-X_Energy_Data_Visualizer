<p align="center">
  <img src="assets/FX_logo_top_left.png" alt="Factory-X Logo" width="300">
</p>

# Factory-X Audit App v1.5

*Updated: January 22, 2026*

The **Factory-X Audit App** is a Streamlit-based application for automated extraction, processing, and evaluation of energy data from manufacturing processes. It combines modern LLM capabilities with classical data analysis to make scientific publications and real machine datasets comparable.

## Core Features

| Tab | Purpose |
|-----|---------|
| **Document -> JSON** | Extract structured data from PDFs, CSV, Excel, or JSON files via LLMs and store the results in a local literature database. |
| **Data -> JSON** | Process machine measurement data from Excel or CSV files and compute energy KPIs, duty cycles, and performance values for electric and pneumatic components. |
| **JSON Comparison** | Compare audit results with literature benchmarks and export analysis results as PDF. |
| **Ask about data** | Use a context-aware chat assistant for deeper audit-data analysis with configurable system prompts. |

## Demo

The app is available on **Streamlit Community Cloud**:

[**Launch the Factory-X Audit App**](https://factory-x-audit-app.streamlit.app)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Factory-X_Audit-App.git
   cd Factory-X_Audit-App
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the API key** by creating `.streamlit/secrets.toml`
   ```toml
   [openrouter]
   api_key = "sk-or-v1-YOUR_OPENROUTER_API_KEY"
   ```
   This file is ignored by `.gitignore` and should not be committed.

4. **Start the application**
   ```bash
   streamlit run app.py
   ```

## Project Structure

```text
Factory-X_Audit-App/
|-- app.py
|-- config/
|-- core/
|-- database/
|-- services/
|-- assets/
`-- data/
```

## Design and Styling

The application follows the **Factory-X design guide**:

- **Material Design** with Material Symbols Rounded
- **Responsive layout** optimized for wide mode
- **Factory-X branding** with a consistent logo and color system

## Technology Stack

| Category | Technology |
|----------|------------|
| Frontend / Backend | Streamlit |
| AI / LLM Integration | OpenRouter |
| Data Analysis | Pandas, NumPy |
| Visualization | Plotly |
| PDF Export | ReportLab |

---

<p align="center">
  <i>Developed as part of the Factory-X project to improve energy efficiency in production.</i>
</p>
