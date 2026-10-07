USE nyc_airbnb;
DROP TABLE IF EXISTS listings_clean;
CREATE TABLE listings_clean LIKE listings_raw;
INSERT INTO listings_clean SELECT * FROM listings_raw;
SELECT COUNT(*) AS clean_rows FROM listings_clean;
SELECT COUNT(*) AS raw_rows, COUNT(DISTINCT id) AS raw_distinct_ids FROM listings_raw;
TRUNCATE TABLE listings_clean;
INSERT INTO listings_clean SELECT * FROM listings_raw;
TRUNCATE TABLE listings_raw;
LOAD DATA LOCAL INFILE 'D:/Kagal/New York City Airbnb Open Data/New York City Airbnb/New York City Airbnb.csv'
INTO TABLE listings_raw
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
       OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(id, name, host_id, host_name, neighbourhood_group, neighbourhood,
 latitude, longitude, room_type, price, minimum_nights,
 number_of_reviews, last_review, reviews_per_month,
 calculated_host_listings_count, availability_365);
 TRUNCATE TABLE listings_clean;
 INSERT INTO listings_clean SELECT * FROM listings_raw;
 SELECT (SELECT COUNT(*) FROM listings_raw)   AS raw_rows,
       (SELECT COUNT(*) FROM listings_clean) AS clean_rows,
       (SELECT COUNT(DISTINCT id) FROM listings_clean) AS distinct_ids;
       SELECT COUNT(*) AS duplicate_groups,
       COALESCE(SUM(copies - 1), 0) AS extra_rows
FROM (
    SELECT COUNT(*) AS copies
    FROM listings_clean
    GROUP BY name, host_id, neighbourhood, latitude, longitude,
             room_type, price, minimum_nights, number_of_reviews,
             availability_365
    HAVING COUNT(*) > 1
) d;
SELECT
    SUM(price < 0)                         AS negative_price,
    SUM(price = 0)                         AS zero_price,
    SUM(minimum_nights < 1)                AS min_nights_below_1,
    SUM(number_of_reviews < 0)             AS negative_reviews,
    SUM(availability_365 < 0)              AS negative_availability,
    SUM(availability_365 > 365)            AS availability_over_365,
    SUM(calculated_host_listings_count < 1) AS host_count_below_1
FROM listings_clean;
SET SQL_SAFE_UPDATES = 0;
ALTER TABLE listings_clean ADD COLUMN price_valid TINYINT NOT NULL DEFAULT 1;
UPDATE listings_clean SET price_valid = 0 WHERE price = 0;
SELECT price_valid, COUNT(*) AS rows_count
FROM listings_clean
GROUP BY price_valid;
SELECT availability_365, number_of_reviews, COUNT(*) AS rows_count
FROM listings_clean
WHERE price = 0
GROUP BY availability_365, number_of_reviews
ORDER BY availability_365;
SELECT
    SUM(price < 0)                                           AS negative_price,
    SUM(minimum_nights < 1)                                  AS min_nights_below_1,
    SUM(number_of_reviews < 0)                               AS negative_reviews,
    SUM(availability_365 < 0 OR availability_365 > 365)     AS availability_out_of_range,
    SUM(calculated_host_listings_count < 1)                  AS host_count_below_1,
    SUM(price_valid = 0)                                     AS flagged_zero_price,
    -- Check 3: logically impossible rows
    SUM(number_of_reviews = 0 AND last_review <> '')         AS no_reviews_but_has_date,
    SUM(number_of_reviews > 0 AND (last_review IS NULL OR last_review = '')) AS reviews_but_no_date,
    SUM(number_of_reviews = 0 AND reviews_per_month <> '')   AS no_reviews_but_has_rate,
    SUM(latitude  NOT BETWEEN 40.4 AND 41.0
     OR longitude NOT BETWEEN -74.3 AND -73.6)               AS outside_nyc_coordinates
FROM listings_clean;
SELECT MIN(price) AS min_price, MAX(price) AS max_price, ROUND(AVG(price),1) AS avg_price,
       MIN(minimum_nights) AS min_nights, MAX(minimum_nights) AS max_nights,
       MAX(number_of_reviews) AS max_reviews,
       MAX(calculated_host_listings_count) AS max_host_listings
FROM listings_clean;
SELECT SUM(price >= 1000)        AS price_1000_plus,
       SUM(price >= 5000)        AS price_5000_plus,
       SUM(minimum_nights > 365) AS min_nights_over_365,
       SUM(minimum_nights > 30)  AS min_nights_over_30
FROM listings_clean;
SELECT row_id, id, name, neighbourhood_group, room_type, price,
       minimum_nights, availability_365
