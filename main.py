"""MapleLeaf 6.3 -- unified route-and-market-control engine for Kaggriculture.

New in 6.3: the backbone route is replaced with an original per-seat
blend of Kaito Fukami's and Syed Muhammad Gillani's real routes, not a
copy of either. Built by pooling both players' tune-split games together
(per seat) and taking the per-step majority-consensus action across the
combined pool -- the same majority-vote technique used for 6.2's
single-player route, applied to the union of two players' games instead
of one. Syed was investigated after checking self-consistency across
several other high-ranked players specifically to find a stronger
foundation than Kaito's own route (Kaito: 95-97.5%, Victor @ Tufa Labs:
100%, Syed: ~98%; Victor's route turned out perfect as P0 but lost every
game as P1, a net wash, while Syed's route beat bare-Kaito head-to-head
18/20, +19,487/game -- a real, load-bearing edge, not noise).

The hybrid differs from Kaito's own consensus route on only 24 of 719
steps per seat (99.4%/99.4% raw step-match, since Kaito contributed more
pooled games and dominates the vote almost everywhere) and from Syed's on
about 4% of steps (95.8%/96.1% match) -- yet its measured performance
tracks Syed's standalone route almost exactly, not Kaito's:
  - 75-game real-opponent replay set: 74/75 wins, +37,412/game (vs. 6.2's
    71/75; pure-Syed standalone measured 74/75, +37,422/game -- the
    hybrid is statistically indistinguishable from pure Syed here, not
    from Kaito).
  - Live benchmarks: 10/10 vs main_inspo(5.9, +18,434/game), 10/10 vs
    models/5_6.py (+18,939/game), 10/10 vs models/4_5.py (+15,192/game).
  - vs Kaito's own held-out real opponents: 20/23 wins.
  - vs Syed's own held-out real opponents: 16/16 wins.
  - The critical result -- this file vs the bare Kaito route (no
    overlays, the realistic proxy for the real Kaito's actual
    submission): 19/20 wins (95%), +20,052/game average. 6.2's identical
    test (Kaito's own route + this same overlay stack vs bare Kaito)
    scored only 10/20, +1,092/game -- so the handful of steps where the
    pooled vote picked Syed's action over Kaito's own appear to carry
    essentially all of Syed's real advantage forward, despite being a
    small minority of the route by raw step count.

Caveat carried over from 6.2, still true here: "bare Kaito route" is a
proxy assuming the real Kaito's live submission doesn't run anything
like this file's overlay stack. The more trustworthy signal is the two
real-recorded-opponent numbers above (74/75 and 20/23 and 16/16), which
all point the same direction independently of that proxy's assumption.

(6.2 note, superseded in 6.3 above): the backbone route was swapped from
6.1's v27 (a third-party public route, one coherent sequence shared by
both seats) to a majority-consensus reconstruction of Kaito Fukami's
(real #1 on the leaderboard) own route, built per-seat from his real
recorded games (P0/P1 differ, unlike v27). Majority-consensus
reconstruction -- taking the modal action at each of the 719 steps
across many of a player's real games -- is only valid when that player
is highly self-consistent; it was
tried first for THUNDER THUNDER and catastrophically failed (0/19 wins on
a held-out replay set) because THUNDER's self-consistency across games is
low, so per-step voting stitches together incoherent fragments of
genuinely different underlying strategies at different steps. Kaito's
self-consistency is 95-97.5% across both seats (checked before building
anything, exactly to avoid repeating the THUNDER mistake), so the same
technique works cleanly for him.

Validated with the same tune/held-out-split discipline as every fix
below (all overlays -- weed repair, price-floor guard, mirror-gated
premium-shift, fertilizer relay, opportunistic sell, terminal
liquidation -- kept unchanged from 6.1; only the backbone route
differs from 6.1's file):
  - 75-game real-opponent replay set (loss5.8/ + training data v3/):
    71/75 wins (vs. 72/75 for 6.1's v27 route -- statistically tied).
  - Live benchmarks (kaggle_environments==1.32.6, the real competition
    engine, not the locally-installed 1.32.4): 10/10 vs main_inspo
    (5.9, +26,200/game), 10/10 vs models/5_6.py (+32,213/game), 10/10 vs
    models/4_5.py (+14,924/game) -- larger margins than 6.1 on all three.
  - vs ShiviWhivi's (aka BlackPearls1) real recorded opponents, using
    their current/latest submission's games: 16/16 wins, +37,212/game.
  - vs Kaito's own held-out real opponents (games not used to build the
    route, kept separate from the tune split used to construct it):
    18/23 wins.
  - The critical honest result, run specifically to test whether this
    file can beat Kaito's *own* strategy (not just his real opponents):
    against the bare Kaito route with no overlays at all (the realistic
    proxy for "the real Kaito, who likely doesn't run anything like this
    file's overlay stack") -- 10/20 wins, +1,092/game average. Crosses
    the 1,000-coin average-margin bar but not the 95-100% win-rate bar;
    against a full "Kaito-clone" (his route plus this file's entire
    overlay stack, an unrealistically hard exact mirror) -- 0/20, the
    expected ceiling for two structurally identical strategies. This
    establishes overlay/timing tricks alone have a real ceiling against
    an identical or near-identical route; genuinely widening the edge
    over Kaito specifically requires either fixing a real inefficiency
    in his route (checked so far: feeding/watering discipline and
    fertilizer economy, both already clean, no exploitable gap found
    yet) or substituting a stronger backbone from a different highly
    self-consistent player (Victor @ Tufa Labs: 100% self-agreement,
    Syed Muhammad Gillani: ~98% -- both candidates, not yet built/tested
    head-to-head against Kaito's route as of this file).

New in 6.1, found by replaying real historical opponents (loss5.8/ +
training data v3/, all of THUNDER THUNDER's own recorded games) against
6.0 and bisecting the losses, exactly the same way 5.6-5.9 were tuned:

  1. `_price_floor_guard` was unconditionally stripping any SELL priced at
     the $1 floor. That's only a real trade when it frees a market-order
     slot (10/turn cap) for something else to use -- with room to spare it
     just forgoes a real $1/unit for nothing. Cost as much as -26,207 in a
     single real-opponent replay. Fixed to only strip at the order cap.
     Tried gating this further on the mirror detector below (only strip
     against a confirmed near-mirror, since that's where the freed slot
     reliably gets used) -- rejected: the early-checkpoint mirror check has
     a real false-positive rate (many real opponents share a similar
     strong opening through step 100 without running anything like our
     actual strategy), and being wrong here is expensive, unlike for
     `_premium_shift` below.
  2. `_premium_shift`'s clone-distance gate moved from a live per-step
     check to the checkpoint-locked `_mirror_state` (checkpoints at 40/70/
     100, well before `_PREEMPT_START`). A per-step check looks
     unconditional but was a false read: against a real near-mirror
     (main_inspo/5.9, same route family) structural distance stays ~0
     through step ~240 then drifts to 28-64 by step 280+ purely from each
     side's independently-triggered weed-repairs/shifts compounding --
     nothing to do with the opponent diverging. That would incorrectly
     "un-mirror" a genuine mirror mid-game. Small, safe improvement.
  3. The backbone route itself (previously two THUNDER THUNDER games, ep
     91385999/91471546) is replaced by a third-party public route
     (`model_score/25-27-strict-future-v27-midgame-meta-reset.ipynb`'s
     "v27", decompressed directly from its embedded artifact -- same
     technique as the 6.0 rewrite's port from kaggriculture-findings).
     v27 uses one coherent route for both seats. Measured on the same
     75-game real-opponent replay set used to find fixes 1-2: THUNDER's
     original two-game route reached 65/75 after fixes 1-2; swapping in
     v27 (keeping every one of this file's overlays, which v27 itself
     doesn't have at all -- it ships with only weed-repair and sell-slot
     reordering) reached 72/75. Tested three ways -- v27 on both seats,
     v27-P0/THUNDER-P1, and THUNDER-P0/v27-P1 -- all three landed at
     exactly 72/75; kept v27 on both seats as the simplest of the three
     tied options, matching its own source's design ("one coherent route
     for both seats"). Also improved every live-opponent benchmark: vs
     main_inspo(5.9) 7/10->9/10 (+6,120->+8,909/game), vs models/4_5.py
     10/10->10/10 (+8,246->+13,213/game), vs models/5_6.py 9/10->9/10
     (+14,269->+11,844/game, the one case with a modest per-game
     tradeoff despite the higher overall win count elsewhere).

Complete rewrite (version-mapleleaf-6.0), not an incremental patch of 5.9.
main_inspo.py (5.9) accreted its runtime overlays one A/B-tested fix at a
time across 5.0-5.9 (documented in its own docstring history) and ended up
with two near-duplicate state machines (premium preemption vs. fertilizer
relay) and a hand-picked fixed terminal-liquidation order. This rewrite keeps
every one of 5.9's validated *behaviors* -- nothing empirically tuned is
regressed -- but rebuilds the implementation around the routing/market logic
found by auditing all nine notebooks in model_score/, most importantly by
directly decompressing the embedded `main.py` inside
model_score/kaggriculture-findings-from-zero-to-top-meta.ipynb (a "v21.1
conditional Top-30 memory" agent, independently league-tested there at
176-0 / Bradley-Terry 2128 across a 12-agent, 1056-game round robin -- the
single most rigorously validated agent architecture found anywhere in
model_score/). Concretely, three pieces are ported/adapted from that source
and cross-checked against the other eight model_score notebooks (all of
which independently reimplement the identical market-price formula, which
also matches this file's own _MARKET_PARAMS -- strong convergent validation
that the constants below are the real engine's):

  1. Opponent-similarity metric -- `_public_route_signature` /
     `_signature_distance` replace 5.9's coarser `_public_signature` /
     `_clone_distance` (aggregate tile-type counts only) with a per-actor
     position-aware signature (each hand's (x, y), a popcount over unlocked
     quadrants, per-tile yield totals). This is used only where 5.9 already
     gated on clone distance; per 5.9's own hard-won finding (see its
     docstring "Retuned in 5.8" section: tightening this gate was net
     -negative under the real 1.32.6 engine, fully unconditional was the
     best result found), every gate threshold below stays at the same
     effectively-unconditional sentinel 5.9 shipped with. The finer metric
     changes nothing about *when* these mechanisms fire today; it only
     gives the still-present opponent-tile-reading fallback path (see next)
     a more precise signal if the gate is ever tightened again.
  2. `_opponent_exposure` generalizes 5.8's premium-only
     `_opponent_ready_premium` to every sellable item (still reading the
     opponent's public tile `yield_units`, never private state). It backs
     both the premium-preempt fallback (as in 5.8) and the new terminal-
     liquidation scoring (next item) -- one function, two call sites,
     instead of bespoke logic in each.
  3. Terminal liquidation now scores shed items by
     (1 + opponent_exposure) x glut_weight x price x log1p(quantity)
     instead of a fixed hand-picked priority tuple -- ported from that
     agent's `_terminal_market`. It still only *appends* extra SELLs beyond
     what the route already planned that step (5.9's safer incremental
     behavior, not the source notebook's full-overwrite), at the same
     706/708 soft/hard steps 5.9 tuned.

One deliberately NEW (not merely ported) piece, flagged here because it is
NOT yet A/B-validated the way everything above is:
  4. `_opportunistic_sell`'s fixed "50% of base price" threshold (5.9) is
     replaced by a reserve price that (a) ramps smoothly from the same 50%
     down to 15% between step 600 and the terminal-liquidation handoff at
     706 (5.9 had a hard, sudden switch), and (b) is discounted when the
     opponent's live tile counts show they can outproduce us of that item
     (a real, computable "this is about to be a glut, sell now" signal,
     the same intuition as the source notebook's `_opponent_scale`, without
     needing its precomputed self-play supply table, which we don't have
     for our own route). Same item set, same step window, same batch cap as
     5.9 -- only the threshold computation changed. Recommend an A/B pass
     (benchmark.py or a real held-out replay) before trusting this piece
     the way the rest of this file's behavior is trusted.

(6.0 note, superseded in 6.1 above): the two backbone routes were originally
kept unchanged from 5.9 on the reasoning that every _ACTIONS-style blob in
model_score/ is *someone else's* opaque compressed route with no
reconstructable generation process. That turned out to be wrong in one
case: 25-27-strict-future-v27-midgame-meta-reset.ipynb's embedded artifact
*does* decompress cleanly (same technique used to port kaggriculture-
findings' agent in the 6.0 rewrite above), which is how 6.1's route swap
became possible. kaggriculture-rank-your-agent.ipynb's tiered POLICY-driven
reference agents remain a benchmarking harness for *other* people's agents,
not a route-construction algorithm applicable here.

Retained unchanged from 5.9 because they are already the canonical,
convergently-validated implementation (identical code appears, sometimes
byte-for-byte, in nearly every model_score notebook): weed repair, the
price-impact SELL-slot ranking formula and demand-urgency weighting, the
price-floor guard, and opponent-type detection (heavy_animal / high_worker
by step-2 hired-hand count) -- the latter cross-checked against
model_score/kaggriculture-what-the-top-farms-do-a-live-meta.ipynb's live-
meta finding that the current top-ladder modal build runs ~11 hired hands,
confirming >=4 hands is squarely in the "normal" bucket and <=2 hands
correctly isolates the low-hire, animal-heavy archetype (COW x3 / SuperFarm)
that 5.9 built this detector for.
"""
import base64
import copy
import json
import math
import zlib


