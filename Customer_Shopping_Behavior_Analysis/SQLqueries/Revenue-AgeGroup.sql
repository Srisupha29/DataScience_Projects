
-- What is the revenue contribution of each age group?

select age_group,
sum(purchase_amount) as total_revenue
from customer_shopping_behavior_updated
group by age_group 
order by total_revenue desc;