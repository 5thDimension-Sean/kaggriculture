"""MapleLeaf 6.5 -- Filip Strzalka route swap for Kaggriculture.

6.4 (Nikita Lugovoy 8C/4S route + widened premium market-lead) was
submitted and started climbing the real ladder (2645 shortly after
submission). A forensic pass on 6.4's first real losses -- all three of
them, HealthStone/cf696666/Efnutrrionpy, essentially the entire loss
population at that point -- found real signal:

  - vs HealthStone: WOOL revenue alone was a $9,669 deficit (us $18,216 vs
    their $27,885) against a final margin of only -$3,092 -- i.e. without
    the WOOL gap this game was a clear win. HealthStone ran 16 animals to
    our 12 on the SAME hand count (10=10): more output per hand, not more
    hands.
  - vs cf696666/Efnutrrionpy (same opponent script both times, identical
    sell quantities in both games): we actually out-SOLD them in revenue
    (133,801 vs 116,493; 155,367 vs 137,242) yet still lost on final
    money -- the deficit is in spending/timing, not production, and
    wasn't cleanly reconstructable from observed prices (large multi-unit
    sells shift price mid-batch, so a step-start price times full
    quantity over/under-estimates real revenue). Recorded as a real but
    imprecisely-quantified signal, not chased further.

Given 6.4's own docstring already proved "add more animals" is a net
loss once bolted onto an existing route (Fibonacci-scaled daily re-hire
cost), the HealthStone gap pointed at needing a *different route*, not a
patch on top of this one -- so this session surveyed the current
leaderboard directly for a stronger backbone, checking self-consistency
(majority-vote reconstruction only works on players who play the same way
every game) before trusting anyone:

  - カワシギ (#1, 3198): 62.7%/38.6% self-consistency -- too adaptive to
    reconstruct, ruled out immediately.
  - researchstudio.site (#2, 3161): 48.0%/48.0% -- same, ruled out.
  - Filip Strzalka (#3, 3154): 98.7%/99.3% across 10 real games (6 P0, 4
    P1) -- higher than Kaito's or Syed's own consistency in earlier
    versions. Majority-vote reconstructed and independently benchmarked
    with this project's own benchmark.py before adopting anything:
      - vs the actual shipped 6.4: 18/20 wins, +1,692/game.
      - vs main_inspo (5.9): 10/10, +29,448/game (6.4 itself: +29,788,
        i.e. statistically tied, not worse).
      - vs models/5_6.py: 10/10, +33,774/game (6.4: +34,428, tied).
      - vs models/4_5.py: 10/10, +17,084/game (6.4: +17,542, tied).
    Net effect: a real, validated win against the thing that actually
    matters (the previous shipped version), with no regression anywhere
    else tested.

Tried and rejected before finalizing: pooling Filip's games together with
9 freshly-mined real Nikita Lugovoy games (99.7%/99.7% self-consistency,
also excellent) into a combined majority-vote route, on the theory that
combining two strong, high-consistency players might beat either alone.
It did not -- the pooled route lost to pure Filip 0/20 (-877/game),
though it still beat 6.4 (9/10, +904/game). This matches the same lesson
from 6.3's own history (pooling in Erfan Eshratifar regressed the
Kaito+Syed pool): pooling a real but *weaker* source dilutes a stronger
one rather than improving it. Nikita's route, while excellent by
self-consistency, loses to Filip's in their own head-to-head real game on
the ladder -- the pooled vote pulls back toward the weaker source.

Also checked (not adopted, needs real route-design work rather than
mining): カワシギ and researchstudio.site's *actual play*, since their low
self-consistency ruled out reconstructing their scripts but not learning
from their strategy. Both currently sell roughly 2.5x our WHEAT volume
(~1,200-1,265 vs Filip's ~479) while running with far fewer hands than we
do (8 and 4 respectively, vs our ~10-14) -- i.e. meaningfully more output
per hand rather than more hands (which would cost more anyway, given
Fibonacci-scaled daily re-hire pricing). This is a real, well-evidenced
lead for a future version, but building a competing hand-labor schedule
from scratch is a different, larger undertaking than adopting an
existing high-consistency player's route, and was not attempted here.

Everything else (weed repair, the repay/front-run state machine, the
widened 9-item `_FR_ITEMS` from 6.4) is unchanged; only `_ACTIONS` (now
Filip Strzalka's route, used for both seats -- his P0 and P1 routes
differ by only a handful of steps, matching the same near-symmetry seen
in every majority-vote route this project has built) was swapped.
"""
import base64
import copy
import json
import os
import sys
import zlib