_ACTIONS_P0 = json.loads(zlib.decompress(base64.b85decode(
    "c-rk<%WhoP5&RdfXQ6qJBD15UaYUFF1&YkT5eUIR90UlQg_B*7e-A}+Ubm~OtNWZglw_?ure^Lv@6%mfUH$RDM}Pn2_uqc~{pe30kKUhu_;7SLIr_&h|N7g%@BeWB@wZ=o|L3p&x&Qp}=+*7dpWa_zy}5mTb2K?xy<MK)|985$n|wTadvU!y3O;=P`T4txpUyAufBpJub^lxQ=MQg}%lAi<#rhvUESGQY|NPVP^6K5u<aqGsrzRZV-TiN}*NuzUKi<CIdCR6lACFec4>u3Z*?f5F^v=&Vt=RAXhvntv_N`~QjdR?_ncK$oIPSIb-PQHY+lNMNKiPIZ{dB*bgZDgjQ+@WU+l$LLpYH$n=JxZnkp~aHski>}{Pl7($m|X4Z+@P|z31Qm!@HZ!kUQ`BVR!u5Yxcjmw^q(?me=0%U!Mm9^!NolF6$nwU%K<$r!TQ_8SGN@xNXx5Q)^$aeH_>}`h?o&Zl2~3h&++@@gJ^kp9UO^M>v80IByr89gfQU?X=Dxho<@4oO*T~TINp~kcRn_#-%ck>)(Rmc<ey!aohDa{8R0Dc6ht22G;$i)v$iZ^1S0BP)4Kk8hHGWc-+3B@M!Xc*Fm__USC~aE??h#`eAu}b8&g`*N0}>`y_Sy7p^VT4Dx{WEthI2cx%|uV04nrUhmzW6I9v!^#kMkPrm=;3;GFko_2Q1qdSNFMB`?j<ou_N6%wC3zWHzctV!)CGyag`SKlSinn6EWZinrqSZOFY|6$ve7W#JyZe#p&Gfd$jzqSuL4-*)CJW7=Y4(<KaBG~bo3a_>UTxh~}fK3bJ@deZ73~<;$=2;ewQZqz_XKY5u{#G3!@K8KJ<=f(q^4scFw|D351BTPVpFiAOpRZmmudjdpj4{?O!@-B{mtwE$@p&%F)+=-Ep6<+4YfmIsYyyDF@|CLJ8@6%wSi>XI>{bo0-==#4_<i&u?$H4QduB%nOd`TMV_#CSkhaUC^t^4uT>QI}ndzAxnh|2{g#jkmblKX2!v&y<jU0e(Emz<7hxB<!n_bZ4@scw!h@O7G`^)ZfTjP@+VX@7|e=fRcjwAhf^`2k<rEr0P!6es28FWaPIN+fmkXCV$hc33%oTmd`Th7lh3A)R@X`R&Z?YFT9ZlmA%7+#a@K-}}qt*lIl?vdMYs60zjD6G=wZ~y9EpWH7WjNzJ_?@*w0?|;!ocdC0z!|Q*RF%B9a2V^6}E?DfI#+FjM!SUP{0&*}9U@j1Hm~S`4r?y83>pRN+N>oQXK7>6sKs3&3AFQpgy)QRc(&LA=O*DLL4_L=RMGk;;CtPtB6KHY8RTQn|T4dd<kEsHe9QYwkVH!g`I?xO}C#W#bg9?hV4qo$R83(%#$sz0l=5B=kq>n>%0a5bzUn2a#ARvZo^cr~Jd3FatT1Y1-wox|&^a#=chJIBUcV@^WY!CYwyb!_%y}7=6AFKmnUu`|ftE<bWlNy}hn<SF^i|5TzY};A10lk{Ip|hSr==Bpb2ZwHxaxZlAoXuj>pG=&V?PCorHZTejyll^#0m&wb1*%+?HfB_C1#oVU7y>V$FAsZWN;i#?h?W9qW<?a_;m32l616yr9Ko5BU3#W7DqG_|6BweBLp&|`P4d&IKo5Ga>eF>;sSXl>^fur87|W&v=ASb<PB-k4Us+wl!=H}81k){A47Ff+?Ozt?P|2}xYJLXsTD&=9>!~xzc>O9gHS*f&N;pN}sePq4QBB?nSkJ-x;EG<V_5q+#nKcWRfNwk}Odf@W48XYvZ)EO89fu_mR_(k)!`OjOWsk&xafla&jrwcsK`nF2xlaX3ndC|k2-iM%Fgq-qq%U2VQoFZn&|^0S_nV795581*V@&u%Ha_}#OAs3D3-EUF8mUBx8OS>sEimn7pN>mB+l^pv9hshP(*(OJJ!8t;p)z;`F<^(3INza~xenD#w|OO3W_w@TF=|PvbzZl7es2a=xA<pw9ny1E_bKB@Dk)^x1+pg8C=O7FBTpC&2w7OQMZx_Y(@Mx^8hLRDUXL;A1lpQJda!2W&@Ac{J=orQ&M0K^^AyS|FpXVrIQOn#79DGAZ%He(Ibi<-lXd$xGxo0U94{Ugp9pQp&1A5I(!>kV77owZa1jC5&OZ&Phnq<XB`1~7esr;p&2T8|sd_qr(MOz+9!$;Q4Lu16u`MPtQ{iEVP=k5Qf^*z39$K|0cX^%%5E)Wl-6T2l6j#*x_S41XkDt5d1wuyf4qmoKSDFm}nPV4m!=HH#kq;oi>XH?Yi6t2WR^SRqMsv=J?#?hkZM64arA_m!b&2q-=)UYgeJM~#BG)iJ*DFku!LlW1d>t6gGgAbcpN&f|*MwS@+XY=%E)B5{urxw90>nNlNwS0>9tO-}WZ!HVmogGA+NNG^-T@3cvK~8Z6gC9N)rgj$nTJkE^W0|+mZ0HuCFO2xTmod+i6Pr25SKWayQ{NJ71DgzeKhlu`ejnVWj_L^p1gmcfHP9c*d$QJ8Sk}YM;=Cb5hHG$I5CGU(Xq3OG1?$>;hF90hI=W6(^&`42^@yH=VU{@AOgd_)P?8oXl7||3>xn<&|A|A>>0Ik4HQCI$hrkZ%3TfivR$)oouBXSSc{Eau||^xaJJ1&d3-~m?;vz0cDc=M1o=)>gWm$vI|AO?ys!{q-US665I}m{9bkGonLU7yRe_{c)4*;C(0V9WPih^E1aAY0|G*RqPX=Hgqt4R#8H_|l${F?v@UxL!?fb6|F)HI@3?`WfP2$Z$cskpKvw@g_N93eME#pj<C;R1um^BWS;?$*5DBMb*2JbL<ME;gcpk>o<gD{{pLQE`##FGRt0D(;}*a)!{#cNJF?qrpNw}tqXj2D6fbF&qE1Oj&{TK2m$cH*w@vjePe5_uea6ATo)@Wqj8T&>a3%Pk$3qp|yMkBflMZsnjB5Nn_I9P}%|(KO5=DKOZ$5Vd=Y)>>khpsZjp6F^M9CS}s77tC$xQ+;KM_CkS?n(jtI&a&SkQ@Rn(SmqMYlL08N*<WtJ2YOC??~#tsBmeS{fSv~N^#tEUzA^;gC^Vwwi7pyAsr*{X;Wmv>8fr=gOv|=xWKL_C3JRbDh6$h>tlTGpqm96w=#DQbSzrpkqKw@MBu01Mbq9634))ymFM!QY`Sr2ZXgT4Bty?>{xn+y?8dz6F0oIT+EKTtw*r-jKt}r9bOdL1ziB3m_0?lSO-bW(V5pQ?fu<ftcsd_e#fKu|wy;U2b5Y@`<21bl&)A@-|0Z-utud^ntAQV597QDqF3aZpFE_^1i!YC@8h_AR+Qj5vi`JBs;>k$!~I+O#=GeInYymIx9?ezqU?irg^$(}yI(6lH=zxc|0W6F9-X-Q&AKM3<7sYvb{+u!b<lr#5Vrn>KZdZ)--5{f<dH|#LD6qa6@0!h}aK(0A>`hY^beJ*bwO(Y1#Y1RM_lJ{X1D{D955kX6B^Sk|xs6~+Aj;m%bd)atpk25Wr3I_-hc_sOkc>IXuxK}|V!Sdzie?MWE6=5mR5wl-Uh^Bz(B_S5-LxgD;nG(1Dx?9l)3&}lXRb)!ck#&c;S-^ebj(K0{A+jql<u5C4S}R#&y;2VP5@oF=p{-=jJRU$bj4L{u`&Nj1O(={cPM=0XWyJS$Cf7HVv<s!Ar-o>0Hba?SiR|P_Ej}eCsi&arB$c>Ruk4wI6uMk;wn%7Z45Fv3h?&ibNHsU%#7;O5GF$~#`?}~;`;7>b-sii+^)P~qy9S4Rw)pCjPM$fDe&xt~q!a4f6p_?VhmSP32@fAO@<zaj-r?fbu$x+;qhXb$K!c>M#Duph;5^JZf!EEb%Z$mYvJN&ZG7{VB$R2LfM?%gFBZ$^82QdqqhZU`JQn5{$vy))IW`eDt6<%N9s<hu}IHh?~Iy#GMQPy0h4_zRH^G~w?3TkZXTBKGrv!!=kzSFy=41NlS6H>!?Y4z3|v7TV(3T`Zct(F4TMfJ=J5%Rxuo*?CweG~Mp``M@##>>en?vs(k-FK_zUyw7UCGL0ds(_Q-kYw-2GW(POavu*&pddRi0i+9MT~;7$Br~|4tLlqwG^2O5xn1-2vcSdM_f?!oT_a_3MdswcmUhN&;&~LLoMa>Yi9u2}2uto%Z0keFq}iPjyJSQyB1p>A+Kh_Ec<{a-fdFwwT@N<n-XTWcQfD}hV8`<<$plRL4+XCa;_nCKV;rpbPYiys;0>F+I`M<4`Gk8Ge3R@QLF`0x9<jToz$u<R099~9b2KFjh*-p)h*8RQV7zC4BY-$pZtCiOCL$EeJHzv~+6Yl(REbhZh>CX6ZUe)$eS>uc;{;wBUmLfG%~;u|C*KCK)>hJ)>MAJ}0&W}%oR^YQ9l~uoM^)q5_7F&GaI0y=&~c;3@>peEW#CF>slXs6H-?v;%I@N^&AjKMkTIkSxRg%VFsjL&lc^X2t*>A)v}`830B|&z@>sEH(?jl!>(fa7dnTM96Bq-+>1Lpz4Q>Be<i{%9#2_~wpcxs|hv~tQNFkN?0*7EDB8#MoREaC0AZD?)J0%Ze{W#Q^_Ek*>iUzhz{7bDU7#@I)NzSVxv8=mCqt>!l0hyX1K{lt88iCZo&L!_I!@*avtCm_^DT#@=?obm^7LCMar4T-`=VTF5>8T?oeYW#=OQ+nA1SJ^2#y_?}kS34VE_#XLDiF!W@=15YqtgXo_`WbS*3+*pWSZAH-}NYKE^R6f+lSr?J=wYYFQH~S{ME5gl(t|~MDBR%@bho7qTYBS7MviH2~Pf(5HZ&3Vex<`>rJK9P(8Ao5UbR4UbQG3&u&Y5ea!INrGZCCdBEC>VtAd4eM!~oHIgw)i{pWpga(ULyjloyP$vKd4zVLsK@VDa`%#dA7FS^BfsmnAbM+m~UO7yT*QC4A7_*@wOCzQ5p&gp7`H(p3S}_-j=!)6LVU2>e(rSn|XC^?2=Vv7cBC+W>wV4T#HO2h31a@{37Zwx%w(;PC>q@5wP<m81c8E|6IVKMvR7p9HboHmG=B(W<V6ljd^&C|ruDV=XWK4OBY=1#RgNZSMlQF>_2xdtV6N@#}*0U#b5W|`#?X|ZF#sj!k3XepnXL5jY-j+xop3+&V?uckHn~JL8MXkE=q_G<%!nF*7>DgCZ4e$WyR*RaroNmx5vo>4S+Vf+I3ATzNRN%a<md_`m3>1b0R^Lht%-5Nt0lpEMyFHYuyT}UY8ct{_wN;P<gkRT~qf91}zk8?!x}wwq>N+<Na-`^^urMY5dV(*;Xb0?s5!qyY%XdebOtGs+0k+CuF+1J|`gmFR5?Ms$(NOL|L8L+P2f;hTsUnvK>|hLpu%#YoLNdC|NMlCqjKnfmhpL*S&Xa90G;bY)9pAEpuO6{l$q{O^rE~j|HAbe7`F0Z<x*~eRTFhQY#Lg9!yy6&w)Pg7iVcVA>eA&i8<N*?^h<|1u(vs~EC%>N>PR+@;kPkoU=hcp_1J0`38)imDR~s^^TL@*VWgiAbqqtQTIPT8(uy=n>+?y~>i+qlGCzl9xNEZFh1sf_nk78D61d)pQm!-gAR&O6C2q+#kuLjgrgWu5;W;wvQ%=DH7|GYAPp5PBG@wmA97_=;gr+|r51+7NX>gTRON<c9g4D6!3h?l+K<nz;{RCkII>Zwq+g)v#QF%(N}2j{5XdrGgo%)Y6RhuHK98s<WlM>B$fkQGgt9__PIwmN3%FYZb>ObBvd;4d(5^@yP~))2xF&I3e#ZfcoaoE{)q%j$?VAh{%Fzm0YipCpv&ZdEg<72%YcbF9X<233qDmk4K9K`jadf-_;L^T{eRnj*ATT>pksRYr;0`)Yfo92I)lxtShL;z=&bJw{1!1+7VmIE=_80I*1!S1UF5ImP2?DbuVl1hAgiFGiy#==yVL&er97DU88$=Gz$zFvC|!MA1`jNX9+#YS*KpBncOl4W-N#2WD0L7^WUkpTj13L{6SyWx2Gv^|h4l&}}4xoDW3%s&|3#P{=f(T7tRqayXPJq#odtvRE>n9!Yu)CM}uJ7Br82YpR$dj8-nIi{{XgEVlO12U0r3YzVY-^7)SyMbFATNls*PHqmOgtIQT)Ad)tCO9j~#E7A$6I#rQXY5sMyhGyOb9H-j61kukTzYLhq(nu-yduDnBz&b4QO2ceY1SB;H>@H1hYg$I60rk!a>q<8)C#BMC4pxoOVo*Z*%F6;~6Z@0l-U%yJ1i2*f6`xZH?Vq>uh_NYJEX{<U7X~3i3NQ1oI(?;4;AL@gpd6Skl{PqZc3jkR86!lRFU`R`B^L9ply$b8%0yXl?dr_egy@lApgZ%#Y230pm9p9qk%fM9RHYX^V=|62XIy5r8n+~XxIMs^msjsVTIovR`vrzvnhvEITwP^gNX~V<MWN0iEkjYE7^LP+(v1QBxy9p{Zh+zrI%ao)t+(ie>LY4Xt3(s{(>B~`Mi8tGVz@oc@l+@?%dWB*EDYgBsOsyVRI$KYqSA|hIeV8RB-6%V$Y4t3+Kb*+)XLZR3Ya8dC?Xl`DC*s#fD*zqUPNVE1?*@jj+7HbQu2IbZqa7)b1Rk8zLmU~aH=E9zqZ;WQ;+Jx%88#re}*mL3_K5-<_WPu&^IZg7keOJ#U}Zr@axP9Bkje;V10oK31&c(mt47!V(y1l0(mCxiDu;NnQC*Qpf|hz<oW>?)LZ2PrNKQ-^nXNPK8IAM&cpRmo82X<ZChHQ<-X}rdw2@@Afm{S^A1MVFHY;T-4F8@_r4&g6Cv1q*dGYM&Dx28r*`lna^Mce{SC1LyXsdvxscmRPq321comsuY9U0$K7#G!@LVriUmr9?FW<z!8PobYm3Cr`HD1h#%6*dd6OggINm^xRXis6(FCi6;zx_ad`2wm(30l5!LJGr48){8)t1FRB$RAWIqEt$q4jQtQw5D0arYIf7eKn;+JM|==XkE;eaAAhPVQJRH4!jvWwA|{d5+tRRX;mA=XWd%fF<wdLKnmTISGO0JZ$91INjJAXNlnaiBOO4}4($gH%6qyzf4zLNrPA78)`bBbSkHx)`e;-^23>f1B|CY@Jq!cm0WeHvDPpb<O4S5b?liJec&;@1R}MW@%EM0+VTHh@j|vHh)zKu>OAr`<5Nj0k0ocxZy%W>OBme}^`kssVBDQeh0`P11VUL}h`EiB8Q3(Th5pCuS<Tpk-ec6KNybRbBl&Q+GKB>j+X>f6IGeurK&hqC-U{tiiqCmEt-e3A8pW3WaJ>Q2zY@`DuTD!MwrjF3_qF#V5jbP1RcnH>4PRnZ|(9Qd&qo%NsMm8Krlj4*LA9?CjsElY0CE=zn+A#&{8Y@Q@k<kiLJ#{9UUb<Qr*7nm?Qm!B?Y#LUE7ep;eyNDapiZqr4#I$WBq(12eD}(wiBtxxR0yXoGbpdpxwoikWmz>Ng<vAtltG3l(*09oS;TO++$Tg%=sxqjiBq`5kDg=>y#GnDB-dAP)f$_^Pz<gdJTLp<)ggjxGu0xjpNl=c;P5*e<MIvztB%T&UlM|n~=(WO1!gr$}057`Ax!r|WUK{Np>7pX8W5e{zM?7qbUSbjuF@iBIFJLC~q<h=BvRM9t%xXMQt#7UY$0e#I`7H7QH0%&%&^@8-KR}M$NDljP)nSKEJ5h^$$He-B7L8&?ANflsAix@1Vu>k<Za}&Jd|1AkGF56B(1<`dPGu`J-1=onaRu}>6VW|fEi5|Zd23y@kQv)L;R8p+14Yn{2J1uqs>FP+k`0PmGL=q=Srki`hY(rl;P46q{{f4&PrYRT%qE73MkL#LNr2cOKn*KNJ3d)Vnvk5jRx*}+{sRABFUMgJ!wTjb#?|ThqGWf;`^>J3n%or?U$K-i3Wgf;3{86zNJjZJXs1kAf^sqH6u*nwc>G=|!4?V4_Z3JIN>v8H(R;BByL!G%>ft1EQqbgIuyPUo1^j><D-b9<MtU;kNmf98B@Uw*ZR|KIo<cU!z#=LDbKOZTP9CX|(mTq;Qp6^<s7LL}1c;ab<dVpkP1uUIF#)a;()0qO%))r=JSEvwOv88hrQD&4fIX!hvi=x#jyzy5MFP(0faywH!GqXA$SHz(+!2%{c+~LvR*=W0@_RnKI4_ptqe;TOQq9D?F^>==3QCQgTSh$s&1hsoVLf3IEU_Aw=;PEa*S$VeY6&JZMOjzTT-KP~ETe=ihUnUt)Ul{~bQ-A9s`YWqk#G<uT9vLg7Cl$_Rz621unT;ta6$SOeMb9hCFG81XG}V}0L(q6rxPM>%N`oKlI~Ni#H<!UWHP-isf}nOvAl}NP!*F6T3CSSlfRNfz2&T?waot$eatXzv3Ih{Fey8B(n6?cn--)M`E+Hh1KE$9Z>eCO0HDlp#DY{BTA7b&?@Rbvjco~$*nx*uEEw<76$5G6AbzGyzipPRF27O)JIRIUrSK&6SI}6k_tj>8><6LPK%krXC|K>~=S*LigfCRmZ{enkB}z4jVmNl3C>>0y;e(p~Lhe(se4*441|;`nW9?7$)8#PjU;D2kPBOA)d807-!jk}0SXuLOoul5ID^aY6o~KQXm6#eL$4YFaYYZHcJjK$lG;MU1J|&upQ(eDjB}l*M^r^UVV}!Q!rAl%3j-GVO7&KCJv;&-1$yz~DVv&8M>aX;N`56C&Gn~ZQbNxtZ`9w#7kmpVw%|I#DuF9rov9epdDQv!SAv<9M#MN{ZU30~ksPAluuhO-jtD&c!d9B--<Xgz)3Yk;S$VR^EY7cfBPqt0O75vOe+=oh>LBihx#f(7xnQZVJ&O=u@!3agV8LNXAJCSvg&Wgg8a-qV2uhP0-;kgsAU$gb16><kdz4F*h{SacTBS{mDO7Z1z9HZsY$T0$~jl^(hzns~YHGBwpC94-C6L7k;ZoCg8;6f(=7qS)aj=v?1=Pyl9hZ1NgRke%4j>@Nz>c}zD%`+(OXhUn*k%y3i(*$@VgGwsI{Dn*N&{Q!NQ52Y*OCgJhCW^`daxz`50er#GV!0Y&q#RI;`^WTsh%-m_H6U99=5$~UplWtjHm6`(7iD45a@n1sh2TXVV6j_N5rlOv)NQR$&lE8sr3#iPFQf`cH|7^9B~Veb;)}`(dGX39$$)g^;^i?{iCM|kekiB{dU~enXiB=}u(miUVHZFE`vz5RZ{)Jjgmf4ds$kG=N8rDZpXbMC7_WdAluBUzj0i*^SsJ;7r;oy6YHeqDI~z~H9->N-s49a=!g*6UP(aCdFU=}EUNVFx00)7jAd0&nD8}hsLDhP$QhnGgF?FiihvBoksxQs3`jUqo4)UeG4Y&t%_GMf4)B;~9QnJ)Mp%v4ZEhR)fIWb0rhhpEG<Xy<VN2MZHn?%yIoWzhW%%v+Vcj*Y%wiF;XP4$Q>S9B{lB_$Zus}<85I+xg!-UgETT7=UAFQlx}UDyFp87G}9E|uNUK}-UiiMy8K^Q<aQ$Jn>OHC2hV)rbo?rC5-X(uu&>))XIJtB7n&<Y<w=NH4~Qgg(b?AAK!UfJC9fxK1}|lN1kL#L2fTUQiUtw^p)ENd=t76*=#T4yNe;39eBl4LPjB#v~p+DVoR~lp!+Wr*LT|PzO!TFk}7Dn-^=zV|B1lyo24aCkbr8+xI(KJt4ehd&{90Q^CqZ1^T+HtcsUcH7fMuQ30jC&6d)vNV8j!3P3<v96M8%r=bLO44)@GNm-1Ml>+NQqCg@#qJm<QG@G*k>Bo8r%mY^Bk^4)ja(*VinS95lPcawjv8z!lmHf@wuzI7D)v)x`2)?>f6uyLNqMrNCe1~}XG6`Hoi#W*nNN}?$>75d-n4{Kr0u|O+&Ijeb(sERdPPTGliLIKWspWSnNn<77(l&^Ol46x$SK}y3qKM2c0N1Qi<#TE^gBxx-3RGx0r@Sh2nw|`w92PEKYQhqkq02Rl(;(Vvps^4niAs}t=6)?7vfO((O-Mi2l+B3{UsB6QjQ%bXP3C6|L<LxRo%niBc_2-Z=kJXW8Zo?nn9X}k=?0B@6)>KjD_Bp=LmCg_ZBPMKO>m6ZE|pS<T+xg*Bp$YG44#^C+`DC#W;`skK6}9UPUT~_jgM$CiaLuKJvy4luD*{OA-M<u4az$!SQOQY49{vYh$t_WGE4olp}vR`NwHDe6OFPSsNf|Eg0gC6L8@s&V2z*T(y3b9coo{FN+?Z^9Fy(~2163WOJN*v*+;%&<U-Nk&>yE396EUfDFY>lmE%!Rc>`7zWaF=B&~wN>U4!r^ceO@y)?SE)pxnoY9#%TBNc91XBybDKhvBzbn*1rCw4S&zrMMf3W<e*{t;L${#Eb>T25ZdJ+kI>nb+D8^6nnL%XPwl^*uB!|2c2Wh{md7>`#)IyPon"
)))

