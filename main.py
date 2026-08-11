"""MapleLeaf 6.2 -- unified route-and-market-control engine for Kaggriculture.

New in 6.2: the backbone route is swapped again, from 6.1's v27 (a
third-party public route, one coherent sequence shared by both seats) to
a majority-consensus reconstruction of Kaito Fukami's (real #1 on the
leaderboard) own route, built per-seat from his real recorded games
(P0/P1 differ, unlike v27). Majority-consensus reconstruction -- taking
the modal action at each of the 719 steps across many of a player's real
games -- is only valid when that player is highly self-consistent; it was
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
    'c-rk<U2j|05&SQD=7UK}veh?PW@;gdWyn&A)DVmSO;MmoAJV=R{qL0}@$2sF?ChR%DOvGT7@55He4pLf+1bzkJ^1@CzyJ2@?+1VSeDLw~)2D;m$-zH<`Pbk6efNjEkH7u$`#*pE&)w(G2XAkF{_^qa^4-nZ^}*y|`F?SF_uuK^?d0>p`}3>CLGa=0&rd&`|8#nB_v^FE<=t=1pFh1{EIuAg4p;y1X|Z^B_vfD$7ndInCP#xmKQ`g$_V$01oo<|;{dn_n>n-aJeLh$&K3(58XZ_)^(_24Vw_>;dpB5Jvo420eHqLPyXKou;<G9nx50_Wh@9!J6`DEMq_|x5X4&L+FP4(GtZ_Y2?eYyMJ>zl9BMjkx)rr!FC)3e2Tkl7nn-~2j@JI}xShY#25A$Q*M!}j>I*X(|AXRVxGFRr}jpPdE+^za2dE~_4_Ub^+%$1kyQ8SGN@xJ}awQ)^$ac^ud_`h?o&uAk-)h&++@@t-bl9tRwZM>v80IByo79gfQUZMDuHho<>kpL%v2TINp~kcRn_#-%cktKWj*c<4awahvrv{8R0Dc6ht22G;$i)v$WV;<V!;P)4Kk8hH4Sc-*d`@L=+U*Fm__&Mq%57H8LAepp;xpI@B+^}d<*K1tpFg=-5ngFIk$%cU9$-WoPE7@cIZS9`bT1XVVF{lNJClkY!yMn8eh)7DOTaObd}Xxz->od2}8LgJIhH~+1lHK`qC#vfAr>f7X5Gw4Ul?XbBND-8wbKWw|wLjNwoZH#|zhABMcSN1{YVFH7XN2$`lp}n741Y2HH;njA43r*MzuxWujzF^v%0S+6;Jj=pSYKExrjP(fF->M@79*PI3d|Uicep|ijcJ91gz;HVF^QY^p)8*U6)z!~mF~-_uIQY>0QtWj-KFvkhdS$NM)2*3m?TO@yO#o0?zEbsj!#2(yYj{MO-KydB+jLI=zmHzTJvv}u&+G_+Nkmv@>`N*Z(q?&-p0{b3i+^`AGd<HoGeWGrFu(+xE?awWxByhKkps}J<?8$XkUkG-vkRI$UUDV|(bMmDf7xAbYkblpEVkMB&qWu_aiqVl-qWkU6fQ6@nB<x$gANH32Rsx6(kf2!(8ZRT^LW5(%lRoLL3g>=t&=*w`8M{zZS*@I!)vk~h<m=im6Zw6J#rfkm1ju`g;o0e@~`gI$^H7?7_Pbb4h2g0{tw&ePIXUdc>T{Z#z6z*fNX@=1&iI&*ivdYIG)-<Kn~^}%mqRY^X-QC)b<EreMi|}iRx&_hp@*6h{jp%gS8bl_vQLZdic<`iH48u0qZ!Z$R3dHge%Ts0xhn%ilVh#i>#aVF;(D_JwK!=Ok;>gdzyi#1Qq6aP(d-)!E2tEaj@->?87c#?ndZO`Zz=v5G8;ACBhF30%EvEuYm`iXLkUkg>-^q8+9{4k09+~=$DmoXNF9|_OOq^3n6^ayQ|BO!8#!J)y9*&yu5fkslf@pP9nLxc-|evww*;A(5s0XI_nvPUOh2$aOgHE_d?gtSuZyI$;4^dJl4Qs1EV0p%l5n(kZh7zpvqNgV@3s60O$6IA@CCVa=&M$bkit_XeoeZRzyMWe>}%4QH!I<5u7>Mr6)S0vNi5Afgvh6#M6S`BtMM`^q}{uK3$iV>L3wFZ}ZKMv203U{yC%Lbi*F`mDM#o{OJfxFx{fXPz#pV?qz`vl^pw~=4TME#hWv>o;s6^SFb`-Bd?vVgi{2b+E;oL)#ROk^&GqpuIPno9{?JaS+igX_{MX><WX420Gx~PM&@4Baaa;z)y_LKj2-w?_DCEUhj?MwsK3S@)H0`>`&6KmNv;HeaP5N!v%|tk`qG6dwL7~8J$7wyzdQf);7f%!#)Lm)<D;*)1fjvc0B;wskxGP^fxMH^0@H5x>A1wR?Fjb9k?H9+O|YxdGp5WPDuYK519nJ>^Bt<0>rl;fn^$sWHutq1qn4Cf=XKlX_j+J;i+^_8Aw5@hpE8c5l0t@EAZtR6;sAv>@`TZVkcCxS6x`o2t%Q80kr#*H^%$d0psh)y2WvJC&7w}xgUzkyj6x<qPob;=)7bTfbMFdf(XqC6mb5~f1NJ{KSvPMpWAFOT@#10eiO_~zPX<dUO}r3o;qaUd7ZGsn{L_GXxS6C-a#H#1M;Gf@4~Mdzs;3heeZ&dr!PFey(35}=+hQU!6&{8NHJHaNIL8g+p;dc)o9B4|ks;;PO_DQ@aYe0fKb>Fv__b?ZAY=sZ;B{+srOEK0Id%~@{F&Df`2Yf}E?M!ISduYd1+IW(H0P}7?hFIeMtlEN+BDBvmk7^_?#m9;mjZ<(at-5iy}~pZEL(EM*MZSIGexlZ*|_v_O{itLS<r>$(h&OqOCxk6K<uNEBufb5VZba#_RW@YDI?*cZR+Lv9l)R?>#@T|VMBmijc5s)dFYfh&wb`#2^vmUQtrmaB|wIq7_w~wafy?;y*k@eA<c*FM>8*}UnUh?_9JlW$@>QiI3uNuO#)S%@m@Q2<YAN-G2+&-6LZ)Q9Xq=iqYXkAp4qN$xR+8moptb>z+tF+PBzpFA~5VrU3mVEW|sEGpz%Hfy)~`Co>5EJKp~WctXoi|+|^(&+coRf`T6dSwb<AdYcyE^XVcu2$2S!E4nk*Qm)qP%kncn__$@HKCE%^i3kwnET~N>g0i?Ix0j8&u*#r1k6-Zh&4eXWxt%q{;q}IVm@HUY64@{x(WB~Rt>MWg~!AMl3oME2;KO5QAzW?eFqcT3mV3LW@B;G89r?Xi&Yls<mL{3`NBF<!av|o;iS>sSC-ndi>g<A>K;2j2!$lsC)v~2oq5C)V+h>3-ec#;4HAh78L8zGjWc+E-2ovd>3wh+IP@j`H5uD61ZK;SM#%YJ*tj@|WrvWN9eB9DV_f`MWezBp2it2H`$xuxTBG`9ckVG;1ztsK+>V(rtOgMI}#nub{<1qK@zqIPf5T1)H_lobqS0*J}iq)Zz1g1Ieys;^AZUMMh9)7?nOS@v6GN;kq8%Ul9_G63Z@`^ydZKu?M9J<t()<X`R+(9<Bkp5U9vSBBslg+{bI(ZdE#D!-O;xJ@IJhMJNA)3PlanbR7kf&%D(VFKs|EBA@uXd`eZy5mbq7MQ}XC}Vd5iP4>R-9g=~gB>^i8L;^&zdqI)Ehqf2b!+D~w`|c~1M8|Nz#4Lfr74~S8?{N(6=tNFiQ`5-(dnpApxNxk`$)t(;_Yr5w)yocRnO)TP)a_zw`wC4qFTA#z=$zzIzJIA;3>S|b=IU6gyN^tg10zCL6sWDg---l7)7NM@fEj9YB4!GpK}><JtAULhjO5KCWs}FSFYZ%y`EsvJz=vd+0%O%nil2gSKpX#Oj$1}ElEu22Vp)W70G>L``hi4a_0WaRQH|V+$u7cgksPA4Lb}jg{4=fK$0~pkZbmyKA;e9pUT@u6A40bnl-?K<b7Dh%GynMM9@-O|8939Y7r#3<Eq)qUN&CY<4lXD!U2LrUP*o>9zP;E?p4r8uzb1s-%l83NmvSW#O&7-qA4JHNr;8|5MkOyro^qk?w0hyLUIpT6`2xqWZhwI7I2@qW8PPKi0leX`OAu%)=Jh`uatwnL|JP=Xe*gBj|Wf<<BHDat`*{56AB}V)2ES88S(v`$@L8-?LsN(sUcdL%}}OSB0G6fi%*G3>M3YjNhR*oD|@CPg)WzzEfSg;gXl3UVrH`<Qq4^`u@laN3|E2GzApOIej~!9_xbj4-H+hmZG%HTJN)L7PM$cCe(A`3q!a4f6p_?V`;RoY2@mf#@<zaj-r?fbu$x+;qhXb$K!c>M#Duph;5^JZf!EEb%Z$mYvJN&ZG7{VB$R2LfM?%gFBZ$^82QdqqhZU`JQn5{$vy))IW`eDt6<%N9s<hu}IHh?~Iy#GMQPy0h4_zRH^G~w?3TkZXTBKGrv!%CPzBji`8T=FuC!~h)((0`_Vm-mm72H??TP+2wi|UydBIJMRJVDAU`zGjH_p?zgjF*#D+$ST6yX#iXpOG`ACGL0ds(_Q-kYw-2GW(POavu*&pddRi0i+9MU6vqhBr~|4s_KhvG^2O5xn1-2vcSdM_hp<&T_a_3MdswcmUhN=;&~LLoMa>Yi9u2}2uto%Z0mi<q}iPjyJSQyB1p>A+Kh_Ec<{a-fdFwwT@N<n-XTWcLT5ORV8`<<$plRL4+XCa;_nCKW9+T?PYiys;0>F+I`M<4`Gk8Ge3R@QLF`0x9<jToz$u<R099~9b2KFjh*-p)h*8RQV7zC4BY-$pZtCiOCL$EeJHzv~+6Yl(REbhZh>CX6ZUe)$d4qKY;{;wBUmLfG%~;u|$1j6eYb)tYb(NF~0XGf>&P&Ou4&gSPqpI<2dkCa8xYaab=(y2id91RoGH|7`RA3O38^g;^Wq0w|X5RBr$QaTETuLWw7}ey?$y5x1)>p6?S~ini05}><d92v9=^^*V^=TykJrhol35)^ZbUo0}hPHn!@?#ZlVvrjT(2NY~!}Q=tq>##cfkUtnkwsEPs>GF05VKg@osx&KejI8{`>Lh`MFZO<{-stF3=hECB<EF;Sk~QxQES<&fK1JhAe+-kjX>&P=aP39;oz&-RZA_dl*B|_cc_Udi$-F-QV5^ebFv7j^o=7XeX{j;OQ+n81SJ^2#y_?}kS34VE_#XLDiF!W@=3SDqtipc@O@=ytZ%-#kZE4)eA}a}xwNS`Y#(|n^knDmzl56U@K;AdQQCq{5xL{3!_U9TihARTSa5<&COG-eA!4l6!{Px?)|*PHp?YLFAy%p9ylPQ6p52!A`k3LjO#_dR@_@A$#qc^8`;w~FYb0Zq7RLiG2@Mvhc(oAZpiTe^9AZbNf*!Q;_M;#JEv~@M10h4L=IT3|y>gfwuSs{KF=j(WmPSh9LpwBE^C5B6wPG$5(G|0g!x{x`rPUB`&P;$3&(BH@L}Jr%YBLieYl``63GD17E-WYjY~#TN*Og8Wp!BG2>=2<Ca!ejTsFHFX>FQ5W%~`u!z+w>@>p7}MTy?p&$e8jL+5Uot1`}fhCu4#=5X_P!CKhX`t!7W=Aci$f+G}qUj0bS76ds9C&twnfye*MFJf*Wz-4W4ZHWgLFi&}N#Nn<xkglicD)01zy8sHw#trj(LIo+UBW^J~twdcna6KoYlsK9wyE}l+A87K@1tiGifn6EQO1AHSicY7#Rcaas)HJs2=YO5dz2*0i|N103{e|KLCbV;cN)OBtk<Vev+VPQ)A^#osx(GJ)NBeKc*mhX-<nPOLu0&JDRVs^X_^zpLrC9;UhqoLe`f=Gkn4}y1wQ$;Qf*ufYGVM{&Ggk*G^k;aVJ8Hr`C4plWtohRF1Xx=&oTfSunUp->Ak|We+OXv0_Ym7`E^X(=!bVc-rwV1t*h@C4cdBrgVsRdC4!nQ9%__B?G$O9x+5&z6Sq$S%SPJVx5I5o#FAs>Fy&#N6<2b@*6H_VKRt~O*+w-Cyfi#`mBMscewaNM2mVekH&xHn;%7Wo|WPA(DXkSzM03pP}E9>uKC2qG2pFH3>LtlmCO5Kug7UJa<L2EU^x%yNKpndvPF{&{8oJi#AW;&E~HF=$x~PXQCB3R;b%)z4jnlz?I~7}!O55ifhe$>*m@sqPdb)Kj5s3uCfqV<?u|4$e`%_mp0FnSE0s53%VJG|Yu8k7fh|AuF0PJ=$lbY<0}iKfEpBFd@i+fxp1K)gy+|SVIUyI1do{xv6Dxae9DcEvh5dfaH>x{U+K?e3DS6yH(AcR)kY(&aoQb8dNcsTq2xZ1+^#;2u_5d&L^wPXo}EEas36Ss*Dn~_to}FIV$w9b2B}h#FJc<dyJCe3R;sAaTt+H0AP_cuU2aAQ;NsaQl?p92w*+2UyMdg(DmogoUO|DQW%5h%(pWbV1}=dh@z+5kc@le)viWGNfIt98%mig4$P|fF-$$8K8H>6h@3pZ%5rIS>uV|9q1#9XIUk7jRqq1fp^#}nwFGnJ<!~rdNIk$OWwB&DJ(BbqOj<IbEodJ5)>JV^7_D4Z7tNs~S#0g252SR6*$`;w<ntdZik_8wlAOroY@*d}mzgcVKqPJO77DT}R-_YBb*dt((){aY4b8j>I8L>B38J4xei<;IrIAwZ_ssMNfOS~pm4?}*2uNxY*j<|1*0hXB1L~a<)|GBpPD-WO9IP6l#h`@rmDdH#CiW-8y%Scd2y#i{D?X<Z+COjQ0b^6NSegkxuM9$l6kg`vboxr8z{}zBo^oKiRNCOs*-=r?WsDGMzBC8(lvvEWQr6jWDidYJwW~8<6QW0gf$q!`r*XsTRLW{cL>BtZQI%fwjLA68oN<}eYTS|l;^qKfTwHztX{Aer?-v+yX*!f<aCMb|AvxFa7KJ*8v<yXsVvw3QNjC=g=N6A+x&ewi=$PFFw%%bUR3A~BS|ysmpElu6GlF1k5X0?pj;BJIS$37hU||S1LRDY?q>2UJ5|v*3%h|gmA(=J?Lk3eK*Ix9tqE^1fSHL6zLlMbfM^Wz{1(Xn`@ggeQDqu%Laip9el9J~ebBorKpIfP%_O0Z_gi{?+{<YO6nR-+gR!;m3`ZH_^XW)6zG*5^Pg1$)^z1RZ*D>lg|g<oe@7-=sy2I~t{NH7DMyyVJ-6mvhc638=gPc$QE&s3We1-;qzC)W?Kpx!bcC=KpuqW>cT^Esq4bsnyk+Uzz_ZQIfcE%!~2+QU=G2NC%(I5DKTM87z#&vrk|U)=eEpiYEfbI?P3RLt6mfIE4OYfGGx1Gg~l7sL+is$cEoLT)NO!AcI}Rb-l}g%B0{2)2{MbG>MNeb5lSd=vj>OzZ1Z+KDmNcrhm`_et7MK*sVWX_cL!J%v%fgj6*C_C5LK8B~uFw0z@)6o!*F)SBW}S0bB`Kd4qjsgyb$G-M%ZO|ytiQ96qIYD$N;>PbG*x|l2B!VH1K(yWOccr$otxz$xANJ=Twsy2$xy0yGxypqg;6uK#IZ_Y2?eYvxfu5WyjnwaNCI)J1d+7BF*_jGZ3ws^Fq(%N6vg#jH{&4rfwXjDN4U3h#YJ9)@G3<Ki<Fid7CVy+KL)dW`VG_q27t~B~r4n0-M!%q`og}|kc3JHkS(InJM5Ey_EYZUVV*v@Lb6Vu2f00hwbj*Iy!ws7GB@N4&BkDZ+PafQKA2?KZ$t>+BnH%2;r*@EZ14A>NusmifFsm1MSaB*=nMP5D5^5;lkRJ6jPK(?LUU-~4U+N@GN--knNqyr>cyR&Sjj?nXAy#QSr!J5DF5Ug*Ume)j}oA*ygO<^I8Y&ec4#VHj&^3<tN8POU_!cASYV+zzYR*ozpqZOoj>P$4fbhR$5?We1xTtQaYG^`9Sh+33(5jUn4X)FndY1>FhebNn92K8G=hFZ4-YUUs70_aL@p9U>2Ihj++b4t`#ZL7hoVWru^FP{65Ye=P3Wl&8?Ql8CJ2qO82K?6v=ugdxZ<CkB6`MgB73KF#ldBQMVhb;e-pd6K({^78TMB)-iJS~bQCq8k}YlW4B??yoYUUZdny9=?r*4jhTMMYf4hUu4&c-R!Z#3UeM1Y=rWz)a>z_qKCovHS&@)p(*>-&_NZOH@npS>yv~*gndjdqUZNfE>Az9QLEC!w#QztQPx@iS>Ie8pVu0@|R9PfHk(n5>pc0fO7x&uzWLRs?;)|5rJ@=%2sH&^~;jt3g~MlqPxFZSaitq*1BpTGq!cY2abpbil7?})`$F6iTPe78x*%>DxDIuC>AacA+pfH;S~n{0~TwaddmQqO$-x_NVfBm0I@-U8kUlFe6pA{AvtxeWGwmo1^&NYj>8~^70fq`tJCvE$?lT(nOzq(xhpEZVku)33^n8#n)W7;jPh&HPMNR-<zmz+eiyaz_`OnsEfSjVOOPa#stkam_hK1#^?aGs!%5_%pvk{r<s$kE_yIXqAW(LM^kmADtbqDT97Z$R*l|=mg>0gMMN|Ohx|Ld-JW?a2ca({xh)rxzkJ^<95HSJBC6O_kuoZ1%0$e4e=><lah4I*VO0ub#hVSr8xkD8JdrCWG{W0nsdB9$Z1f0_W)0Mb_2eE^YQv~z4BPdDmpyBmWkjJL-dp^84FP7t@Ny5ES&BVMhj}RmZN{yXcMm++}Xk<cRJz)|ou^N}?<J2wJz1~-92_`f}Sy$0q)|lNaql7Jn=-QXmv8Z}<8mQ5#^>NIRa1bV1m991xJy-cwK1U_63w)_?LHZVbM*C|i<c?@(Ogg#%%sr;36C!Sl9vZrm?o+J9tQJ9JGQBOSjc6mWyo$(B6_X8GSb*r0zmh|}<*cT)%>NU8%rI@Sce2VbDLZ!3La1ny7NiyVbY-jq*^iuWsbHP}pv-W@f>at>nU87jOZZxiZ3&UsfrnNs81K>*18LbHex^*nZI-Mqzf=S}$%W{p@FewD&{(bZ)p~yH2cg)2lE4XsT-=nM=_~6$AG+yciBb)s7>*q$N(Yl__@Ji0lKWIFUnq5i0m(htSZG$~)Bd&pI^rZFYnC?(lOK8#fC?*XUaoW0n{y?K_0aRQsj(7ML*!VAt#plneUhhG`jw`QuF|JOQ*o;6_bdhJ7o9#8S8j~ZmcCRe&fd|JZW)6{ijH=G^D0>@NJ=cSk5v7Y{xBcozi@_=SbMG?DJ`GqC=l}8$)g!4rP@{5^ek3(i#LVMS1x2HY=F3$j-qR>_!9M<4e?dF_H#A#)HAPjJCl41xm+Q0>KWO{S6%JFZsW<eiMWEFIf?sFi8Dy}TcDT`s6Uepp2K<QDkm7BNH=43@M0&jPSROY*itT381PkE_bWVi0`_aRUbI5)V5nCfo2ef{jCCYwqERV6R{z9;Hb%>%kz)i}8;Rl2emS!(YxofIN>(pOCg5~w-FP2Hz=e(hE@Ug-9la!t=jW!ULkTpLs@g?iN9EH<b>tZ7<_Q#cw4pWZ$bCq`X#zZwK_wMpe&*6VG*yg66a^;dLdYVbiK23VoJ?110ADb)SguAGDF+ne{xN+Y;>?kK4anAjIqg{ksG6OX%_*4HMOj$1Ty|$@A$XAoSnL*61Yw;Ebz3XcGet~Dse&cS3#kIqjrm1N2~^aq_@c5xUc53&G9VqfczMiKVpg)X9}22~o}Q>Wnv!lgtSwGT*aZ;4u0fUC8@VhrAsvQ=Dj2le5%@3U=lSs&#w*|jr4m>_BLWdfmPRh&>7#I%TH6`k&c+k4hp18{s>)!JaNbl76j1WrNwW%%mkgl^z(F7>h~h2?ig9{ZP_>?`R3A1=Or5IsVfgH>>Ps`MzT{ztgM6u%0r!B;zHZB&I>Z->lq@w*XvH*UO9@d=PK*)Zq1g8(c^9(pQK`t)CXqBPCo!Z8bLk4pT{^<GEd_{8Q$3=}72OI>NeM>vYQ^-1&L#Gww}GU-7U8tO3n{B~7j{5Y#!2UjOJ#R-5R(9B;;yCmJgdsnG4}0mO;uuTIpP9NDHf!pbRsaeHN}V5Dk2*bIa(wz(u=Vnq0cefM_&sSAW^6=uG3B0B*lXlaq=yT7ZgSEt(9z3QURxNNzQwsgDLudf@_pXLk_F3F^NY{iY9UgWr&RUDO{Qf)In1-%veA4=EYj_SRE`B?_f9VaRM9g_WhPtPY7?>-g4;0RIu_;fxhl4tK#KVjSBtv!_JMAlB!4}TX6|MH#t0VCMZuj391%8O)`?Q^dg%CR)0icLv$bor6XzXW&yyD)e)G#tB4`@7f$7DOnwjfZcLxjE!00(V^k{Dn{!|FMki}u>4^}0b)^V<35`TO)17$=@$zMYw~F#`kl~SFVpEDcrByMvtnUOW9I>3o$vvaRsEV9y<-~$oHMdgB=2TL|N}i-`5Dgr~n!v82QIs+f72yEj%raFhr&b}j;ijXogqC5-YcQwD$neQwnc{^eBas=pT*El&p{?Q>3pkP(G^t+hSMDLpy@!j0)N)OcoCx0~m3zckZ^mKbXAHyuSTUXWdQW*EO>yS$jSw0!yndL?dql|vjp`IIdY&s!Ps~Fa{o!p;;ZsdsjMy%f!iQYHj5Q=4wrs?mnsMB_WtL_<EVLSX!0%3FU$>2qXfcYaiW&7enzgRJj~gL5yq|{PofRxfXhnu+we&-jg-Us({@GApM2QsGsO^bHSr1h35(W8KHIE?GG$D+}Pjcy0EpEIDNmHedCP$75^#y|=$={_g4!G<iUomo_=x^wcQwt8AJc4k660*v%Ca9PJs{yk1S2XB(Xd+IJRX0j(H0S7rXb8%5yzgNc{hcETz)T;&NCLNzd>DS4CB?r11lD6WrWAK0(JbiXx|LV6otUw}*kJ9M>beijq7IhQhhnc*WUS*l^}1Km{GfBJxnJ4AxBmxdV@po'
)))

_ACTIONS_P1 = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<O>Z075&SPY^I(#aZ09E1+*nwxWyo@fjUgBdWP<>~=CH{v$bXM4i5zmey1KgG8%p;2v|O2-dEc+Qy1M$)e~<qD%kRJa`uowJJ{`S3`|#oDW_I+CU;g#Cf8YM$_Tz8A{Ql2h|8x8K)6uJsKYxCIb@}Gw>+7T0(faM`?DoI&<D1#1qqpZ*tE1q<m!F@#JOAnI;`Z0CFW0xfHGlr_cC~tcG&|n>!-v)C&F!CmT3uYeJDQ!0{`}B{lbf6W&Gx!+{`$v{?|0s^?a-&A_3Fd*U30b{9y-1Avu!K(`~P8eaWTC0C2r#qw{h;aar=ecR=&Hux_*1tsNs`s=fh9;+c|pALpRlDzxsH7@#gdG|6YImGHv9+qi^c1zc_on+72>%!{(b`W^wQNxBu|&dOPIKdw$p*fA*UFFYc|Cv+LEB_x#sq!2sQV0gub32b-7fJon*CY+OdW6g_TedSPnq3x>ymZKF@9eeU*Y{(#66X&?XL^5esRgYgI_&>!bv;o0G+%->Gy{BdZSzwN1K$Dw8ZlmTg&KWSVl^SJpf7>@f6)E+mixAC89&$GkZWi_zwH?4-vLsn-U7lASwo!7wqhs5Ld4TXD?C%g{AmG=7b;$rps`tuK~tLyWN^S|CT)7~ek+rMyap=OW=Y;L(!L&00ah6baPZ1!gF_MD)~=C2<Z-+%J`Cr{`n(0SU~DfjLi_7jbpd7AT|wpK`d^7!Vz^|NNRqs;h2ieG(`JZnb%Xt^DROR>^WaQ?%#D=qZz65Pi4=Vq9~Lw;i)bRH%!_;{2m4IJD1sYS5kH5FcM2e{CLVSr5w<naa5<_vJyK;~H%j#4v3g=cI>$o^IxA@EQ<K;_%wkMi5<RkwHNjRC{`KYzHsI$OV5U0wbB1!JsThNBPNFU4Nh<KtYEtykv8J>8k9)}BbN*bD%b<ttUcH*DkVv4%&a*{vF1zfJc9@cZaR+@k{q_RNkDm_&qi#=fLtAq~r;^t_>AF8<xg%=AnT%?Ppf!Uz*=x@_&i;Q~;_Mvg$YmaFgkL;5_V%`Ry2c*&U<L{Gop{bhH#t?@~Zu-InfKNnpz$C3WBde5%@Qn<jtV3KR13_2uC9Pm&ONUJ!>V;5U$&cgw(E$7FW1l{G{wodB!@NMjY+vs;bhSy{}5chn0D=QPCd*n78D$kM>3aj+_+rPRuC-?I^W4Pw#I}|A0`#)}@JJmg<@%6vR7zYiI1F{if7c6#9V@s*s;CO5c0XdilFc%0p%(oljQ`;ki^&Mq@C90zxAHp6RAR1@257t%~?#u0!bpN4k6OA9+1J-d+kpm#z30IuO1X^5i6-8^g7FjpzW2(R<2YyIXn8px~4m1Og2`Vh}pn_togV#JQ<6zezIfPxn+>Owm^l^wTAWHuJON1X71jKNSUIPz2&+Y(73+V*KHtJ@89zi<5(61}w&J3A^?O`8-7ee@;H&>VMgLOdctHG1Jyu5fgslf@pO(MCyc-|bvww*;A(5s0Xy672%-aIjLaOgHE_d>VN*)BHy$;4?H9&2E+kx`J~WqaNXNH$3<Q01z$F{6SjfOC7q5O@iFx!W^yx@nX|v=l(ID54;DKVIUMsKrs_2+or1(w91;vNi5AgCQz8#M6S`BtK0G^q}{uK3$iV>L3wFZ}ZKMsccGM{yC%Lbi*F`mDM#q{OJhHFx{fXPz#pV{$+s<l^pw~=4TME#hWv>o;s6^H?KldBd?vVgi{2b+E;oL)#ROk^&GqpuIQC&9{?JaS+igX_{MX><WX420Gx~PM&@4Baaa;z)y_LKj2-w?_DCEVhj?MwsK3S@)H0`>`&6KmNv;HeaP5Ofv%|tk`qG6dwR^h;J$7qwzd8T&=u3q+#)Lm)<D;*)1fjvc0B;wskxGP^fxNTH0@H5x>9oYN-3a#J$n<oZX4qBf8B^vCmBAy30XwF|`3}{>b*L7)%`3Sw!+mYXs3oP=dEM^$y&YKH;$Pf!NY7Q>r;H=1q>y13$eK`-I6xteJYzH<WMS171^0JMD<Pk0;>96&J;taLXloMb!J3U@v#3+_V7T?1QOM-yDU?-U8oS<b?p?twI@Z?Sl2&MQ!2Sm&>+m)+_O9<7FCG@32yMviWUz$N#0$|D4$s+e5dqiEKMkmdn@I{KCza2Bbg_=@a474kdOCs8N1TuzOwI8PJqrl2EhaKk;bDkSgL%w?bKEc<TeYV*d7cLl8B$)|BsudCSJe9U)A_}ZU%KW6LMHGIp0`F<nhgJiV;6D5pLq?D4<Nwmk`<4MB^d)&;0j1abIywH&M-i2wD(`7P0OrxiSVrGzU)AKDNslv*DyZUD@>EovL$DH9T?3sQv{ozjY}`rgj$xvf-WqVhS&#K8lf8jVjq<xSwavG17<O@Z?=p}83`9{Q!lsg00tddj~zA&8v^8NL`%@jL#L#9?lT8V&~UnvayK?E0W$2wkZlu)OPtKz)!C*BX+G>ent4h6GO6IQpMX<O-ak^nnJ8s!7O3J(_u8o=50kuz5w}jAn8QGH?CfGpHV9pKX8XF~UP|G7(ZO>9hoSB{*-$Ttz_2fM;rTn7S=t+e#`_HP*0ch9My*`~g-{l<Zb6Z9SA)H5*Q{IT=es-BVq;gV(PROfp}8rKZ!Gj3gwDh+x4DfV--&AQTVQ%ez+0Oa79z~Mpr8W+NN>9XOiw4X2k@~fkhE$V*ewBC59R7ft%Hf+Z6NU<m_p&n0PJJbSvo(Xk*G*H!#)9iHnOXI|J5NzWqgd$Bom=YyjciOXIMB}h#7c9PFmC|&SZJ8Urvcx<4`GHxKs*-TM5+Q9R`oc-;xQmZ2D~w29!pKiG`4Ok^lxEu;~RGA(o<e%}K|dta9+S5WkY~LU3Siw}OvA;4VeWes{)B-Sz$Q0PCAX9!K8<1H~?UaikhoYjpH-OULDC?Ec&RBH*)IIj9B1+NV7S{R(h24YNoJ3^p!A?cSobme?gID;O*U5R<P-nKbGJb6fgUUzwu4P++8{yOEHy?6=62ZiF+IxdilN0Lp9jmmBbb9uwcYrz7;pzdR(Mr$Kx@!8ehw48b=Fjc9qI#|@lRel6v2n?@)NH6;V4Wm`5er!`Ck1<(P*1kepu?i0b$Cg4tV$Cs2WFoj=H#_j|XqdV`qgF38(JvaUdu=y#!KGqs7C;YH=Yv(q%Y|&l=>#8Wg8ghoEDV_xzwMo+zW~7;k<3>Kw>8Mbk+3d#qNW?ng?QR=3{CbnBXY&XsC7;||wGj$Yt=w*4#F#dnp9mH36khN;Ytjlr@l$ERTO6XGN)6+}F9lW@MWqw*6}L)iF*!S*a~X0yB4SgAa-ex8h$WC$uHLD=o?y{EVzVmQ(+3!u7Uk$?Uzu-ASuZIqNlfVnVLl`k$$ew{+uf6L;r`29_nlwdC^DCXV$b~zI}9#`rB|jvk~J%kYYv`1pb&2#%iBj22|{t2HNb=9eOSfH+D&*w&{Es}Zhs?c5hS?ds@cn4HeT7|OpB(%0fIzcNq!|BKO#BqRnSPVe7X7GPZ(xRSPFE+?AH^bDIj`Dh=uwPVcJEe#I3*X*7U(bat~P*nG$nk-C=GPaG$ti-dB2v><Ucz%Zi)UO4eAfl!LxRS!+dTE15Ho2T%>;iq7V~72;kK3L}Zrr;$(@@%^01^$jKMLMiE~AzGTvP^MQRJ9$!zPl-wDDQG)MCGONKd!`|UE|;7w5}Fx<=pid&VY4Dq%}qG5GtPqySAo^OF8b7dBf_Nj<?e9Zjo|T3gG0VJ{_2uW9yyVI?Z|wj6YAR(k<?Fzk2JRl4<9!2M!<;P;o{b?n_8ixVU?vogQTs*gtsc-Jj^+P*UhBMjLE994mK<@65Hy?9&Xb|Le2~$h}JL%F$<fA6|Hkpu}zt?lVHDQf~}wxUSHs<wBKnsrFl|1I*V&j)?B6!T_A+>PqP3DYHaFSq*gVvrFUJv7dK5A{1gr+q=xCz>a96qJ;BZu+*krzEd{KL>X{cJ<bUZrLCP!pCg@xDvr#RKmy=c8CnJfw?^Z3JkTazv?sxF2fRo*jWbel^`;-839}i5RAUiMtqzh$T)*x&oGq@hB>WghOqj$BrUCZ{ez{TA6b(~0DBV}?$=H$PYcE)bvc@(6aWh4EGK~gpdOYT%`>qE$-*_{!)WJE0@NXpdOjEcs1@V*~`0C7iM4>sf8Ax7UyXE;t^$MY@81Wfu51+NR@?+4^#9IW_H41TfT4V%0=@q?-PgnJfzlk6Qq>_l@OvAd?gDV{w5Rd7RdG$jj&Sj3))QOb2-yk~zSfH+rf>gs+bA{5Iz!}GS<2vKBIiBd?2igwX%1H(1E!McKR0xylPO<Tlfs_fI#Z-ZECE9uO2m6QqrHx30ZOUbDY;WnM4s_|@l2&6T*)ih%0xY1L2tg@~$aHX<TU=Wj=!plx&ck$R}-t$q&7}5n?N+)a>)#T2}R1AUESFjjbHj`ZdI2ufOtk|^aA@|1hX(azW6Hbr`i~-?vJJ8UEwtp=0V-;><kQ)!sj120-^x#OOkji_3L$DE%MN&no#FbDGvsl}ml83Q=9BNGas-^=)1KTD3rB)OS55U$W=T(td*4@2PYuT%SOwEuWo6|{+K<Z%Ul6P0(;H%hGOD(RH#6(<osEH_xMq;~C2%p$<vIwd4g(D{Ya_8@sPPrcmN-%(pe{6#wO&+mb^b*BYAd*exlkSE`=f{BI`^?Z-Uwm~T)4bOCu18sOX;X37KJ-@T$u8Z02{qH<uTF%bv;~_Ya>rALpMR4T^~Mvi-~^dWaPpr*#8|6`#RHzKH<eOD^~iEUtWwW;)uM1byDjbYF~e_{1|A{h0c$Uc;dL(dB~`1}NX9HJjt5>68Z1)rY9Yu$od6U##Ewh_J!s|aM?nT!T!EbjLWWw+)ps;|<uEy3lkP@i%!Z0Ajg-QNc4)TdL*l4w#at+&D`p>uH455Ft0CT;nE)l8pOqYl#HQoaW+p_|6!X^-*x5;3SWp1i#)Av4E1e!d=~3O-Awn_am^^?`CFMNQ)t{o8vv#+D#Ue7+b5xDE>T+$7G370?{RIsTCdLR(#sqsHm?cR}EY?ul%%03a3~QRS*WM-=58zrUJQAUv$pOlFTOxgUN@u0IBcjD(E~<tXwd$sm#%|F+;|Qe5D)?%v0UiL|YEcuH(+xUh)@I9EdwxtY!B$a(3Y?eq>hVOBfx?i$>RXF}`8snnz&Ap3w}(=77g+&a!wD^=whD59@ar0Ll*vT$cMr8d*OXd7UFQZujud?q7N*2sPw>SU?SP#yBAcvl`R+)QDR%WJz*ZS7X2<(LA1@1EB8#Xz8p=H=h%_kvAb4juRpiou9gKkxw$uYnNJh7rXv~P6kyz&HP*s!Ed9n?L=B;C}<6Cy{)gx9bIYMo=bZ%d=#>n(B-)>?<S43}Ei`nal*tw#TR~$o-S`bAbZ2K~VFWVT1JV0U<@z3l-TCyGD<o6fGqdol=^5JLwyxOUCz*%*B!_27YYC|S<3!!Yi>cgOD6t~I($KClJ_U_M#dlRN<k<YR0<Pw1n$)ex6U_*uHQOpXBAW|{^vJ^PX>h0qM0mY-{)quKc@H=|KEC)E3nckA%pI7G36a0ZC9v4@if|kYb6fkkBpw&cL{oFN32`DCmfnAgr@v;}3e14jg>P|62Jr&BfFeZyOhGMDh;2hO^PwADH**6vP5Su<h!(7PnXhtv)vZ5)|qkUG&R>v&;<C_u=6M`HV_zTQiJz^-0HH0vP^8k^bn_4Cprw2&Zsybo~NG^%l57BPolY}zet!n19BAillj@9_qpo*#F65;GBs6~N5@KPA+e6q@d2Ix16>)&vy$|O;HUv00Hqe2fmH`BvOJjq45rzk0|pfxEGhY7g^02WE}YNh5rrg%IpWttU+0M--x#bne3U4IVE*`|Cig)w-}d^>{yX7~z;D0<2b$+$;e?PgSzB;lg6p_IAez^sZN!_*_{bJ!%0$jK9|ESFZdzLwG*x{YLz^MPnz^)3(|3Yi8}OE6bn4u>*@)B}7{7E8v{BT28pq$LyDg66SrO%-#5(aL3Y(HuIG#nwLhKuU+04S{w}KL4?z=vlcZ$%#zPCR*)wo!J5mMA8Otr69XvMLHo>rz)~4&A)Ee(9D~F<5ZiMAo^M4mjUxx8Y$&|&rFX1ScgSkX_!rlfTSjY-KD8*P0NThpx!xQUFnA9q*R*C!Kx8j3`$5}d0xP5Vt+E+J7J}YAeSV*;&UpY{qt7tF*ZeurJ3;a%phb);br+%r>`^$yd0k%C<mrXr40_9ofP$4rU;SdOLH(!iN(AtWt}ajGEr7syE^kVA$lYj=*~QG8V6RVQdT=6ve0i%s`R2~OvZ8MjLWQ6<CX*vhXZ_darq9Um97=OUtq|k=}?-%)l~+D<Xp#F6zUw(G87exL2BM4-5B7XTRe{G1}N^JV|EwVddHnmeMD_)m1qKg8p54s1i{)MhTFp&&xJCx>?(`F!VqqRs=oe76$`v2D!urZvv)~CGHncojHX1cz36R4t$dBIfJp*|B9g(5qTW3UC?QPaMO3y`z>bFENI5|yCC@kJ7Hua#w^BLnTgi(Fr#hniYpYE%^{6haocI~^XWSCb!1JJKo)8-ZeUmbJu?GTHY?4n3zs{^M(q3!~))%OdU<NdK$(0K!=6+};kZ0naXhzPSsWvAHdb8_Kt{-4Qy>&iN8r;)F|3?Job4X?CJlrg`#Z98xwxtzX?wcO9ho_JaB8m(-?_gy8;<P^7{V;!V?+b!D5rWOf{eb}7q6Bje1~-=EnZMxVz#WYH8)64`)vtDPA%{v&u#&@c6`2-lAw<PKg6-t+TrXN*A2dWS-^9Ne)A~A<c4CY*Ud)NgeUkPQkg>c;T4iTwPhr$AAr+0keMf$I0@b4gE#EjHh2f+PwWhe$mB=RK52_VWDy2>b4OvNA(=1|Bl#b%Qn$n@2dXf*cF6K(OFhk(5G;3l9-V7dEZgo`&l2XdFs*U2aZY}Q^uOxFIg>K5LkLMR}KHu6&*B^b7nwaNCI)J1d+7BF*_jGagdi7vSrM17T3j;c^nF}rT(Wruqy72HycJh#W7zV}zV3^EO#9SYhstK&zd1R&VTxs;L9D1shho2|H3V}->6%r7uqe-ZjATR(S)+pu!u$|3%C#I1}00^M<J$Le1Y~jKM;MeZM9y>Yn;|hb55(e-h+RhosZ;W*MvIWm=!7yGJOxQI6bHj&Y;p`F08j)9zv-~*{7!|FsD3EQZ_m@7&r#7op&-dXF8|eUv*6uBmxq~1b*9*|4iF(Ut7XF(rz5!ZZ6M=5oKOHrNg*39^IGPlvRQSkKr$S{!YbXgfb<vI~P}f*FvWSdUkm{*3(e%>Qy0EsNu99*ESz*(#GQ1#aQQAe^m{z2*Bp{}3BO&!kH&_|eZy_0K-4dvof2<3jE46(Zw7leGPAShRQD3#K2D65hW(&V~?nAC2l~R>KH6=-THd7&p<Rb<RAoac~>ko`yegWq564@$9)FR{w!*m_8{7-^%RBrnF!!8nuOCa&ID4Lx3#6_<aRuaA&1p#=`RnF}$#PZr|4@nmlaUC0`Uq0etQ}hy(fQS){X?X!NnJ3-b&XvXT7i3oBiE4dw4LB}QEy-t*51?U(D1+_^W&Z(k<R)_1PpS?(eA=m6>^mmbAGBx`Gy2G1IspOJ*b+-jNpu6s{pZ8-)s(4H%Ya4%!f7g7q2bmqONuL?ubGJM;c8*gA<tXus)fwh)(IatA|5D$ZZudQ@>eD1dzEZZ+>)tuO3b2Ixjcl(LI;Oe82ArZtbOV&17J2WOf(|d&PxKs1_5eVOWN_tV$y`<)U}ea<ntH!|9UwNgBVsY-!QID&le@TOWtR8UDV{RsQ8Mdj8QPukY{Mxn?N$kuR%Ly!V;8=QK$G_)W+lYN(r_|XuhvOl2EEL0FK^^W!Tm8WmXR-k&}WZ|ALi^=r7<0<XC|~*$L8<DNnKj>ML;=&1hrCQSlVAi3S!?0hsGfYH{*Njg;O|CYB;LF`yo`D-$4M0+350V>V$c+QtO9N=VZSj4})3vGbH<Q!x$S@t1OkDgySDcF6i;)H(8iy%Y&Jrvs)daRm=z2O*~j=5a?*lHgv$>svt{o67I`@Zz#qj*lh@_ewPr^Ts?vkSHiMb#58;2sERS35E59NwCCfT%wOtw_Nx7P^l%D&=h4|MRQqWcC(BUwiu#oUsA`S>d|SSMyuAxF-O8dm}ynI+F0~l<y-k2mB23WrNRa2Tl5+2ueFdnqMb46=mIeJn4V6ExUG6<=t{azu@bXd1d++~wxl+qjl}XQB12V7HfUi1qEG%x4)vC^n$|M^PxLXvw8h@ZD&wT=*hveaq9H9vEAr{eSO>BnIp0#jJOMzN;fMvPG_*1w)83cxwHn(JBC#V6tynPLr7H%~vO)YznSR?WSzUgu2zHVS(M#b;>aU=&+U%?C{MZjdv4KE0^Iovp%g>oVGsWIeNx$QIa+sQyZQ&nqI|8bgRKo`~{h8dSV);U;BMeCH$;R5B=!eT;-oN%=N1SA0&GJTJ@?%c|P+?^)%XN-=bFM_O9(tZOHCAG3h#V`im98;xNb(d*ztXhPRr-`@D$aHNp0yzTqSL41%8e1)(w8d5**kjDEo0C~(a{cYUL|V<Nr^@Fk*dGaALe8H7tU}JYtQu~rR5VH1wx)Xc{Bs1RJ$shp2f;;@usl(%7yHN4G>q;QFP4}U!uOVA-+o2ey)a|dgirmXOeFrmn&pWJtG_Ws;fQNZ9LgF5m)dtCvhJtaRv#03luW~^=Godb2txO<pd)X>1M1BUhG8HNjhr^TgrtB1HMY@eud{wz<$lvi&n@T4E4%mGxbA=v5q87G%CfH!*Pt3M<d4wv^EmMq5X1ZTh{O)<dv*mkW9eo(z@wBOn?iW8Vm@L5uZIF+DtPp^wjipD1nAjRl6wcsC*i!jvOQ1Jc8nmHnfHvc?c;uO@K!-sH8&7Ph6UZri!tMqQK-_30XumQB)3)lj&*=;0uNp%hd=Y<$z+`Kc??PoH??u0ofWbrvqyMRkO3QIR*2&C<}|0%kB&<1TXRci`}A%AgpttZfk{lrickCRj@>PAyq)SF~3MDfr^?HUsP7ei&sWT2BaewFORuO%u2TQLqQeL)0e7_rleaAYm1W-b^!#iZ&2m-MlK6YNQYse3I^?V1pW*8d47C`@d|iBsRY)~h(H9ArIAZ``Y0Tx)^>)sv+)G%A*vLKsxp`)oHvyN1(baE(yYScB|~Tea1cleqPPo!Vw~Pl=_Gt6%G%a!mY6zK?Zf!lUDcNsSbfRE4oCS?-v-<RI{UmWd+HcpC{nW2GNBdIm@OqlJvlK(gok3^o8(={zDK1ZSDQrAyqv_4F3hDXEO+S$*R~WOHcj=2DpzzXI3*<*)vFcL8#<TRlimiB`dWn30xzVj(p}gAQ5h$lD=wAY(LqcCoQb=Z;`6L3PsiA|zcp2fwe^GxIHg#SlG2I5*wz#uUaN>~Oyp>hz(_B~hJ-%HY#)6sRDeXG!njU1X_FKWUc||_EM8C)$+uRrO-Tiu#x*(bi4Lad{|T;9CJi~P!p0;XJt>;V9h4z5;-_$FCQt`W%`jvA(3=-)$zye}P`rcPu%`)Zz}xpbT0J4WWqZq^7gFnL9~J29uCgj#Ue&13k3a6*NGYj`G_n<!I0eaNC(Z<&q)~{VYT@G~BPmNSvPod|M-(<h2U1WvlICs}0Q^`Tf%&_N7;=B%RL;ia_mJ<#^eNp!{c|-&rBb~)_f>Cnvi6mp2*FoZim;c^NYpdknWqphUnY2~C=Ul29tkEkrMOdC6?4n_PN2dO%XysKGg?im$jMetET~m;E46G+B}J^{N!kX{z)`FT>?#^XDHBl<4gk)qQ^j&>6@nXXItoi@8K%4jbDE3{pB$DcUTHECnW4)yjFTSPDxR@`BZ)zi>g9gr9<tnfxJXDX*A&T#@Lf{5M~wAm943CoKn#Et(}}P5ln2rjXa3#@p%LTjhuOR*lw8oLP64Cmx$^YHJfzVd-Ubyu)#Sy9?NTXx$o0!uL*ik}M%<|x$Gux-X~x4stFZ_C?o{@5+xUnUqo}HwQJ<q(>+1Ws5t76EX$am~!J>p#WO!CfKSWumlt=2H4fREoNP&&oo@kWyKm{*RkdIaK2vSWG!f5;?mrm8<#;cGtRr+Xh<d{%jFc^~jT?*rX%RcfIBNvMPhW<FU;Lyn<2p1?Js~l^BiW#sPAX|S$gPzAG;`~%~qr^sYj$Vj{piIZR9){81C6WNl^Z|?{a0|(Y@wZu0{0l%}J#}MBaW@jpf=;emd6i=73l;?nJ8Y}#-ZzUnSV|w-dbK>QQ?Gj^&5t_An)`(veDi;|7fVh'
)))

__version__ = "mapleleaf-6.2-kaito-route"

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
