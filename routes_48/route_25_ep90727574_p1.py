"""Kaggriculture agent — Route candidate ep=90727574 P1 score=138,408
Route:   ep=90794783 P1 (best of 400 candidates from 200 top-player replays;
         benchmarked vs 4.6 — 10 games each)
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + Town-Center-phase-aware terminal liquidation
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -10)
         + price-gate: hold sells when price < 30% of base (floor-crash defense)
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 4.7: wire in _price_gate_sells (threshold 30%) to stop selling at floor prices.
        Root cause of "weird" losses: opponent floods MILK market, MapLeaf keeps
        selling at $1/unit. Gating holds crashed items; NPC demand slowly recovers
        prices, and shed overflow + last-2-days bypass prevent deadlock.
        Result: 20/20 wins, +$3,182/game vs 4.7.
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<%Z?jKlKhuC^B^Y4dhD%Q;;e+JRtcrj60?m$qk)~l0E^i}&)gRK@2gSqkxVx?H}{AvN!@cJ_{s>6$Vhi{bMv46_u?<V{Q9>)|9bInKV5vd{rK_XX>sw_U;gL6{{H!m&oBS>%dh|a=YM>D{nN$UcMsdopK33D`1GfrZ{NTB@%HXwaq;?ocd;1E+aKR<w;x6yeB5r|e13cPc6<AHvACMN{p0rT{{6*bdHni^hx<35UO%3Gv3Yv>zs1>n-o5_grw^k69B1~^#cuoY@ykfx-#<LQ{qkx*{n78nBYghBxk)~5@9s|5Urn$7!>4z5Z+`y#w~wE`m}PYN(^c8^_kTQ$zBeAgbh>x9uebZz>K8K~k}K?uHu~%76yYV@FOf?T+Z~tg^Mv1@*8kjuds{rOV59vG*LmK8UpB+-<M!eFihua$HXV;@|Lv4HPyc(G<lzFZZ}-OAf2ou4PLn!b>G&PH=ffG;H37D=8)EV^zDj2o5Upo7L~O>x|0T_L+zAclqg(B`6ZEY%{a?{)r=8HnSolVrPB^mK^f4t`ZS<CIHgl;?)&g_zEn+?z-CPA@0fYE95^hK`74xE#iR=r<Xx+v=u~oNmpTBtdzuliDj?V}Etd;9$9lwzJzhU}+`vbJ;Kc+|P*BVE`zUDs;F4b>hGTYnsh3PSl*Y|gK+t-gj|6%*^`0noAf1W?QD*yQL{!{xh^&i%ohx-rd|5zM@o6$h#xyuS0B0PbXjsN$}+;Pmn<(-q+x4kX`Vp_*AaNi|hhr;S|H~>VB)6oAaTKn-IpWJtHh2X?H`#-cM#^(}t-|{JpPfk|_?yq&}+zTzH7F@;_Jo#YOf{8iCmu@n)Y=l7=Ne&^9jQ}ofPaYD_wXD5#Z8mKXwS1@ZUN+7f9!%nMg+=RL^wZ<%4kvPa@%(Le(r(;iURhi)nm)5GT{>xq@}>DhTZwyTvjMsEZ^8uT7B7VHmD{fIGQZz{o4Bd#jGMYv-Bj+cu5kiQ@sO0H*8a~F@Q^t|;1biz_jWmxmuxfFSu&{RqEErjW?RL_3kq$R$2j?HHs9UO8zdkz0Yqqga>c@|GmkR%T(4h{*fhl3dthwh_2ea7b$mqUADF8UysKYudUN==gt?Q}U)d;?5M}Nm4Bys90VnLd7yP=@?Ui<V>FfRLZ)4|nm3D4@kD%S{-FQ5(K5p+gMvJ*z!&93pOj%XBXSHf{kB?N8Cij?dks3UG;4jA@-+aM^o#ctf6LJ+8Sk0JR9lbLt*k}Oql2G*Vv$wYo|DjHECBT$>$D7YnXRjQG2d{x5&gmwt68!A&Ph(NIW7ag|-{X)LQ}f7Gkhf$0=4dV{!V-{ZW~Ax*XA+yIx5lr)U+1~L1X)H5KAc4oNKu6Sc(~qp8`!zQ`!Ta7gv{q9$K<=wTJh|ju!cOXVr;w6kv0<pdt}e1IDRJNt`ms>aKY(R8zx9Mzq591nuo{i@~IU?J^a(!A)c&);({fo{x89eQgDR|;9u(D@cbvKfuU7P4KoZH+;}%N&NL5E_=yL>r3PlROyR(iHm?}aEky{2>*81q=SFhE9z@h~G*=_$-^)*0BKu8yWDkFR**9`u1u$!ufV~!`4_(6a6dsYYrG2tAOs*8T&t_OQ?bxm<+L>F5(+U3Y@s<{*Pc8;cur8X2Q)p>snUK6f3i!a_B7KckxvZ^nOJ#5qg~XPKS^TK1I6#F8)I_ez`ZIQ{ZE+gKCF~z65xXAxHJiiQnylQeb>QT`6}#BMMg(5jEHTw<;=pXeDER*V?oi<l{ItuAH+FaX{>?>Laz8E6kK?#$Nj>&#&@*538gC|PppTCax4R#<4-bF3SX{>sQCg7h=YsmBY=r04lv{K<k$vHTcz|h#(LNCj6{q>C$^xCP1wK0r?U*x}eCI1Hl2=LYgJ?0Wd6ikN<K?F5J(L0&-9I^)gWX9}ErKX7Qm%A_(+268<FxDkD}a-L3D2&|_VRSNeK=px?eerP&JVv}Kh!gi$K^P_m}X9cw2kT}%PRybh0xKaVA}(y=?3&Iwt&`b=+G@Ln=&|tkeu8uY+*2FePK5}h;Px#qgN*{SbxNW!EOZdAbEg}&377+d`c(-imZq3hR~wZ7^2fk6GoxQ?zNH4Hf3rZ3!ilUl{C{PF$Z-%r0Pk(8e>ArQPvBw*DgyOHLgfDj!f2x&}n=`!zZ;U|J4A^FJHwEgOi|@Ew0A{PrefF*y|@TY3f|*I0xV|wvFs2;jp7C9fwW7RUy4)mez=tO%MO=)JFkh>oQ2Puprp5>uN_+@l5QvXdyp~_K;4OXI;Rgn`yzhV;M4&B16lmo>$pNF^@PIfZ-0f(>{f~tC8oj<(@PqICZfp0ItmqkH}6A=gJWutCjzllN}N<!K#luC7+0<(JU)2BO%~9w+=cn-CBN}$1LSjz!qe=Qpz7LFkLk+pm2(UMYW%`Wt_MY9-`+~Mj+=R?0p3(os!gMWmqse^sg!vK6XvkFuu7IQZ=W%k{4!U36q;s0Wbc)?#_f4fBtV6KK=Oa?vMMxNujmE^Sj?b!|*U?r6@inX-87>X-#%`Hm~Z*!Ct!CAZopG7I&GCW(PHzT{cCt&o63JFDro162wmbF7<GnNCe{mD;KjCi@YYaNCAr9ZzLp*U^5$s9Gn(3JK2xZKh>5B_)~hYL<d};E!$-y3+ZQJ{IH}z*tW5FY#&fUCdbMZfRbLChmmAaD^3>J5q1f~45XO&&AU8W>M^sxdZK})PQzV@id=j^O?6+J9Y%ByZgV$dBYsW*N{tCJi{7-bo5D>NI%}yBLPr+y(_InrIaV*i$E0QIyp~OxDZK_k{QmjIFrn<tDBIG@Of9-CFSUn%Csxto>1I*=MMFfzvK~s1w?c1j^mq>g+$m8GORB`_OOP6=F+uf20eH$DM?uq>4Z~67Jy>?KktSP_udqR~eTP$yJIbs8_y1@lyLg>xk?eLv!MR;ND=m>sgk+Ww0_9+@w`359R1FO>mrc{UAz@Jco)CCbbm!<`>2X!rY-znQzRWg;h2PI?y>&)Gfx>4D%YkH2Z9H-f3py6SU5jXMF@=12$)&Xd%Ak1vu&g3HZ4$i3q8JEzWeFl6z1?R}{ER(a7ChM*fTR{xYjPrJJVD-d@`7!>%j_KyP$dwCb2?%0xLGD^+&Yv8ZlYvRgm7{(m3TMC_a@jx@`6q^Y?M6U_*u5M=cQmgd+{g*mwWp-6_%Ad3^$$ut3L_rQ@epE60((K*oFb<O>_C;-l(frC9bVjuxOeA$7m3u-SSF6_$fLCtAyfl4t7{&)RPb`cWfhsc?&UI$ULkwjRh4DueQ&JRN3R5O`OHNGX=KeN*cdzkOhv?gwXseGZHEzEqfSPlP(O4xC#?V7hzdyakS48*{g`N1ZL{jtM#eSqZCA1B8QYPS+m_BdF$9F<B?}JD61#ddCoM@AQ|<OflM_W=saA<g2tP8a>7LG5z@h}_d`!37517$uA3$Zg&<Mn{+%|Qmeba!AIkiGDlDpD48Su5uwzUlSDCfcV5OSRnCz+2AN1`@iPqsk?ZY3HKwT4WTog-NS<HZ=ZJlT%)JYFZA_KQ*#tYD+l6B=HTy}69>m(LNt9GV;RqdrKu%8{iLEJz-WGGNtvsR(t+QX@+I1JbEoz+`HB0K1`DPl|+*}M`8bHYt1NKR2w%4q@-iYk%AEv6Em1XuRkSGjyhv{-dY4&!HeC`@JPahX%`L6Bqkoa}f)&GIKm#C~6q<u8}3OLsxs%2O^8D{Bug0+sFj#*`{2X5ioe<UP0DIuAV6J2dqop}nBPskRz3tzUp}>r;VAvzS4;#A8!LPAvhaBn-D)R|?xDIH@<&$Kp$;VW3iMxkRQ45!h!M$V>Xvf<8znTO3QODKL8mA<|G5D*^*u4TR2%75aos8DZCv*+b+O0uo3aACLtBa?Vq1(-cHG-E9f6FhyG+Ao&oI73sOsL(rMYfHY}?ttE$<>3>*99`r>j_0%S%|2|(bC#JwPB8B#xWX*Cn3KNLP^uV%y+bM&|d~t-n@tZK&b?0>4`}ur;F|~CTle6{$xSlsci%K-#*>S;VgAy|&Rw;K-NDj#JD^#$MM#x=v3Y8mB*hML`Ob9njkcAY?T$`9CO+&3J%tcMZyl8F#npM3(O@BH{Tjis)rP6Mty(m8$oMky0O^RZaB;2dmo`qpHo7Z}MWd%SiLFH(7`hhRm-yG}I`We4Nu|6zmwtK@vglo3f3eSnNRc+i!)5PR0H}&7FwnPV#Bo$;jmXOO*>FTXq?=Q)>Gcr!&^jVoT+FAhZ1qNVh#U)iKztSNT^K0tK3?|8MIAXIxSIC7t7D}UQZ+Xhp$oq?6P;$K{@9!%9_vkevDW~8j%Z1VC`F_#_S=St#!AyV$psCq%w5^BDWPPt<B}YPE4@P$+w>;ip`5;H`T67lP49y*UpQE@NQ(;rfRSC(Tj*?_UT&>=wICfTfJn{HD*OpTi?0UCCYi(MHIteEFWFg{gN3O46r8NPaY~Id8!p?D-{%mGOo{4N|soSBSM3^QjDUo>9)U5@?3?v$<G!scRh+(#<6Nzbc0CP&^1>Yo&E8yu)vWRrOZ<<)AOywbnzg6>JK4pZOX{o7f|4UWXQ>xc=g)cf0A5rAlq*QTLD(bY??AI1kCz_XHsIb@=JUIxp^Vx43>MezGo;3emW`qdxicAB@kp*ZYEUFi)4}>D!MPvotbN?+SA?C|Qh<S-T*$s}jIeCGQWK}FT0rI!zI9_O&t*H>HF={{&n>}NqCJz|K+-Jq<Rhegzf&S*qzNmg6#kO7|NkjY>x-456rEE{+bSSBPfqV~}6>z1bn5=tJC~Hbu>eDfO<cS6acR3aO3C$S@_0n_-Pja(-ho33yn}<m!t7zBEBW;IEPH{>OlByv`61YWJQ3);bNo1KY-cE*>D7~ZB#tpP46P=T^M>DpX20AdkWqb)WU^)T>b~ohvNxiF*>PVf~n_ySSA|TRi=Fkh5HbE|w2lsT3sc;>@Xr+PJ8L3B`p>M5Bd~Fc>Y9K?V3)_bF!nQAm#B%sLWo&~W3N8I+-KuB3e(I7|9Kr&#xdp9hD16qt?lAQ6j@mfW8-HgtU)Ius64qJL1gJ*Una#;JBJKjgHi@LCi|k}_H~`GCqgObT9hTKO2+4Sk-<-yU$G1DDRjJ@F#VP7VR7Em97XTI*!$sljP1}aVQ7?!+&ewkYv)uA;GG$n{a0PhlM7YYd`>e-8{1p|3lQW>JL>V3C)-h`0`3l1KXDF#7t&nTrSQXeJIABg?Kf&I0FeT6x!MnMVnN_%njWiIfQ_L1&3Y1<M$)PAx%-gila5+SR=o+N-j91M3D%XTbS(aFf4UAHds?ME)bYQGYZE_!5BQfqnXd7RcD`OkEcR_?`AeAPGu1tM|wZmokHf!(JozmXJx0v?kuOOT}Pior<5aWDt?<}Wz)MoqBjvy&Cr{xSOZRS?dL};J%waaUBn-x(K>I<Z+gH{z<>{H24YmX(`TPBKTJEfyZ-xo(PIFX73?zd7HhDQ)Kkl8kL^rfYXTbkvd^*Sj}kP*nWc31^#B^@CGj&KKcOh$&N4J~7=tZ79i9E}&Jv?}{fYU2yWf*$j#wL_QtGIl(Iu#q2H;rMfk7kWxnD~8AGOoT-9F^tap<qS2_3WGfuvv+tt`=~cGQbyiVhABVA%s6b~AgQK3${_6D8MlhL?gZ<?2_ggup0VIgZE3h0K_X3jjhXoXcD)6Q>uL5{vex$N8pjk@&fe;k)%EsnvJSMyI4>7_&d4*D+a>2RxN%aloP}<yE{$`!gOu-W?Kxa3txQJp6#R;&-n&|J>vmv`+a`<k4fE%cS;t$74pF+~OdYf(GC`mSNuH`y=wp^0gYu7xCWh}E&ylR=#TXzzEr(%VDn#jFbk)22E~|xLi38@cy4lG}k{g61<V59#6ke>yc)Jba!W8L}q`=T7wD}H)X`r7%x&9b(D_F7YLf~0eG=8t1x`{=h`~KY4p!CucH*FVjNmu&D8bfZ=g}(TP)LIh!j#;%pjn(@-Q=5idpHxJ(ue2Q$4N#WkrPw~JEJ9t`Dj}h=so~yBw8#?uox*Ohrj6oes;ekVKsD@~V$vPlRHf?qpw=q4n-by?toIO+6h6L4?Ggw#tY?!Gjt{)?i-x^Ji-OY4xzCNW_!kYLod!XEF&h#C)6$|4K(;6>6ZGpzDtnWYn3+BcTSlB|dII-qmRdock2Q2F?u(n_W1O>}LG1=6LcAQ>l1)zqOG9hu3qeh<21q#l9$`i<dQ?G5S#(U*;ZjVZ1hE`E5wCMfZwnw5mkC1stSOF`^Xt`6-2p`8G<g6zLGY~>_$br8O_KW!&8;yGdiSnYiz{>jcwAdRqSj{ytuB%0NyiB{kllv7kefxk!7p1@Q{bv3!rl1xr%UQLw(bJ&(C15}T!7zYv^C{1xfT%3ka*^n1#nhKm*zbSN>WGfnLPN}9oj2Y1&~~{!r0D4y&}{4IF(rDh%Q)VDv_^^x(%bT+z(e0D8acaiEV_vlyqgpf=-IAu_$y#ZaDR{yw^6CsL1ki$e8!vq-0GQxFbXMwv7&$T~-TiRvF}Jc?mY_S5bi|C{zwFj8XXv5?%^(sq$+mHOc&=1lcVM<|scsh(>})p$ZCcR?Q@=Dm97dJqrDr`&4yRW@2}-<?%SYQUKP(b>8)EaXPT3H0os}C0^i!!UIsr73yL20ohogmfd)<NH~`+EzDt^*l`{uAVLeF1AP7$IvH6K-IPPszz5=No2??!NMWL^-l^Uo8-Nj42|$}A)HS41E2OiyL?;=1*l+=G(74#9_mep2lhj4j^p7gRC<>KEYiP$#1Uho%bVRI#R$H+cL@Pk$H=^E#8cEUUwN}vzo&PR=O4oXMqUUW;n__o>JH>JnO1)^0=>btJ5aI^g;Q2;HiWB9K05*u#vfM)MX!Go}l5c=eRt?Y26l(66w+f+-g4|31j%vInL1sA|{M1A}s%Sm;UgBYeuv7Bu6i~GFntC;OKxHM`0-V_hy;NPCrqB&5Tt<sWdAB$L-DF@aBTz)vhp^UcVP{c@RYv{l>o>d-G7jgmn|*pd<~uwp<%hGd%!aSdGAkFv4PiPVS#Z{|5e=<e)R<esTiv?QSR8{_?Q`XHEZj3gR~n!jDk`whZPU3e4cGx8Q9~POOM4CE$JlM4np5cyUR(A+x)35%+@ulIs06``4+bqOH>HlWX7J~{4JJ>nr%R1w-Vy209zrxB-EEWMd}XN<JDm>@e51DO(cSKd@k;jhU<gglTWSOmOXEg_Yx%~ED}jSHr@C|utu&3|&gfnx0zS32nhkPCoMciPsVz^^Pie}?X9O2<sL`niH+fh@C$aOj(I>DpYiAp#fyPIQSdavwAl-Ub0_Df;-TnJ6tS@*-vl?+*aS_TSMFDKc@3@Y`2V3n0pRD$4)8@7KE%!6LV9(1lcx=7ZGP_Jd$#jGP06ay_>${$G%DqP=Iyhw?pdk`9PZSnzE^N)w*Am|BaVCm4LO>=q(Md0qE>cY^XVV9a@$Z7GwfZ)Zo@Ii);xm$1^P*n#t4${$NKkF|Klx_qS+o|7m?h88N^GM(d@ZR+P4Pd|?5tE7fu)PwJaxgXz_cCrmz68QrSx<5U3a3-!1CxJTB}*V4y?iv$@OSX7I0FY5)D)<tSqw8Xv=1%g6m-zs`4-a#*Xz{3Bjr&g^9t!PAo~amPqfU!k)Ym>Lj$r%(7B;n%h+83Ti8)Vj}Un`RGPrX|A6VZIC!|CaMReuUuMO$OWu6t8VCr8=o2REmh;fX{VdS>yWZ50%lt3ED%(6Cr)fujTA69;*cFR;+Fbv!=0pRt+9K--ed%RyjFy?^deX91_<l8m}DY#IQ)c!em5zM6n;$mDUxWu435cUGD86|8DE4y!Wjo|k=ay)TzswQR_}_Xvzf>v6^gU*d#^%N(+()D{i2JD+3{Df|J=HS%fa0ty%Sq<nk--7V4P_Mu>D`JJf7GYfy`zyMn`ue0=Rh*1hBKB*g}J1+m*&Nj#nA^YeMyaych+0eDEq;t=B~Ovc-8p@1=TGVbgXXn&BaDplzJFo_wKH7y|&ZLgyutSKw_}cm~^-lrCnN0UF^85&dFkDe&l7A(R}uGX59cg6yW0sde5I%I$FF22Oz+1msgoaz3C6H(qye8@+k=@17^gC0)SW^f-pp-|EWEc8wFtgHa|q6Va%Rl(oi#b^BKyfrs^H_g{j=s38g!x-07q?Tss7y#!lC48FSb{buGrEKxW!d?5K0s-jS{gAB2`@Z!E)IL5gbEx-d+y-n>grB0|IUCyv4Q9p`tzFt<P9FVRmyiv>JYixYxQ0=U@8$eEAL4Xh$K8<Qk+|ERkZdyoaOffB@ulMax7kib5<1u`YpSX?2=iytdwi;9rYx;bP<=3wa&~n3cklGQKWvaX1d}3MM+U${DTo7|uyPs@Y8Ce5w?f0UBShl1o&Bz+Q2^lF8<+DCbT^LtwQ(0AHj(54r0NRE}*~_yLtRON(b*;2kepKqLAV!^0!Xo|h7|n;4916nQowcx1jRs{t4%xv@B3KjHmUXVQPU5><<8j*Rn34FV_sc@Rxi)R2GKRB8p`9dd-=MDzcovBk&WM{RX=Wrf&ARDav0E<HP!F#ggS(aX=PDO2r+noUh@jYR@3D(r5pptfq})o8b+j9m#TU^^<@hocJTwJlvf((~B?@{2F&8>&HoGR;Of(AyH}VrlOGl7j)(L?gmx9;2dR0dO##k$O)$yTddlk4b^sP3{EuI62YGFxjWllnrt8i7gGKa%VP-_bxPLlk+vPfFDx<b7l;fg1v!FCZ?oJdwp-%3ex0T?+f7>Ksn`S0wqlB}X6lx8SJ?Y(Mq*#uA&9sr=$2x5<ea4%zZ>8Z1_?5nvyU|v@vrYJWIc)9w{RR?yLvjR$cKtpnBE&*-mFj=O3Nzh@s#BV;n7r^{1K9lErDRuTW$`6ZP8;D;*Ua&?0lQu*!xJ09&j1S!k6LVUGiBy?e*=KLi%x}QYCSjOd0+o=JmbBPOiDr<Fq^N)kv5=yZ%S09!>|nm-sqc%|?YO&iVO=Wa4aRIYd`SOc9h1nO*Y^!7vD}J$u~<^@U{t0NC6)o^<`5iZiMj)w3TG<|Tx>A6sdE0chfl~Y&rE=URx~jqR2{b!8DnMx?Nl=8Hmc+4q4G`7nK%kn=b(>V7Kz^Ju`+Xz5P=Sze2lI_tKva`_N13kg=I&1fjTN*xZB2!4x9TLqVZA27bB*{R2%{x+&tBwI?7a&Wl6zr3v;+EH<}DLmmDi3W#2mS32igPero9=)7et43&b@$4_W?w=gZr%hj?w+7!6vxa`00SWHmD|wI19A`7jIV?R!9?dMS<d=Cys7@?y)7O7&f-hoxuYg9vkJg-J}d`aJp&*{+_N${!hvjcfTN$TxHCG=`E&k5j6#)jkJJ7L2zhq^n{1Co$wyp|G){$v9XHE34(Y&QM=Z?a+uQG=o5);R_?RIu$uxBATP})*{I!L2!>O3Zrj1Z4v5HV1%TGL;yo|__AhJ>iap=Ds1~23OdrlV2q-iFt}7R1jb@YpoVfPg>a!HfUBko#;OO|V}wzxw9Uo7RcacDyEF?d5)1REyK=BqF2bO8JtWBht+F3Y#v|i|<yL6{c5CohUoJ{S`et+QwMJ@YR7i=+;H5ud?l^etbg77Tj$6tT(==ciDXFjyflwYD@bO6yK6L18Lju(bxM9~ZQ7kOw6i9*a!KbUP0Q5N1!cpx}Vw+Ib6#V7p2EY{Q=8au}wHv^goI-h59T2u_2TB~i9f|)5e7Tqzic3p-mF3+#GQJ>7Dub{=RkF@#TLJ1gR+D!q4^;{+8+E{l-<6iz*OG?4b-~#EASzz94VUr3g0wW-BorV^#aK<vAz`G(0kEKiETM>9(zk{ui=|lPA}Szu60-49a%TzMll@fe0FH~sbfCFvcH4Ro$cF{Tf!d!`P8@MlYRcR+R*r;B0>VG4^F8KO1^GGb1-%j=;i%zj4fkOyu_Mq`<H}I-EayIkja0WS;?4oT%D;`tQBG~E8J?=BX`VIVB2oA}K&$Aj!KOr_Zw=nzni5fG(Oru4Lgkuy(~6)_OQyxe>^;3zE8(jrW7*VmC2&g;LfgA4qYp;?g{g=FaD=>*Y5&-+4CZlpmURh+Y>6Wz$k}s&D7xjjnl2EwMsF#ODvPwDvO+txl>A$7aXWkT90wSmq~OtXTEfFqa<&=ScU*#+(<P`0Hd`&J0RDI^H?6|>zYk_w9s_Ewc<f9oOOA0?JWHwTp(&pi5VKdhfYrxXh<dH9PAUk~!L!2lj2_lYAyllqjw)Sc1ox$CMJqk+P*|w=m{={^(#0pmz#^;#%JTz`aBk1?;LP8^T1!kt?yX3@v8Ll$2E8heikM|_Nh5Ay_iq?>$zX>h{ZVQ}$%&;RM>492D{Tm598|g$AkonwLRk{oO|g@7pCj~<ZUx@Bqt>+xnKi=I)RtdbWo`#Uqe%qNs9IjCfovW#93Y2s(UOP|a%FvHg~slJGMFZ6Z2^9V2$e76uomtlMXiWRWoY92dYgh~&{ocQ?Xvpr63dvD#=Zi~qvcbzLm!j<56Tz8lsODVJMJ0KArfrbsHhv3B@1vb1G7ZPr%t;9geU$Rx*d|t%oLb;04vrqI&_02Kg;lj-N%WpTM)7E&OH&guy~_{L$ra3eY>K@$&O02M9}z#r5T#Fes`5{CDYj>+>klTqJpJjb5*I2efUsRg_IMqYsS3zV#H_dA(O$icrtWZoy8I;-|F3YnYK?zD5j6G9`Ff=avL6mijFi%A`(|R&9@3tRU%WF)6lJ;Ha#~%1O<{yv=?EN$OV@m`9`|}g6@c%k{X0^V^9F%XVAQvWRy3oGc#Wjk7|Ju>5SSy=KlXU<2d&f|GAh?{|{&YNgD'
)))

_PRICE_FLOOR = 1
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

_SELLABLE = (
    "STRAWBERRY", "MELON", "MILK", "WOOL", "EGG",
    "TOMATO", "CARROT", "WHEAT", "FERTILIZER",
)
_PRODUCT_BY_ANIMAL = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
_GLUT_WEIGHT = {
    "STRAWBERRY": 2.0, "MELON": 3.6, "MILK": 2.0, "WOOL": 3.2,
    "EGG": 1.5, "TOMATO": 1.3, "CARROT": 1.0, "WHEAT": 1.0,
    "FERTILIZER": 1.0,
}

_WEED_STATE = {0: {}, 1: {}}

# ── NPC demand data ────────────────────────────────────────────────────────────
# Town center consumes 1 of each product (excl. FERTILIZER) per 12 turns.
# After day 10 → 2/12t, after day 20 → 4/12t.
# Shops each consume their products every 4 turns when unlocked.
_TC_BASE_PER_4 = 1.0 / 3.0  # 1 unit per 12 turns expressed as per-4-turn rate

# Per-shop demand per 4-turn tick (matches borg.md shop table)
_SHOP_DEMAND = {
    "BAKERY":         {"EGG": 1.0, "WHEAT": 1.0},
    "PIZZA_SHOP":     {"MILK": 1.0, "TOMATO": 1.0, "WHEAT": 1.0},
    "BRUNCH_SPOT":    {"EGG": 1.0, "WHEAT": 1.0, "STRAWBERRY": 1.0},
    "YARN_STORE":     {"WOOL": 2.0},
    "ICE_CREAM_SHOP": {"STRAWBERRY": 1.0, "MILK": 1.0, "WHEAT": 1.0},
    "PET_CAFE":       {"CARROT": 2.0},
    "SMOOTHIE_SHOP":  {"STRAWBERRY": 1.0, "MILK": 1.0},
    "FARMERS_MARKET": {"WHEAT": 1.0, "CARROT": 1.0, "TOMATO": 1.0, "STRAWBERRY": 1.0},
}

# Maximum possible shop demand (all shops unlocked) — used as fallback
_MAX_SHOP_DEMAND = {}
for _sd in _SHOP_DEMAND.values():
    for _k, _v in _sd.items():
        _MAX_SHOP_DEMAND[_k] = _MAX_SHOP_DEMAND.get(_k, 0.0) + _v


def _npc_eff(item, day, obs=None):
    """Effective NPC demand per 4 turns.

    Uses actual unlocked shop state from obs when available.
    Correctly separates shop demand (static) from Town Center (scales with day).
    """
    if item == "FERTILIZER":
        return 0.0
    # Town center component — scales with day phase
    tc_mult = 4.0 if day >= 20 else (2.0 if day >= 10 else 1.0)
    tc = _TC_BASE_PER_4 * tc_mult
    # Shop component — sum over unlocked shops
    if obs is not None:
        town = _get(obs, "town", {}) or {}
        unlocked = set(_get(town, "unlocked_shops", []) or [])
        shop = sum(
            _SHOP_DEMAND[s].get(item, 0.0)
            for s in unlocked if s in _SHOP_DEMAND
        )
    else:
        shop = _MAX_SHOP_DEMAND.get(item, 0.0)
    return tc + shop


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands":  [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _align_hands(action, obs):
    action   = _copy_action(action)
    seat     = _seat(obs)
    farm     = _farm(obs, seat)
    expected = len(_get(farm, "hands", []) or [])
    hands    = list(action.get("hands") or [])
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


def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )


def _trace_actor_action(actions, step, actor):
    trace = actions[min(max(int(step), 0), len(actions) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, actions, step):
    """DIG on WEED tile, then replay original action + up-to-8-step catch-up."""
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

    for actor, txn in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - txn["start"]
        if age == 1:
            unit_actions[index] = list(txn["intended"])
        elif 2 <= age <= 9:
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
        active[actor]        = {"start": step, "intended": list(intended)}
        unit_actions[index]  = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"]  = unit_actions[1:]
    return _align_hands(action, obs)


def _shed_access(size):
    half = size // 2
    return {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}


def _projected_shed(obs, action):
    """Estimate shed contents after pending DROP/PLACE actions this turn."""
    seat        = _seat(obs)
    farm        = _farm(obs, seat)
    private     = _get(obs, "private", {}) or {}
    projected   = {
        k: max(0, int(v or 0))
        for k, v in dict(_get(private, "shed", {}) or {}).items()
    }
    inventories = list(_get(private, "inventories", []) or [])
    positions   = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    acts        = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles       = list(_get(farm, "tiles", []) or [])
    access      = _shed_access(len(tiles) or 10)

    for index, unit_action in enumerate(acts):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        if tiles[y][x] == "LOCKED" or not isinstance(unit_action, list) or not unit_action:
            continue
        inventory = {
            k: max(0, int(v or 0))
            for k, v in dict(inventories[index] or {}).items()
        }
        if unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item      = unit_action[1]
            tile      = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if (
                structure is not None and isinstance(tile, dict)
                and tile.get("kind") == structure and "animal" not in tile
            ):
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


def _safe_market(obs, action):
    """Clamp SELL quantities to projected shed so we never over-sell."""
    action    = _align_hands(action, obs)
    remaining = _projected_shed(obs, action)
    market    = []
    for raw in action.get("market", []) or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL":
            item = order[1]
            try:
                requested = max(0, int(order[2]))
            except (TypeError, ValueError):
                requested = 0
            quantity = min(requested, max(0, int(remaining.get(item, 0) or 0)))
            if quantity <= 0:
                continue
            order[2]        = quantity
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - quantity)
        market.append(order)
    action["market"] = market[:10]
    return action


def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear": return value
    if name == "sq":     return value * value
    if name == "sqrt":   return math.sqrt(value)
    if name == "log":    return math.log1p(value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, bf, bt, af, at_ = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = bt * base / _shape(bf, scale)
        price     = base + amplitude * _shape(bf, equilibrium - inventory)
    else:
        amplitude = at_ * base / _shape(af, scale)
        price     = base - amplitude * _shape(af, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))


def _impact_score(obs, order, opponent_exposure=None):
    """Coins lost to price impact × NPC-demand persistence bonus × opponent threat.

    Items whose price drop is permanent (low NPC demand, e.g. MELON,
    FERTILIZER) receive a small boost so they sort first when raw impact is
    similar — their market damage accumulates across turns, whereas high-demand
    items (WHEAT, STRAWBERRY) naturally recover between turns.
    Max bonus is 10 % (persistence=1.0 → factor 1.10, WHEAT at day 20+ → 1.00).

    When opponent_exposure is provided, items the opponent also produces get a
    further 20 % boost per unit of threat — race to market before they flood.
    """
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market    = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices    = _get(market, "prices", {}) or {}
    cur_inv   = int(_get(inventory, item, 10000) or 0)
    cur_quote = float(_get(prices, item, _market_price(item, cur_inv)) or 0)
    later_q   = float(_market_price(item, cur_inv + quantity))
    price_impact = float(quantity) * max(0.0, cur_quote - later_q)

    day         = int(_get(obs, "day", 0) or 0)
    npc         = _npc_eff(item, day, obs)
    # persistence in (0.05, 1.0]: FERTILIZER→1.0, WHEAT@day20→~0.05
    persistence = 1.0 / (1.0 + npc)
    base_score  = price_impact * (1.0 + 0.10 * persistence)
    threat      = float((opponent_exposure or {}).get(item, 0.0))
    return base_score * (1.0 + 0.20 * threat)


def _impact_slots(obs, action, opponent_exposure=None):
    """Move SELL slots with highest self-price-impact to execute first.

    When opponent_exposure is provided it is forwarded to _impact_score so
    contested products receive a sort-priority boost.
    """
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows   = [
        (_impact_score(obs, o, opponent_exposure=opponent_exposure), -i, list(o))
        for i, o in enumerate(market)
        if _is_sell(o)
    ]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked         = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(o) else o for o in market]
    return action


def _opponent_exposure(obs):
    """Opponent production weighted by NPC glut-threat.

    Items with low NPC demand (MELON, FERTILIZER) that the opponent also
    produces represent a bigger glut threat because the oversupply persists.
    Threat weight = 1 / (1 + npc_eff * 0.1): ranges from 1.0 (FERTILIZER)
    down to ~0.33 (WHEAT at day 20+), giving no-recovery items 3× the weight.
    """
    seat     = _seat(obs)
    farms    = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    exposure = {item: 0.0 for item in _SELLABLE}
    day      = int(_get(obs, "day", 0) or 0)
    for row in (_get(opponent, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            crop    = str(tile.get("crop",   "")).upper()
            product = _PRODUCT_BY_ANIMAL.get(str(tile.get("animal", "")).upper())
            yield_u = float(tile.get("yield_units", 0) or 0)
            if crop in exposure:
                threat_w            = 1.0 / (1.0 + _npc_eff(crop, day, obs) * 0.1)
                exposure[crop]     += threat_w * math.log1p(max(0.0, yield_u))
            if product:
                threat_w            = 1.0 / (1.0 + _npc_eff(product, day, obs) * 0.1)
                exposure[product]  += threat_w * math.log1p(1.0 + max(0.0, yield_u))
            if tile.get("fertilizer_available", False):
                exposure["FERTILIZER"] += 1.0   # FERTILIZER has 0 NPC → threat_w=1.0
    return exposure


def _terminal_market(obs, action):
    """Final step: sell everything, priority = opponent exposure × glut
    sensitivity × NPC-no-recovery urgency × price × log(qty).

    NPC urgency: items with no NPC demand (MELON, FERTILIZER) must be sold
    FIRST — if we sell them later the market is already flooded and they won't
    recover.  Factor = 1 / (1 + npc_eff × 0.08): ranges from 1.0 (FERTILIZER)
    to ~0.38 (WHEAT at day 20+).  Town Center phase (2× day 10, 4× day 20)
    scales all NPC rates, so in late game high-demand items get an even larger
    discount (they recover faster), increasing the urgency gap.
    """
    action   = _align_hands(action, obs)
    shed     = _projected_shed(obs, action)
    prices   = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    exposure = _opponent_exposure(obs)
    day      = int(_get(obs, "day", 0) or 0)
    rows     = []
    for index, item in enumerate(_SELLABLE):
        quantity = max(0, int(shed.get(item, 0) or 0))
        if quantity <= 0:
            continue
        npc_urgency = 1.0 / (1.0 + _npc_eff(item, day, obs) * 0.08)
        score = (
            (1.0 + exposure.get(item, 0.0))
            * _GLUT_WEIGHT.get(item, 1.0)
            * npc_urgency
            * max(1.0, float(prices.get(item, 1) or 1))
            * math.log1p(quantity)
        )
        rows.append((score, -index, item, quantity))
    rows.sort(reverse=True)
    action["market"] = [["SELL", item, qty] for _, _, item, qty in rows[:10]]
    return action


_NO_RECOVERY_ITEMS = frozenset(("MELON", "WOOL", "FERTILIZER", "STRAWBERRY", "MILK"))


def _preterminal_no_recovery(obs, action):
    """7 steps before end: sell no-recovery items before both players pile in.

    MELON (sq/3.6×) and WOOL (sq/3.2×) crash to $1 on even modest oversupply
    and have near-zero NPC recovery.  Bleeding them 4 steps before the full
    terminal nets meaningfully higher prices than a single end-step dump.
    """
    action  = _align_hands(action, obs)
    shed    = _projected_shed(obs, action)
    market  = list(action.get("market") or [])
    current = {str(o[1]) for o in market if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"}
    for item in _NO_RECOVERY_ITEMS:
        if item in current or len(market) >= 10:
            continue
        qty = max(0, int(shed.get(item, 0) or 0))
        if qty > 0:
            market.append(["SELL", item, qty])
    action["market"] = market
    return action


_BASE_PRICES = {
    "STRAWBERRY": 120, "MELON": 250, "MILK": 160, "WOOL": 200,
    "EGG": 50, "TOMATO": 60, "CARROT": 35, "WHEAT": 25, "FERTILIZER": 100,
}
_PRICE_GATE_THRESH     = 0.30   # skip sell if price < 30% of base (catches mid-crash)
_PRICE_GATE_FORCE_DAY  = 28    # always sell in last two days regardless of price
_PRICE_GATE_SHED_LIMIT = 90    # bypass gate if shed is near capacity


def _price_gate_sells(obs, action, opp_sold=None):
    """Skip SELL orders where price has crashed to extreme lows (<20% of base).

    The threshold is intentionally conservative so normal route sells are never
    blocked — market prices during normal play are 30-80% of base and must go
    through.  Only genuine floor-crashed prices (opponent flooded the market far
    below equilibrium) are held back.
    """
    action = _copy_action(action)
    day = int(_get(obs, "day", 0) or 0)
    if day >= _PRICE_GATE_FORCE_DAY:
        return action
    shed = _projected_shed(obs, action)
    if sum(shed.values()) > _PRICE_GATE_SHED_LIMIT:
        return action
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    market = []
    for raw in list(action.get("market", []) or []):
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and order[1] in _BASE_PRICES:
            item      = order[1]
            cur_price = float(prices.get(item, _BASE_PRICES[item]) or 1)
            if cur_price < _BASE_PRICES[item] * _PRICE_GATE_THRESH:
                continue  # extreme floor crash; NPC demand will recover it
        market.append(order)
    action["market"] = market
    return action


_PREMIUM_ITEMS   = frozenset(("STRAWBERRY", "MELON", "MILK", "WOOL"))
_PREMIUM_WINDOW  = (120, 680)
_PREMIUM_MAX_QTY = 30
_SHED_OVERFLOW   = 75   # earlier force-sell prevents lost end-of-day drops
_WHEAT_BUFFER    = 10   # extra wheat to keep beyond feeding need


def _farm_fingerprint(farm):
    counts = {}
    for row in (_get(farm, "tiles", []) or []):
        for tile in (row if isinstance(row, list) else [row]):
            if not isinstance(tile, dict):
                continue
            a = str(tile.get("animal", "") or "").upper()
            c = str(tile.get("crop",   "") or "").upper()
            if a: counts[a] = counts.get(a, 0) + 1
            if c: counts[c] = counts.get(c, 0) + 1
    return counts


def _clone_distance(fp_a, fp_b):
    keys = set(fp_a) | set(fp_b)
    return sum(abs(fp_a.get(k, 0) - fp_b.get(k, 0)) for k in keys)


def _clone_threshold(obs):
    """Day-adaptive clone threshold: wider early game when farms haven't diverged yet."""
    day = int(_get(obs, "day", 0) or 0)
    return 12 if day < 10 else 8


