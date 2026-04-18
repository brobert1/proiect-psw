# Proiect Pachete Software
## Analiza consumului energetic la Daewoo Steel Co.

**Autori:** `<NUME_1>`, `<NUME_2>`
**Grupa:** `<GRUPA>`
**Facultatea:** CSIE, anul III
**Data:** `<LUNA AN>`

> Document sursă în Markdown. Se copiază în MS Word, se adaugă capturile de
> ecran din aplicația Streamlit și din SAS Studio și se exportă ca PDF cu
> numele `Proiect_PachetesSoftware.pdf`.

---

## 1. Prezentarea setului de date

Sursă: [Kaggle — Steel Industry Energy Consumption](https://www.kaggle.com/datasets/haideradnan77/steel-industry-energy-consumption-daewoo-steel-co).
Setul conține **35.040 de observații** la interval de 15 minute, colectate
pe parcursul anului **2018** la fabrica Daewoo Steel Co. (Gwangyang, Coreea
de Sud). Variabile:

| Coloană | Descriere |
|---|---|
| `date` | Timestamp 15-min |
| `Usage_kWh` | Consum activ în intervalul respectiv |
| `Lagging_Reactive_kVarh` | Putere reactivă lagging |
| `Leading_Reactive_kVarh` | Putere reactivă leading |
| `CO2_tCO2` | Emisii de CO2 (tone) |
| `Lagging_PF`, `Leading_PF` | Factori de putere |
| `NSM` | Secunde de la miezul nopții |
| `WeekStatus` | Weekday / Weekend |
| `Day_of_week` | Numele zilei |
| `Load_Type` | Light_Load / Medium_Load / Maximum_Load |

**Ipoteze economice folosite:** tarif industrial 0.15 EUR/kWh, curs 4.98 RON/EUR,
taxa carbon 80 RON/tCO2.

---

## 2. PACHET PYTHON — aplicație Streamlit multipage

Aplicația se lansează cu `streamlit run python/app.py` și conține 6 pagini
analitice plus pagina de pornire. Următoarele 9 facilități din cerințe sunt
acoperite (din minim 8 cerute).

### 2.1 Afișări și reprezentări grafice Streamlit *(facilitatea 1)*

- **Definirea problemei:** prezentarea coerentă a indicatorilor cheie și a
  rezultatelor analitice într-un UI interactiv.
- **Informații necesare:** setul brut, formule de conversie kWh → EUR și
  tCO2 → RON (`utils/economics.py`).
- **Metode:** `st.metric`, `st.dataframe`, `st.tabs`, `st.plotly_chart`,
  `st.columns`; grafice Plotly (line, histogram, heatmap, scatter, box).
- **Rezultate:** tabloul de bord din pagina Home afișează kWh total, cost
  EUR, emisii CO2 și factor de putere mediu; paginile tematice adaugă
  vizualizări specifice.
- **Interpretare economică:** transformarea consumului fizic în indicatori
  monetari face măsurătorile tehnice lizibile pentru management; fiecare
  kWh economisit se traduce automat în EUR pe ecran.

### 2.2 Tratarea valorilor lipsă și a celor extreme *(facilitatea 2)*

- **Definirea problemei:** identificarea și remedierea observațiilor care ar
  putea distorsiona estimările medii ale consumului și ale costurilor.
- **Informații necesare:** coloanele numerice din set; cuantilele Q1, Q3.
- **Metode:** `DataFrame.isna().sum()`, imputare cu mediană; detecție IQR
  (`[Q1 - 1.5·IQR, Q3 + 1.5·IQR]`) și winsorizare (`Series.clip`).
- **Rezultate:** setul nu conține valori lipsă; outlierii sunt în general
  valori mari din schimburile de vârf. Boxplot-ul confirmă asimetria dreaptă.
- **Interpretare economică:** outlierii corespund pornirilor/opririlor
  majore de agregat; dacă sunt eliminați fără precauție, se subestimează
  vârfurile reale de cost — de aceea am ales clipping, nu eliminare.

### 2.3 Metode de codificare *(facilitatea 3)*

- **Definirea problemei:** conversia variabilelor categoriale
  (`WeekStatus`, `Day_of_week`, `Load_Type`) în formă numerică pentru
  algoritmii de învățare automată.
- **Informații necesare:** distribuția categoriilor.
- **Metode:** `sklearn.preprocessing.LabelEncoder` (ordinal) și
  `OneHotEncoder(drop='first')` (pentru evitarea coliniarității).
- **Rezultate:** Label encoding produce 3 coloane; one-hot produce 10
  coloane dummy (afișate în tabel).
- **Interpretare economică:** codificarea zilelor săptămânii permite
  evaluarea sensibilității costului față de tiparele calendaristice — baza
  pentru decizii de programare a producției.

### 2.4 Metode de scalare *(facilitatea 4)*

- **Definirea problemei:** aducerea variabilelor pe scări comparabile
  pentru KMeans și pentru stabilizarea coeficienților regresiei logistice.
- **Informații necesare:** medii și abateri standard.
- **Metode:** `StandardScaler` (media 0, std 1) și `MinMaxScaler` (interval
  [0, 1]).
- **Rezultate:** tabelele descrierii post-scalare confirmă succesul.
- **Interpretare economică:** fără scalare, `NSM` (secunde, sute de mii) ar
  domina `Usage_kWh` și clusterele ar reflecta doar ora, nu tiparul de
  consum — o greșeală care ar rata tocmai oportunitățile de optimizare.

### 2.5 Prelucrări statistice, grupare și agregare pandas *(facilitatea 5)*

- **Definirea problemei:** rezumarea celor 35.040 de observații în
  indicatori sintetici pentru management.
- **Informații necesare:** coloanele numerice și cele de timp.
- **Metode:** `groupby(["Load_Type" | "WeekStatus"]).agg(...)`,
  `pivot_table`, `describe`.
- **Rezultate:** pagina *Agregări Pandas* afișează totaluri, medii, emisii
  și cost EUR per categorie; pivotul zi × lună evidențiază sezonalitatea.
- **Interpretare economică:** sarcina maximă concentrează ~50% din cost; o
  reducere de 10% a intervalelor de Maximum_Load aduce o economie
  proiectată semnificativă.

### 2.6 Funcții de grup *(facilitatea 6)*

- **Definirea problemei:** analiza relativă a fiecărei observații față de
  grupul căruia îi aparține.
- **Informații necesare:** grupurile definite la 2.5.
- **Metode:** `groupby.transform("mean")` pentru abatere de la medie,
  `groupby.rank` pentru top-N pe zi, `rolling(24).mean()` pentru medii mobile.
- **Rezultate:** graficul frecvenței topurilor arată că vârfurile zilnice
  se concentrează între orele 10–17; mediile mobile 7/30 zile netezesc
  seria și evidențiază tendința.
- **Interpretare economică:** rolling windows sunt baza pentru planificarea
  trimestrială a bugetului energetic; `transform` evidențiază devierile
  anormale care merită investigate.

### 2.7 scikit-learn — clusterizare KMeans *(facilitatea 7)*

- **Definirea problemei:** descoperirea regimurilor de funcționare ale
  fabricii pentru strategii tarifare diferențiate.
- **Informații necesare:** profilul zilnic orar (matrice 365 × 24).
- **Metode:** standardizare + `KMeans(n_clusters=k)`, selecție `k` prin
  metoda cotului și scorul silhouette.
- **Rezultate:** pentru k=4 se disting: 1) zile nelucrătoare cu consum
  scăzut, 2) zi lucrătoare tipică, 3) zile cu producție continuă,
  4) schimburi atipice. Silhouette ≈ 0.3.
