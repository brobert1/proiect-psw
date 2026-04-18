/*------------------------------------------------------------------
  05_report.sas
  Obiectiv : utilizarea procedurilor de raportare
  Facilitate acoperita : "utilizarea de proceduri pentru raportare"
  Proceduri : PROC MEANS, PROC TABULATE, PROC REPORT, PROC FREQ
------------------------------------------------------------------*/

/* 1. PROC MEANS : statistici descriptive pe tipul de sarcina. */
proc means data=steel.clean n mean std min max sum maxdec=2;
    class Load_Type;
    var Usage_kWh cos_phi cost_eur;
    title "Statistici descriptive per tip de sarcina";
run;

/* 2. PROC TABULATE : tabel incrucisat WeekStatus x schimb. */
proc tabulate data=steel.clean;
    class WeekStatus schimb;
    var Usage_kWh cost_eur;
    table WeekStatus * schimb,
          (Usage_kWh cost_eur) * (n mean sum*f=comma10.2);
    title "Consum si cost pe stare saptamana x schimb";
run;

/* 3. PROC REPORT : raport de top zile cu cost maxim. */
proc sort data=steel.daily out=steel.daily_sorted;
    by descending cost_zi;
run;

data steel.top10;
    set steel.daily_sorted(obs=10);
run;

proc report data=steel.top10 nowd headline;
    columns zi kwh_zi co2_zi cost_zi;
    define zi      / display "Ziua" format=date9.;
    define kwh_zi  / analysis sum "Consum (kWh)" format=comma10.0;
    define co2_zi  / analysis sum "CO2 (t)"      format=8.3;
    define cost_zi / analysis sum "Cost (EUR)"   format=comma10.2;
    title "Top 10 zile cu cel mai mare cost";
run;

/* 4. PROC FREQ : distributia incrucisata Load_Type x WeekStatus. */
proc freq data=steel.clean;
    tables Load_Type * WeekStatus / chisq;
    title "Asocierea dintre Load_Type si WeekStatus";
run;

title;
