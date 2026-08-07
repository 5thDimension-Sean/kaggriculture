"""Kaggriculture agent — Route candidate ep=90636794 P1 score=140,235
Route:   ep=90637595 P1 (best of 204 candidates from 102 top-player replays;
         +5,731/game and 20/20 wins vs 4.5)
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + Town-Center-phase-aware terminal liquidation
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -7)
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 4.5: new route backbone extracted from 200+ top-player replay JSON files,
        benchmarked against all candidates; COW+SHEEP dual strategy with
        BUY_PRODUCT WHEAT 5 at step 0 for faster early feed cycle.
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<U2j`Sa{VuQ=7UMevL|m^o4XcPV;PbhVlxm117w2$!RBF-w;=yL8i^vWZdIK+^>HsL#ZRV5inqGEy1PD3o%-c}PX6t;-~aLV-%tMOmy>T7x3?$vi<5u<?LYtZzaHLrc=?ate*cfZ|M$b|UrxSU-mD)!<zD>h``>=O_<H&C#ns8;<kR)$WU&%&-+o!IzYRXPU9UesyuJCdzPLMCd>Fm`^ZM%g>&ard`}((=>(Adm-R=M4{r&y_E?$i1^3z|xf7?H4IT+h7C!6){-J`5uuW#<YJigk!HG1)KB5v1LSNo?f&8P0ZFnsFn)8V9CUVZ-cVe;?3Z)cB_L!AU6&h{rX5%$w!KQcE5;Gx?;Ih}sw<6j?0vtM#$@yBlspFLjdtBX(T-AulCgdCgpQ1J>p?9apf@p5vvV*H^~fBe?N|G(bt_Kf~c<jJ2d#uGS_<zcEW?$$S>SI-aKe`_QLn%U7=v=d?|`TFA4czWoU_dh77Y4?cTi`(n(&UDEqD2l$5c=yA-(>2zK_E{4uAmvw{`Sc>U@OydDid7~}9zTP_pfp=stznjVG5mI7zL2uX&Dk??<AZR586@;gz5}k2jNYN?%bW|_cLs9q-?1K*dw?=oyN^bXOpahLulV7o7lGeJUj^nB__Jp%WWH-%w1FEEef9e4YW?Z%*FUds?k=w`|K)Mkx`!}_JYypdeD(P}`yqN+^vG8E@m1*2Zk?FH5-iSacQ)W}ZohB_{msZu5B;_6C)8|y_}8pchV?#XBTO|-5gFt(HF&O_lO$bn-X;=fU+mHL4Dan*R|aK*kqBK=ymyj30hI|3%#kw10Z(&s9hUA#*8~q#AYpcn-RGp2H}{hZrgr4&O597aW47TE%3M8D=wa?QE}VV&6K|5MBz?RE?+x!c?opOFz$UzVLo?<d<n~RQnlkrjnpMZb?*Ci*ldQ`zdQoyUn0(4O`xdvg7gKpDu^%QJ7v~2jGt(DsUZ5RaE!;^)i2cjO%|FNQtg(r&M(wwvq~j!t85x`tWWDcydz{F~+<itMxwLFjt#*r*UN|jY?}pk7E2y1OCI40%0PoI0pI6hif@L#Yto;wZcsIU&a;-py(YH)ehg>PqvvZPU?v>GKDo0_eb~3y2{6bmL;xAf>o2m)2z0_9kAJxD!OQeOcoZic<_zdZD?`V9?xqa-<mw%ba{HJ$VldoBcn-K@1W$H{AB@4~jlYp@))8xoOkvd!|cJ|(~-#C}6`Py<=B~Ne;uP@?#*vI}sQ&_-SK8_StAVpHlVeJjNR0fSofo0;G!2ReA4VS%WUyTWuIlMw0?pfCoO=usCv7E_NRt>v0Q7-G*QMtZ;_-Fa<*$sKHCO;R-54K*+?cL4A=1=RJo4-B$_D?3pV|AZ#*%X6j<aM!i6p1@psW6aXL+M(}7xc-pB7((ZnGLxlc2&w1z~}R3gdV3<0L+1>`}PMOdhqFu{+fXt=Vs{H-y3YPw8<zyzuJ?zQj5rqWb2Jmg%F+sWkFNx2<$c`7LFt3=pva)u{4Q5NsuwAX?2rE3#e+@%PNulqbKL$pqf*DF+Ky~JO%R>?5c*cM%FD7UcLs@k~3d{)tk_OQ;H0<!`{pvCe3qIEOkYVX>xag@pdVHrsNb|LACXCg$Ov-#(vX2MTdT%NKINzaIQPHUOpfPs(&V1J>==gLK~Patf3Sw*8nVu_c{8rF4>e)9(BnM1ckwl-ZJ3JNuLCGEN6*wVJ&fXe$OMcU;1*(Y?-osoXMg(SzeW`SC$vFG-yckoLy1(w$-n_BH{=^5b*g|@kEBH=CNh1l+h>bDWM$FJ_hK8Nv);b3uKr33CFD-1`Hz=0aA<eYjvh;wp?1S+E6ceGmp>@XKfhe*hHX7Zsp2?0xO{>Z2v}$`D%MOVh#}QrE^TU6C}llP%|C`ML`c=96)rbFWd^kqBYBvW7C39Vg9GpT!Vs?%vC{aVN+m1Rwkt7cPabs=gX_VKGXJ$SYtjI(4+IP85oO~Fa5~0$y^b${0!4{jHFty_oKY8q^YQzt2Le*bRJNrnk`5%9t`8Lq}^JNgzfDT<HBV?lHJi@*Vr|)3UlG(O%;O3`H1-}H_Qw3=)z1g+3@wuOi-H4t4_`cRjvWVsiXu^_s=a^`LxxY)r*n^xEr_PV`$V#yoV*ny?++J_@)fWVS?l^RX)TI5~%GIro2Rr>yBK`yhnxGKyQh#V;0OLPqW>_9<jZPDsF1`bB4Cc=PHCuJ!>ni)q(pjgO(+j3~wvf!lS__<?Zy@9;8EH9`QUMr9W_5HTzlne+BR|OO6pVL{*t2LQOE9`n;Q~oUgzPHc{Xi^c@mXp!zn_cd$_}Q-r8lyO0Vj*Ym_^iqu-eND*m+<E2lIE)7GAO8sTB5SEIN0%@J%vZ-J?2%@lIW|<)nE`&g6PihSu8jcjT;O{9rX@fUUU>l`p6M$$`s~Ib0c=NRC0k~FBmMC}{G>NZih_1HE_QQ^pMPi(je08764QLaNA`8BRD}HWaT1T6^&o|fKI9RkE;vO1m>3O9=T0*;}--RZ<cd7w)!FD8e^Syf^)(1`W>MSzRr#&(wkMn65QQbJLO!I(CBPX+8q!5@=7?%hMxYGzAU(cMXxjZI=7j=>g^V;jVQ_=-ykjwumi}jQfJO{g&De_^x|Bg8<v_fIgYep1cSg5o*ZGf=Bc!%<#Ux2f4Ai73?nJ}zVSh-<alkuA?^P90@T5weWP$__pU6kIL_U6ibQyC%-x5#V<z{wOLfwGkVu3T|&I#l5QkdQ;MxS$3Oz$F<>zGekSmX8BE?v_+(3K3sF4<XJ1$9v;WJ~Yx!2C<NMSnbe*6_j{Nnf;`SdjhIw#*T;;I&0c}#@kdE6FXAGXk$=|c@Q#+hlCCr934Y3UJ9yE#QWF)AW*i7(Kqa!uH>-`^w`8+1j_~&$*cRxYNHa_rFZUX+MTOp!Gn6a;CLEKmDebArX<fnJq`k*1TOzk;3Kv-)u3u9SH7N0Pcy^Q`b~{)ha@r}tZ^lTuN+52YWh%73Vx9bT_gB<aqg!AA<72Il-x}<y5x?M!*fyvEf|t<_sN>Xo_?8Alas!-J-m9&3AAgrEfOjNZQTfc(Y8{!%nqO^0kdHwCS4oK1lE;<R+GU78}u;D0k_t+(MwR8hz)Iv;DG}&lAU%Lw~mnEV$ytm$wMaVC?KkQAg^L}!9XO)l8cb2bpsTrW5&1!3xx^jSBbq>Oc<_sECvfUPT8xN9Ur^WQz>a5OMtAsR{rTs1?+8GYAUA$$~?F@kLKhmUKRhA3OWX&-F9>r2F()92ekRr&ZK0KGOCsJ7BCQ%O0u<Baav*Fs(Jeot0iIUXNr?^Pwe*C{$G_B3`>hS7{Z4)fIK*i=M$?cLv27c_vq|CKo+(SC_q6`#V5hURwEyk(`DxoVMC=%r5-`}Liu#)-gS~NX@*&vC?@O(LJrN~gttRKGY%qVr)#D=By>Iwh+t6<_6bwl1-7w=sC(F&e}1-S+y#(&65s#|2|=<eNmY1uS@Nk}bSZT!e{3mo^hY7BXU~}Y^qTEe^)zsp0!u$qpi@;SOwbmUznSzB_bA0k#<@p;Ptb49WunijtG0M{{1EautO=M$z=yRnO)@Mlx3lK~Z+g4U$&?YUQFJQ}s`9YIS3B_e9(BK`zV<l~=6AN0YLP&F#(d$7IRXSP!U0Mp(fMK62WH7Rwz<ztcCpn#4&@XJy)hy_@uWG$PGdj7dOJ-v(KF<YY@+Rf&+D58(B2V4E8=>}lq1(uye(rL)vkbVmhL=SQ8XMX0a?$6(%4LXk|QYS%}$!u@%+w@JnlOHxd`_lD<ar5rf>Qx>*75|@v{a6$XkA|l+Q1b#~`UWgxgp9QbS`e&W|_=5VM@IIkW^n9`rWzoHBVS9h*tW)aEEjf2&E&Hgu<M8Bk1~9SO`xq7c~1L`iNjqe;T|a9*h?iFqU-Kd7>``De^2%IlmYeO4*&O*@9z&1lbEN;8>q9Q!A`OWBETCex=dBPhLKlaIK<H<1KKR986*T5`aQkLdYDP`|^k=(Hq(;ZW2rSk$^E>g`jl>LBdXN3dq98EfnkkXVjlDCkKzQfWpt1*N3+B)@!Mmn&4iGTXymTZl3n<hXiwI?7hbyrfc?3fRsHRswK%G(o+DWh{$YN>e5|;wJKuk4u_T3Uc0dNp`|=4|P6T2R{g3KAPOA@)x30srtz|{-m!Cv@uhwihF9fC47O>Wcgjh)rOiZA4?V($^VLT#V^-$`}Z%ksx6t@pJN_C@J-PfaQLyMrZ*h3_|Sv(mTu0Rwz5TlfEn7igXO|8dJ*;|FSS!haF4V5A1n>Ct-yEqI%M2z*AFvsS@##OvKmRG>$UUA-SS`?DaS#{BZdr+@)94q%~PpLrnFZ%l<LvOtfo-ikr5i2hANQFAeE><rN_2BRWLKDBFN+_BHf^P?FQJG*}(<Uca--lqbEia4}b>`WIP$?l4>KjmY9{ALUc%;V@zTM>yog_1cff>dGQm6?OpxhO~NaVB@Dy7utNP_Xk|4)4LL=FPh7Rp&hx;!8=m5rNV-Qp+k@3fN`~(OxFOM*Iw>&Ws0PS~vD+3Tu%9&IqrC9EQ?BaIa-j;KbUw&4iLDNC8e)2y0-;nFvkk%e6I+t_?tnWuo{YB-_$f)I>wJM6*%aI)M_4T%ZA_5x3wz7t!Q>+b6{o>pr~<ihGq`}IkiV^+<g|X<2cEtQ$}`H>@RPwg?UmAa4!71EwqZKEkC3A~-RDsXi`CpxY!o*4VG7-t%P|J9+pZ2K#%6=>D6pk)N$VymYMS_%g+C8Cay#Wy0%4?1dw7!#)wT3d^5v@JgTgcg<Dkm@(G^3eRlQHhB-qtuFcrvjkGJJVfibblOnze6^iB^J5P4nPc_zey<PyzBJF<l0(Em=5pEh%ibK*@y8c^^n<RJ>BK4y|~J@V5uoXI%MG20(WmC(R(4*hFfK)|7)a>Y}&Mmw+?l97F4?alK+V#{pZ0n9)>+=^~Ijtf_^xh`8XvZ%d|u>tS|nmm;!4Z$X0O#|I<5qew99p?Cs`eOQ99dhTh@nLR16yYzr?(m#`xLgG9+DNDZx$GV{pOJ8{1k$u&Gfq8IKa=UAF<`2A_I>004y2x`r5+SHc*+s>3O;Z#5YW#VGU+%&HGe{1i6qT0#7;vovxwq2pWl~V?{_?J{qlX;)jmq%`eOkh1UlJ=;`4dDf!=8eq|l<SR%iVNlf7)0Sl&FkXD5vuXdbjXuVHTnW?$2&b1?lFs6g3EYZLcLm73G&_&xxFaL82DjTaZm!9ca4!OTj@)65r~a9anr9mQz-RH8ppc9QHYO&z)NWGt;y9>9Q^T%_Xy)BCAKS~g%7Qne0bm+zhxO28OEd4#es=)CUPJRGbcyKV4MprquzSQ?X&=Rgn?zXkX8bqlG4a;8F>i!e@yxwsP=9U%Qu?lcG+fE*4HMFs>MsIvmDn#^6t6b4znE#qXQN;X_ET}PYG-Ebcxd>&M}Hi}LVn=uz5a7;$FV>y`O7DR(eOOR~b-7A?>EL7@Q--&5hQG^=Xz{;Cq)Hu2Ti%mAcGE<x}6dU-3`q%GWIK^@`Wd}km-8mhgU(Z`!0!b`jS!qS$iO5ND&Y$7y2(l{VGV&mez5fc&z!9sOWkKUJ(nKb!wu2M~ic#oSH(`9^bln8l-H2=}rSR5DP^#}Fls>Sp)vUfz_?Bfn@zS)B{B{;$qrBml3sc+QFYE{B^&|y3Vbl(6LmQ$CfG(fUTalR#8K$W6P;jnn@NR&rpE=DWz@NwJaocu%%WoBYt;r3c95DcGa28l};s(jGi#X3v)Fp9vQ$vdwVGb7$rN>3E1?trTDQ|!V0lB@!CJJzpgK>d;HRPcOTN}PRKnXF2?X&y7zPkRZIcX4B#(?dWC}NJjNU8#4TdpxiVZ{&8&N$EmqMR)l5?}kr21ZsTiT!q(XPe3~-BVh_%K5YXIuyZk$yl7cmsG|?qgxOE<~eL3G90FQOownWYxnW~fQ&ULKGMTx^D<$!kY#|2@r<0y*l3*#=LqV%UOCom<E4Bjs{y00ft>V3PMH7~D#<rz66W<$XHZ}O4#)7C`hcR0yH}0X1n%nT9vbQ+>iae&EQ%V%_dM%R4<pVERReQ=RxeW}C$|sR_XkI4tNDDk5n0yHLXis)z(bDW+z~vygV_2(npY=+apA#d9wHmjeI^!z0iW@mbU`auXNEcNJ~sUd^r;hZX8AgXw~&OLAy1YHFF-USVu(rf=0mK7kot@iazq)M3;@8)h!ep?K9%RUW+*=t9hNJlhAo`aP<%fnU7%78SuhS&4gmH%?X)<!4ETr=gk{!mVbUZlxy%0}VMM2yQ2_iNh4ZqLzB!<ms<p{ZPLs)2jJ)VW3rpq~_npfK%Sr}f&J3iQ)Ucnj1%UMsOkd>X=wdM>9P89Wwg$UHy+15-aj@B^jmry=!AI%~ZFa@%5X|6PEw;nZIzW+;?Lf(V1mvg?ZG%6h8ieEr9S{1XI%1JUq@Z+e-l{&H3JIG0>d5#2P^5|v`UOs><#h?@Q(L3_u48y*BU~eP=itx?Td0Yh&E|-m&1$=u;ihUjKPKbtN))2uYi%PPW|EDXdH9&)yVDH}Y87|7JOo1ytOjmZKA(k)NQVVO<df<UqM+g#pmh<cBU}&NCe#api@bYRRd<NtoK43tRWynKQ}JX9a~*{8W+2#hvv6E(?i^nTfD=$I&sy+cHuf0+!YB*?hXEnQFw?!*8(0GgOH7-)#-&41H72j4>chn-S8KKBI|{gT_M^^oUT_oDf6^r*bc;04rwo*l-41fYX{^eO3e0sUpSKTKlnE(XgL<e2Nc!+UU;ZUjQCdT&Oy3#FugXK{C@&&a2vAHK0~~N_Y}eCwe>E-0c8cOaVU<ox>JU(2gPfA*f8}32f0Af(WIOGlNW8y9Oyw(8Kh{$^r$fsSI~(?WpO>JGZ&%BWFWAjGzLuA{dQts*JFEbVbhCPnoq5b=Wz-5Xjmm91Y{jR=atG690s=xsN-DmutfjPM_ydS1AN%N|Ked1mORqk_!^suzJeCSKs%K3oL{oucLZ77x9a&~Ht%l~|D(^OaM47*e0frIc^-5KtNDo;|o4=H0Mo^+Dk6Ygwr=*vQxYO@F9&L2wjQ<77_yRrD$xe@`%amlx{&$%p#y*b<#Tud5iqh6^w=R-q5=H~<bT@G?EWGPo*?2H?W)_Fav4HL9e<_wti$y9eEUOy_Rkjv~Cw(Gx%juaPYqWafE#K+Q@!nj(@i5^<h5(JAn#12+xxvN{eZ`f`i1-)X)M*3&k1HrJLHSKgXoRyL6*Pgi>+iP5hTT}4S!sBydiOoo+*MTu)*9PwpPH)<J#35qxf_ZJB=N`!L)`C70rWGed(4QGAv$cTDNJ`>CrkI-^e<Ib=<Q@LvEiWk0_cJacRla6BVCG&ETK>wql~eO9jF=sU_o%j<Z_T1Gp&ObxeOq>KtKX>6h7qsbe1QO)}w%PiI$*BKco=DUW(gZ1I*FEL`VW@MA=4_b@7I1ioc6EL%5!e4u@l`GMNO6GR+h>#LjZyu9*{@G1+AVPnkH554Ko!uc;w_K|<a!r4SU?+$$RVA%yOxn?jPzY0y1MlupJN`bi!G<wqx|oizFTmk!iR#PgpcKW7IEy}Z)Sh>-j|6pzpXDUF~lzMH!r5tyw#A{LZt0yRlv#BiAxvc`_E9U@91!qLsq0}(k>I8c&Ug}J&Pl04hcEj*&0hmcyTN?JB!qeEOqrWLqzz@}+C8sb=p%bXqe7aR2-dFBZ$QGi>X?n}s$yCGPVf0Ig472hMvgU_+NJ7<iq7Qmwdm4c4{hoKO@a~+_{a#A%gZIB=mhV_4ZCk*IOaa8I_Ar+g+Nn|^HRU>__3(yb6DPfKwWPh+}_*KrCMnD0QCom8plv5iNNs&#1UhsENSC(JmC(QBqYx(YwT-nSKO@$cDPJk~E9#k>e^6ZE(9j`RPpkgqV7|G!fE}go$@nd9TN+DR7u8EVDoKY<1W}KiqSs&pA$5bLf^oW&PYv%_=%!470vo9Yx*kDtr0?W%p{rIr?jScZg=ef?Ndb!3oAtYEjsG01imu{++>cMqfee+<p3HB25hui}s;}i3)yPMNpE{as^h?ilFBI((j&<z7<A>aw}JS17#srrymORdPRj6nfX-Rz)A0SlJa1#)jCn-0Qz^^Kt&5WNU4J+PB)I|7s2%6^I^eh|UECmJ@g$z2g+TuQ-@0svl^Nb_K^Ix$lxq0n$2_!!x6!#o;+7j5%}t9wvvN-ePQ;UU%O4aK6e;SQ&g^Sl&s=^`EPZ|Sy@u$SeTUV`*8a`pZ#1+I=Il;!v8z}!F_f36ysnyBAfazsT+;Qk(P9MKVE51NYH*y#(0keTp9D0u`^aj<rAG%GbZ`u(d%)X(AC$8p{Z+jx#-tck{d>n-Gb5#u~rBfQp(jpagR@J8np;wP*ht%t<2@e}-t)8#DYV#>yIdLb2CpoHR>;&{n~y9gWvQ@6(f`Wp`uG&sp)<k8s&drw+?R>?3*6^DcX6gVyy<Dp8H5Xrvh9*!nj@&{~0<ql>D#Iz)SuHr~D4E%byK(U~|^?ZB+5i*vg?&74dd!sv5NcfgB3yJiO>u?c;l?kf$V!KfxlcV<+dzaZ3XbfqFXmb^yKom;~)2U-FH8=S1o={GOpba;71xE)iL5KB9pz;f=<;qvfJ^0Swh#H!WSxwNlP;wiw>vtYuCgKa;P(+bqXtyKBNsgje4P2VNeRQ$LTgk@be}>wARJsIy&@a@Z3<9b<@fFaXw@~#=0xH|Mj*D-MyuY8enO{=aY5MiCjNF?rFY1iE-0UDA4*kd|w!^rnW9p=*e=}6_(bh08X2^DQuE`L1akVw2`i?3M7Z4FShDmbPI<*!q1;WH4A;m;tHNW_Y3W_Hy%t&e-1&Qku6Z<izxNjRi`JpFSta}5@qh0~h<2al&V&aBJ20qB%Q~eaXs&rUr2IvRXC5l~AHwlbkva+BbGQ3I|Kpe*Ad{O9J&Q{$xk@>iFGd`aN0U&yv=jwml+WJ_-^$eUf1~56~4D?75?Xk<Ufkcd^4V(s#1GP~Oiu#V{WCaz%;mSCU$Ti4#naNZJ_%D>L<5=L6FAnS{n_L_3nQo<1uGUJiksWnVQm(FSIcq($Gh`%=Z!7{hNHUSW_Gc6HRk?@DE?wy1uq4iIeVEReTScDI<{@+C4#e&`Ed}L%lIdeartuFioDU`HoRElVydu#PP&6&IPD%8H>XwZqep2`dBK=|%NCuK$N)57H&+;rY@+fAmvYaME2be`=KdcM_h(C1l{{H~Y+O>@'
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
_PRICE_GATE_THRESH     = 0.20   # skip sell if price < 20% of base (extreme crash only)
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
        action   = _safe_market(obs, action)
        if step >= len(_ACTIONS) - 7:
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