_ACTIONS_P1 = json.loads(zlib.decompress(base64.b85decode(
    "c-rk<O>Z075&SPY^I(#aZ09E1+*nwxWyo@fjUgBdWP<>~=CH{v$bXM4i5zmey1KgG8%p;2v|O2-dEc+Qy1M$)e~<qD%kRJa`uowJJ{`S3`|#oDW_I+CU;g#Cf8YM$_Tz8A{Ql2h|8x8K)6uJsKYxCIb@}Gw>+7T0(faM`?DoI&<D1#1qqpZ*tE1q<m!F@#JOAnI;`Z0CFW0xfHGlr_cC~tcG&|n>!-v)C&F!CmT3uYeJDQ!0{`}B{lbf6W&Gx!+{`$v{?|0s^?a-&A_3Fd*U30b{9y-1Avu!K(`~P8eaWTC0C2r#qw{hXNaWjs4t$cTRb^Z3PQNt(O&WE4ww{!HKhi<CRe)aME;?3vV|GobBW!lJtN8i+2e{uGDwH;*khRrv>%;MhjZ~x)l^>)ae_x!Ls{_HjTU))<OXV<GM@A<FKf&se!0v?x54>m8|dG5oP*tm>#DSF({^upBI7YvUB+eV*I``qo*`~i_C(mwvf<;RBs2jdY=pg+#T!n4CsnZKRZ`Qy+uf7?^fjzi1*DFf0lf6};A=5g~|FdX+Cs6B32Z{t7Jo@a-*%W7cVZ(0qThpf&zE&^pVI<JBI4~fU^8w&R(Pk0@KEA92=#l`CN_2(Z}SJ&qk=YPFxroB&6w}0W<Ld_r#*xYidhJv?-4Gl&o+3d~U?Kwe}&0jw-zW?O=PoB_Ep!2k|Q|{e4>?ayG^EBr_ZLN^_<nhga>u1esN15@56u<f=dDe{j(Q-Qsmtv)%;QWVeS6b-bCAf|8&&@D}hy2Dq=sZkd@bM^B8aTH1Q;T57Ybw0j4sf9f!vLEW$m0v9%^BdZfy}ck9HnN63eVV%ko~PXLg1lzfXcVUALX~zt8VYk+XoEiqd$MRzB*gKT3ucJ`~_pIU529%-7m#n*W=?{l&x3h#y#Dcsn(uIuGkC!mE|i{zc*~-?6HPNq}i<+U%yTF1n~RlMcktU2KLO35ST=Sb;iD=Vj&I7qx8I?VJ`mN$;|Xj56uX%_QD7gY`Sdi!Qlc>#YT=mx0b8#`$PIXq|Gj9@_5Oa7(`FM-~DBGxvlX@kFeNg<3AT&G{=$tvU<<1{!+NWz+jSVq6|7DOdRk~5J;;y$zvB=YR<y}uPx`tm;~MB-nLHa`0#D)f!pYJK8Dw1I}rDLdn+pwqI={v94gO}6bh^K`P;v`Hz)V=J7c)!<~tN9-TOaoqdV0-rSbK@$QTC=kOQ(2VizoSPh(4|-Qaj^3jsNp2QU{1In1{k;#1org!LU|e<iA;9UsCT8z35IwGY--81BpMm3051Z4-?j+XL2dP>};5-3eEm#ROVhaTP^txfWSB>tm|GB?o>;Q<%mOj}9~gj|nO)^Pqxatb^A)E#qL<AvuIyz}$_{pY(BvE+9(&{!4@(7zD&{ja~x}JkRa`NDJu%#Ww0@fF40Qz|gNN<IW73gzaG;gBL>hpf^{S?}K$f?5n|(yu7@4IH|!2zD**zy?EXn#kQSA8_=tX8@lKjgx)+cb8zT3DfdFR&)F_E{mH~>86In3v5`@b;AMN>3`jOfEKudDv@xTCD}Zx*#1ME1eYx8+bGm7iM6?t@vnZk<cRya@m8iv0<Ot4^?9!Jyqp~&bGlL;2ImFX~-y}ax3iP1&sy<zpmg*o8NN@AakEv`*VE#Fy<8;Fw`IXf*KK$tj%rM=e#ZU{D*ZyUJ4wW4Hrsii5uf>})ww^kZj5n`BQzNgPu7pzrp4wM>6V>FMfb|@_53cByY99a^m07c33HZiy!sJm{$N-#+@J8ld)Nxo6Vb#t%G>jeiRQ5<58Hadb*r>n89@H|YocmOulu51xfpG1EN3+AiN&3=-DYbjM20eCbaKAbK^XN;3H^ziNWaFc+w*;ZVz5s6*uaQcGn1Q^r$pX`E_UW|5v)u^x;K=lJn`YQm=^0bz4wb<phygpM#Q6@@!gZ(?y3H%OGQ)js$EYQx)_L9T`Mn)j-Qr)|bV$!t-KUHrsicr$7s#4WlQ=*jjyz*DAY@_H76tcrOe-OuY2w8pcs<6b6KHD^>A{+fW3#AJ^kBI4oKeW+=P8s`U>dvLaPD2fEIQWK-jY^mbHM%wChPDvGxo0U94{Ugp9pQp?PRco(!>kV77owZa1jC5&OZ&Phnq<XB`1~7esr;p?QkgTsd_qr(MOz+9!$;g4Lu78u`MPtQ{iEVP=k5Qf^*z39$U4iH+h~15E)Wl-6T2l5LeXt_S5;rk6*gx1wtn94xYD0SDFm}g<}_S!=HH#kq;oi>XH?Yi6t2WR^SRqMsv=J?#?hkZM64arA^DMb&2q-=)UYgeJM~#BG)iJ*DFku(Xu6Hd>t6gGgAbcpN&f|*MwS@!-6g>mxkB}SQ?=l0b(DOBw0cb4+CZ~vTwGGOBo3lZBs9|?*IlJS&tny3L66CYD7!W%tNQ7dG0d@OVDt-l5#gTE&(#^#E@+hh)bNz-PPHq3TZy<KAL$+{W7WGvY&ucPu@RLz?mpzY!;~EO!wNUBM+0jh!M9=otVQwbnNV6Og0EzcxL;$;a*DNe9^&k0*9gQIoVJzh`_Kfb>aCtnpxT#gU0&|^wzWjdq%BY1BFl)vTi|<a#w@BY}c$?=jXdS)?#B<tkGlvoT0fXk8dpW9fZ!rF1NXjAm52<@LOPdN5ET~7ZxJSyP%*00!VMW158gRvj_08Dv-2l8rUrXS`X#wNv(s4;B6rBADBYn$pGwQ)LA+|qmigcIm12yem1hJegD-VMrC}A(IgY0NxWGIPiI&-TZkEWL{3`ND$ZniuwPDzS>sSCUbs{Wg<A>K;2j2!$lsC)v~2oq5C)V+h>3-ec#;4HAh78L8zGjWc+E-2ovd>3wh+IP@j`H5ZnuJuK;SM#%YJvpPTlqW@&N0bL>@=q1Ovq`d~u{2S8H_ia!beMXzc#m{UYGATREr&#M-Al2mK0gG!3&z3Jf+bMD5<9wU*c=C@UB&1Q3(2Ntrb21#?^aR9~5*y-;AJrn`}lv+TFXlx~DGmbnD<WB|%*_Lm#*fgTgzyQd@c$iF-!pr=86J;67TuMELA3XN!aqQ?!KRDLbxaGORb4K*bLre#|;F{d?51qILn!vxR`R_+tQ(I((dbjO#JEHH&%QO52B5~Dlsx`R5bgFQF?39$JozdqI)Ehqf2b!+D~w`|c~1M8|Nz#4Lfr74~T8?{N(6=tNFiQ`5-(dnpApxNxk`$)t(;_Yr5HvD>%s%P^EC?%iVTeT4iQLWr=V8oa<ou3F5@DyI~I&0DjLh(~+!CM@nph^wn!Y>6@7)7NM@fEj9YB4!GpK}><JtAULhjO5KCWs}FSFYZvy`EsvJz}#e+0zFYnil2gXJ46bOj$1}ElEu22Vp)W70G>L``g`<a^e2VT=$({+$b`agksPA4Lb}jg{4=fK$0~pkZTT}KA;e9AIsZE6A40bnl-?K<b7Dh%GynMM9@;({%(IGY7r#3<Eq)qUN&CY<4lXD!U2LrUP*o>9zP;E?p4r8uzb1s-%l83O;`$a#O&7-qA4JHNr;8|5MkOyro^qk?$-3dLUIpT6`2xqWZhwI7I2@qW8PPKi0leX`OAu%)=Jh`uatwnL|JP^Xe*gBj|Wf<<BHDaz7^tL6AB}V)2ES88S(v`$@L8-?LsN(sUcdL%}}OSB0G6fi%*G3>M3YDNhR*oD|@CPg)WzzEfSg;gXkeEVqvo)Qq4^`u`|wt3|E2GzApOIej~!9_vP+z-HqV!O@l+eIR5IAP98ate(lJ7q!a4f6p_?VhmSP32@fAO@<zaj-r?fbu$x+;qhXb$K!c>M#Duph;5^JZf!EEX%Z$mYvJN&ZG7{VB$R2LfM?%gFBZ$^82QdqqhZU`JQn5{$vy))IW`eDt6<%N9s<hu}IHh?~Iy#GMQPy0h4_zRH^G~w?3TkZXTBKGrv!!=kz85!58T=FuC!~hy((0`_Vm-mm72H??TP+2wi|UydBIJMRJVDAU`zGjH_p?zgjF*#D+$ST6yYE&lpO7=9CGL0ds(_Q-kYw-2GW(POavu*&pddRi0i+9MUDhCMBr~`ktLlqwG^2O5xn0ZlvcSdM_jQ~|T_a_3MdswcmUhN&;&~LLoMj{Zi9u2}2uto%Z0keFq}iPjyJSQyB1p>A+Kh_Ec<{a-fdFwwT@N<n-XTWcN@qAuV8`<<$plRL4+XCa;_nCKV;rpbPYiys;0>F+I`M<4`Gk8Ge3R@QLF`0x9<jToz$u<R099~9b2KFjh*-p)h*8RQV7zC4BY-$pZtCiOCL$EeJHzv~+6Yl(REbhZh>CX6ZUe(LyurGHaRM)muT5LTW~%Jd({F=VYb)u@b(NF~0XGf>E=$R&4&gSPqpI<2dkCa8xYaab=(y2Sd91RoGH|7`RA3O3o5IUZWq0w|X5RBr$QaTETuLWw7}ey?$y5x1)>p6?S~ini05}><d92v9=^^*V^=TykJrhol35)^ZbUV<{hPHn!@?#ZlVvrjT(2NY~!}Q=tq>##cfkUtnkwsEPs>GF05VKg@osx&KejI8{`>Lh`MFZO<{-stF3=hE8B<EF;Sk~RWQES<&fK1JhAe+-kjX>&P=aP3<;oz&-RZA_dl*B|_cc_Udi$-F*QV5^ebFv7j^o1iP{c`8;mQJ}J2}&@4jel%|AWa^zUGx&gRUnd0<&*A)N9V_Y;rq<cSYLc~A=A9p`L0J<b7@m?*go`D=*ceKe+f0y;jd1FqO=8@B67!5ho66w74^mwvET%mOmOm_Ld00Bhs6V)tT&ZXL-ojVLab8HdDWtDJi9IJ^)bV5mj)go<pFCiis5xG_9a!T*GR@JEsh6X5*jR0@oFK+L7e~;IK+-j1wClx?MFcdT3msh2SSEg&DD1_d*v`WUX$)dW6Xw%ERB@HhjwVT=0oDBYsFkBqAO+}hcyb?N~<B>oS6V6o}ZN*h{UGj)Mh3`))e#C64=>ETv$*5*v5kkt}C4$K<QE4*danO<d{5wP$lI&($$}$nzMGdfW;y*)^k*ixax9kkul{hvi$`O4JO72PR0a#AebddOf1$=+svNKK@4k}wAbDy7!TlDDLfLPp2-2qd0QfVcuHrbx+9{+VlJwN7q#l9lg4h82-h+Q<}bhMYJdkow_4Q1<#dBinYG!n)}9|zOt4iHp#tY+y?Q(mWuP!5u=>_wV7|^A4e*W7-0h)M-9=VF*Kk5hsjY$>ApE+<9Az?*{M|z>&^4tNP}jMEkRwGOg@q~c*Asj(Mmu09jL0VITfRHeWQtuq3b0iMi`nr$(8tTdm&hV2kA`v&3L*`PKM39#P8GQ{U<YF$ge~<z6Oz$wCK@whXC#)nI#kspb)Ia4p?T{V?D&=)eD#RcN{&#QEuGt!tT8fu%(t7^&=t`e)?)TLB6hB*<Q2ydq!vUG2;064;mbA#A`g&QMf@}Skd|zRIQjjB;nbXd3;FP~eqQa=I^e9jy<uilbhROqx`j}-UiD#6G>Thgf#dFc4}16L#JvgAw8-aJc5;b8hh)+3T(F_S^C)J8Mi8l(e_09~X7%=Qf`H;t^J+j{HTWGpVU`1&%S>-c@Xssr=L!D65|4|kPeIFKcnX*}RnTf8t$ywrqy!X`!N4xci+I@!PCh?PN_D3gp`Hq5TNsl?8$+?wc5sgBy{Gib%j}y9d5BG)pkXd#c{C#!2wBmT>CrwbWvgSB{_#x-hY3Lr4EzP=tsXIy#u`Ex!g+wm&rL0pi_-%nYgHYw1|*ln?1yMK@kv6N?p8H(S`kjEImc>zYf!~ha*1$u71W|YAb2SZbv{{TK~sb_itFESs>&o$dtYs@l%qlqJ2%tANj%9#xu+;8uAnt35r+x61OOIE^J=B$KBjm)EoGV&h5*(R`^99`1YLg)&Do}WFNHC9&U`zA0cQ9Li70x?4avAiUhQU7lqBJzvZ0i@;=rtmAH&om>T}p6kI2artSpySx4xFr9lDKVkn@3PU-d2!9txQTR7)^dUJi#ch13IlQWi_b(<4c*!K5V<+Jfe>Z%q|*gwe`nb<rF;lEv0O`anvDm<@q;PCoy!qUc$<C&`IS&L&#zcAeP*3`EifZ>1o+VnsS3Ri`SlD$T!c*3itGfa6q~mmvCC<d*^SSsE$je$Pyg09c1bUTK(3ih!ghf!(F4ZB5IFG@#x&VO{Bl<)l=a&B3Y>S`11^UwK}@Y+`>h+&f{ViXfLHzT$H#q5bn#?lCq+i=~<H^UNS*Na1DqRj02s3cMVj9w-N<OQj7Cot+f*T&4(-=1X%hPl?66D`lN6r!rAiT)R5+H6eN=80gMCaT*6!r&3lsBC^nLPO9{xXH3R%=8Vg%R^yfg5QhVNb#eI)q?N7}zF%O-rRh+b!PQj;hU8qwTNLUX(lQhkia~1LB;6R`pIbbR=>{n7pksCy*m}pEP<=#gYL#dLe;UG_W(2|7Acot+9M6R^v+OF1!NL%3gsQ&&NfiscB`Ur6m$P?CLNaX(hK!~}uD$4OMXh{|uYgGch9Z)|j-uW@3Me5=<3&`qRltsh;z&6`Bqh%`<`!)yKetjj?OVx<38y-u{A;UCGWDn~tep56^k>`>&cO4aX`T=p1bve-da(xrR&0__3ct>*Fw$OZ4AvK@kYENhdC8RvDdv7?C6H(0o@hqSo~bq`3VO5aPp%(eLA`Z8P#WCRME^$w=5t78>O9;mwZ%=M+P0+?TJD=3wTGvW4<d>TIqzU({o=Gf+x;+qaqkO)IuU}+$Nhl-+@hTb_<|DwEuKA?>)#eTu&aKxlM6XidV-Z4rmM)bPzxa{_7Q9+hv$0H`ud<Ddif^)&6w8Lsk9Sgtnp$_RPK|spMZ?zP0}hmLwgFNehH~){OvpP%M+*`C20A^2`LOGZKyTHt*%5iA%9S<h*BwaI%vpB(wb%wo1%0S_tlgR?bMTepmi}<!i5<EhoxB)JMd=k&~mG*N|2ONrd4eepLJ__$9N@~11WS<UVS{jc=P$zPP+c+lhnjKH_`zl?a+SUpuDGxv)8K!TPm&nWnCE1fz4cKsgFh#WYmR+SF)3b+`}+19st8+mLlf*s8mg0<<283h3876f923qr9AvR5mpFX`lyhASRGA5y##>)2(d;nAAs#_);lqcOaedvt?#**&teM~E&#uFANJVEnIBgeoRlzt7twakKz?JS)0ZuHZVQI-!eGL#378u`91CZUP}YdNdYt9Yk-(^Eg++mEJH5a3Nj|k%rFy;(huBC5NVIluk<1;T=i_<-x-^2deAW@1dP=msCIa2Ee>!Rk3u$D-aWpATsqm4fPKC;d)=&~|>Y^P}psulUWDyyyAk|Z6qUoipbzyBkT_xoTvcjfeWq3i<qO^;+F|9~rNkB~7MndY7Zm=?_-$F9fx+PFE|5z75S8Dq-XnD!WoKl`sqP}Wd4Q351%@%&~+=pC4Dy1reYD$vwY^FjG$wv$tK<a%})*l$Z`~uA9C9+kJs71&VhUq$F`JV*ksND4Thg~ERmq6laQ8YR6iHlw<tR#Fl3Igz=tDM_ih~>4_9+EC9;yN}=zkI~QrsyRm0TCk@)A9mlGEcg<ohyswFUYLM6V>|W8gN{qT9VHqA3(znQ3l-;%Kii7$W7$1pHv-o__R~C*mq2<KWNb?X7rK2bOHjbu_cz6lIRAM`_G5vt0_~ZmH~|jgws^ELc^_JmK0Y&Uo#Qi!_~r~L!P(RRSTK1trI?QL_AOg-Dt2r<gZH1_bS<-xFu8Rl$b@aa(M`mg$@p{Fz_F+So_pl2Ec4$m}o?@otFfN4Fc4#mbBxO#iR+zscR);$>%Td|MhYl1~IH)zF}OQo-ayvm%PvHx~R!rQSlW^8KYpRA<xjXH-Ti7UxRkage52!qfYU=sEx<(l@e@`(0pHmB%xGg035v+%do5G%d8$wA}0k+{sk)+(O<w1$gu)}vJ<2yQ=Vi6)K}s#n$gCNqv9!K6Adh)0x;K|)Z*lk8Y#V_Oe{rgVn97=S0+Hj1R$40#%#h?w2cXHm5`<v7-bg5W9KQ!reYet<1gh7RRruQ?U41ysB`22dnpodP6td^;tC$b4nj^5%;S!rB*DFg*SCT^HkIG=;l*XK93M>*?v-jL=8buTAW=|i>fAEw5oksu6AJ4IlVFL}xI`bPZn^IDp;AjQp()C`isrJ$>}DAyY%xUFzNC&t)uYoujaIFXV~&J_Fw?4ZwXx{A%D3`4DuG?#ON9&4x9Bt4Uuz+EL_1^B(FI`cF+H6Saa;A!(3NzbVkKs^2qKf|ZAooJ8;RvrM24!EY|z32M4$YX9O^A+HLYd-pXg(TX^Xv+RmMr#v6B`;MMGMUR^-!_u?}QEa=xX4c>;hk!x0NoX=r6WroAuWYc;kdL}EuCTCrffOIHk}WrO&cGX1t$vby|Q5$q%vqL;#x)L%hkwb@tO`LQ2_VgrG0=DlFGm!C6#W{SO`l77ea<S;cY+rmHKb_7%}sfG_~`ZKvt#qxzxM;MUYlZ~}M(GQoyynpS#jyTE0n&pkc<j0-_pu);pmg^k#=3I$lJ@h<nYOKW65II(2D_vvYkmM<rex+%ntMn<+RGjPjJ!?VwMW;{2l^Y|pr7u;Avv>5QTgIS~qN5$)yh_#zk`jyTBUOK;Kg`GYFPz~d)}HG}O3NoY3WPj&@@NK1sdiO1J&Tpy;!R=ml?&Mk8z8Qxqv)C|zC?XzLwuF4{ag(_^~`JC&LrPLE?3B$dPX+#Rabkk+jz2VBCg<PPU1dP;tUf07AR%}>d$0@=Wrgn$_Yj&(#=>Myx57XlXTV;wv-DM27Hy){R+>Wfc=`S7p;&x80wYBX6lC!V;xDFXjF<XhvOJ6k4BCWXl*2hL;K~-wyfbp$SYaBAen&ErFGMNm;e_#H5d>gBR+dVw3%jH=&9-HPy!95s&-M>QTa4d9XUq2c?88BZD<WU@(@yRngEYvP)UWDpSUy+O%-DiMS;n=60(SBqNp4oC)3p$z!wZHma7p)$^pf=e@x$pICErQ1F|(>P6yTis%B?pa|-5lQ5F_0m)#j!2wvm?7Q00iL0IQP-PQ{AOc4`Os$hxoLaKmtV}6lR0u?nYzNoB_7q5(x3`j>VULJFmn3Zhphk`1gr!Q3<O-Z*L))prv>;ed2-=NCvja(L*kPgE_6%5+#2>ciF^ZfV>;}!6NQVFb|5rGIKOCy)?^ieoWt?dkNXX6RjLsTgeRb?<qIBzNk3Ml#RrCEi?ONP({;2@9`L~$1c#W=mA(n<JCl(ntdEHQPe+K2J8yQ(iOu=<jR9ggy)z74nsboO~$_S7-HP^4t3WkM^aF<VNAdU9fn2oJ@+H_5w@eUC~-t~QCJc{zz8U6@N(Snkphu5BqmY?|s3Rj%k(a7s!rs#hzfH*_wsC%p|M^|c761zt#5rMs{LqB2f8S6nK)ql1_PI1_g*#phX7o{q6^e`~4|YwHOYa7wWtC8ZOAv8^dSyjBs}n8?v0fstN}4GDdY**^MOr~rvVg>jv3(k3Y$yoi%;S-hYql5eeKo01ARjcan=6CF&^{}WuJOd4`ng^fu(dQvozJ19eB#82VUOrQ>$nqkKJp*JtqlE>;`p?C+oVNVm-fVb~=w0c5#%l4K-FQnGhJ}S`HU1e3gysA;5ACC$s^=-D4W<{Faid39}bh8s@%1+X_L{P`@anh5N#TZ#BupT4|B%&iKC?-j>ISY_}te3z%U_~CezmzKHXY!lLcWn9;bD<u)8nsf%-<%DrH#%7jOHYm9t1Cs}OQ<I5x$n$(h?g&uz*V$}gPe~9H=B~)Dbb2KYJDeAVU6W{Q0^<OCe`R<D<_uNsyUikey5T&R`M-vgJ>uzRta`Bj-n)r$m{}e%{o;+r&cq#;ijWNg_d*5t1_qQ$?(Zx;o_AhERh+yT*EjGqOArR3qg{oG^uCq*YY9Dy@%6;^m9$woCxtHwS2_r?{T8Z{EUI904uK(U+*aoq$%?Jy%9nq#@7$Cc~2<api!>^#?x~J>xp?t<3YR)Dxj(fjuG3XQVNkPnz4q&!<LP~Q!|cxx6IOvhlSQ>4;bI6eC)RI5iLehXECEkNAuX#_i-a67XhF_d1nQSqFRyRSuF+;<)u<)sed-q7f~W9HfnpKQPu+$yhK4zR?RF(HBAVt@snISRf`+1LfcdcrOA<F(tW{TNP>7Ni~}zF$XAS9DEb@v<J5vfCyyXypaijUJPImrz^a05{S^&*9-D~sQ`L<U8_ijJAsT{mAMbh?#)Fqg6fn~VFp|J6Bp=4#W@+*-0HyWRjVZ<5NHhyNxo$01im5MH6fEqpt+#vMEb3q>eQ4{|^0ZFI?v+MA>KtqC7ryY#{{dMgPon"
)))

