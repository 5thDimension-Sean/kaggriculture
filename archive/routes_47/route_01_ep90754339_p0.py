"""Kaggriculture agent — Route candidate ep=90754339 P0 score=159,259
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
    'c-rk<O>bM-k^L`Pb76kzV|I$o#6r}TA;}>+4WiLNG8iC87Co~Y%zq!XMUjuMs!pA%TbHCeUYRB-zWaTvPMtdS)Bj%l=P$qh^Y6c2{KrohpKqU@E;f^k|N7-$fBWy3H(p-;^Os-$@%R6EdHvJH$GgYX%ctCnKYaP|=i5(rKiuA5OfKF(tS=@r@%Gcl)#~%$gQwN%!^_+2kE`3~i^<jK?H^Y651%e3)7{rUKR$f;^8R`M7t77&|0W0hxqJWTFQ4~MnhyH*)5UuA^!&B0pB^5cKYo3+du#OKa3G#m_xJm!PJjE__${j;`@b19WcTTCobK*F{QNQ>&tJ9!$~8?L7tx&UPiRfpkCgpL_1XL*wym1?@8|f}2d&x9xib6Xw?IEX-`~Dp?Z)lk5wdUEL&Yobus;qr$l>5_oAKKU`t7$~{{QKDw`ufuB2RvQJ08GMTV96h_IdR<diD0u{kKNVKqEUkjCPF}wtRK_WIR3e%ljXc!?b(E?#0u?7iYNS6O@I%Yw_-fYlmyRCdx-mECJbm<(aQ9audIAFPgEIL6gVN;4o+!t?jB|rg<{_c4EBHVw0P*X5hvLVTTbU)|-5Xzp|)xhlVe6E^OZ!v~&NC^{Ctfl)>74G<syR2mAJlAAWri_+9i>U`&BOds~Ifcdd&ya6_W6KHT50-ar5R$JOKW-TmEPzm8gU7mm@Mv5^P9`gWduZ+dgnBU|PBSD{P0b=wA0Fj?6CY{22%eqjL}&d5#={k82UwAuXduUV%Iultyd&}*0?ZIHuM;JH=~l61v+n@F5}u}9k@yti-NHYfv(nou>wdnYN5bwtKU8RCGa*?kR5_oHfn2TLGfc8=ZWq?dQ>CpVbdk*h0lFU5}8f=eiK_4HVWx!btm?8~2cU9OV!@fN%{yyv(_S>gcec=v`z%s<HOn>ICM?$LDAH5PXNe@}msbvZ^anp_Pgo-z)<#cl0LFE1tb!-V7F{9rdTeNyHH+URP-on%1lA8#N362G&?CccW=Z<~_FNfa|OI3~z?-~aYFkde9j3?R8_+T^m@O;&p1G`!x0+8bt2JENNXTdf1UI|qGUZM8L6Hp9u<|KP#9@%fW;1tN^TWs*ANngTsLCrQR$nH5dND9ojujIO-BP-e987p=ezBBjhW8KdOwkLLqQi*2Y#n_=4D?`-iR(kJ2Bc%8@gx<B0gsgpxM@3|uHvjs^bj!4V+>4=+!#_Y9$u_4piks~KnI9crI{hmF^V>zGST2!maH#~+P81YB!WB;T<Enq*NM^GyeG--@#?M=K?OpOYPWe`u`kko?3&3?7Nj0q<?JVO-@Th$bGv=7GY&SY?_jm=gQ-C939y!<nLhy0P>2JOX~{Lqk*u=Qe|o*!@5e^@;}{`m6D8<X`h+hm+L!eyI8ax6l3w31;Ufkf$S%NO*?G9%#Qahr{HNj9r&SAen4n-My4sZg2&PxtK)-1Xqo3;i{NOU{kZo4+^MVri36(15ikbIBKx8_8ZbN?t;E2$Ts;%_Fee6m%S8=jbBowXn1nfg~YgP}9pz8Z98tW#3lG?H@fkhm2}Y`R(`&gyR&9WU#XuiX&OKNO<}RcudZC1!k|K0jH!LXotNSQB0cWYO~ZCHHOLE1;*P=5j7>s=r&ZFPqz^P$J*F$+NbEy52US0s|k*E#n#IMav&e5+w37vN2cDu0Ad?&(Q*yIlz5+`KdWk+lH8+C*@?(8*wLE?d^zcp0FPynNFde%XO|nEvwi5xO|yy1_HicD>}0}KHiKDS(9)nG&2x4}-P=~b_8K`zh?IcOzZOqq7<?XE)=FZ1!k!X~L)yoH&(PIc+Py$_xgT)cuET&~q;f*qaDFZGbj2o6%UK()3*O8l)`v4U%;H!_$VzT5%Y>pYp(kwrM#X%!JsdFy2=~%CCfos%&4=VOo)$%s5f2U^I{6oF1!2*e3Cyu!!KX0)(`u|i;ZElAqBYnQSdc9PlKb5;jJ-@TkAAqj|MQ!+k75K~DjGYpuwfWO(5F6DZK_+uY(c|V9doND?2RdJFljvM25g%a4mu&IbIxu^BSH)jTGEnj$Hw-Sig5)qM9OM>*foF6IK#0x^yU(R?D~j7EjP@8!E|eeootGGW+bSU%rBjsS*lzNNOwtrRrk+rvioT}Ji9KMY{Ff?6|X~+SK@sx+3)?c_{lfhknAQ17gH%ld?&%O?P1(YX1VU#<qUq5+zr+(0Yql$P4YC`J?tynchbtF+WnldTIF*U(WaWYmG<iZ5Rfot6LE&Op4$M^;FIzSOmz<$o9^>Xo(pu{YW1_`{|pdlrkrYMNX;@SmYPsS^`$vyIaeVe6UyX(23?0lD^Lm?={ndnm>!rlYZg*Sb9>+z4Uw9T7|Am&@VoTE(ObhPr&52J%$21eQ_xx`|Ew2p2XPkG%qaUp%QJw0_!7+0;-r166>xDlDb)rKP}y8-yr0T<7GTw=Ml)WN;mwnG7{MKaVno5M?}~%7Yj(jb2Yrny+YkFumd<ezwRa6XDP{90yC_digAp8UR6aaDeC8O?I(F@vV6#n@d?nVc^q$agf>vh^)n$aHV0#F=@!q`<^MeL@wlLc~uW2Ci8(-U;TnK~`|3D%m*FZXTav@p+frC(Ub~6jS!Gqx%orIxfDP~;_$uWVrxM#~P!&={Z63UMys#8!AI%T$Aqjr~(EF9JwuNbg~@+B<2%<#&GnMAXB0mlsD56XvrhRnp_&>DCzvE))@wqf0o@tZUAo3U<Md{V$5X<!ArG`fZM=FEIk=^}<dWbgqHS(y9cYLj5|$+`eI>BOPfPzZeld69R|RXKxDECrC#2H1}b#a^>?BLq#3x44^TrRqa`PCddm%LA`PjeMq~9m!!C?l5_QqW)PH$W36c%1w*V90}_L7Nv;^G3SqB`P~%lRpV`{sEG{$F>5!t=6MD(f<r<_6NbGIo=dS38mT=t*9YXRVxkReFDM~vdV?;nGaD4l8=NIC>nFP$6&RP^&dSxhyz0B1l_+>{u}(NG$EI9t1g9y%bC98fh$sR3VFa1PHmnM?hGONbW362tIay|?Tk<kVat6X{(GSVX9w9n~>{_HF^r@ue3n%ao9$DDm94Smj*=?DOy<WXbZa>*QC$JDl%WgKIDrSd;F5CLztvqwkAipKjp|-u`<%V`xibvZ|p_J3oT~i7i>T7=41`66Rkpc@2{ik$_>Rj=@mYV?G5$7P-w1*n;JK&<*9z+wVXBsf@?Iw7fgiOmWt8!$$R)!N@1EI*94X+63HczE7lt@$B>)Q8Zb9Ga}GE=h}D1r&&(awuj70b&BEIPm<7MAc$AbbItZ)KRr+DY9N1Lo6hYO+1;^9xAO(~hw;qhNBYGf1$OFTv!QN7jV`4ti{Oo~_EI_$ux@1-=I20XF^(fkJxz8S_FLY3;Zp(>Ht*2WAp`vmHR~l3F$vkS%O-l@8IQ`AK*uRO+_19Ew;Kq~|bN2c0P$r_IY4rdn%soU7J^4apa&^rf!PjXg42JJ%=j^<v3;s3NQ85H2<Wm9{<L0vn1FYY7RwHq}=-Tz144*0u`NTq8(%ga!}g%OcCb361fhzmiRn*YgQG#Zc<BW_t2W-i)t|MFfjgDTy5tC%Uj~7W+J6@QinfJ!2cMNPCHuXy6;K>=~s$-S!OB69t@)NSrrUYNoaE>{R6w4bX*Gy;Vx4VsW#{sa=Kk2zyoq27Z!3X|y;MjjLid0H+1okg%dH0shw0H4UPgG8wo7QHntkLbn(}%5s8>TbouJtc8*uD~bl>*+s~!x1)tJRv}Lc4-;6|)+>}@Kb*qqCbhJ-hwZ*v!_h|)%0t`?7luYwI)<*n3nhywkV#aIh9t9?Sja?Sre2;t#=MxHcZ_*-AkORX1SXhViWr1K$m_yHY+yxp4IxXuSc8ia5MZte9xvwYZoCmZwvmV9`s9J^g@_Rtaja#8*>)C~JM^;qk_)(*d}Z8;A4_OieHb@_f$waJa#K8-6U?ZMMw>=ELu<IKb=Tz0km8I>Ld-Hkh>;mTY<SwY$(70S9;0}RgN*yFEL}>wQWEAtuzHv}LX=!5vm`?%Yh3WNB^A7}u{8<mzsJBTiBKF*b8j*Iw+Ub`8WhMc3j_k3X!XrW#3A@-_02aQtu7-a>vjvJgj*4rj>LI^c~4}@=lEHRO%?SN2M3Fy(^~%U;ygI3aDfMBD`5pvu6CE`XG=bQ+VjOOQ&CWQ8BxnvuOdEk{WL5(=He2yhx*5+BSg|*NuK!jC=&3FEOh1MsEH_FZ6aFvUYMWYXxD|6HMSC?T_o3HFbjP}C~2gsO+s$6&&kdt8Mi6QKy^q;d!!*?OmVxZFtHjhRN}C*R0LkOE*D)YdCLGCdrcxid=QDO<vpMPqKqpmndCqivB4?<E}GU*FW?-Df(NKp*KG~&;CGJHM$fH*d~2FQ$S1=y4%z%=6%<GsW>4fN&cj#Qcd~f6@)x4$vHHm+{)EltK5D34ZSLIgu=s+M-2(JTRT9-}w>-g{W5@AP2Z~e@75%D{5C9G*dHeT=ORX##Ur!PkWSW>wXR;d3ja#thsuB!+Zg1*xq?Bs9g0i7N(=!T{iq6In$ToglmP|^K)Z?l;7)^`_YPy(B2)@IYD#N9}eHe}7QyjdiUZqT}3iX_Gj}EZulw&1O>Oi&`;w9P*ER2RBD9~$NWs>xjQ>`6(%`Pjdush=F)8rJgYOMlrgn3f48=_#TJe;sTv(m)+#Uq?@A|f46X962L+uuM?m2%`IYGl+V0(lI9I5gu8Q^he?lG4<+M(FI<%Z!Jg({W>(%#{thJQCr8UB*Wy%(P;5SIzKKUp~#dbK}!k#F~@CPs|G|)Z#%(vkqzyRG|{$$_HCbtrP?d&*24u#ru=(vsU?xci(l{qv5-N0*mUWgu61@0JDU99?*Noj%l#!NRO(m(vR@0b2u-``m>zGK$b-w^y=bZKwgd*o)j7z!I7zol50YAEIL`9`X#ZI;0X|?Uf5ShgEmAzp$jTAU3N;Hq%%~#h?bdY@O&57eT6W<v>^SZU}aX>3oI8<xN}@GTd1mwc1O^g!9Gg$E#nMwgin)Db7Eg9bw!Q6yIm8*dVPyPLbbB+jj;j@FBG>!mCqugw(}6x$+bq9WK!n7Zf0#t;KXhkf&`I*0jRzeAT+52cvJuxAtR)EO%fpE^e_PD3bC-7pgW=wF`mx&q;OA%>ASX)8|_tSv6-b1h;E3AxdB1X*+N(JR0b=aO{Fxy6u!%<Zk#wJN^?|sW#u?hlP%iN+~B_T9JuE7QR=9W=p&om;O%!W1cAf!O`Vx`s|cao$vVgu;l*caMnD%Hg+n<4TP~e1>k*OVEjlmV@OI=}&ukTq=_XLdvqs!g$FzAii)^9mNwAeym?V^B2~@TFls>;R+pd=YnKH~Z22*78+4MI%tUJQu)!E9KS*{e3TZkkaGy68;M=Opmm)>OX5a=xlaS4P)zzBUN(^B3cF0DsFZ>00%P~ZR??A2un7mijuijhe?J!m}Qn*cfx)TU@5lt|xMyB!b#rjfCrCO<G<`)F}CHlwZHB2`m$=)GPmbl#NneE>pSS7!AntzMj4MU7K>;V5#%5GYdV-W*jzx1K<ZF6uW{rra<Q)AAO}`$zZOq=^G9nA3aWFua>)`Geudv<b>qTA2h{O1gl~MyR7h2zN{+40)(XjvT9X4F*-3{LFkh5Vv)3)o7gEkYW-<Qh#Fl4bY(>Zic3L$}=Rej*w#IBmO{YlBNZuh*Sm%>6g~bP=XBsGEAU1iTNt|&BIY4vfBn91xgs-n-?{TA0SRJL?D=X8l8s-BBZ#(5JZUc>F}r;&L_f)0ydzss1XZ7N8x-;+U+2!vkx*rQEe5HXvGcggx#5_N{FvLOxK`Aiybjsa?ZIL6jz?C(Fr($6=R-;d|b84G?UIFbBQ{&D_IVs-;lK`sEpx2UpeJnGtx3&RF*H*QH&Fdq?{MnVrzxiLMf7@5LQgl33l2aEqSKJbl$T>D#af}CA#<%s3l7#q(xHJ;!dKv4A>K(JD@5UC4`dwSNsIgoGgbK%+2IxERIA+aXpkqnGY1Ts}egYsMEo+pin5#0&c*V)NEU~1sZ&&W52wnhx(3{rqF>|qr5?E(9jBG#8q4MD(a~^NJyLvWh2D9n8BkED{>ASlOZ3NG7nELs3rvIO#CqwP>Beul*EODIxvwOY6@J_>JR2fijaMivz)5dEXtjTh$ds<A|+i3u^TBpAPDImp8w`=H02`7>qol(Nlj}6oWkIhqH~fUKB=CHg}F@h@=%d^1K%DLuzEvqZ4^-l2UqtGpT3G{6zGR(7^(uzkjrm3fcw6Qv32)ubElaC$&&YEU1zim(Tb6l%4J82#wsz@<WiOWSFl1HX~|Tq_DFsR=W|7L@N8<xBat&HbDCZ$R&Asx1O=m<zctXKqE3-qLE^*Rc#!k;IvNMc(rw7-cdl8CYX<V-t&neA|2a`2i;zd-(o|9if#uutTD2jCh&B=$W^V~o6ARin*%Ze~3@cKcWd(a2AE(J-uPMjt`IEZMh5A*-SM!KZ{-yz{goa0rAv(s~$Rx}~y*AJ<ka|$#gXy*M8r?9+cft#=i+&He;7G0-))Y-~aUgq(C!ukiTFG!qQJp3Y)HJ?ebzUN>c<X4aLFp#Nc8(+LrygY>@ELRa;)TMH>xx28%F<(`R1ZZR_%v$`bim{_xyKbsBwzeej<p4{=E_F$#o$cqGUi|t+96tc6>uWCN?9c>gG#_y86_;#LR6Yk_PKnp!%YLIgLKm~<0`KRWq|EQ1bJ$H7UJB{dYJ{>cnS-NQQCGt`8r;;IzAz(BU0gqDO@0!P9>1eHve@(fIJIhvKL3fb?Vq`--M)(O@2d4q(Ro(@+4Z$u-_;yW3v7N_h=+-aqa7?1iO&A`9l@LY+eK=qCv%4s?}#8>l*b%wC<PGMrcQoLSiW-caqAUJZ`?AC;mc;2EldgTUwF)KvE)xLW_f3frc5%Z#qIjjoo*KU!7Qi6&oxr?S%4^){#KD^_?OBB+1*z7Ozj2gUU+jcnCWdhT(*DfqG1!ra4)10iiVPTvV;Q2)$(Zbl>bi>@;mh)vP4g0lG9A4n@Vt7nwyy>V$b5Q99xjEXLKaz#Ldkxlv&lBTKp~T5XcssbT>@J)2{}DbR>xKqb`V3Be>aPUWnv7`ey)QUkeMQPXw~0svDm45e6guqNs5)~aRHmog}3?*eAboWLS+%|*^MjB)WjRrI)ADXJnUctPfMUiK_@M%GQpb*C_~GumLTJbeR}m#BLd6;^7I4nJnWCcXO~?*0@?RPD<IX|LquXa1o8xCg5p7n#WDroYXnZ-;5CAY0jrqnNeSf6_z3Vk)&m=B;yY|H{95`y^o-+W;Zhoh#A}!+i~8$FxqTl*-YGX|(r@f+TOVfh){mw9pJs4`P_4xQ<lxO>o!n<>$y0qGgUTuABm+<hJby2jI4p<RM30+dF_r?$J`@9L#z08xgTEx$ZOL%H=FG{#0s{1{5X*jDLB+(SS-PfxXJ(s$+~}L<<R3n<Hqr^5P*Ob61~y?x!C?d=P4lqatUB+5~xhyxy_WaOGzR5;}yzA{Q<%KN^x3_N+dt>YU7!8y_d)HU+Ee0H2ugS7QQIW5F~<GGFqim?OqMk5EZn$Zcg17eF3F$)_m$&lciqMBS7#0DZ=^Urt}w(I)i!RR$i_JBe4bbi$dTq+g*yH`T2kY2}vb|Ig1eCv*71un+Y9%udbrL;46%Zf@#-Wx*qtHyvyLQ5ycp7c3$4rD$?pn|_Ltfm}bJ!d`-*bINLhs%{ZX^|Pstr>r%Idt@iC5Hetq2wr({LOcU857M@ix)w8pTm-n(9Dw$yN@+Ze))UjC5Xc;xiWW%o;C$RN#^7$2a!GD~1vFqgLvbuxW+l4i5yc1ro=}`EIUUM2=E||N)nEf0<TVj{brV|AFuNJ}8EMGmz$<!KI4LxCzMv{Bk-7%3bfOu{pPAiRMM^q)bn?suD6Ln3d~E`d)Ttwz7)U6*^d%w@VL+|Ih{~uSlDApfBNQi8Ryt=j8EA(NQP@|7PIS^iWVqZVL(YvJQ1ac%G8#pch)9s%5p`(2cI%)rN?eBZU@|)vRq+J6Zoz65qaM2nsFzg<sCFgG?GC;Y=+<Q^x;6W*IEFGb8LSFkuo8DFB+RKdzh5h$9B9fEJ0hVMOk&HVwy`xYInoA^Eqdk^FJU$)wE1H*(OU5mrw#gq#|mWYBo!|aaSwX~ZAxPCLVb9Ou<%>4hG26&OH43g3#_)lS)tv596vnVe5D3y-M24&R;WF|>kRe4T_>SBc<ja;`=PleC)YTtE*M7~{M{;h0Hod^vW)2c=43!(5nrAHmyJYigbqhktLJjlt15vfTG@bd_)T_!VRYH3Q52gkLsQ%X-swQ1&7t~u#)~i1Jwyn2WyI;MR|Xa0{4gkFr)H7bQvry&s$~pZae`)1+G1>_+ymamOadFrcDO{Aqr8#Nx%sZc-lYuX3~O}Jie5{Yp?C^)E|QG2@Q?vpip;h7N>ULKMByvyAHSYtuxt*v{=1cqM5_3~dR(w7)0vip4A$T(WrWpKbaXU$!H$X5sXR(4M@lq;(pdmBv11f&1X@@wfRrh%+D)llo*24~PvWaF`awP+SM#!xh(d`B7@sCYo*mM0t1h&dE+T3|0x_x#u4mvCqYVhYH?gP~DpCM4WJ_x!Vo4@$p$rj#34@AE4B(U%j!O#T#j2);ws#Z53K8}Zvqd>v6d)bbJX144)&gKkUABrwWvRo`5mxRx7@dT<pdNY_BYNjR6Q+`)f`^1O>8o?uBs(dlw1uF%7~eG3+OWtNk3%Aft3?-yt9P<6;B_fkXF5IqT(nanRfv7YypyH$%sLejr22ytziMed*{Xsk=|*#%K^Wd8#j?Pwb1ppSX?!K5!rZvQG0PDmMhyir98&ld4VSO)MG@ZiQiPD-!6(_-nk;<v@tO*S4s~TunHG{G!5o8joGVK-@`LO+ge{aWN(AM57B9qoqw2abNs>6>r!f^NRTh-Pf3y!XXAA=R6yfinpc9IPRGc4xF6!wQ@v=tj@v=^yBsD@tL^++val*W|5$bHh6_QBB2g2U5j(l{e{}V2-3rK6Wl@--4$BPbh*Q*_xX1S$tf52>Wn4OB9-JnZJRhY$PH({L(g~Ve_Q)EWSDiedXp=J7I4*}fcfP_AqY@yWRY~22YkQS@Nw2YcUp12xWwON}5hHRH1;DUie#aV11Ne;KGk`*I(4Ph`PPwuLnPWH|M-R4+wYHL6*vjCrA2(%!3-zd=xnUpSAmn>tRCWWo}#Jld*7!eJP5;#9~^~G=_&#BlV+YK1=`4%cE+Nnk7P&5$_xx<xAfI!I-iSb0mAnx6v(jjF2`4qsCR1mswp$BfND*+LY10H&|;2>Rk&~UCo3l|lJ!AxTOX<!V2Maq^8gkmN^-F&xoE?vytJFvJS9?;j{s7S~x^zYTQ8q;G5EllJfY7$^}K8-2u8zL?!?a_|pT!K$cdji7Xu{@td^C(C0c+Da6zmC_S-sRrTwlOtQISTvcz)fFBr+mJw=CK^F=v?4Va*RiY0+YD0BO1V5@w4RP+3w@Q21gl$+8KbUHh}?%zyWl*TAb7Y=?Q)-RQd$1F&nC9M+`}njt`49rUX%B6KKXQsW3`8$$@E6on>PNvkEJSxgRNhPOCcwo{vR7y@ZX3HzRA9?ezuS(2$#s=4e1^l^KG@fM!>_bv}~<gv_&%)CZHJ+xYkferSvI0t<378J4*g>{hK)2oehF`VzQ;!mWrGTxaY;+-%v+Y^xiZxO=uT*5KQ4-&<vZbEY(iGcw`D!I`u9e>iIQEd'
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