def _premium_shift(obs, action, step, thresh=8):
    """Advance-sell premium items up to 2 steps early when farms are converged.

    step+1 tranche: qty // 2  (half the planned sell, one step ahead)
    step+2 tranche: qty // 3  (a third of the planned sell, two steps ahead)
    Each item is only advanced once (first match wins across both offsets).
    """
    if not (_PREMIUM_WINDOW[0] <= step < _PREMIUM_WINDOW[1]):
        return action
    seat     = _seat(obs)
    farms    = list(_get(obs, "farms", []) or [])
    my_farm  = _farm(obs, seat)
    opp_farm = farms[1 - seat] if len(farms) >= 2 else {}
    if _clone_distance(_farm_fingerprint(my_farm), _farm_fingerprint(opp_farm)) > thresh:
        return action
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    current_sells = {
        str(o[1]) for o in (action.get("market") or [])
        if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"
    }
    action  = _copy_action(action)
    market  = list(action.get("market") or [])
    prices  = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    for offset, qty_div in ((1, 2), (2, 3)):
        if step + offset >= len(_ACTIONS):
            continue
        future_market = list((_ACTIONS[step + offset].get("market") or []))
        for order in future_market:
            if not (isinstance(order, list) and len(order) >= 3 and order[0] == "SELL"):
                continue
            item = str(order[1])
            if item not in _PREMIUM_ITEMS or item in current_sells:
                continue
            # Skip advance if price is already crashed below 55% of base.
            # The route will still sell at the scheduled step — we only skip the
            # extra advance tranche so we don't pile on a flooded market.
            base_price = _BASE_PRICES.get(item, 1)
            cur_price  = float(prices.get(item, base_price) or 1)
            if cur_price < base_price * 0.55:
                continue
            future_qty = max(0, int(order[2]))
            shed_qty   = max(0, int(shed.get(item, 0) or 0))
            advance    = min(_PREMIUM_MAX_QTY, shed_qty, future_qty // qty_div)
            if advance <= 0:
                continue
            market.append(["SELL", item, advance])
            current_sells.add(item)
    action["market"] = market
    return action


def _expand_route_sells(obs, action, thresh=8):
    """When farms are converged, expand route SELL qty to 1.5× (capped at shed).

    Sells 50% more than the route planned rather than the full shed — keeps
    price impact proportional and preserves inventory for later route windows.
    """
    seat     = _seat(obs)
    farms    = list(_get(obs, "farms", []) or [])
    my_farm  = _farm(obs, seat)
    opp_farm = farms[1 - seat] if len(farms) >= 2 else {}
    if _clone_distance(_farm_fingerprint(my_farm), _farm_fingerprint(opp_farm)) > thresh:
        return action
    shed   = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    action = _copy_action(action)
    market = list(action.get("market") or [])
    for order in market:
        if not (isinstance(order, list) and len(order) >= 3 and order[0] == "SELL"):
            continue
        item      = str(order[1])
        route_qty = max(0, int(order[2]))
        shed_qty  = max(0, int(shed.get(item, 0) or 0))
        expanded  = min(shed_qty, route_qty * 3 // 2)   # 1.5× route qty, not full shed
        if expanded > route_qty:
            order[2] = expanded
    action["market"] = market
    return action


def _merge_sells(action):
    """Merge duplicate SELL orders for the same item preserving original order.

    Keeps the first occurrence of each item at its original position with the
    summed quantity; drops later duplicate SELL orders for the same item.
    This preserves the SELL-before-BUY ordering the route uses to ensure coins
    are available for BUY_PRODUCT orders.
    """
    action    = _copy_action(action)
    market    = list(action.get("market") or [])
    sell_totals = {}
    for order in market:
        if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            sell_totals[item] = sell_totals.get(item, 0) + max(0, int(order[2]))
    seen_sells = set()
    merged     = []
    for order in market:
        if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            if item in seen_sells:
                continue
            seen_sells.add(item)
            merged.append(["SELL", item, sell_totals[item]])
        else:
            merged.append(order)
    action["market"] = merged[:10]
    return action


def _overflow_sells(obs, action):
    """When shed is full, force-sell the most plentiful items not already being sold."""
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    total   = sum(max(0, int(v or 0)) for v in shed.values())
    if total < _SHED_OVERFLOW:
        return action
    action        = _copy_action(action)
    market        = list(action.get("market") or [])
    current_sells = {str(o[1]) for o in market
                     if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"}
    items_by_qty  = sorted(
        ((item, max(0, int(shed.get(item, 0) or 0))) for item in _SELLABLE),
        key=lambda x: -x[1],
    )
    slots_left = 10 - len(market)
    for item, qty in items_by_qty:
        if slots_left <= 0:
            break
        if item in current_sells or qty <= 0:
            continue
        market.append(["SELL", item, qty])
        current_sells.add(item)
        slots_left -= 1
    action["market"] = market
    return action


def _fertilizer_sell(obs, action):
    """Sell any fertilizer sitting in the shed every turn.

    Replay analysis shows the route collects ~293 fertilizer/game but only sells
    ~27 — ~182 units are discarded when the shed fills up with other items.
    Fertilizer market is stable (linear ±0.4, T=200) so selling every turn is safe.
    Only adds the order if FERTILIZER isn't already being sold and a slot is free.
    """
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    qty     = max(0, int(shed.get("FERTILIZER", 0) or 0))
    if qty <= 0:
        return action
    market = list(action.get("market", []) or [])
    if any(isinstance(o, list) and len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER"
           for o in market):
        return action
    if len(market) >= 10:
        return action
    action = _copy_action(action)
    action["market"] = market + [["SELL", "FERTILIZER", qty]]
    return action


def _wheat_buffer_sell(obs, action):
    """Sell wheat beyond what animals still need for the rest of the game."""
    if any(isinstance(o, list) and len(o) >= 2 and o[0] == "SELL" and o[1] == "WHEAT"
           for o in (action.get("market") or [])):
        return action
    seat    = _seat(obs)
    farm    = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    day     = int(_get(obs, "day", 0) or 0)
    tiles   = _get(farm, "tiles", []) or []
    n_animals = sum(
        1 for row in tiles
        for t in (row if isinstance(row, list) else [row])
        if isinstance(t, dict) and t.get("animal")
    )
    days_left    = max(1, 30 - day)
    wheat_needed = n_animals * days_left + _WHEAT_BUFFER
    excess       = max(0, int(shed.get("WHEAT", 0) or 0) - wheat_needed)
    if excess <= 0:
        return action
    action = _copy_action(action)
    market = list(action.get("market") or [])
    if len(market) < 10:
        market.append(["SELL", "WHEAT", excess])
        action["market"] = market
    return action


_prev_market_inv  = {}
_opp_flood_steps  = 0   # cumulative count of steps with large opponent dumps this game


def _detect_opponent_sells(obs, step):
    """Update market-inventory tracker and detect opponent flood/dump behaviour.

    Returns items the opponent likely sold last step (inventory jumped >3 units).
    Side-effect: increments _opp_flood_steps when a >20-unit jump is observed.
    """
    global _prev_market_inv, _opp_flood_steps
    if step == 0:
        _prev_market_inv = {}
        _opp_flood_steps = 0
    market    = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    opp_sold  = set()
    for item in _SELLABLE:
        prev = _prev_market_inv.get(item, -1)
        if prev < 0:
            continue
        curr  = max(0, int(_get(inventory, item, 0) or 0))
        delta = curr - prev
        if delta > 3:
            opp_sold.add(item)
        if delta > 20:
            _opp_flood_steps += 1
    _prev_market_inv = {item: max(0, int(_get(inventory, item, 0) or 0)) for item in _SELLABLE}
    return opp_sold


def _is_flood_opponent():
    """True if the opponent has dumped large volumes (>20 units) on 3+ steps."""
    return _opp_flood_steps >= 3


def _opp_hold_sells(obs, action, opp_sold, step):
    """Defer a SELL order by 1 step when the opponent just flooded that item.

    Only defers if the route plans to sell the same item in the next 2 steps —
    otherwise we might miss the sell entirely.  Never defers in the last 10 steps.
    """
    if not opp_sold or step >= len(_ACTIONS) - 10:
        return action
    action = _copy_action(action)
    market = list(action.get("market") or [])
    # Items the route plans to sell in the next 2 steps
    future_sells = set()
    for offset in (1, 2):
        if step + offset < len(_ACTIONS):
            for order in (_ACTIONS[step + offset].get("market") or []):
                if isinstance(order, list) and len(order) >= 2 and order[0] == "SELL":
                    future_sells.add(str(order[1]))
    held   = set()
    kept   = []
    for order in market:
        if (isinstance(order, list) and len(order) >= 3 and order[0] == "SELL"
                and str(order[1]) in opp_sold and str(order[1]) in future_sells):
            held.add(str(order[1]))
        else:
            kept.append(order)
    action["market"] = kept
    return action


def agent(obs):
    try:
        step     = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        thresh   = _clone_threshold(obs)
        _detect_opponent_sells(obs, step)   # updates market-inv tracker + flood counter
        action   = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), _ACTIONS, step)
        action   = _safe_market(obs, action)
        action   = _premium_shift(obs, action, step, thresh=thresh)
        action   = _safe_market(obs, action)
        exposure = _opponent_exposure(obs)
        action   = _impact_slots(obs, action, opponent_exposure=exposure)
        action   = _merge_sells(action)
        action   = _price_gate_sells(obs, action)
        action   = _safe_market(obs, action)
        if step >= len(_ACTIONS) - 10:
            action = _preterminal_no_recovery(obs, action)
        if step >= len(_ACTIONS) - 3:
            action = _terminal_market(obs, action)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands":  [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs):
    return agent(obs)
