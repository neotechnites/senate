# PANOPTICON netcode review — 2026-10-05

Reference design: Quake 3 / Source. Reviewed on branch `net-review` after merging
`net-view-angles` (1ada525). Paths are relative to the game repo. Risk is the risk
to a listen-server host + internet-client playtest if left as is.

Count: 13 MATCHES, 9 DEVIATES.

| # | Mechanism | Reference (Q3 / Source) | What we do (file:line) | Verdict | Known solution | Playtest risk |
|---|---|---|---|---|---|---|
| 1 | Transport and channels | UDP; unreliable sequenced packets for the per-tick streams, a reliable stream for rare commands | ENet; intent ch 1, snapshot ch 2, decoy motion ch 3 unreliable_ordered; lobby, rules and match events reliable ch 0 (`scripts/net/net_transport.gd:93`, `scripts/net/enet_transport.gd:51`) | MATCHES | — | — |
| 2 | Input commands up | usercmd every client frame, absolute view angles, unreliable, last N commands repeated (`cl_packetdup`) | Every tick, absolute yaw/pitch, last 2 intents per packet, client tick stamped (`scripts/net/player_net_link.gd:515`, `scripts/net/net_codec.gd:181`) | MATCHES | — | — |
| 3 | Server input consumption | Server runs each received usercmd once, in order, drops repeats; idle client gets a null think | Repeats refused by tick, one queued intent per tick, 4 deep, last command held 12 ticks then released (`scripts/net/remote_intent_source.gd:95`, `:127`) | MATCHES | — | — |
| 4 | Facing set by the server | `delta_angles` in playerState; client adds it to its own view | `view_base` in the snapshot, client rebases on reconcile (`scripts/player/player_controller.gd:641`, `scripts/net/player_net_link.gd:686`) | MATCHES | — | — |
| 5 | Snapshots down | Server-tick-stamped full state, delta-compressed against the last snapshot the client acked | Full state of every body at 30 Hz, server tick stamped, never delta'd, no client ack of snapshots (`scripts/net/net_replicator.gd:305`, `scripts/net/net_codec.gd:289`) | DEVIATES | Client acks newest snapshot tick in its usercmd header; server deltas against that baseline | Low: ~230 B at 8 bodies, bandwidth is not the bottleneck at 1v1–1v3 |
| 6 | Per-entity state | Health, weapon, powerups, event sequence bits in entity/playerState | Health, finisher, armed, power, cooldown, jump counter, slide/crouch in each body record (`scripts/net/player_net_link.gd:391`) | MATCHES | — | — |
| 7 | Scene / level epoch | `serverId` changes on every map load; stamped on gamestate and snapshots, echoed in every client packet; anything from another serverId is dropped | Snapshot carries a hash of the scene file path (same id every visit to the same scene); intents and decoy motion carry nothing (`scripts/net/net_match.gd:111`, `scripts/net/net_replicator.gd:444`, `scripts/net/player_net_link.gd:600`) | DEVIATES | One epoch counter the host bumps on every launch and hub return, published in the lobby state, stamped on snapshots, intents and decoy motion, checked on receipt | High: stale intents/snapshots across hub↔match is the class of bug the playtest hit |
| 8 | Level change ownership | Server changes the map; every client follows the server's gamestate, never its own button | Each UI scene changes scene on its own: multiplayer screen and hub on `match_launching`, result screen to the hub on a local button (`scripts/ui/multiplayer_screen.gd:302`, `scripts/hub/hub_lobby.gd:542`, `scripts/ui/match_result_screen.gd:270`). A client still on the result screen when the host launches has no listener and is stranded | DEVIATES | One session-level follower loads the scene the host's lobby state names, on every client, whatever scene it is in | High: host back to hub and starting the next map before the client clicks strands the client |
| 9 | Match/round/phase state | Configstrings: state every client converges to; a late client gets the whole gamestate | Match flow is a stream of reliable `_ev_*` one-shots replayed into `MatchController.net_*` (`scripts/net/net_match.gd:285`, `scripts/match/match_controller.gd:1313`). A client that binds after the start gets only "match started" and "round N, seat S" (`scripts/net/net_match.gd:504`): no removed/ghosted runners, finisher, scores or race-outs | DEVIATES | Host keeps the match state record and sends it whole to a late binder (gamestate baseline); events after that stay ordered on the same reliable channel | Medium-high: an internet client whose map load outlasts the 10 s launch wait plays a desynced round |
| 10 | Roster, rules, lobby phase | Configstrings / serverinfo, full state on change and to every new client | Whole roster+phase broadcast on every change, rules sent on change and to each joiner (`scripts/net/net_lobby.gd:865`, `:850`) | MATCHES | — | — |
| 11 | Hub vote | (state) | Whole vote state broadcast on change and to a joiner (`scripts/hub/hub_lobby.gd:455`) | MATCHES | — | — |
| 12 | Client prediction / reconciliation | Predict own player from own usercmds; on snapshot rewind to server state at the acked command and replay the rest | Same, with a 64-tick ring, smoothed view error, snap past 1 m (`scripts/net/player_net_link.gd:686`) | MATCHES | — | — |
| 13 | Predicted power | Owner predicts its own item/powerup use, server is authoritative | Owner predicts, authority's word taken once the changing intent is acked (`scripts/net/player_net_link.gd:452`, `:642`) | MATCHES | — | — |
| 14 | Remote entity interpolation | Draw remote entities in the past between two snapshots (`cl_interp`), bounded extrapolation | Playout clock behind newest snapshot, adaptive jitter buffer, 150 ms extrapolation cap (`scripts/net/net_replicator.gd:502`, `:527`, `:576`) | MATCHES | — | — |
| 15 | Lag compensation | Server rewinds other players' hitboxes to the time the shooter saw (command time − interp) before tracing the shot | None: a client's shot is traced against the bodies where they are on the host now (`scripts/net/net_match.gd:376`, `scripts/weapon/rifle.gd:837`, documented gap at `scripts/net/net_replicator.gd:61`) | DEVIATES | Client sends the tick it is drawing remote bodies at in each usercmd; server keeps a short per-tick history of every body and traces the shot against them moved back to that tick, then restores | High: a client guard misses runners it had dead to rights; error is runner speed × (RTT/2 + interp delay) |
| 16 | Own weapon fire feedback | Shooter predicts muzzle flash, sound and tracer locally; server decides hits | Client's trigger is off; its own shot is drawn only when the host's reliable `_ev_rifle_fired` returns, a round trip late (`scripts/match/match_controller.gd:3455`, `scripts/net/net_match.gd:589`) | DEVIATES | Predict the shot's presentation on the owning client, skip the echoed event for the shooter | Medium: shot feels late over the internet; no wrong outcome |
| 17 | One-shot game events | Entity events / reliable server commands | Reliable ordered `_ev_*` RPCs on ch 0 (`scripts/net/net_match.gd:418`) | MATCHES | — | — |
| 18 | Hologram (decoy) | An entity in the snapshot | Separate reliable spawn/despawn plus unreliable motion stream with its own spawn epoch (`scripts/net/net_replicator.gd:342`) | DEVIATES | Decoy as an entity record in the snapshot | Low: works, just a second mechanism |
| 19 | Connect | Challenge/connect with retries, then gamestate | ENet connect, 5 s wall-clock connect timeout, seat assigned on join, roster + rules sent (`scripts/net/net_session.gd:105`, `scripts/net/net_lobby.gd:557`) | MATCHES | — | — |
| 20 | Disconnect / timeout | Clean disconnect message; timeout 30–40 s; "connection interrupted" shown after ~1 s of silence | ENet disconnect; 8 s ENet timeout; host loss shown; no interrupted indicator; leaver's seat goes to a bot (`scripts/net/enet_transport.gd:232`, `scripts/net/net_lobby.gd:580`, `scripts/net/net_match.gd:519`) | DEVIATES | Long timeout (30 s) plus a client-side "connection interrupted" state after ~1 s without snapshots | Low-medium: a >8 s hitch still drops a player for good |
| 21 | Late join / reconnect | A (re)connecting client is a new client that receives the gamestate and spawns | Refused with a kick while the lobby is not gathering (`scripts/net/net_lobby.gd:568`); no reconnect | DEVIATES | Seat a returning player back into its bot-filled seat, send gamestate (row 9) and the scene (row 8) | Medium-high: a dropped internet client cannot get back in until the match ends |
| 22 | Sender identity / flood | Server derives the client from the address; rate limits | Seat derived from `get_remote_sender_id`, token bucket on lobby requests, packets-per-tick cap on intent (`scripts/net/net_lobby.gd:708`, `scripts/net/player_net_link.gd:600`) | MATCHES | — | — |

