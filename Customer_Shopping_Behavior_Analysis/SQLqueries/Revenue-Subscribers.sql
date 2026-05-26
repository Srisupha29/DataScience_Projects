-- Do subscribed customers spend more? Compare average spend and total revenue between subscribers and non-subscribers
select subscription_status, 
count(customer_id) as total_customers,
round(avg(purchase_amount), 2) as average_spend,
sum(purchase_amount) as revenue
from customer_shopping_behavior_updated
group by subscription_status;

# Even though the average spend is similar, the total revenue is much higher for people without a subscription
