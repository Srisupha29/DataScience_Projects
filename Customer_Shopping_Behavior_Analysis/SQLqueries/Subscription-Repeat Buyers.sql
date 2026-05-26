-- Subscription Adoption among Repeat Buyers
select subscription_status, 
count(customer_id) as repeat_buyers
from customer_shopping_behavior_updated
where previous_purchases > 5 
group by subscription_status;