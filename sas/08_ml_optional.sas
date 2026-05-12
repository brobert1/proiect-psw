/*------------------------------------------------------------------
  08_ml_optional.sas
  Obiectiv : incercare SAS ML (random forest)
  NOTA : PROC HPFOREST NU este disponibila in SAS OnDemand for Academics
         (necesita SAS Enterprise Miner / SAS Viya). In cazul in care
         rularea esueaza, se documenteaza tentativa in PDF si se
         considera acoperita de PROC LOGISTIC + PROC REG din 06_stats.sas.
------------------------------------------------------------------*/

/* Testare disponibilitate. */
%macro try_hpforest;
    %if %sysfunc(exist(steel.logit_in)) %then %do;
        proc hpforest data=steel.logit_in maxtrees=50 seed=42;
            target high_load / level=binary;
            input 'Lagging_Current_Reactive.Power_k'n
                  Leading_Current_Reactive_Power_k
                  Lagging_Current_Power_Factor
                  Leading_Current_Power_Factor
                  NSM / level=interval;
            input schimb WeekStatus / level=nominal;
            ods output VariableImportance=steel.vi;
        run;

        proc print data=steel.vi;
            title "Importanta variabilelor - HPFOREST";
        run;
    %end;
%mend try_hpforest;

%try_hpforest;

/* Alternativa : PROC HPLOGISTIC (parte din SAS/STAT, disponibila pe ODA). */
proc hplogistic data=steel.logit_in;
    class schimb WeekStatus;
    model high_load(event="1") =
        'Lagging_Current_Reactive.Power_k'n
        Leading_Current_Reactive_Power_k
        Lagging_Current_Power_Factor
        Leading_Current_Power_Factor
        NSM schimb WeekStatus;
    title "HPLOGISTIC - versiune high-performance a regresiei logistice";
run;

title;
