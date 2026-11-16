window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "sql-window", area: "sql", title: "Window functions: ROW_NUMBER, RANK, LAG", mins: 35, level: 3, light: false,
    res: { label: "PostgreSQL docs: window functions tutorial", url: "https://www.postgresql.org/docs/current/tutorial-window.html", src: "free" },
    aloud: "Explain how a window function differs from GROUP BY, then describe how you would find each customer's previous order.",
    interviewQ: "Write a query that returns the top 3 products by revenue within each category.",
    quiz: [
      { q: "Three rows tie for first place. What is the difference between RANK() and ROW_NUMBER()?",
        options: ["They are identical", "RANK gives tied rows the same rank and skips the next numbers, while ROW_NUMBER always gives unique numbers", "ROW_NUMBER gives ties the same number", "RANK cannot be used with ORDER BY"],
        answer: 1, why: "With a three-way tie for first, RANK returns 1, 1, 1, 4. ROW_NUMBER returns 1, 2, 3, 4, breaking ties arbitrarily unless you add a tie-breaker." },
      { q: "Which expression returns each customer's previous order amount, ordered by date?",
        options: ["LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date)", "LEAD(amount) OVER (ORDER BY customer_id)", "SUM(amount) GROUP BY customer_id", "ROW_NUMBER() OVER (PARTITION BY amount)"],
        answer: 0, why: "LAG looks back within the partition, and ORDER BY defines what 'previous' means. LEAD would look forward." },
      { q: "How does a window function differ from GROUP BY?",
        options: ["It collapses rows into one per group", "It keeps every input row and adds a computed column", "It can only be used on numeric columns", "It requires a HAVING clause"],
        answer: 1, why: "Window functions compute across related rows but do not collapse them, so you can show row details next to a group total or rank." }
    ]
  },
  {
    id: "sql-joins", area: "sql", title: "Joins and where NULLs bite", mins: 30, level: 2, light: false,
    res: { label: "DataCamp: Joining Data in SQL", url: "https://www.datacamp.com/courses/joining-data-in-sql", src: "datacamp" },
    aloud: "Explain INNER, LEFT and FULL joins using customers and orders, and say what happens to rows with no match.",
    interviewQ: "After joining customers to orders, your row count went up. Why, and how do you check it?",
    quiz: [
      { q: "You LEFT JOIN customers to orders. What do you get for a customer with no orders?",
        options: ["The customer is dropped", "One row with NULLs in the order columns", "An error", "A row with zeros in the order columns"],
        answer: 1, why: "A LEFT JOIN keeps every row from the left table and fills missing right-side columns with NULL." },
      { q: "A query does customers LEFT JOIN orders, then adds WHERE orders.status = 'paid'. Why does it behave like an INNER JOIN?",
        options: ["WHERE removes the NULL rows from unmatched customers because NULL = 'paid' is not true", "LEFT JOIN is ignored when WHERE is present", "The status column is indexed", "SQL rewrites it to a FULL JOIN"],
        answer: 0, why: "Unmatched customers have NULL status, and the WHERE filter discards them. Put the condition in the ON clause to keep them." },
      { q: "One customer row joins to 3 order rows. How many rows come back?",
        options: ["1", "3", "4", "0"],
        answer: 1, why: "A one-to-many join repeats the customer once per matching order. This is why summing a customer-level column after a join double-counts." }
    ]
  },
  {
    id: "sql-cte", area: "sql", title: "CTEs and subqueries", mins: 30, level: 2, light: false,
    res: { label: "PostgreSQL docs: WITH queries (CTEs)", url: "https://www.postgresql.org/docs/current/queries-with.html", src: "free" },
    aloud: "Explain what a CTE is, why you would use one, and how it differs from a subquery or a temporary table.",
    interviewQ: "Rewrite a query with three nested subqueries into CTEs and explain why it is easier to read and debug.",
    quiz: [
      { q: "What is the main purpose of a CTE (WITH clause)?",
        options: ["To permanently store a table", "To give an intermediate result a name so a query is easier to read and reuse", "To make every query faster", "To replace indexes"],
        answer: 1, why: "A CTE is mainly a readability tool. Performance depends on the database and the query." },
      { q: "How long does a CTE exist?",
        options: ["Until the session ends", "For the duration of the single statement that defines it", "Until the database restarts", "Forever"],
        answer: 1, why: "A CTE is not stored. It exists only inside the statement that follows the WITH clause." },
      { q: "A recursive CTE is typically used for:",
        options: ["Sorting large tables", "Hierarchical data such as an employee-manager tree", "Removing duplicates", "Creating indexes"],
        answer: 1, why: "Recursion lets a query walk parent-child relationships of unknown depth." }
    ]
  },
  {
    id: "sql-groupby", area: "sql", title: "GROUP BY, HAVING and NULL-safe aggregation", mins: 25, level: 2, light: true,
    res: { label: "PostgreSQL docs: aggregate functions", url: "https://www.postgresql.org/docs/current/functions-aggregate.html", src: "free" },
    aloud: "Explain the difference between WHERE and HAVING, and what each aggregate does with NULLs.",
    interviewQ: "Find customers who placed more than 5 orders in 2025. Which clause does each condition go in?",
    quiz: [
      { q: "What is the difference between WHERE and HAVING?",
        options: ["They are identical", "WHERE filters rows before grouping, while HAVING filters groups after aggregation", "HAVING filters rows before grouping", "WHERE can only be used with numbers"],
        answer: 1, why: "You cannot use an aggregate like COUNT(*) in WHERE because the groups do not exist yet." },
      { q: "A column has the values 10, 20 and NULL. What does COUNT(col) return, compared with COUNT(*)?",
        options: ["COUNT(col) is 2 and COUNT(*) is 3", "Both are 3", "Both are 2", "COUNT(col) is 3 and COUNT(*) is 2"],
        answer: 0, why: "COUNT(col) skips NULLs, while COUNT(*) counts rows." },
      { q: "What does AVG return for the values 10, 20 and NULL?",
        options: ["10", "15", "20", "30"],
        answer: 1, why: "AVG ignores NULLs, so it averages 10 and 20 to get 15. It does not treat NULL as zero." }
    ]
  },
  {
    id: "sql-indexes", area: "sql", title: "Indexes and reading query plans", mins: 35, level: 3, light: false,
    res: { label: "PostgreSQL docs: indexes introduction", url: "https://www.postgresql.org/docs/current/indexes-intro.html", src: "free" },
    aloud: "Explain what an index does, what it costs, and how EXPLAIN helps you decide whether a query needs one.",
    interviewQ: "A query on a 50-million-row table is slow. How do you investigate?",
    quiz: [
      { q: "What is the trade-off of adding an index?",
        options: ["Faster reads on that column, but slower writes and extra storage", "Faster writes and slower reads", "No trade-off", "It changes the table's data"],
        answer: 0, why: "Every insert or update must also maintain the index." },
      { q: "In PostgreSQL there is a plain index on email. Which query will not use that index efficiently?",
        options: ["WHERE email = 'a@b.com'", "WHERE LOWER(email) = 'a@b.com'", "WHERE email IN ('a@b.com', 'c@d.com')", "ORDER BY email LIMIT 10"],
        answer: 1, why: "Wrapping the column in a function stops the planner from using the plain index. An expression index on LOWER(email) would fix it." },
      { q: "In an EXPLAIN plan, what does a 'Seq Scan' mean?",
        options: ["The database read the whole table", "The database used an index", "The query was cached", "The query failed"],
        answer: 0, why: "A sequential scan reads every row. It is fine for small tables, but a warning sign on large ones with selective filters." }
    ]
  },
  {
    id: "sql-dedupe", area: "sql", title: "Finding and removing duplicates", mins: 25, level: 2, light: true,
    res: { label: "PostgreSQL docs: SELECT and DISTINCT", url: "https://www.postgresql.org/docs/current/sql-select.html", src: "free" },
    aloud: "Describe two ways to find duplicate rows and one way to keep only the most recent row per user.",
    interviewQ: "A users table has multiple rows per email. Keep only the most recently updated row for each email.",
    quiz: [
      { q: "Which query finds emails that appear more than once?",
        options: ["SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1", "SELECT DISTINCT email FROM users", "SELECT email FROM users WHERE COUNT(*) > 1", "SELECT email FROM users ORDER BY email"],
        answer: 0, why: "Group by the column, then use HAVING to keep groups with more than one row." },
      { q: "How do you keep only the latest row per user_id?",
        options: ["ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) and keep row number 1", "SELECT DISTINCT user_id", "ORDER BY updated_at LIMIT 1", "GROUP BY user_id, updated_at"],
        answer: 0, why: "Number the rows within each user from newest to oldest, then filter to 1. LIMIT 1 would return only one row in total." },
      { q: "SELECT DISTINCT a, b FROM t removes duplicates based on:",
        options: ["Column a only", "The combination of a and b", "Column b only", "The primary key"],
        answer: 1, why: "DISTINCT applies to the whole selected row, not to the first column." }
    ]
  },
  {
    id: "sql-case", area: "sql", title: "CASE WHEN and conditional aggregation", mins: 30, level: 2, light: false,
    res: { label: "PostgreSQL docs: conditional expressions", url: "https://www.postgresql.org/docs/current/functions-conditional.html", src: "free" },
    aloud: "Explain how SUM(CASE WHEN ...) lets you build several metrics in one pass over the data.",
    interviewQ: "From an orders table, return one row per day with total orders, paid orders and refunded orders.",
    quiz: [
      { q: "What does SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) compute?",
        options: ["The total amount for paid orders", "The number of paid orders", "The total amount for all orders", "The average paid amount"],
        answer: 0, why: "Rows that are not paid contribute 0, so the sum covers only paid orders." },
      { q: "A CASE expression has no ELSE and no condition matches. What is returned?",
        options: ["0", "An empty string", "NULL", "An error"],
        answer: 2, why: "Without ELSE, unmatched rows return NULL." },
      { q: "Which expression counts only rows where status is 'paid'?",
        options: ["COUNT(CASE WHEN status = 'paid' THEN 1 END)", "COUNT(status = 'paid')", "SUM(status)", "COUNT(DISTINCT status)"],
        answer: 0, why: "COUNT ignores NULLs, and the CASE returns NULL for non-paid rows. COUNT(status = 'paid') counts every row with a non-null boolean, including false." }
    ]
  }
]);
