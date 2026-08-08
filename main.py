"""Kaggriculture agent — MapleLeaf 4.9
Route:   ep=90794783 P1 (best of 400 candidates from 200 top-player replays;
         benchmarked vs 4.6 — 10 games each)
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + Town-Center-phase-aware terminal liquidation
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -13)
         + price-gate: day-adaptive threshold (35/30/25% by phase) floor-crash defense
         + fertilizer sell: sell excess above route PICKUP reserve (new in 4.9)
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 4.8 V2: fixed and wired _fertilizer_sell — route has 84 FERTILIZER units reserved
           for PICKUP/FERTILIZE actions; _FERT_RESERVE[step] ensures we only sell
           genuine excess, capturing ~650/game extra revenue without disrupting farm.
           _overflow_sells and _opp_hold_sells remain unwired: both cause regressions
           (overflow sells items route needs for BUY/animal-feed; opp_hold infinite-
           defers in mirror play even with corrected _detect_opponent_sells).
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<O>bM-k^L`Pb0L07_Usg!iG`>wLy|*u8bqUkWH3OGEP7@)nEyVqMUjuMs!pA%TbHCAuS`=U-~GPzaq663{`cZPfBXHPfB*gBKYqFRbo2Olv6)=_*Khy&+kZd5@%-|izy1D?zyHtk>t8ND+&-+H|H{4i!{?uWz4>_i)6Lz*<l^1^`eHH@Z$Exmtv(I@@VHvNe|~%YVRiF#F}WVS{nP61{^P}Dy8HO2hx_-R-#zWWvD|F_Z*tI|+joEd{AvHB>7Z}FT&!1*PhZ>m@&4iI!`D~4w?;1x2jX#ccej7)^vlP_Z&?l5e`nB;-Cu{}bbI&y*XQ|o`n(-bu4(GHh~{j6LTkc)r0hqk&*mSoZPmPgKgYj5Xw81kmDwM^1^W5v?&jTUH*N=ykbTo0Dqewy{c*TK4hMJJj4vzb%WpmZ|Krnc)9CL+p8W1+Jb<INJP*~))9PXL>h+=fPmP*^Ms{=<?HVy``ReA;czWoU_dh6yY4?cTi^u!V&Tz>mC<}ep;@uC|4%c{1l#iNN0<!(eGhbfhCVt;uG-EA;CXb)NVbC;M+f~C%^JMtx#CV~_CO2ozz>N>W4kJjcH~9{KWl`%64PWM5*uFDp=l&h*QMm^wgSGq9=#j}D?At4T_~k|5chN_IF$KQ%x(b=kS{H5LhD0B|zq?z#d;0Z{tB0rCyW78h9kuE%9HTvBBM*G^^*sC0^ya2Vw#tu>LYH>ywhg9WvatQxfWx`{zydm)k)0m;w(Tdh+5GU^tW$>9eauGaHB6B<$YCn*Tq_4jy5hV|B+kCrqwNvi+qZ5TlmSLfs2bwElN672M8-%N;(({weGN<ZqiTQ$OCVu(j@{>^mv`(ZH<;Ryt1EFY#g5s6ODJ>o^jL?v+qmKE%b$2%u9Ece7Q8pS=eS2%;sEP-_l8EyKgjKyHZ^4K(R9=`7Iy!?r>|sPj?s%ISA)r?jMHy%TYJ*WONsq3;kY<I*v(9zlzD-6bhY75GD7ShZXW&;zq7_Bz8baPHYFV=QOwBTm>}zY|J&n4M&|A_0?AF&CYRN2veFZ$#p~Trd&3NBXH=7at95{P=b+E4t+ocsW;j{<A3S(BK7VqqK!(w`Oj3tjQ=(_*B+1+>v!baSg}Jno*_GE9%8WMtqLsKopp@ArW0bspc|L%&*oKO<8K(XH&K55seG;CH*LiHO`~B^oIynUNo-6V`TOw)15osAe9ph%9F?(rXY{;~B<iJT4P8K_Q-?JxqEa&rE%W5_GhR5&&BmRhe?4LBL1?=bZNNNR=CXHFGy@{8~sZmL>OvDp7B(=ffX205B#)K0co}mhdt!j!o+6QBFXEM3fhGwhDZmsX{pZ}R&B7fw|pgmiY?;9!-wqDHR)5FdB537fVpP!%k)<k{GHW??5aM>o28jH{!tyCDuK%#WE<qP^`nGxaRahr{HNi?f$R{*ikn-O~CQh_uFp6=Tpxa+~E7y4@kmYf@*SATD?#nL9DfB|by=87*OH<G<>l)8lQ5GWIxnnz%_DbaBpJ4Y8uuZ5+x2own!gPLA$(r5v7F8j7hZ2#!VxyY#Il;4ccKsZjpOa?ovp*)gxi-f1I0LSEvS77!!8gNS4fp*xN8O5Y|t~N`ZQDd0gU0}T3lu=W%jBZ1<`E(l*aIB5}ru`Ki`hl`FX*I#IuGo6{fE=g?>Nb1G(~+e&FoD>HTeMsQFeTpK(buZlrWE(6Q+6V740iOU0bfq~B*0@?BnpVN#M#w`$7~<^a?@<#vVEM%GCNstm91cw7qm2JNb{VXQTMjhuf0YL5&|XQ^RLAd877~{mbFq?pRlLI;*j<+z%z8UmUb_YUG66wx9c!q7^#?$wm835dAec?sO78;*9C9p5$nU58)k8=BVZ-BmSsZ0m(UZo-%(?}+8&OW1B83&924#U$>u}w84ru1z=#J25MBHWw}P-}%>w4wu;5de|7kVXpkOC+b<tYb6j+cg1CsmQaTt4<LLU8ed-vy8Zl4jC&ddn@Uxf|BSOk6Q$Er<si<m8F7^`D!)r7q<<qal{N8NyJ<HA8F1a;2Y4QY%J!w4;D$+pMF_Lhoq1v5a(>iDp0{+fA)V`1pcB?Qs+5rbN8m;;09#!Nfe5ckYTP%D{VIytjcxfl@dk`h+kKex&5r|t0Ux@fWqcl}np4vk)k_qk-h_s`-d-)uv&n;>0Gl^F4z1k1LEaW9eOx@(s+_)&2;ShqwVG7E2#r`hgdU(vpkRwUK#=Zw`VpR15I)y%E5Uk3pJ8OCe^&hXZATfj8<q&x#t-Gjy^{d|+h0=;Rq`dRaT1^_fujx{vIW|<^QO|YW+)SR=NtB{}xWokf!u0x^~s05C59c&m(kC-)U7E+Ps_QWw7BDEYbQfFG=cj<$pw}xR(rM{W0m8C+aptVl@SuflU!Yr(rQ6`C&jn+@x0yt@L(!SLSxHue@YJ&%;Y_2ulPvtucplVd3886E4=E*yZ;0{4KqTtp?YjzP?v($3X*Qm1nupedd92Y@**T9ofHjlE4^58U>!O=$L{lony4gsylu3Zysw#kC8#JZK<6B<s?>Ya7ia;PGhg6$#f#(Vcd%nusqnZ2pzH4Q|5<4c>93xQzbA5diE8c3H;F2!iUz(J@vyO{;v;K6W>R%Phi6#Y<Ba!evF?%8t7u-3Ppgz94nbqXp&r_9z%*6u1&g~NK|6$92FU&6x646l4xNi>@mV9a3rLHVO!Av19>v_`y_SaK;a+fa98{N~L3WUQMOo)jQR8c@M5jBcU5IWyl>x`@LcGWh_2EX;jzy-A??q%Ht1I&mO2RD?bfd69R|bvc4iECo=~2GEZT#9p&>BLGbfx44^TMfD**ryk&&#evsGjeMk|oylPl?yz`)g8o^1^)j$m<)%f^92wRLEJ`ybMD%H)?A6Pny=uHoiJI6UAZG0b*F29vM&Xdq(S*ZZD4t895*ndBHr5B!tYV-IYcD7%YkGq&W|<8N<_*r0SM`%!j!GDp-p<O^yO{Rf&Po<MxL79~mt#{cHVUUH$#YPlgMcUj`(YF^iEUUl&>G5>ua32L`N+vt2D&9LlO$#!ycP-6?$ss$r;uHXbc8;YlzQPr{DY4y>~D@#Oh(ylnTow$y-RLC**zz*5bne>(hDJU+13|t<(Y#9H&diTZF|Y94ehWLkG7veC8wpkrZjM<n}2WGf`WFKNC^uL{ik$^>Rd6`-fRMJM_hwo!yanL?|_SLdk{^ao@v0qx0~Q$5;84YR7JSFR)z~*`6R|-vEdm3-R7w<h7xK@dtLjUY)&^7EHkyLfdZH?Nw2p>tBS?t1Qs1Y5sPHvGLXK2$hWeX$J!~~6$9qOZEC7L?ehyz(9@3ba<+*Sw>pCawR{OA&oTmjP=bRV8lFe1awWcs`%VR41Ni_u{tW|#^!!f=^FkYG?YJY$H+)kbRuX%&9f;Z`xooUJwy?=nI7AcYC*hq?rQ38$Bi9zvbMO)k-&0-2u&i2x<6O5EY)HIFp)WPRJ~#Bp$fCGDk*^mk-b0G4nnSqQ1X$Yk0T<X%R9H(;;I*;7%HgszzEImLpt&X&^KujC;Guk3WEnWAF`o2y;+xYnpHJ8+hE%6D)00Q?W_)E#B3R5yN$ij~(1k^_*ym9Z*dYMkK-^0#MFZdXSqZ8ky=NewD8PI~^1L~znbyX$Q<X0?Ko?&1Rw<bZ8KNQCu0nf+J*xr(FRzui8&-2y&-;g2(DdWVaVFCRE7}s^Z#|vUAj&C|33nh!F%Thi#R!<iy$CICZCdSMEu{2VQ81v<0$ywaUcH?yl(`CdQg|_eb*)~ZO#9&yR=237wLNV2RSic!lEAFZqKXg&2;oImg47H}4OOa`0+mGN(U4>n6B{y7kf~Q^kYiq)caGUh=;h-HOftDNVh~CpuL}#Yffd;|g*+>CQ33?aMakpKb~oNg9@~+J<ND-*>V=3A7;&s+hS_!&n6k3|OD^DM^2)f<y?<M|`f%I`Ccd*J%1!xbjxeJ(8*Lix%t`mQ)?Je~LkcrafUyuDMppc=>1p34S0>AQjN&a0D(<(mbSdsi377}T>S5^!A-S%vmo^JJPWahU3ci?cj+kw1hA@9SiB;VTe6u+n=iZxtn*{cvfr0$0fFR%`+3JS;^>>%8E(0a&b_>OXTalTL<avR4PgKh1Qq_x174#G*2aB@PN|Z+F!bvczaDfMBD`5pvu6CE~XG=YP+VjOOQ&mzrQsBE@MSSM^Y0ygRtAw-&?V<j;=?IWCD9IDw9z_J+k%g|D93>fL=|DiPd@s#UV6^Mf%31+B1M-$@F<6DZBA7H%YLgI~>|?SsMaFH6GLRjT;vVUpFs9PPYQ9j(!%C?Lylg#VMPc%m2{`teM1=St6IqLUKnX;dS5_*?0Wo5ORRUZzt)X7RIhF<INBHWpt>GQ~&QVtM+#1NYrYVJdf_R37zJI~@_lRsPj~d>J<M5YfRCBF-Lx>)$f4RbcVQaaMnrc^@J2yNmUXZd|f*!F-BE5E+Ev9!KA9bLLC2@Hk0D!|u-hTgZsg-5p>p=p8N)xl`OjX0VVGGurD#6g__NFf7jF!U{lnn)%o?)n*Gg-Q0As;YY))psgRh&o&AF!tdm@Z}$g3s_$Wmx*#52JB-ii20xt8~t=)@kRQdvt(JryMH*se}1ERLia1z`|%41_gSpt4xu;a;mk5UbD-J5_U&eeHxrXs@5t2jxbJY&Ip#u!wK^<D^09lJYruE;f{DY6WG|<{sxk&lp`;rMus*KsACA^p&4(O631LgNK@Myp{rltW<2~Hj~mlu3Rs?NbSq^YvJ;LAm}!mKT{pmKN`g&JmBaMh@H9sFNonYj!%xf$E7jtKlx7{+ASj^{;>rhGO;rj4hUf5tz~ueO_R-Km+kMw*kB0982rSZ133tVVAQJ9*fbShUra{$_9;&U<kMOK>I4{cjvz$b}Q}cY#tBZpHaXDgmQaQ3n9GOy-Toa^Y(aG}iXv9{6CqNu}VP72$+z|bUE~v_M*(r6B&XDyYDl^mI`AT|{S|SWEEr@?9sLU#Rf$0JYca95Y3#qzjcLco|?4wlQGR`1J@H7cFC-#-1D{AcB?V1?s^(_LV-O9o@#tI<3P~HwHp9M&5mEtfsHJ&xX6q7Rdbu(&H22Sjzp^zYAFaYXX0YH-qfJXwzC^AB_*CYdE93KY2Tp<)zQ|OLpL=2}hJ}KPOVS3pnxzVmdi_I(rK=hVS%#D^vDI+s{U*J+w^qF4~OtVF0d?(AgapICF%~9o<mE)0`tY|}XgZt_^aLwz()KNjvM>e~`+wU#}fz$L&otbu1gi!8eJ;)Zp#b-1lpbL-Ep&WoMSI(F9h)8*h&PzAE9XZ!CtD-?<m3cRhE1=S2+B}*?w$Sw?SmhO_2qh_js&=2^=XYk?^%5XbhPlRIiHts*{$_`|BW%1ntDKp|N)fe%h{7?mZzF!R;`nmqO$H8u-jXmbfnpIbL!YU%ly`^=>rtXN()n>9Z~zVV;>Co;iWHAxWD-vg8jtWM01gBluNFXw^qsZa0Rdnd5esVZ1LL)i7H4BK+VmDFP1T|I`$ho*q@3@AAjBKP*Iwko6{E7DGgH(!r5BDeM+|@>Rqo9}C3Ncv<mjS)V`a$=lQAuCvAlnD&rO;*(1JO=Cl1rQX_P-0ehizSY^9Y6kfo>#=xT&IID~M=RKSoI70H2PwXVUWN|T?NF9+hb4pxoE)eR{mL8SC2#@_%P8scVXnx{NM0`mwdRzAWHq$X)v0E$RekdS_9%?u^b5TL>YdXpHhlHWWW6e7EA@KK<o@x6Ibv-knv1Oo(um8a2ph(v@GcNhi{;&?hds)qB4;za=)P+8On1))dbd`{Z!AgZ$uDnOC83JJ9026w{lOr#Rxa}U!Rv}my-giFpjSCit(lQlR22e4wy(~ys=s!TKGJhGOkQ@fIK82yH<l|f}34)mE*E}J7Q^F^h6sUF2RF-gjK1zT*c5Su7Pf)v7xDLTMT`_hs}T1@9XB~mH;Ad=|fPoS16nGhFAS&KW7>N3He0NeqoV3Yt#_8;*JM02zpW->QZo3S_&9L4oe8fiXI)~<@|q(G;GMM0rdpcS|QV^Xti-4<x!Gd=dpb9$)nSY-+wkTuF1#0CwmK!#kkm9L^6s)LBc$y7Fqco!ph6ktWpVPh)f15@V3(+kvuAe@OmrUEPxVV06OaZm>&k^@bFYg+xm97qwOZ*rDX)tW`M6A{v6OkAXtD<O0v#RmjKx`*e#`5R5Oi1PZ8?thZg8U;>a@=D=3NdTWzPsNJ4Omumu$h?714+N}UBe-@HQ4bET?(RQ+CDAD057T0(N@#{$e!BtO_f3qgyLX#A%?Kn*+>>>k(KJLWhFU6D9Vr^C<W!SORrX(r72-@wMzPuh`Jp(UOQM5kQ;R$jHIuT;=>-(kR)~Z`!KmhM4fv?2QzR!yY>vftf6f+Se9~k;Kd@#otQn|_w^F`w{^x{57D123m8qm61eR~lbJd0zBHBP`7`-J-O-yLxR8t(MFsz7imL=?Qe4HkSy+)4L^Cxwi3-zlEujT=t{7nN`2@Q`Lhv*n{BU3OJ_1ZwcK<Pn^52kD7HM(IC?}Qg#7yce{!I4-s%qg0};z0Bk4?^QGwG!c!f;vqaplQ5db)F)sc<X4WLFp#Nc8){rrygY>@fmab;zD7_bw#NsW$7_gs)sxee3`Wtbim*>xyKbqBrkp`$Jz?A=42yzF*wt@j5*i@cZgPA1)NAuDXXMqkO>$wqlAfCh!Q4cpUVe3*fbDzkZyWrT;&y^46xmZAWqG%LYy1)FSCFfPsKuFkha}VzKmBbk57o|h-CO-gbM`HsV=1R)|kcx73x_WDXvq8X8R^6eQfX>Vj>Nq-j*lfa)$jzc^MP+7q~|wWs7T{UnSUu%*`KC2(xh!7>EWLYpGVB0j+D)7ty+3qK(iVMGBFnkl0D8dh)pSf*$z`Ng4##v2STb>H|rN7%EyE#0oUbP=3=93~KDYGyLkr3ar>*acU=2pR|r7%B{~71wfLxjjVWmS`I2prQ=1|F)<8BtP9v<0-ENe<N}J)uyawh?jrD#;nRJy1EJHj9aXcEU<YVvG@OcxfiE(PjN}RPFrswEDJaI(u)v(KoN}YWG)5M5SG3wBwo{D-0QPJS1*e2Y90MxBCQlG1sd*}AZN<Pn{)ZaC<qDg&a}a<q1%ptEse?69cekpRQ6I`gF?$P`F>?Y%;@Ua6WTj}k`q__C(HK^WQUnDr$hyv}o?>UDZbGg*g@v8b26OWC4Y9n0?pc&rsf9ZHn1W4u_ut?CDO9N17YWj?<m6ZWp#-=WRy%HFBEy^hI-kBBrmcdkvK0q0YtetwQ^H~@wL|8$bFcr(Z@vB{VH?{4La;kmq#K6&8mNwGolZ%WqXW}u?-?aYUS|U<%;9LE%uLFJHA$``8GSQVsVNNvPnb==qj&^gpjuppalpkXaYPQ$ws#hReE87bUh=57e5!)EbxB*N<z&jMj%fHKR(B1i2P==O1`w@dWJn8^7n@VJmb_`m7<rC>Uy{HnR<{C_QMNGPEr1%UNR3n?f{aQjrEidr-X`gG<DN>frFHt4rxFPvBJ_;O0HE}UKwTxcMfEp)mMi`&Rc4ajWROda=_f$vTYpN`f8g*mKJYz>AetN3iiXFI5K#W90@WZ+0twqG!UtJAu^j%G%%AQLQEfH@)(qL)gzI0Ngl?vj&}pqG5&&47XHn+aq4=WgaSIow6IAni(^1WjIg-hKPw7tfRR9F-)~uiiE#0YQ0yzvHBf<O4hzY{W3fGUWSFnEc3{(fhhJsJnbZUh{4;JPT$Z6e=DU!EK8m=PY8K>$M{1{PGek8raxcquE-<;ohCVZ7SK3qtdhj9!@qqPt=dj1G=q&u0C09qaN#3Ht`%VpbHwWy;bNz9|&FIp;&<Z**V0z8ff<)4*b_TjGp!PY>g7b?Vt8Wak-mUlU5z*Ulz0PT;6W`ay9X+&t6KcY!BG6B61wW%{&F!@62%B$6UN-_bdCt`a5g_cUD45s~6O-TB%X4noX8I=$=OF6!5`_2w+d-c6Cv^gHh*a7E(^|Tl`sFhZuVHhV1q8o|m2|-MN+OO28+6RO=B#nKLacoe@je>emEHoj#c^Hrrm9*1kttRJ|5baWVQhS7M*vHuq@-$RznuuU|0k`F*i+U%c4IFKLSMg5lPSmtGFW!mu6iLBLHmr9_?M@g1<LKZhNO!AtCoVK|Vs#busz(&=)Qt)so_aR=onAJR16VRZj}wS?Dkp7%s;?z57uq-uGG)!UxBm8)Zch8wKrnBAGsL8YfoDyxdUmAI3J)afL6ehf+(z#ZS^(}r<Tf9W*}>?R{GP^M9g4qL=Kd>SiC5^r%9$umhV%(y2TGX;1INkl@H1rUR^50ux`Vtr46c$oNzJDb(m8<#$bPJmv*qHWISMw6mVs1T@$0;*UX6$b#Ny>u4U?!rsw1`RWU*S$l@rBcn|pxnn8`rLb!|jNvX<=tFyB7u{257YF0k+=L@e1qXu>J_6OU<tX|0_zuT;e#XFFbX<yk9ZLg4~L*^pssib!9ENO~CP)cNaJl5pY(6WZwnDXB<ekxE;o{3J#8z{b52k<z4~Bu1TiIrd7Dt9~Mp)Pz7MPs~wGm2j&rWOU6X2!D#|DO_)g6aXL*fk~Po!1Co5p|?;cIU&{<<dLLRi-fw{<zv?s^{Mg&jR9f={0I~xf+*#4Iw6Hj6;Kk2dMHM=2TDLuX9mQg<mm!SLyo!<DS$<d%3}%mMO2QHcQF~{4MR1>fI!9|om`8RK#aEeLPS|+O;_unf`YFY2^K(}So8x|y;K9UVTr@=NdfR>X4Rri^|G~s^0euX`ZO5Y(b9)2f(z9J&bSerMIULwY=?q;=H0~xPt%WP{XvX!fOXyYM&@HGCsQQ!$iH~)zku}Jait15)=`#%%6u;xDs7i3q%-*_hseBRu)1_tGemRfW%;8;TxHdD*`S73dj;qrm>|LtYVBwib57_jD!Cc*w>4imE(?kU126<AbC95zjl%rRkto8Vhd#%H6915Znb<~hBy&CDlJp@#Ftia=NH*Y2^*b3Ph_hgQ?(r;?1QiqNCp5r8Aq-MpY!^VHY{P2rUZZMKi2p^5c<>zX))b7@c}A03)&&EcdZT5nqTq)EM})!M<Zm8{u%q>Zoti*2(NxVMIxqN{MDVI0EdpDx%N0nvyGp4dwwd>%+SQH@0m^2?@O=umk{3c&z5=BV)?yP`!Mqa2DN@A|b)1xj1bkef61Uf*Y0(_fo0$<kMTBy8*&Nd|_W3D7dM9SGXI}WHOaW@jhZuD$JzEoO?VJMRd8jOcSLZ6F$d+w2bmIi-h=yBpf{Lqz0wN%tJc`KSiY%H6Y`zZigkB*R{Ci1B1Fbbk6>c>ZT_mfBSPu-u<w7eGX}0(Z4}>Uh$Q}>t_`xs)I6jlD3Zvd+(2G$>%tZ#0B9x#?!R8hTtubJ`AT4^&0f<%S5Gd%Rj}dAI5s4=Py}eu6NgnJ+8_u&0HPu6=uR7FY8!=XW4;pR!35_my^fwC_l8kjREc{1o4!9MHTcPH;v*Q9~;l@**92(4k4BeBOrm(q9!ulsY@t{~OS6CB9k>nRqAluJn`BH+*&GQz}@8~ppevOYAQ%_d~dcG=Bd(4rYf<&|OSPzuPGJu9!<hy}Taoi!JO{l%Qnwyy8)w)VraSfbwQ%f_H&@$H!Oj2y+^pS~32-o4Ol4O&$l|f06!_K6gxLrVWsbnLS#V#{u%<wLCB|Wd3M4x1P)*wTU6UvNCi^&}@z1BDz69&Cpz}!L_6(+#>n5M>>imfR76|i*r-rJXG|K|SzbsZGr'
)))


def _compute_fert_reserve(actions):
    """Total fertilizer the route will PICKUP from shed, step s onwards."""
    reserve = [0] * len(actions)
    running = 0
    for s in range(len(actions) - 1, -1, -1):
        act = actions[s]
        for unit in [act.get("farmer", [])] + list(act.get("hands") or []):
            if (isinstance(unit, list) and len(unit) >= 3
                    and unit[0] == "PICKUP" and unit[1] == "FERTILIZER"):
                running += max(0, int(unit[2]))
        reserve[s] = running
    return reserve

_FERT_RESERVE = _compute_fert_reserve(_ACTIONS)

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
_PRICE_GATE_FORCE_DAY  = 28    # always sell in last two days regardless of price
_PRICE_GATE_SHED_LIMIT = 90    # bypass gate if shed is near capacity


def _price_gate_thresh(day):
    """Day-adaptive floor threshold: stricter in early game, looser late game."""
    if day < 10:  return 0.35
    if day < 20:  return 0.30
    return 0.25


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
            if cur_price < _BASE_PRICES[item] * _price_gate_thresh(day):
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
    """When shed is nearly full, sell items the route won't sell soon.

    Only sells items absent from the route's market in the next 20 steps, so
    we never front-run planned sells — depleting the shed before the route's
    window causes _safe_market to clamp route sells to 0 (net loss).
    """
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    total   = sum(max(0, int(v or 0)) for v in shed.values())
    if total < _SHED_OVERFLOW:
        return action
    step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
    # Items the route plans to sell in next 20 steps — don't front-run these
    route_sells_soon = set()
    for fs in range(step + 1, min(step + 21, len(_ACTIONS))):
        for o in (_ACTIONS[fs].get("market") or []):
            if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL":
                route_sells_soon.add(str(o[1]))
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
        if item in current_sells or qty <= 0 or item in route_sells_soon:
            continue
        market.append(["SELL", item, qty])
        current_sells.add(item)
        slots_left -= 1
    action["market"] = market
    return action


def _fertilizer_sell(obs, action):
    """Sell genuinely excess fertilizer — above what the route's PICKUP actions still need.

    Root cause of V3 regression: old route had FERTILIZE actions that consumed
    fertilizer from shed via PICKUP first; selling before those pickups starved
    the farm and collapsed crop yields by ~14k/game.  _FERT_RESERVE[step] holds
    the total PICKUP quantity still outstanding so we only sell what's truly excess.
    (New route ep=90914286 has zero PICKUP FERTILIZER, so _FERT_RESERVE is all zeros
    and all shed fertilizer beyond the route's own planned sells is sellable.)
    """
    step     = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
    reserve  = _FERT_RESERVE[step]
    private  = _get(obs, "private", {}) or {}
    shed     = _get(private, "shed", {}) or {}
    shed_qty = max(0, int(shed.get("FERTILIZER", 0) or 0))
    sellable = max(0, shed_qty - reserve)
    if sellable <= 0:
        return action
    market = list(action.get("market", []) or [])
    if any(isinstance(o, list) and len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER"
           for o in market):
        return action
    if len(market) >= 10:
        return action
    action = _copy_action(action)
    action["market"] = market + [["SELL", "FERTILIZER", sellable]]
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
_our_last_sells   = {}  # what we sold last step (to subtract from total delta)


def _detect_opponent_sells(obs, step):
    """Track market-inventory delta, subtracting our own sells to isolate opponent activity.

    Market delta = our_sells + opp_sells - NPC_recovery. By subtracting our
    known sells (from the previous turn's action), we get a net signal that
    only fires when the opponent is genuinely flooding, not in mirror play.
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
        curr      = max(0, int(_get(inventory, item, 0) or 0))
        net_delta = (curr - prev) - _our_last_sells.get(item, 0)
        if net_delta > 3:
            opp_sold.add(item)
        if net_delta > 20:
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
    global _our_last_sells
    try:
        step     = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        thresh   = _clone_threshold(obs)
        opp_sold = _detect_opponent_sells(obs, step)
        action   = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), _ACTIONS, step)
        action   = _safe_market(obs, action)
        action   = _premium_shift(obs, action, step, thresh=thresh)
        action   = _safe_market(obs, action)
        exposure = _opponent_exposure(obs)
        action   = _impact_slots(obs, action, opponent_exposure=exposure)
        action   = _merge_sells(action)
        action   = _price_gate_sells(obs, action)
        action   = _fertilizer_sell(obs, action)
        action   = _safe_market(obs, action)
        if step >= len(_ACTIONS) - 13:
            action = _preterminal_no_recovery(obs, action)
        if step >= len(_ACTIONS) - 3:
            action = _terminal_market(obs, action)
        final = _align_hands(action, obs)
        _our_last_sells = {
            o[1]: int(o[2]) for o in (final.get("market") or [])
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
        }
        return final
    except Exception:
        _our_last_sells = {}
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands":  [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs):
    return agent(obs)
