<p align="center">
  <img src="assets/FX_logo_top_left.png" alt="Factory-X Logo" width="300">
</p>

# Factory-X Audit-App v1.5

*Stand: 22. Januar 2026*

Die **Factory-X Audit-App** ist eine Streamlit-basierte Anwendung zur automatisierten Extraktion, Verarbeitung und Bewertung von Energiedaten aus Fertigungsprozessen. Sie kombiniert moderne LLM-Technologie mit klassischer Datenanalyse, um wissenschaftliche Publikationen und reale Maschinendaten vergleichbar zu machen.

## Kernfunktionen

| Tab | Funktion |
|-----|----------|
| **Document → JSON** | Extraktion strukturierter Daten aus PDFs, CSV, Excel oder JSON mittels LLMs. Die Ergebnisse werden in einer lokalen Literaturdatenbank gespeichert. |
| **Data → JSON** | Verarbeitung von Maschinen-Messdaten (Excel/CSV). Automatische Berechnung von Energie-KPIs, Duty Cycles und Leistungswerten für elektrische und pneumatische Komponenten. |
| **JSON Comparison** | KI-gestützter Vergleich zwischen Audit-Ergebnissen und Literatur-Benchmarks inklusive PDF-Export der Analyseergebnisse. |
| **Ask about data** | Kontextbezogener Chat-Assistent für tiefgehende Analysen der Audit-Daten mit konfigurierbaren System-Prompts. |

## Demo

Die App ist live verfügbar auf der **Streamlit Community Cloud**:

👉 [**Factory-X Audit-App starten**](https://factory-x-audit-app.streamlit.app)

## Installation (Lokale Entwicklung)

1. **Repository klonen**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Factory-X_Audit-App.git
   cd Factory-X_Audit-App
   ```

2. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

3. **API-Key konfigurieren** – Erstellen Sie `.streamlit/secrets.toml`:
   ```toml
   [openrouter]
   api_key = "sk-or-v1-DEIN_OPENROUTER_API_KEY"
   ```
   > ⚠️ Diese Datei ist in `.gitignore` enthalten und wird nicht committed.

4. **Anwendung starten**:
   ```bash
   streamlit run app.py
   ```

## Projektstruktur

```
Factory-X_Audit-App/
├── app.py                 # Hauptanwendung und UI-Logik
├── config/                # Zentrale Einstellungen und LLM-Prompts
├── core/                  # LLM-Provider, Datenverarbeitung, Parsing
├── database/              # Literaturdatenbank und Audit-Store
├── services/              # Visualisierung (Plotly) und PDF-Export
├── assets/                # Logos und Styling-Assets
└── data/                  # Lokale Ablage für Audits (gitignored)
```

## Design und Styling

Die Anwendung folgt dem **Factory-X Design-Guide**:
- **Material Design**: Material Symbols Rounded für intuitive Navigation
- **Responsive Layout**: Optimiert für Wide-Mode
- **Branding**: Factory-X Logos und Farbschema

## Technologie-Stack

| Kategorie | Technologie |
|-----------|-------------|
| Frontend/Backend | Streamlit |
| KI/LLM Integration | OpenRouter (Zugang zu 100+ Modellen) |
| Datenanalyse | Pandas, NumPy |
| Visualisierung | Plotly |
| PDF-Export | ReportLab |

---

<p align="center">
  <i>Entwickelt im Rahmen des Factory-X Projekts zur Steigerung der Energieeffizienz in der Produktion.</i>
</p>
