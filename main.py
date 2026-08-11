"""MapleLeaf 6.1 -- unified route-and-market-control engine for Kaggriculture.

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
    'c-rk<O>Y}nlKd|^^I(#)Z0}8NbEbt+TZSwzG20Lt4a_VSSj--J_qN#ozOqEJij|R(k@;Rxvd1@CCad1}%Z!YS{Plm&{{8nq{_*!e&i>`svrm_wKcC$%&i>=~|N7g1Km6h0<3E1?<3IoYKM$XOJ^T6UcJuJR^uteI{`%YH$E#m1ug?}|?{Btei>3MV=bty5PiKqs{eOJkY(6~vdHeI`^6qT$dh+LAHrF>FM}Piwd-LJT`@8WE?*DIb)QhY4fBEuh^!`JCem&c6KHohy^zdQV=h4p&?HhOBd&jO3$8Y&~b9?vm<3oo}_C33w()a9|sXqIsFIU$eetY=m-IuQuLLNN%rr!GN%lDhZAkiV(ee>%q96kTxKR(_aX4ZMnpT>)Vz2^9fM{|97x4HG6|Nb%<pr<e3aoP7^|I*QOcVA-TGTCJ4aYNG!Q)^!^JPs^-eM0SX4^Q(4M4m|d_|G?Ab^{K^Bb-2goQH*Hhodroqt^N3&@_LCQ_GG+%ls(=(lCG0xK!qG|64E|PaUW|Zdh;AKh>URhqudWVBK$84f}^|E;}v)Wi&dkfu|3N$00i>ybi*Z_WtJjdh`D7w?A!e@2;+|{_U}u_C877{)KA`HG@20f6JvB3f>wvG#H&^v-f+q=LA(YfBnGt@sl4vc|kupJ`+E0uD`l&qn+~Pkzo(e_-GgRDgWtUg~TV1Z~j|9Yf(GOj6ZZdG_b?V`{Y?O=|{`$FkFh2hJy1Swq0qVf0y7k#y>a16dv+>`=IkMfx*Y4RB7PU-cK!pk=ImswH@F>6NUjcEs)0-Oq(;nVFQ_GSvX3~5EY(r7$N&xb%ek}@c@-?i+`5iR<F9FJMS39Tu%P{`R?{|`_tz3_OEA)b@4KseCU2D_PQRQ=b~)AGWYK3Xr@|wBDrD<092N*RQ=wtjkCuZ9+76ZYI^-P-4np?qZe_H4j9-oJ3?R*5!M;|l8S{iERWLjhK9NLcPBH`Gd(mT#M%oJOt9&)wFid_KouJ~0o_`zz8??i^N=>XpvmJUXW}$m`s42J<u121KIst_+id*jqKoD@(qC8a<?X)~E-)~d<eDgh4ha(nJQM`dDo*m$#g>}0JK(kD{2Y^@yWEG?NgW@)jXiK1{m#emnrsK+o*!;yWkPh1+=fHtS&~9wl|Fy}SNHzpe)DJy*W7%E+@yQ|=WTSQx~DX~{#O~}paF6~HbU%z#qMcrDYY9M&ut+f2lE8x0wIU_c0+t>dxWsQqwKFlb+qF{*kc1k<E-|<+6u#cdAO3EKD2G3>0^7qIu0sw0;D_PinEwNiz}|8Xf4+w>t=mS6}aTY4`~Y17~;{1X5cwNg>@cOP>gl(nwMo9j2)6w*aghp2>nSPhv)*L<nO;k_<=z{4A<y2@WAuz4uG_fPEc&4ZU*QPq!SGNwleO_kV)7c_Az)Ngb(^~d-Ew+2gJS_Jjt7z>)lBWPVn{K{d>50KAgq2okbhatBD)B>KTOIKQVJ~=r$?$LJ!Y5EH?eg#Az8GYhba7QIOzed)^F4Hc2c{<*KwXqk=1db9=-PcnN)Z+%rqMX_OSR6hN~oq9BhyUgMRh#Zlx4&YJAfcRHi8HSV*3Au2h<(}Le5Kg|mCp!cdiU6+>XAQ4D!^UaUBY)WAMIiurr!yfsS)ipi*=?E+^-J-=%3zpaMWq}Tr9Q&r`XArN&n=`haI+Kj|uR>EJubr-hQv{ycS9%lG<eh-^9J~*%=#6S002-B9vtSAM#&g2tQCP?ToQv>A=3dlsSQ25?&O0=W9r#rCNSqjlcwyM6zs4TaGN+vTRG^eet^|Q_?Sm(?!@^1W(uFCtN4o|+_F!;-xcc+tONBSagg<2Cqp!CFp~1cYZx^qTN`#n!yo=ca({A?Zyu`C{1bc8~db&*u?5gyPDRYO);1R@t<q9HWhic_IR4d))m0X$OzP4l3l2YruZhU?p23EKDSN9##b5-{#<47tgWY`6=Ce$nrP>3Th7!3$nShYpL{T<Uv$Y+{)aR^?IG3o@`nnZfAX5-W>>J&W~ZarrdGWmH5Wfhplt~Z=}S1^l?wRN<l71|uI|AEOmyv>Zg>pRDbhs7sC8}cw2ETJ^<LbQd$b2eN=z_s&F1M1;sl0wNz<+C4Mtm7~o%6h7vPGIyAC!_~cb9zHB0zzzyiOf`Z7$VeQ9^>GgVi-@Y+Kc-<&jW}I^|k&_X!QSbb^VvGqkv;3%U9M9c+(n3X)^Iwjs?U`eC8iS*1iCsOZGaZkYr3%ffXQ`$2ohsJC^{p(cW~GHm$REBtovDo3R7Qr9c*moWS@5uW(8x%a)wxbqF-iK@qHbHZHxK5NbmX3%ame8loIvX@m{~h;mfYVF?vH42{JYzS%M^IV4=PO}#w41DI}PJ$BeAYzUB35iLP851rEExpy2aLBrlk3ftHS1jwZmgR@O=EpaEutFul2(R>&`n)yTha;D(2pMgD3-apa0nJGDJ5$NB{_u9E*470q5QM4|c=)yp0?CfI9HV9o9WyeC~Z#p<g;LOt<BpbU0Ar<zeF2sFD1WS8k(0HFx-kK+1kD{$>hY$`z*7`4U=xR8Y?V9!8`~-H#C~WMCwT-OC@X*|pV>eaq4q{<qm)pEUkibMm^)1poQsma=g~j~xo+jvkfV$i601MMe)d2*n3dXEj0Cr1&)<gYyQoLX$yc%fs2Nq9wG5|9eb(YT0WF#uu%&<>@aE;7o-%WLxP8nBXGRZ_a5^oklycrhGE*AwlK2Dy~CQeP+nJE{Z_2P3Q-n!ffg)9l=-5pAfNXU{Iv26NnR0Y&Jh?#<rNs{pYA%5va4<TftILAr<oUC&2wh*S0VL@<U9=3uHG~g~p%YHm#7w-CgcY^gzLWz@af`MWezBp2it2H`$xuxThF2?`&v<Ud@Rt{<bnD%+hLB9gHOoJwpih+#_QM<Qj@g#N$%8~>t0juO|Qf7f3ju!$RWcyTKnWDW=h&HFYk<h2?x5$)kgfo`81ax*kB`W*NEx|ZA9ciFPLgguOI}OR}3BHL0WC*@dXhci=JZ~VG@@pxF+cZLHs3{pRE!(o0NvdIPCx8wZCV+0Ra-Rr}HUmYXJHDi(btyE8GIl4h65V;%9n@hR9J%o?fSykY^RaknIfI9-TRXS8WsCM2SXV_w)sO@%P4Obws7)fRFvZMF95?cb@J5Bx%w{*<M<Uh{Z+F|U;n(}zJDV6lIrik<s*O;HYUOqV<G-{C_e7|GC)tA6S(Eq=il0gg-r^7inQ2VLT?y<j3QH#fEN<P?V!Cxci!$VNL<FWjZ0jWB!)oVL?%uiGo?z8IW3wvx&?gw07A@#k-<Weu*)1t`NKD-aaXuve$em;R+woDka{p(kJI`<L72!%krRNTZ9R`=f(kmk%$&MA+H78FKPzbiq<?f@21hF{H9N<y%KI~y-?Iv6zXsR84cf1j`5E9&R)qG?xzpm_Zre#p!071g8B&ZUP9}yAvYGNeVyxjipC-t%=GzB_h_Uj256cD~7%tC#LFz+H$wANpDTl!!jiHEF;Owl;9?l3tE_)pw3?<*!mb_M4AW#vk1MQE&B%28jUm9-(fmCTvPBdCUQMQ8Ka3URLqg_1Nj@!knhU*`HbbL-nl+I><INJF$V;wt;^O>Y?zxm043GHroOys~2&66JE?Z;{W;2t<{(CH&O|=RAfpZiTCh?z7(rmW}_I7;-+!3)#n*8+`B8_<6h3lhrquTJp^4@>@r?Bb_$irf{TwI(?wIO-T5(fj0t0^o|y{M%~nk8x5;01sNnQB_^a*f#zY#3A}D*U1m%sm36RTk&)0=NAhr+-Vt(T7(cXzIEcB{JgR72lZt7|T%82@H4|$Et?>E+SEc<<!zs;E&(T?23$o@Cedq!qlz*B8P*7J>*CMs5nJvu&qq#(ViiQ(X!+hEE)*i8*VCRx-EP<_-0@g*w>{JoF)AMRy6q9$Hk8cuMj(w{23v!#ZMEnl^6Y#Jbvg!SpWuM|b?&E>66Qltq0CS-r%NB%(WUAJ4)oZbhW<0Jo2W#D4(6^Z6zKt`cYwSy|rJVfV(#{xXm`B0LMK+?J7$jwbuq;l+iav$xncW$&^F?GKg6vDJ&8XaqhvWN^1`uD=m0UB99AfTmbSmQv7CYaPOsS;*Q1FT#{(eB-#L3F`#4s0&(y+;^6Fit~Pq=5nH_6@+R82HD5&LBdaN^kmz-4?Jo1-b2KSUSy)QVC*0wXy48v#VLa#L4#C=qd3-WfJL$oZ<(MiObDD1zCP{VEMtTc+;ms?E&hi@y6l__DU-%~DrCsqkv!7~i^-bn5VE)48V_eYS`2S%Vi%LxGOhJePwi%OV5MDa-H$!L~V^>QvSi4_f9O9ff!y-M6JQ!G=*y?wm|%4`^%!i=kyR*#&^Zyp*1bEtwuNZd`Xpa@R9q0-2W>@JJ5>4NYeI$0F@jp&SM|?*P2WfILj+jf4QHY!^5L8v$4(L8MAo36(30Mc64P80*5J#<Z_$I#4uXUE)=0)w}Qj97JMx`64xi^TN>Ep6F;Os2Q6B6ezN(oz!Tg{&y~kcN0#Q3T?F%*-A-GxN(rC6m=@~b68n~SL``ugh2Tg5Ge5iTP3uLteb3OAx)04UEC7QRbY<I<*SaPq|0*~COs~kG|bI66*<jIn2$ZpnyZ@%$M)f~LJxQC{!gfp4uADps482qH6k}Xb;$WQTv1;<5fV<Y#{}p9B?OMOGFLqA$$C?%AXE=9C&VfB6jv=6$CKI8-XJpw$Gq<dFb`;YQ7Er-4KJzOyv8bKS#Ui5lF(d{s!t2C4(c4B_#t+1DyTv$Q9nwuro|N4c_3t@)gS;zqgRfW<2C7SG)8c!sL)6$duWGdYdj>5x>hWPBE4d=aafa}tzsIY&zT8O!unZ-fk<3B&SYl7V@;udEnl6T#DxU~0B=0F;JVUT0+c1yjU*yeGmbd~2yIf%BVFt%DkW=o3s@{7Lp{gXKteo#o1R`|OlXU2e?c;Xi7#%IYS3=1D3~QlJ1mw=+s~d%MGR}0v=`4N7!ROaDRdH{e#t58aSt_6qEk96%}rFoACb4!Qd9}=QwaR!NP<t0uy;;!!MB%*Jq5jHMz>nj!{w}lPN}rnYSo?}Q_QGU1fT-vWxIJk(PSVfB#`^IV!*ymAPw-1(A@2zOx;CCK$mPnOR2459N_)B#vElhk%Zk-Ezm8c98lM}fv6)z8HI%@(by9_GDb&WCydB4>sysOl3<EmJqoZ@28-G8KG4Ujy_ZNND!+zu5(=seia!Y68BP_sG++l~AcQUTKmwA{aAq1aVrL|lxjIyu44E}gdCm=n=B;Be@+~{~>Ji(O9HA2|B)u<LV`N&HZ#S`_E21~7#Z+R>*EUx~@rq-}G7Myy^9&KpHU=UO3SEPLzbBbvWhpf8zK1OMML#EYZk2CVyxtHoDyrF#P~E~4+iv<0CK|=7vN&;fdWXI0bJE>}a9X5qtUGx?phL2xcP_S2p>-5<K_f&|%(^Va3A1YYI8Q)vpn0*Mt_u5(S}@D}&E=!Fr1j@@_wzh|V0g#1)8}AeG57>boGMr~lM+Ao1X2Qt$=F{PWktN~1)rXuCZ)1cj3-ZJuq|rIf{URTYC9H3)!b8R<Ylr=g)79SPf#cql0BLM3k0NSy7OqCNi~&@)dv<0I38cb@lipE8pIcC9cw5`Ae;w?>)h0`Kx)Ez>5POc4p_r{D+=4JL`Epgof0djwcV8JaqTF?T*`-VDwV?S1#SR<6qYrm^CwkvPr&aezpSll_cxJ-GD}3>7t|}|pU{)d&Ejy9N^%kGIm&}8&`e6WVMd++z(CTRS*f|tsRU2Ul4ivqfT_fOF&phbmzYCywlBp?F$<n2-_A~eS-L`!iJneFvh0xyyB`%L(YGjGC}pKMn5yEmFvW=a95yK+a$*Flu%*?Yucc*&J|Y?9e301}whP3DLKXp)3(QrD!(mDxtpJ~t#q#g;ND5Cqq6f*rt^MAQ9cikPBaBuqV~gg;kqou=(FgK5#B2!ka`L&2717ShJxNYvayHSzwcE@VV2F`6cpC-A6^qLWX*g9KRcZcpvxa8X1pKAiyab`nB6kd!&(cUK_j_h~1avyA*Ggk*Qn({E3G6OSZEIQ+qygg2Y3E8eEGL}OObu3A(1K7xYRa1eXcPOB;oh;ls+?|Te8uOKLHp;VJb`SA&PqKq<w&IEi172OAHC;gq^2~Ax13*`D8HpkF%1r#y)J6C%n=XGSKnZs5({uwDl}WZWTHa2c6H{<KJ-W)(4BeWG!BeSr9yVZTA|;ZRmDZmhKz&C8JAfttSyNi4k!EO`sO1@8Qm)6zQB-6bDuPWtE<Ed$)}FDDAYEjl_n~Dg4Dc8nlQjWw|E@W1W?>T$Luap^Ugb=`iRHWD!&B&G{ig22!gdi47c4JFNK=1>?(`F!VqqRO1}O{6^pkein;igvv)~C=4=dxOr}IGr08u$twN2jVo3sqB9g(5qTW4nunZ#B20B5PqXKp`)IZ9J9Vt1yF_Gvn`MH(KIo?XnOE}dLzh7HzlBq|vUFD?Cpg+@=aJrobP4i^eAn2Qv$csG?uws+sQTTOcg^~7RW3awJh2$}yw@a>E$S3zhD}nS9_e3)i_Dp#>QJtGze{#(L3+iq2fzsffCfYtCFrPyzQ|IA+sjco4rLzZv!6(1zQG0j_`5>Z5k@F5l)-TTMv)vDK6OX<iC=VgneA*ufz^!U9=fU81sDNA>e2j5_N9@3^+SE?s<51lRR&SWE3e!rhb*R`!u$>&9>qYD9gNEoOoA@_lT3@GfPK>d}3pi0JPttw@GL|<<tE3F=DUA9hWT5f4AIUE-pkkDu(;H`>Fr2iZz7)5*5~+jyLAAn3r9A1NAsb0Ynni4ivQXStQ#v$!dr#|Pu7nFS1P)8H-gV&3;GyMKSCt?s<wvW!CqC=e@{aLJG6z!Vru_8f>iWZP4|dYs7oVgiCbf|cARUMH0|#X}U0=T6>};vDu9tOTKnM17q2)PFEM?<)>|V)E9&!)Ez<2-*lUa(G>yt7xft9<AtQ4LYjsBNIPn8Pr%S2cqaOtBW0b)h8gf>(n@dlobhxHzXf&k>R-v-2DGI;?(*N(i*SFzy>*M(ok4?FVYDu{~>&dMXeYwIv)An!4f=F65k=as*fpfXjC3`z}gPj-vznRO`|7661%oeB#M*>-v@?~{~jvrY9hAdb8xJ5VbjmloSvpIeY`x%v*scTF_8b^oN(6ynjydE=N-oH*g*OPxxM5&57bsMJLcra(|*1;rxDSwVfL&NtJGQtQ&#eo{)x;bSF8!<z4cPDN=Kag$k5yOQ9Rwv7Y^%nwNh6<A0fTDLT5<^}5#=1O&*26-+yWmC##N>oT~tFEjeqS?|do;Q$dNTt|hP!CDcj?L8gAz6n(14zZL%K8K2mtTPS>_fH+64eBGS}<LQEX$K%8I_y<>9C7*-x7E`Eo&yHHyt^L%M$qrUyg!?yXgAnwihCE8C55GQxR9NVgBVa9_vxbRU!f3A{f*13TARnit`DS&BMx8{({VEN^5f6r8SsxEkQd@QMlaGy8b7~e4EKZe_eIZ;nObE^4u|9{-kA|n2|^R(#i3+#+6tUN+J<ZMn4~xZ>F%6TDUW!1<q583Jte@H&Pq{ea*yaPglK)4td@>S1n@3p-%X`5uHGhX`><dkd-R&*{c+S;+9M$Nn&oq#$^{o201vq!f<}TP3==5833_~VWI)WcD50qD+tiSR+4{DmVYMHrLMJyB_F@Q>enl37=*Bb@rGe>dcG(*Tk<}$>!K!NMI}`%5sZSLh7v=Q*#zoPehu0w6PBP{K03wPqBb7CS4tjYLbiPiQh!q7{y6w97EV{smqk5%L{18t(hF8DVy}Q7kYmLcZJ(;dlqXpM@s+rXX0);6sCWw5^Z^T?0E~5%Fq}M6qoS24ze<si*wOnI)hiPKU;=PUB4IWSE8507PQ~Qq1wxob?bvxra-^6t@AOMW*p1P_f{~?CSJXN3fV~v8H>d8U>uUuMVh15-_~miOl|4+KWVpT;<guxOo)0gsixu@~>Tj<EGBF#>BLImqQFCXEQI9|~8kzi8PnblidQZQtsTZ9%VFVMHqFkzIE=9g}B2R=ZhUnUtG_R;8bQ-A93hr^tk#G(cTA{7BN_$+pTlpLntuFAR!UgGD^ch93t&kC-oiXX?0x<WON=}HlZF(r<N@`BAzOq`!kcscMBrKwh#L^-nLsiTbXkq=KPyR{{Rg|+z)iU2t^fAL^#NN3k(^Tu&NeiK(A*)BL)9H#+2Vx#M-%`Om0YI7Igaw%}W8?YVeL_)R!q;l-N{GZxJhWnoca*Ma1ZybB%Xe$4S%GG})G$Si%d7K}6jed%&Hx{Wd9o>Z)DB`|m{0Q5OHZ~1$Wx!YnO%uu3!<Ej9TdRyBGW{A&YNB=G$^%~VZ%KMR%r6pORmE+D(Lqt*vHK3;*ApG=bl)f!n9hKD-!kQQHioTwCGw>V<q;5$eR*d>0a=sBt)?kDow>)r9_G5-%?lF*$N^pIwdNuu^1sJed$k}k)!9qGFFTf@$3N6RWeVI=vQR)s7fjQp*zND;jAUGN?bppSw2}&AlbQ-N3%#uRi?5jR;)l4Zwi~QTo_K+0CC+LMS)y#5b8S{Vy1NM=c?VQXI|@eCMgqgVL|4oGXjyXkJ^K=#uH`}u>wE)5%-}IJCHE7K*S=@X(k&yhuzRsPH;bwLdGiA6_V5v^eT!)$~6T85=!fag$GYSY0Z{)Ru~%$%E}`y^;3vZi6r?ls+yNWXN(|6BXJ0{HWH|z{c>je_;oc#N>;;1X4Q0Q-FzQrK!z>=GW5zIL$ALlIp&upibGj3lz-YqCPyX7NG0DGlja#@bF`r~l*d!ZvuP?il0_xeOn%||IyC=_g$V_E=0->jqS>Ev)SFCKYgAq^v{(X082$#l;r@YoALGn1cn!+d06Lvm$fufel}!{_)|FLQ2wZk&Xw7z!+*j-tRrO$<3nf-7d@@B5NGVt)Y6PiT&y7h#O0`ndtoWj`YFxaCNiy;rxp;ZdRiaC>wI7P2D595=lsGK+O{&TTuKuy%l-mQj6fz-~g~cQohASfcK`xe2wk>A9M&^+pxM7R~UK1)21YoQmg4NQHCOnlC!cuEH!&}>U2=;JQ>O58HO5`OuZ3H57bWAPEA3KD;Bxo5$cnpGQoZjW{1~&FNJt^hG^x0hnlvY?k35>#Pkn;2$fICfzPUragkn)<=30arM#3mt_$@wlK=o5R?Bt=5@C@Lkf+SH7e<$Qy5Wh`C%xJyU4?4$skX#z!5WTIQeCn*=GUM`s4ueltY^fr)$(jxQ~_!eaW?ZOU->L}^7ZmI5#4owm`Ox(2;b!TO9I)=3Ut*NS^ZD(A-DRF_6>P-Z(wr1n-VnJkMA~%VIJ9-f@BuqIb@#t%z0uKr$zI7H!o7#8qBF?F0QGlX;y|spI_9&n#ZpnF1Br8Q1=xuDXXEKJvGH6VV(Nm3ys=&OfR)O*O09K#Z79vxV!B{`^=CK;xOvo$L*<d&9MZ&Xp%TW&^E+IH&d(;S=)TBsQ7Ll^O#%}m|XO~z?bs~*yg%tod<oq?w8ZsgwFEg9S!$rzXi>wb=Xc2||(9siAX`~621z<jwEMT6kqEOsl&6Kk#`HkZ{EPd*yP)}TqF{xZ_PF~d;oh(45XEN~Bl_K0FgbVfbbLJDo%a^IpDssR<ibjG;O*!h67R4N}z7wc$ymG!J_klLE%4D*Y6RTX+97ru4Q_1lv`HZ$f!1RPdjB=e=QrfprDpC=-*rqDk)Qa>r+<+9A&{9Wv8RRs{7(O{H3B1uXA2LIiYZxavw3Q=cp+yoyCI!U(sybvFyj8b>;*5eC!dihJURB4bOl`dky~+ISfhYj0d=p>$DbJ)SqWq%~LL;Wv60?P0Q}?w|b^`i}xeD>bY^3oY-Ubyw)wIBfO;f2#$i>E3L*ik}#@wlS$Gu)=fyTo^E1w6v?NnNI+xUo<q$q)yk&2_~=<55p5t2jvX%OC7!J^((WO!EVG(_2@lsD?14fREoNNtVUo@kWyOa<>z(0Wz#15!;B0%`mtmrm8<#;cGlRr+Ug<d~{nFc^%TQ49UTWgq#9kqbqCLw}rFaOmU_6bazBbYL1d=2WGC73?_pD;gvnM>BTd{Kb8((VV3hq9iDT@v(=MPMoLu07eqHh2+EZ+Z3k05IC&6#Q3*DHxkW)POe)fm3Cs4>4aTlrt<Amv#5im^r5X+>kC!-v2XbU*vq)NZys88|NntQ0?7'
)))

_ACTIONS_P1 = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<O>Y}nlKd|^^I(#)Z0}8NbEbt+TZSwzG20Lt4a_VSSj--J_qN#ozOqEJij|R(k@;Rxvd1@CCad1}%Z!YS{Plm&{{8nq{_*!e&i>`svrm_wKcC$%&i>=~|N7g1Km6h0<3E1?<3IoYKM$XOJ^T6UcJuJR^uteI{`%YH$E#m1ug?}|?{Btei>3MV=bty5PiKqs{eOJkY(6~vdHeI`^6qT$dh+LAHrF>FM}Piwd-LJT`@8WE?*DIb)QhY4fBEuh^!`JCem&c6KHohy^zdQV=h4p&?HhOBd&jO3$8Y&~b9?vm<3oo}_C33w()a9|sXqIsFIU$eetY=m-IuQuLLNN%rr!GN%lDhZAkiV(ee>%q96kTxKR(_aX4ZMnpT>)Vz2^9fM{|97x4HG6|Nb%<pr<e3aoP7^|I*QOcVA-TGTCJ4aYNG!Q)^!^JPs^-eM0SX4^Q(4M4m|d_|G?Ab^{K^Bb-2goQH*Hhodroqt^N3&@_LCQ_GG+%ls(=(lCG0xK!qG|64E|PaUW|Zdh;AKh>URhqudWVBK$84f}^|E;}v)Wi&dkfu|3N$00i>ybi*Z_WtJjdh`D7w?A!e@2;+|{_U}u_C877{)KA`HG@20f6JvB3f>wvG#H&^v-f+q=LA(YfBnGt@sl4vc|kupJ`+E0uD`l&qn+~Pkzo(e_-GgRDgWtUg~TV1Z~j|9Yf(GOj6ZZdG_b?V`{Y?O=|{`$FkFh2hJy1Swq0qVf0y7k#y>a16dv+>`=IkMfx*Y4RB7PU-cK!pk=ImswH@F>6NUjcEs)0-Oq(;nVFQ_GSvX3~5EY(r7$N&xb%ek}@c@-?i+`5iR<F9FJMS39Tu%P{`R?{|`_tz3_OEA)b@4KseCU2D_PQRQ=b~)AGWYK3Xr@|wBDrD<092N*RQ=wtjkCuZ9+76ZYI^-P-4np?qZe_H4j9-oJ3?R*5!M;|l8S{iERWLjhK9NLcPBH`Gd(mT#M%oJOt9&)wFid_KouJ~0o_`zz8??i^N=>XpvmJUXW}$m`s42J<u121KIst_+id*jqKoD@(qC8a<?X)~E-)~d<eDgh4ha(nJQM`dDo*m$#g>}0JK(kD{2Y^@yWEG?NgW@)jXiK1{m#emnrsK+o*!;yWkPh1+=fHtS&~9wl|Fy}SNHzpe)DJy*W7%E+@yQ|=WTSQx~DX~{#O~}paF6~HbU%z#qMcrDYY9M&ut+f2lE8x0wIU_c0+t>dxWsQqwKFlb+qF{*kc1k<E-|<+6u#cdAO3EKD2G3>0^7qIu0sw0;D_PinEwNiz}|8Xf4+w>t=mS6}aTY4`~Y17~;{1X5cwNg>@cOP>gl(nwMo9j2)6w*aghp2>nSPhv)*L<nO;k_<=z{4A<y2@WAuz4uG_fPEc&4ZU*QPq!SGNwleO_kV)7c_Az)Ngb(^~d-Ew+2gJS_Jjt7z>)lBWPVn{K{d>50KAgq2okbhatBD)B>KTOIKQVJ~=r$?$LJ!Y5EH?eg#Az8GYhba7QIOzed)^F4Hc2c{<*KwXqk=1db9=-PcnN)Z+%rqMX_OSR6hN~oq9BhyUgMRh#Zlx4&YJAfcRHi8HSV*3Au2h<(}Le5Kg|mCp!cdiU6+>XAQ4D!^UaUBY)WAMIiurr!yfsS)ipi*=?E+^-J-=%3zpaMWq}Tr9Q&r`XArN&n=`haI+Kj|uR>EJubr-hQv{ycS9%lG<eh-^9J~*%=#6S002-B9vtSAM#&g2tQCP?ToQv>A=3dlsSQ25?&O0=W9r#rCNSqjlcwyM6zs4TaGN+vTRG^eet^|Q_?Sm(?!@^1W(uFCtN4o|+_F!;-xcc+tONBSagg<2Cqp!CFp~1cYZx^qTN`#n!yo=ca({A?Zyu`C{1bc8~db&*u?5gyPDRYO);1R@t<q9HWhic_IR4d))m0X$OzP4l3l2YruZhU?p23EKDSN9##b5-{#<47tgWY`6=Ce$nrP>3Th7!3$nShYpL{T<Uv$Y+{)aR^?IG3o@`nnZfAX5-W>>J&W~ZarrdGWmH5Wfhplt~Z=}S1^l?wRN<l71|uI|AEOmyv>Zg>pRDbhs7sC8}cw2ETJ^<LbQd$b2eN=z_s&F1M1;sl0wNz<+C4Mtm7~o%6h7vPGIyAC!_~cb9zHB0zzzyiOf`Z7$VeQ9^>GgVi-@Y+Kc-<&jW}I^|k&_X!QSbb^VvGqkv;3%U9M9c+(n3X)^Iwjs?U`eC8iS*1iCsOZGaZkYr3%ffXQ`$2ohsJC^{p(cW~GHm$REBtovDo3R7Qr9c*moWS@5uW(8x%a)wxbqF-iK@qHbHZHxK5NbmX3%ame8loIvX@m{~h;mfYVF?vH42{JYzS%M^IV4=PO}#w41DI}PJ$BeAYzUB35iLP851rEExpy2aLBrlk3ftHS1jwZmgR@O=EpaEutFul2(R>&`n)yTha;D(2pMgD3-apa0nJGDJ5$NB{_u9E*470q5QM4|c=)yp0?CfI9HV9o9WyeC~Z#p<g;LOt<BpbU0Ar<zeF2sFD1WS8k(0HFx-kK+1kD{$>hY$`z*7`4U=xR8Y?V9!8`~-H#C~WMCwT-OC@X*|pV>eaq4q{<qm)pEUkibMm^)1poQsma=g~j~xo+jvkfV$i601MMe)d2*n3dXEj0Cr1&)<gYyQoLX$yc%fs2Nq9wG5|9eb(YT0WF#uu%&<>@aE;7o-%WLxP8nBXGRZ_a5^oklycrhGE*AwlK2Dy~CQeP+nJE{Z_2P3Q-n!ffg)9l=-5pAfNXU{Iv26NnR0Y&Jh?#<rNs{pYA%5va4<TftILAr<oUC&2wh*S0VL@<U9=3uHG~g~p%YHm#7w-CgcY^gzLWz@af`MWezBp2it2H`$xuxThF2?`&v<Ud@Rt{<bnD%+hLB9gHOoJwpih+#_QM<Qj@g#N$%8~>t0juO|Qf7f3ju!$RWcyTKnWDW=h&HFYk<h2?x5$)kgfo`81ax*kB`W*NEx|ZA9ciFPLgguOI}OR}3BHL0WC*@dXhci=JZ~VG@@pxF+cZLHs3{pRE!(o0NvdIPCx8wZCV+0Ra-Rr}HUmYXJHDi(btyE8GIl4h65V;%9n@hR9J%o?fSykY^RaknIfI9-TRXS8WsCM2SXV_w)sO@%P4Obws7)fRFvZMF95?cb@J5Bx%w{*<M<Uh{Z+F|U;n(}zJDV6lIrik<s*O;HYUOqV<G-{C_e7|GC)tA6S(Eq=il0gg-r^7inQ2VLT?y<j3QH#fEN<P?V!Cxci!$VNL<FWjZ0jWB!)oVL?%uiGo?z8IW3wvx&?gw07A@#k-<Weu*)1t`NKD-aaXuve$em;R+woDka{p(kJI`<L72!%krRNTZ9R`=f(kmk%$&MA+H78FKPzbiq<?f@21hF{H9N<y%KI~y-?Iv6zXsR84cf1j`5E9&R)qG?xzpm_Zre#p!071g8B&ZUP9}yAvYGNeVyxjipC-t%=GzB_h_Uj256cD~7%tC#LFz+H$wANpDTl!!jiHEF;Owl;9?l3tE_)pw3?<*!mb_M4AW#vk1MQE&B%28jUm9-(fmCTvPBdCUQMQ8Ka3URLqg_1Nj@!knhU*`HbbL-nl+I><INJF$V;wt;^O>Y?zxm043GHroOys~2&66JE?Z;{W;2t<{(CH&O|=RAfpZiTCh?z7(rmW}_I7;-+!3)#n*8+`B8_<6h3lhrquTJp^4@>@r?Bb_$irf{TwI(?wIO-T5(fj0t0^o|y{M%~nk8x5;01sNnQB_^a*f#zY#3A}D*U1m%sm36RTk&)0=NAhr+-Vt(T7(cXzIEcB{JgR72lZt7|T%82@H4|$Et?>E+SEc<<!zs;E&(T?23$o@Cedq!qlz*B8P*7J>*CMs5nJvu&qq#(ViiQ(X!+hEE)*i8*VCRx-EP<_-0@g*w>{JoF)AMRy6q9$Hk8cuMj(w{23v!#ZMEnl^6Y#Jbvg!SpWuM|b?&E>66Qltq0CS-r%NB%(WUAJ4)oZbhW<0Jo2W#D4(6^Z6zKt`cYwSy|rJVfV(#{xXm`B0LMK+?J7$jwbuq;l+iav$xncW$&^F?GKg6vDJ&8XaqhvWN^1`uD=m0UB99AfTmbSmQv7CYaPOsS;*Q1FT#{(eB-#L3F`#4s0&(y+;^6Fit~Pq=5nH_6@+R82HD5&LBdaN^kmz-4?Jo1-b2KSUSy)QVC*0wXy48v#VLa#L4#C=qd3-WfJL$oZ<(MiObDD1zCP{VEMtTc+;ms?E&hi@y6l__DU-%~DrCsqkv!7~i^-bn5VE)48V_eYS`2S%Vi%LxGOhJePwi%OV5MDa-H$!L~V^>QvSi4_f9O9ff!y-M6JQ!G=*y?wm|%4`^%!i=kyR*#&^Zyp*1bEtwuNZd`Xpa@R9q0-2W>@JJ5>4NYeI$0F@jp&SM|?*P2WfILj+jf4QHY!^5L8v$4(L8MAo36(30Mc64P80*5J#<Z_$I#4uXUE)=0)w}Qj97JMx`64xi^TN>Ep6F;Os2Q6B6ezN(oz!Tg{&y~kcN0#Q3T?F%*-A-GxN(rC6m=@~b68n~SL``ugh2Tg5Ge5iTP3uLteb3OAx)04UEC7QRbY<I<*SaPq|0*~COs~kG|bI66*<jIn2$ZpnyZ@%$M)f~LJxQC{!gfp4uADps482qH6k}Xb;$WQTv1;<5fV<Y#{}p9B?OMOGFLqA$$C?%AXE=9C&VfB6jv=6$CKI8-XJpw$Gq<dFb`;YQ7Er-4KJzOyv8bKS#Ui5lF(d{s!t2C4(c4B_#t+1DyTv$Q9nwuro|N4c_3t@)gS;zqgRfW<2C7SG)8c!sL)6$duWGdYdj>5x>hWPBE4d=aafa}tzsIY&zT8O!unZ-fk<3B&SYl7V@;udEnl6T#DxU~0B=0F;JVUT0+c1yjU*yeGmbd~2yIf%BVFt%DkW=o3s@{7Lp{gXKteo#o1R`|OlXU2e?c;Xi7#%IYS3=1D3~QlJ1mw=+s~d%MGR}0v=`4N7!ROaDRdH{e#t58aSt_6qEk96%}rFoACb4!Qd9}=QwaR!NP<t0uy;;!!MB%*Jq5jHMz>nj!{w}lPN}rnYSo?}Q_QGU1fT-vWxIJk(PSVfB#`^IV!*ymAPw-1(A@2zOx;CCK$mPnOR2459N_)B#vElhk%Zk-Ezm8c98lM}fv6)z8HI%@(by9_GDb&WCydB4>sysOl3<EmJqoZ@28-G8KG4Ujy_ZNND!+zu5(=seia!Y68BP_sG++l~AcQUTKmwA{aAq1aVrL|lxjIyu44E}gdCm=n=B;Be@+~{~>Ji(O9HA2|B)u<LV`N&HZ#S`_E21~7#Z+R>*EUx~@rq-}G7Myy^9&KpHU=UO3SEPLzbBbvWhpf8zK1OMML#EYZk2CVyxtHoDyrF#P~E~4+iv<0CK|=7vN&;fdWXI0bJE>}a9X5qtUGx?phL2xcP_S2p>-5<K_f&|%(^Va3A1YYI8Q)vpn0*Mt_u5(S}@D}&E=!Fr1j@@_wzh|V0g#1)8}AeG57>boGMr~lM+Ao1X2Qt$=F{PWktN~1)rXuCZ)1cj3-ZJuq|rIf{URTYC9H3)!b8R<Ylr=g)79SPf#cql0BLM3k0NSy7OqCNi~&@)dv<0I38cb@lipE8pIcC9cw5`Ae;w?>)h0`Kx)Ez>5POc4p_r{D+=4JL`Epgof0djwcV8JaqTF?T*`-VDwV?S1#SR<6qYrm^CwkvPr&aezpSll_cxJ-GD}3>7t|}|pU{)d&Ejy9N^%kGIm&}8&`e6WVMd++z(CTRS*f|tsRU2Ul4ivqfT_fOF&phbmzYCywlBp?F$<n2-_A~eS-L`!iJneFvh0xyyB`%L(YGjGC}pKMn5yEmFvW=a95yK+a$*Flu%*?Yucc*&J|Y?9e301}whP3DLKXp)3(QrD!(mDxtpJ~t#q#g;ND5Cqq6f*rt^MAQ9cikPBaBuqV~gg;kqou=(FgK5#B2!ka`L&2717ShJxNYvayHSzwcE@VV2F`6cpC-A6^qLWX*g9KRcZcpvxa8X1pKAiyab`nB6kd!&(cUK_j_h~1avyA*Ggk*Qn({E3G6OSZEIQ+qygg2Y3E8eEGL}OObu3A(1K7xYRa1eXcPOB;oh;ls+?|Te8uOKLHp;VJb`SA&PqKq<w&IEi172OAHC;gq^2~Ax13*`D8HpkF%1r#y)J6C%n=XGSKnZs5({uwDl}WZWTHa2c6H{<KJ-W)(4BeWG!BeSr9yVZTA|;ZRmDZmhKz&C8JAfttSyNi4k!EO`sO1@8Qm)6zQB-6bDuPWtE<Ed$)}FDDAYEjl_n~Dg4Dc8nlQjWw|E@W1W?>T$Luap^Ugb=`iRHWD!&B&G{ig22!gdi47c4JFNK=1>?(`F!VqqRO1}O{6^pkein;igvv)~C=4=dxOr}IGr08u$twN2jVo3sqB9g(5qTW4nunZ#B20B5PqXKp`)IZ9J9Vt1yF_Gvn`MH(KIo?XnOE}dLzh7HzlBq|vUFD?Cpg+@=aJrobP4i^eAn2Qv$csG?uws+sQTTOcg^~7RW3awJh2$}yw@a>E$S3zhD}nS9_e3)i_Dp#>QJtGze{#(L3+iq2fzsffCfYtCFrPyzQ|IA+sjco4rLzZv!6(1zQG0j_`5>Z5k@F5l)-TTMv)vDK6OX<iC=VgneA*ufz^!U9=fU81sDNA>e2j5_N9@3^+SE?s<51lRR&SWE3e!rhb*R`!u$>&9>qYD9gNEoOoA@_lT3@GfPK>d}3pi0JPttw@GL|<<tE3F=DUA9hWT5f4AIUE-pkkDu(;H`>Fr2iZz7)5*5~+jyLAAn3r9A1NAsb0Ynni4ivQXStQ#v$!dr#|Pu7nFS1P)8H-gV&3;GyMKSCt?s<wvW!CqC=e@{aLJG6z!Vru_8f>iWZP4|dYs7oVgiCbf|cARUMH0|#X}U0=T6>};vDu9tOTKnM17q2)PFEM?<)>|V)E9&!)Ez<2-*lUa(G>yt7xft9<AtQ4LYjsBNIPn8Pr%S2cqaOtBW0b)h8gf>(n@dlobhxHzXf&k>R-v-2DGI;?(*N(i*SFzy>*M(ok4?FVYDu{~>&dMXeYwIv)An!4f=F65k=as*fpfXjC3`z}gPj-vznRO`|7661%oeB#M*>-v@?~{~jvrY9hAdb8xJ5VbjmloSvpIeY`x%v*scTF_8b^oN(6ynjydE=N-oH*g*OPxxM5&57bsMJLcra(|*1;rxDSwVfL&NtJGQtQ&#eo{)x;bSF8!<z4cPDN=Kag$k5yOQ9Rwv7Y^%nwNh6<A0fTDLT5<^}5#=1O&*26-+yWmC##N>oT~tFEjeqS?|do;Q$dNTt|hP!CDcj?L8gAz6n(14zZL%K8K2mtTPS>_fH+64eBGS}<LQEX$K%8I_y<>9C7*-x7E`Eo&yHHyt^L%M$qrUyg!?yXgAnwihCE8C55GQxR9NVgBVa9_vxbRU!f3A{f*13TARnit`DS&BMx8{({VEN^5f6r8SsxEkQd@QMlaGy8b7~e4EKZe_eIZ;nObE^4u|9{-kA|n2|^R(#i3+#+6tUN+J<ZMn4~xZ>F%6TDUW!1<q583Jte@H&Pq{ea*yaPglK)4td@>S1n@3p-%X`5uHGhX`><dkd-R&*{c+S;+9M$Nn&oq#$^{o201vq!f<}TP3==5833_~VWI)WcD50qD+tiSR+4{DmVYMHrLMJyB_F@Q>enl37=*Bb@rGe>dcG(*Tk<}$>!K!NMI}`%5sZSLh7v=Q*#zoPehu0w6PBP{K03wPqBb7CS4tjYLbiPiQh!q7{y6w97EV{smqk5%L{18t(hF8DVy}Q7kYmLcZJ(;dlqXpM@s+rXX0);6sCWw5^Z^T?0E~5%Fq}M6qoS24ze<si*wOnI)hiPKU;=PUB4IWSE8507PQ~Qq1wxob?bvxra-^6t@AOMW*p1P_f{~?CSJXN3fV~v8H>d8U>uUuMVh15-_~miOl|4+KWVpT;<guxOo)0gsixu@~>Tj<EGBF#>BLImqQFCXEQI9|~8kzi8PnblidQZQtsTZ9%VFVMHqFkzIE=9g}B2R=ZhUnUtG_R;8bQ-A93hr^tk#G(cTA{7BN_$+pTlpLntuFAR!UgGD^ch93t&kC-oiXX?0x<WON=}HlZF(r<N@`BAzOq`!kcscMBrKwh#L^-nLsiTbXkq=KPyR{{Rg|+z)iU2t^fAL^#NN3k(^Tu&NeiK(A*)BL)9H#+2Vx#M-%`Om0YI7Igaw%}W8?YVeL_)R!q;l-N{GZxJhWnoca*Ma1ZybB%Xe$4S%GG})G$Si%d7K}6jed%&Hx{Wd9o>Z)DB`|m{0Q5OHZ~1$Wx!YnO%uu3!<Ej9TdRyBGW{A&YNB=G$^%~VZ%KMR%r6pORmE+D(Lqt*vHK3;*ApG=bl)f!n9hKD-!kQQHioTwCGw>V<q;5$eR*d>0a=sBt)?kDow>)r9_G5-%?lF*$N^pIwdNuu^1sJed$k}k)!9qGFFTf@$3N6RWeVI=vQR)s7fjQp*zND;jAUGN?bppSw2}&AlbQ-N3%#uRi?5jR;)l4Zwi~QTo_K+0CC+LMS)y#5b8S{Vy1NM=c?VQXI|@eCMgqgVL|4oGXjyXkJ^K=#uH`}u>wE)5%-}IJCHE7K*S=@X(k&yhuzRsPH;bwLdGiA6_V5v^eT!)$~6T85=!fag$GYSY0Z{)Ru~%$%E}`y^;3vZi6r?ls+yNWXN(|6BXJ0{HWH|z{c>je_;oc#N>;;1X4Q0Q-FzQrK!z>=GW5zIL$ALlIp&upibGj3lz-YqCPyX7NG0DGlja#@bF`r~l*d!ZvuP?il0_xeOn%||IyC=_g$V_E=0->jqS>Ev)SFCKYgAq^v{(X082$#l;r@YoALGn1cn!+d06Lvm$fufel}!{_)|FLQ2wZk&Xw7z!+*j-tRrO$<3nf-7d@@B5NGVt)Y6PiT&y7h#O0`ndtoWj`YFxaCNiy;rxp;ZdRiaC>wI7P2D595=lsGK+O{&TTuKuy%l-mQj6fz-~g~cQohASfcK`xe2wk>A9M&^+pxM7R~UK1)21YoQmg4NQHCOnlC!cuEH!&}>U2=;JQ>O58HO5`OuZ3H57bWAPEA3KD;Bxo5$cnpGQoZjW{1~&FNJt^hG^x0hnlvY?k35>#Pkn;2$fICfzPUragkn)<=30arM#3mt_$@wlK=o5R?Bt=5@C@Lkf+SH7e<$Qy5Wh`C%xJyU4?4$skX#z!5WTIQeCn*=GUM`s4ueltY^fr)$(jxQ~_!eaW?ZOU->L}^7ZmI5#4owm`Ox(2;b!TO9I)=3Ut*NS^ZD(A-DRF_6>P-Z(wr1n-VnJkMA~%VIJ9-f@BuqIb@#t%z0uKr$zI7H!o7#8qBF?F0QGlX;y|spI_9&n#ZpnF1Br8Q1=xuDXXEKJvGH6VV(Nm3ys=&OfR)O*O09K#Z79vxV!B{`^=CK;xOvo$L*<d&9MZ&Xp%TW&^E+IH&d(;S=)TBsQ7Ll^O#%}m|XO~z?bs~*yg%tod<oq?w8ZsgwFEg9S!$rzXi>wb=Xc2||(9siAX`~621z<jwEMT6kqEOsl&6Kk#`HkZ{EPd*yP)}TqF{xZ_PF~d;oh(45XEN~Bl_K0FgbVfbbLJDo%a^IpDssR<ibjG;O*!h67R4N}z7wc$ymG!J_klLE%4D*Y6RTX+97ru4Q_1lv`HZ$f!1RPdjB=e=QrfprDpC=-*rqDk)Qa>r+<+9A&{9Wv8RRs{7(O{H3B1uXA2LIiYZxavw3Q=cp+yoyCI!U(sybvFyj8b>;*5eC!dihJURB4bOl`dky~+ISfhYj0d=p>$DbJ)SqWq%~LL;Wv60?P0Q}?w|b^`i}xeD>bY^3oY-Ubyw)wIBfO;f2#$i>E3L*ik}#@wlS$Gu)=fyTo^E1w6v?NnNI+xUo<q$q)yk&2_~=<55p5t2jvX%OC7!J^((WO!EVG(_2@lsD?14fREoNNtVUo@kWyOa<>z(0Wz#15!;B0%`mtmrm8<#;cGlRr+Ug<d~{nFc^%TQ49UTWgq#9kqbqCLw}rFaOmU_6bazBbYL1d=2WGC73?_pD;gvnM>BTd{Kb8((VV3hq9iDT@v(=MPMoLu07eqHh2+EZ+Z3k05IC&6#Q3*DHxkW)POe)fm3Cs4>4aTlrt<Amv#5im^r5X+>kC!-v2XbU*vq)NZys88|NntQ0?7'
)))

__version__ = "mapleleaf-6.1-v27-route-plus-floor-guard-fix"

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
