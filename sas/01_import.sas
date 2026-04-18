/*------------------------------------------------------------------
  01_import.sas
  Obiectiv : crearea unui set de date SAS din fisier extern (CSV)
  Facilitate acoperita : "crearea unui set de date SAS din fisiere externe"
  Mediu    : SAS OnDemand for Academics (SAS Studio)
------------------------------------------------------------------*/

/* 1. Macro variabila cu calea catre CSV (se ajusteaza cu user-ul propriu). */
%let path = /home/u<USER>/pachete_software/data;

/* 2. Biblioteca permanenta pentru proiect. */
libname steel "&path";

/* 3. Import CSV cu PROC IMPORT. */
proc import datafile="&path/Steel_industry_data.csv"
    out=steel.raw
    dbms=csv
    replace;
    getnames=yes;
    guessingrows=max;
run;

/* 4. Inspectie structura + primele randuri. */
proc contents data=steel.raw;
    title "Structura setului Daewoo Steel";
run;

proc print data=steel.raw(obs=10);
    title "Primele 10 observatii";
run;

title;
