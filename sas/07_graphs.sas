/*------------------------------------------------------------------
  07_graphs.sas
  Obiectiv : generarea de grafice cu PROC SGPLOT
------------------------------------------------------------------*/

/* 1. Serie temporala a consumului zilnic. */
proc sgplot data=steel.daily;
    series x=zi y=kwh_zi / lineattrs=(thickness=2);
    xaxis label="Ziua";
    yaxis label="Consum (kWh)";
    title "Consum zilnic de energie activa - 2018";
run;

/* 2. Histograma pentru Usage_kWh. */
proc sgplot data=steel.clean;
    histogram Usage_kWh / scale=count;
    density Usage_kWh / type=normal;
    title "Distributia consumului pe interval de 15 min";
run;

/* 3. Boxplot pe tip de sarcina. */
proc sgplot data=steel.clean;
    vbox Usage_kWh / category=Load_Type;
    title "Variabilitatea consumului per tip de sarcina";
run;

/* 4. Scatterplot Usage vs reactiv lagging, culoare pe Load_Type. */
proc sgplot data=steel.clean;
    scatter x=Lagging_Current_Reactive_Power_kVarh y=Usage_kWh
        / group=Load_Type markerattrs=(symbol=circlefilled size=4);
    xaxis label="Putere reactiva lagging (kVarh)";
    yaxis label="Consum activ (kWh)";
    title "Consum activ vs putere reactiva";
run;

/* 5. Bar chart: cost total per schimb. */
proc sql;
    create table steel.cost_schimb as
    select schimb, sum(cost_eur) as cost_total label="Cost total (EUR)"
    from steel.clean
    group by schimb;
quit;

proc sgplot data=steel.cost_schimb;
    vbar schimb / response=cost_total datalabel;
    title "Cost total estimat per schimb";
run;

title;
