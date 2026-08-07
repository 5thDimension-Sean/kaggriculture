"""Kaggriculture agent — Route candidate ep=90686756 P0 score=148,678
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
    'c-rk<%WfOl5&ajfxiBeO<7B7U%vgxVG9)=fG7ts>WP$)evY2ES<lm#nRI}N)>eQ*nZBl|)Zc`GwZrxWsPM!MkKWBga`PYB^^6S}ee?0qqd3SgAusHkM&;R_(zaBq$eEi4HzyAG~e?LC|c=qw?cJugC?%{V|{`Ax3r>h?>ug?}|?{Btei&gXS-N()5^XLb6o6U#EkGCH;m-lCj?<ODru(`hZbhcOyzyA65=EIlw_xrzi`|$AJ#ld*4-v8mt=lz?Oqp|&Xw%y#_Kgs&(=Jx*M)6?+L<l#^ecbn_${acsnTZdm5zjgTOSSeT6AAWjN{{5Go_Bc62B{bsfzCsdVuNM84F&%)H?*8Pw|H!A`K9XiX<-+7oKN`P#I@i~i?>B=c4_?uZO?qkb1YY+0@%}he?oN#Vuc`lk*W>>`-4A<4{>1a<_m@)zPGosh)#d%>cJlQ6(*18u#6X&zoJE5WW63v{cgovc-@O0AR!zezhKIYGFNV6>HwX)Tka+mwT6Im=M7h?QCD6(*yz}crY~uIwq8ZC5tv!B5he1kPyH&$X^J4tl0ezvx)^5%k#Z3>w4jLrZTl)#PMk4DDsV{Oa>^>REx&K6aRqO?VvW6c`UKt$0Uf$-5zdks=7yT+QufU%@uR`W`wTsqqL!w{3xxU`KzyIm?o7?-V>#ILMX{~w)bI3C_^1!b?pJ(4hPmAu^D&Kw;dbB$yW;6whweHS3{LS4jtf9Z@+3Bvo*8PN>%@6;Yb;|I%_t^-&)Z~$&Ra1fITB)Sg73XcD=IrymTG#O2zBOeK6pTcuQt{qNvIG<q?9h>*Vuz>MeGRwnN0ov{OCVr&PTl9AmpAvD6Q;K3>I&RTzGJrF5{g_sJ=S6DHcp&<@e{AhRT4hlocD(H9`h&*9AF*qUYEw~gIvF9Ln<?mrdijR+x>q{e-d>$CJ!lBgUP2%vu}P|d(q2F@qIDjxENp9%}igEd4YO#HE|~?A@+}#w}15CSyK~VjN0!+3CBqUGt#LOWWDdddz#3I+<i(QIW=wVvKl5UJaJOI-VC)TW>7k#QvR(p0N$O0KCiUe5|+()vi4ti@Tq_P+PMN5M%yw89dfBe&)_7rxmRXIQ#lHCX$P|_&kw?kCcjZj++<CV-KDmA`?L%!v!t~Umi@iVjL#50_fE#goZH9#aP@sB^Pk>fMZRVxZblr4nyJ$<O6JnpR{?!0ljMj&kt$p&R(r46Z=B23d}%qXlqWcc*XQv*^ke_1DJ)<upGFGHks?Xvu=WOBD1%0&z#{QY;C|GGhSOfOy^IN$**!xQ?pf6ob+iwrSk7Q7D~Da{l*@W{RBmn_|5?6yc0(Sm$q$M0gPj+1cYk}i{oUsF_D_%B{TmhIv3iKOY=S{E@w(VLiohK$R2Z~j!`8KKALx^1MFfkdGAnYm*wt1p2R@%SBjh-x0AO~!-L^mQ(4B8D^w$*RIH#d!e{ZzK!X{$_`jy_ym0EaiBz@foRS0es2ooBbM_{)Jv2YwIM;A%2g(XP@N`e%nhL>Aww1BFXy{s*gfAZ#798_}3FQ;c9)RQxB!Op5HYoy&G?&&K)EgAZ9%w9(WPAD>v4tq6!7&OmCvBViw)MV}g<>OTTOvovkf=csg3gK|9mHj6D6dn4GBDL0Pg1WBQdhvi9sQ&3Td&tvi3vFP!Fo#mqTmvvA*3Z$ORmmol@`zJ*Bq)sP=#A@{NpG(8N`TL@4ipSask4g*9;1zmwM$%~wy>@(v5M9#x0iHl)Q~1RJE!K2D_?y{)DeOq;4?7ejf~UHpajzqO(ROZTPqo07`oa_!vnI;?X=@=B|6L_5eJfs_Dj{K8@6b=owf1G;Eg?EeHe4YERL-Qpk&ssEGWnldc*E-#K^C-i#<jG;ba;Ig{h!cd<Zz>p->b6@!$xe3x45NXzW_GXxXP0d=B$pEoK}9ykx8vS_+;5J2In?lJE7Pjh5djXrqhK=RaIs|KXYF$7KxqqUK9GKCSXs_^dzGK%FA07VHh#-dL@{C>yOgz8iERQ0JO1NHQ)A<FcgfnvaO>EfeL+Wx$fvQDM{IRkI6o;pEjN1QGNe6T00n2L{rmnrzZx>=8{+E16$9F*8)S2oSfD5KP^_H)ZG3c6W4Lq-?-p+=7=OQ7G{~Ry*$fyZFghWe5%vB#EgqB7Try+4eBzTlBc>%Eb(PRKN|^EfIc<f|}aXY<Srd#&?m$PYqwEtk(9u0x?s~+_v`WC;-p~FH>+C-dfIuNu6(sTk5mD2)P934b<md*6?RNfR#;)X>)_RNGqqFz&cNIYEx~lVr~I5sz6Pr(@h9SflAs)H$exw^oU5aCLk3@&ZmZvip26lPu*yNk0mQdmWE+MrT#Kl`$~mFfwV?FSv4|epF2Rfge{|IhBY`5@1WhL4e(w#Ce(y;C+wvy-ad|v6xJp{&WI*5UY73dQ@Reo#e$MT&hwy1d})Qq%U0Na*lW_5i(`_n9wMm#N#Q7rU`x2-bqljNlI}j--hAe;(4vF~rdn99G%~AM-K~>_lwPZ909VkxhC$!MLo+`}(W|vb(dRWXBlq&_FuZHyJfr3jfksSbyE4I{QW%7A2{^0>AYYA6#nc^>u=9Gv3BA_3>6CO14N|_nG+AHMdKX|9GnGB8t6!nRME?^fWDQj(t<DQjYt!JyB)uvA*si=;7}#7TqD&aqA&8tgU@<b{8>WU+1(=is+8EsW(ol4$u^C-y^B4dF69fDm&_7MwO;pZ+hk(`{IfU7eg;EQHi6R(OBm=*fY+uhjBI83(zJr7ZJ&P73oJES)MxFFAw|PPq^A5`yC>S8Ua`jzl<#2pOK8|&%zTqfalR1)@7COuVbuMfkgzO5B5Qh<tnW5M(g;uD7{OHFIyA$c_UC3e2xho-D82SIjYf=dJ&c1hHv8!_>E;y3LAbe9g9hssVgfekl`;$P2PxgZYeR4eb65^Y=mSSX>#OWBz{?{)sgn}4O1(&q+aUm4-B9A%EsDbv2YhdBURf4U^ZJc&AMkb&_=G^jcMYa}{I@2-nWBb4=zU;7yvP^f2^n<I|GY|fmAI^hNFj^RF97zh7c`^ZW;Y5{W&|w5MbaB9N*3Iq|NM`9UhJod8B>f|jofp}sye(f`0RZUoOi{%Ae+h4+zJzVtE7n33tSAxuPk}Xv30W5{AQs}{SYIhB-pw6RYE$O!Z;k5JMmshprKaFfKb8RVdajDoPz7vMo9YlJM7;QTVNKzx;Kx#tLq|MY$LqteSD=%Cq)+Kg3f3B<l2>a2DekKj^@{T1)@T>=@hOT*!q$(}7{}gN?5e%y8i8?%Fb5|1uB@Ekln@2S@qB!xVW_94<Q}ab9L!&8-g`}#Z4$I<IVRCoU3&T+c1Mbo+Y!7iluw85T_c+kri-QdUfhl#nImwtNh^eOMjS*;HCN1CNUV83<blOC=qF5W7wE<wV&Gv5_jzs4xC<bUBuM5ba(ZNok*x6Sw8Ys@(WO+q_<d6mV=;2AdiIQot5@xnx)3Xx-Aq>Ukpi8nM8SbHsr=0(*QtAXLL$yR0&#-oaVD*Nbh%2Cr^gQ=8N-IaYdCyZJweun#oO&{dBEG+)^TkX3|AkT6$Dv%*x`%q^lXp1-c#S$L<aLa+d>tHqwZq9aK`Kb0--|a;y4rnv*aAh+-D}cSn43Va*ByY7apIuYfiD!*muy^_Q@t%hP;wZ)IIQdeN#K#s7DQoT+cS;$TbKr%UF9?m%}#;w-L=OG#n}cS<ix!SAvgX{LFC<L=uw(QL|<sJF|3>o6|07CIK4{stKFPwRY9o1>ZFI^P-~);vE}T$hk-L-}|S%3y^OkEm?8)nll;gj+m0FZ~FF9vv1#CG?QN<Brcz_l;w^}$4&F<)0JhoP5I)dh&C%ylb#eHu!4zl+GMVh1m@w4QBivGMBsaH$>#LW7*mu#*(EWSD$0$zeAs~~&q}sNGUXE1E4ym36YWO&Cnr7lJ7*UT|AH^#@bxTR;VdZ0?lP$_%MXI<+x--;x!szr!rdzv0D!!?M-QOW#->IJ5p&ECkP40>5U5EdQVB#cxg;d*TKad#E*I!|+dK|?Z6QW$kiDwi=_n7?W*mjuQov7^uo8g7BMEAyB7OPMR01-{>ek6wJ}qfd$;IRO_lGQXHLT{}9DE3s9sZ(eC@TKs0{^70!m}_3D~fxrxFvk)QMb%3Vpc=FkWVGQi{yX7S>VI@-2MIGswzv<)@P4L=`K}t2KGH~(s?`<A1AytrS_~H10yZ$5+G=VuWd%mGzKHWp5dNa;Z*@exFfJa%?z`#!0+%i#<(A@r&JyCvF)Ft%aO>&OXpJ{9q*vsi^dJ8oc-8s?zK=NMZ4LoKO4uRRtnX=7~!00%mCS|QHTm;nqaqAGG-MO1nIs+S~tjFl|iwV`UdAn-%;Lg8$D6lZUCgWBjd?9msFRxCcc(k5EYWgD32JyswB)(Iic%$ULeIB!5Bv|_^X0hoJu%`dC)@sR)}TQp-P-0uP3ftZ;N<f<&95sObcBjpYF-ZG$hb}#kN3=z=YQdWfZbF6lu{(1$}6rl`HMjAj*lsbuE6!)txZcnh5&ft?aip;aMZCKgTo`G?t)3J{+00TA^9Y4=97ij4&_9D+RYoq%<Sm^E|mxI7ThrU)=R<A_?L|Ucpx1h#!S+%lBmHEmxjW^Du7A4_(pP&WU3g_W^Q4wFDi4h>w0~nj0e0@!nA?Z&nca7ykZ<iQxz)C+a#wrM(1o3qrYeBm|U6uYrwFaR6MmQG?9o!?u8C9g2RTf|&L@Tt^4+^4fspmI_M4HuW_;0OrPm&@9GlZBO+oy6#CwKsOQu6?MrVjwV#Fyl^Z73s2-yYbnskyjPYNusmg~q<3wIW&Lv5^^RPnBDs|e%V;!85~UhX3*485oD;7Poj?U87b*5B^Os}PNop|t$jya2Sq^=9u+e?!&rv>*LsZolU}30A1l(~Vbyu9{X>!9mI<t{ASFK$s2aPi+Uz4mETIaC*U=yG{Kw4`JZ;HX%m`f8{0kI#pD{I#hsPk%XYsjMCwyU(<YG0SMD9*>od<afd!FGftBka=WDqEC1J-ta?z9&;LA_!aKZ<^t>tzK<ofVooqbAm6~2m;L&gDz5Vl+FeCf5zkC8V4dsNL9k$=Y~(*-cvvwl)BFEXxDkUY<=hR*VOC&$QT4i`*|0XGVVwtD5o<!-l?_MmdNOD&2CUpkx3^+bV#6Sa<U$Em@ElR2ZnhIc2*W|i%_8kR=y+fAWsrORBo{RBM^$fOa#Li!9fhLHE&`J63wl<?GcV3gSZ7eiF_Y1e6v}2;&PmdtDU0&xqXhMAD-KIULyU{z!pK8N5?HzyaRFohzW2v77lw;v&dofg1|D!FLRVa;PbYnO$Pi#{V>BjxSht)&w)K)#KNY#mp@|RHWBw5--|A`F(cOO3H)$!64@p!6Rgq+??%*^fG>1Lj3L6HtSy~7Uwk|iOcI^qLrFjt1hITg3XJ$pY!P?l%NUNaEq8L+=o#}XR&TT*3d5wieoax8lZ&&6929T!R2;xw*I&tjBbMh5HgB?oL^$g8QQNmcdADsu4ko9$wb&TPHtCbQb#G;vV&r!{20&v(46hgFPf?5o4bMa3!MEs6lzbGm7r+56vbW=5RgkKvlo_M%!$=DQQsVHet64}kLm3B5rD#%+v`&f(wpTor61DccnA>EWela^L&8R@`-+aQ6vTXeD2T@8oBEXbX`<Q;*cqDs>IygO4ltb|bFoQ;h1&%c+Noj$ta$*K8i2@&snZ-+I93z`yPbr9+v5zSgc$FtR5O)@FbVUj=9QZ^Wn2~<UPatkM>0qz`bS7<>e&XZ0xF}3)jbqz;wklmnI1Em!QIOoho`;pe*zZ2HP>NnS7&+n`rvmmXNc}3Ax?*#E^GOPtaD!rt*?p@R7i)s=icsMbAT}M<R<<}9>Ke}p+eVKh<f_XX;^=EAjiA_SEC4Aj$yo7|6v5P+uGSzbEo+s+;ROeWj)@Q%&es!VJ!T+22(ID~>gz$KogN^~WV^Q_nd^rxorz$g9thnDmPS<FGx^S%z$9B3Q>VhyE|0;6zPPG9pulKrA`7Jjjn7W8zq;;3z&fF6V&>^oM3IcdG=Ea9ibz(a=>iP4@21ioO#3sVpeEW($zi%v2)#5KkwNR346@BSx9UfQ)Mc}Av)DGX$VM|^&0va!y$PV*9Brt~5Uv<h%xV*|u#j|p`ql5!RU3@TvJc@}G#nrP>KU91;EKSc#{t(Wp9e!b8?2Os4R9Dw6mgeqS@@r+cvw^^!4rTFiiXVh5fO><EMpD0e@LnnzcMrslW?h2rJ{E4l|Z=WKyC?KGUGGkIokP7!FR3G{4#|Bh}VbRLU}`1Zy{$#rMGjk{4$M{I2th(&*ex%_3y2OhM>ABr`T<Y<GjcWY0myjaDZf`m<y;ecSk0Fmt3k~@RZsz;c<aDm*7K0VlNSrUPwy8&WbO^cYNY&ivqz-xtthf2L@~y#*Fu|vEWrjah709Co-I6G5h5D522!~7);rS9Ki5cCKMx_0Vt3Qt5BUFiGp>u3VOf3$OFlOYn?W!C5L;9+0;F%R7}rp#|lG0P}l`rjN`R`nniZFR-L20y=T{RfMv|<R<x{Iw3zciz~KnKF;aS!3E`_Cj)p3P^cY34)h3KFizxv^>~~DLgbpt!Vy=P=<Ympbz%K=sM>U`GIB@i>Zt@6lAga3~cp!@&FM2l4VtVa_hf~-}%PTNfL^yAEEp80*7oSMaEk3jR;p%%LY8C^K%ovcc>tayZh?O&gh@O*(Q|zCfCsej+HSI`$l|pG%H}O&oV*s*fRr36A`&Z9DG412ltPeHzLNOOLCrQ*Cq6)>-bhgc>Fiw-kDsHDM5Qk=Pz;IHwvS7ESP;+N*Q)@8~s03IH&#q=n+{@G+t{u$&5;g-HV?rj%V3M|upTwm<+WIQCN7{OzENyt;4-=kz>YdGA41l7zV$=$~VXLh20P2{@Xs5|hCv4+*(b=TZmBpgP*u1uZ?YP1dwjwjd7VmWZx&!26(tgLKbxcLBiz?7xlmrF{R6d+3ElO>AluZ96`xGwMa@TG0?rZg6gz+5B%>+bQTjs}{D-ObiVp=pn(ACZ{MR*VG8gUT9q+djkqHUOxM1!E&(`nzPz(ViQ0(D0%EvkI5{j>S-d*^EfnfDtxrdSz}D{TPqLh0;LZjK>h7cpx~N7S%qBRSttF#X&5s6FSX0XWFsj@^xp8wOYY#GBRgH>%rm#vKMnHBZNEV~43AY*zyG_MN@W9c~`rbN3uLg0AJjEKZAVO_<;z>s=5`mjQ!v)~O#DD>uU(^|)A<o24oSCo`gUFyTV>@5UiISNA)h^H%v_gQJWh2o;Ap-KcH>*7bsD->EKdEQlmhJ_tgDR>)1T=cwIK#5@MkV(x=f*b^iV<Tg+OExt`lz))>G97IeZZ3_|$SrSRxAgF{-QVPmvulY9DC5^=j21!-V?XiSR3k7lPC!}lRHT&$79>F1-Eju_fK>@JZ&CU+@z}=#8@>>zAr_Dtalk(^iK}=kLOx4N?$cHTFmJhmS1x*obO+1v;s@zKG+G<IJpPs`hZ(lcp?Z|jFin@UgXLO^nqB2l008moQ8EUdf77JRXE{R@pW}ihChGn<md<kt9A?5=#ns#?f3ierKJtJIb8i>>#yW66d`8_@}$;OLYrtSvrdqTwijTHesjz`^$S<{-uQV}^_{|PIrQE^?oi6R_9kY9{1gmeKBT=M{1q7$`F2ulqD3_Sh=cvMsphb&u{b?vg<k#b9Vg)$Fz)*IFIr7J06JXP4NgA2^#)|PKvT@zuH$tonrb@mC^j{p_`$R%tN2+kd<L#dIL*>QkJ3-!eFk-1XR(jGI{zE8i~^Ndg_LMpxDf&-Vlb9l)~E-l<Sw2WXYCY)Ws;}_75i>!hT5qH_=H`!3hDbZ>jCop0mYit<KTTHVBS&~JpPFYt&0;xlTa2P#Qbu_d}JvIy<0jh_KV{yoShBkI}zA=<^E;L$`Y+M{ykTo;RcID;tGC|=R%1Q3RZ^cu00kpW20gA1D>eVAqw=b!Vh|d00716R#gFrs!!MZ0Uz%{`~#3w_5+$z@ea?4Yu_|k0piDC60$a8b?eOZ~AvW|-=krhp9m8gjbfTs|j4TwNFkCDhCV_;N16y7G*w=C4~R1hCADsyet?4B-BXb#4=SZoaQpEsk}U^J8u+tCmtR4(rtGJovLLYwG-<JQe?I3%>B4w^bDyxk&U4BY4%z)=KoyKoa3=pBSUaZx_C(U_Q!ogOMfKL(l8Q!r=s=5^O%ok~%b7BQDIrQo+!`+LHQe%`0w8^s-t+qE)7nx_{WtQ~cZrl?gGt_{IB4NhXnXYz8I$&sqC^5T%jqeHVfwq^`5Ht2jEd?V92TF(WTi*Zhp!18o#PzT&TyRkYF-9xK3ci%cII6;-xQ3W6rklDf6A=<fm9Rd@3V5Z!Ea0qw~Pr)ND$b|6Fih~5QY16?K!OLJzN*B~mw3!dnavmo;2yu~NK@L!yzA^bsvH&b%3_12ZW)22`>7uO^epCZ0ND2&~p^!Z=Y+xN=!5Oc?6>NmX_jGHox0bzVC?BHYYkPeObw|&33hYm8G^}e<+Y>eL86fiz61m1uywRrPM9Zl$#r;PSCZc2>Slh&ahM@?d4OwcpsI!qD(@2q`)SmJh%9MkAn=$cH+Q-PI_&dZHk2HZmoFpXc!e+&Ual%ZESgU?S=0tYA)KE?<`{YEyQfe8+9)z)WfPZOKnBNKQ5|=M16sX-7r(P20DuC<P*boM=xY|4!QrM-3At!AgG*+Tfp}V6WpW>dg9U&XWij1RMi$T(hFM${I>LJLxeS#a=y;~q?qoBuOGoh_KMH!OR6G;rfW6WI!lMC`p+vY-`Du>@rMv+A%4I=gOqLVlVbCjnH07MZ`i6PssG)G+$EfI7@cp26cm()BgqA9Yl9q(=C@IzH3$RUGap(=C%(J8Jg$lw%!4&P+>CWGnps-;Z_-mQU#d3h`_j$Vy`4Qx};YYSaevZ;W><UOV6qyjNOTc-s_o)}e)3vqoCLXi@{1by>_B+%1zV87Ld7bYmfBZ0Uo%&tO4iZIA!xk=56?luQlBep;%xEyLr=0F3Kr2Mp)evqfNXd_3<U_hN82Gfw;X-e$&8A=sE3J^nPl&l9mNF7%JDm4H%rlYLj)ZWgOS=78;ICERt0IQh~#PNeP*S>JwcMc1QHbC5tlHo`!qP2-2Qrme)csX0sdx-yD2{r$#kdW;nLK98NsL~R=d*F{yARrLg>=W9~>%;#5^)|02'
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
