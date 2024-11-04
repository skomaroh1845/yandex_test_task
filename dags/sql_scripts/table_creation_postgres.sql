CREATE TABLE IF NOT EXISTS transactions (
    user_id INT,
    price INT
);

CREATE TABLE IF NOT EXISTS users (
   user_id INT PRIMARY KEY,
   email VARCHAR,
   date_registration TIMESTAMP
);

CREATE TABLE IF NOT EXISTS webinar (
    email VARCHAR
);
