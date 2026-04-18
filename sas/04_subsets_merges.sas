/*------------------------------------------------------------------
  04_subsets_merges.sas
  Obiective :
    - crearea de subseturi de date (WHERE)
    - combinarea seturilor prin DATA step (MERGE) si SQL (JOIN)
------------------------------------------------------------------*/

/* 1. Subset : doar zilele lucratoare cu sarcina maxima. */
data steel.sub_max;
    set steel.clean;
    where WeekStatus = "Weekday" and Load_Type = "Maximum_Load";
run;

proc print data=steel.sub_max(obs=5);
    title "Subset: zile lucratoare cu sarcina maxima";
run;

/* 2. Subset prin PROC SQL. */
proc sql;
    create table steel.sub_weekend as
    select *
    from steel.clean
    where WeekStatus = "Weekend";
quit;

/* 3. Tabel auxiliar cu tarife per schimb (pentru MERGE / JOIN). */
data steel.tariff;
    length schimb $12;
    input schimb $ tarif_eur_kwh;
    datalines;
Noapte       0.10
Dimineata    0.13
Dupa-amiaza  0.18
;
run;

/* 4. Combinare prin DATA step MERGE dupa schimb. */
proc sort data=steel.clean out=steel.clean_sort;
    by schimb;
run;
proc sort data=steel.tariff;
    by schimb;
run;

data steel.clean_with_tariff;
    merge steel.clean_sort(in=a) steel.tariff(in=b);
    by schimb;
    if a;
    cost_real = Usage_kWh * tarif_eur_kwh;
run;

/* 5. Combinare prin PROC SQL (inner join). */
proc sql;
    create table steel.cost_by_day as
    select datepart(c.stamp) as zi format=date9.,
           sum(c.Usage_kWh * t.tarif_eur_kwh) as cost_dif_tarifar,
           sum(c.Usage_kWh)                    as kwh_zi,
           count(*)                            as n_obs
    from steel.clean as c
    inner join steel.tariff as t
        on c.schimb = t.schimb
    group by calculated zi;
quit;

proc print data=steel.cost_by_day(obs=10);
    title "Cost zilnic calculat prin SQL cu tarife diferentiate";
run;

title;
