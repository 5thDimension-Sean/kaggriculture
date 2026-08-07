"""Kaggriculture agent — Route candidate ep=90726072 P0 score=149,550
Route:   v22 roma (ep 90473746, 2026-08-07)
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + Town-Center-phase-aware terminal liquidation
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -7)
         + opponent-dump hold: defer sell 1 step when opp just flooded item
         + hyperactive-opponent detection: skip premium_shift vs RL flood bots
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 4.4: _opp_hold_sells wired (defers route sells 1 step after opponent dumps);
        _detect_opponent_sells return value used for hold logic; hyperactive
        opponent mode disables premium_shift (their floods make advance sells
        unpredictable).
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<O>bM-4gD`(YZ1wgV|V9CG!tVyabP<YrhzdSpi>kmri*EJMgM!9SeBk1$-_hP-Y413DvB)W@$!E0<M8nFe~$k4>mR@W_Q%nmJ|BI&xV=5PpB?@E*MI)?Uk`6Qy!`#wKmPICzaL(IK6-z7vwZj~_u{)xKmT&^;qs@8tE1V`+w0ZQY$4vheZO3O9Q@&SxqSEV_Uire;_hhnX7u(?%d6`TN3;3n;~#IX-+g*}xBbTJ`}_aScE)r0_Qy{jw@;c6#`gJWwY<IiD(i>qo4fa4Uv1tRz1UU6?egks`_#Gl)XfKmPu=`=sFcgAcfUL+|L)UTdz>7q5`;MGpU_0us>Oa}P6yzj>#rR5ANly#2hwb(T$%jwTf=9M=lbg6?Q)~Zokz&AX%7{zz{9>D?vGvNuEqGWroQ~v!~Z|rZT5`*PUOjNFUATS$?~A8i@W8`=+)Chx1Sn`fiychi#9?GC0}0L8cz@X^7aR%nl_Kvytuvo<fuzNL0RY<i8nvoR$b#Y(Ohd{2}t>sXFk5jP5f3~G-DN|$>V2m7?iZNUNy`#&xW5)=nE}2xjEY?ZhR1S&>*qi<U8OR$*eo1zRbC>erF)(_8sd{xd$l9+Wcws$m9sN@`@jRd=dCv^ig15fv-KSLgus9MH{#w(MPYZu9k1_e))cRb9Z@l`IoO+YdwT1<QW@z;G<9H**DS4qDQvMw~s=PcJ0IrreJnryR!j*bNzu6=x;`Ldg$A>pHQ>;;kQ|*46pl`jnGR?5gDYK8hEZPl_Xtp-X;=fU+mGghPU>uD}$n7Btk0{Z=EDhKt;g;9Vsdfc$(eUuyj9KDR{615@zSveNK9LQ$M+2YDccF#Jv<dW*b~WnX9MAI?Ub1g|jbz;&r)7(#Koy-teB|9%YFGtmEAq(wKjc+c#}WW$w{5=^6{W|1aq)S(jt<qU35Y`IK??EpBVidU+|aA0`|Z=Lfr)>9b~DpdDQ;+(|}={r$zwpW}Dd*u+<(_G?knaT3Lh4C(|~@7v!VCo(d3pAkqdO`BX+o5@N~oEEQlL+ynb)Xu1qf2$3EcjutbtF5+zWiy<t?GNs}8=pTpS0KaaTPCSPu9WE6I7u@1%B*NAM`14QWOn80g)*bXU$hc8RTE@=sV!cAT?U?6A}xe@e=oD*Go;VGgYhw^_Oahx{?N(%r*~K*U$YW7BMwB%)ae){3+e1pz?jN3IdV{>7A_U5y_f7aPUUJow;Wc<6P&{9i+CUQvA@?87O<8NBZU=6krZ=STZ1l@L8DS&nfNAfKiY<d%U-m<j0u-HJVPzqvsP2o(LNYsIg_cZ8g{KsE^Bpt{qWEH74k>EDDA<Td{-zxSbH(IcQ+TS@0K?=KR-P4+{Ab+?lUf%V$h7dF1C&$aYri^1~P0YU2FM*K3Nt-uy`!9A(zCiO1T2~eBO-E<CF@3Iq-Df{=h>IKE0v8W+2Bo4L$jLgDsXe83pK9doovQ5xJ4<b)!@vgjJwSXlfpT-KNCCaiknwB)t}vCJ`tJGL)KLZqjH0RV`atC6a&i<Xjw7bILEqXCTy5FmJ)mYA9=D-6G-XYk*pE^c9%Bjs~1kWS|}PX8tf~o~vT1Gis>G-37+mrTm$aQ*;H@=F=4-;8+{`P5Uc4^aDj|(rSXbZn5?90Xb0p({1*Ury~n(V7jn|QnXwHFeTpK(brnZrj+uiQ?@5440iP90bfq~B*0@iNt6p~iL=vt9-+PK%gwW8%Jy+4i|S-~RkmJPUeMB@A<c7kM%~+1zxIlVBLqRf=U>GW8K#=YmbFqwpRlLI;*j<+KreK)mNqYtUG66w*XuA~7^w)5TAW|2GhMRf(sI^@>w-7)i1p#j4YN2_5onTIxiX``O6Upe@2D|fZ4XDx0m8j>jtN&mQhW$C<3Ugq^l;|@qDy_@RuC4gS*{#Y3qFPUpH_1X3Q{sx1+9fmfdyGnNR!{C?7N>XuYP=@?HRGgyfH%kr(rWN7B8Rsk!h2;B4+s+rs)_-HDm8bd0$CWQ8!m>JU8e(piVVgkYYR-#$!plwH^uE+9k$?%YY<XM}u8s*UTzRg^xFv5Jb*L%xAe_cFdy-Gs$Gb*E5=+Rx-bIaz?0f4IoY>C5XCxZpq50t?ul)C|Q7;aVtKCMxDfaSaRIkXYrG7%8(o;NDfowL;N7Yvh88YOVqgT$mPs?RJaY+EfIFif|=xLwt3iBZ11d!o7()Gv0CMG6+)&qb1SXYf%`9mmL-@BZ!6crqroTT?exhW1aLlQ(jPdkn*FT(zW{idImZYZqN+?1p(YqlecsJQ&R1Xtn<(%M`VI*xP<<QeJJ_g~9wBPhE~Em>^*k|Bky>jQDI#s)c<IW~rD14Msc$9=VW|iykk%<K>jl$65QP<^Wrjew5CWk+sU>h|I8xMtzo+b^72Z67ZIsp~0MV#cGhUS8&C_%pfNKS1iGrs=Bk{ErqAy!z`(a1QA~DWMzPQii1~i4E$bv87g4Zof>u9=rcXR!bgGK8h?xCTU)+-It602MKT}bI|RSmEUwj;68_vVF|AEfBTNkq}dZDd9s=i@M<YvZ`0<^h*RPG-MIA)rzimk0^CSrI_KHab;vc}xZ`>LeHR+SYTYqzh<}%l|2p^_UYp1-qCj@?pLI7CJ1nLSfNsMigLJsI)k40AYji4&{%20nW^U=o$fL!mv(Z<%Vrd#&0gnPsWC6!Bqi3r2sm1QF<rZn+x+zWr#T3BC{O;CsTw3%2oona>c>vP=Wt_LJq~`f*Lpgmt-*cniU+GJ`U)(nNp=GM11}{gg6TvZyR^=p^<hnh=s(%YKJyhL5Zi7*-xstC$RL)*by;9CyjQW@ix`P#Euj(t1-BWc@Q#+hlCCr934Y3UJ9yE#QWF)AW*i7(Kqa!uH>-`^w`8+1k(m5$*cRxu0|!YOYhu8-<_*u!Gr5^#_=?kDz8!KOi7-DdK?5q30(f8z(;IvszKFIu6#MwI?W7E>o+yJ9g@g^@QN!TeC0SIQqzZuQt*ph=o-P-&bglogeV&*Q*zg9bjckhhv%dUnqWxA-6v}jd+W<oO-}mS_VDU8JFKqBwn(T9wCP4@7i}wr%j^J(5-=M^V$!vtOkiC(Xf+vZut6J!IpEgXHhKw46S1Lf5j=1}MzZ5p#;qe{xR^AbU-FR2Itqv?AIL8;yI>#^WXVNH)Vcu*)G=XPgN4Eb)>nzWS11fuJQjlmE2r#LXvfE{w5gP|k0n6XUMv4}Q~`V2mYT{bfie#+&Z9ZGidV(IrGk!uXty2Rg+a4K^8rnt+L@FrQbx71-UJ4sQc1QJD^4pcTs3cBVzne}{Y-Ik?uo5EwijGpFf1hYKnGSO!kZU>JlK!t6RRpiZ9p~m=;S^?7Pbv2KtWN(C&9#4BOjIOvh#?rp;D$&k05-Zd^&XRI!Tx`!z@h{6Lth4hh|XW&7q$e2NAQ=HKscx)_fcg!J;1Q6Q;HcY-0~m_pmkpytXIY1(13Y-~b8<L9#1JRd{w<@~K^PDYahwv8l+>AB9#ud&cC|YqnR_)4*X0Ed5A<PF0~WL7P<mX3|UCqZA_<=N<t*LBBbdi9WkrwaK&Nhmgl%Nx(b;KCGQ-l3{VVojnhD)wbK5Oc~)CMYqzRDi1q+wF95;QMdQhmp%u=^v<?YEfT2Dm@b?#d4NEvBs$#>`@keQ$7b#`lU;1;Act~_h29tupSWvIv8AyeV7={=P4o<TBb#V@;M4l10kn6-(2BU8GUdqi6mOQXj;^kNZ<g*nT3Ki~R06V|4N7A(`ALqTplx>2w2r5De&liA0+5Sv53(YHO=J3|uQD&*V-!DYP=LJV_e%Nv5_t@gnnSpKwJ$X^_Tv1AU4WS7jLp6!`1YXxgFNSnp6BdBrZz=M`b$k}HbZynmI1}&*&=}%NfZKGnJCFEW;99o9?mN@N@5-e$PX^rn*JGcit;+Uq|Ykly=lh~yBW=Mm(on89LM&`ZnfBnZYKRxm=Tm-u*pY!!8alajx1f}ENGGgW_(1?FM{hk{EALX5*Q9;*#(PQmqfjNs#P6?efkL2Of_STT>=uzQ49rb5{^`wQB6T9sXfUrAK2vz)vwI<u-6u%%mz8GwmThVt7KkMDNF@yX9X((I6Ru5Ucxe#MJ=T%lN@oKeB{HDrj&x5wq25)u-xL857xmC!j}&wcdC3tbShQ<a*F@bt`4+erdAdA*l<hu0;O*GUBuOfnk*km78uF@jB~}i^SS>1?y72*%x#}z9zgI-(HU^~p{1r*9JBb)gY~9v%AB^cMSy@A+PA&s!ZCUg_9ZX1Q%G=+v-=-R4YRGlXZSi~+-%nmGjUn>ombfvNu=ww^U2-vU>hmNLCGVA43P2?AG*!GmP)3yS2>jG(Z=jbp}Hd@G&BuWAe%udQGrU2ZF#C-W>Q6v?n^|vLGjuRurafP3#9KT?^i}oj3yoc4<5*PGR`H{Ms6uFE42mDLh>AA5+hhE39C#{=z^XWKe6B5)o)%Tyy8&8Fw6@p)bE8>79DEHDH?p@s*QG@2iD#26vsr;ZRE2(Se>L~_%47O5}m1&0uzpEfP5IcZ9xM2t`Q&Qh3B1eRezQXRRE>)L7pzQI>c!R^)w2EQeDhe1nW<1O5(c%?%;Sb-ag=al1$h60y(lNxJeGMT0YvCAmJCbEt3bzM+_=XgTGJ(a>LEw0+vGlwsw-!>)Sr?^j%QaC||=*2IsU_O5-`)T65TjiJ>7f6aw%&C_RMw*_8UIyHslc=Ax*dxhKn5I~gdjMMF_7R3^<gRY5=&6?BZ+V4@fSNo0`>2yu1v0BeKLH>FS&Aw&$!G2Z*`exJXpF}K&73L;x56WDk}jx0_fJ>C!ua6Wi{sG3uw1>;`gAJ3F3PxAyB?$B&>BTFD&7Pv3BI452ol7JROTcp^B%u0^4#HGRXqbyf0Up-_M!7^t^&7nh$Qg<BqDOW3%b!JHZ_0CH-yd60gF-!9vYGU7pqEC+lSF*RR%fPk<U<wD44e!+9Q*_nNY`g9Ngm5s|7%XehXVc&8kSw1K2xpt8WuZDm=@%k&%k0~T!>o9?TuF+NV6OzuG!cO34ztslia2?h47e$t+^x+EuSP=ElpSpVsoQhN_C0iPUPo^n#R(Z%(Q_}Ej*G{e5Y#aaySHVUB=(clA0zpTLezSF6*S_97|v3zc+TZMNWS_*!5#z}*oVUMd6<E2MS;v&)PHPQw!tJVn@cROAKinKrVg}Z_V1Cyq-z>%4%CnF36#yWG~u39g*gq1Z-+Y&ZkY<U@uDL+^rtp7m_;f1oB28uZtLJ~qZnkL%I`<2O_B|zsUsIS-l+&<8n=K6TofZ8W%W~&G;aV^NR>E{{%M;TN}v}&RRr`ZF^Z(XSV5r~vfBn91xhB~n-?Y#kFXC6JO`FEM&}_C8B*{FFqjYru3@cWmt&D?WFKGxQ*JyMUQyy;K=W(ms;dGNBcgr_BrK|?^clO8QTqX(S(Wb2h&BhpyX3rfHEXUsS;HG}m@3Ac4f(`s|I|oKrc<#86?{P=_fuJwhhq%4Xc?3_=J65pS1*Z$<KUt*HbI5W&LPnaVVVvdZ>N3fH4o94ANTBHNWlqFKOg=Gs+6RJ7%-Yi+=<YXi4FyD602p4BtA%eZ$ILfOy&q8%q%cWT6U(AOjdTod`+bAAEo=kv>W}p5U}tmlsY6Ds|T{gfo<zbpvBwtU@^}{!Sr!wJj5&{M|p$TprIAWux3^(?%QL05WO>*`bHu0#?T)Hk&*M*m}>IClz9R82E9@s4vIgf0=x-fDvmheO$P{540wZEG1ftj5WPdyF>-p$tyvu6E^_h68l_DH4~K?=+f5IvfFEHZPR9Zjb7IDt81g7((OM86&G%a|5J8-6QV2p4z$y~EhkTLP%4FtIUs||0_Gz}4SJxlD@>dYJwk6dSK$#hGVKU)&*CENWo`b{4G*y>&6Wb6A5l(H_D&QDichhW&tW+7igz0J~Oen2gy5>!?K`Ze<m#PL|kJ@DMM@cAr=iwo#U@5$RLdV6~eTpmR@!LvGnFL{Kj5@Dh0EX@GpldD<ehVhzM9(5M%}EGdL9bbEK968)Eo+cvgKKp`Wv-t=r%(vPQ*Y|M6AR<$f*SvZ@u+6lHP0^3Z3665>f6oF)@MrR(9Yn%KsoI%?vowJaytPb&~$YdpmmL+aj{$nTho)}l?edMs7^O!NFxI*<D26mB5hoZ2ljGI*L2@pez8m06u1=b;lzN)kXP)tyK>%A5C0sVdL`llxcm$5HV{_{Mvwy9w5gJuqCMp;JwlelsVG-Ed(3$Sh|H=^fPUz@Na@L=Ob~KCn~=E}Wywh(RYfEP8@1V2Spe0_j=&D$t)m^45g9<qqNFpvVMg&ulaFQU5+A3*FP&Rd;uSlEcRN4JgTGE>G~?vik>EU2q8u9;hHU&GBrJgLTJ!{W5#4#!UzLm1DlTYL7P#_xOoC$}n3ZdR7KWPvBe<yO5GVfr`Aun7P!Q2zvO$Hx$0Id?u|`8pY~|v#ReSm<U>7SKQdE|2goh+juSZh1aFpiS2*C1$K!N^6d@*(y52C`Z&{E(lu^AI|Gj_9Mx_`>DWvi)76`*?taZTABI+;ctsUQQ68<;1<Adn)!tc=XHcd~E`e)Nw#HH&M{ADn_xVaVfUT#hU-?7F_tV0a>Egh1e7Hq_$FlzB=kFhgjqgmQAols3yyIT;YyGHfcJ?2Z=y>epQni*ew79>6e(H`D^l?r{gS2n`mnH6WN6w5krFjZ~niRi&5TWaDv`8B#!@h_ZhZFS1YCB%E9taB1<a@^jLjU{n)J@Pe$;Jnaz3LlGhk2$CC4m(F3Z<R6xd9b`8#hqoY2A>ONv67C?j0~WvhAyju-gS&K#KRRqg2!!Ohr4WpCV8O?y+0-w03w@$}t39Z!(5;E0z%{n+)8L-|RnQ^pzqr0yrm&RB4y^d8VoFJoh8ou(>S#4*345T8@v_AI-!Ke?!>CHe9}g%IXoBc)5TaF#nT@lxTY>18JOeji2Zu7#i41wi4*`jA?@mQ%$>@u1Ouw^Q=!9uBWArtuQcT12B+R$AJc#(+8foRh_w-QeU;OWY1Ic9na{b1$7$loWnkxqg1>=GoYJ5l&%nuM%y-JY${=w27ZL2fAI`<u0*Z@&%5@a?$cEr6&uD|($ujXZf4PLNXGB|?fZK$l${*#(K*BHCnj@)cz=R|Uq*e)`3{JeQcSgv-%7Fzj`iHLM(<g`tA%L#5OA}epn^~pmF)9cD#v&WEAP9hM$#Tt794WsODHb>puBRHUfk>?$|`cbU>?g;kT_>UR^!Wh^@2m9_07^TLbhIYsu1XnCi7v?6a4ZB~jK{PsG5K(+y0GBgmqe6!?itNt~F>O7&8fvx@4E^W{1U1k@h(A%A!$c!`RJY{+Emz={I5*Vo=5oAXhVM+9xMi&usUikSbl_^|K=)`4Tt=qb@(@MH^zH?TBZO7THdbnA5#lOV;in#OsWC|NXD|fEV~0317A+?|+SKkxWumA(0;G3SH#s+a5M+7s!7?m<sy_mmMNo>9LLO=6P=o=GD(+SSuyhYyFZZ6D9>bd^>~v?_*zV(;zbq-rL;d6giSQ`?L+%CJ+=G>_G8V%emXT%X*+ek5ZR9#4ohLD$V+Am$?3h}IN~KI06<U)8%CHkm9Cun9B2|(-3RmjmG+f+p{BAK<FoBl--sseu-+0d|;W{R6H@=j-klV?9m;Rj`L>_oEllAQ+o!&(FFW;?`u5RP>cYs|w*#gtJ)~kIvd2Tb<`QgCZaeCm_40f<<7fv<DOmcn4?8qs4ZJN;+C)iU7sfBg{641wJx=0HJkXK&jJ`mgWGumJa-POT#;4_$J;EGSEodzJ~DiTrPky+G?z>s@_JS)t#6Ov7VW`)~aqPL<bymV{J2x}~Yeqb1Aro>dctI%ZuwGR09cnDIc*{lcI3s3|&L>B?l80k_em=fv*x5rANMZ+6PEC-@wNu<mf(V8?RCi43$T{F{qLjsA@t!Y`}DP&mRiFqpJiu1*{fJ4hJlyl5NhA=cXmdL~^^d}qB@(&ItTBJ>8_d-R6_`pXvP2WTkw|1%sTx$}^Fg`&z(&2Y_%uzz&;qR|kBPMxr%6OX6v%Ae0nZ1hj9=U0owO6Ea<-w&C<6@bb#GQ*fk!3X2P}`K@YW`2ssemnxAXcr-?oahV402K-`^5J{AU#+Beue1k7!)M4r1-;jl{pGX@Nup2m)2>IiJAogq^a5}s>_@*zjc=%))V`ednlGAv5APvBZNlm*8R?Fyc9O1W3{3Qy`!FY=@vFxH5YexrP$Dv0D;`1sKP8nf0R%%#pmvB!z7;;6A{=u^;FZa%`1mZ>ajE4*~{#V_ng2ZOe!T?$+bA?(@ziO_P}_cbKjh$DUhp#-F6|3Q)VFLK75d6ffO9PI^;He?1*XZtsEisgnj%lLpo;V67L;Qi$B**^N7ZMz7(EWyG<8B#!y8Sc=|ckx&o?C)4&GhTv2+a30nxl=HxC*ejN4^sFO-T&`3`NFH!20iIhjtNFBfNr%^k^R1p!U2Z!yD8%?8H_L2lG4;9qxk~&JbS{D$<fJR}1GsKC4Rl0d9^%GmD5o68A;j1Lt=v0UKtG&Z~>N*i=a#_#jz7?Z!O4$TbV{RhFcFDo5Ko~X<{>J?!SksN!*wHiSIEOFO=&_dmG+D=RuoOR<q=&idKvQFIpg0$wprBeo+&R+@7T_2ms3TTM7G{fV3U)+sRv1f1I5PA%CuZTsx#j6d^OZHKJCoDuWlJ#kW4zu>X*YTN+L-a@L>Ogt);v%i`a}&*OL&&gdgN;N{Ju+z$E1k+XxRv<We%wcqeo7E_-zz{;Zdt;OzO^{90-*bb?jzngR#5RIuYz@Ui5F3h?%tO5y(V_vhkc`JY2DFazGHd&Jdw@lsq?(CqYanBs-82WiTD{q$FWb8yoQOBc62q9!+t@a>u)tvl9EV>1ucD#G$dyJR5aYvx_FE<{%~)Y*ieBufpkipAm#=+!Y|hn7HrQ;ea`w$D@G{zXJ~03GQnC-}wt522RAR2?|#R#}PWwF)e^&R`wFb&E3Xi@!c~g4v4FDu(6gAr=%N9S!!cDV!%-ZZKjQE()aVxiGIS4=V{9c<*XnNmrVLh;=Py?;BwRAiStBfyv)GlQM3YlE<9bU=N*hxPOd_2L)q~ju?HkA42i?IVYqk(v{A0LLnkf+5PPijkb%`T$ic0M0c$Fd9MHf>2qF_1n66V1L`i?!-$WdEXMTq&<T5F8K+Y;=1fhOf3TB$%A&@!4%{w8@2E{*DO7c?^fKtQ=B0;Pvv{>FWk_;_qIU}fj+@oAyXnF7d2bKvW8~'
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
