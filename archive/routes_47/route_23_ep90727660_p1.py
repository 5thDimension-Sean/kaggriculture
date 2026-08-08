"""Kaggriculture agent — Route candidate ep=90727660 P1 score=139,253
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
    'c-rk<O>bM-4gD`(YZ1wg<8<dqG!tVyabP<YrhzdSpi>kmri*EJMgM!9SeBk1$-_hP-Y41hDvB)W@$!E0<M8mye~$k4>mR@W_Q%nmz8rlzzqvWOn;rfA*MI)?U-xg^zx@5zKmPICzwcjvIr?yMy}bV`_u{+HKmT(6@#3fR%cI%RyQ|gFY$4vh`LJAm8vNmAxqN^B_Ugm({Pt+}X7u(?%gd{eN3;3n<Dagt-hX~~yZy%NySx9+cE)q@?#IucwojT5#`fiCwY<6gChNzm>)Q|CUTxkQz1UU6&GPbc`_#Gl)XfKmPu=`=sFaJ#_rKgL|Mv4*dz>7q5`;MGpU_0us>Oa}P6yzj>#rR5ANly#2hwb(T$%jwTf=9M=lb&e-EyPJokz&AX%7{zz{9>D?vGvNuEqGeroR5x{r^ASZuX4+PUOk&&c_NI$#So%^V{Y1=+)yxx1Sn`fiychi#9?GC10N37*7xV^7aR%nl_Kvytujg?5ImVL0RY<i8nvoR$b#Y(Ohd{2}t>sXFj~hP5f3~G-DN|$>V2m7?iZNUNy`#&xW5)=nE}2xjEY?ZhR1S&>*qi<U8OR$*eo1zRbC>erF)(_8sd{xd$l9+Wcws$m9sN@`@jRcoFzr^ig15fv-KTLgus9MH{#w(MPW?FPHCbfBAlSeS2|v@t1E}YdwT1<QW@z;G>V{*^B69(IZ>s<)hG}T{|&@DVUwu?rgx{Tz}vM`kRrR9{RTJC)8|y_-)oH!|Og~BlJ>JL<Xs*2A*q6B}rGDw~55r7kjj=;jMk^%AhD1iO@>LTPMjAP*HF|M~aFAo@VzoEZvV*3LY$hgxNWEpOaqR)K4y$+L5a(aWBP=*#?(T=IZIO4s*A0;q1$wcwMfN^zjzFH@xS#M_J+k>v;EuH0B@V_D!2onR_%%y2irp|8x3E*5w$zD7hL;K4qMJi`&|>US3M<hY82U`N3{x`mC83Xh&BIcajle|8Rc&=lGp9Hu2S{{aTcCoJ27rgE~Rh`}ViTiHywMX9SW<(<YbIX0p-~r^V~tP<vqpwKJ;Z-)aNk-8ty<YOAea*$gLZ`-400#^+DY70599mPzW6D<yh1PLj;MGAo+OQJ70RnO%8&q0DIU7p=ri)dX2zYKzz3mVsxMNDE=!-^;A{4C!<4V0_G}eeCxaKXfwx=^fU{*Q~_Nhy&3wbvj1LLOOd8Fs3q1jvN%Jg-gY1?>YO8Q@NT?Er(U|1gG%&BHo96?C&*&1+3-6NMQw1B*h%o)}Tve(5MtxCcX*WkG7%VvKQ?yW5Q()&rl2Ztko2Cv=7Eu&SWa9hFxou%UWGs-TyOxh5V7PO1rlv-xtac)?Uob?e+QUyXE!u&-c%KYhpYWcNv#WF=$3!7h6Y>xTBQ{0~t1yuC;tYpDYU^SUi^5kV|4$rCb4gK5s_oaY_Zi9C*5Kf8e19pWe`4Gmzt)h93RB!4^xKi~{tlJ((-Dh}=l_x>2eS!YWWEG&PUFZc}36I8u%-l3oi-lL(Xq8A?qrH)*ths+O&+63IV$axM<4Ipyc$GZ5-2n73eOHIy~7ZjtcxH9##n`U=cmM*~hNGSCitGk=&g&sDM188y`8?gHcOQvOWIDY}Ac^XUo^aIB5}ru`Ki`hg-fX*EGzx7d35fE=j)={9@F(~*TXFkM(fDO#=pm=f>r=xeQHQ%ZT%Dcchi20ME5fG;O~65z3%B+7-g#M$W`kI>%r<>uKkW&1djMRl^gDqF8CFKB7dkmfl%qwa01UwcKw5rQD#^RMEG3{%Zx%UUU;PuNppaY*|ZpclGYOPd$SF833T>vb3~j8p_jEzYminJ(FKX*p}db-|l?#QJdNhFKh|2sFv9T$xc|CG>>#chs1#wud9;0O4Lb$AqgODL#an@gOJ)dbo1{(WSm{D+r6$ELV=H1)swFPpi2G1u2=Ug4V*Oz=EtOq{;76_T5hxmp?wz_Ka9#-WZ|&)36yBi<i&+$h65^5wrXZ({zlanz8qzysxCGsGF-bo*Q%?P^X$LNHHD^<FTaOT91Tn?God{Wk8axqrtARYi1Ru!pECS2qNbr=Cj-|JLb{3nPjrz>lsZ@E16$9IU`iL1`wx`5=7lTw`AqhR(Ez?lq|r_xD_8mqfX*IEIID&v-rt3Wk?PaB!{W;A%2ix+4eByC2CxE<Z|XcD%=L^mIym$!A$Zr+dS+Wws%&=O>KV8SgrE83L#UQxs}%H!2Op&%Mwh6x0P$*(cqKvcKT!w0yv*D=?@%N&3@MYUjV$!oMQwHQB@|1P!o)&KJVrt=PNLSO%!+reTRe;sJ@N#9c<J~j}SF$7gB-cdY%}mNUb%D6p=P?ymaO0(lE5B)HjobuvCN;Nb3}r^@8ajh{B4|GD9F-2!YU^)Dk!}94TtS-&1zd3U8jkHcD#~fM`^!886E4=4rYPz_o(1M8VUbk@(sQ(U+~V{jeitkr?MBU)*JK1De87WWkqk!Rr>Lbu`_*zrOm!!J_pL_s~#F>y-v+iPbIrE~NCfss`8v+mYDld-Fof4^s5vB%<i!HZmiR^I;g#wQ*cg^MFeuC$nFq5Kt+MON0d6tOy`q8=b1TJSKw|b&?BuZR@#H(gifg<^Pn)ddLZ$f?doM`LN!93mq0(p|I#RBMLAqR9YN2fUv=Mhw?|i0B7bvbd3NrVOXcIa>KSJ<2M)PCu763;Hm(iQUD#hD7_Qy&4u}<GDIA1k=YJ_lPN+1Wh(((x#Hk-sKEa|A%|jeK@A*$OEQ>z%?gf89|v^YOsUcoB0hf}LYxJTw~agb&`3KO#6sd>wL=@Mpu|(k>?c*+6Igm??1-45lSaGGc$?~CVn>RY)fimGJO~-ZLqdlQj*g)iF9lU7;(crY5GY&4=o|J<SMt~edTe4Zf@y=3<kkITSECZyrFZV4@6J`S;K6k{<9HfNmDebArX<fnJq`k*1TOzk;3Kv-)u3u9SH7HToo0ro^_v>q4oPG{c*T_vzH%H9sp&&SDfmS$bdBI^=iE;PLX-`ZDY@%4y5x?M!*fyvO)w<m?vpi%z4c|PCMSJudwBJl9ah(5TO?El+H@ndi?)@*Wp)5X378EdG3nY+Ca|s?w3-Yy*q{x=9B^xG8@&XjiP+G#2p%{fBiV5)<JJ)}TuhqJFL}sh9R);{59F7aT`&*{vg9HpYTW<@>X<OD!9rmI>#M}xD-?z+9*e<(l~eXAwBut}+Ehx~#}XiGua$o~s(`(1OHJjJK$!;@=h2*8#jE1qQbET+wA+sE!k}5A`GBTR?MzA*DWh6hZvq2RsU%yA6{i&zu9~+mv04(gex^7%_r%s7+y7O0!LYQLgCV?m2FQc`cs{YJGSmiCbB|8$0%T#^fC3a0ReTamY&G&xsV+N@2pcM8D)k7$7s{tY_pXzKNi)pSL@{AU5OQb+72X{BnQ;&?J6&VCLt@Rx0TC?f!9HPXyTCT~5Ooh*^UrI0!d(EVCjkzikPsxhl2nCfrzM}-MVC_R#UGoB9Q{#f)w5?zUcF{}RXq(HrohsV6zEhH3KO(R<!>gv#63zel5y@4;1l$lbD8L~%T=2^JAMdx9F_#kBjCf@nI;()m)qI%fLCq1&B>Gzu2FO=4XX06!&f`-`5tw9PkrfgAWZLUE7c-_`i$wq8B+uZcESNlCDG}A*as%bIW}{jne1Xy2RW2eEcC{R_{3dviY<-(0PAg^Y@%n#8`(tL1E1D64WPXvhE~M&lqpB9r+BlBb#!$Fe6w`t(aJ)@p%RewY)~4T$xm_w1#PpFrgc2M^COS@7JyuYdyo|oY#P%yeU*9f9;5hKg979=zgNoVm&jv~)EvU?t9_}Vu@~n@>;l9rXKeN@!OMf5XP(n^V+L8xE@Wy`l%zk`q-Ha8r*0WgOr9+gn2|&wu$76D++s$Pgzw?JQllj1fq?wrlC9~VF{dc6vrGD{Qr??(46&QhJa;M0WXf@Duk2Qfo#<xLKZO}V=>?m7#20)clHkbFRnCGYIbg;|^!y^YzQeERv?PJyP?lY=sC7xy+oxL9LD;8{V9iuB*4QN=u^h!v&?ezXr5V)}l#<$${PKZau2B8TY!7>FA<Ar!<7&IpQMO9vC6&Tdz;;%!5`e>_3F;**V_DQvnli}|*U3jdENMz9$Z6Xp*$K-n)cIf?{2+Y!U~;F*H$<mW^)ILRFYW3;8)j-%agPnRgfCF)mfuBOZK%oep=5!P{7*PnygQ%k@9(avX35<4IpzTb-xQqzhaXyMdc`q|4?S3K>ZZ(TD_aBzn4x{!TP_@<7hzxWQagnN_c*)%!PGF@3VepIL&nW^{V)@kb>DfFU6Dk(UOS)MEf2PlavYRAV#oj~FY%$<+-s?1N_&+<sUB_2t`w>}GD1VsPzACXq!JaV^w^fC3T7r%1nIs+q#G2k-2fXiJGemlj`DtG^u%c50r22~j3?t<Qf=gx60=fU5G^FnF(xsBwUV&P1cff>Y4H>L?OpxmS;8w0B@Dy7utNP_Xl2o%hMc0oC$8FP=Xqe=4Nq}QB;7_n+k@3fN`~(OxFOM*Iw>&Ws0PS~vD+3Tu<si2QC@i7DOdGpxljdAIv?ceVyi=(hEPwVKq%G4Y(=pC#HJ*^JKzqEC*$n{z9-3aoiC6hn}VC<0ITJrjR_KdVcRl!pnSxj;xzaRRUkLq3@%_P<Zo*yIlaE^15e)tWsUMR{A6%Wd!;m<!>u)kZI~DuB10hnzk||4sGm)#kGe~>24F6V`k8yOjJ1=20$Vf`)k0;`d{Y$!WKluKs0}8H5s*X{$$$`7M-Q+z2z^ruRS`nOz#QYf@9y{cs~U5Ay{RCwh4LhMJAE{VssFcw_lJr&Wytf6_ZI(nqEvaBC&+MzW}_Qf0`aoIeYwRs@%oSiv>@6d#Xe+Ka-1bD4W=JuxpMjHA*%?MIYVj=9cq-i<G@e3TB)ovL-Mb8Ub^A!$hnAFn)gr>`!*DPdK|cty>(p%wlx4#IFM|3rw*T@t9EAFbq64XgSp0FS%W^C{$__{`D{Qq+dM4`)gem15TRRU-$oo}#lz)FQj7$9C2*#R06ce?oz7Im$;)KGP4Vb%ZC-da5~`-`Xah+D{@}2@HC&$8(Hlo`LPl2f+)Jk8;_)T~b&SLAZJ8#C{bcpWNdBS_wO(HZjrbvkGr|>b<#Hb+U;UwA4+0JBLt*(m%s{uIK;|s!KejB}V3L;2C6?EZ?!ie@2U;@w_sC(=H4Qcg>c{v5%4S-ca8IhjoCd|W!yO2>Oa<F`(UBbbQyUu0qLlp2e4Pomb#S*)46;w<_aoIN$%fL@kqaE}RD>~&TfhV^ijj}9`l(5pH-IXnN*qZ4w9O19&<mg{0(zAgMN(j_pwJB2ZG(>jB@^$>3zLXP*arrl14|mC^AL#)DR=}JOo#*5uvVpOF?2!}sYdnzCNSm3gW(k=4hA&8R<61#Krtffw?M+8YD%B6I~lbf@R?QV?u=-2AiPV?Yge=8%9Ay`0f(t#%-N7ntoBch#AG@Zdr-j_ByvBMRe3nZaEq2fnPUqdF@M#bZ}X5?I1Vm4V-r-^>>Lu^5T@zS@pjsmUh@!*`Ek!Kh7_C-_4DD6ph`(fhykOS#GMFDndndeC$U<#NaBOk_x2-x$z+Zo!ps80q-AF+$z)|W%-2K;|53UxOuNyq3jqtCLa9Tdv3ej&9N4z51X{dJ4;J%W6igp?#zV|Pa+EiS4H{a33~Oe!;=Vn`2hlr|sc#e_Zw&oW5E(g-jj1LNOqmyeZ_q0R;-L6rD!`i%rs9Yb-gJO4#eg@s6=NOb2+=!K9V4g5+?vH9?jjeDtWnxT@Nj4-xZU)y3iuHmae6?-$ZiqGW~_-Jk5U$`1@X~*zZC-!#Mvf=AS3~-BC&hO7m2M*W*+sWg^Ob!=XQB{_3;~j1%Yc@Qe6R*nIRV@6MlCck}T^vIE+kFb!j)T4Y3g6)OM``j^TAT&8EmomBCAxu4cl7(%PkK-Xt5e5)X8#YVh@_O%{KYgu-_o9+C={!uuz5T%6sdxN;u8y*Po8%ZCd{W7K*53@~hm2VHY{@LMnuCwdmCX--1u3VO|Q^LYeYYgvOV8(gakDs%k=I)y?Qo_bU7omd!07u5JSj7K%Yu6cHOZWCaiQr~WVwmwrjhjs=B2FhuFahL2smfHykfu^gw0Ih2jjf>?v*qWX!uS@`7Ms>O=LmC-i8Q&Zi5ozOMJg}Ezx~BW)@{3){rog3e4<`mZhP-0G-Ieo}didw?)GHAez~x_Xw}H4yFoG1&rcIUP6zwT*=@GIVPDQ!W*<;QtKx9^R0`x=IMM_T|WrC3F*@Vo+C`(QPsVX8V*r?6E$^xiXnFwq~WB?_LlFs;s8O0|}K9;FVe3%BmbZ$|JSL_tt?fmQsth^I&qupr6$&(|&d7?x)HZly^_(4cm0Nu6d3GO1g^Qylp7pqlV(5NhM<@1;X$3ieG*8(jJHv>j+QPCkz{QdKr(yX8$qQPW?3WJYFY64@8hML&Q#c8Yd^ijYrRyd@nEZ+zZNu*wnq;BCT&9xDL<q3fT{fqcw>@Xfgg<YYgz*k~3Cg^7DX2*2@lx53SQ<*A2_YC5ivO9D#jXF|61{^mqPliDtMSxiunQQN4;THVpA9-pP*PcH(1*O7}$IG}JSzy?8eWAhdM9>I<z{6~)#g{4blvZGd&{_%Q<d7+CmZ5SoAhKoHR6f}qE&kPSyCN3j!2LXcVG?hs1(w~z4rmb?EMRLuFfnLV9YPzaKvSzqFTcsg<190zfI<;v|0Z5!pR~@LTy`t4#Y^Sqq&>l?CYIm@S*3Z}A&`e6L>dqzH=Hh=!(hojEEzk<Zek8^L7GCmR~seVL2L&se(^)7?z9GX=@x%<*oY7a$#Y8~80o-*kB_sdU+xzAMEh2IP+6f{6Gee*Y~9DfJ^rhpL)L$BeYH$sDU%&o@l(Z=k|GT?u0hn%YR(e&KpW#_iTl4{7z&3`m5e_gP$JL-(cvIOs~9sIGi*V}0!)7r=!~G4OdGI+Lz(GBhP>m4fJC@=ry{gu^u;!&-&rkm!ep!Mve&3eF%8p`FyGqpAmVpxq?HHX(?h9$@xKEOB$NHi^&8J(kZdApt{fl~j0<w8@gYqxKR{IVDnau52TOajt<Lo7+;?nY14OY&klFay5%(s!{^kq5nwJSSc)@DP;0T(xp|VQ*Pipd9W9(`>a<i446UkL#yU5V-^X4I8x!Mg|XyrpDBGR3a(>CEPC%CDIth^=HCl4`9uPcAe9>1{69T?Cs%Km0^)XhDD11cE#wqsX6ik06T!9E-RQ6oSY1Dohz-`xSD)ELyz4!MKiisk9T+(flu_v<x?Mh6Tciq8w+a;9ul=#WN{{kb8gt!Gz5%~pb;A3cGf26_nbCu(z;Xhe_dmi)iv3fvOshPvHcju*`EooN%dto0&Q#6XD-T<sj_9?gNv$aGsCq6nGZy&!Rfuu9p+N)0VST*WH<)B`Rx25J5bhTwSY5NF1s<)lZO+Wn|Z6tzcy^ls`V=Y|i0ERQ}|hQ&|yM<BBZN^w%iBh4I&FyK+e-AVwK?xE}D-jmZ~c+-TP?ra;|eVp@`B}I9tpPV2O9>ssiy<nSru+mk=Vwl4+vJ5?&2*$RJTt}qyB<6Fh0Oph(Q|nNvlqsV^YcgpCJHf<pr?nwcCE25Jr9Mu>#SO>r7IOs?XzA~blD>W6Ju8Omn7G~eQu0D>CwE=?cXAMU;LS|dx07^w6XCynw@$jcjnm%&cIjjbOygRw_T}Wc&0yz;18>LafnPJ&!LD66)f_X)^&PV#r|7k5Mqiv@PbH)l+672JAEW6aEfhdrd71k_Y}e0dgDrGd2h)MiV48s|KB0CRfRw99M1e<UQ8NNV?g{d&FxO5<HU*j$ZgYv=isB~Itt}(0u?YHsVW623Q|+!omj%>1;M?ONNTFu49%L^-5#SJA1W03~OQm2+s2AKGD~T2jZz!=Gh>|6dGG|0<(v+CU@2_;tOzRB^Bu=+#S)wFT-wAClEDp0%8Jd_cUIGp+yHL(C3mL-D*jOSHtI(fpOv^twoM@3YncWK&8R7#U;WT{{N!;40B5<uqB*XXw;Yf$y;W0-Eg@?btUX7UK$tmM$O3&^#V`TO!)_dfpZPs3q%9RI~QjCjbY7%!Y?nIW+SVL`7hO7BMNv8s~ID%NUHoHI712M=+h3pgG4}tVx0r(Z7uVYY<%#z{{+g0W$Ai>AA#$Q^eJtk@v1dyg`tEet>%KX+{eppZJU+$q;mc%9^DvuBvv0L{$ukljYkdD=gCiISa-lbdEXw_WY-IZcPQvw8Xi=qm%5dBd?$rPWvyA6|kT1-S>@6=OG*`!`MY*G)M@y?!SXS}Bb9$```*-Ea(NuPdtD7Od31D*TkEKPx2CG55fX`C_xDfi)nEDNOI;MF0w>0?Jsb8qDcsVD5?hZ)i_E0=ihfLi>yZkk6l?(?Pa%-U_b05XOus=(9FvDOt(eVPU~DCdgOGfmh+5H=@wS@Pqsmq49V3W7#@B6x{Xr%a?gibm@AjX#arA*PCmI6XLQhumly)v}i)XnClhW|!1a!qvKfI0iHd8=N6d6s*$CQ>mZWLX8+}J`P_c(MD9KFrD^Hp{^5=CYSYW?prY$r<6?~HRdK#Y?mC|3WQ+;;cwhuf;HWkjU7FMj&t}jjUH?1Pm^^F2TSpzNqU&O4m33e2a0p?2@0we#GNzkU;&O1f;wWAWMQ_*reH@DXN9qJgd;<Lb7B^5oLiobG+$Yxx-&VgUbY0E_wjl&tF}x5dmX=S9i8h)7-ij;2g*aAsKIFo&+=K1T<yNS>(b&eDdIj_HbQEdLu$h4k<%Z38%1Dv)M^@&x-%#TLZw9=yBXSG>@KxV1iP9S{aYnsChd9zGLfNdJSQ0sSL~Y{5JavsMCctQ&kf{B5Yq|C4x~gGOvgMaNf^||20Z+TCtbfsQ(Up!@vh~p#J+60+TA*FXsk2OMqSnHq6w-wh{*+86^G!faJt@S1fd#t1;{Wa?mKokV2-EpXyC)|fJ1hIyC;gD_x2eO11DnE1cfVu;|QJTm=?e>D|?CJ=5AxM`0kk#2gKDn*jUSmQ_>BlEVZ#6G2keIHq%Bn>HGQUL_cB2^R(rJa#oOsOD26L@m|acaJgym#Cf7KUS?qOC|UtN7oM)w^A1KTCs(1iq3n2%*aMOlhQwjqFkCzX+9=oBp%a$@h&@(%$iV6v<lt7sfHf6J4rpK`1d)jhOxLLhqNKm=Z<1VpYkQI?<A=nbkh6*z0TB00>8F($fXo?g-U(@z7GD<eoBE%h1q^buAmK>NHH8Qh-!zg8EoeC-sD0dnTwiH<@BRn7fg~I'
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