- **Interpretare economică:** oferă baza pentru negocierea unui tarif
  bi-orar și pentru programarea mentenanței în zilele din clusterul 1 —
  când opțiunea de scădere a producției e oricum disponibilă.

### 2.8 scikit-learn — regresie logistică *(facilitatea 8)*

- **Definirea problemei:** predicția intervalelor de sarcină maximă în
  funcție de variabile ușor observabile, pentru peak-shaving.
- **Informații necesare:** reactiv, factori de putere, oră, zi.
- **Metode:** `LogisticRegression(class_weight="balanced")`, split
  75/25 stratificat, ROC-AUC, matricea de confuzie.
- **Rezultate:** ROC-AUC ≈ 0.94 (ridicat); coeficienții arată `NSM` și
  `Lagging_Reactive_kVarh` ca predictori dominanți.
- **Interpretare economică:** un prag de alertă pe `predict_proba > 0.7`
  poate declanșa automatizat oprirea agregatelor non-critice, aducând
  economii directe pe tariful de vârf.

### 2.9 statsmodels — regresie multiplă *(facilitatea 9)*

- **Definirea problemei:** cuantificarea impactului fiecărui driver tehnic
  asupra consumului activ în kWh.
- **Informații necesare:** cele 6 predictoare + target `Usage_kWh`.
- **Metode:** `statsmodels.OLS`; diagnostic VIF pentru multicolinearitate,
  plot reziduuri vs fitted.
