-- egmnet customers into new, returning, and loyal based on their total number of previous purchases 
-- and show the count of each segment

with customer_type as 
(select customer_id, previous_purchases,
case when previous_purchases = 1 then 'New'
     when previous_purchases between 2 and 10 then 'Returning'
     else 'Loyal'
     end as customer_segment
from customer_shopping_behavior_updated)

select customer_segment, count(*) as 'Number of Customers'
from customer_type
group by customer_segment;