__version__ = "mapleleaf-6.3-kaito-syed-hybrid-route"

_PRICE_FLOOR = 1
_I0 = 10000  # equilibrium / soft-cap inventory shared by every market item
_DEMAND_ALPHA = 0.25

# (base_price, equilibrium_inventory, scale, below_func, below_target,
#  above_func, above_target). Unchanged from 5.9 -- independently
# reimplemented byte-for-byte (down to the curve-shape names) in every one
# of the nine model_score notebooks that touch the market model, the
# strongest possible cross-validation that these are the real engine's
# published constants rather than a locally-fit approximation.
_MARKET_PARAMS = {
    "WHEAT":       (25,  10000, 400, "sqrt",   0.8, "log",    0.2),
    "CARROT":      (35,  10000, 450, "log",    0.2, "sqrt",   0.7),
    "TOMATO":      (60,  10000, 200, "linear", 0.4, "sqrt",   0.6),
    "STRAWBERRY":  (120, 10000, 100, "sqrt",   0.7, "linear", 1.6),
    "MELON":       (250, 10000, 300, "log",    0.2, "sq",     3.6),
    "EGG":         (50,  10000, 332, "linear", 0.4, "log",    0.2),
    "MILK":        (160, 10000, 122, "sqrt",   0.6, "linear", 1.6),
    "WOOL":        (200, 10000, 105, "log",    0.2, "sq",     3.2),
    "FERTILIZER":  (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}
_SHOP_PRODUCTS = {
    "BAKERY":        ("EGG", "WHEAT"),
    "PIZZA_SHOP":    ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":   ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":    ("WOOL",),
    "ICE_CREAM_SHOP":("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":      ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET":("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
_SELLABLE = tuple(_MARKET_PARAMS)
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")
_PRODUCT_BY_ANIMAL = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}

# Terminal-liquidation glut weighting, ported from model_score/kaggriculture-
# findings-from-zero-to-top-meta.ipynb's embedded agent -- roughly tracks
# each item's `above_target` steepness in _MARKET_PARAMS (steeper curve =
# more valuable to sell before the opponent's matching output lands).
_GLUT_WEIGHT = {
    "STRAWBERRY": 2.0, "MELON": 3.6, "MILK": 2.0, "WOOL": 3.2,
    "EGG": 1.5, "TOMATO": 1.3, "CARROT": 1.0, "WHEAT": 1.0,
    "FERTILIZER": 1.0,
}

_CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
_ANIMALS = ("COW", "SHEEP", "GOOSE")
_STRUCTURE_KINDS = ("PASTURE", "COOP")
_QUADRANTS = ("NW", "NE", "SW", "SE")
_MAX_ACTORS = 13

# Official Kaggle competition configuration (rebalance regime).
_DEFAULT_CONFIGURATION = {
    "turnsPerDay": 24,
    "townShopSellInterval": 4,
    "townCenterSellInterval": 24,
}


# ===========================================================================
# Core obs/action helpers -- canonical across every model_score notebook.
# ===========================================================================

def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands":  [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _align_hands(action, obs):
    action   = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands    = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action


def _actions_for_seat(seat):
    return _ACTIONS_P1 if seat == 1 else _ACTIONS_P0


def _shed_access(size):
    half = size // 2
    return {
        (half - 1, half - 1), (half, half - 1),
        (half - 1, half),     (half, half),
    }


def _projected_shed(obs, action):
    """Shed contents after this step's DROP/PLACE actions land, capped at 100."""
    farm    = _farm(obs, _seat(obs))
    private = _get(obs, "private", {}) or {}
    projected = {
        key: max(0, int(value or 0))
        for key, value in dict(_get(private, "shed", {}) or {}).items()
    }
    inventories = list(_get(private, "inventories", []) or [])
    positions   = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles  = list(_get(farm, "tiles", []) or [])
    access = _shed_access(len(tiles) or 10)
    for index, unit_action in enumerate(unit_actions):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        inventory = {key: max(0, int(value or 0)) for key, value in dict(inventories[index] or {}).items()}
        if unit_action and unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action and unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = unit_action[1]
            tile = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if structure and isinstance(tile, dict) and tile.get("kind") == structure and not tile.get("animal"):
                continue
            try:
                requested = int(unit_action[2]) if len(unit_action) >= 3 else 1
            except (TypeError, ValueError):
                continue
            deposits = ((item, min(max(0, requested), inventory.get(item, 0))),)
        else:
            continue
        for item, quantity in deposits:
            room   = max(0, 100 - sum(projected.values()))
            amount = min(max(0, int(quantity or 0)), room)
            if amount:
                projected[item] = projected.get(item, 0) + amount
    return projected


# ===========================================================================
# Opponent similarity -- position-aware signature distance.
# Ported from model_score/kaggriculture-findings-from-zero-to-top-meta.ipynb's
# embedded `_public_route_signature` / `_signature_distance` (a finer
# generalization of 5.9's tile-count-only `_public_signature` /
# `_clone_distance`: it additionally tracks each actor's live (x, y)
# position and per-item yield totals, not just aggregate tile counts).
# Gate thresholds that consume this distance stay at 5.9's validated,
# effectively-unconditional sentinel -- see module docstring point 1.
# ===========================================================================

def _position(value):
    try:
        return (int(value[0]), int(value[1]))
    except (IndexError, TypeError, ValueError):
        return (-1, -1)


def _public_route_signature(farm):
    hands   = list(_get(farm, "hands", []) or [])
    unlocks = set(_get(farm, "unlocked_quadrants", []) or [])
    positions = [_position(_get(farm, "farmer", (-1, -1)))]
    positions.extend(_position(item) for item in hands)
    positions = (positions + [(-1, -1)] * _MAX_ACTORS)[:_MAX_ACTORS]
    counts = {key: 0 for key in (*_CROPS, *_ANIMALS, *_STRUCTURE_KINDS, "WEED")}
    yields = {key: 0 for key in (*_CROPS, *_ANIMALS)}
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            crop   = str(tile.get("crop", "")).upper()
            animal = str(tile.get("animal", "")).upper()
            kind   = str(tile.get("kind", "")).upper()
            if crop in counts:
                counts[crop] += 1
                yields[crop] += max(0, int(tile.get("yield_units", 0) or 0))
            if animal in counts:
                counts[animal] += 1
                yields[animal] += max(0, int(tile.get("yield_units", 0) or 0))
            if kind in _STRUCTURE_KINDS:
                counts[kind] += 1
            if kind == "WEED":
                counts["WEED"] += 1
    return {
        "workers": len(hands),
        "unlocks": sum(1 << index for index, name in enumerate(_QUADRANTS) if name in unlocks),
        "positions": [coordinate for point in positions for coordinate in point],
        "counts": [counts[key] for key in (*_CROPS, *_ANIMALS, *_STRUCTURE_KINDS, "WEED")],
        "yields": [yields[key] for key in (*_CROPS, *_ANIMALS)],
    }


def _signature_distance(left, right):
    total  = 12.0 * abs(int(left["workers"]) - int(right["workers"]))
    total += 7.0 * (int(left["unlocks"]) ^ int(right["unlocks"])).bit_count()
    left_positions, right_positions = list(left["positions"]), list(right["positions"])
    for actor in range(_MAX_ACTORS):
        offset = 2 * actor
        left_point  = left_positions[offset:offset + 2]
        right_point = right_positions[offset:offset + 2]
        if left_point == [-1, -1] and right_point == [-1, -1]:
            continue
        weight = 0.8 if actor == 0 else 0.25
        total += weight * sum(abs(a - b) for a, b in zip(left_point, right_point))
    left_counts, right_counts = list(left["counts"]), list(right["counts"])
    for index, (a, b) in enumerate(zip(left_counts, right_counts)):
        total += (0.25 if index == len(left_counts) - 1 else 3.0) * abs(a - b)
    total += 0.15 * sum(abs(a - b) for a, b in zip(left["yields"], right["yields"]))
    return total


def _clone_distance(obs):
    farms = list(_get(obs, "farms", []) or [])
    if len(farms) < 2:
        return 10**9
    return _signature_distance(_public_route_signature(farms[0]), _public_route_signature(farms[1]))


def _opponent_exposure(obs):
    """Harvestable-now units on the opponent's PUBLIC tiles, per sellable
    item. Generalizes 5.8's premium-only `_opponent_ready_premium` (farms
    are visible for both players every turn, including live `yield_units`);
    used as the premium-preempt fallback signal and to weight terminal-
    liquidation priority."""
    seat = _seat(obs)
    farm = _farm(obs, 1 - seat)
    exposure = {item: 0.0 for item in _SELLABLE}
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            yield_units = max(0.0, float(tile.get("yield_units", 0) or 0))
            crop = str(tile.get("crop", "")).upper()
            if crop in exposure and yield_units > 0:
                exposure[crop] += yield_units
            product = _PRODUCT_BY_ANIMAL.get(str(tile.get("animal", "")).upper())
            if product in exposure and yield_units > 0:
                exposure[product] += yield_units
    return exposure


# ===========================================================================
# Weed repair -- unchanged; identical implementation across every
# model_score notebook analyzed (DIG for one step on an unexpected WEED
# tile, replay the originally-intended action, then trust the bounded
# replay window before rejoining the route).
# ===========================================================================

_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _trace_actor_action(actions, step, actor):
    trace = actions[min(max(int(step), 0), len(actions) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, actions, step):
    action = _align_hands(action, obs)
    seat   = _seat(obs)
    game   = _WEED_STATE[seat]
    if step == 0 or step < game.get("last_step", -1):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm         = _farm(obs, seat)
    positions    = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active       = game["active"]

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - transaction["start"]
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(actions, step - 1, actor)
        else:
            active.pop(actor, None)

    for index, (position, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if index == 0 else index - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("BUILD_PASTURE", "PLANT"):
            continue
        tile = _tile_at(farm, position)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[index] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"]  = unit_actions[1:]
    return _align_hands(action, obs)


# ===========================================================================
# Opponent-type detection -- unchanged from 5.9. Cross-validated against
# model_score/kaggriculture-what-the-top-farms-do-a-live-meta.ipynb's live-
# meta snapshot (top-ladder modal build ~11 hired hands), confirming these
# thresholds already isolate the right archetypes.
# ===========================================================================

_OPPONENT_TYPE = {0: "unknown", 1: "unknown"}


def _detect_opponent_type(obs, step):
    if step != 2:
        return
    seat      = _seat(obs)
    opp_farm  = _farm(obs, 1 - seat)
    opp_hands = len(_get(opp_farm, "hands", []) or [])
    if opp_hands <= 2:
        _OPPONENT_TYPE[seat] = "heavy_animal"
    elif opp_hands >= 4:
        _OPPONENT_TYPE[seat] = "high_worker"
    else:
        _OPPONENT_TYPE[seat] = "standard"


# ===========================================================================
# Premium preemption + fertilizer relay -- two structurally distinct,
# independently-tuned mechanisms in 5.9 (per-step multi-horizon search vs.
# checkpoint-locked single lead), kept as two functions since unifying them
# would risk conflating separately-validated behaviors, but sharing state-
# reset and repay helpers to remove 5.9's literal code duplication.
# ===========================================================================

def _consume_due(market, item, remaining):
    """Reduce (never below 0) an existing SELL `item` order by up to
    `remaining` units; drop the order entirely if it hits 0."""
    out = []
    for raw in market:
        order = list(raw)
        if remaining > 0 and len(order) >= 3 and order[0] == "SELL" and order[1] == item:
            requested  = max(0, int(order[2]))
            reduction  = min(requested, remaining)
            requested -= reduction
            remaining -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        out.append(order)
    return out


def _reset_if_new_episode(state, step, empty_factory):
    if step == 0 or step < int(state.get("last_step", -1)):
        state = empty_factory()
    state["last_step"] = step
    return state


_PREEMPT_ENABLED             = True
_PREEMPT_FRACTION            = 2.0
_PREEMPT_MAX_BATCH           = 30
_PREEMPT_MIN_PRICE_RATIO     = 0.0
_PREEMPT_MIN_FUTURE_QUANTITY = 2
_PREEMPT_OPPONENT_READY_THRESHOLD = 4
_PREEMPT_START = 120
_PREEMPT_STOP  = 680

# Checkpoint-locked mirror gate (6.1): a per-step clone-distance check looks
# unconditional (5.8's own finding: tightening a *per-step* check was net-
# negative there) but is a false read -- measured against a real near-mirror
# opponent (main_inspo/5.9, same P0/P1 route family), distance stays ~0
# through step ~240 then rises to 28-64 by step 280+ purely from each side's
# independently-triggered weed-repairs/shifts compounding over hundreds of
# steps -- nothing to do with the opponent actually diverging. A per-step
# check would incorrectly "un-mirror" a genuine mirror mid-game. Checking
# only at early checkpoints (well before that drift accumulates, and before
# _PREEMPT_START so the decision is already made when premium_shift first
# needs it) avoids that failure mode. Validated: recovers most of a real-
# opponent regression (main.py's own P0/P1 route replayed against real
# THUNDER THUNDER opponents) with zero change against true near-mirrors.
_MIRROR_CHECKPOINTS   = (40, 70, 100)
_MIRROR_MAX_DISTANCE  = 20
_MIRROR_STATE = {
    0: {"last_step": -1, "checks": {}, "locked": None},
    1: {"last_step": -1, "checks": {}, "locked": None},
}


def _mirror_state(obs, step):
    seat  = _seat(obs)
    state = _reset_if_new_episode(
        _MIRROR_STATE[seat], step,
        lambda: {"last_step": step, "checks": {}, "locked": None},
    )
    _MIRROR_STATE[seat] = state
    if step in _MIRROR_CHECKPOINTS and step not in state["checks"]:
        state["checks"][step] = _clone_distance(obs) <= _MIRROR_MAX_DISTANCE
        if all(cp in state["checks"] for cp in _MIRROR_CHECKPOINTS):
            state["locked"] = all(state["checks"].values())
    return state


_SHIFT_STATE = {
    0: {"last_step": -1, "due_step": -1, "due": {}},
    1: {"last_step": -1, "due_step": -1, "due": {}},
}


def _shift_state(obs, step):
    seat = _seat(obs)
    _SHIFT_STATE[seat] = _reset_if_new_episode(
        _SHIFT_STATE[seat], step,
        lambda: {"last_step": step, "due_step": -1, "due": {}},
    )
    return _SHIFT_STATE[seat]


def _repay_premium_shift(obs, action, step):
    if not _PREEMPT_ENABLED:
        return action
    state = _shift_state(obs, step)
    if int(state.get("due_step", -1)) != step:
        if int(state.get("due_step", -1)) < step:
            state["due_step"], state["due"] = -1, {}
        return action
    action = _copy_action(action)
    market = list(action.get("market") or [])
    for item, quantity in dict(state.get("due") or {}).items():
        market = _consume_due(market, item, max(0, int(quantity)))
    action["market"]               = market
    state["due_step"], state["due"] = -1, {}
    return action


def _future_sells_at(step, horizon, seat, items):
    actions = _actions_for_seat(seat)
    if step + horizon >= len(actions):
        return {}
    result = {}
    for raw in (actions[step + horizon].get("market") or []):
        if len(raw) >= 3 and raw[0] == "SELL" and raw[1] in items:
            result[raw[1]] = result.get(raw[1], 0) + max(0, int(raw[2]))
    return result


def _premium_shift(obs, action, step):
    """3-then-2-then-1-turn-ahead premium preemption (unchanged mechanics
    from 5.9's `_preempt_shift`), gated on the checkpoint-locked mirror
    detector above instead of a live per-step clone-distance check."""
    mirror = _mirror_state(obs, step)
    if not _PREEMPT_ENABLED or not (_PREEMPT_START <= step < _PREEMPT_STOP):
        return action
    seat  = _seat(obs)
    state = _shift_state(obs, step)
    if state.get("due"):
        return action
    if mirror["locked"]:
        eligible_items = _PREMIUM
    else:
        opponent_ready = _opponent_exposure(obs)
        eligible_items = tuple(
            item for item in _PREMIUM
            if opponent_ready.get(item, 0) >= _PREEMPT_OPPONENT_READY_THRESHOLD
        )
    if not eligible_items:
        return action
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    remaining = _projected_shed(obs, action)
    for raw in market:
        if len(raw) >= 3 and raw[0] == "SELL":
            item = raw[1]
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - max(0, int(raw[2])))
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}

    for horizon in (3, 2, 1):
        future = _future_sells_at(step, horizon, seat, _PREMIUM)
        if not future:
            continue
        shifted         = {}
        trial_market    = list(market)
        trial_remaining = dict(remaining)
        for item in eligible_items:
            future_quantity = max(0, int(future.get(item, 0) or 0))
            if future_quantity < _PREEMPT_MIN_FUTURE_QUANTITY:
                continue
            base_price    = float(_MARKET_PARAMS[item][0])
            current_price = float(_get(prices, item, 0) or 0)
            if current_price <= _PRICE_FLOOR or current_price < base_price * _PREEMPT_MIN_PRICE_RATIO:
                continue
            target = min(
                max(0, int(trial_remaining.get(item, 0) or 0)),
                future_quantity,
                _PREEMPT_MAX_BATCH,
                max(1, int(round(future_quantity * _PREEMPT_FRACTION))),
            )
            if target <= 0 or len(trial_market) >= 10:
                continue
            trial_market.append(["SELL", item, target])
            trial_remaining[item] = max(0, int(trial_remaining.get(item, 0) or 0) - target)
            shifted[item] = target
        if shifted:
            action             = _copy_action(action)
            action["market"]   = trial_market[:10]
            state["due_step"]  = step + horizon
            state["due"]       = shifted
            return action
    return action


_RELAY_CHECKPOINTS  = (216, 240, 264)
# Effectively unconditional -- same rationale as _PREEMPT_MAX_CLONE_DISTANCE
# above; kept as a real checkpoint-lock structure (not just a bare flag) so
# it stays a meaningful dormant fallback if this gate is ever tightened.
_RELAY_DISTANCE_MAX = 9999
_RELAY_LEAD  = 3
_RELAY_START = 278
_RELAY_STOP  = 662
_RELAY_STATE = {
    0: {"last_step": -1, "checks": {}, "locked": False, "due_step": -1, "due": 0},
    1: {"last_step": -1, "checks": {}, "locked": False, "due_step": -1, "due": 0},
}


def _relay_state(obs, step):
    seat  = _seat(obs)
    state = _reset_if_new_episode(
        _RELAY_STATE[seat], step,
        lambda: {"last_step": step, "checks": {}, "locked": False, "due_step": -1, "due": 0},
    )
    _RELAY_STATE[seat] = state
    if step in _RELAY_CHECKPOINTS and step not in state["checks"]:
        state["checks"][step] = _clone_distance(obs) <= _RELAY_DISTANCE_MAX
        if all(cp in state["checks"] for cp in _RELAY_CHECKPOINTS):
            state["locked"] = all(state["checks"].values())
    return state


def _effective_relay_lead(seat):
    """6 steps vs. heavy-animal opponents (COW x3 / SuperFarm-low-hire) to
    pre-sell before their larger herd floods the fertilizer market; 3 vs.
    everyone else. Unchanged from 5.9."""
    if _OPPONENT_TYPE.get(seat) == "heavy_animal":
        return 6
    return _RELAY_LEAD


def _repay_fertilizer_relay(obs, action, step):
    state = _relay_state(obs, step)
    due_step = int(state.get("due_step", -1))
    if due_step != step:
        if 0 <= due_step < step:
            state["due_step"], state["due"] = -1, 0
        return action
    action = _copy_action(action)
    action["market"] = _consume_due(list(action.get("market") or []), "FERTILIZER", max(0, int(state.get("due", 0))))
    state["due_step"], state["due"] = -1, 0
    return action


def _fertilizer_relay(obs, action, step):
    """RC2-style fertilizer relay (unchanged behavior from 5.9): pre-sell
    FERTILIZER `_effective_relay_lead()` steps early once the checkpoint
    gate above locks in."""
    seat  = _seat(obs)
    state = _relay_state(obs, step)
    if not state.get("locked") or state.get("due") or not (_RELAY_START <= step <= _RELAY_STOP):
        return action
    lead        = _effective_relay_lead(seat)
    future_step = step + lead
    actions     = _actions_for_seat(seat)
    if future_step >= len(actions):
        return action
    target = sum(
        max(0, int(order[2]))
        for order in (actions[future_step].get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == "FERTILIZER"
    )
    if target <= 0:
        return action
    market = [list(o) for o in (action.get("market") or [])]
    if len(market) >= 10:
        return action
    shed      = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    available = max(0, int(_get(shed, "FERTILIZER", 0) or 0))
    for o in market:
        if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
            available = max(0, available - max(0, int(o[2])))
    quantity = min(target, available)
    if quantity <= 0:
        return action
    action            = _copy_action(action)
    market.append(["SELL", "FERTILIZER", quantity])
    action["market"]  = market[:10]
    state["due_step"] = step + lead
    state["due"]      = quantity
    return action


# ===========================================================================
# Sell-slot ranking by price impact + demand urgency, and the price-floor
# guard. Unchanged from 5.9 -- explicitly validated as the correct ranking
# key in model_score/kaggriculture-findings-from-zero-to-top-meta.ipynb's
# league test (impact-ranked 176-0; ranking by unit price or gross revenue
# at stake were both tested there and lost).
# ===========================================================================

def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear": return value
    if name == "sq":     return value * value
    if name == "sqrt":   return math.sqrt(value)
    if name == "log":    return math.log1p(value)
    if name == "log10":  return math.log10(1.0 + value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price     = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price     = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))


def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )


def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market            = _get(obs, "market", {}) or {}
    inventory         = _get(market, "inventory", {}) or {}
    prices            = _get(market, "prices", {}) or {}
    current_inventory = int(_get(inventory, item, _I0) or 0)
    current_quote     = float(_get(prices, item, _market_price(item, current_inventory)) or 0)
    later_quote       = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)


