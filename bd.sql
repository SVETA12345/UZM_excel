
alter table excel_parcer_data add date DATETIME;
select * from excel_parcer_data;
CREATE INDEX idx_date ON excel_parcer_data(date) WHERE date IS NOT NULL;