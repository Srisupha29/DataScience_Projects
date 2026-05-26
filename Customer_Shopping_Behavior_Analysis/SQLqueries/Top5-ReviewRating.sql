-- Which are the top five products with the highest average review rating
select item_purchased, round(avg(review_rating), 2) as 'avg_product_rating'
from customer_shopping_behavior_updated
group by item_purchased
order by avg(review_rating) desc 
limit 5;

