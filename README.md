# Frosthold Outpost

An original survival and town-building game for phones and desktop browsers. Lead a frozen settlement: gather wood, meat, stone and gold, keep your people warm and fed, wall in the fort, and grow it from a camp into a citadel while wolves and yetis raid from the wilds.

Open `index.html` in a browser. There is no build step; three.js r128 loads from cdnjs.

## Controls
- **Touch / mouse:** drag anywhere for a floating joystick
- **Keyboard:** WASD or arrow keys

Your axes swing automatically at trees, rocks, yaks and raiders in reach. With a full pack, extra logs and stone drop on the ground for later. Stand on a build space to pay for it with what you carry. Stand on a stall's counter side to hand over goods, and on a cash pallet to collect.

## Wild encounters
Monster camps guard treasure chests across the wilds; the minimap marks them (orange easy, red medium, purple dangerous, gold when cleared). Near the fort you meet spiders, goblins and wolves; farther out bears and trolls; at the edges of the map wraiths and stone golems. Defeat every guard, then step on the chest. Treasures give weapons (Frostbite Axe, Ember Cleaver, Runic Greataxe), armour (Fur Jerkin, Iron Mail, Runic Plate), heart stones (+health), war runes (+damage), wind charms (+speed), storage charms (bigger piles), ember totems (repair walls, longer-lasting firewood), yak totems, plus cash and materials. New camps appear over time.

## Exploring
The valley spans roughly 430 m by 430 m. Monster camps start about 65 m from the fort, and crystal veins lie 170–290 m out. The farther from the fort you go, the tougher the monsters, the richer the treasure, and the further out the stone quarries (middle distance) and crystal veins (the far edges). The minimap shows a 140 m window around you, with an arrow and distance pointing home when the fort is off the map. It starts dark: it reveals ground that you or a co-op teammate have walked near, and remembers it in your save.

## Days, nights and seasons
A day lasts 4 minutes; the last part is night, which is darker, colder (more firewood burned, worst in winter) and more dangerous (monsters spot you from farther and hit harder; raids bring extra wolves). Every 3 days the season turns: winter, spring, summer, autumn, then a new year. The ground, trees, ponds and lakes change with each season; summer needs the least firewood, winter the most, and blizzards only blow in winter. Lakes block your path except in winter, when they freeze over.

## Things to find
Meadows of yaks graze all around the valley. Ruins (standing stones, abandoned cabins, watchtowers, shrines, sled wrecks) each hide a cache you can search once for gold, materials, med kits or heart stones. Lakes and ruins show on the minimap once explored.

## Knockouts and revives
- Solo: you respawn at the Town Hall a few seconds after being knocked out, and your pack spills where you fell.
- **Med Center** (Town Hall II): revives you where you fell, once every 5 minutes. In co-op each player has their own 5-minute timer.
- **Med kits**: buy them at the Med Center (up to 5) or find them in treasure. Stand next to a downed teammate for two seconds to revive them.

## Crystal
Crystal veins only appear far out in the wilds and need a **Crystal Pick** (Blacksmith research at Town Hall II, or a rare treasure) to mine.

## HUD
- The minimap (right) shows trees, rocks, yaks, piles, camps, raiders, other players and you.
- Tap a resource counter to leave that resource on the ground: you still chop, mine and hunt, but nothing of that kind goes into your pack until you tap it again.
- **Loggers: pile/stall** switches where loggers deliver. Hunters always deliver to the cookhouse once it is built.

## Co-op
**Without a Claude account (self-hosted):** put `index.html` on any website (for example GitHub Pages). On that site, tap **Co-op**, then **Host a game** to get a 4-character room code and a QR link; friends tap **Co-op**, enter the code (or scan the QR) and join. This uses PeerJS for direct browser-to-browser connections, so no account or server is needed; a few strict networks block these connections.

**On claude.ai:**
Tap **Co-op** on the published page. The first player in hosts, so their town is the shared one. Anyone else who opens the page and taps Co-op joins that town with their own hero, pack and wallet, and can chop, fight, build and trade alongside the host. Guests' own saved towns stay untouched; **Leave co-op** returns them to it. If the host leaves, a guest takes over hosting. Players need Contributor (interact) access or higher to host; anyone who can open the page can join as a guest.

## Saving
Progress saves automatically every few seconds and when you leave the page. Saves are stored only in this browser. Use **New game** (tap twice) to start over.

## Art
Models come from Meshy (`tools/meshy_assets.py`, cached so nothing is paid for twice) and the snow ground from OpenAI images (`tools/openai_texture.py`, also skipped once it exists).

## Village upgrades
Three cash-only upgrade spaces sit around the plaza. Comfort opens once the camp is secure, Trade after the first house and Folk after the blacksmith, and later upgrades wait for Town Hall II and III: Warm Cloaks, Smokehouse, Hearth Stones and Granary (supplies last longer); Market Bell, Fair Prices, Tax Office and Merchant Guild (more income); Snow Boots, Medic Tent, Work Sleds, Watch Horn and Iron Boots (hero, workers and towers). Twin axes are on sale in the plaza for $12 from the start.

## Survival
- **Warmth:** every villager burns firewood. Sell logs at the firewood stall to keep the warmth meter up. Each meat sold feeds three times as long as a log warms. Firewood burns slowly in the camp and faster as the town grows. Blizzards start once you reach Town Hall II and make it burn 2.5× faster.
- **Food:** once the cookhouse is built, villagers also eat. Sell meat there. Plant a **Garden** (after the cookhouse) and veggies pile up beside it: fastest in summer, slowest in winter. Herds of yaks graze just outside the fort and across the valley, wolves drop 2 meat and yetis 8, and the fishery adds a steady supply.
- If either meter hits zero, villagers start dying. Lose them all and Frosthold falls.
- With both meters above half and free housing, new villagers arrive. Villagers pay taxes to the Town Hall pallet.

## Progression
| Tier | Goal | Unlocks |
|---|---|---|
| Camp (TH I) | Rebuild the ruined east and west palisade | Cookhouse, houses, watchtowers, blacksmith (Axe II, Pack 100), logger lodge |
| Town (TH II) | Wall in the larger town square (logs + stone, three gates) | Barracks and guards, hunter lodge, storehouse and quarry lodge, fishery, more houses and towers, Masonry, Arrows II, Axe III, Pack 200 |
| Citadel (TH III) | Raise the citadel wall (stone + gold) | Gold mine, miner camp, gold trader, treasury, carpenter, Guard drill, Arrows III, Axe IV, Pack 400 |

Finishing a new wall ring tears down the old one and clears the forest inside it, giving the town new ground. Town Hall upgrades need the current ring fully secured.

## Workers and defense
- **Loggers, hunters, stonecutters, miners** gather on their own and stack what they collect on a pile beside their lodge (the fishery makes its own fish pile). Stand on a pile to load your pack, then build with it or sell it. Piles hold 80, or 300 after the Warehouse. They use the nearest gate and walk around the walls.
- **Guards** hold the north gate and fight raiders nearby. **Watchtowers** shoot anything in range.
- **Raids** grow every wave, and yetis join from wave 4. Raiders chew through walls; broken sections show a cheaper rebuild pad. Your hero can be knocked out, which spills the pack on the ground.
- **Hero levels** come from gathering, building, selling and fighting, and add damage and health.