def _demand_per_day(obs, configuration, item):
    town          = _get(obs, "town", {}) or {}
    shops         = list(_get(town, "unlocked_shops", []) or [])
    turns_per_day = int(_get(configuration, "turnsPerDay", 24) or 24)
    shop_interval = max(1, int(_get(configuration, "townShopSellInterval", 4) or 4))
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
    if item != "FERTILIZER":
        center_interval = max(1, int(_get(configuration, "townCenterSellInterval", 24) or 24))
        demand += turns_per_day / center_interval
    return demand


def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    item     = str(order[1])
    quantity = max(0, int(order[2]))
    market   = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    current_inventory = int(_get(inventory, item, _I0) or 0)
    demand   = max(0.25, _demand_per_day(obs, configuration, item))
    excess   = max(0.0, current_inventory + quantity - _I0)
    urgency  = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + _DEMAND_ALPHA * urgency)


def _rank_sell_slots(obs, action, configuration):
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows   = [
        (_order_score(obs, configuration, order), -index, list(order))
        for index, order in enumerate(market)
        if _is_sell(order)
    ]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
    return action


def _price_floor_guard(obs, action, step):
    """Drop a SELL priced at the $1 floor -- but only when doing so actually
    frees a scarce market-order slot (the 10-orders-per-turn cap). A floor
    sale still nets $1/unit and never adds back to market inventory, so
    stripping it is a real trade *only* when something else could use that
    slot instead. Tried gating this further on the checkpoint-locked mirror
    detector (only strip when facing a confirmed near-mirror, since that's
    where later overlays reliably have something to shift into the freed
    slot) -- rejected: the early-checkpoint mirror check has a high false-
    positive rate (many real opponents share a similar strong opening
    through step 100 without running anything like our actual strategy),
    and unlike premium_shift, being wrong here is expensive (-26,207 in one
    real game). Measured net effect of the order-cap-only version above
    across the full validation suite: +6,120/+14,269/+8,246 per game vs
    main_inspo(5.9)/5_6/4_5 respectively, and 65/75 wins on a 75-game real-
    opponent replay set -- better than both the unconditional original and
    a full removal of this guard."""
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    market = list(action.get("market") or [])
    if len(market) < 10:
        return action
    out = []
    for order in market:
        if _is_sell(order):
            current_price = float(_get(prices, str(order[1]), 999) or 999)
            if current_price <= _PRICE_FLOOR:
                continue
        out.append(order)
    action["market"] = out
    return action


