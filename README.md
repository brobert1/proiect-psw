# Proiect Pachete Software — Daewoo Steel Energy Consumption

Facultatea CSIE, anul III. Echipă: `<NUME_1>`, `<NUME_2>` — grupa `<GRUPA>`.

## Narativă

Analiza consumului energetic al fabricii Daewoo Steel Co. (set date Kaggle,
~35k observații la interval de 15 minute, anul 2018) din perspectiva
**eficienței energetice și optimizării de cost**. Se estimează costul în EUR
(tarif industrial 0.15 EUR/kWh) și impactul CO2 (taxă carbon 80 RON/tCO2).

## Structură

```
python/    aplicație Streamlit multipage (app.py + pages/)
sas/       8 scripturi .sas rulabile în SAS OnDemand for Academics
documentatie/  documentul PDF final
```

## Rulare Python

```bash
cd python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Setul de date trebuie plasat la `python/data/Steel_industry_data.csv`
(descărcat manual din Kaggle: steel-industry-energy-consumption-daewoo-steel-co).

## Rulare SAS

1. Se încarcă fișierul CSV în folderul SAS OnDemand (ex. `/home/u<user>/data/`).
2. Se ajustează `%let path = ...;` din `sas/01_import.sas`.
3. Se rulează scripturile în ordinea numerotării (01 → 08).

## Acoperire cerințe

- **Python (9/9 facilități listate)**: Streamlit display/charts, valori lipsă,
  outlieri, codificare, scalare, agregări pandas, funcții de grup, KMeans
  (sklearn), regresie logistică (sklearn), regresie multiplă (statsmodels).
- **SAS (11/11 facilități listate)**: import extern, formate user-defined,
  procesare iterativă/condițională, subseturi, funcții SAS, combinare
  seturi (DATA + SQL), masive, proceduri raportare, proceduri statistice,
  grafice, încercare SAS ML (HPFOREST) cu fallback.
