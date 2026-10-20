# Morning brief

A page that rebuilds itself every morning (about 07:17 Bangkok time) with four tabs:
world news with the story behind it, AI news, markets, and data science / ML reading.
It runs for free on GitHub; the only cost is a few cents of Claude API credit per day.

## Set it up (about 20 minutes)

1. **Get an API key.** In the Anthropic Console (platform.claude.com), add $5 of credit
   and create an API key.
2. **Create a GitHub repo** (public, because free GitHub Pages needs that) and upload
   everything in this folder. If the hidden `.github` folder doesn't upload, use
   Add file, Create new file, type `.github/workflows/daily.yml` as the name, and paste in
   the contents of that file.
3. **Add the key.** Repo, Settings, Secrets and variables, Actions, New repository secret.
   Name: `ANTHROPIC_API_KEY`. Value: your key.
4. **Turn on Pages.** Repo, Settings, Pages, Source: **GitHub Actions**.
5. **Run it once.** Repo, Actions tab, "Build daily brief", Run workflow. After a minute
   or two, your page is live at `https://<your-username>.github.io/<repo-name>/`.

From then on it updates by itself every day. Bookmark the page on your phone.

## Customise

Everything lives in `config.py`: news feeds, the stocks you track, the indices, and the
list of finance topics that rotate daily. Add or remove lines and commit.

## Try it on your computer

```
pip install -r requirements.txt
python build.py --sample      # fake data, just to preview the layout
python build.py --no-ai       # real headlines, no summaries, free
ANTHROPIC_API_KEY=sk-... python build.py
```

Then open `docs/index.html`.

## Good to know

- The page is public to anyone who has the link. It only contains news summaries, and your
  API key is never placed on it.
- Scheduled runs can start a few minutes late. GitHub also pauses schedules on repos with
  no activity for 60 days; re-enable them from the Actions tab if that happens.
- The "worth researching" stocks are starting points, not recommendations.
- To cut cost further, keep the default model (`claude-haiku-5-5`). Set a `MODEL` value in
  the workflow to try a stronger one.