# ===========================================================================
# Opportunistic surplus sell -- same item set / step window / batch cap as
# 5.9, but the fixed "50% of base price" threshold is replaced by a reserve
# price: ramps 50%->15% of base price between step 600 and the terminal-
# liquidation handoff (5.9 had a hard switch instead of a ramp), discounted
# further when the opponent's live tile counts show they can outproduce us
# of that item (an oversupply race is worth selling into sooner). This
# piece is new, not ported verbatim -- see module docstring point 4.
# ===========================================================================

_OPP_SELL_ENABLED     = True
_OPP_SELL_START       = 50
_OPP_SELL_STOP        = 705
_OPP_SELL_BATCH_CAP   = 8
_OPP_SELL_ITEMS       = ("MILK", "WOOL", "STRAWBERRY", "MELON")
_OPP_SELL_BASE_FRACTION  = 0.5
_OPP_SELL_FLOOR_FRACTION = 0.15
_OPP_SELL_RAMP_START     = 600
_OPP_SELL_MIN_SUPPLY_FRACTION = 0.5

_SUPPLY_DRIVER = {
    "MILK": ("animal", "COW"),
    "WOOL": ("animal", "SHEEP"),
    "STRAWBERRY": ("crop", "STRAWBERRY"),
    "MELON": ("crop", "MELON"),
}


