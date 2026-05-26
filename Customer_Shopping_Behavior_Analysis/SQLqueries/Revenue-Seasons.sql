-- Whats the revenue in accordance to seasons

select season, sum(purchase_amount) as revenue, avg(purchase_amount) as AOV
from customer_shopping_behavior_updated
group by season