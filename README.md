<p align="center">
  <img src="assets/FX_logo_top_left.png" alt="Factory-X Logo" width="300">
</p>

# Factory-X Energy Data Visualizer v1.0

*Stand: 18. März 2026*

Der **Factory-X Energy Data Visualizer** ist eine Streamlit-basierte Anwendung zur interaktiven Visualisierung und Analyse von Energiedaten aus Fertigungsprozessen. Sie ermöglicht die schnelle Erstellung publikationsreifer Diagramme aus Maschinen-Messdaten mit umfangreichen Anpassungsmöglichkeiten.

## Kernfunktionen

| Tab | Funktion |
|-----|----------|
| **Data Processing** | Import von Excel- und CSV-Dateien, Datenvorschau, Komponenten-Aliasing und Zeitbereichsfilterung. |
| **Linienplots** | Zeitreihenvisualisierung elektrischer und pneumatischer Leistungsdaten mit optionaler Sekundärachse. |
| **Säulendiagramme** | Gestapelte oder gruppierte Balkendiagramme mit Mittelwert- oder Summenberechnung und Vergleichsfunktion. |
| **Boxplots** | Statistische Verteilungsanalysen zur Identifikation von Ausreißern und Streuungen. |
| **Torten und Donuts** | Anteilsvisualisierung mit konfigurierbarem Sollwert und prozentual oder absoluter Beschriftung. |
| **Scatter / Histogramm** | Korrelationsanalysen und Verteilungsdarstellungen für tiefere Einblicke in die Messdaten. |
| **Sankey** | Energieflussdiagramme zur Darstellung von Verbrauchsverteilungen zwischen Komponenten. |

## Demo

Die App ist live verfügbar auf der **Streamlit Community Cloud**:

👉 [**Factory-X Energy Data Visualizer starten**](https://factory-x-energy-data-visualizer.streamlit.app)

## Installation (Lokale Entwicklung)

1. **Repository klonen**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Factory-X_Energy_Data_Visualizer.git
   cd Factory-X_Energy_Data_Visualizer
   ```

2. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Anwendung starten**:
   ```bash
   streamlit run app.py
   ```

   Die Anwendung öffnet sich automatisch im Browser unter `http://localhost:8501`.

## Projektstruktur

### Architektur im Überblick

Die Anwendung ist in vier klar getrennte Ebenen aufgeteilt:

1. **Start und Branding**
   `app.py` initialisiert Streamlit, setzt das Seitenlayout und injiziert das Factory-X Branding.

2. **Datenfluss**
   `app/data_manager.py` lädt CSV-/Excel-Dateien, erkennt oder erzeugt `elapsedTime` und führt mehrere Dateien zu einem gemeinsamen Datenbestand zusammen.
   `app/preprocessor.py` übernimmt darauf aufbauend Aliasing, Zeitfilter und die Harmonisierung der Daten für alle Visualisierungsmodule.

3. **UI-Orchestrierung**
   `app/main.py` steuert den gesamten Ablauf aus Upload, Sidebar, Preprocessing und Tab-Rendering.
   Unter `app/ui/` liegen Session-State, wiederverwendbare UI-Bausteine und die Sidebar-Logik.

4. **Visualisierung und Export**
   `app/plotting.py` enthält die Matplotlib- und Plotly-Funktionen für die Diagramme.
   `app/export.py` kapselt den Export der erzeugten Plots als PNG, PDF, SVG und EPS.

### Verzeichnisbaum

```text
Factory-X_Energy_Data_Visualizer/
├── app.py                           # Streamlit-Einstiegspunkt, Page Config, Branding/CSS
├── requirements.txt                 # Python-Abhängigkeiten
├── pytest.ini                       # Test-Konfiguration
├── README.md                        # Projektdokumentation
├── README_example.md                # Beispiel-/Alternativfassung der README
├── LICENSE                          # Lizenzdatei
├── .devcontainer/
│   └── devcontainer.json            # Entwicklungsumgebung für Container/VS Code
├── .streamlit/
│   └── config.toml                  # Streamlit-spezifische Konfiguration
├── app/
│   ├── __init__.py                  # Paketmarker
│   ├── config.py                    # Zentrale Defaults für Farben, Tabs und Plot-Optionen
│   ├── data_manager.py              # Dateieinlesung, Zeitnormalisierung und Datenzusammenführung
│   ├── export.py                    # Download- und Exportlogik für Matplotlib/Plotly-Figuren
│   ├── main.py                      # Orchestrierung von Upload, Sidebar, Preprocessing und Tabs
│   ├── plotting.py                  # Plot-Funktionen für Linien-, Balken-, Box-, Histogramm- und Sankey-Diagramme
│   ├── preprocessor.py              # Aliasing, Zeitfilter und Aufbereitung für die UI
│   └── ui/
│       ├── __init__.py              # Paketmarker für die UI-Schicht
│       ├── components.py            # Wiederverwendbare UI-Widgets, z. B. Farbauswahl
│       ├── sidebar.py               # Globale Einstellungen für Daten, Darstellung und Export
│       ├── state.py                 # Verwaltung des Streamlit Session State
│       └── tabs/
│           ├── __init__.py          # Importiert die Tab-Module
│           ├── data_processing.py   # Vorschau, Summary und Quick-Plot der eingelesenen Daten
│           ├── line_plots.py        # Zeitreihenplots mit optionaler Sekundärachse
│           ├── bar_plots.py         # Säulendiagramme und Vergleichsansichten
│           ├── box_plots.py         # Boxplot-Darstellungen für Verteilungsanalysen
│           ├── donut_plots.py       # Torten- und Donut-Diagramme
│           ├── scatter_plots.py     # Scatter-Plots für Korrelationsanalysen
│           ├── histogram_plots.py   # Histogramme zur Verteilungsdarstellung
│           └── sankey_plots.py      # Sankey-Visualisierungen der Energieflüsse
├── assets/
│   ├── FX_logo_top_left.png         # Logo für Sidebar und README
│   └── FX_style_top_right.svg       # Dekoratives Branding-Element im Hintergrund
├── docs/
│   └── matplotlib_defaults.md       # Dokumentation der Plot-Defaults und Exportparameter
├── example_data/
│   └── PROCESSING_Alu_100.csv       # Beispieldatensatz für lokale Tests und Demo-Zwecke
└── tests/
    ├── __init__.py                  # Paketmarker für Tests
    ├── test_data_manager.py         # Tests für Datenimport und Aggregationslogik
    └── test_ui_manager.py           # Basis-Tests für Sidebar und Session-State
```

### Datenfluss in Kurzform

```text
Datei-Upload
    -> DataManager
    -> Preprocessor
    -> Sidebar-Optionen + Session State
    -> Tab-spezifische Renderer
    -> Plotting / Export
```

## Design und Styling

Die Anwendung folgt dem **Factory-X Design-Guide**:
- **Material Design**: Material Symbols Rounded für intuitive Navigation
- **Responsive Layout**: Optimiert für Wide-Mode mit Drei-Spalten-Layout
- **Branding**: Factory-X Logos und Farbschema mit transparentem Hintergrund-Gradienten

## Technologie-Stack

| Kategorie | Technologie |
|-----------|-------------|
| Frontend/Backend | Streamlit |
| Datenanalyse | Pandas, NumPy |
| Visualisierung | Plotly, Matplotlib |
| Export | Matplotlib-Export, Plotly-Export, Kaleido |
| Tabellenverarbeitung | OpenPyXL |

---

<p align="center">
  <i>Entwickelt im Rahmen des Factory-X Projekts zur Steigerung der Energieeffizienz in der Produktion.</i>
</p>