def _count_driver(farm, kind, name):
    total = 0
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            if kind == "animal":
                if str(tile.get("animal", "")).upper() == name:
                    total += 1
            elif tile.get("kind") == "PLANT" and str(tile.get("crop", "")).upper() == name:
                total += 1
    return total


def _opponent_supply_scale(obs, item):
    """Opponent's estimated remaining output of `item` relative to ours,
    from live public tile counts (herd size / crop tile count). >1 means
    they can outproduce us -- an oversupply race, not something worth
    holding out for a better price on."""
    driver = _SUPPLY_DRIVER.get(item)
    if driver is None:
        return 1.0
    seat  = _seat(obs)
    mine  = _count_driver(_farm(obs, seat), *driver)
    theirs = _count_driver(_farm(obs, 1 - seat), *driver)
    if mine <= 0:
        return 2.0 if theirs > 0 else 1.0
    return max(0.0, min(2.0, theirs / float(mine)))


def _threshold_fraction(step):
    if step <= _OPP_SELL_RAMP_START:
        return _OPP_SELL_BASE_FRACTION
    span = max(1, _OPP_SELL_STOP - _OPP_SELL_RAMP_START)
    t = min(1.0, (step - _OPP_SELL_RAMP_START) / span)
    return _OPP_SELL_BASE_FRACTION + t * (_OPP_SELL_FLOOR_FRACTION - _OPP_SELL_BASE_FRACTION)


