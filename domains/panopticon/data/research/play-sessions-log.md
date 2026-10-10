# Human play sessions: what went wrong in each (from the pod DB and git)

Compiled 2026-10-10 for devlog 0. Bot runs are not sessions. Source for each line is a task id (T), decision id (D) or commit.

## Session 1: 2026-09-11, evening (the first online 1v1, Ryan + one friend)

Build state going in: hell ring with the lava lake platforms Ryan laid that afternoon, the tower he hand-edited in Blender that evening, the shove added that day (F key, 2 m reach), prisoner2 model landing between 20:54 and 21:19, placeholder music (WRLD, Wangan). The Host panel showing a public IP to hand to a friend went in at 21:34 (9f3a5d04), i.e. right before they connected.

What went wrong (fixes commit between 21:30 and 00:04, so these are the night's bugs):
- The exported build had NO RIFLE and no spawn placement: the binary scene conversion dropped Player/Head/Rifle from match.tscn (aef39b53, 22:51).
- The client saw the host FACE-PLANTED: mirrored bodies carried no velocity or floor state, so remote avatars never left the death pose (1114dc55, 23:30). This is "face-plant mode".
- Runner powers did not replicate: shield, armor shell, camo, hologram drawn only on the owner's screen (87e2c0e6; T122 "Ryan 2026-09-11: that obviously all needs to be replicated").
- Client parity missing: no death screen or death camera on the client, no footsteps on the client, and the client pressing Play Again wiped its own match (64d5aec6).
- Finisher was host-only (a client reaching the portal could not fire, no rifle, no aim, no audio); kill beat host-only; misses not replicated; jump/slide/crouch/shove cues and ability cooldowns not replicated (T123, b0246fd1 00:03).
- Client got no ADS vignette or viewmodel hide (119d4666).
- UI did not fit the monitor: borderless fullscreen + canvas stretch added (e6d55af0, 22:42).
- Balance: the guard was far too strong in a human 1v1 (D73); candidates listed: powers on by default, longer reloads per turn, shove, more runner HP. Reload-per-turn grid added that night (1b951168).
- Lag in rounds (D69/D70, measured earlier that day on the PC): bot cover search scanning all 119 lava traps per sample, 22-47 ms per tick.
Shove was tuned four times across the evening (reach, speed, cooldown, left click).

## Session 2: 2026-10-04, afternoon/evening, play A (Ryan + one friend, 1v1, exported build 753/788)

- The host CRASHED entering a match from the hub on the exported Windows build (0xc0000005), found on builds 788-g1523981 and 753-g3a8223c; they played a NO-HUB build instead (T330). Cause: the hub's net link kept receiving intents after being detached. Fixed 20:57 (7362a7b8).
- The friend (client) drifted left/right when pushing forward/back (T328), and as guard had to aim far above the runner at 22 bullet drop while the host aimed normally (T331). One cause: the host rebuilt the client's aim by summing mouse deltas and ENet's throttle dropped packets. Fixed 21:02 (7d60fb14, build 794 "aim-fixed").
The record reads as two plays on Oct 4 because D221's open list (after "play session over") excludes these three; confirm with Ryan.

## Session 3: 2026-10-04, later, play B (same friend, build 794, hell and forest)

Ryan: "play session over. we need to fix all those things" (D221). All fixed between 21:22 and 21:36:
- First time at the portal nobody could win until Skip Phase (T329); skin sometimes red starting in the forest (T334). One cause: the match started before the chosen map was installed when the client had already acked (18ec4f52).
- Ryan shot him, he kept playing, Ryan's game started a new round with him as a bot (T335): disconnect timeout floor was 2 s, a 3 s hitch dropped him (18ec4f52: a hitch is not a disconnect).
- The client's powers showed for one frame then vanished and never showed on the host (T332): now run on the host, predicted by the owner (06042e6e).
- Through the portal the client landed on the spikes before the tower (T336); back in the hub the client was stuck in the centre tower and the host fell through the floor (T337): snapshots carried no scene id, collision not restored (65869d89).
- Mouse cursor vanished in the debug menu (T333): one owner for the mouse mode (89cc1da8).
Ordered the next morning: full netcode review against Quake 3 / Source (D222), merged 2026-10-05.

## No other human sessions are recorded. Everything else in `playtests` is BOT.