## Order of replacement (highest playtest risk first)

1. Rows 7 + 8: scene epoch on every unreliable packet, and one session-level scene follower.
2. Row 15: server-side lag compensation.
3. Row 9: gamestate baseline for a late binder.
4. Row 21: reconnect into a bot-filled seat (needs 1 and 3).
5. Row 16: predicted own fire.
6. Row 20: long timeout plus interrupted indicator.
7. Rows 5, 18: delta snapshots, decoy in the snapshot.

## Status after step 3 (branch `net-review`)

| Row | Replaced by | Commit | Proving run (host+client, 10% loss, 40–50 ms delay each way) |
|---|---|---|---|
| 7 | One lobby epoch on roster, snapshots, intents | c6d6ee4 | Client left on result screen while host relaunched: before, its old match took the new match's snapshots (bodies jumped to new spawns); after, epoch 0, refused |
| 8 | `NetLevel` loads the scene the lobby names per epoch | 4c78a41 | Same scenario: before, client stranded in the old match; after, client followed through 7 relaunches, bound and predicted each |
| 15 | Per-tick position history, rewind around hitscan trace and each round-flight step; trigger latched with its command | a38dafd | Client guard aiming at drawn runners: target traced 0.05–0.17 m from where client drew it; old trace point was 2.6–3.0 m away |
| 9 | Gamestate sent whole to a late binder | 202dc58 | Client bound 13 s late after finisher armed: before, never armed on client; after, armed on bind |

Not replaced: 21 (reconnect: needs mid-match seat reclaim and scene bind outside LAUNCHING), 16 (predicted own fire), 20 (timeout + interrupted indicator: needs a HUD element and strings), 5 (delta snapshots), 18 (decoy in snapshot).
