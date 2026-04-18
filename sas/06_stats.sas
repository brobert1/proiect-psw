/*------------------------------------------------------------------
  06_stats.sas
  Obiectiv : folosirea procedurilor statistice
  Proceduri : PROC CORR, PROC REG, PROC LOGISTIC, PROC FASTCLUS
------------------------------------------------------------------*/

/* 1. Corelatii Pearson intre variabilele numerice. */
proc corr data=steel.clean pearson;
    var Usage_kWh Lagging_Current_Reactive_Power_kVarh
        Leading_Current_Reactive_Power_kVarh
        Lagging_Current_Power_Factor Leading_Current_Power_Factor
        CO2_tCO2_ NSM;
    title "Matricea corelatiilor Pearson";
run;

/* 2. Regresie multipla : Usage_kWh ~ driverii tehnici. */
proc reg data=steel.clean;
    model Usage_kWh = Lagging_Current_Reactive_Power_kVarh
                      Leading_Current_Reactive_Power_kVarh
                      Lagging_Current_Power_Factor
                      Leading_Current_Power_Factor
                      NSM
          / vif;
    title "Regresie multipla pentru consumul activ";
run;
quit;

/* 3. Variabila dependenta binara : High_Load = 1 daca Maximum_Load. */
data steel.logit_in;
    set steel.clean;
    high_load = (Load_Type = "Maximum_Load");
run;

/* 4. Regresie logistica. */
proc logistic data=steel.logit_in descending;
    class schimb WeekStatus / param=ref;
    model high_load(event="1") =
        Lagging_Current_Reactive_Power_kVarh
        Leading_Current_Reactive_Power_kVarh
        Lagging_Current_Power_Factor
        Leading_Current_Power_Factor
        NSM schimb WeekStatus
        / lackfit;
    output out=steel.logit_out p=phat;
    title "Regresie logistica : prob. de Maximum_Load";
run;

/* 5. Clusterizare pe profil agregat zi x ora (matrice 24 coloane). */
proc sql;
    create table steel.daily_profile as
    select datepart(stamp) as zi format=date9.,
           hour(timepart(stamp)) as ora,
           mean(Usage_kWh) as kwh
    from steel.clean
    group by calculated zi, calculated ora;
quit;

proc transpose data=steel.daily_profile out=steel.profile_wide(drop=_name_) prefix=h;
    by zi;
    id ora;
    var kwh;
run;

proc fastclus data=steel.profile_wide maxclusters=4 out=steel.clusters;
    var h0--h23;
    title "Clusterizare FASTCLUS pe profile zilnice orare";
run;

proc freq data=steel.clusters;
    tables cluster;
    title "Distributia zilelor in clustere";
run;

title;