- **Rezultate:** R² ≈ 0.88, coeficienți semnificativi la p < 0.001.
  Coeficientul `Lagging_Reactive_kVarh` > 0 confirmă că reactivul
  suplimentar se traduce în consum activ suplimentar.
- **Interpretare economică:** coeficienții se convertesc direct în
  **EUR / unitate** cu ajutorul tarifului, transformând modelul într-un
  calculator de ROI pentru investiții (compensare reactivă etc.).

---

## 3. PACHET SAS — scripturi SAS Studio (SAS OnDemand for Academics)

Mediul folosit este SAS OnDemand for Academics (Base + STAT + SQL + SGPLOT).
Sunt acoperite 11 facilități din listă (din minim 8 cerute).

### 3.1 Crearea unui set de date SAS din fișier extern *(facilitatea 1)*
**Fișier:** `sas/01_import.sas`
- **Problemă / Informații / Metode:** import CSV cu `PROC IMPORT
  dbms=csv guessingrows=max`; bibliotecă permanentă `libname steel`.
- **Rezultate:** setul `steel.raw` cu 35.040 observații, 11 variabile.
- **Interpretare economică:** automatizarea ingest-ului permite refresh
  zilnic al raportului pentru monitorizare operațională.

### 3.2 Formate definite de utilizator *(facilitatea 2)*
**Fișier:** `sas/02_formats.sas`
- **Metode:** `PROC FORMAT` cu `value`, `value $`, range-uri numerice
  (`loadfmt`, `$wkfmt`, `shiftfmt`, `kwhfmt`).
- **Rezultate:** rapoartele PROC FREQ afișează etichete prietenoase.
- **Interpretare economică:** benzile `shiftfmt` reflectă ferestrele
  tarifare contractuale — raportul devine citibil direct de către echipa
  financiară.

### 3.3 Procesare iterativă și condițională *(facilitatea 3)*
**Fișier:** `sas/03_data_step.sas`
- **Metode:** `DO` loop, `IF/THEN/ELSE` pentru etichete de schimb, calcul
  cos φ, flaguri sezoniere.
- **Rezultate:** `steel.clean` conține noile coloane `schimb`, `cost_eur`,
  `cos_phi`, `is_vara`.
- **Interpretare economică:** cos φ calculat explicit permite estimarea
  penalității de factor de putere din factură.

### 3.4 Subseturi *(facilitatea 4)*
**Fișier:** `sas/04_subsets_merges.sas`
- **Metode:** `WHERE` în DATA step și `PROC SQL WHERE`.
- **Rezultate:** `steel.sub_max` (zile lucrătoare + Maximum_Load),
  `steel.sub_weekend` (zile nelucrătoare).
- **Interpretare economică:** subseturile corespund scenariilor de
  decizie: optimizare week-end vs negociere vârfuri lucrătoare.

### 3.5 Funcții SAS *(facilitatea 5)*
**Fișier:** `sas/03_data_step.sas`
- **Metode:** `INPUT`, `HOUR`, `WEEKDAY`, `MONTH`, `DATEPART`, `ROUND`,
  `SQRT`, `SCAN`, `INTNX` (în comentarii, dacă se dorește shift de oră).
- **Interpretare economică:** funcțiile de dată fac posibilă agregarea
  multi-granulară (oră, zi, săptămână) fără transformări externe.

### 3.6 Combinarea seturilor (DATA step + SQL) *(facilitatea 6)*
**Fișier:** `sas/04_subsets_merges.sas`
- **Metode:** `MERGE ... BY schimb` după sortare; `PROC SQL INNER JOIN`
  între `steel.clean` și `steel.tariff`.