# __file__ is NOT guaranteed to be defined here: Kaggle's actual grading
# harness (kaggle_environments/agent.py's get_last_callable) execs a
# submitted file's source into a bare `{}` globals dict with no __file__ key
# at all -- confirmed by reproducing the exact "Validation Episode failed"
# failure locally via `kaggle_environments.make(...).run(["main.py", ...])`
# (the real file-path-loading code path; every earlier local test in this
# project's history called an already-imported agent function directly,
# which never exercises this and never showed the bug). This bare
# `sys.path.insert(..., __file__)` line, unconditionally evaluated at
# module scope, was therefore a hard NameError crash on Kaggle's real
# servers regardless of single- vs. multi-file structure -- the actual root
# cause behind 6.6/6.7's first three submission attempts all coming back
# "Validation Episode failed" (two earlier, now-abandoned theories -- a bad
# live-engine import, and a multi-file sibling-import problem -- were both
# real cleanups but neither was sufficient on its own). Guarded so this
# never crashes regardless of how the file is loaded; local dev tools
# (benchmark.py/evolve.py/build_agent.py) always set __file__ explicitly
# before exec'ing main.py, so `import overlays` still resolves normally
# there. The actual Kaggle submission artifact is built by
# make_submission.py, which replaces `import overlays` with an inlined
# in-memory module and needs no sys.path change at all.
if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base64 as _sub_b64, types as _sub_types, zlib as _sub_zlib
_OVERLAYS_SRC = _sub_zlib.decompress(_sub_b64.b85decode('c-qxHX>;SYlHc_!xOyKVP9#~<oN-2}ay*(DSA4ClNjA@=<<Jsjb4`&7N%_ds{P*nx00AD7JV&bD)T<YhY&05;Mqg+^&1N&c6-nqnq}}C%)9E-zesUwSP7q}x41+5XO@*UCoJ8CPw_@hZlXwA;%TOE&f9|~KK5ewFg3Ou5iv|4W`TWIC)1L-z+gZj*2Jl(zB&*1YBlv6S#B=BF+Rp@FbuRts&1D=3Cy7^?08B3${w!W*Y1erpLV=C%uH#Uoekhy(+Fv8kGoa)y37|pDulzJ!EtXjzA0u(c2ph9t7X6UH3#8&&EPjSRvEM{=GLa&B|H==dG_%_|t0)UXCyMX7jm9YtA`*Vmfwq@^7A%}r>Mw+oW-yM<!k=CTk=U7Di|NfW2HthTczOe0lhrg^B}gCQZ^TJ(6-0iBjE3hFJ|sA-ED5H7sO|V+BK+Ay=hhE{nUB3L#Pr&af^?C>*N6tu2;)1Ty^{p#jdSNeAbS`7ji3QK*(&lcky$CezY$`I?}Nk%<Evomh<ksUg%3bc138$9h|tCnyc74CNPxWHZ^Gs59UgY}_fF4YUV%e?l%;Oh8379(bT2nieAx&=C{moAH>0<E9}dUf>E7Ai(fQBL)DJ^!JP)pb3$3M}_>0tq&OoS^Fbm5ho{BWxxdL8xfUnc*#-*6Yz>^j52FPFHJ02IHZ>2(D&p~wMrAskIk==2`Z5-YT_#24ZbDG>qvjHqz;V}FRCL21Mt)Qy{h2|F!;vZ5+&(Ni~_HTnYX()!Z762HMAR_@NdA>6X=5vvVC@ToE3t}?@sZdMDnXjTLiD!U}nu(==|BDdsEJ%@)9b)GtJSV{|;t#UaxdIVrDCQ$Sd?$rgAZwx165XpVwuWz0l)-xh_zC{C9YK==>ooMQ@a<baOoa<l*H|D!5k1bYxQEvGppgQ<Q3RA6;xqsj;DUF0HX0qBj=iJ3|MB(@PmV|4n}hT5-tqnjrocNJ9q#?9-yje#Rv0ZX`2WN-1Kz?@7AFtgMzh&$G=c>x2N2xsy3zO-u6&1I(MpAe3(`amupJ1S1&N?(Ak~A!<Dv!e5;JIg<6m8c!V}SLki^jfMg#rAg!os&X?>(76(C)BNW1s}mftGGg$lSNUDj({zt9vULws~;9&Y1+)}jN8bJm&0OPaWO#sYWkBUMXOm+>kEs;^KokX|8$7+Rvjlq_L224hAA3Z#J~j{y(hNLQDOAWcznT1`{qzG%9zyg&t^;5p|S>>M=GD(#NW&Q8vp9l+51oplMK7%hVo*y+su02tR)+7sqFbV7eNgC*G-^ad|Fy;q&V00qVowA_~oE`@(N@Q|{S^)snSvv>u15A<k+ij4FJ$londjw=S3mw}RnQFRj3staUtuHWXsQ>EE}0e7q^Ss$S~meT>!1Y_<xXToRsg}!1y^s#ncU&H_Z!vFt~r3NG>fWiCB)QpusuH7I7On$hC!3<1Al7T^h-d9n&TCzayT%tY)cp&39>JY>k)WQnJdX@MyT0<~~%lIBJwIt06C}|KO<UA^GLs=-<1kC{2q77PyR(3e=a8p1sjluj9ukV74RG>pMfvlBklV$-3Q5uODNF#D_+9JS`UB|1dYtSW<k16pRhv9>9OBOiqF=%OLCT`V=>N>Yi(b5Y9M_C6vO3DM^L9UNTWr2(UXfVf5mk(eKL0xq457V;Zx>D=a>35$Fx-T7GPeA|C-q~*>rIL5f-=CbG@9^UHK<=hu=k)9Vl*-$~lan))XbFGN10@Zn5GhDwb^~ZSSuR<}rb@=qMk&7kkP<yCtSQQ;l+3R4(WAjUc#?Pz+sUQhaz7$0V!Mp93?wR^6ORLAE1O&&EX?nnljFlbr9L2^z-ci}Q)Ym#rh_IPX$CZs1X^_HECr|=BakpO)^ng07Rf`Urdush21OUu=<wV918iey<;kXkGnS;pY!EhhnZ~OGox`~UZccXHCc#)ONDK;Ay8DeOYZT1*(D~GG;2-JSMX*{(<IxGhis3uK&LIIcC5)F|!vuNKRyKDX`LEyYwW|O@e3L8(1HeHYV7xTpoENXE0q2QN+Cc*kYPtsF?vZ<>AfML21(7#jp~dq4${qlCPze?<mmb-7FS`aM1^zV-|Cxkc1W6Jn)Ti<;%+cVWC9^@BftL*4BKp&y%eXzh_2{|4+nlimi0T6S1330y5V`hAhM<W-v}OUa3RG2#d>ElU3uQ#z5^kLRob;#dN&xR#__wg$qX4uaK))!1*)u<Q`Kk)Uobwki2AWBv!oU-YVXa@S{A8wP1YUde+F%p0NH&bg_`o^>A8iUYD_MrC6s<(a7;qNxsVu<;r!`PXdY$JLFa^PNUiO|Bfk+O$sh>l>DublL7VciRgolT2LiM`+5)|m2rA_;bUWslLd$iTzgNcv&l)MDhwIH`X4E|b4Z-|koFJ2lOYy4$TiGlup4O3@)f2DCF37s^I!HW3N4H{x}0Dz26I)zZi1^;*^7HB|M3C7b8&YcLZt~17uZ6x;rMOu^vg5l<#A1<$b8rT3v_8Havd&4f*xw$*&4((X}to;NEn!FZmpp}=$hPurWT!NaNtZ2bQRQ@b`dw^*cPtoxKMo4$o@h>3`!Z-qg`3E+bWGl7v+y-w1z!*Q<#%?3G^FycKgMSUf5x{qihUGeFGtm6w{b+Bj1m;r{<q@BNZBFx`2Y+hR@B#s!_3$rpCp-+*;8ipI3#J-%k$ewRe<d>F|0{&1L1}1+t_fJZH=qZ-&vGL7_rNVzgynQSt*7gGnJ#pH1@={>3k0T2S3ZgoT`x6V<CCMk@kxoU7ri>V2E9kn)$2Zc6kRVgUFYMoy+3}1Smsaopy@)pTSHg>ar5}HVjcs`^EBHfy7~rPM<a-UOY${%UQ5^03c7NMDbY2k;uiy#=z40<HG20h*WdX(uA%Gc;49~GE4e>9IQ&f$md|6oeDw!|$IRo4FPz6ePEHQXbg^*P$k+4lH;*~L-j2@32Zsm$9-Uco-+R=0%sH^tJl63Gp+A$kp~x&(vcK;AHll^8{#}s#wUzpv$ibW*{QKW~9yXS+7c38Lt#?XIem(ney#L-iKUK=IfVyp|2G#1%y|ZKQe0*{?(jCzRtM6z#_RmIpM~avW6HD9CWEJQKM(^*v9qEx?C_Szq&W}z`#_tbCdXSZf74+M^v!l`3xyN%zWav>z#1?Dpk&@Y$Yt%`X!Hq~cpL!2bTAISs7>zPdCkFcWJ7XCqqmjOeglIc|t^8R6PSBL&P9KxVY@>s$>&#nY7s55CkAWOT`<TW?hXBItk1QA;orUlt&edQhoa10H`Do-hXOv$1O9)E6_Xo%CM&7%<gJY1LSKVHt(U^(3<I(pP%3s^LZ#(1RaU2PEmzZ=9pb!wWdf)>&_w3mRbIPJ3WlCCiA?^SV1_oJzfOW?6r68Oql~B^Llu($B?BdH-Rj07fcbx(-yljEtb$)cJTl8_c7F+at^=)`+nGNzA`bJ~S6^xzNL#LO2GsmZ2u7G#<;B<}~1&|eVXwJryoW(1rgYJXtJbB^_8WvifEi)g}3No>1gKXV`ZwG-_oAU#yIf2b)^DTuue&!fnTi5wrZJ==eW1c4<bv_70Xt4_YE~beQ*AfOK_YRN=me1#2ATbkyLp2GY%L`VR{F1y!cm-;cUyS*AEFXcrdLYhg0MEHQm&kIhI?>-CEHS@IZ8-s+5*0gIyg{(xf39xG;oy+Lek43k3}7I)V{%ru6k#e#gc%CFf-p;sKbEjgiLjhW9S6;hY^eqNzGX}^f@iHHUPZGO;dNbCE&Fx(H7z@pNi<Mv8`5Yxk4JdUR#BcpYkgckWY=-@)agu}rfMfQHh<QCb=T6@{K%u;Dj$crQyDpN$dhjsT>EMC0|$Wl&Op~W_vh3K)AKv&O|abMJUFM=(^4K2qA9^)thir>!8E`P5}2s?M$FohS3bsBl=l|%Ic7^>$?@oQ%9sN;z1$wLU9xGjgqa0a31H-_t`XG@b3djE(u($mrW#p;SA~K@TTir|RwZD&piZhVOTTC6&>zerkT_I4XkaY_#v(<K=$7^^VZERao)3Lz#~HLuFE0P|#QFk{&s|&L7pSY&%w)i8J^?TChlX7HuwJcF0BiS6W!$WNw@TS(qSP*Pw~5Q%v%_|C9yz$rrNAo&^wx8O94tV0^5(<-7(erjc;}<T!@XY*NAM<FEkn`r3bTsamq!O5j?j`6eKU&XOz#hUMruOcc)$MX?HwN+?H!`)+uT3-1Kni>eExnkLYI$Q!Hah%C+FxYlEeDB;k`TjF!uf!9lU!#&Ru6KuEnHp9#TR$*VX|Of09uO1PE4`*Y7@W8=-r@`?PIj82a2)CPMODk`-FeYanv}j6M6-)}E-Q7#PLe;r7TL%@)lL0D`u_%nxTH@3({FHw=8bcaCqUyA$x70qnm&?7cbLJ03H@F(Er9h;v3v$Z!*SZy!8;1nWO-cxpdj|K#}X!MhJ<d*g$XW125CPwA;h-uRRce+D?R_%1rXj+f^m3=eP@=#~<{>eIf!cZH9GXXJPvvi2ocq(#LEyxo!4IJoZ54rK{bR=uR}rJDox&j%fuf>V47#La?f*0Ogpl$9*iOlZq^N)-{bfj0$vLc6H>{*05tnyo66Ky5_6Iy@7qy!-?rfxC#bzT0*7v0|fGpW(=&47JgS<r?IsNlajfb6UVk16TZ|E>}TJ9U*s~&&PY?5sf^RQHd-yAXKykng|>OMjM$}4u?J7+~bsCDlH@xmRySLPKZd7lf|(%VOL>%2_B_)N>BC7=C9q=5-B%a%uk=?H=@P!Ie!iy+KVZD*wuC+6@I3)e&5jD-q8VW%6r6u3xt}Ggob{KiD!Wc^-dpzki4A~Bmd8Bj3IF68J^I){+wewe}C|HY$2=0Hd~3}Godz6arMS#R5gTAbxCbcJ)@(O)6<jV(ec<D|9P6Tpt*`}B3O9M#<$<W+()^MFTwc|;S%>RTfDu6<t0G`D+6nOK>R^!Z^SZ_yWvXWWB~)XYk(?>rMuIKlbPONri6YRDRk~P-|8fB10TLc1x;-r6T$+iNz8}~1DTYJGpt?(j8boip!C-1V;6Cn$XMjzE$WdW{^4g?qA)cvjA)Y(>X;Q*A?{YRxKX(yeqYf`{@v`uhLb}_1?uspPK*B|`{4(*wB?hrcx4}-G*QjDpDYAs4Z<K*Er<>3i;L|q&@P=fCvH1$iLQG}nH_4%0${?@%IDX(^iAB{mQhdKiGh`UEX)AqSl3~a@C8(#bwUN!QwwBW@<)!p&mnHsA|Zm$Fqcd4@&qRPdW5Sd(>)kvIyygtJYjf5tP~u)Oo8V_uz``@141B6QfJaYU*&oSYDh!Ac0v)g=!?ref67M!W)<cfZBHu={#GJ>?S~lp;v4dyt!Zx2*Ny|4NBxDKF8*D9lf&6Ct|mclE(0A%43E+hKcpOpG1!z(fcC0y(IO5VllA-(SOs#*;wph<f2ewIb~!b}ar7<E5lhBR+o70(gr4w9jDQ;{H4(dA^z+k}%U!4tJ`nZ{<_HXk@?0+Cl(yip@dY)+p||z2f(Afv57v$IBu6e`coCR5Ib{J}N+wq~;jLJdZDU1B%xjhxyCgwa7^5VEK9q;XqJ|S?N*>B5H6Yl2&&@+W(EImolX#pG5v_n;^ajjPxmGHVS~|ZBN%%EKsRQeiF%yOG4_reC-B%({+(;~#_E88g2-&2VL^KS90tN9$F10yua)}a?HWwD^U;_ofiU;T&WmPr1AUUw!^e3)KPYYYQOje|306NDPtsW*iAEb_ubAaw7y}vi#Up!3QO&rQ|SC3d*#tcYqRxT<z8dDUIP~#a`L5bZrXSg|FQ3@^uawjF`Ng5S;4Jg9x@Sh&;?T?!D6}e+TxF}VHNu=z>(8AN7SP;lw45%fSFYfKnd2zcD78?<rj*N|WIyk0q?=vl6B*e8zo12yMFdRc{ks9gNaC`yJtOssjlA2`5?8YchIg~8(DM(DE)DRDnhcaX${#x<b0hW1_hXYV7K!4Q)JY_4_xA2MkDY~7l@xxM#&@pX0zoRome{V~rAx15k+F1lqONzNB*EO=Zn)T=dxNh4NH#5~-*{8~W(MA${%N}UeNGb~36LGvyn>lUV!UWTst`;qA@4Dptfxx@A6!?pH6=m2o9}03?cgYL4O+AzZh+CKWr@Q5S1Js$C5R)a8nnx6-kD)=oL!ff9T!L#215SfQ5c&y@a0m0caf&56-zBP0s+s+7DQ%X>%YnB@RU%NX*ZC2Yy4<0Vf_#9gQcChBp;p*2TI}?-$G==%hQZXMgA`sGTtz-EW-{U05yZ;g3j1DmGo+V+!78?ZsNHJ7U%=+`mS~i1bbK_^DqSEo7FT*Ax@{K^*F>{c-kubnl}RS*%YEj40!ZbB>H)WOj6|4wv1>eW=Tj8ml#HHufJmH;oS@a(dcs*haH&)R5C1Hr=`e*j8og;sWA_k<aJD@{*$RP@_>O?qJ7aeCoD2{&qPA9a3vb#q`7(02fESb9q7Eo{JcjAmQm;;v7&p_vp0sicf-ljQHC?y6S}q~HE$A(>Fr{YF@T_Tw2CUSKtlFAJ7=<I1z$TvUs-fZg3j~`uKMo59D4*6G!qB!kB?RQ5QA>@$v8;G`_?zir!1WXvFkeFxaTX{lN_Q=7*r0+kg$lhbS{Ahk__KkcoQ$}OA(&4vsesM`FMT67AXOH8Mr+x3UcYt%Ru*k1!gD`Xz>(+8$^B3O5{Zdd>k>>mObH{MSVZt#&*1ARzk+XO&VmO>jU}%ptOdS6shD_q#u2Za`we)@*$-tXbV)e`aB~Q35-he=#x2fhZT1IU+*<Q5Q!;G`c%f$m)KP~wu(752-ZhZG)V?Gn1_m{0fZ=~l4EcMvdkJ14u}-e!a0w(Xl`&&H`6QvWr4JI5`9&*Na55==!~*0i+WgX1A(zk?x)|V?5m>(sm&l<d`dQ)fBHoR`#0)0*N<WxkPKc0T1=$8o$iYtRcN=_1u6>5?dfiu~FNk(%-;?R5?%=rw)|{5Dp3q{zS@U6vF4=neZRZjP|97x#so}_(3a9WiwRtNAxX4)jIuG)}nj>!4UTV}0;Wgt<O=$}UK;{Yug-bh}qCCm$+EXgBaq=P95``u3Ta1zhB3H~rN_hUlwQ_HSTPIUPa5D1+k|zrvnb(scj?CU!83L7d>|rg@PbMW*OLU#Hm$I|D9)uiFIl5T-(4KOejR8{5acJb|YLa+;j88D%sp={S5xP9+rC~W_&+^&y-t&LBuVa`}v-WNt#{Oe1?iaaDh9jeyj@ref>z88fn>j_f`(iX{6k@;GYD!X2+S?~0xA53XL@T6UPPfERNxED)3O3&p0cGXkNpYZwB@7)C_6!Q9uJ@lUm!{99&S;fda>i)W+#wERP`SOOg9`~7%)V7+nK0jWJm!4cMp3Wty3lPwX?y1%PEQa2^xm8u{60F%3rJ*rh&fQqz`1#~i1~?Aac<S2ikw>GwQJO)<N&hXgG!JK`c@vkN~eA(SdCI}%cEs6#Z_kwrjYytE=#~5rCr9dMd|j|Xz~S?9SsXhqqv6!{v&^JRSiUtr0ZH~Yfxwj)KZ6bIj$rWeam33u>Ybw8%4iSGD#{H^IKHtBOB~UrHdUHb(1rZiD{PeJbPG5UgMs7z6p#^&VLQdCV36>@FbnisR)_csAfZ5iUoSkvAnjruiN&w4qi6&V$0F|GIXA8fd;%EkA3uJMX_vMGt@{kKbc|GfenMpthbw&CBXQNr_bLZ`FAFk{sVA+b_Md!l?vc`%bFQk5W}y(Pa;sB-1cTG(c(?!woLFQ0t*|0=t>G0_+Xd?o8(5tC!@lxjA(;4u%$l<FxJ+OMoNoAZCJ?dZ_1R@l{EOQHaF1AY8tQm^qO3<MqO^+NEvXW!K7fn6ERz<Dgs=Fy0tm*8vLDM-n;;!Mpp|$JWz<rCH=L=Pz}Qw=IwKqud=Sc#F`YzN>kgwN4s<>n0t}9^Q4TmsEUbIN!!8G@(-~5r*y2^)+`jMVU-g;ye8&STQ+@p$q;8j^KlUn&~4$CJ|KO&Fd9$DeH2S`1O)UQ*4`1-19jvDANKtL4jvHy=1Wc$g6+Q_?f-Uqav-Z6@le)F-Xn1vR<W2=NRKQPYgf2A{YPW@+%PN6>M5x$Gpit@|2PcV-;g&GaK&BG^i^9nC3e+PUr~}L*FdF<SojzEi_4i`91Aa@wLF!@g_ZSyEav8l!yvOlV%YD5?{WuSE+X0Qq_Fbx4;R>ILQYRP8Gy=&y$|p7qVgsPdlTOe!`5_J(LHAn>xeHn|7!g+laMyVTfms_6IN*jSvDl^>DXF4Dyk@JWu*lA2vONyZfaM7HS97mk_QQT5}tM4hgrK+bQV!|aHgxTM46OaTR*pDdSz8}JwIG!83;W*wh!p2;$xvkW^I$#g%*YcX;7LQ^@=14nfdASn(^pz!m5fx4l&p!49n$%g~GhXnoV*nEwKmJELLmfL(@I3@z5%^#?@B3tVvMhO&oP3r15B;+5A!!f_&8s-d>S<u&mS_c$}(J-o$mB1b?IG(eRY)&F-a*2S-;zXpx!eGAJ8kdFxnHm##wO)2Gix$FzXr0+3HCC(RN;>>It-+#7|bvM-7+!4nN49$V2BMWQYkhFvy%L7nqUS!iI)Aif_I61dz<@_fU}ZabA6+q}|s<y9Gm?>w2HX^>7|6-*2Q<gU{fY)nv=Ys~mIR(!p#DXyz^<WK~UbmVqt*DSfZ3V<;lO)Do1>HJVde5nI+zA<rFmxiuK&PSHy?jBi8v$u8sI9fKk=cEeB)i1+}d8)ekDG%UL0Bq{kPUxf5p<Gn_iKy%M)?v@1sNvdT+)aV#R*QMJI)F3QuDM3l=i*A{O6pG4de#NOQ>shl{7SydA{l0s?zZI(QK?lZtOqMKCMme5Z9Fk(o-|>-O#2#-)6h!r++yJ<<JqvaM<T`r%(<b>lE4o=TUMkH6kyC5Co@?Qf}1-pb&{HM053ta=Z@dom0r~~0|tgFg;%&~ZL(zmPd8(!lh)GFwvH-tS(-Y*Uf5SzC3t&evArze23b)qff`h4gT+Gdn$(&;i@9w@BpoQ1`I1r-vr5CB)GD5rUFV#o<!^L`p*#`#YP?AWKBT8_o<=vO^-0CF>g&UB&D!Wn+?1SnEfXSCk!%QiNylv{G|gM8EY1ZhCpD|wUqL1cT-H^MkD3V3S&ZDqE!VTg$uOpBkPwCQ$r~MM8`APmO+H-g_Ir~@y7{(8*;W)*-I!q+8{516);XrPg^LoueM*Us@D(yjgZ>M!4VYINym;m|%yWK^PAP3V<hOO2=L_+F&eNCjO2%)L16p$ovKZihNy2B-xMUupd<3&D6;z(-e;^Z7cVXujWP?idf2U*+Uw47GcjR|{wv3Z(K(D>+!zBO+!1wT2*Mb&3Rb`CUUM6ZEf~#qQP-gBXzf_fhYSTA{SXZqG-g}i&Cr>KWXI1nbtZGn|n4!}*8sf|IFukuz!&F!eD?PF)9BEsZAXo{MLIBBUBizPgM^=?A**vYAWA}=ib=RlpHmSo}xsjckJ3G7{UEcdC=dX0~pmcApkvSMTC5VlA1G>U_xNbc+49`&tyL1B(reQnu^kvKJl0k)bd$BaHQQ_`Z>@eB~c?)?cgPciy)NDksU$8xD%6TLAVQt@as}NrvP?m?2Hy%v>qKF?u`-<4O;=pXhQCHRsw|+ne(rpKrkYR)3%D00*J+zt>LToa>g7FnhFF3|!^72<!+8{QP20DApAs5e_(NfQ;2HZ5O+h)2;afr=5)!$@8vN?C-w|3ug-R2$qBQE-R=@#e92YDwN-{uTt@jc9ryvEtM-~_=sbfGn1qD#KNxrhHR`aLB4L6{WF&3vkd&f<#e^YA(gdFi<N(V0$%r~-Bh`n{BCoZ!!?VCniaT+P()!RTuxr+zX8#&^`+kaP>23!DKcyhp~5=vN^U0jvoH-u&ce`e#9=@HGuW`Rg`xe;Zbf#Nfj|L{t7biy-SZJo9=g$G)vfIdMTsxhtvsta}ZNszUl&I>`K`btSZAX<a*|h#@)f=vHr5P9|B(PFIm^UWGtDb+Z#h^QK(7d=eLH2o()(`6QmH25PO&wx>xYEj?M0mTxnyOG!40N2v)~ZAR(410E`_HZaqkx<N&L)68<2J!vg&+>FR64DY~7cB#gHt>SELip;CH8?Dr{YoZQe=_N(P+h763k#Ed3N}`~@nfGzp<LH>38wG)MEBq2Z%#=T=?v3)<tu(4I@n$P~hBK~hv$>yM$4mPh0D_qZB?+Qj|3~+1DPqhiE0APe$c5Pn!UF%%-Ftz&c1wzSzr6-o)m2_?hmk&$?3QYKsO6n*X}acOa~jTWqfjGG(rR5c$I&4GgPw6M=S=0JRny`Tf9f1hhS)6Hu?LIO-x?@iL*X(nX6fg9>e%Cd)wvo|y1(qPT&%eD%$%Kk#QA`V<0*7(iaIyab;GE&Og&m4$W)yKg|ktoeRYC_097`28&ym#)~n#HwC;CSpI@aAwd}KM!CyewT5;qyCAH3ktkZCytB?XdbuEAHf*n`7kgz4Osh`BaAIIneQag=9GYQLq??}$GP}c8YOmM}>E_4RP{xJ<Z#<qr7xH(Hj*mb|gu{O-M5W{HgXPArX>j}S0)kzZH(J}SbmW!<IbOL!0j$hardU*~`N3r=aI2G0fB`?j2{*a#P17c?S9e}!NoZyxp{`QC%j+2!PY;Z>SrVYGF3?Q-m)i}*U9n=LN7m>KfO;|)xMJg*+9-S4fGmc4ZHpl$+9`g6ME3zv8<j-2c`s)4SuimDAy&+~Vm4g>JXa&)=`gqIDO-ntu@u#AQbo}qP-s!BarLK@LtgHSf!qb!5AA|b#dr2p!r*x{(I~b3S_##&8Zrs|NV5NE2r6qbhwN-IMMJ5BQe(9;aC@e_(=cQz7Vd+P?r(=P0ju8!0U3b!hwG0)}xULO4aL}n;mbr#Zuw;0Exn;o=egvyTWdVnE{b+J4O9}E5SC;0H*WqtlWuSUNbyGKk%xdGXmsRdma|+CCGz-$Hajg%r8m;^e&m2CQSlrsi0Btd<>L<V^?P5!7vWP!V@^L>YLQ7^_zr!XK*k)y4`gJzD#IEqWY^5A|L3-WYf3R}(v5DJnVy4Xd4>#6(Eki$w@GI6e*=3(!Y=A7B7nZG|Yog50`n0fNj*6w6g&@H?Gj40xQl@!L0m)?|{F}ztR|M%5uJ*<2wMk=JyNX>D0P=n|)Q;7p?rSdRDwJ#~b6A;HFHfAl_RK0}kvPhyu}ZYAt<piYCULd(mT$$6CxTpTpE&>C-o?1$=MlflNkjc>ibhB4w5d^WT=heZldn^YU%%t@O;n$8$;7(aVJXPQRTP^pqR_gqLgTkfHSgPK$D&^Raa~?yz5<D#trmJiR+c1J{iNo^ie4vWm8nLzyGdmjyM1-~0)oQC$HEegf%b<LwG<TAYZ7*zEakxnw@@7_o7IxJ4Sm0#p_jUN9qALt{N)JabH7`t>!g2Aa{sB;2K4zFTbC2f@`tFFEu!6E4h7><x3!2~g}{W&L-rf-Fyz80e7TGNchSR3X-c6y&Zk$#sG|6i87wNsEev9@NsW@Ge(mZUsW|>0L__dE')).decode('utf-8')
overlays = _sub_types.ModuleType('overlays')
exec(compile(_OVERLAYS_SRC, 'overlays.py', 'exec'), overlays.__dict__)