FROM listings_clean
WHERE price >= 5000 OR minimum_nights > 365
ORDER BY price DESC;
SET SQL_SAFE_UPDATES = 0;
SELECT COUNT(*) AS rows_to_delete FROM listings_clean
WHERE price >= 5000 OR minimum_nights > 365;
DELETE FROM listings_clean WHERE price >= 5000 OR minimum_nights > 365;
SELECT COUNT(*) AS clean_rows FROM listings_clean;
SELECT
    SUM(name IS NULL OR name = '')                           AS missing_name,
    SUM(host_name IS NULL OR host_name = '')                 AS missing_host_name,
    SUM(neighbourhood_group IS NULL OR neighbourhood_group = '') AS missing_borough,
    SUM(neighbourhood IS NULL OR neighbourhood = '')         AS missing_neighbourhood,
    SUM(room_type IS NULL OR room_type = '')                 AS missing_room_type,
    SUM(last_review IS NULL OR last_review = '')             AS missing_last_review,
    SUM(reviews_per_month IS NULL OR reviews_per_month = '') AS missing_reviews_per_month,
    SUM(price IS NULL OR minimum_nights IS NULL
        OR number_of_reviews IS NULL OR availability_365 IS NULL) AS missing_numeric
FROM listings_clean;
SET SQL_SAFE_UPDATES = 0;
SELECT COUNT(*) AS rows_to_delete FROM listings_clean
WHERE name IS NULL OR name = '' OR host_name IS NULL OR host_name = '';
DELETE FROM listings_clean
WHERE name IS NULL OR name = '' OR host_name IS NULL OR host_name = '';
SELECT COUNT(*) AS clean_rows FROM listings_clean;
UPDATE listings_clean SET last_review = NULL WHERE last_review = '';
UPDATE listings_clean SET reviews_per_month = NULL WHERE reviews_per_month = '';

ALTER TABLE listings_clean
  MODIFY last_review DATE NULL,
  MODIFY reviews_per_month DECIMAL(6,2) NULL;

SELECT COUNT(*) AS clean_rows,
       SUM(last_review IS NULL) AS null_review_dates
FROM listings_clean;
SELECT COUNT(*) AS clean_rows,
       SUM(last_review IS NULL)       AS null_review_dates,
       SUM(reviews_per_month IS NULL) AS null_rate,
       MIN(last_review)               AS first_review,
       MAX(last_review)               AS last_review_date
FROM listings_clean;
SET SQL_MODE = '';
UPDATE listings_clean SET last_review = NULL WHERE last_review = '0000-00-00';
SELECT
    SUM(name <> TRIM(name))                             AS name_spaces,
    SUM(host_name <> TRIM(host_name))                   AS host_spaces,
    SUM(neighbourhood_group <> TRIM(neighbourhood_group)) AS borough_spaces,
    SUM(neighbourhood <> TRIM(neighbourhood))           AS neighbourhood_spaces,
    SUM(room_type <> TRIM(room_type))                   AS room_type_spaces,
    COUNT(DISTINCT BINARY neighbourhood_group) AS boroughs_exact,
    COUNT(DISTINCT UPPER(neighbourhood_group)) AS boroughs_upper,
    COUNT(DISTINCT BINARY neighbourhood)       AS neighbourhoods_exact,
    COUNT(DISTINCT UPPER(neighbourhood))       AS neighbourhoods_upper,
    COUNT(DISTINCT BINARY room_type)           AS room_types_exact,
    COUNT(DISTINCT UPPER(room_type))           AS room_types_upper
FROM listings_clean;
SET SQL_SAFE_UPDATES = 0;
UPDATE listings_clean
SET name = TRIM(REPLACE(REPLACE(name, CHAR(13), ' '), CHAR(10), ' '))
WHERE name <> TRIM(name) OR name LIKE '%\r%' OR name LIKE '%\n%';
SELECT COUNT(*) AS clean_rows,
       SUM(name <> TRIM(name)) AS name_spaces_left,
       SUM(name LIKE '%\n%' OR name LIKE '%\r%') AS name_linebreaks_left
FROM listings_clean;
SELECT COUNT(*) AS clean_rows,
       SUM(last_review IS NULL)       AS null_review_dates,
       SUM(reviews_per_month IS NULL) AS null_rate,
       MIN(last_review)               AS first_review,
       MAX(last_review)               AS last_review_date
FROM listings_clean;
SET SESSION sql_mode = '';
SET SQL_SAFE_UPDATES = 0;
UPDATE listings_clean SET last_review = NULL WHERE number_of_reviews = 0;
UPDATE listings_clean SET reviews_per_month = NULL WHERE number_of_reviews = 0;
SELECT COUNT(*)                                      AS clean_rows,
       SUM(last_review IS NULL)                      AS null_review_dates,
       SUM(reviews_per_month IS NULL)                AS null_rate,
       MIN(last_review)                              AS first_review,
       MAX(last_review)                              AS last_review_date,
       SUM(name <> TRIM(name))                       AS name_spaces_left,
       SUM(name LIKE '%\n%' OR name LIKE '%\r%')     AS name_linebreaks_left
FROM listings_clean;



