-- SQLite-compatible retail business queries

-- Revenue by category
SELECT category,
       ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS revenue
FROM retail_sales
GROUP BY category
ORDER BY revenue DESC;

-- Revenue by region
SELECT region,
       ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS revenue
FROM retail_sales
GROUP BY region
ORDER BY revenue DESC;

-- Monthly revenue
SELECT strftime('%Y-%m', order_date) AS month,
       ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS revenue
FROM retail_sales
GROUP BY month
ORDER BY month;

-- Top 10 products
SELECT product,
       SUM(quantity) AS units_sold,
       ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS revenue
FROM retail_sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;

-- Highest-value customers
SELECT customer_id,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS revenue
FROM retail_sales
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;