_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-qxnU2j|05&SQD=7ag6uf8cZ(+E{8LzYXV24MtfiULLYkoK+Uf3GZ&m%MjpXJ_{uTIo|1nc_Y7eC*ksot^#spR>RH{M)a;{C4(-&u1TQK7Ksg&d&b+^FROkucu!;{rKz8zy0Hve?R^F`Ruz-KYjV|aR2Vp+sCun+2)7!&C`G9tL^Ob*$=l5>$Bj8uYZ2?{`SY4yQjZ?d%t=5Tl4FWKdjdu&StCqKYU!T-#z{M$MxO)`?J~k<k!0)oF5*u{qJn_KDTfG^y$OV<Ayi;e70GCe0(0)@Wb1i-AIQ&8-_EUh>z>LyTjwJ@nDyDunTvL`w1P5^8Nk8;}6e+I{dU-CHtr2aZaAIdrkGbzx#B1_wLKn|2}?to>>2jC!f?ue|PhCeVF7qd&d5=U>%?S>HXs{?c-++EBgJ{HDC{T`M_v@+&r!yyzhJYfqdWYlW;EfBYs)6(f95?#Aaf0MA6qBhF(}sJMzQVfuoXHL^Jf^`^c1pOJ@iC@&40ps=-VYmd<Xm!@&1nTUoiI(V6$}vvPxt8=ll@<&-HYtei9>;R@Q}4sQ)6;$`5u4Y41}VW&-hm7C2Yn>d-)!am5oe&asa4{v>wUVbu8I}a_Um%V=a>&C7CbUVBaQ<&LP|4HF2onl~~>0*C!e|NWj`}pPi^~2-s-R)nV7uMdlDUYbKx4<yS7wo-&)Ihx*-7q`JVejo+&jqR&%J^?8bCo}?U7qr726l=+;c?<FJUUwU;}C5c5}Jtea;qEkvMuWVw_bSczUDj^2oCO5Y%XjpV*^F}Mb1z!wu$IQFlT{b*p0u%gdgtuoGpe!QwHMO_3BWDSqKg7-m9t20+>QP36*h70}$!NgabT^?+Rl&Ol)Ot{HQ^GAFy1`jE4hcv2Ve?4O3IT0Bg^6-oM2{rybjtJ8TT`%_qP9`1o+M`ELF2@Y7dR@bxaJRII`SZuw4&Mku|eb}>$V=ypNQYA!m$KKtK|t+(Vp&_3FuIp1KuErm!k0I*h`#_wHn`-G!D*g`x-&G8RFCBp9naTvX=n=Y#81q^zdoguJz2)YG9U&HnQCn%08=}28<zv}QE_CxHUSZ87|tP`|8Wgre;GJ(vBe&_@qtf7Lsi@`xV{c`77MJZ4tM^H^;R`08tBS$VS=?lv@7>TQ=4pur0l%7(FMI!T?m^qfAH8!F4g_EH2>xR2|`14vln<!$o6YZsLx`g5&rB(TM@HHEG8i1jjhNQUx?yMs}CBKiA(xcbo@h0Zt@Mk!xwb|}<{c7>=+{PeyxbIS{Ci~7{;qpsKg0oK3;f0coet`0A4dF`WF(>jn9Q0sCcvKw-Q1wt@>W?fk-bx`}N4`TLj}NTu>B1%7CFzIGI>A^kr=!LKvrb32RD|zUnnt^W)M<=EIf-@?PoVVy4wv3=o4ou`+vC%(>j7Ojk$<N=dhYshv&F{~SQuFZ1ob4O^tr(b2ml+S{3XPpI4p(yqKnK`tu9Rmw;+Ltd{Y==nTH`1*Bd<Mn_S-Yl{$90vmi_&UoQh44Bu@49wwY&4@V!9)#sPn^3|BQZyBnTU@}Bgj6=*yUf234C8q*F`i0bkh$*>ynI;@%RKJ(=lJGn1*WeWnzv$h={Rd}(i7$0HEcf?!yTT4&q=(9mr%UIZG0XNHEGU2;ZNs{S7}hOvr&o6-c~m!i&#+_kZzj>g;cE>{HM!jrjA%cc0L2}Nea0>~W!V#Evyif_cq1=c|LK|#tGZGJUkmqkT@(?8=dWFY;BuBol6c3_jB-V=nQKf2S?aIclIF1~sWJmWK}nK7ofJ+%&y8ZXM)rj0AkCOZkeZ#P?v^r>1cCzRU953W;!1WKO>I7%lNqK0KpG*uqLaI6dP5+4qA@}gJJ0-2Feh{qCD(-|hCmWa-X1LkPn%NWiO-ODqF>;4CBQZ{{teuk#e)JUJzz6h@69^2jl2;TC={Fz=Hsi|fH=-9V;LIb@=>uSY~sn`^@pi-Aq>>YWq{){lgLQL%bz|L<xl#}wmk-52*VzEcl$>?lvZDd)F!)AJZmXcs@wuiPg8y{C936RO+7YI$dCqGF9RO;vKHUuP}@|d^uVG+pEIaH&j0p98zEAmF@hVBEvi<DI{(LZcbG8&8(nNW6j4S2Nhb18ii&WwVVxL#C!8l%TMsB)pC(QAOPWov2EzvFTtEwb#o?*mt<jvEw|C*xJ!yo(kCJ!ztuqB#3RM$$pl<Zol|142QInmk>>uD@1E=xuykXW&lo@XmhQ3=r2Ifd}S1o%WbX_7tSt)$5$C=_5MjoeF-R3gyJT%}i4RGIJDtISr<a>%EZ=!+gVr>pWaHK_;-p3c)im-`&6u?$m_z)~5)k~;^#2i*=rL!K+E_X)XL<HTk9{K!DYucfOlFEXfY>gs!>lfHn;9h;TG?Co!k@sB7AdtK`b&X3tvYb6fkG3n`vsM$__o17t8ggbgFSi9B4~?<J*^pQfkRGoU!1b>~wNqeyb{*Sq+ZDrxjP^mPX3;N=%|QL}qeVoYx(sc69`F$0ht1GQNFdk;e#novcYgvmAd3QkBL?<eODY37eMkZ=3hLrR58QLK;9(%?PEJyG1fcTvS7NPk0nkL`Cm60Yg(B8XIsR%Ev6QQ2Qbjq3-5eRS7G|;H$LT(~Qhgj9oDTKMnpfK4{TK)6YRq#xwP&upsQ2nf=meAZ<`*R%(^%X2vJ<?&aI)@tAYikOAX~sb)WqbT=mlv{2nI{pDoxd10O>Mb07!ywglI_oSbx0PtJ0WpS_cQp8(+mbA{HE}2153IS++-f<y!DegIeIyTQuxQJXu>0md(<`u&HJ>-2Z6z@bHa#_<A6>DhG0Ca|u2HR0}7f@+z=fR?`8}E44EMs;|(?(uJGML`5TZ=7FbXTWgC$$v26pak|Jbok1k2(X84x7~oV8cR2Mc>$pN;=ZL%jrcT=aijYQ~{u+Y1kX0y;NO*o~Yw{<~uW8<l2+_x+G==NH!s;0Qp9LSM!6<rPK{eUm*6!5g0ZEoI9sY6H`yj5TuQc7~7yed0Cnw;d=Z0p$O>RR|_c1$FrR|DM5Z{B;xdCT%Vgaccvp|Dlo53cuw#ITc;fn-#los<Rh1%4e$F3J^30*r(ebPeC3tjkN-wZ|og!9pm2_^tqZzu`N!Jz0Hj?I=G7eqUK{DOUFlj5Fdl6>$e+)BiWW{V8aM#s7b%rA{0?!O@Gl%#-8%0?@651DoP;Y7?^WnZ2G4fCtp1USq(SXm{2Re}bI23^I78nG=j6oziKj-&=#g^rPbcwtEH775j0suLvayTLdJq11BsexXoz#pmD>f(cj?9a8WmF^A3MIl{)GI-_tC6q4C)wOx8!@}#VV^{VuOFp?*TEfw|1(WjF%1P+rC<w*{6qAb)R_H7tOU=Iz&xig5j9mtU@zpJrgPAi?)oL0>|F-dXglsYKDR+j24*=%Ze1jO1aJPAtLme2=APt~|pNs(TL?~;^-+vKrGC(&favOgFbQ<GL@!7}Zu!bexoD(M?ubYsWp{N8Uc5e2qNhvLWoqwtarJf(n#N!K95g#_-z=yLej@#Vg7|7EU+pI5r#2bAptWNHe4QdVY5YaO{%(_>;5N76(LXLrhpBWCo{GG|jIc(jxS;?+w89M-WN{zy!6z#T8u0)Zu_VR6RSla&;4gagT&gu|8KV-tyDJ4JwvtW|x|j6BAFpIOrv{Ui#5lvGSWQ%aQLj2o2#31^d9fXpGb8xl3A@WWbAkU?oMO&bv(3J`q2j59n%?V>BnF%i}l&7W6&>39f%RDlidI1B}>ADjG)8RTg}cp@0v=ZH>zd`aj59qO6ZAS`6v6oKiH)PF*Je#SLn)-QJ;>^?HWF8~GA>pF&S8?R>N3|I_JYkFhZDXvPnF1BL^ml>Nv;*~O$@%ma}+|($#)L3Xbq&q{m`dx>ur^$h~R0b#Voj{RP%fsgcVbq^apY@a#N^#vt@3c~?4mri47D$XNL7s!k8Hu%)*;LtQ8<%?CxxEBY^<iawsotfFew_#6c#UAjVp2<+Q<AVjN4A-RTG5dSijPV5JcHni6|yw{;wGi4-Z=Qe1c5U5RQolAGc7%{P<+iHo??m+0AkgRfD~qZO4H;w<r-;)aE{NLZr+yLraEc}6xZU@ROKnFhq6U2eU-d(wa5`cIjR+E(0~fFXZ$yv(|pP!3))PC7it4Z`y0lBeKudK?Wt3GEw8B1!^@qk7MZ+Vmm+CDZ`aiF!~a^~ss_bhh4vJJjrDpla!%1}wRW(B)QERMJOIMG>-J9Hk!HT$DV(`?^@d?$S|RzbsgrU{U;`PynVPmv_`mE3u<Q{{5B5ti*sUHj)<|7{#WRzjN)HPkLGpHjGVJJt3#T=7X9at-0JGpt^Yf#4tnE{P#sIukCUK$DE7DCnLO}-_g%sHQOb8`BWRP=vyxAMBzjQE$1#TO8zNEVaQzk<_VvG%ogLMIYV-#GwnZtx(rrA;$h|#VL(M|_lRVHN4+OiP{FGK{j1jk4p>Z&wNheukSSxRLkC7sVZYM!b~vFzD`pjZzzlUF5bvRcU~7E}cir(#?VSXbe4TF<$_<z#It#@tOxVVX%bgq*6`LuslIztSw46R$RkUFF-qtDI3PWGr>Rz`Aj(ZCU44(U;|NX%%l!x;{%~Vhyg3xc@Vq1E7}_tbOH3*!9HXSCmgTI3zs|2hlH`1z~Qg_C)2#u|h&m1Bz5P<wQ;xB{U+k5^`S#?_dI0B<V#Hi@Dqq!zPhJi`v6RXfIc72G5wKkxEUf)myNO=|qXi*b;6xi`;6h2@syE!N=x3QeuwwTnN}G@^Yx|rmh?fe{*$~>u`NkjHsm(PfE`*rhHZyoD^aic8J7l4fAG%KdPYm#ekFwxJg2=GIR-Vw0vARFUEzyGhMub4s)hxuR(5E$eE`D%T%(lj|L5lCztNOgu>47ug>#brKDEjej%f7v=mjIKAA-!;Ym1rLS+37l%82kn9YAu9i%25<V>5LT0->Lfp_vu>~htjE#_SvbBO_z95)vcwJ;KazSMaYL_W~}W95-5J*=fXp0#t<$}>@-3&#p#?A^-g4&_vtC_6i%OuMesAP1osD7m8pbKZGn8FV>NS}0kxu;=3}XlO3##&Z+Z3S2;d6PpztNK-zuuxX^mI;1QNBn=^m?3s7GHRCE%rlr)BndZsYwP04YZ35t2JcZy|(G%K~SR=9$U<h`#&AbmgtU=}*_gR9rM-g_x#ZNQ%j-U>l2nPj+JCHQSr^9Om+5j}$HZF2mY*fBYHSCl;_$hjW+xJDm0cNT(N@7DL8^;$AfyI2t8?mdQ93JS^F-qyRC@yugwT$UD#*mh+9#c_PV%Z~ULKZU@vWisQ>uSF-VLaKXYlQwVB0*1dr=`4B=9CvpAd^%8H;4$C&zB_|3d(GQKqApXwi<<jN>;)X+tiZ9l5DV`2}0m-spu_VPo!)&y&9Nmn$RxAFWm(fwY%H+PLvlj$>o&Ff*Us@?}0?4(M<Pac^62TGGYIUI@F~CRmF^mtR*#OG3yS-h29h|W`g(LHdV~QCKbG@I*fWqw2=jxKa8=&Jk?QRVkLxS;F00dfeQq_7uAM&wtTB?;siLj@>(E~u(?ZMX|CSfECYuIQ<PwgMAR>)j&u~=!2mhRC2HdeLj1Hu(`5f#XGSG6o<P@TGJgfsA2?-<nP}sO@w6%chYi?{a;R4GNyhF$0;59Q56N*}74eMX1!O~CZY%AeN7v-lYm(AC(GFf&Mwm5xHavie^etrBw$P6@op|4p=8tSh%cJU`2n42%8BVTQ*=Mk|I0d|jEHWH|?p@l;Xq9~tYM4{`%_YiI0d7nfXOS##4|+l|ZVIx7Wxst@xbzZ$i0BQR+PJImDGnopDtzxE%zagK&{o?LBPKj>c(cc8t%7dhJVR{bOlVp)(bx-yF{U??^zkO7aC23tUIHB(#zaWzA!j%vc_DGu43}x2G3FxM4Gp3TQt=2?!&doGJjpsnmy1|Mh!9}ZEbvE3N72e;LRdgjp!8C|nR<7zd9DL5`t1SIQ&&KgwR9=d-L@9(kpCs&ht1dP<?8cAhOi;^lA>h`QtPD}M*!-B+g7~Idd8z2eEs_RWU0PQy(<&i6VJXnSgFi_877~!@6-<HDdb+AauvuURr8)shgamKH)&#~G|aB`15vdw(*z3c5vEU?D^-=!=(-jbn)!XVN*dksy5oAl0ZSlp5rJL@K?;>o5V)TJWj&HQX|(Df>fq{4g!g)<(pTdNc~ZzPHe0O~u7)wwc>45wrLU_M=%J9-NKT@Rs*^Dfk0?M3)NyRI9C_YJ!;b51sv)Tzy50muE6Q@)?sn4ji`uYh6*#n>iBuZ#MKOhvu<o_7gDkt=12GY)Cat2OSGfd%Ehe^0>&Tapv|eOj7k2{J3jFEhfVI+$Fu5s(i17~4y%t)55fEr<PF9fLE3%n@kLyiN;f|+^Kp<RrVc^3ow)^gQB2>1lbhur@qY4byw>?9}B0tcnSO9jpLK%tzv%)cD`hjluf<|3?I&qENu3w;{*e+gdD=oZ6ypcCXso^3G!~o`V0Me8?C{#-q8dWY<7r#H9d=4m`7lkTnxocU8FwbF$`@$BF^Fj4U=(5T$uDn9K#Kw1sVR~FmVmML&CT9@&%hsGA$KEGO(89E45U8>%T#^;UYq`F=e=ns$!PXBPqcnd;^H-V_FG!WDJycK%jVi;7N$S*6NNN~Tdp1@!?Sw{-&)I{dRRpCG{iRhb2K?$kq&1TUb^!5;cFQ_nB$|MWVmw-(IhJdmm>5MQD&MqLxFNk8400w(PiJhBS%HOj>a>0lRtgWKt;CR>85ZFUthxYug@7c$`1Ydgr4!b-RhAG?u&D{@u#VwA<FwqcNW|G~5&c@*E|Skg6&<tXaNhe&N5bh;9&*ad1cM}FtjSf{iXs;fevJ7y<Dp^CDz)RdF3C=!HLmnz*B|7P*c?Eh6~m*kjO;X%QiZu}Rm_;($Byr9YlSxXyk2lk5-k!D9R|84(~OQ%HN|?jT9%fj9qAciUKpBTeqJ4)hTRo<zD>Ls*I%*kAJ%S-me#MfBbqVRE&~x3h$JnV;kr4R&{ZeqRIRNkV=&esxEQ(@tHa*jZ}vtRiKU;eFUdk};N>J&73T#GpMy`ms9Sy5IKYvQDq#30V=h+>_SYMpPz^vbJd)W3s>?w=bfY!~d^2cHxxOp@z%y;)+cixQ6gp#WzN|D4&nb6k5`|R!i)wvDq~g!u!D~qimL&j+$C5`h>_v_mp6zHn%nNrZKGU<=Tevm|1n`t{Cr75lMS+Y|0U8tw6Y8YpiQ=sk*%RyXfA{J3?%kIskLB^xL#!XjOL@o(plWp4kN~gv>5t#8M?OtT8OR0+V5Iv=FICd*o`6gVx%ptiG{7v$tSijn=td1wzVpaU;ANobUpWxdrGqd*!-FU|67&`u0ZD)mDUXJ5Vw9o)FvxzFk9`%x%T7pf&fnNDP>}G0%P%yiQZ0PkLMzz}X?GR8DJQ1!t{N6oETxPnOkH&ig1rAmbCrqYG0{GbYn3@hwo&B{L3^b=TIKadOO4Zt=IE6c9FQV>Fp@HysFTecf!$WbX8GpZwT(R`cS<`uIcC(dfAw7o9VpVAIKUD!)O|3fSO-M3OGJRBB2Y2!z)fNebRxD<hS0B4jr2~Zy4J1F@DJ^h&~uPA$_u*%3)S@5UWqdF#~oiLz9WGkwWEYY=S<EmXnsJdf~p4w&5$l%taQR?PzI7K<-Ed>L}$NbbI%g6nC+6_x$C)sDE-iaULzGfNZK5Olx773AiZvK(;{spy%LM9BkP@I?Asz&SxGk+t9K(n0mEUQO;Ds1mB6BD$DicjB-#qTrigN~7$oM70=o|Qy+Fb$N;AXglWbyfd?dF#1LZThIW!xONwJWY+a&Z1ojtO@M1d9*p)%c>%GOfURM|KR4OKd*%&uNDm~HN1QYmWM^H@$4=$=;tUHEMmYJ1n1@qE(uD9o`UztIBctUeO*c!D-6UW%J?ulbbxUb?TSJ?A1eSyRInG->)RMniA(F_TP8wCOqDR?_JZ0a09C)u&`E*hKUfaa)($idYj&33Gf+%~K_E+b1ociOR}w0zWBVW4EiAYL>`}eY$lz{raMSBH1!FcELb8orK&Q!g>|?M53C*X03I*OvLS8aIAB(X+eqzf5i<m1avdZ=t5KCRK-x7g3B3+Iyo7+2FpJZ2`7v&&!p9o_CUysIy+A8O&S1O)UP6CIIO-}I7YfO@&?ppRH})oUFF82K=5E%f!squ{0RHC)BqGsTMAHSXueb?L<5zgDew;ug#?dkADwo$!Ila3nNq%Pv`Y1E%u3fUP{ku4l0kDvD@|;-vD=X<=SDb(e_)jwC`)0Uf?+eiV_K|UMf{1A1M1;r5|Vux@Q>3^<-{2kfoO{xfngB6W;;~1i{a@-np+Sy(k{5Iyr-$5lMk9Liw&M=J)~0TQtaoHp^1pPG6eQ=oa<!q4Rov}`9i9g(y#hPYwMKKJ?Rg=VRtsl%%G4>)ZR(CAes*pUBI$RuY3A3sW9HtiTkgdf6Zfek+HMf>SSgvrRy39Hq5LLrQFpCN={5UW<;lqMAEG|Rdh6g-^Ii@pfOfLC9;c!UQV7|Oss||V>wLDQY=e7&+xkFli{9MlMkIZUg#&gnM1i!UDJA^yjZ1!`A}+DBL+QizeXT=HkV4TnFwDw)MoIeaU8Mp1!Id63mZW-AT38kdxA|&2v*xxBJ5E7x5m6fCw(dmRcuA<QrR-fl0@vPwHsWZ63le^Lg13|&aBa}sttCc_9tps9Q%VH(=83~I-@x*YH<)o0ALPzMZ7Vz^`=)NDrLa5ZkrY1E^;iM3g=}E_;u_MePX5F#&VREhxjU_oMpsoX+j#34Vp#H4P}MugOhUp0i#A7o$JD$fH%X6RNy<v-fOatmj|xTFB9b<hz6uq5Ku^qd0)*1RtcVrNS?6wL$7X3K5swZTyOOJOd(@)?kKc(h^#d&d@-Re%Bl*@QI~2b%zRmxz}6ykCfYSTp<$P;W1&4<)?)6Nl5L=Ux)A&+a(qJML!kh~eqly>X)d9WL63I7ds6`UpMcXrxbkwdEG_zFAyGmQf4R+6Z6xaEI8T?xqmuW2d@zK2o1#@w$v+c2qO{3k;+s=Zfl16(-RVuqF6wNO4F&mt=`2a>rcdmYa(gb>pg<pt5%!76<jT;w4b@<J7*B@TdCI0EHIq)8JD&+7HlHH!0yrUht5w#=j48fmG8jO_7!_A3q9=JbQd}ZIdAZiHDW$lPMjWYc`=$>q#KMN8y6R;0R_$<2H}#NZND!gCN$qyJj?-r{7bMvwiG6Q4?$x%l8i_X11Cw-JkgPhbIEl!eWw(+3GRy7j>6u6iMJkX8MJd-0N#eiLa_~r0vk|l+UKUR|hY4niP!&Yy=(sG#>FDD7(Kn&BX1N|>i{aBMsd%+5DxejIwNhUhothI#s%(TsQ~<0ZM#bSTO`{{gR7(R4`_k~1fYcnK^IWP=q3dEVs)-s=WMaGxk*hgjwmNtJ@Q8DxFjNz)Aujz0UWQAZ8vliLe5#<nQHL8x9yryrE@5>NRm6!bmjda~$UY(x(VmwSLMx<33HljSSTG7^Rj)-EU$_-`ff!TlAJ@p##;HNGe%cSrI_ZyE7%8YR0emTG%z_FH7lKI!bu8}5j3q1HQqif|YuwEIEa+>AuO?v=F#OAIRW_2IV!(`XKezOe6}=8bt*Rl7;gX^&L9{x$jRa*&k#kc@MA7=_1`>=a@e<Is17(kRoWRLZ)wj7<#>$0?ds1w@jN6A7@t9V;g2`5H^oBIbdPsblU|UAgE;P~*@t%O!`V3V8ZYZhX;LJ6Z7DQsqT%K0#3{E><gY(m}53ys5Ge<HqS%o%x>{O~<m8roAO6%IHjMNfIT2MzR32LF7(hEA?B#kWusAy>JmfEPA?=)Wk&wT3q+r-{R5ef#FfGw6^=lMFv{VHEf=_=C{C2%*wlO0vsg6617C#-7~m$s`B!2T?W4~iXZSE7`Xqa7ZLN0o*fEC%0%xr=$Gyd|uABM6IaDIaNa!CK$x-kuA3cy=(PY{F_#kVO!rm;KpPMnhm`X*8yqY1_brSY7l9^}8t2w(%jVt_Drc23^(M7=G^laT6~&h~ltcu0(k~d^Q%(B*Jt`$1Ju~-w2`)SwYdM$rHG4;fSLKaJX46bCjq@mr*`R3R#B9Q+=uvrdiqpthyQbvi?8ja*l!iMC4LSRYSSCNws4`$D|Z1<{5`5S0&lG0tTa}5{XQpB0Cg}V;VdbHEDS0IW08D<u%-R=U^1Md*@oFg=;l6juK9EyOAC&Gj3e~R#jl%o^KNc|CIj0OZ&yFZZT))=efP5CW-}d{k#xB3{IzIBT?fElsbu6!({h)OsuOoU}J1_nj3}9UP&L2<}4=#MFTk%znxDi9&03>yTV5Kn@eGclOL4!9Y|Afd>k$k+pF+saa6&j#a`fi**PH{Mvu83&!HFLoHRFUJ(4(@Z;QYwyPfO+U3sZYGaTlr1yVy~ex;#F1zpTpRJ}Jv(IrKR3v_TY;>60*jWY4>!7B0z=sfX-5Bg4zslLjg;4Lm?IY6~R=5&ZxsqS`>ZyWO4X`;5uj^zh{ayi+qt`k=jaYr$WofuROS3r-@d&eSAJT<hKR1zP9_<ATJn5^8SwRLH7=9tD?T-q8VGAVQhZu<xhjAoAh4gKTPhC}<E^$K90(%}~XE>MqwvXO1ZE|Y?>>}qjvs;X{?V@;ybyuvOWFi7wc6+H0i>EH2d(@5<sl=&qCIRyLWp8#EFN@1qSw}sHQd-pIJ1d<#j5!F9RRE1ICG7|<C`bLr_pcQ$guc5{Ee|tY8$p')).decode('utf-8'))
__version__ = "mapleleaf-6.7-live-import-bugfix"

# ===========================================================================
# MapleLeaf 6.7 -- critical bugfix: 6.6's live Kaggle submission (2026-08-22
# 20:47) came back SubmissionStatus.ERROR / "Validation Episode failed" --
# it never actually ran on the ladder. Root cause: overlays.py imported
# `kaggle_environments.envs.kaggriculture.kaggriculture` (an internal env
# submodule) at module load to source its market-price model. That import
# works fine in this local dev install but is almost certainly unsupported
# in Kaggle's actual grading sandbox for a submitted agent -- it was the
# only non-stdlib, non-local import anywhere in main.py/overlays.py, and
# the only thing that changed between 6.5 (validated fine) and 6.6 (errored).
# Fixed by hand-copying the verified-correct constants directly into
# overlays.py (byte-exact match confirmed against the live 1.32.7 engine via
# `overlays._verify_against_live_engine()`) so the agent never touches the
# live package's internals at runtime. See overlays.py's own comment for
# the full story. No route or overlay-tuning changes in this version --
# everything else is byte-identical to 6.6's CMA-ES-tuned baseline.
# ===========================================================================
# MapleLeaf 6.6 -- CMA-ES-tuned revived overlays on top of the unchanged
# 6.5 (Filip Strzalka) route.
#
# Phase A (route refresh): surveyed the entire current top-20 leaderboard's
# real replays (route_mining.py's majority-vote self-consistency check).
# Only ReCurSiON's P1 seat qualified (96.4% over 11 real games) as a
# clonable fixed script -- every other top-20 player-seat, including all 20
# P0 seats, came back too adaptive to reconstruct (<95%). Benchmarked
# ReCurSiON's real P1 route as a straight swap-in for Filip's P1 route:
# LOST, -1,009/game, 2/20 wins vs. unmodified 6.5. Backbone route is
# unchanged -- per this project's own "adopt only on a clear win" rule.
#
# Phase B/C (overlay tuning): overlays.py revives 6.3's pre-6.4-rewrite
# overlay library (premium market-lead preemption, fertilizer relay,
# price-floor guard, impact-based sell-slot ranking, opportunistic surplus
# sell, terminal liquidation) -- deleted wholesale in 6.4 on the assumption
# the new route didn't need them, never re-tested since. evolve.py ran a
# ~40-dimension CMA-ES search over every overlay threshold + main.py's own
# weed-repair/demand-forecast constants + front-run item priority, scored
# on a variance-penalized fitness (mean - 0.35*std of per-game score delta)
# against a pool of {this route unmodified, legacy 6.3, a real ReCurSiON
# game} -- the concrete "steadier, long-term growth" mechanism requested
# for this version. Winner (fitness 3335.7, mean_delta +4,883, std +4,421
# after 53 generations, ~65 min at 110-way parallelism): premium market-
# lead preemption ON (unlike 6.3's original tuning) and impact-based
# sell-slot ranking ON; fertilizer relay, price-floor guard, and
# opportunistic sell all tuned OFF. Validated: 20/20 wins, +2,303/game vs.
# the unmodified 6.5 baseline; 36/40 wins, +6,626/game vs. Ryo Hasegawa's
# real games (current #1, 2026-08-22 leaderboard).
# ===========================================================================

_BAKED_BASE_PARAMS = {
    "weed_replay_steps": 2,
    "town_demand_pulse_period": 16,
    "town_demand_check_interval": 5,
    "town_demand_single_shop_bonus": 2.300216812449822,
    "town_demand_multi_shop_bonus": 1.1189036311966576,
}
_BAKED_OVERLAY_PARAMS = {
    "premium_shift_enabled": 1.0,
    "premium_shift_start": 40,
    "premium_shift_stop": 703,
    "premium_shift_fraction": 2.9642044932873715,
    "premium_shift_max_batch": 23,
    "premium_shift_min_future_qty": 2,
    "premium_shift_opp_ready_threshold": 1,
    "mirror_max_distance": 8.175368097055422,
    "fert_relay_enabled": 0.0,
    "fert_relay_lead": 7,
    "fert_relay_lead_heavy_animal": 4,
    "fert_relay_start": 154,
    "fert_relay_stop": 585,
    "price_floor_enabled": 0.0,
    "rank_sell_slots_enabled": 1.0,
    "demand_alpha": 0.9956143660096762,
    "opp_sell_enabled": 0.0,
    "opp_sell_start": 166,
    "opp_sell_stop": 656,
    "opp_sell_batch_cap": 11,
    "opp_sell_base_fraction": 0.34051958804010085,
    "opp_sell_floor_fraction": 0.25263219724334873,
    "opp_sell_ramp_start": 401,
    "opp_sell_min_supply_fraction": 0.39881985070649717,
    "terminal_soft_start": 719,
    "terminal_hard_start": 695,
}
_BAKED_FR_ORDER = ('MILK', 'STRAWBERRY', 'CARROT', 'TOMATO', 'WOOL', 'FERTILIZER', 'MELON', 'WHEAT', 'EGG')

_FR_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL', 'WHEAT', 'FERTILIZER', 'EGG', 'CARROT', 'TOMATO')
_FR_STATE = {
    0: {"last_step": -1, "due_step": -1, "due": {}},
    1: {"last_step": -1, "due_step": -1, "due": {}},
}
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8

# Tunable knobs for main.py's own overlays (weed repair + front-run demand
# forecast). Defaults reproduce exact 6.5 behavior; configure_base() lets
# evolve.py's CMA-ES search patch these without editing this file. See
# tuning_spec.py for the search bounds these are drawn from.
_BASE_PARAMS = {
    "weed_replay_steps": _WEED_REPLAY_STEPS,
    "town_demand_pulse_period": 24,
    "town_demand_check_interval": 4,
    "town_demand_single_shop_bonus": 2,
    "town_demand_multi_shop_bonus": 1,
}


def configure_base(params):
    global _WEED_REPLAY_STEPS, _BASE_PARAMS
    _BASE_PARAMS = dict(_BASE_PARAMS)
    _BASE_PARAMS.update(params or {})
    _WEED_REPLAY_STEPS = int(_BASE_PARAMS["weed_replay_steps"])


_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


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
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _align_hands(action, obs):
    action = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _trace_actor_action(step, actor):
    trace = _ACTIONS[min(max(int(step), 0), len(_ACTIONS) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, step):
    action = _align_hands(action, obs)
    seat = _seat(obs)
    game = _WEED_STATE[seat]
    if step == 0 or step < int(game.get("last_step", -1)):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game.setdefault("active", {})

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - int(transaction["start"])
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(step - 1, actor)
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
    action["hands"] = unit_actions[1:]
    return _align_hands(action, obs)


def _fr_state(obs, step):
    seat = _seat(obs)
    state = _FR_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due_step": -1, "due": {}}
        _FR_STATE[seat] = state
    state["last_step"] = step
    if 0 <= int(state.get("due_step", -1)) < step:
        state["due_step"], state["due"] = -1, {}
    return state


def _town_demand_now(obs, item, step):
    pulse_period = int(_BASE_PARAMS["town_demand_pulse_period"])
    check_interval = int(_BASE_PARAMS["town_demand_check_interval"])
    demand = 1 if item != "FERTILIZER" and step % pulse_period == 0 else 0
    if step % check_interval != 0:
        return demand
    town = _get(obs, "town", {}) or {}
    single_bonus = _BASE_PARAMS["town_demand_single_shop_bonus"]
    multi_bonus = _BASE_PARAMS["town_demand_multi_shop_bonus"]
    for shop in list(_get(town, "unlocked_shops", []) or []):
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += single_bonus if len(products) == 1 else multi_bonus
    return demand


def _future_quantity(step, item):
    future = step + 1
    if not 0 <= future < len(_ACTIONS):
        return 0
    return sum(
        max(0, int(order[2]))
        for order in (_ACTIONS[future].get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _pickup_reserve(action, item):
    reserve = 0
    for order in [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and order[0] == "PICKUP" and order[1] == item:
            try:
                reserve += max(0, int(order[2])) if len(order) >= 3 else 1
            except (TypeError, ValueError):
                reserve += 1
    return reserve


def _existing_sell(action, item):
    return sum(
        max(0, int(order[2]))
        for order in (action.get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _repay(action, state, step):
    if int(state.get("due_step", -1)) != step:
        return action
    due = {str(item): max(0, int(quantity)) for item, quantity in dict(state.get("due", {})).items()}
    action = _copy_action(action)
    market = []
    for raw in action.get("market") or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and order[1] in due and due[order[1]] > 0:
            requested = max(0, int(order[2]))
            reduction = min(requested, due[order[1]])
            requested -= reduction
            due[order[1]] -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        market.append(order)
    action["market"] = market[:10]
    state["due_step"], state["due"] = -1, {}
    return action


def _front_run(action, obs, state, step):
    if not _FR_ITEMS:
        return action
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    moved = {}
    action = _copy_action(action)
    for item in _FR_ITEMS:
        target = _future_quantity(step, item)
        if target <= 0 or _town_demand_now(obs, item, step) > 0:
            continue
        stock = max(0, int(_get(shed, item, 0) or 0))
        reserve = _pickup_reserve(action, item) + _existing_sell(action, item)
        quantity = min(target, max(0, stock - reserve))
        if quantity <= 0:
            continue
        market = [list(order) for order in (action.get("market") or [])]
        existing = next((order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + quantity
        elif len(market) < 10:
            market.append(["SELL", item, quantity])
        else:
            continue
        action["market"] = market[:10]
        moved[item] = moved.get(item, 0) + quantity
    if moved:
        state["due_step"] = step + 1
        state["due"] = moved
    return action


# Activate the CMA-ES-discovered configuration (see docstring above).
configure_base(_BAKED_BASE_PARAMS)
_FR_ITEMS = _BAKED_FR_ORDER
overlays.configure(_BAKED_OVERLAY_PARAMS)


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        state = _fr_state(obs, step)
        action = _repay(action, state, step)
        action = overlays.repay_premium_shift(obs, action, step)
        action = overlays.repay_fertilizer_relay(obs, action, step)
        action = _front_run(action, obs, state, step)
        overlays._detect_opponent_type(obs, step)
        action = overlays.price_floor_guard(obs, action, step)
        action = overlays.rank_sell_slots(obs, action)
        action = overlays.premium_shift(obs, action, step, _ACTIONS)
        action = overlays.fertilizer_relay(obs, action, step, _ACTIONS)
        action = overlays.opportunistic_sell(obs, action, step)
        action = overlays.terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs)
