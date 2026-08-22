"""Kaggriculture agent — Route candidate ep=90621013 P0 score=145,251
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
    'c-rk<O>bM-4gD`(YZ1wclXT}vG!tVyabP<YrhzdSpi>kmri*EJMgM!9SeBk1$-_hP-Y413DvB)W@$!E0<M8nFe@_1P>mR@W_Q%PeKA(I%zqvWNo1Ogq*MI)?U-xg^zx@5zKmPICzwcjvK6!s}y}JJ^_u{)xKmT(6;o_(B%ahs3+pG1-Y$4vhdB0kH9Q@&CwR(5|_WJ$m{Ptw_YV`I`tIMkoC$stX;~%fD-hFy|yZgq=ySx9+_QrGZ_Qy{jcTbuR#`gJSy}G&mD(i=<>)ZEVUv1wSz1Ua8&Fb=U_td%h)a?g`Pu>1?sFaJ#cfZ^#|Mt^Hdz>7q5`;LLpU_0usl|R|P6yzjo3EVqANly#2h!}OT$%jwTf=9M=lb&e?P{yZy+_EgX%7{zz{9>D?vH)tZp8SqroQ~v{r^AQZugA-PUOjN&&LWJ$#So%^V`++=+)yxcb^)Gfiychi?%`xC10K27*7xV^6m$vnzoPFzPP#i<fuzNL0RZqiMK!8R$b#Y(Ohd{2}t>sXFj~hP5e$?G-DN|$>V2m7?iZNSvAZw&xW5)=nE}2xjEY?ZhR1S&>*qi<U8OR$*eo1zRbC>d1oN!?j7q<xd$l9+Wu+u$m9ri@`@jRcoFzr^ig15fv-KTLgus9MH{#w(MPW?FIR7GfBAlOeS2|v@t3b!YdwT1<QW@z;G>V{**DS4qDQvMw~s=PcH_hhreL<T-PwS@x%t2n`kRrR9{RTJC)8|y_-)oH!|Og~BlJ>JL<Xs*2A*q6B}rGDw~55r7kjj=;hlZ!%AhD1iO@>LJ15B#P*HF|M~aFAo@VzoEZvV*3LY$hgxNWEpOaqR)K4y$+L5a(aWBP=*#?(T=IZIO4s*A0;q1$wcwMfN^zjzFH@xS#M_J+k>v;EuH0B@V_D!2onR_%%y2irp|8x3E*5w$zD7hL;K4qMJi`&|>US3M<hY82U`N3{x`mC83Xh&BIcajlee}8`c=lGp9Hu2S{{YI2@oJ27rgE~Rh`|h{LiHywMX9SW<(<YbIcCykFr^V~tP<vqpwKJ;Z-)aNk-8ty<YOAea*$gLZ_k(-y#^+DY70599mPzW6D<yiiPLj;MGAo+OQJ70RnO%8&q0DIU7p=ri)dbmGYKxa&mw{)NNDE=!-^;A{4C!<4Xnf46ee8D^KXfwx=^fU{*Q~_Nhy&3wbvj1LLOOd8Fs3q1jvN%Jg-gY1?>YO8Q@NT?Er(U|1gG%&BHo96>>o6R1+3-cNMQw1B*h%o&Y(+W(5MtxCcX*WkG7%VvKQ?yW5Q()&rl2Ztko2Cv=7Eu&SWa9hFxou%UWMu-TyOxf&7s#O1rlv-xbOaHeSrl?e+QkyVdpe&-c%KV`4lOcNv#WF=$3!7h6Y>xTBQ{0~t1yuC;tYpDYU^SUi^5kV|4$rCb4gK5s_oaY_Zi9C*5Kf8e19pWe`4Gmzt)h93RB!4^xKi~{tlJ((-Dh}=l_x>2eS!YWWEG&PUFZc}36I8u%-l3oi-lL(Xq8A?qrH)*ths+OIs63IV$axM<4Ipyc$GZ5-2n73eOHIy~7ZjtcxH9##n`U=cmM*~hNGSCitGk=&g&sDM188y`8?gHcOQvOWIDY}Ac^XUo^aIB5}ru`Ki`hg-fX*EGzx7d35fE=j)={9@F(~*TXFkM(fDO#=pm=f>r=xeQHQ%ZT%DLW7p20ME5fG;O~65z2c6Xn8M;_U2>M`-W+a`SANvVEM%qB>b#m91Bn7qm2JNb{VXQTMjhue~DT2tg3=`B(8ohN<SUWv!IaC+sP)IHY|H&<kCyrR@u3m-`9F%{mMiMk)fN7U$RMOjm5Vw4Al!y5P+`VtqJs!z_+<1e)YluFNQ~5_-bsJ8H~V+rtrafN(FJW5QLC6dyv(cn}l?J={Bh=u%&}6@*1=mMh29f=^-or`248f|SfvL2F@CU_n+C(&Tq3`|hWU%O4+Udq%7=uZ&RtS=bDW#mnb@WZGn|h*^GyX*xzy&Di@<-dEC8)Xmiz&kZ^cs8h`rq!<r|@mSJstw+Lkc8PJ}G9by;(O}ouHM0s+;p5FE1d;O*^I2|~J@e??OfuQ<^^7K{mCP@loDr&A1Bg>e38L<vTe9+Lt2?_cN*3UD+=`E(Q77>pmK^u)S^VUiG9-rylEYN_5I;z;Y<rmU5;d+nayj!J6>fudON1S>U?zE*Z6Ed(+dHe`rnWz4tXBD4g^;Pu+)8V8;Qq^?WeFz3+sd`@Xz)pSJAJYT0i4fk=?|P%&3@MYUjV$!oMQwHQB@|1P!o)&KJVrt=PNLSO%!+reTRe;sJ@N#9c<J~j}SF$7gB-cdY%}mNUb%D6p=P?ymaO0(lE5B)HjobuvCN;Nb3}r^@8ajh{BrDGD9F-2!YU^)CxE>94TtS-&1zd8gHJ!HcD#~fM`^!886E4=4rYPz_o(1M8VUbk@(sQ(U+~V{jeitkr?MBU)*JK1De87WWkqk!Rr>Lbu`_*yT1C!!J_pL_s~#F>y-v+iPbIrE~NCfss`8v+mYDnd;3Dn4^s4E8Bz3U8<~;E`7n&=+BmJKdBCNSli4p)2&fdsB|-vjR|Jr+jZW2E9+Sa~I>`mSw)Na8=>i($@_))?J>&$>z%FKrd|2<lg$@g?P+0Vu5d|0)DlJYMK-gfsL;0g$fHQL-x<-JRFsxHpxnWzA@tX_tld)l1a8&?MDS(b$l-^Q%b78)z3=xN0WVQp~WQveL*-8Lct~fXyD)4_u$f1~APy+|xk_;wavw|bj#{nI;Q>rwDh|iyg5NCnoZR1WpG}2B6v5<IJ?a&4*DDjjs`$-k|1eTr|J0fOi*=Y9}Z&O`N>_`!_8iT8t2O*<)Na(P^(J>U`rJxE$ypIh40%fZheZ$`AN*=pFk4@}FFl}&>yt<$4YE&Y-^v+%M-MLB@Jh(1r98Y7Z@*0KCl;k<6$3Z}pz~w&*e8l#q8dMGC%2!jZ)6DR+ep92{A&CqKuecJzSB@hhHGQZk1;5CJt`U6go%^Xkh_Zn)C3n3>m)ucucuuOI35I0ceX=I8x4ul(<fN}{53gRc!|IxBi-gKRn{I@5(Y8{!%nqO^0kdHwCS4oK1lE;<R+GU78?<4V18%KtqnDsG5gXbT!2<_mBs*<o+&V&ri%IkOB@dabqkyRLf&3D)3kD)VmRy8Hts9^~9TUbiSSU<jeU;dIg~D*fV=-8;cFJCbc6{tgn@UOhSOR42wen9#6|lE$si~Y2DD&XrJerfMcvbvcD(D!9cH7Zi7&J>XAJFuvok__eWmGHcO<*7@m1JwN;<UoTRrB^GR!hRx&lD%;p4i%B`@bqLkZ6Npv9X3CdG!pC2Z!-|VpV0R4XEZGE$;$kVY`3=6ckl_5=?A0@=>WSJC6t(DrGA52*MZ2r$hIylY~h#%+f?LVMh>hXa*JD9Qv7Y5HUMlW4c3P&Bp-|Eb75NVQRa;Huey84_oukYkR_70I4Sd4xo?_B)gJSg=eQFpV~#2QtQPZn~EI$QE1h(XG~tbW_wjV4IHMx(vKAAR22#nv`OV}CcVTxN->gg?h)V<^qX^;=(EdJn>;&y2zeY<1k5Ag!`hi985Wn@+4F$cZM)6Mlo75`bSn+2^032KJMj4)b$d^J<#QlR?`$j8B7yph>B1RP1PJz=f2ES>>@e&DljIzmxz9{?v8jU`$|)9lV?=!7t~te)#(seHwof+EGvtkIqV0iC>zfA9-VsA9;(E%IBiB>BS;jiLx&ppgy7Opdq2W*o$a*#?jm_jIIf8<=*-6tnp5FP9$9)SxF2X&?iU>B1>6^aFym*gM{H#F%@`m3l<?~DAF-U3-;r7+O)X><A^CNZvVwN*DhnC>mgPv!e({y77>CP@>YEzV?Ki8yYGjykJ8Bk1~EfScKL?N)1iIUu6Mw5i^;k;6#B<7KT{NR$U>7OyDD6g|i`m9pkn|2Jbo6$UXDa~Zcacr;bR*RkJX3{@}8A0g<n|#C<d?S+J$kJ8Lf+jg&#z*x0BDlW8ujsTSf#Fb=U9hNiMbz7;TGc_=r;lLGR5RAtB_OdJ#Zb^D;Yg(!)fAMH+LQe9fnBap{mN_)du<`gY>?w>yVFs&O6Db%!c@R^R<II)!=nl6B`jlE)KZ!<$r0DdM?NlTN-4-`+a=iv%N^ADXdV0@eEDc{r^+`(r&9GVXZSDe>OdQ2YE^Mh4Y!0ZQ0kW7MO<yD$?~yefsy=AI9I$spPTRRuc~Ir-1a%<0R-O^odJg*TWWgEF^dm9Sa0g4%xNoI1PGX+eLGk#9HSRuU-D8rg#`CFyZ^z|Fxv`zhOa}$&364T6PI=0dzD?0M7mx(pWH1Ewvloilssa{04Xo=q1)VRsborfl|!i>ZOpC|syi}5L(@<NvKgcj6{z&smZu74CRGIKzC@%O6tCR?8#6n&K>CjIer5E;XyO6z;DL-M<6Kg0<W>^1Qd<x$B+oG>F@m*{u*w95F6e3T6Nl|x{pwl5D~=@$!@RIU{a$Eg(V>Q%qQNJw+Gyu_VBHN*aZDuLMn2nv)k#W*?*h0X(V03aFyW{M$cM4p79_Cm8u3wHc-|>j^=G+I1yDL4<mqCoL!5?CPoqF6)x~U0u>QoRB)&V~4vr_|?E}6i$#k7BkRzLdo8$<q<)e)W5`JOZGI^kU#Gv9d_zP7aH{1*^U@7EpYbQCqzU>1~-vwoj@-_Tqa87%rG@iq)HHU4O7#bo&AppOF(nF}9O{tH%OSJ}IE{gh@d$NqRlYs(TG!)fBWzu|86$E5aLC2^KCW;Y|L>9?_5LZVJur>&NQwmiPLd3uv<Gt_h_xXz&b9=q1AhLz>BzcP^&64+K@cvLWXGROggTz0cC{>>32{PQF+2}@=K)ft)Uv6<uygnoWEr_;Av5%RR9A}A3gXu?Eu3Wx)$SQ(m&XAfzhZ?2sIPg=hRx0bvko@bNmu`4FaxP+)<~`KJz70j69tW;uZ(WyxZ4JN_4kR1isl%t}s-4+(-2n*UV6HJ()}YU(zu6&KJ{u6uHc!h!b%@e0MCg{;w-JX~@o>446eGc237lyn0M8v}r!y6C@-i84Q#`s`+ZSGqgsLe!+5l3wZ*;W0;^4fD-Z+XAGP0uQUNRjQk2fKxV;pvG%QQ*sC#ye3@)w1u_4+Dk#1ApNPPyVam-{IB>W>9`5NKc@3d`qV2D%jmGG|f$v1Qo?leBCuvAlkC4^Emo(2_a4M-G#&X|Op^KgK6eHq*+4dr}qVG$_6u?m)O@D%i%0j^xmv+R$JYrQ~ns>rA+<gS(AlkbNq@AE`D;Hk780T;O=8B8+L=0w!=#jC_>UPfgOi0aPJX;z0VRZDuHeUI0}Q(5u8Kk^*A|g=WZZ8+;TfnRstrm_$6nJ}~ecSkf4she%{d!6U$6LL9h;wTfMiMXHf~fC)^w@nCpGiGu;nZ<MR93Q&xQ`Yn*KsG8De>`q4Q2YhB#x;rD<90>1{^V-#{x$<NUZ@^)y7;`q{6RZ7GBQcpy#U51f1&Q2GWmO)IG2EhMQ0A1!N6cS5Cl-#Qi_X{t6*fDEL^p(KI&{39_NA9RL}Py1vx^}GCq(^x_#>!Nk`iLTXeMzdLQ^I>6u?QWS1pqGAoacbh+i_9BZx4wz%XgqnMyKQ*$wkGk-~qJ?hDgy^y@;v!lzK`kZ7zP$Px#(tt){RZ_|UtJQoGi$DQ#IvydF+4Pt|aRv^QgS*^HlkMTkD&SdHvg~%I2e-uPU&SPV$$pcg71>hU>N`W{i{+J5zCWNUt;)FLHAWSjf4Q|C)2RTCY4pqm<=`puvafrLf#UpE!wh=rW8VYVVJ*)zLgo!wv3RKL}j5RUjQOcsVAU>M!w`L%MINPKUgd~7fBz6z^BC(ap%%i@vaB=M8Y_Be_K78e`AaHFfsw;ppGvvZ#!tbs_l4U&yhmmQjuIwhZAr>N>+OAc=F}&`k*%Vo+GI$Bo)l8UBTDx@3n`DDl;(;zz4Za?=$>NWaQ25TnLsG#~c>jcsi`RE4uAGN&D>Y>jgsCy=ynF^2w&R1YxjgtSn1~ZSi_|nHA#?@3X1V!1f~~czL6!}!)diKgegd6BAq-EwsSi#pjH3%`{2Rujnqk*GyF9lEuurLPH$PjSDV;+*g98KQw7<AZb|A~`1cX4-)m?zrHHyZ?avf|<PnK6E05GFE-IO7X46uxEj*E!2aWNj)%Q0QkeRKK6E@e~TQn-f`10F+OvES~>c}qR~b9m~thzsEIFSy%4Tm>*kNF)C=qD`AB$tl`X-qIsvIh=}erL)JJSAfW@>ICSAu8WkOJjw(i*Ru(ki&2)G1X5K*Qm|3meU$}JtuqnWjK}~=7A2kW4Ks>QntUu%m-sLZe(Btz60dLy@Ae+FG{9d=8O>NeITD;FN|a+G!;p<1goFjqU5lRJE}}cH`m1uWTEzv8$^zFuk4bPW1haB2(86#tU<4Nx9pc14JijT;3JM|`Og5-6_;{oyFxF_OiLG3mwrWow1?*ylLyF4sjqs2}>h(zK7LL+f8v$6J5Gc^Uh%d$t<3Uu|6<P{>B{pM%ZpLnQO!rS&wQMz&sRDG*Ag(F9LnqUyBNb%8aRc*Y7z9!Tn3a*a_D&XV!H@otr)F{O`GZqXDhzqNjLVS)hF#Ye8VpYajSvVt%!XQgnKDml1!f4Xl~7I&nbKw%DklRXTZT>LliktcU;Vl(VlfWf&jT1H@rGJp**)xl7NNlcwgv<fgI3isw2=xlwW{>;n`}JJGD8X|6jAnX;zjmJ>(=qhr0E)lu)bA(PSz8QYGMgqkX4#z9RhhMLZksfa>MD;ISiKk!;-P1>?Y>$7NjY}d$m!*9mMv);uk-J>P~BLmu~S#hm8n<kUX~(f{~6a`1m-R`sHq+Pqc5f2bC4NHBl6}#@2lt+~dCrI%M+~*H_CFmNMCaH9u8MDJjxW;~GRAt>!FY5415}mbm{LhM{m6Rmu3{0VM)W5FHLew2Cpaakh3V5dD&8;1=xQP-Z%jA@BGBkO*TK^6pfGmW;mG#`HU@g-)18Ge%#dD#bKRPr`g_%Y%sDt&vt9d`}Oh{>A?eIFL;CFBg#VItIxmlIF?*LczEohZ-N!1oHz#Rj(2xzkjf_N89R5ug-nP7B)Z>n*^DSj~#JulIw52;H!C=V1pN|mJE)dc^fLLwEv_g&o#!bwj(!N**TG1CANzU9Y1d#5|*pou!UAWWFjKn898ec-g1JQipa`aa((g;!}PlH*X-#xmboJX8b;aQY>v9QM{qy|Bj0rF>PNBiyCXPc<3DNy2xDLq9UQtlV3Znz8rm^;5L~l7U6`AwHtc@A2GQt%K}7L+0bI_MjS3yoD6&5{#I*J7YN**tF!ZA*5Y#{qA^t>d4ik;&QQeaNw_Jf+;@nWTo6GTn8NM@Z;#Rd@q>30Q(SfU-1Kp!Ja2c6y%R>|))4LZWju2KU+gPcgMTo0dg`axBrN$u5pTQ6uj~(L7ShSq<Xj8i%m5HME2$0@Q-Q?WxL6GIqIm@v4ss0FL7C|Xa3VEcNLlFi%s<>MTz|uW*z1(|pdJNy0u+yDwW4n)Y{<5Sf5A~B1B*LTk54jg?a}QR!%2*6@SVoqiXA{BLwvp?Ibe_a~jupV1vSVr;DwQ&2RA@~W_`^;xaolNbh*U}TC|s$J({ORa@w>%br_)rl_ewzzE{`aZ_q2G=5GTjVtGo0<Zp*ta{X02`Jn&{F>)S~>y@~K&zFQ|<-Nxzf2)lH$1*UPWSNn4E+-9)z!;!b+^uVtf>|oa}oNA7l<ob@;kyG^AG@~z0u%{AI3+)0VppVgXkroOdue{8CAhzpgw80j-tApvlXE4pc6`xQ$4M56OB%;70v#1$?A@>A%R+wuiB%1=w3b(mLZ$(jf>DHDJ)>s7nz%bBEiK%v1q00hl9q{e(5TsDESr4)opa^h?E&`-6(xp-`CDaRUkCjA=hBuU04n)b4NSW6}YtodM$nURo%}nbJ2_#OpmR%|5XOLliFXpN6tj`zU0uC*^P|h(68N$%mSRxav(4TBf%Re}rXpuIV-3t{N;sYPyG<_3E+}f!kaIHxs!}tW@NXOsdF-Hl7hkv+UjhN)gDdTBM&+ay3WcDi7d*r5V)?Sgyl?RtnjEiMz5_c}{M3&K5Lv2%rtNA}krvkP(f>^aSyFb+fF~~`U>=WM)f%ISj_!XkBV^EOHlHw2Bb>=7_!N;}6Us|U<CTbQ0kfv&@s4jEL{MKE5SWoO<?x9$g#3mvtj}RKMTlYJ!@lx23j@61L^p1MorCZo&)m+@&m109v0t9l4q6)JR{ZT^66ra1h4U>FYOhn+|)Kk^4&8FL(q?oq}rd~YH&UjA=Ji??>vXxwmWuJa}D7Od31D*TkEKPx2CG55fX`C_xDfi)nEDNOI;MFm=>0?Jsb8qDcsVD5?hZ)i_E0=ihh+6!)Zkk6l?(?Pa%-U_b05XOus=(9FvDOt(eVPU~DCdgOGfmh+5H=@wS@Pqsmq49V3W7#@B6x{Xr%a?gibm@AjX#arA*PCmI6XLQhumly)v}i)XnClhW|!1a!qvKfI0iHd8=N6d6s*$CQ>mZWL5&z|J`P_c(MD%<Nx+hzt`m_am-TG!TQM4^luaNt<|a~XmmJ&*gkb~WZ`@ykHQktv9X*3ibNDii9&6=KlXVOSOYx&gdYHQoG&KeXigWP^3aT~4oipuV0ge%ZI%1V%VYbMoU`G^Zg|T#mBSU|4Vis<kTb_<IUs<ENGdZnZwj|c))2}yE+D)FmG-mwl2@ytFoi&e?hdxn*(-NNLvmUwHeRJ2P#bZ*$L$qv!)H27^gwZ3XKmIm~!0@QmG$wUtP!5Dji#m2Qw87Y2YMlsnH81+NPQ*;w^$27lL)myvG9IqjH#s1PTxW>TJ4&7#$de$Z6OtWBi87duc~X)vsErMH_z_RKevhWOV!7j8%UOwi*>tu0b>h%iXP%9^s@X*oRC5rM3$`i_!B^pQz0U|jHSP+KVNBe2?0CQ&Pvg;S53)x$&n)y=J|RDk6oH9Z6BMotjw5uUV_E>mtn4L<o4bw4;=5-~91vIQU}G&KPDwYIved?Q#DJp++DseSr0?gW6a9o8&(oF@%2`1kE}8V1#CtI(z~!dJ6X%J}c$tC8qi6;ATzI-x&pQ~YoLq(4hO*;5Vh>1K7!rqZ!*KBoXro+fhfZ7uAof`4Ap@&xkb_$h1J+a^IiP`&5JV<2FkPo2h?4%cze#faZ46DKj2{wzLe45?1VCJgrany#K;{g$?}Ri<i!W>SP5sYb2MltwAmK>NHH8QhUp0~pEoeC-sD0dnTwiE;@BRmC(<B@'
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
