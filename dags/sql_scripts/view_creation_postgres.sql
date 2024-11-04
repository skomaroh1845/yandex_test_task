
CREATE MATERIALIZED VIEW replenishments AS
WITH first_reg_users AS (
    SELECT * FROM (
        SELECT *, min(date_registration::DATE) OVER (PARTITION BY email) AS first_reg_date
        FROM users
    ) u
    WHERE first_reg_date > '2016-04-01'
)
SELECT w.email AS email, sum(price) AS price_sum
FROM first_reg_users f  -- get users who have first registration after webinar
INNER JOIN webinar w ON f.email = w.email  -- intersecting with users from webinar
INNER JOIN transactions t ON f.user_id = t.user_id  -- getting neccessary transactions
GROUP BY w.email;  -- aggregate data for each participant
