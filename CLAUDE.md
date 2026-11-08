# Working on Frosthold

- The game is one file: `index.html`. No build step.
- **Every gameplay change must update `README.md`.** README.md is shown in-game as the Help screen (cog → Help), so it is the player guide: keep it accurate, player-facing and organised by topic. Remove anything that becomes outdated.
- **Check the tutorial (`TUT` in index.html) after every change** and update a step if the change affects the basics it teaches (moving, chopping, firewood, resources, goal card, walls, warmth/food, growing the town, raids, menu).
- When publishing the claude.ai artifact, include `README.md` in `files` so Help can load it.
- Meshy credits cost money: `tools/meshy_assets.py` only generates models whose prompt is new or changed; run `--dry-run` first.
- Help screenshots live in `assets/help/` and are referenced from README.md as `![caption](assets/help/name.jpg)`. Retake them (daylight, no banners) when the look of that feature changes, and include them in artifact publishes.
