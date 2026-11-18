window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "pbi-star", area: "powerbi", title: "Star schema and data modeling", mins: 35, level: 3, light: false,
    res: { label: "Microsoft Learn: star schema and Power BI", url: "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema", src: "free" },
    aloud: "Explain fact tables and dimension tables with a sales example, and why one wide flat table is a worse model.",
    interviewQ: "You are given one huge Excel sheet with sales, products, customers and dates in the same table. How do you model it in Power BI?",
    quiz: [
      { q: "In a star schema, what do fact tables and dimension tables hold?",
        options: ["Facts hold descriptive attributes and dimensions hold events", "Facts hold measurable events such as sales, and dimensions hold descriptive attributes such as product or date", "Both hold the same data", "Facts hold only text"],
        answer: 1, why: "Facts are rows of things that happened, which you aggregate. Dimensions describe them and are what you filter and group by." },
      { q: "Why is a star schema usually better than one flat wide table in Power BI?",
        options: ["It is required by Microsoft", "It reduces duplication, makes the model smaller and faster, and makes filtering clearer", "It removes the need for DAX", "It makes data refresh instant"],
        answer: 1, why: "Descriptive attributes are stored once in dimensions instead of repeated on every fact row." },
      { q: "What is the usual relationship between a dimension and a fact table?",
        options: ["One-to-many, from the dimension to the fact", "Many-to-many in both directions", "One-to-one", "No relationship"],
        answer: 0, why: "One product or date row relates to many sales rows, and filters flow from the dimension to the fact." }
    ]
  },
  {
    id: "pbi-calculate", area: "powerbi", title: "DAX: CALCULATE and filter context", mins: 40, level: 3, light: false,
    res: { label: "Microsoft Learn: CALCULATE function", url: "https://learn.microsoft.com/en-us/dax/calculate-function-dax", src: "free" },
    aloud: "Explain filter context, and how CALCULATE changes it, using a total sales measure and a slicer.",
    interviewQ: "What is the difference between a measure and a calculated column, and when do you use each?",
    quiz: [
      { q: "What does CALCULATE do?",
        options: ["Sorts a table", "Evaluates an expression in a filter context that you modify", "Creates a relationship", "Refreshes the data"],
        answer: 1, why: "CALCULATE lets you add, remove or replace filters before evaluating an expression, which is the core of most useful DAX." },
      { q: "How does a measure differ from a calculated column?",
        options: ["They are identical", "A measure is evaluated at query time in the current filter context, while a calculated column is computed row by row at refresh and stored", "A measure is stored in the table", "A calculated column responds to slicers"],
        answer: 1, why: "Measures react to slicers and visuals. Calculated columns are fixed values stored in the model." },
      { q: "Which function removes existing filters from a table inside CALCULATE?",
        options: ["ALL", "VALUES", "SUMX", "RELATED"],
        answer: 0, why: "ALL(table) ignores filters on that table. VALUES returns the distinct values that are still visible under the current filters." }
    ]
  },
  {
    id: "pbi-time", area: "powerbi", title: "Time intelligence: YTD and year over year", mins: 35, level: 3, light: false,
    res: { label: "Microsoft Learn: time intelligence functions", url: "https://learn.microsoft.com/en-us/dax/time-intelligence-functions-dax", src: "free" },
    aloud: "Explain why time intelligence needs a proper date table and what YTD and same period last year each return.",
    interviewQ: "Build a measure for year-over-year sales growth. What do you need in the model first?",
    quiz: [
      { q: "What does DAX time intelligence need in the model to work reliably?",
        options: ["A date table with one row for every day and no gaps, marked as the date table", "Only a date column in the fact table", "A text column for months", "A calculated column for years"],
        answer: 0, why: "The functions shift and compare date ranges, so the calendar must be continuous." },
      { q: "Which function returns the year-to-date total?",
        options: ["TOTALYTD", "SAMEPERIODLASTYEAR", "RELATED", "DISTINCTCOUNT"],
        answer: 0, why: "TOTALYTD (or CALCULATE with DATESYTD) accumulates from the start of the year to the current date in context." },
      { q: "What does SAMEPERIODLASTYEAR return?",
        options: ["The dates in the current context shifted back one year", "Next year's dates", "The total for all years", "The first day of the year"],
        answer: 0, why: "It is the standard building block for year-over-year comparisons, used inside CALCULATE." }
    ]
  },
  {
    id: "pbi-query", area: "powerbi", title: "Power Query transformations", mins: 30, level: 2, light: false,
    res: { label: "Microsoft Learn: what is Power Query", url: "https://learn.microsoft.com/en-us/power-query/power-query-what-is-power-query", src: "free" },
    aloud: "Explain what Power Query does before data reaches the model, and what query folding is.",
    interviewQ: "Your data has one column per month (Jan, Feb, Mar...). How do you reshape it for analysis?",
    quiz: [
      { q: "What is Power Query used for?",
        options: ["Writing DAX measures", "Connecting to, cleaning and shaping data before it loads into the model", "Designing dashboards", "Setting up row-level security"],
        answer: 1, why: "It is the extract-and-transform step, and each step you apply is recorded and repeated on refresh." },
      { q: "What is query folding?",
        options: ["Hiding a query", "Power Query pushing transformation steps back to the source database as a native query, for speed", "Merging two tables", "Compressing the model"],
        answer: 1, why: "When steps fold, the database does the heavy work. Some transformations break folding and slow refreshes." },
      { q: "What does unpivoting columns do?",
        options: ["Turns column headers such as months into rows of attribute and value pairs", "Deletes columns", "Merges two tables", "Sorts the data"],
        answer: 0, why: "Month-per-column data is hard to analyze. Unpivoting gives one row per month, which suits charts and DAX." }
    ]
  },
  {
    id: "pbi-storage", area: "powerbi", title: "Import vs DirectQuery", mins: 30, level: 2, light: false,
    res: { label: "Microsoft Learn: DirectQuery in Power BI", url: "https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-directquery-about", src: "free" },
    aloud: "Compare Import and DirectQuery in terms of speed, freshness and limits, and say how you would choose.",
    interviewQ: "A dashboard must show data that is at most five minutes old, from a very large database. Which storage mode would you consider and what is the catch?",
    quiz: [
      { q: "What does Import mode do?",
        options: ["Queries the source for every visual", "Loads a compressed copy of the data into the model, which is refreshed on a schedule", "Streams live data without storing it", "Only works with Excel"],
        answer: 1, why: "Import is usually the fastest for users because the data is held in memory, but it is as fresh as the last refresh." },
      { q: "What is the main trade-off of DirectQuery?",
        options: ["Data is fresher, but performance depends on the source and some features are limited", "Data is older but faster", "It cannot connect to databases", "It needs no gateway"],
        answer: 0, why: "Each interaction sends queries to the source, so a slow source means a slow report." },
      { q: "Data must be near real-time and is too large to import. What is a reasonable option?",
        options: ["Import with a daily refresh", "DirectQuery, or a composite model that mixes modes", "Excel files on a laptop", "Do not use Power BI"],
        answer: 1, why: "DirectQuery avoids copying the data. Composite models can import small dimensions and keep large facts live." }
    ]
  },
  {
    id: "pbi-rls", area: "powerbi", title: "Row-level security", mins: 25, level: 2, light: true,
    res: { label: "Microsoft Learn: row-level security", url: "https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security", src: "free" },
    aloud: "Explain what row-level security does and how a role uses a DAX filter to limit what each person sees.",
    interviewQ: "Sales managers should only see their own region. How do you set that up and test it?",
    quiz: [
      { q: "What does row-level security (RLS) do?",
        options: ["Encrypts the file", "Restricts which rows of data each user can see", "Hides entire reports", "Prevents data refresh"],
        answer: 1, why: "RLS filters the rows a person can see, so one report can serve many audiences safely." },
      { q: "How is an RLS role defined?",
        options: ["With a DAX filter expression on one or more tables, such as [Region] = \"Asia\"", "With a Power Query step", "By renaming the table", "By hiding columns"],
        answer: 0, why: "The expression is applied as a filter whenever a member of the role views the data." },
      { q: "How can you check a role before publishing it?",
        options: ["You cannot", "Use 'View as' to see the report as that role", "Ask users to try it", "Delete the role and recreate it"],
        answer: 1, why: "Testing each role avoids accidentally exposing or hiding data." }
    ]
  },
  {
    id: "pbi-visuals", area: "powerbi", title: "Choosing the right visual", mins: 25, level: 1, light: true,
    res: { label: "Microsoft Learn: visualization types in Power BI", url: "https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a", src: "free" },
    aloud: "Pick a visual for each of these: a trend over time, a ranking of many categories, a share of a total, and a comparison of two measures.",
    interviewQ: "A stakeholder asks for a pie chart with 15 slices. What do you suggest instead and why?",
    quiz: [
      { q: "Which visual is best for showing a trend over time?",
        options: ["Line chart", "Pie chart", "Treemap", "Card"],
        answer: 0, why: "Lines make the direction and the rate of change over a continuous axis easy to see." },
      { q: "You need to compare values across 15 categories. What is the best choice?",
        options: ["A pie chart with 15 slices", "A sorted bar chart", "A gauge", "A 3D chart"],
        answer: 1, why: "Humans compare lengths of aligned bars more accurately than angles, and sorting shows the ranking at once." },
      { q: "What does a slicer do?",
        options: ["Cuts a visual in half", "Lets viewers filter the other visuals on the page", "Adds a new measure", "Exports data"],
        answer: 1, why: "A slicer applies a filter to the visuals it is connected to, and viewers use it to explore." }
    ]
  }
]);
