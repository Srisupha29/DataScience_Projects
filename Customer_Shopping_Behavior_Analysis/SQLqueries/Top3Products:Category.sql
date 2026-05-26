-- What are the top three most purchased products within each category

with item_counts as (
select category, item_purchased,
count(customer_id) as total_orders,
row_number() over(partition by category order by count(customer_id) desc) as item_rank
from customer_shopping_behavior_updated
group by category, item_purchased
)

select item_rank, item_purchased, category, total_orders
from item_counts
where item_rank <= 3;