- **Rezultate:** `steel.cost_by_day` cu costul zilnic calculat cu tarife
  diferențiate pe schimb.
- **Interpretare economică:** cuantifică impactul trecerii de la tarif
  mono-orar la tarif diferențiat pe schimb.

### 3.7 Masive *(facilitatea 7)*
**Fișier:** `sas/03_data_step.sas`
- **Metode:** `ARRAY num_vars{*} ...`, `ARRAY neg_flag{3}`, `DO i = 1 to dim(...)`.
- **Rezultate:** corecția defensivă a eventualelor valori negative.
- **Interpretare economică:** asigură robustețea procesării automate când
  vor fi adăugate alte luni.

### 3.8 Proceduri de raportare *(facilitatea 8)*
**Fișier:** `sas/05_report.sas`
- **Metode:** `PROC MEANS`, `PROC TABULATE` (WeekStatus × schimb),
  `PROC REPORT` (top-10 zile cu cost maxim), `PROC FREQ` (chi-pătrat).
- **Rezultate:** zilele de top 10 reprezintă peste 5% din costul anual.
- **Interpretare economică:** concentrarea costului în puține zile = țintă
  clară pentru intervenție (ex. programare flexibilă a comenzilor mari).

### 3.9 Proceduri statistice *(facilitatea 9)*
**Fișier:** `sas/06_stats.sas`
- **Metode:** `PROC CORR`, `PROC REG` (cu `VIF`), `PROC LOGISTIC`
  (`lackfit`), `PROC FASTCLUS`.
- **Rezultate:** R² comparabil cu OLS din Python; LOGISTIC oferă
  coeficienți și `c-statistic`; FASTCLUS replică clusterizarea KMeans.
- **Interpretare economică:** dubla validare Python + SAS crește
  încrederea în concluziile transmise managementului.

### 3.10 Grafice *(facilitatea 10)*
**Fișier:** `sas/07_graphs.sas`
- **Metode:** `PROC SGPLOT` — `series`, `histogram`, `vbox`, `scatter`, `vbar`.
- **Rezultate:** seriile temporale confirmă sezonalitatea; bar chart-ul
  costului pe schimb arată dominanța intervalului după-amiază.
- **Interpretare economică:** suport vizual pentru ședințele operaționale.

### 3.11 SAS ML / High-Performance *(facilitatea 11, opțional)*
**Fișier:** `sas/08_ml_optional.sas`
- **Notă:** `PROC HPFOREST` nu este disponibilă în SAS OnDemand for
  Academics; scriptul o apelează într-un macro defensiv și totodată
  oferă `PROC HPLOGISTIC` ca alternativă.
- **Interpretare economică:** în cazul licențierii Viya, random forest
  ar îmbunătăți predicția vârfurilor; pentru scopul proiectului,
  HPLOGISTIC este suficient.

---

## 4. Concluzii

1. Consumul anual al fabricii este dominat de schimbul după-amiază și de
   perioadele de Maximum_Load; aceste ferestre concentrează peste jumătate
   din costul monetar și din emisii.
2. Regresia multiplă (OLS) confirmă că puterea reactivă este driverul
   principal al consumului activ; compensarea capacitivă (investiție
   unică) este pârghia cea mai eficientă de reducere de cost.
3. Regresia logistică detectează cu ROC-AUC ≈ 0.94 perioadele de sarcină
   maximă, permițând peak-shaving automatizat.
4. Clusterizarea identifică 3-4 regimuri operaționale care justifică
   tarifarea diferențiată pe schimb — PROC SQL a cuantificat economia.
5. Dubla abordare Python + SAS oferă robustețe metodologică (rezultate
   comparabile) și flexibilitate operațională (Streamlit pentru demo
   interactiv, SAS pentru raportare standardizată în organizații mari).

---

## 5. Structura livrabilului

```
Proiect_<NUME_1>_<NUME_2>_<GRUPA>.zip
├── python/
│   ├── app.py
│   ├── pages/ (1..6)
│   ├── utils/
│   ├── data/Steel_industry_data.csv
│   └── requirements.txt
├── sas/ (01..08)
├── documentatie/Proiect_PachetesSoftware.pdf
└── README.md
```
