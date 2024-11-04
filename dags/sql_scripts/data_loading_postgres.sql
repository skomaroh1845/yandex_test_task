COPY transactions FROM '/mnt/data_to_load/transactions.csv' DELIMITER ',' CSV HEADER;

COPY users FROM '/mnt/data_to_load/users.csv' DELIMITER ',' CSV HEADER;

COPY webinar FROM '/mnt/data_to_load/webinar.csv' DELIMITER ',' CSV HEADER;