-- Get the top 5 places with the highest revenue

select location, sum(purchase_amount) as revenue  
from customer_shopping_behavior_updated
group by location
order by revenue desc
limit 5 