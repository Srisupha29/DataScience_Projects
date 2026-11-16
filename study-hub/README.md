# Study hub

A page that picks one small study topic a day, links one resource, and checks you with a 3-question quiz.

## Start it (GitHub Pages)

1. Unzip `study-hub.zip`. You get one folder called `study-hub`.
2. Copy that folder into your `DataScience_Projects` repo, next to `daily-brief`.
3. In a terminal inside the repo:
   ```
   git add study-hub
   git commit -m "Add study hub"
   git push
   ```
4. Wait 1-2 minutes, then open the page. If your daily brief address ends in `/daily-brief/`, this one ends in `/study-hub/`.
   If it does not load, open the repo's Settings, then Pages, and check which folder or branch is published.
5. On your phone, use "Add to Home Screen" so it opens like an app.

To try it on your laptop first, open `index.html` in a browser. It works without a server.

## Using it each day

- The card shows today's topic, one resource, the time it should take, a say-it-aloud prompt and an interview question.
- **Done, check me** starts a 3-question quiz. Get 2 of 3 and the topic is mastered. Miss it and the topic comes back in 3 days.
- **Not sure yet** brings the topic back in 2 days, with no quiz.
- **Give me another** swaps the topic (2 per day). **Low energy** switches to a lighter topic and does not use a swap.
- Topics rotate through ML, statistics, SQL, LLMs and AI, Python and Power BI.

## Your progress

Progress is saved in the browser you use, so your phone and laptop keep separate progress.
Use **Export backup** on one and **Import backup** on the other to move it. Export now and then as a backup too.

## Flagged questions

If a quiz question looks wrong, press **This question is wrong**. Later, press **Copy flagged questions** at the bottom of the page and paste them to Claude to be fixed.

## Adding topics

Topics live in the `data` folder, one file per subject. Each topic looks like this:

```js
{
  id: "stats-example", area: "stats", title: "Topic title", mins: 30, level: 2, light: false,
  res: { label: "Name of the resource", url: "https://...", src: "free" },   // src is "free" or "datacamp"
  aloud: "Explain ... out loud.",
  interviewQ: "An interview-style question.",
  quiz: [
    { q: "Question text?", options: ["A", "B", "C", "D"], answer: 1, why: "Why the answer is right." }
    // exactly 3 questions; answer is the position of the right option, starting at 0
  ]
}
```

Areas are `stats`, `ml`, `sql`, `llm`, `python` and `powerbi`. Set `light: true` for short, easier topics that the Low energy button can pick.
