<p align="center">
  <img src="assets/FX_logo_top_left.png" alt="Factory-X Logo" width="300">
</p>

# Factory-X Energy Data Visualizer v1.0

*Updated: March 18, 2026*

The **Factory-X Energy Data Visualizer** is a Streamlit application for the interactive visualization and analysis of energy data from manufacturing processes. It enables fast creation of publication-ready charts from machine measurement data with extensive customization options.

## Core Features

| Tab | Purpose |
|-----|---------|
| **Data Processing** | Import Excel and CSV files, inspect previews, and create quick summaries of loaded datasets. |
| **Line Plots** | Visualize electric and pneumatic power signals over time with an optional secondary axis. |
| **Bar Charts** | Build stacked or grouped bar charts using average aggregation. |
| **Box Plots** | Explore distributions and outliers across selected components. |
| **Pie and Donut Charts** | Show proportional energy shares with optional target scaling and percentage or kW labels. |
| **Scatter Plot / Histogram** | Explore correlations and distributions in the measurement data. |
| **Sankey** | Display energy flow distributions between selected component groups. |

## Demo

The app is available on **Streamlit Community Cloud**:

[**Launch the Factory-X Energy Data Visualizer**](https://factory-x-energy-data-visualizer.streamlit.app)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Factory-X_Energy_Data_Visualizer.git
   cd Factory-X_Energy_Data_Visualizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   streamlit run app.py
   ```

The application opens in your browser at `http://localhost:8501`.

## Project Structure

The application is organized into four main layers:

1. **Entry Point and Branding**
   `app.py` initializes Streamlit, sets the page layout, and injects the Factory-X branding.

2. **Data Handling**
   `app/data_manager.py` loads CSV and Excel files, derives or normalizes `elapsedTime`, and combines multiple files into one shared dataset.
   `app/x_axis.py` resolves a shared X axis across files while keeping compatibility with existing German-style time columns such as `zeit`.

3. **UI Orchestration**
   `app/main.py` coordinates upload, sidebar state, shared options, and tab rendering.
   `app/ui/` contains session-state helpers, reusable UI components, and all tab modules.

4. **Plotting and Export**
   `app/plotting.py` contains the Matplotlib and Plotly chart functions.
   `app/export.py` provides export helpers for PNG, PDF, SVG, and EPS downloads.

```text
Factory-X_Energy_Data_Visualizer/
|-- app.py
|-- requirements.txt
|-- pytest.ini
|-- README.md
|-- README_example.md
|-- LICENSE
|-- .devcontainer/
|   `-- devcontainer.json
|-- .streamlit/
|   `-- config.toml
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- data_manager.py
|   |-- export.py
|   |-- main.py
|   |-- plotting.py
|   |-- x_axis.py
|   `-- ui/
|       |-- __init__.py
|       |-- components.py
|       |-- sidebar.py
|       |-- state.py
|       `-- tabs/
|           |-- __init__.py
|           |-- data_processing.py
|           |-- line_plots.py
|           |-- bar_plots.py
|           |-- box_plots.py
|           |-- donut_plots.py
|           |-- scatter_plots.py
|           |-- histogram_plots.py
|           `-- sankey_plots.py
|-- assets/
|   |-- FX_logo_top_left.png
|   `-- FX_style_top_right.svg
|-- docs/
|   `-- matplotlib_defaults.md
|-- example_data/
|   `-- PROCESSING_Alu_100.csv
`-- tests/
    |-- __init__.py
    |-- test_data_manager.py
    |-- test_ui_components.py
    |-- test_ui_manager.py
    `-- test_x_axis.py
```

## Data Flow

```text
File Upload
    -> DataManager
    -> Shared X-Axis Resolution
    -> Sidebar Options + Session State
    -> Tab Renderers
    -> Plotting / Export
```

## Design and Styling

The app follows the **Factory-X design guide**:

- **Material Design** with Material Symbols Rounded
- **Responsive layout** optimized for Streamlit wide mode
- **Factory-X branding** with logo assets and a translucent background gradient

## Technology Stack

| Category | Technology |
|----------|------------|
| Frontend / Backend | Streamlit |
| Data Analysis | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Export | Matplotlib export, Plotly export, Kaleido |
| Spreadsheet Processing | OpenPyXL |

---

<p align="center">
  <i>Developed as part of the Factory-X project to improve energy efficiency in production.</i>
</p>
