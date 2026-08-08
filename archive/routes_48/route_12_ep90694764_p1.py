"""Kaggriculture agent — Route candidate ep=90694764 P1 score=144,155
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
    'c-rk<U2hyoa{MoR<^$)06y-OrG-nCN6$MK2;JhFf3-}BJ#`$6GH^cwkI%%f6r!z7#GOKz-t?q3=&U9C0Raa+5Mn?YfzZd`h+wXt->+cu;^vlKjyAK~Oo-Qx`<G26%xBve9htD7X_S^6O`PcvX{P~xQH*X(zpZ}|U`03MMe!YA5_UF6%i_42w5BrPDwfXahH@n^Y$v-~qcCSDGdH-g2_wnNL#q7^N@9rPoU0kk)ufKnMc>U?s$MF}}Pf!1Mc`~23um1e${bT^c%znAp?>>C|GSYVsk00NB`E;26<ag5%e*M9zN#HQn^I`n->FxdNUq4^{<EJmynT%q*IUB}s;qiOZam;6ZfA?y4n6!Q~^G|YzgY71lo=*|p!u=At6|vp0f}bb+ZnXcY2@kgTx{!_bJKpE(PW-Yb?mq4wPw)7rzwg%Rs1DywnRC4EILYG;Ufmsxclc5#<BgLV?lgSIZvAiuc1?h-?1q^AjIYwk4MgkN4H291c)g_ghMmx0KDyP0ouF^E`E^CBjXR->vG9XBpKxTg`P)jg+T>5V+03mvSqsd;w}|=I<l!n93mC+=k?=s0shAI)Ok_VeM(Z~2nXS5w`}D*4FMBvk9M=!}IUCpA8orRap7EOw2WZnZ=11$d8b`st<{C$r>JKrQ-Cg^_^ccshhx_~8tB=3_Y4`Z??fu(-J$-pquK3~MQ~NUYAJ*%~hxf}qO&@mme-G;>L%#HbwH_NHJb_k?*LyZk95Z}*=VbP6ubY6FHo2Qr^r5i292JNo$N5T6FEcvp`t|1L+sXCN3K$Oynsj_P980a9!T@C)2=ITcPuFm7Yt+#RvqtSY?I!!jMo1ivIfx)OLgv;apewC?uW5s@<p-TNI7t?oxEm35y7$}(fYTj5eEs%vxBdZU&0pk7EWDTv$gTgFCMbmV&-KoIum3$=ZRX!@Gyd&X^>4YOyTu7O#j{e9Vuy<<s3UWrz%Ayt7b2yUtD3xJo4HQ1NHuSNj*|Aa6$*fuTRHn*<(Afnc19p42@l$;6Ho3~m}2Hl#$N078xos_5PT2VO}t-ARJiH*(oVd{5(6^m$u}6ovoi`vZ2s^z0f+8CjM6Ks^(=?*T_*;Yx~!Zl^!#M!?cc?NzV;|-eLU!CfY#fGraZ2Noalk+(&R)Fs#C*MfL9$uh|5{ePI9CPDGpKs9B0(A29#WI2c@`0nC@mVfPDDho4dz<Q61rpfRrAbe?E1cR5J_@-UG$6^UYo59opfKV^Jt=)-==K<A5162FYEJFJ&$>m`jTC1TdT#X}<oMeCzn9=_hdMXwU@8Ml?d4$r6}Zgo1gz-*nOKOyJX(SpmW*^b&OPvuCY%@&s5zj%ya%F7&|7#K4X?P&$VH<+j8y0dVE{oWfHYX6uu4rn}!+&Uof&ME3ZKxpwBY2?`xnybNIl9+ZN^Q~(lFuY#`^Nev7wQEHfB)ZoU>sd1*skit(q&@VMGo7M^kmb7`rfNniRI9wMKYd9E_6ZR0OmZP~EGXE$)X$kGG+e3T!>zlrz`=)=yezrKhTZ+rRA{GtG`xuB#sA3;BZe*a2WHf@DbY=wQ0>!TEj2sQiuHgBm9k2E#kvXx`W+0M&hHP?4VC7-Vpdt!!E)lx;QCM++3fHKKy_NM}>{yfGS_XBn7gQp2J+5muhqX0Xxqa)v$+Z=`*uh4m;i_5Y?#Xo+<32pxA8YA>7j`rGd&T{_zkB!kBCPkH>jT7r+q|A1`#Z>85Z%O=v&7GbkB@izpLUOrf4R84jo-+$4BpTFESI*KvyjH~*Oxd*iUD|GEWX}&G-mFhSbDrN_}_6LLk48_ou#eqRh|35R`}Xsb{{T2&&;7L#AJ`Rt^p`_LGS9mv{~T5084<R$zX|vdF05@Cj()dc|L<qqZA_<Pd?-HWD7P@3pd+rx?vrM5Ay_SkcDY*%H^d66-wv`6u|W@VfiMO)LIQ4#My;R431$Uqnm}T3C1j}>$R>Eq$XqBRYspiuU81h6N3c~Jb9^3%{PuHK1w=T5AFQWqVt%c(^v^1(PZz6e6ODS&W^2#idHj6ldOa~LsDy{-;Gf#<<RR)9JZShQ;kccO{0}<BAl8Y=kNtD3XwJ7^Q)`)jWJ4V*)o4T@Z={U3b=g|GpEj-hB*L#v~6TBpY#9$-Dwy${Z@q^mswgPpEiF(?B<RP7+aS?l7$7qja^qen!tS#$3;a3SS*PY!#wK(^4vlT&b`l&o)j5c&KzB3U(P(jWyps+;7<D#lCLK2&5pa<nB~;PrU1=04?JQ#Im9bR1}&^Q(oS~By#%X1@sxZvn#QaYhG|7keHNbc=%5qR6&1jl(o&KIY(bWdr7YqCxm6<s3a2PoRQtcSG!)n5LyX+Y2;>BXeXby{Qxg5G3=4*k{#~Vd%dQz5MlqK{s^&ac^2Tf|A@n?#664o(cP6~~*K5P@>F2lie+En*cuw~l5DBX(+cjsTC_E*pNHRdjV)=C8;f3x|eQRY`jy^aDW?$rk*|i$Xu9||`uODgzFe|9g62s0fmwGqOw2E<jl?z#m$-`NVQULV#8wtrY*nG$_!KcN{PR?Y!Qf;Y#JEg};bif7bvRyW^kba`Zk4g%pZ5xWm_5np>a;RLvC+V$u6iF7f;$wjwVV5vWWr}&`yvL&@EHewNCnH!6Hr$1%s>R3CRPVLfUqsK~F844t!si5^)EFd-2ww}kDcoeCvz8hm^luSI-Bm+hV)Y_;Oj@SSYuTj1(rXaJ?_X{VGh*L%Il+%!W@?d!IoBTkF|E>+)@0nC%Z8AOWj&NAZ-f4Ltp|J<;9h4UKg+$u=}V9rS%@9V9L-@AG@aQn97PF)WheVmXC)B}8ztMna2j%XrL40*Sj4WB%(<*`1v#JBu9cOJ@UtFE6i7j!9PD*5gV>X*iVO%mNwl`U7)Jxg5%^GaVDz*~5%xCy^vn3d+prdXU)rAu3M7lcD9FYTpS~1QxgZ9eFyH_{oVu>uL-B!PnMZg?bseNCB!WI!UJ1yGFE&nofR7^qJ_5s{=3~6k%eFNg6EwsisXP0?hnswC0v-lJh{nSTkDH~*rj1g0SSU&mMffS#W{LM~{7{2^B`@e)B}YjzP7_@Rd)^4fvp0_te7QdlQ(-y3<8b2{u*#XRBDNbuBjILA`fkr!$%FMaS5ETtWhwcol}MW2$1&K1NWHxF5dIe(gH^inG?lv!n|5sj((lwp2vQd!#E{om=P?UHBVG}rkJvIVfK8l5)C+~p(_$XK=8;9J(uC0bD>D*AA1pT+Sd%Uc3*OQb(YIH`_67O$xSlQGKY@Aq#c+MZ=P8|$*54r^P1Zs<$OJpKk=*nqS(0HPS>>}%qox4~$=HuJGZlTH#d6o;)#+BBojTE~g#>i#644W?R_~kvKYW~vJkj&U+HzKW{GnVuK$J=wzzN{30_ZbluB%jDYQu#pQ32sp<zVO=nv%W41Kx*MI)(U}u;gX2ESE(aI8N6IKz;3?%jz)dkVK~k&$>>e$!NvCaHs#`sY>9F9t^K1e1;%FN!40?M1v{jGjQB(^<j|c7dnxP*f++~G8@9yON6^r(8{9BnQ=}LWGfNaEi{ui15eOIYgOk6F~XP!+;m!bT!~eDDdbp4qiIL%Eq}~J4E;^hj?jzjrRO4Udny;U$+Z(;`g+9+)eX;Ybg5!w0g@2_|8sk_^T1ObSyLYp+7gQpmJmdKsFZQ)TdumOHKdDJu8ZKUWf+yz@K)PO<-UYy^`<ge&}$q9sx_C3fU1aueMy3JsZXBh1IDt&u|%Q*b!lB$nFx+_6&*USOz1r_orf0EO=jinJ_<N3Em+faSp*^Hjm4I4fKqRCNJ-OA*UG0zV;LRvO37a{<&&Cb+FCaq^vRhDiVYt?L#R$xW10v)ku;|=!Jn|iGUgr~CX<nA{$;(pG1JO?dxZZLOX-LAfzL1ic$WT{t(xLUWl#xww}@o(ts3VD8-%DK@k@CmLZU*R?4e?kG|=w4C8)3he_1891BkU|q#&k9LrR8jO)!*Z-Bu;`qSk4e&C<Lc8{o~3k8S6Q6{#j=9hZvmW;8wI3bH|6mR`~%wML22y+{-+e6v}{*83|f0KyU~=DXM550d@OTYy?W^J-MA4~xC+-teI5n(eiceBysqo0!scHu;mwP-vE+q60~CA2R)2$Ze_a_fA$qkaYAJv#4?UtN<NtEdUb(12C=UlH8VG$`Ps@77hSP$KVefv00&K=A}Fq$^dMS515vFe|ZpE7@##(aQiIu=*%N&%HW36h0*9#1kw;%7h_z&On{=G$^3Fiu7}NJ<+EZHN<w%L27@HYJ>6jW;HR<2(^l*8WRqMky(HJVl;je!Mjh4K)^Qzwn;6?P(3-pai*=xM%kKLW*3%l@Sv1in@f2rHGDcn3aC@&pzE2v7RRd6)b}VqGbrgK}mg&c+<kn9=%#)tW)l!paB-M(gQ^y@<imtS1S`fip*LYVnHC6$@iS=CLO_3nXGTDqENN-3g-aKWLuW5O0ydsHVNad-nuE=tnO%%VX+929ZrLtCg&wi~)bq;+g5(~?%!5fLNQj3ydVaY%k@I(f8q=p6fEHV(FcNSohP+UMPuOO?kerk;Z8Y-2)pM=J8nGG?=ktf{2@ir$y5Gt)o5+@P{t@)BO4YM_^BDJjzm}`q?U(`ed!>jwOIK3-#IWjQfl9?RUU8FeKITAj^i=oT1lM&DMq)>;#;xpuq*sOp<B?WWc6HHlC(psgCsVGl8DR|1M@KI>aKn|IvW_ZG!<xc#pTi={cI`KvOmk!h*NsY^){UFI6awLIAgjKfCnxsU=3S;+Vc!}CUYHi%5Y&Ov@#6X(n)g<MCjV*mlC|A?bAFz!fr%>tymXw3aZWlePC(EEnvsprZUD^b>$Q?YqJ*L9t5u=p`>Taa^ZGkSpGP$-v-K>FG+1$q}UtRa*j5v`W?2u+`uBBTG(%aH+wymn++ovum%5_-fwzO<GjfGD-1RjSz-3Zst^rqk0ESCYbsD$;F0t4FG(dI-RQM7?*o5c82Q+s5o0d!-Bs<1CRtf6xnlJN}RoJWDfpO;V3Qh8(wRK#^#9VMPa9|+-10wa0(JR^>JLF{q58>T-KH$-N<r0~m@(Ez`mNP3wzt9;D4fQf&ivU>XlRsT(*ln?X!7(McI<>B93%lb%D>KcMpMZXAGnCo|tpbI;|6KGlCJ%M_DEK}oWRFYuzWVQ}eU=_;%5CxxN>Zpya%K;Yz<shkOx`yUgxei&%vcwv7V3dN=ckW!I17n?qlk@^>Bu1PFZR5+9Wo#q&hlubIq*x^}rh5u|pVaw*NOkG@zip><`T9Ag%lRh=LobsOcjC%8&)hpZYTmxt?!gm;3(aY@Kq{QMRWyOxC++QW<lN>`lm~l;G<VSILyM0pd2Q{zL>u@-adD?KHfgxyXe%dDn7|`fiqr52!Ztm-hJMSmd~!#VCbVWK<q9%dyVjVjV6EhPonR{5L!DBcA^t;4DJyGQ5m`s$#Tl~7zLT0PgR!93ylU;x=e~&@k06rdhgLZLTt6Z`L#q|!<8>ygs`(&BXAN^^8|fs%UX0l%JfF<e8$u}~Zz%<p-(qGQHs6rc6t|+4(@s0LouFShK?EwnGZs9lE$xsaOr(kDu`s>BuD4)uJ!@af{aOLylWt9&vcaCP>I>(-H|Jogm+MUz<fqHMtaFLqIG0&YUbhvv#wp;nlqPO%2wf`pOh)n){fegEyDoR<Hp7j3T8niNom0@P`7nioD5r9vUgi?vAdsLWuTZKivQUY!*)b?dspxX}&heRY+`O&>q_yS9%uA2-?GnTa9KnOh5(ms<b@P>-rU8N!a>nwK3@`d)4B*8V1?(TDS%$Wy&5AfQ27zYLtI3Gmf>$i_5a^zP#-}!^y3iFm98S#-N<BRt*LDG#bbWEGkK}fm=!=U;9X-MCm{nP;nXg5(>!(C5Z<Ccnwo!p#%re0g|7TT8sLNd?Y*aQd+-HdfW1^ds+ZkRsW33&9+f))#R<Fu$lh$NCc&17v`$1_}Zi6L6ELgK9qLMs(sBN4nO0iu`Avr$prXQM*m^5|b)C!k=SEql_CtB$f<QIz}I53?p3J+v!(;C16lH9USISIe%`>|!jnMN;guVyJ3<ej-tcXUSDIHgvDx)98kI3G%r&0z)WKnwIUeOQ_h8>#6NPTNQDlM6(3YV6HoXsUIWA|;h+>rDc6Qc@KM#rb9FTQdT5?ld6+I%n{$65`aPl_!DSFk*&_qR|%4&@5c7<ItJqaTx;%!B050Jz9eE8gdr-2EQyVTBfVFMcDO7I6fZe%K06`!?NI8p+&2X2hkT&B&~q|%J^}Lv#=E)(2(Kg79eo?NmFB^qkJDpq({AmSG@vRfY(K<iET=xG@S6fJzLG;Ua+E6`#;qZ+pf$hvAe^HS@MaiWt1TOmBd5BMpL?^V?p3W7l#!3N;jb6TIOvROKxO|K@11_`c29fl_5YfWN+K((A!NjF==|W6+b2$ih_EnR}`c**JlR1d<qM%#ko-lK9n0}t|(!DtAaVoZyKWQAab~Z3ZP9h3#`hGB0`lyv+F)(WtExOU2M5U4zU#gL2;pZy=7h<p<^T|UQLC92~ai`YI*em>sVEo-DI)EIoDU+cj-*LO>8)iS`Yz|&{saagieN*#6nxb-@q&4bf2A~H%W1*taNMFb_8q(Q$&qbEU=}sSjTd@{;<OY;J|U+Q12&k$SA6!XqhEdO;Xfcjh5ApoydsfD*T9k3M~L*QHfR)%O6D2nOKm}(aXQ06*~Q0{NAp$I7M&epj^i80C$Sz-kf?JA=5FU_##9ScEKx;>MbWKGy#whOM$ty<<aKZYgOm~%d8rnohj7ZF>w}x9|Z}V07lg~Q-Wf2IQY4VdKC704!^|l3W2EP*C`xnOGxzs^?)Ty<PJDR5<0GB!JNXPSv<;npb6+E17jJ9B(fTW|7I&oi^8%p>Zh+(n4Rz<rgX;}UU7KsRyvxYtgoIQgKhoI8EoYuy>*yjNEX3$Y^p=6DK%D@@TYDabu8S$l?1prJQfpLpu-N3KowPC=(g$HVh8MikoTbtw53%Da%Ai_P|d0IO|LC`pr;5?D{j&VkyN5!Ml6Gtm78@(`ZxIhi9M07T9R2yq)~kc$z(bSGWuASPO;Z{1Hm_H+Z#RBj)Jgcc@J>VB*>+v7O_-s#M+jhz^F30tWra(TBCR}dIX79P)bpmbOdeCTH<6BaqMA{lYSgiT0bMgq|I!IO`ad0(gF@k^rUJ4ZK4T)%`S<J=0Ia7Mbt<_R!FDvpLh2U?+}&jBz&uNk%i|uD`vM99-*956z7Iv>TMiS*zz*?`n6x1x9G)xa{tE`Z0(T(H>>P22_@PQQ~+QXHT~~;*D04Dl?36;egK+CY(G%}xw*JD$8t+}xWh~o$Aw@~@lq8vr990l?~Sn`soU>`)3te?@Xsp2a`Bl<tT|IJn$~qEbV!hw_W$#2X<W1(j+iCS<4SC!KD;ieDo*iL(=4u38NyQ+<O<Buaduh#6I?exZQpg<`BW{BA)+<T^=r*)MOmAtrY6+MB2vm;qG4{0zLw!M(Kgjg!PkR8RMq4LUeoncTi<J_@&;o`D);pI?LRLeQT0NotI#@7%hKNHpDr<r3-8Y7d7Id!(kiMDOT4y9H)NfRcKeiQ^Ta7PQC+Imeu$~x^=Q=H&?4A7J4kD_3I&aj=(N*LB7{g;8NKCuGpR_{V0WGiie~$+Rt_-MI*`Ntq^iFKc7Pd$87_8Pua)&Sdsz0xG#*jQs(^2JqT(e#ISP@5AIW}pC7QR`z&(CkLRB*vaD+d?`3rBgS&uQHR-s$1uioNICq{+%G(?zcJ@0}HE)4~RK9VH+XJ=4J59F35Tn+9G>0RYOsq9{fMcgFA=BZVz>~QJLl}G)$5;7aN9WcV{vtWdh$eD+aenasyjT%<Q2Agm{pm;{%ARpe!*8Mf{#BAwb&_=3WpV+h=h$4E(LTDRjuDxI=XvQ#ttc-h!8y5H<7OlbdC54e0o`J>_L;S$leF|K9RzM|(u#7fFw;+2cWk#Mig>q|OxffO72r2G#jqWI{J9vza_!)2{xsVK)n;zPbQeIs;+OBazA2CWcXJQ<+DYVu@v2Op$EAY7f?D<QuAvH*$!jffuuDx*u#F$`<h_P3f9_Gya$0Z79h7Tm4WmOc9cAz0P7hV*Y3&%J;qXmkf2wQ58DHTTr@p=YJiAq$A7It3cbim81@KP<+ud#=l!^X4TZU91o1p)GB_%y2ZqdSphdfCELV>)dS4Zd%)z1XWf9*^ORe55}bpNDU;mI2RSWU(at3xlY<WO`bjq*6QNvPyL@TuyhZTgyPwY7Bx7TlYWLt)#6rZ&P?yZ7o|0l_qVipM@e73G-PysV=0fwyA6?YRmgvp#g0Tr0nHB94v?fQH?CEEg_Xi<C?wAs#>JcALIDYx<o<$dwE^0R3Al|vqN@pkPuGme9M|yTBG!RuCF@n<jmNB>U>viBr^uIMzNiw#4l{rbrUx!(V-fV93}mYq&`}WPN!8Yum>~M3J|X@L&cSb?=T~&@#}J0TTb-}iV6?DzS#RAxrLoj(e6_gazv}bNPzpSup5LfQrIRNj>Bf6I5<#>p`&KAOB|}Js|;7rnHU2l^F%c5YDJ(cmRjZYwO;vBfJD}cY;_bV+HnN}4gFJ_q8HB;L`AivNHeEd$~C?!jGE*5CTPKh?<PrZUs<G50i5zI5sGY5cx)d*%88WL{7*bQh{5Kt${^Zir@ynyN^*~q44WYywKv(#<s3kDc>t4IBZxf}Lfmj|AnesspJLG)=UG_+-LKUZ7)Co3dGqZmL^m<}Yr7Qt%cnv$my$NL#w?S=Bz!SlD!3dg3;=@`*U7WOl!E;lF^I*p4fHS}dsw51NgE;<T%rk5#)odjk~w+8M5WBF?6Ws$emLN9lgLailS+tIOXBaO)H6t0QUt(7SW*LKpeNtq)YZkyG;AiK(mQ)6E6^GR{p^MhNkXhc6WR0nzCk6LJCRiu>lKEDrh2JhZVtgwmZ(n933Imoz=Z~LrE)p{+QTR07HcNJKr5P<5h|kFiM%qif%Yn8bQcx-^w1Ee2TvS@s&mjsE{js{^;nrXNQh>KPCiCz;f<;Fx~i}eDX)M>D@ymfxZ`4T(?m2rN&;hCwV0hlBHEXN0G<fdQ9hfjc?y18nAT0Xv1Pd5<X9o8AJ>U>XqzwgQ)d_X(3Y58V2jy#$a3?0Unh^f#B0OGc+fUxQ8u-j+^(6RrNa?gf(Q5Q(5Lh3ll7*$eV3wStB_swU1^S`XW~N!ODT*=<hJ@emf^Os`bS1=<9+KA<eR0o6$3z}Hzk$f(%bB9$w6Nd6XR_T=>l11NenQtxovb-8>_91qs6cQTQ2_$h5FP6kP3x{uZz@MRaI}&pqmCQxJchg(DEZ|!q{6*&xNiMVuZGaBnLy;`Xp(l`28G^6}FxY<s)fDF$PvfST5C*ff1V$K%$&oA@nE-^Qx(dv9d$<`eCdqZF8}2mAVw-=FtMN#HIq$%|X~I7m-oB9+K98CJBHh<MDG^;4EX=Sb#1{Li+Y`AF4*CW>jj43gxAXFy|b+a=O$^JLf9ph-o^qjF41Vhd@h@4tO~7!?z2aZAhNl#DuW0uu~xa!MB;N!2*EeOlwHBsflfFS(E&iyCDEm$W0-S;pwddj;*?4a4&(#7}Wa$RUVBv-0kye69CM-UWx=(mjEjZ#dqX<L7r3wb%W|<oe{VKA~IB+cc>y&>M<Mj!ibxd7Vg(FiM{p1*z+JNW3>&JF~WkxG}|N;M@xlNO}!^!V8%hQpoT1=n_ZH_h9`?9S>ysJAc_+5@lvvA34N5qRFJsvVbPd2G#A%yTMvTpuvj=y1(d3eBX&wnz?+7~k>E){`A4<CLuNHEQwOl$sBdfy&S4hc6GW<U1t?9H(;mYHt-F-`bB;;nKd$7+rnc1#-zHS2f#d<&ME5!yyB<_?9f_zn={`kRp@Ph;DMgjQ7W3@%)~<wEo{UE0i03Mf0|K`qA*j8ta`Iq2A2M<FNzr=SThr2SGMymX6~MMO3g6Zh6|(h-klkia03zC!Ct6xO!UX7nJ)on>BBiJ>(9SO<^VTe4cL|e}&^qDiHOwVGdcoUiT=L_Ka<R#a;`b@sYqO$4_b0H$RzbvWoA9DPC<85z>onIfcBYRd$G9j)rBv(CWX>6c><Q1S!x#&ZthLpsZ7?4^D_74*VVw(gVnuUQ(JCXhFV!Gg*=dKELUqT)8qfwfCP%9x!~;t41I}@7&+_=p-@sbKOhxIf$eyvL<Cz1!){g3zWwAyhSz-5Y7^2C*h9u}wYEQ{Ir6LzHs&gxC2xJ^okQJcI(IG<l57|wzmo%RvM3HU<-n65J^dPfF7@FGfORKl-U}!Xn00vcyMl(AZV1jbtk%;|q4ShD}#@2!|s3z)V0q({=>ixKNISrSVKCNseMTCedU}(zwdXIuKRFSV9C6K48_b%~?bE<oCcRnWh9~32m>2Z8Y=={CDp-dQ0nu#)Vu-I4th#5R3LPK?u6`(iq-;_OV%B#P2#o8`K?C&Lp#>!ZR-L#4JT1+R_9C9K^VF5=8bZBdd(YO0)oCT?bMg)#;SekXSTJOFRn`Byegc~wvSyXaV?4l~Qun*sMsuXe}P|cVZ-;6k@JradnPA9{J)oCb!c&*-sm&x;lTw(go>VcJT+_wDIW8LCy%8<Ctysl2-O9iPak%P?1<n4JU5K@685^X~m<#xd>NFLHIQ%YaN)Y8w1(Qz4vpBD3mt-jZt`cmuOESIb^LYjenh(tzhY~TC!(P}>ZKT&c3@B'
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
