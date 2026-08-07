"""Kaggriculture agent — Route candidate ep=90638412 P0 score=151,029
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
    'c-rk<U2j{*5&bWE=7UMeveP%kzKMk>mLbU{QbPy=G(~|TeMtLO^uJfJDDv{o%$YMYyO*@;C({(k-8(zGJ0EAxeEQGH-+uZ1w_krh`O~M94;Qz$C-;k!zyI>jzy9mtjfa=N{qp-ie*O2u>rW@|E^mg1zj80W{rJ<*7w<2Bytq19oV>YSpDb45?b~<5@L}|a+hKV7@b>!MaB+9Ccr|(Z$KmSw{mEjv{rHEQ>$e}@-0i;c^8Wt6i@oQ$eDlM{54(|;qi6ecvL0^lKF{_2_08S8&#$&`O<wE^;&!;Y+Ksw2N8Ns4JnHtZW1(DLz5V$?_;(*S(&Of#3PDU~^Ap+>c4D!I%*g-@y7|g!|0kdR`e-)0C07=I`qp^t=~`c1ycxEV+#5nZn>MI;1qS<Wyg&AZyP3uxI`zkIJ^cUu-FDCD??gs^b1@a*WG)Y)y0{x|Ca<0b-F<2@4J6sgS+t$Rc;>^!tucD&mv=uX#k3t_`{MTcqa!Xkf}-f#8E=2Mt+=K-(Oham1?2pdF&|&#7JfHhv|<&Z$>V2q7?h;7(Hdr%7voPS<b{+?Zq7D>n;wK6BuMC+d<R@38NEZ|%bW|FcSiHvy<-iP8$c1(_D_=`lTWalulV7|7lGeJ9|h(W_}Y^eGM}|B+Q1EoK6-t1HN3g|`Mcrf?(*vLFQ28>`Vr=s&(z2RAALH{zD~V7^~hHF`cdf7Zk(9W5-iSacQ)W}Za#1Z{msZu4}IJA6KXa;{5I>9VZD#p2))D<nS&Hl1JAXkkfbZl+eG5*iw$i{cxT_bb5I0~rqD{nJ15DTpd#Raj1&<EJk9PpEZvV*0v@SA!t9*7&q*(D?vV?ocI4_x+)J@zw!tNoxq5o&VeU3AoPGHdugg`EKHh@&hBuCTlqC+Zj(2ZJV*WvH-?S-_xkuBiIu>^SpVL>eF303W$<<);Dbws*+}2+7@={_yOgJvi4|X%t7tOptJGxr9lZ+7iyNjDY$M3AEiLXZOH&aQ+Nfa|OC=+D8?|yrl$jID%Mj*MgY*MYZi<MqDEne@2+6ybFolzzKR(k;6or6BFrfmhwX1rLtAKZI4zJ7A8K!(w`Oj3tjDbcfal4S0c(P%11VXAgAyYloxS<&JzT8W#g39`A=RxdxRfoGOT3t`#c%dGee>2vRBe9XCh?6;TScQXI!9oER#ti;WT1JN>dI!4JtGJBk0Ok~<Ta!{leE)^@i=j=Dm<!XLuIjoW=IEU94@jmQh|DY)>U@ad<3M-HzDdw<t23;zHMy0?q@lD`<v<(fHy=Y&J370v%LM`00R!h{;KA2)Tlc}s4cCAe=YkhtF@XzuE<&WqPjR!;Xtyg}q@nUZ8ZZ6i}4mUSHJ&gH{iSbz7XIwVLpqY4GY#l}7j#erRWY|!;*75~?vaE<;@pR6{yd-v2&MSb==gkN`PN@Kx1Ec%)2Y&S6=neff13At~=*iz3ZLze;C_um3$XuyK<VLdfMyWywi$Gb>)H(vYO^Jo$NIAMldMTDRBTy1#2sN#4(r5uyExWl&B>!aOTpUz$$}gs8Ae2)uZ^5o=C~IWhBH`t0fLe0o6<EEF2Aoo4pdI#R{xE5ttJ6|f)DV-q3yil*`7<S_=uT8yPj?al$J*F$+F#M3A1G3jRuhzUi>;Rr$bssgZmWkp9a(4t(}gvZqU9QZCGq}_zSe4PN-2-JWCw!6;5zeVz?YLg3Gi6X66L~L;_UpMM`-W+a?5O)vVEM%qB>b#m91Bn7qm2JNb{UsQTMjhue~DT2tg3=`B(8o#;NA1Wv!IaC+sPq9MV1p=!LG<()I<i%l(AoMh^pqk%|DR#rd^5(}69Qma8__3*O8l^ut*jMmg3IXp&pGvY^09XoSso)R?cfha=_y;a)n&gexF9eF!z<K~NO*aPI)3OMT&15EiXjt{f8!K85+8R&xysQZiQst%Xg21z8bDli#K6yB{yFet4qonXtyZGD7|5VKXomFJJnRX_L7kX89SW=@dz|VDCqHUrAF@H&<&sH|RW|PBnWX#dt7`$C7qyJrcIFON<Mb0ZF!w2D`?tnN^qzA8)D<M9xRdXSrea%%cl4$z;RVGm@Y*nOB{h5vp7Rh*L=kqVC2mS^2cpoz;ty1-N}~#mCU7lXwqHKKE`ce(}vYBp(wbhpF-*{vm<d_AuooYFu~Za^^iM+y;6}gdMYBCV84|2m6feT~u*X+n+PERgS9=GPPM-X|0aje;Kqa!DM(_xfUJ`j+D34XB!CMd|pd`;IwM?v-bZA;ANH^BWQ@KGD(D*U_AACH&;1dfqB?OfoITnNX!D&w~@Ysje6-3qGs(vDzIG76C)9+wT6)*(gu!~E*yO}3@s}4&14}g6(I$)b&AV+!E_KrVa-UHArLNvKxj{D01gdDidyjZl%2H3n<uc1($WMV8r5pXN*UffP4xg=D=148JPjI6U(*m>ZI$hZ9Vv^%I5+dveI_@c2^>Wh{28uz*}}ArCcC#c*B>}ov>xIf8)|8}(jYCN-O}$uLT@W-fL*X1iLJc1FU0yFL9fmtf<A3CXXJ4{K1NhGPAg&_acSh{>=!8nL<-{)p$Tp^0?e<COx0W-lfjER$pyK#_1vl11tiGj|CGgg%n6<wyEy0h@9KYg$gt1~g+;F!QGjuw((1GUgbl_!lt20fI12}&YXq1H!#ahP8@Dx?zPU0#8GB3%t_lDu1<<jJ(mT`MT$yhwkBGx9GTQ-gGDS$BY$bpzR~(!U75G0S<WMXwsDT4;Nd}XzS;3Lz<A9FaB~_Y2#MjS5h_k?PVr@@fC<es~{yq$BVB3ZVAyJGSfW;AQpoJ2CDU+pCEl@yH%}^7upl6LXtMN9~^u!J<G0GcMdLFZk!Y84#2?x_qNSH!46yZTOUI<jVVz3Tt0w`(k0-H9m7s0Z@Me@povf8Kwg6W;R>brB5q<K&;7aXl)sZbk5+LT;7DBnT2m4K}<iIc?krW%6{rPhbJ^fdE$T6?O=?T`c#gf*@N2$s(gnKgZ=DD}a}<F4_6?VbCnxQViXG8KBgo-Vng<l{M+g(i@bX|u}Oj6MA_MU$I-ZF_j-ogK7mwk;B>8g04}+6CuI(KS2XqQuw6ftz$GDHDfR4q9yvHa4LRAsujQZ5zFWyouP*_7prUL1t#Bt&Ce|lHuCZd^*YlGV7ors@fp0Vs?E&B*>DBkf>z_6b59*xCV=y3Fude>{kd37f2R^1#72DR!GN(y0j^*w2vjg?Ov-EbwmMM;g)*PDS<K%UCx6)xdK_mzomkXf#A3u-GxE3M6Uu(p4yp|tZ7E2wcY{-qEbn67b{LHEL=6sUn0RIZ2e3vb8f`e9^3y_HNv<OnL{nSYUFJk5~y$(&nH%dhPsAo?$OzOfLm-AP=FIf1)>CTTaBw!ip$O;!v0H{!ajl@hVtpqz3U`l(uA}$uT0nxgp`{>fj38rW*kIJX4jY<k<j@#eu4!_*e6VF7ud!gV)|hz0(fc9xC<atCBOj`5`ttClj`KzWyz;@(WTT{`D06wV@nEYJ$uIF#cOtB)ziRX#w`6vflgJSjzL>g{$|oE;-ict8Rs71LqU5wm$*KwuG-?+@k2=aFc2`0fDdbDnq*j9ZfDN}Ubk&dCsRhaq|q%*sLqFde6?Yp?@_n+)CZq3VSZ;@DJ}_=bIcdcm?J>27Y<MgkIoN6RxnG>v6=hKWEYz{$f2BKp_N9&C+?b4Y-#KVNOJpR6Fo!T$R^qz_`JSp0PP(yv?8vjOgVBb$eU%XquLel&C-oZD~g6gB_QkBpprI|pXB%q+GZzB>v(?WM;`Yr0J#YFAS)u+G^TI*D(m76qxe~)dgTorSjy*@$YYSy9K-FaZLFcO7pGI~0>mt5Yz{qxuLC{LJg4c#jIx?txYy>WV1KSj&1UFM-7=tvKU*X)BZ)#_D-#vG#f&Bi-@|#OMoG*g0r^3dt;wG;rzo$pOZu!*-kWv|v76C6cPY(e%5iKj>{iN7G(YK|!i=Ewf;~av3g3uRIHJ1BS<oa0%=n0&Uj+3#{EALX5*Q9e?Se(E15t0E>TCyLpFV;$Q_WZ-qkueg6hlFqgd>$^R8vq&YERP92X?u_3@o!f?6rj$wn2`o?M_G8Dw&s53R3|&TER*H4v#ibFJT$WqL$K>NlLj+KJszRrj&x56~3(WTav#2(K`4+`0~-@PL*$n#-{3D&hcN`)qyt5)T+}xHQW-uK&e}P7g4*Rp3KLR1xEA#f^)_D>$&;<zE(9$=C;o<k0AKw)ERL2v8ATh91;20gY}kf&YZTgMZg48EOCd*g=6$0Y-3*PzL20QXZJr?8fII8&+v7~xHqpKX5zB$d#|z@Nu=ww^U2-vU>hmNLCGVAgpu+RAG^)HR3%f|s~k%8Xk%7WsAkFt4NXH8$lj4kRG`w5Tb?SI$W)m~cNLLtP`q{nY|QM#1=4qv_ba0(M$Zp`2M=UC8RwGfIyXqnN=+eJ%sj`K#7wN!4695~=z^XXKXKSr*RP%>yy95GFw6@p)bE8>Rvl`{Db{@As*N_P2iD#A6vsr;ZRTftusTV}_+0=uBpO*KCrmi10rFw&wgvg_yGDGJ7oK;@RsC5mQ~{LE2YI^K>JX<P#M3AcN;N%O6Rbb6C5i72xP#-#c>93wNitpM3*^YA;3hf3YWZkmf`nh#woD!fA2Fyn{QyH1$PG7x3s?&I+uBJ^>$iR2>ARpTQND(s49;n<ls<L16X&>V6GKB}2n67FP<jZpzbUm{cd6C@%taADb5EABb}~?4PYp%2P?<E}R0RQ9RM0W%nu%frB#}ijAjH+t1FQ`~-;_dC#3W*1j_KZa_xtiijk&$vgAmz5d6dcO43goEMR0DQPrflaHXbDY@r6?5X`Ud%9h!}9WC_H}6Yk3`&P}fmNk9vtEppn&%u0^4#HEMnM_I01zIw<if@RK-nnQ;grS3TJQ?6Dj>&%e+>z!3Myd60gF-!9v>UrOWqEC+lSF*RR%fPk<U<wD44e!*)r|7Dk)pp$h2;pF^F<921ucp7*Az3~f5Y9GF%R+UC(l12lmf5!vhgtD(xsntk!CncRL2?M>FDdg3IF#}ZaUm#5;6-{l4gyOn(%SQ4zA?O&@U^0N8WU4_sr0z_tRAN<#dOHvqlAzZ(y7*N6NCgQ=J{2iJ>$+#l({&KTJx`hO#GO`xC8`q+P{`Q_}LMG5z5WH4h%*>u~&dbNR{bwxC7m+0;#m9L)o&9gUMnxpRv4{beB%rKG3u|yo(OAuxa!;5I+ViP)5{X;y<a9a~dVz4u~N9G!=d0g-dd9Q0>uRTBYQG<_k}_t%KW-V$^*q;U6hKNp_f~j$Gi0r$UZtAOmJ}QOtjo=1(osvH^A>Rr5ePtZh~(0cQYZ641@Wu#y6W1qE-&ZX0|QD5-gGU6{-~0z)u(9a!TSU57}hNb!?lbRmvp!&1fG=PK3NK0pno+;}kFq6Ef(<Tt`qwE|Qpq6Q2kPO2vK1-p|`KLVd>m2TIFHU|R0<h*t@jjoKW0T4Kl6=TkZd}6hsDpT+xt8F^XE6LK|Ph?eMj%i%6Wl-i6119!pIbJ*`T8^WO&e)6<HeH8=JA`>VbO4_ArI$QrV|m)Mts#XkL=ArUBdAiN5~9RtHsekVr%ZGx0GwD4EwcI`7ry(5UqhK=j4;!}FpJrlTQXVd4RbpYCIFQG3-fUFYfHf5sZdgp=(HY48wa+nI|D7=rU#38atfxgJL4f{F*?c{#0Cv%AVZ^BEx~UO`ayipWKtZ3$QxsU6o^L7V`Iw8154%w;2ShgfxsyKm<kXngt<B53^*MyO)(@6?#)<7JwiASRoKYMF{iUQ#9bukkwr_}2p$d%1-F|XRslbPBTkRV0_oPCnz1H^O-fN(ix*Y%{niX-5NDed#*hTkiUji^UnHiP%sT3-g{x(s)^@nMe*c-!f&jV=RGR>0Wk|(j!tbs_lBGchhmmQj4t7`D5G@f-ZP!ZT7@~L6Y>H^A3|_)?H4`S3)-GKHC+VS;c%aK&gRe(zvG}7T6u$FFq^V#jynjN+#q0YNdCudvl_Ilm1hh?~*m?O3Fl@&MU2}=?TTl}xni#2RPGZs(^qS@7^9Z)qa}CmNaJ?_6%=H)0Iuye2)SLR?Ov5<3pvJ#pJgOOX&9lpMn*jTi`gZfP^_f~av@<v`P)_=*`(#V9+)h9UG+o>UXkDXdTrAhY7Wrg}W&!{+s`X77(#QbI_-?s~SsPd9fxR4)HQh*;S9Uo!1ujL^3qkOh;uU+5Rs@n+Gu3EOrwNonLkJm(bGKt=!Ell<T2%x^+^5t%mw?N4A8^)|rz%pnAMiidZKjHdd{Hh4Vww_j)2}B$`vS345;VHz5Tmc}15(uItjs=$uWBYfIH@QNjc=JLFvEdP_~zhCj|=UW&#msu6?l8c*ftchAZty}%2jzsz>M<+u;&22KN}>*_CPvsf$v)Ngm*=_cpy5?EH7wO7`XPSO@hxtkS*6jE$vu`%9B4l;VBDS!}V)SKB(~c@mNif6crarQl*RYmhD9&W?r%nGEcN^7e#Wpu&;vZ384c0%lPd5s*`0vC!f{OQsgVK7g<i)aPwj2*lE&xDpLi>pFno6XQOR%>jqUEA&!2=;8Hc}WU(cYi;!5D1vAu5b<v7pm`Zpt1)#zZ$)k!kCq$HOX_cvl#I40VaJC0C*7=x9s-`v8lL1&SM1%@85}oqq(8ENebd3Pm@L+%kNd!(;?VSa<vGpTRW3KiwDM$pL2X5Dp8)nNW_z7h}&DKTA1JdA-7$Q!i^z48wu^7dIDt*AYQ!&DpI>a!5FNm&StFJYmv$hAL`dNY(WPRp&hX5Wz4rw=H?s2*_5rf74FbsB-jl~?sf;5|WuZ~K%nb;mo{PO!y=&lBI=@xl(c!&`E$U}-j7}8M$9e3|Nt)}kRSot>XTkYXwg~m-38?Lc+pC0b%Uj-Mk`HSm*W=cwJO{VK3_6$&>h!jbvarL2&Q*%_<AzfZi)iM?f%Aivv*AL&(jf{rlMMTvQJj)f2tO4OJQ9lHCqY`v+B4^&gv-YTuPJQ^~X!mbfmo;Nj+ly{nwa}T;y|RwJQdLswK*20bVzxY@{BByd_ImI^iF;FUVDj!@s$+Nz;cM!;gp!9{N8P0ayaVuu6Dt!)R>5;dhFLr^a^|)BK<di4g=S7bi36$a-kBUWYr}MB@J<W%MwC$nCB`T5cM@U;K1>}H_Nl@?cJA5G<0{K0pN_Oz(pWVmk05o&=B`&uGZ<i{*&>g}Q=aP=p2m=NALyi*is&k9$#&-h$)SvO9cP+*C2AzkPz%228+1G{yfDi9X0y{RS&lL_2Kl06V?T<AACWS&D8@{o@2Ht0;^Zc1td{)%quduwo@o9~foqn23sVj?S-w`C1hs1y8Rkstoou7myZfL+{6r$|qO~{m7KL0$$LV68=xsk&yTU|6dElLgkYGcat;~s_`6VQc;b1w)EUb}3nFt2RlAAx71am0GD2xL>jI+J<z-0#7r-PGqJy7)cC4475N8FTF7R<zMjv#1D;(y3S1c>h4SuDP<-?^W)&<}3S1AuH+D5)4^#f07d0!F<OD%2=`aM7J}!;MvM3M^xZ&+jAcDwT&)gV}7Bkiy=Y>H8$Dn2d}`3k0?~)PhckXKwAK9q7ItI0)*VV`LGmj5&GW+!8`lt_Lt^x#duAN>nLJ25(lG=!?57p*RgVnnBfVHNdr6D)2d2OZ!|xT*ng73WRpN=+xPLm)@3;VH1*YHLYBY@crY8$jnUhtt@ftMi1>q2fGj1!xG0J?9y6B@YTMRdfY?z(W;oVxf)hdW;`t1s?dG4X-VmJ1c>z#>(_A-%26{cQ;bcGJ4-U{6;1okHNF*;T05P_<wtgSDl}hL7pP;rB-0ig{7ID#$~qb_X3#^hhBk0YP@n}ruMg|zJ=%A&GMEvagh}p#3uYuyi9b;IN2XgkNwf1R&_+W>sMS~lEQ><nnB0k=Sh-$qQ2K6)CQu-@Kmn^npx~GW*X4_8h<RG*LP~qcHk`(RlmO#87JQAlo&Zh-7{K{fy318#ubFBm30&)P#Nk{<9IR92<=22imky0fl9tP++_L{dkUjV3<wCSh2%}<PiMrSFG0XrpH@Z`cMaW-Tn{lm&B8Sbfr+@tY4=L@z;jcuPsZ%3ETum9_gKEuX?s^~rE;W*}YmQcgRCap?Zmw?p=JH6uQOaOCxiKdf&#dD@kRT$)&at=I`>FPT4umb#!^`?mmQ5?bq`Quu4$b=CWxA)VLk+b^k1;S;g>DXYPs!@TIst&vqdZBvd?jYVU?SY7%*Efl*&=2&ZJRQeUkU<6R^)jBIb@6Gc;_vU4td+E;S3-}hCnET(r}MwiS(nQA0WDr&}54LiwkWqWJbQG_G4SJ5FssNFRx|Cx7QS-(%BKkUpkPeA0{+|2&z#h6OVt%4Y<7O(>t#H^HdzUY*)GDQ@~h9lk_#)agL)xcbopTApMxDB^}>|1M~Rk)<lWWrA^y9u8@KIruN{*r=oGsdOJI4@MAyGe$q^ZL7Q%OUd@Wrh6q*(4Mgi$hzRe~6OSrv!n)^R;zQ?Z$8LF!$AO+7A3ib20N424-+F+u1nx@igb|!XaeXB_+^3tdhRzh1S;KukqDQ4t{*wgyM2;V#!?sr}$I&mPD<gc9vBOD(Qxplz9G94KfJV_%1`*-K%59XQKpUCF^>L?87azK7pD$SX&V153x8?(5n&6{4WuOXY)^N)oJ<**=Fxn|Ki8P%;{J_y_)O@W<sKM!dAdIaRB55U8<Qb%FaRon=-~$R8Mv%OSGTWJgCP<1FAVG(SPRuT^Jf2obu7z#&AtnGleKT5#LEMkk?-I#|JQcxPeEUtoU$13s@zko4JpY2wUn(T_=os5!CD*#rz&nb|3eLnp2X^U$2&qZhGL19bO5}8oyjdaDs_*Dnzx|4_LKC`f%>&mi^Ya{?0DUt((j~M*!#=9ID22zUHrNZ*#w6R4WeYt0k|$ntQrFN$p<7<Cl&M+?5^iUK`FPfqx#V$gj~pUtG8C$kCx?yUcql>|gotCQt}l7(7qe1OZZg1IwQU4tm)V32-<i=7Uxz;4p+TT!4^grg;y+W|!B<~y(GP!eA^-u8JII~d-u>2Td?&e%QHZU&Y#}MDGQgHbS1I6T?$GrMOat-Hupk3}1`uQIC8xYkMkb<aMI<}sEERNWUEdYvfDO2j(|s&OWy!)4+%~^8+5mM&`i`ZONLd&73rKz&rvbdXBr@?tC?nTF1yJmPT#*%ik(aAU=7-O9^B&A1ADGc0<791kL{%{F_{vOnZ$Vm7$fsx2Kq?3Qb_``OjYM;BX9<*6NiZzW{dQfbVTnw{NoGST1VHj?n7fbR0zd{1a)ilgHy&RBxJ)$yY2P1N&HMiWRK>&3'
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
