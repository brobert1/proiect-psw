/*------------------------------------------------------------------
  02_formats.sas
  Obiectiv : definirea si utilizarea formatelor proprii
  Facilitate acoperita : "crearea si folosirea de formate definite de utilizator"
------------------------------------------------------------------*/

proc format;
    /* Numeric -> etichete pentru tipul de sarcina codificat. */
    value loadfmt
        1 = "Light Load"
        2 = "Medium Load"
        3 = "Maximum Load";

    /* Character -> character pentru ierarhizarea zilelor saptamanii. */
    value $wkfmt
        "Weekday" = "Zi lucratoare"
        "Weekend" = "Zi nelucratoare";

    /* Benzi orare pentru tariful industrial diferentiat (pe ore). */
    value shiftfmt
        0-5   = "Off-peak (00-06)"
        6-9   = "Shoulder (06-10)"
        10-17 = "Peak (10-18)"
        18-21 = "Shoulder (18-22)"
        22-23 = "Off-peak (22-24)";

    /* Benzi tarifare pentru consumul kWh pe un interval de 15 min. */
    value kwhfmt
        low  -< 5    = "Consum mic"
        5    -< 30   = "Consum mediu"
        30   -  high = "Consum ridicat";
run;

/* Aplicarea formatelor (fara modificarea datelor). */
proc freq data=steel.raw;
    tables Load_Type WeekStatus;
    format WeekStatus $wkfmt.;
    title "Distributia tipurilor de sarcina si a starii saptamanii";
run;

title;