def _reserve_price(obs, item, step):
    base           = float(_MARKET_PARAMS[item][0])
    fraction       = _threshold_fraction(step)
    supply_scale   = _opponent_supply_scale(obs, item)
    supply_discount = min(1.0, 1.0 / max(1.0, supply_scale))
    supply_discount = max(_OPP_SELL_MIN_SUPPLY_FRACTION, supply_discount)
    return base * fraction * supply_discount


def _opportunistic_sell(obs, action, step):
    """Sell shed surplus of pure-output products (MILK, WOOL, STRAWBERRY,
    MELON) that the route leaves unsold between scheduled sell steps.
    These are pure OUTPUT products -- selling them is always net-positive
    since they were produced for free and the route doesn't need them as
    inputs."""
    if not _OPP_SELL_ENABLED or not (_OPP_SELL_START <= step <= _OPP_SELL_STOP):
        return action
    action = _copy_action(action)
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    prices    = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    projected = _projected_shed(obs, action)

    planned_sells = {}
    for order in market:
        if _is_sell(order):
            item = str(order[1])
            planned_sells[item] = planned_sells.get(item, 0) + max(0, int(order[2]))

    for item in _OPP_SELL_ITEMS:
        if len(market) >= 10:
            break
        current_price = float(_get(prices, item, 0) or 0)
        threshold     = _reserve_price(obs, item, step)
        if current_price <= _PRICE_FLOOR or current_price < threshold:
            continue
        available = max(0, int(projected.get(item, 0) or 0))
        surplus   = max(0, available - planned_sells.get(item, 0))
        if surplus <= 0:
            continue
        market.append(["SELL", item, min(surplus, _OPP_SELL_BATCH_CAP)])

    action["market"] = market[:10]
    return action


# ===========================================================================
# Terminal liquidation -- same 706/708 soft/hard steps and same safe
# incremental-append behavior as 5.9 (only tops up beyond what the route
# already planned that step), but the priority order is now a live score
# (opponent exposure x glut weight x price x log(quantity)) instead of a
# fixed hand-picked tuple. Ported from model_score/kaggriculture-findings-
# from-zero-to-top-meta.ipynb's `_terminal_market` -- see module docstring
# point 3.
# ===========================================================================

_TERMINAL_SOFT_START = 706
_TERMINAL_HARD_START = 708


def _terminal_liquidation(obs, action, step):
    if step < _TERMINAL_SOFT_START:
        return action
    action  = _copy_action(action)
    shed    = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    prices  = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    exposure = _opponent_exposure(obs)
    planned = {item: 0 for item in _SELLABLE}
    for order in action.get("market", []):
        if _is_sell(order):
            planned[str(order[1])] += max(0, int(order[2]))
    full_dump = step >= _TERMINAL_HARD_START

    rows = []
    for item in _SELLABLE:
        available = max(0, int(_get(shed, item, 0) or 0))
        extra = available if full_dump else max(0, available - planned[item])
        if extra <= 0:
            continue
        score = (
            (1.0 + exposure.get(item, 0.0))
            * _GLUT_WEIGHT.get(item, 1.0)
            * max(1.0, float(_get(prices, item, 1) or 1))
            * math.log1p(extra)
        )
        rows.append((score, item, extra))
    rows.sort(key=lambda row: row[0], reverse=True)
    for _score, item, extra in rows:
        if len(action["market"]) >= 10:
            break
        action["market"].append(["SELL", item, extra])
    return action


# ===========================================================================
# Top-level agent.
# ===========================================================================

def agent(obs, configuration=None):
    try:
        seat    = _seat(obs)
        actions = _actions_for_seat(seat)
        step    = min(max(0, int(_get(obs, "step", 0) or 0)), len(actions) - 1)
        config  = configuration or _DEFAULT_CONFIGURATION
        _detect_opponent_type(obs, step)
        action  = _weed_repair_action(obs, _copy_action(actions[step]), actions, step)
        action  = _repay_premium_shift(obs, action, step)
        action  = _repay_fertilizer_relay(obs, action, step)
        action  = _price_floor_guard(obs, action, step)
        action  = _rank_sell_slots(obs, action, config)
        action  = _premium_shift(obs, action, step)
        action  = _fertilizer_relay(obs, action, step)
        action  = _opportunistic_sell(obs, action, step)
        action  = _terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands":  [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
