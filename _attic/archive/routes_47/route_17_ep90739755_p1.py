"""Kaggriculture agent — Route candidate ep=90739755 P1 score=141,630
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
    'c-rk<OK)3ga{Vt_b0I!N%h_pc&e#}r%aH95lLpafAQJ=#CW}sXLH>KxmPB6OsycP*aY?$<E7K&!`@O%aQ>RY-^gmbs_RFvT`1`L{|Mb(<r@POeuXeMmfB)q_|MkC~-gtWXk6(WMkH7!-)9atEK74%KJblW&_|w<F{e1W1#~<$QuVz>89=2Drg?Rh(ht1~G;DgVb&HJafw;wilU#@0vMsNSHxqtZaYBt}0{nO*a`>*f59RA{FxBK7OQGY(Z`|H<FhbPSkef#NZyZQX(TU&p8c>MC=+pGOsqZh{m@p*H9e|YNrx37)gvKn&un?XbNpAN_A<Nf=epXTGs*Ovk1nx>A6XwJ(|XiYebl>JEc+5973TD6?MpW|O2wB|79%IuHd0{#4SfA?;)AGf1N$i8V06|ca<{yf|u$AkOQjNew!Z@=~Q{~y2XH;w*I<jL>u#sfHN%hOQZec3#YUcEl_@U2lZ(8!JsqkSWWE#KUIHl7~(<--rkVcI`p|Kjt*S7*576O@I%Z}I+zdxvYhCfY|$ECJbm<(bbfaua`OFPgE+pvmKBa2S+E>t)q2(>xn~J275pvB}NZGjQXBaDove)|-5Xzp|)xhlVe6F1)-mXy@S_>ruG}D1){CX!OWr4-V}WKm7b6@Vn@%z?cGm_PPq0?^+ja;D$tBeYn5hy!-O=pEr+RKHh))mv5ui-Gx)MXKdtwufCpVe>A<^^vG8E<Ezl6eR10cQ!rcE{%pYEeEGr(I-HT69{OwBPpH}a@UK~?46pl`jWE?PMcN>TsljvY93<(A^EQz<`(lr_NBCghx@}Mf7&W15h!0Lu9P5aTkut;qPjm7$EZvW;0Uj)YgxNWEpOaqRsh?ahwIf$o;$Dg!vkjL}=IWVZ9p-N1!r7NU@g})S(#Koy-teB|9%YFGY{I)YG-CciZr`-2A#;zWldiF_`~Q3TldQ`zdQoyUn0U%K{1&&hXH$78u^%QJ7v~2jGt*~nUZ9Px7VabiV*haW_|Ne>Yi#1HsQpV*(m07?Mh3?OS?`D69tScqcb@?ym!?fFtNmo9Cr-obU8ub<gW4HY@^7^c@a`P+d9~G6uxy5tb@;)fcjNOX=L$p^eaj?u$dv*;dnZZ8UYQk5#VE|Bos6!$zEEbg_={HH29Z)0yNprt`p3%wrNuT>q|Gp&-tVk<5$TigV!X~%d)@Cp{$(PEfZlUW-e(0#BaTSR_?Zwl3ys-x17ky`wIfGP>Tt5y(fd7nlBaS$zqhDX$u~TO9~kjR>|_6|K`mfEUq(<X5Hu-9wGJj;DyBvS#WIK|a7cQ=;<8`uFJr=q4$n}B!`3xL6WRx3c4soURb#XDM7OpN4^RKhuaQ6U+n_yJlkW=|2`^sE=P!?U+dpj{AOH6B%(o`%W3kIPafHh@i{w~@?r0^$Kmv)<*_JQplVw4`$Ky5|?UHO(*{%R%pEo0P<WiwD2cGWRAGqtmr#Jd*2A7;0p;v!zu*K3Qqo4t6Pv(*@A~%w~Zj`))@DL~ynwm#ow<+j2#?H}2GS$M;S_G1Wj6qE=H)*thJeNaTCAWX{<Qy`pIpufbGZ2nbFp|N}YAB9m-6G-XYv3_C;}w{_2@N<U?La&1&4^;sJXf2g&Zsd=?k+IiE=AOoD5Kj@Z9d&b1RQH)ziFSMLqCwVCaoqo)*V|f56FRhpvh(rc{(!n1_lsoyhY1308`?9j{dBxZAx;FI%Q`f$6!Zq9`NO)PXauaRU&~{3!JTYJZJmZmz!r3m+j+BrrF7at850dyr88)Lz?I8jJmh2e(e=GNQjhx&%cT%G7LVCEo&vQK4DLZ#Ubruz-O4$TH3!rcDWyLd|8J9!${?X)Np<+^K`=|P|H~xt_$AGBi4sAH_YPLM#xHTF3XIfFQF&A{EdqFYI`_h4iN68b4<7cB%2S(XFM&6A|oChKy>mi+zP^?H4~U)!-7v?{-@PggTkH6<wa|-DX<_b1CsmQF^qkaVjlhQ@&2!`+CC#KorMAZufv963_+j!ShcBc5wisiV|C1}nz1*gyuqaLs2i{~EgW=0Q0JW8kRn115n9rctz%;cOU1Z?86ssjKJ1#mW}M+v9C~vJL3Vw_pq3lv$Y8oN!%jBEJu?#2O6HeN&MZ|f2Bf>Bz^aGmmh67o4$rQOl1;epx8ikZ@=CnVCHsAN7C-rB8<O1w;bJPqi0>p=wo@4Ql3A|1b~%F|C3k~$O8}8sdXqfO_7D5U_MKIkRQsPZR;zrjBHGk5x6*zc00I)mED>jT>$wJ)2A`ByVCs9&*rZ?X@?4<Xs@3m`y3CW1@WFWZ^+ZEDmq{5_MlaP@F7<Uh7dgKop()BFj0XLTL@Q9f9O-A+oS7*AZq|mRVCj0484Zz|yBJAIZE(``!O>g8$gEO-nM|yu@Kw-SCs}POk`E#{Y?)CeRhf;}&)jS|X`a%K*arARobGDDT~s#L7VoF_odqa3s)dagWq9-Cy-RS1pny_v>$k1h6|)@lHL7es>~vY8$W1)pEpWS(&7<t1Jd+KEd$dt`|M>8Uqf6^Rw`-NX-DR0tV%<tt3k@e|^$`}IK2;H^!S*Ni1HOMDCJ2r6Vr8~@+0#JeWj?n#xe^Ftd?2WiYapFyd2_vszzm`0>}MAEjz_~a3OR)iPBH6h0FMdV#r<Gz8TNYOvrslIQOkmg=P9%G9OGL@a(39zUB`eGik+}zG{aLL<{d4T4U9C1Nhlxs`7|?!aciK%#F9%<--cC6#&0gnZ^pW5u}=Ztq`)C|Np~yl&4u}<(nXAa$WR5Ky)gI1YM0>t$tnUkMa3cHP<Va>dXaa}s-15rmI6qC16)alkgu7#5jrQwa@<d|QX?Whryf0=WsUd3Mm{gnj{C5Dc$n%y5e1EYuGWFQDmN{Hb0n@4Sd=Cx#PmsVnb%Ew)p(mKfnsAo%-RjEd7iI~@Q~2agmEtf=u#YpA`!@D27wG$Ov_>I1tq}E8%gub1_kp5XUWSE$}UF*$ECNka`mpSr`^s<%sjYQXPok5DRUd)X-cRa<ntifO2B>?K_;;ct0JwT$ol3~Yqx-$FejC~Op*+P@LD7|zSp||`9gLr(h>SpQnHH^_y><H9Bz&jCZp`OOn%=~y-RLC**zz+5bnfkwF}ieJ1&b^>x;MY%t1q&Db%6bUh*<YCs>Ln+fShc)z)3p3LNTd{<;PV+Axs<3l9CKbVBP=@xGV<f^vv!?Xr0fJyLnVMYlbO600X-;M+~`NC}yiE#GvR*-k6NX|aKr&uYi(2fEEuc?>N=miD^#J=t89Rj|y|90-bG!WhL}SPV<d2`oCmITn_1B*+b^Z*7>z)=Bgg1LpH>dU8YU^9u;p(~j|Kv5Ta_I)el&{}NQ5Rb*W#;GoBy=jp0kLa^e#Q{ZbL9$@3&5GZ8le|bxo7urZ`#~qpMA+DL*T_o?=o9zH<msGy7fNWutt8|ExLMY*#P>J5wa#;6}1W3<ev<}w0-*FblFbP|u<Gd+kfUk!?S55fP?}_=Pu}4NX$NWsbUM$rQ)o;}t!qqOI>2?5IU_((FE+Lp#(}<PBWk-BrC9FV&HUbPI6niLN7Fh;PXpEN#p7~f9t^N~silH!S&-5(PRNjoQj3oz~H7to85+}N_Y!>@GVl0D2V$aydD^hA=1s(XtD|=?SINhFs>Z5@35sCBW3e!{@&rVf7(*Rv~-CLz)DyS%*cIbrm2zyoq27X4wE3FE>dfY#(nWi6Cjx(9gSkaaMf9vTA2vG%^4BUYz#h_%NTe_eNF4EQnlY9vUKsFQ&$b*xRS8qoPWvoJ;6doq9?X7Mo!+to2)lF)twukM$TJh0G5}37l-Gp6ie5H+&kV98Pl`N(}CQ&;YlFVXaArpm}y1sxI^Xjr=%$}o|#}k-faw}pG3L$SBGqHgcIcW$vLA<tIlz?1wPw;rPs=M(<@YqHkPV18gvKJyoV8pSO5oX(2n1;0wU2*|8ldq$jqAu{O593BK@SROjF2$oc#f;u)v}v?6KJ!hlyC!dj6la`BTSJ5xneoGhr+u4TnJn)yinln(xPK9`ODSDS!aN984^u~o0`26@7&2Mo@}QMe@YM;!nhg}@?<cT2sTX)o$L>1_V6Upt>Pf{2C8Ojd;t+JST4~?+7Oie0CF^zzrJLIknU2JHfq744%IEl5%Uu`s6bA>JqSFdWqjcdcoK?8MgR_;e0x4H}lIUk8A3yE+Vwb5YC>>JE*lr>|bN@7~CX~S-Diuv1n~o4kg9Uuz+oMVDJF?J~lcOb~tRQJfS>Fru6CCZnu(HNhVg%&mS`22PZwMugRBcMgP4+q2nIz+yq70OWq_js00psN&gzSJYu^KN_;;^!?1YWitEl82_mH{~Snnd#XAQIWjdq4q18CO;^$$>Cp!72eRn$}P+;2evB^CP^zt~GoDzta==ICBH})|5iXXTvj&+5Bzw7IcgE_LT5eoQHpNdpYrN<u62uWc8CZ{)EltK53|3ZSK<Wu=w(olLhFJswArJUho8a<M^lpT`Gyo%OC(8Px8y(A1}4GXna3OV328IHl4|8xHN9TmMcpz^trvMOT|~(=?cn*0!_~-R8l${r(!-}x~yHwtXgs+QTc#9Ex>d!n-F}5FKmVjh5IlX$EP@Y)x1g<ZyD7(?VNLu4zTHzV<k}QK(-m;CE5)vjD{g7Fx9%sB<U-sS{-`LE-R`GJmTup<P@^Ttpad_c~a7qRmz*n!wKs%D^2WQJQ=4vp3Vd|cDBEPpep6aOVr3HP6YB80&!@@8>UKWZX~6twnk_!+}n(YpVM(;noJSPbB(S_)*(CLw1k-|X7{EHKTXP~SzliopT>Zn)@PUeV_sOH77tQdOrQoq6)GXFe6ZEjN<qNz99|Guyg%7K%iey&yYIT}(ePbBfkpLG!d)5J-)|D`c|h+SJEp;^BU6-Zm41Y0ox^!i)}Q4h2C^*jpw}c02IS?4;bCl;#jb!OQza$0gy>jwvOJMOVk^NDAWproua1H?#B@RzRA##DlsZWlsCp4CGgI(<R}%|ifN4ScOTp5tt61UCZR5^y$!wvjF4`SIZwC7))whf@$PqqGLd}VNrPLKQ_U_A?7}o0p)kW9D!Z*eWFuYLQ4plx2h}z1Q<Eini5hj_Gxv$HtO$nUXO+%0%QZNA3w*rJFl>m<_AR}aiRIf>q_z`r*DP;gQ7UF059z?ORvRyG!&-hqzkCORytv*M+WG%MI6t>Y@qP#8z06mk97Aw76tTI^f)GMX=Yy0qSEy~*_4!T^PJKaiif_c^EI0}?42vKhEw6!9*<|Uw?<)noqut28WsT`AGd42NA6POoJ>fn5`5)_INprd*bB7UYw1;h+c{I$lITPHIMv(6b=X@g(r6BfguA;T?G0;0;)K~+Y3v`2NwohRGK7P^iOTNsAPkx3;{p;1)_hAJ%JtOG){a1~<xFxMtb_tB@`Kj~l%6&8EXRsqfOzKA?YBuCk}$*H0j%5+7OxD2*M0M@t-0Wt`Lfz*UdimAM@Tt1TmTS-UG;r@Y5{Oo?cjb2QO3pBFV=SPi4L>s_^@<ciGmAcwhNH!88(5@sz3WBRM)i^arguyFDOS#A|sg<RqhH2=x-zu!<6zp&Wzua~vKPjzVH80F5VFwF;IJ-zFg17-KC6z?a5m0oa4@5qr4s&NB6BCE7x42MwL3doG83wJalYkT9XfzD5r!y_UWMS$G#k1a+BxOoIg3bu(qofF*QzdPAKv9mMtaS|rwjy@+x-ln<+fTT3H%>9h<q589Iax7b4d|T_mrDr=$x~Obz?0&IAYw;q;^qx(l~igE>13y7X!W*%rvh?+pa+bZL?w-y+Z=HvyO;2pp^z@T$x=BN0h$X#+k$z*(Yc9WUWyM7!H_un5s#|tF|T(4uq<G9DtiFYS#(qqVF6|bUWQy<D<HcU)y*MEbhW7nRe<qzrRn;@Xlo$$QVvm2ISk5^H9`nSo(s`3YZ@hLZE+@vOJ<Pybos8PChMZ$@vStiDy1`qM|}yM>oS(KG>9xyq%<v7mnNh`!%2&C!AZ8pj4iMu2`FKu9i5n|{m~82qM0wJEUioNPElz$o?=tUt_o?`<XcQ<6;346%)nUzKFc<cM8de{46*3&6+a6(r~P7v<TD9Cs}oU>T*s=YC4+*dU5Yvl#b8)E916Qyz!VshRHcr<9(UWOA%{8?&P&Ru?^szfkjT+Suu|S2c5`UCGIGCF1(kkw7Lv9nIR*&-ZzgRi^q8ER$!InNrp${jbY!nV3LAf@1%yk&!Z~p*D<%W(x=cHBNJns;t3Q}ywnAQ2&Km1l$0)-mBJGXkwUnefM0}-Gt0266d?%Q{QOcN=SCYgglFI7{FoxkhMU96ct}%X*g%Qp4B4&|!1K%E$S$jpUZ9G(mIXCwYKYo*XX;8V-0Ad9<BA4HO01tf=W9#nSa;KRx-ja!CU2(Kn)`k&4%jNKj#wtPQ<WiOWSAa|$Van81_ZXQ7gmk5z@N8<ZC_#ah$#l;Qw;Fbcplg(wx&^9f)G3lHn|-_+on*u3@kvWkT_m6Hg1LJ@y}=59$5qM`h1>`cKQ6Z^#ptsj0A5i!q+=3kbWlP@nwnU4$w{iok@(J}i_FSOIX+IwiSH>I?YWq`&4v2a#_01{VE(27+L?xvjgdUY+{k2EM!h!BFOVnF<AdoH9gA)lB!A(BH;Kv=x!_3R9#+0hagZRBjc4R>tYgXSN>RLK1@a+ZRy{9d*1UBz3Z-<DVmrr?pHz=B5N3_JeerU3$aO`rD`n|1#F=9?5k5Cx1067FPwsJr9?F+!m1AvzthwT*e91!7x{Nv4glLVH-3FXUuAW;<%b;F0mgEU51Q8rBWuMCjJ1jeZI!HG?Gp_QAPzKm;M37hKr;IKQk)cJvji<1X7~gLHlh5PTD<Bn;-6Ex>nDQEeS2Zo9^VXQ!l>&vG2G?oj(_I9>1Nk~O)eh<9203;&XHgu7{YG&alVcdTM<Z#VTVIqX*oDl^AF5+#b0sjj4eBaWt-b*9;ixa7b-$y6$D)oRg*0<WrY4nNdfFm)o(2%9Ck5BBZ)ru6B}qLX3M~$D1qw5i-*ki)AG_}izdEr3J2qHc;R_{SZ6kql>pM*VNRqb^S3HL+pjK-QNg;U%J67@G<e!1mkGu4|_JL!A!*Zg-9a(n~ddcwVzS)7;Y1)qJSxK-1bOApcii(jhGK-8<fb)2xbi^rGGOn<|99T}dQDGP(OS)@XZIaumVgW$oonyf%(1>F|C2AfJdR1zi%2``6a*zL|0^wZIe0L5408=mwrC1F+f4#L=VWYA}p~-gkGJDLNz?9%}DLxHjTy<kq7n-bkF<dFCZY_90W|6L^EXhY!_sDgpF^x3ZVAS+LUBTAsd{ODCiU|EF%ZlmUfB*3>q2$+TnIQFgV}61l3V?gC+G&xAjM)C`eEN2nwhFTK*Eot<rAnC|5*Aab9Wt+-d;M4b)$1n-+t>yO!S39UZW!)sAUmcyol^8iC#KQfGYXQt&IYc7h|xkbJUxh2k}^S3emTKi!<U~U<cO9z#<+4Cm6F@GCmev=Qj&)p-E{8&BDqI5B4)kh$!|o&!sNOyj4PM3%=lBOrjsa43K;+LfTIDGP6B(K$JK-}ju9;+R1=Y);mV7Lgv?zr`K6zJ1o1&A43A3jA!-xk_3`@AO2d_(AxP*D28&#{ygqA4l-aZTsM?4!Q*L~mh}#sbt|NS6!C#FDRE-7Gl==peKgAp|_IZRfdmy)!L0kZN5G9|Y>_1ylu!y=TX8`()X}_GlNk^L~pP(}EsNPAunxzvij6wz-0(o=Y>QSDytgFp6q`IDj&1cvL`nW94&Gtk32vFQ^?tf*)BbRR{tRhL(L_oe^3!yJXlbf{ZdF#CaB7^;adVUFp&hm^UC{-;ZnCfR!9nV>y68FeXULmBxA`!gyik5f=VjiSzCxtBaXq`*QMSx4q0ccOEp2pK?J<UA|fy}X~Xwfte&c`id4DPa&OLF@wpaI(%iepikmFSj76e9$9LcO-+bST?cvRgHhBU?f^z(L*;u~#>t6%DhSfuE6!Ob)!FhlP_uW9JJhNdskmB6Tj!SpLH7&L&cl)1#ATCO~Pu0_1BGfD}<3CB;BO;o8?qM1%pgWF{&pgGk<HNs~~VP+94m)nuR@Iz(Y#6*|#LckJPEmkc>KdO(SVE6ZpUQ6eHien-@y_1dk2$|!Le*1^f_SX5UP=(+`~Ym9pACZMjn5>V|zqAxr6jliSUWn2rRLH~~x$3TSw{)LA-H4^63o8PZY&<-?ZDmjtR3nsB;Qrp-{p&V(0$QGRfEo!U@3bR3>%^#bIYE4j_Hs})`JCLoj)C5JuJ?stCl*Hmi3-J_T;kRZD!E$j=OfX_g&{p8A(C$EvA0F;4jZI1GzP|KXq4of;Gt>ijorEg-u^V&jhvu4`T;r&8VjOYscdP6Hka~m2GNSjJlL3iEe8~!2E)%s8Ivi20p7n03ssx^BWdY^zo9qI^=(16xC^lP$rnm>Z(}6^rL-p~D7hkA*h!F6~i1Wo%8B~b#!=R88HH*}q3P99dEo0z{Gc=3R7Go;}AMrMn`qDRbxCD!K?O7gw=&(;w^m2hUx@bkO8<?SZ4s|Y)jI{EQ0b7d9wfS075fMb;E9y^9IErwlFku3gXKbxKiB$1}CAwf$rVFhp8LYw8$_VQz3F&C?f*lhpba|4BkCbQxrLzENViT~4kUlu+WRaWy)JpC0#L#Vg5?_rL-peNBYF<_nQD~6?<I{x5vqL&=-L)6fg+)zBAV!tJ^$fgfwgJKS5{rtVA_X8rwvaa>mSo}<$`ApVFsR7H08UxqxTG*%tdeSIdzTnih_H{CEz04d0O^?KnVJc*764P~vML&tr4CC+Sh?$9bQ0!*dgxh<=$!*im`aKY9um@|@6KhD?4+2|7J}|#eA8HK!y;om4hf4A*U_hIfj-%JZ}X;9wE6Aj=c1hxsY2{C=AA61XE9L`L8?DU@vE2SldURvmTr{m48rg(DV7CZU2@?;Pva{g73RhbPFao+F={A~;h4g&Xt;cPFN*NiOA$hT2cKkTYqIdw$9pOiI@FZ|Wm-s%1al1PI9HZv<OkVt2wNy$v<S*iS-cSUjjHR$BuV0gpJFOfsw^mn|7ag(&KLyrDZ<}DK_?Uo={P?CUDVSr;$@B4<7JyXNqU5gh;llS<Aix_Bh=Z1D<qMM4}^nb9r@^3|0i5v7m(I$D=Vs9ju##1u2(xW&2mfQ{(#x$Fgq1HyP!)+RhY$PH({L(g~Ve_Q)EWSDiedXp=J7I4*}fcfP_AqY@yWREN*{7NQ+fsx`~=Xp12xWwON}5hHRH1;DUie#aV11Ne;KGk`*I(4e>N3Pwq`Gpm&7cEurL8qzI%2?7i6EH=W4dcS<xvCZ!A3CCiwnNnu+)@ow^JjEIIt37nt1`eL||msD(#?FNkbd=Hfr?bM=6D4K|e+~G<lK%iua#CW1&5ci&-(jjF2`4qsGR1mswp$BfND*+LY10H&|;2>Rk&~UCo3l|lJ!AxTOX<!V2Maq^8gkmN^-F&xoE?vytJFvJS9?<9C=t#(H^zYTQ8q;G5EllJfY7$^}K8-2u8zL?!?a_|pT!K$edji7Xu{@td^C(C0bj>02zfRYnsmr}xY-4()ay*jFN_y4HoA0;iT;NV}j7Nq7len=X8o*rfv*hF1?&HD+CmDp^8GxxafdPoX0d%=qoYVp734SY7`UI^p8>(kV3`vxZ4~sRX1W{xYXvQt6FiJVefoV~lWn%`j3M+`YA1QuLt2+grk3~McgpG(dBWsu)^ab6}keiO?Xh3N&dC(Zp>}t2pXHtNWc{Y;zU~+Vek1y~;E7A)r$jM|_=31~{wN4>OD5&d8;0n&QB3_W9VdG}YZf09uXyX3a%2<PM!+md+3C@|)AkN5y7YAp~?*9PK!>)$'
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
