<<<<<<< HEAD

alter table excel_parcer_data add date DATETIME;
select * from excel_parcer_data;
CREATE INDEX idx_date ON excel_parcer_data(date) WHERE date IS NOT NULL;
=======
select * from report_graph3;
alter table report_graph3 add y_minBz real;
alter table report_graph3 add y_maxBz real;
alter table report_graph3 add y_delBz real;
select * from report_graph3;
select * from report_graph3;
alter table report_graph1 add y_minGz real;
alter table report_graph1 add y_maxGz real;
alter table report_graph1 add y_delGz real;
select * from report_graph1;
>>>>>>> 8391fa52c91285a0ae0755fc84e395a99d7b57fe
