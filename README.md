<p align="center">
  <img src="assets/FX_logo_top_left.png" alt="Factory-X Logo" width="300">
</p>

# Factory-X Energy Data Visualizer v1.0

*Stand: 22. Januar 2026*

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

```
Factory-X_Energy_Data_Visualizer/
├── app.py                 # Einstiegspunkt und Branding
├── app/
│   ├── config.py          # Zentrale Konfiguration und Defaults
│   ├── data_manager.py    # Datenimport und -verwaltung
│   ├── export.py          # Export-Funktionalität (PDF, PNG)
│   ├── main.py            # Hauptanwendungslogik
│   ├── plotting.py        # Plot-Erstellungsfunktionen
│   ├── preprocessor.py    # Datenvorverarbeitung
│   └── ui/                # UI-Komponenten und Tab-Module
├── assets/                # Logos und Styling-Assets
├── example_data/          # Beispieldatensätze
└── tests/                 # Unit-Tests
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
| Export | Kaleido (PDF/PNG) |
| Tabellenverarbeitung | OpenPyXL |

---

<p align="center">
  <i>Entwickelt im Rahmen des Factory-X Projekts zur Steigerung der Energieeffizienz in der Produktion.</i>
</p>
