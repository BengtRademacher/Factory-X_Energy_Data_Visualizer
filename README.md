# Factory-X_Energy_Data_Visualizer

Eine Streamlit-Anwendung zur Visualisierung und Analyse von Energiedaten.

## Voraussetzungen

- Python 3.11+
- Abhängigkeiten aus `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```

## Starten

```bash
streamlit run app.py
```

Die Anwendung öffnet sich automatisch im Browser unter `http://localhost:8501`.

## Projektstruktur

```
Factory-X_Energy_Data_Visualizer/
├── app.py                 # Einstiegspunkt
├── app/
│   ├── config.py          # Zentrale Konfiguration
│   ├── data_manager.py    # Datenimport und -verwaltung
│   ├── export.py          # Export-Funktionalität
│   ├── main.py            # Hauptanwendungslogik
│   ├── plotting.py        # Plot-Funktionen
│   ├── preprocessor.py    # Datenvorverarbeitung
│   └── ui/
│       ├── sidebar.py     # Globale Sidebar
│       ├── state.py       # Session-State-Management
│       └── tabs/          # Tab-Module
│           ├── data_processing.py
│           ├── line_plots.py
│           ├── bar_plots.py
│           ├── box_plots.py
│           ├── donut_plots.py
│           ├── scatter_plots.py
│           ├── histogram_plots.py
│           └── sankey_plots.py
├── assets/
│   ├── FX_logo_top_left.png
│   └── FX_style_top_right.svg
├── example_data/          # Beispieldateien
├── requirements.txt
└── .gitignore
```

## Features

- **Data Processing**: Datenvorschau, Aliasing, Zeitfilter
- **Linienplots**: Zeitreihen mit optionaler Sekundärachse
- **Säulendiagramme**: Gestapelt, mit Vergleichsfunktion
- **Boxplots**: Statistische Verteilungen
- **Donut-Diagramme**: Anteile visualisieren
- **Scatter Plots**: Korrelationen darstellen
- **Histogramme**: Verteilungsanalysen
- **Sankey-Diagramme**: Energieflüsse

## Layout

- **Linke Sidebar**: Globale Einstellungen (Datenverarbeitung, Darstellung, Export)
- **Hauptbereich**: Diagramme
- **Rechte Spalte**: Tab-spezifische Anpassungen (Komponentenauswahl, Farben)

## Hinweise

- Export von Plotly-Diagrammen als PDF benötigt `kaleido`
- Theme kann in `.streamlit/config.toml` angepasst werden
