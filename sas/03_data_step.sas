/*------------------------------------------------------------------
  03_data_step.sas
  Obiective :
    - procesare iterativa si conditionala a datelor (DO, IF/THEN)
    - utilizare de functii SAS (HOUR, WEEKDAY, INTNX, ROUND, SUM)
    - utilizare de masive (ARRAY)
------------------------------------------------------------------*/

/* 1. DATA step imbogatit : parsare data, flaguri, coloane economice. */
data steel.clean;
    set steel.raw;

    stamp    = date;
    ora      = hour(date);
    zi_sapt  = weekday(datepart(date));    /* 1=Duminica ... 7=Sambata */
    luna     = month(datepart(date));

    /* Eticheta pentru schimb, folosind IF/THEN/ELSE. */
    length schimb $12;
    if ora < 6 then schimb = "Noapte";
    else if ora < 14 then schimb = "Dimineata";
    else if ora < 22 then schimb = "Dupa-amiaza";
    else schimb = "Noapte";

    /* Flag zi de vara (IUN-AUG) pentru analize sezoniere. */
    is_vara = (luna in (6, 7, 8));

    /* Cost energie (EUR) pentru intervalul de 15 min. */
    cost_eur = round(Usage_kWh * 0.15, 0.01);

    /* Estimare factor de putere aparent cosφ. */
    if Usage_kWh > 0 then
        cos_phi = Usage_kWh / sqrt(Usage_kWh**2 + 'Lagging_Current_Reactive.Power_k'n**2);
    else cos_phi = 1;
    cos_phi = round(cos_phi, 0.001);

    format stamp datetime20.;
run;

/* 2. Masiv (ARRAY) : recalibrare valori negative in coloanele numerice. */
data steel.array_demo;
    set steel.clean;

    array num_vars {*} Usage_kWh 'Lagging_Current_Reactive.Power_k'n
                       Leading_Current_Reactive_Power_k;
    array neg_flag {3} neg1 neg2 neg3;

    do i = 1 to dim(num_vars);
        if num_vars{i} < 0 then do;
            neg_flag{i} = 1;
            num_vars{i} = 0;                 /* reparatie defensiva */
        end;
        else neg_flag{i} = 0;
    end;
    drop i;
run;

/* 3. Agregari zilnice folosind BY + FIRST/LAST intr-un DATA step. */
data steel.with_day;
    set steel.clean;
    zi = datepart(stamp);
    format zi date9.;
run;

proc sort data=steel.with_day;
    by zi;
run;

data steel.daily;
    set steel.with_day;
    by zi;
    retain kwh_zi 0 co2_zi 0 cost_zi 0 n_obs 0;

    if first.zi then do;
        kwh_zi = 0; co2_zi = 0; cost_zi = 0; n_obs = 0;
    end;

    kwh_zi + Usage_kWh;
    co2_zi + CO2_tCO2_;
    cost_zi + cost_eur;
    n_obs + 1;

    if last.zi then output;
    format zi date9.;
    keep zi kwh_zi co2_zi cost_zi n_obs;
run;
