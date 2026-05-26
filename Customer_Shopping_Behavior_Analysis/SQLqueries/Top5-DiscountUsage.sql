-- Top 5 Products by Discount Usage

select item_purchased,  
round(sum(case when discount_applied = 'Yes' then 1 else 0 end)/count(*) *100, 2) as discount_rate 
from customer_shopping_behavior_updated 
group by item_purchased 
order by discount_rate desc 
limit 5
