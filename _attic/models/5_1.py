"""Kaggriculture agent — MapleLeaf 5.1
Route:   ep=91442734 P0 (HealthStone, +26,007 margin vs Seb #1 — top margin
         among all new training-data-v3 episodes; new-rules game post-v1.33)
         Sell profile: FERT=231, WHEAT=430, WOOL=94, MILK=167, MELON=102, STRAW=216
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + terminal liquidation (NPC-urgency weighted)
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + price-gate: hold sells when price < 20% of base (floor-crash defense)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -10)
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 5.0: New route (ep=91442734 P0) from post-v1.33 corpus.
        Env fixes: TC now flat 1x/day (was 2x/4x); TC interval 24t (was 12t);
        shop demand now uses list not set (handles replacement-drawn duplicates).
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<%Whm*a{L#rYoQ`3O6?t6s&Na$ZV8lRV%#7a4R{O##(2^8&hWomB3ZASkr9!3PEqY~?+Sd}IycWN9}$s1|M%Iy{`%YB{`%Y5Km2_5;rippv-{QAzy10j|MH(-e(>ev-+uk=-~akwUqAoP>hMp$|NQRe?Jr;c;nU~aP4+)OpZ)Oe;kW3+_n-gr%k@w1e!RXpTb+IUVYB&gwz>?zc=P`5Y_;D0_~T~t_R9}{+}ynX>1_3K@#DK6HrJoN{&+Fg5AWXm`SXYUx2z9_`}5h|=HsV_0sZv;_R|j!pB{g7{3ZwA^XB^Y_Wh@?&sl!a&Gnnj?t6~D1&ra~hx@mD8U(TYc9^|a_;CCF?dLb2_SQPTcV{;K>hKHoz(2nKyd3!E`f1?X-#ysyr%$^%X3yi(x*yqgR=yhf!8F&OHn;T2Pxj;%1~2TIn5>i35GB*Z7uZ?)>Fq5$kfpFQ{?j{Ns^zCw@t?l#F8=0^Uq%<j;(yT`R!p${TQtu7Ts>NsJm$&#Xf*q$w6@T4Eukf(&GzL;+az!K^sC;!+5hwQb)~7;+Fk6z-qMYa^X&wdEj-zmYt2}(PhXy%VMl+oy{nrmcfSMVW0pR_!JIz*%6SMms@bZ1e{-{W^XZpAZEiokyLtD|$L~{EL*Mv23V)hj4TZzy6mMJjj>4aY?R1Kv7rfd({`CLSpVHOy<sRJJe2pLu*2@<!rS=Hu&aGeIfadXoK7~DBQeQkvZ)=73NbQO^@Qrr2V{r9`$N6{>wMVuXqcdms+LPLkbMHaPfr97khX;?W$)jF4R?e9DNqYGD3-@i-kd=Y-8w7WC?{Mw*!o%M<PRTxm;YKL#E)=LQ{4OU_dUDzhJ<eml%kna##o|*MzTh7Z`8#`v?`6RYHqX6*O=hJ|Rx*iroc%jr{P^Ri+v~gUH@CNc0g0Hnx2#l}ANH~|N#`_;0}f6^bHwZ<hNo$N$T2CPPFDB3NaAksVa}U?B#yjx;z_)pxakgqy6S<ur+v|AWw;1CxwUPc<6zfTJ!Oz;+uyqQ@iHd`u5yr2)nkiC^!~qh50s;cPdP{wZBP2fQ?ew}@T(R4lt1p|6FsCJEMFADT(2mVUVP474NePm?96o1dm%6#s2>8;z-hv52A;pa#R?IyA5ESpZr`~Rl|hF~IJtT!M8G`Gq&|@ID&E$c>c8QURxW84z!$1>boc&nefv+_hweVt9(MQ$a61BTqF6h^{>Wf~68IGIdf2}yx@MOCMX^M=xc)~Ub2KX>4?3unKGS2~-oF2kJcZ2F?s|UOqZjw%QTukgUp>6R*zIqga4f`dU_Zz1frtG8*|REgA<OLNQNKJOPZEPR!bty>fCqDumjHR(Vol?ly+a-m*54xDkBjh71)lC}(0UCGmq$@P=$0D3P<L~^dnQdt*e;xd(IB6S_xE;nM!a22WwbCW%NuJNVr6lOO+&7r0gqr<0P=E5U=9*7e>~1lKONyT8xI9utdZs@pmmyM3R<slJn{7EYNkZTo)^7XbmfV>&(;rp|NiCyQ&CJSgmZln7-Tp5m*eQ|8HSl(6#ZKI&NBbXoFD*ocsc>Q=X{*z#pN>FkDK)h03tr~6})d;es^~kGRJ&>l`Zb2()yup|B;{Ne@k>k<=gDOrk`_Cn;*t-(L<Jd(8AO3Xs#5B?3~{?)}!06IpjEYz2(RtqciOelI0|cciXwi08ZV%$XEmsJ>#t_`^5jLmNuh16P-}Q`Ck5$Nb@{guP>7%&(%mG32x<At|x?fU=J_FARHIii^`Mk!A$y`Jn(DLIm3%VNw%owg6$UdK3d+C87AsAL0)7kyXn!7w<?10mB%Z2i3JYbL<FL}&W|Ja0weSjRq#Qc(=wZ35D0?xbD&V>>d3Q*E$X!7Sz6V+2nrnV4t}e|721Dke4UO<ki(jfpr<|wi{Xm`*KFl_jWfVxeC8@VICi?HPSDZ!77WS&MVZf8GGP1yd_p0%Z0-nm&IpiOUU>7R7h~yP-~p!&mrwgV%2d<5aFW~Z<U?t`5}0)N9SdW0qe^1Rg*RKu$AO%y{4fka;{NLE`)a}uUf17Ea8g-u^3qK8sW3Ogq=*ySge|#=N~7$0X~1+$Uz+>Fy&6l*S1!mhD=Q<q5-1_KpnrUK^XIRD7GBW1Rn);YgBq8tJje5wr7Y92v9(`Z<e68vD&%68_j)Vmbgi8~v#>u{Yd*g(+@rv1(T`+>#8!zibxc=iZvm@-#MFQ_R3;LsUu=kX$P%RXekFxnR;I4)&{jkSCJlfn{k*4Z5|X_GUM_Zm8*V5_jU*3Q84QHPEd2jc$aAMI0c?c=D&%>Z`CH{q$BUT-%1%gR8HFON<DLQzk-}S!BTz_ylY%$!!Q=xm{HTWzb*4j$z-+;?2j6Z1NRkC?#i@&jLKqX89m0`m@m&Z9YX22<Ddizqg92ndcO(kzAT+q(f<&h_qpZ2*fLUPL9BQzlPGO5C8sjD-qwbrNq&YQW<gy%5op&v*yvsBZygG&02ZOWjewX-8qaK|@phijgm@}6V-6ruThDjxPa)DWPz($m$A}5EYKIUqoSXFxka%V>mo6D(#1iQrs$F%Yxg>3<1uG~Uha9II8m+BCzGQbQU(X8)*$vHgXqJMOR1e6B{7zHGcF>yu5mvs<IRv;9e*L*blpR~$y-7%lfn`%;I^PyhAWPy3b%3mZpD4?wvjjX)L1G2JIG9$V|<XxTMBpqpaofFj}NGo>2wD_wb9oLM%=S7BOV7;m96z!%dNj=32^Mc2U&wtEoJnst;d0+V=e&_o9;AdNr@CzOB)i{d9=rXPDJp$o<G$;;!1w+iGijQajsru!UTKxKgRIMWafGI7pq6bCQjR>``3v-1~HR5`y)tbW%0W`@c2t*M{aCZs8x#6DBoXKDwGs}%v^CxpmPKvK)&RA}BU%p;YppYuVeqm5RT_G^+h)<C9N<CcD1=j>_QmHjdpEz>_1~bx)ATPVYc`QzLK|O=9DRSW&6{u$wsIH91&aWag`Mkjcu^>jQJl>aA_a&Gjbr1FvCS%ZOI~;!dXZ2;`56lFy#200d1IB3sCOfX;r9srwd!6ebiiNkb{=Z+0#zD&$*lK~2I#)S;<hhj;4PyQoOaX|Y@*i1ZX6sT;*r{ZL0cAkiIqnQhMdS?0qa|IlVg>rjE?i=>-H$-TD$2-g6?0lSLkWXh8sd_0xW$70iceeEWktBK0$Zy$jE~d{Ck~P1Cs^TI7sc5ES)V!;@w!tKFY6+)D)?|pqTpFKG0|M61-axCgDVtugb>#fl4)}E))foW#6`{gW{}m-{#fA9n2{k6RWJVS!;Gnv@Fpb@F?hPJ>zpD{K+F48a~9RH8rmQ(uC;{wZ{W@^?)}zla@UdA9=$n;?Q5|y+e!=p8qouj;j#qH$ATRSeQYUwvnH2!gwm&R2!qv5o@`>TKQs_p^<`f{7|Apf*)$6J642-oeM;@qH4BJS06d=?$X9-~iiyAl_5$aEN}E;eO#^}C(_FcAZyb#%?No!3fcI}PD4L1>9ZlE>&e_-OZ-$&F16!Yi!uF&f4zoQyQTy?z5>}O>uSMM@lV&@!eO?Q-W%=Kv7r_jUhgU0sY5pvZm>ufU6gF~SOVKauM=)UEDq?zN;-DMx;`x1{H4s^o7ChT;a9EylDn}yQ6_Wa_Z8v+GqYv(uk*z)%eJUpn2_3-{^d7SsgV`i>5Pw)hMhi!_0<(;0*>3k<h3Ke1)z*+mVgMvKl&LH-p#>QxRdLxCYznO1i+a<PbZLK7dj9xw5;Sj+Mz1}&dmr5;0B*-yq}vIOT9DG|O}+aSO<&e2(;H*+f{-ZjeVM=1LccRcYl~?Q4;&tmmyPP_U$dxAn3PX@S`~amQCy@biV2GDE7EL`72W5vka<cfdqT4xG?{?ciMhXvarEo?1zHZc84sF?WJjT*A}G}K4-aj6UPOd<L|6-AN=$rWN}1NOegO#$ig&e;Ru@35zBrTvNelEXLhh<7xnhx7JN5Djd5uD5z(YiHrJ%-uS4|HEn2{A10oRizooWsW>sNH_Qr>L}paQ2MVZZZYsdoHKi6C$?zJ2$Px|Bq#1-^_}Y28^;Fd}1|9>Ire##siIDb0`!yidJNZ-?~`;iHC{NFfbZ5H^YNriyo%33sqUs`^S1(R-0d!_J6A90rAhU>c61`sv|6KWx|Xs-U@$$PPlZTwqsN>n(R^?Go2{?sbzVbAbCcN>^cM4r)RqCv68y1<3>|d$x(0%w;CF5W(e*>9P`U7!e*h6i$yh9tsOKmKtRNF*{Nux$MPf57<Z{a9zz1#m8R0&FH-%FMSz9^NSY_(L0DdJ00HE_f2}^Gr+2IW!5B9UKDYruTWY1$tC7=PC<8gr6y14i>8;F<T7~TY!)KgV-|8b4M3pEVjJS$tOp|TLQMiJ55*op|2(y3Z&n5xLetLzp{Hd@3h$uXaEujevEvHaye05+QmxcUVQ`46FXnfO(l~ADNCQxVQPOO?!aLd&kq9$q+tT`_jcHhIeb$syDk6ko#6yc~t`#H;Y8{cR%#22C^wKT7kx)E*w)rin^1e$0^~MszBUM&rfpSM{p2fu=Br++kiZW*O)!ir9%tCXtC5Y2AgO@6sL?kRWo+NQwRvOQTX1BTzV^-faif3+^aYSDXevpvD>0`*IyEA7l&RgIEiji(Zz1j~S(E=WifFp3jq~8v+j?w$XoWzhI`0iDdgpYNbp9XN<vNEd&(ixbfMy5t33XsTIHGQRi?;^(3<a%@?WtIt!vk5k1u=0YlM*tQq)4^4zQlm~Ge%SDTW};o*huLblhuL{S>JKOQvYG;8K8s9hG5lqsG0fC7Bd?9U&y}^%#$@r@aEaDBX1$iE0A0R|X+>rdIvc|G6|09=-#6txuuM1vSjviMY~%Te?1F_D>C#iaoUFy^Nqd2?B{g;_dI!#$6D#b#JQFaY@YG7eCF(Sca8&0^UJS~oM14I<yknTI)^*p{n;s4K2lou2x{u>NbW$Xk`!L|mAl>VA0Nbxm8yj;d-YEiNOEwRVbxgQ;iVeAk9!7tx*JrC0rCv+(E+8<`-GMK?en#xIM=5JTUf{#iJfR5AyugmFX#vw?rMvtb87)sAtX&}nmYd&}%wjL;ZNzy|u7B8Sp-K^vral0US3A{h=(l?)KCd!=w;9Ndm>^?V<>HLsv_3m<STUfZIqMb)yTgg$fC~L(HXGfmGu9~H93Nd{|Mzo<9+$Z)cE$`nmIrYd@?2gF$MSr)b*ao9=C|JzLNDhY!;DSiA+igLCD21*NZXC=37SP}u-{oXtGWFP0VBAeA>arewkYM4fo(|<`Er}!=ASJYY!R@Fl4=okU2Cga1$4vT`rX2&7A4mA)AI$HGWV;HE;#&2sQXUL8=Qy@PUL_&JDvI{Mbh_pj)THz{UdCo5;xFKSgu!8#H6l~Amw*hr}CC0sCqXtuY;v0N=%&>+OdIZ9A+=GaXS6v<|qpm&0l4sJ_}CWA=<4(97dB7dVy0e*QTUS?R102tE%UXKm?`9bv%U8ANtt|@!6o<jhrQ>>@~fgSl=cuzAiMh<2lGI*fYc2R<|9kEhlK+R(tM-RoNB7u5$u^E~B3;xdg%bq<K}06l2pZ{=;woSv%bL)YFcnWJ2&tDfS}2Xff!i?FyL^EIfx9$0u#FPI(Lv)<QfoVy|TPdW7Pf!fm&$%rZT+x-^NNM%nejWVFKoYI6#h+tuS|ec$47D5KL?0SSYM=4+<ZKtIBm?uqS|7_lSMDUgW(m*ARsSbLf(LPZiBjH(ua#o}Ni%Zhl5mfDeJpJYTtt8#T_jNmFxlqrcxhXR~%zamqlLY?7y0=R`|TE7>%e3e`XrsmRuhPuk}lh-_r%+PeTMh;C**AVr*cs*w`Vq>bfu2K)uy|UWt>M|V)(wjY&wHCLfn9xQ^@`Zun-xM6qI(v;^98d${4V7*-ThTX$SKnbGbBBM8?`N|{R?RE8T~<8pZcq9_pAfMizFP;vknBfY!^(rfl;346bj@fflQX)?e0KW-Q!|hiPg}yYi|;7My|G4VCQ7rzI*A-r&aMLt0pv)lEue{Jibr~1){UYIc`%K4K+B=?I7Z~aWA2ZoD^Xmo>z<@w6jI^Wvz04ro_>aoj|)>{>2$e3;f)8#u40iD`oeNTnno$+M5-utxVsW}AB0167m@=DW@nr0@G>A3t_-P&(B3+JAZd(Q4IGC79qUVq+=$WmQI_K>nC_w(VCz!pDKZtpfn+jzH0JG&ypDh1GO-o%3aca4B@DXK;|71b+UdTFs`uq}1ir-QlNOLDl@wSv(q=6qRqSP}yLo*irnUqCca9l&W5;6%gFraEZUauU(cd79i8a79nNcQCiGPwK<?J2jgkiq5jF+_2*$^VM`^qpCM%AjrH?f675o31e+ry33)`KD#fD?k<EF!(pNF4%4U)(Zo%dM?c-<%v`eW_ZiEwmfOXc-trR=)Ho78B-h85T-Pvp>!lGCGd^T(h&Vmhf|Wvh*<o<X43NEHJ1CZL3%BD@Y0_$Vy;sFa-`82@W|HK%oE`I`13_W{PqjjG(rpJ4k2~x+4J|*aD$slP}Jj#s!0dF`1#YF_tK35BJ%%ELsQ*zc=LTn8i2`S&Vgo7xJ7<4CDqDcW<st&}-s1mto@*9<szpDT1bug(3NFkU}<H%Yt;f3n7`TT9_4kg-=>?uW$>kMdf2Q`w)ClG0|j+O_M8KRsP)4CRkw<qH=sGc3LaaD$({>-rT(Z={RK!0fp`MiU<+RO0{(;h5?W1(0ht%c(g#3dvh>o00Bh3<Q`eGq_A%_3*?F}6r^5pnOzVo>!vGk46)#a|227xr=uBn)>g91zpAW$iEw|2w60l9w2nYr6O{)R50_OnRIp6AuI%K7v80#jHm@TvMqHn08OHWba=GeI7R1s_MHv8qvRlUB>^06W+oyn=qwq1HR;M408^LI~e21%>WT@d`fo5XrZpFSMp3plf0<?g?bb+$gh170Dqcl9Bp3T}AjeKajGMRs(&oPu>rX5k4jagz4o{<xb8&idpoeh$PY-JGEPM&&eOM0AR1<+QjOxCIsrV{N%mOi<aF&)W4ogW$O@NTj4Qdi%A6!eTuM^FHkXK@?_%|frRHtwci(T(5f8yx3VD9ZrMgTT|#cw%+D)C67wCW)f=#jqx>${&`1QH6wE3)DjJX<>&@B9u(lnV66wU}}g$hjV_u&@v@a3}Htig^nBAk1Ub#;gpTjH)zMweUf6?#!sasq9@WNZV;YVSo|z#R2l>k2%%L!D9yi}Rf;nQyuhWhOemrw*hMxebE!5+TEavgl=rPgUpTGOSV*)iyXX?B8cmeU-?@p$K@touTeGaoRKqE(nrUS}(Fce|Xx1{BCgY@=aK7Df%G`mF1D-b+#L~UL$!Rfd`JUyjps9OyM)l#JP5ZOKU}wo$G59}40&T+EsAg9NER@X&$vxN=%?te&q>r#_E~tph^z8;WH-c*9=^G<NG<l~Mg|EBYsjMGML9qr(re;ooBk9vLEUXylznyofx|^;m1H^Nmrsun)+_HWd^G;VC_ziL1W+#fuaXjnHQ^+3O$y#?4<kV<3R3K&+1a*unXJpN~^jI7EZ*_nf1E$x(2(0ZTr?5=aMRzLmp10?w=o)Qs`_j9DQYFX^u-L78=S~ve^(xdcOGE%-UdCmHV?tw2{Our%Z}>2|=Tb^%QD8uZ>}EI(!J!|*+$)Tp@5Gt{&qYpOzer$8Udz<GdfQ6KXOJtS4-4|;*;UCz9xBjPpJW;B&V?{|<Qmh3o(yy|#1`7mwkERp7yiSBiMN*t+MKe|15!;|_M<mWa(ysI049~dXoZkSb5XE{TP~)vqpZ@EB8WjA=td*3kD#DhD}M%HG$$j0Q_gw~Iy}*@ez}tB5jyMgvwM0hKa&JjB#i0y^DmRI+Ua!jSfxHMv<8kuuQ)%HNgF!<kVe*)@NK1yv4rZxG0c&-Y2k5RfsLb~PN}lZdM+;K8w=jV)JU1XO~pM=lp1mijCpd%FCv*Tw+((6-~y;j1Wf}MdeKqtJnSykWF@L(Ll1(ZG)WtnW2OLSF02bR2vefb(7nmwyV7<ntL0<Wb86BY>J#d*WO58uaP8m^O8R!l_m4>vvoTM33g*Q1{(0D_$x*G3K4C7-g!odfni&v5e8xKcqzi~VW;3teH(Fd~IXF<(w9rOgBSM?`W|S|z6jr1CQ0?`)Y!@SRWRt$~h#j-~Itw-Rk#@;?q)2&vi6c<3KYF-nq=zv`hmU1}`RK|hbu*u^r*Ka*lc4M|t1C-^ar9!(8MA?mOY_siV?Cb$tKJgUsjBqIs9SVAV`8?6yiP^!wy9>5Cs>Gz5Ju3odNd!Wjz;qsnP5$d4!O+0Aumo6ai2`{CT1)gF-$ke2j$x5CJ!MYj)t5H3pQzmtrQ3gtm$rNLDlxVGBb!*mnl!kZh=l)=~`r5hOqDzjP8tbv$%{c>3TRLR1Jplk1Ih?MXP}!8kMJLG#?RK#N9Ya75i00k(X&boTYinm0`I6dB3|=8L6EV8QtF0l!IN_$}|jO9Tm+cVpeS>_x2LuPFl@3wMM;6%nWY(Hj*kJt1B(yqhf6}Cr}~*@Bm+8<LE6y?uSQn)S>g-N#`j#rf_EW|El&;-e}kbxR+==7=6PaZY&$Fno=oD$xSCcsc>x-cM}|es1IE02_E+sC>kJv4-QZC3au~QYHEI%nh6n>s6=XhA;5-2pc%9ZFNI3C0#L-@e_yX!8cSDZM=4yfmQVxO9k382a14GsuwkBDX{MtNzb~XK<JlOq5o}8@Q!h0;hU1hZQxHYWRB>VATu-|v>)Di$NYC%*@NZsc(q>oj09(IiNTI)9MHkxVp~K1feF?f$TJgkq$JBFaX$NY@YP(5&3FHc_`Oa!q+h`#o`T&ggOd`3&)+?}#nOIZ;W?l$E1mU>Z$~qF~%^tpe)n|z`HUzwKC-HzzpYy7`7UyjBRNHdZoyAlTTOoVA_sxpD&2_|z!JgZzGI@n&p9~UUluH|OE5sX~!R3l2O>x3hB!@Glj8?CCCeSI*ZIV%uZzg&(c4;kUwVMjvSi!k=5tIv@pNa7(QGyDDfFa~V=SgZJE;va`3k?XfZ~1`iMMZ_1=5t{ZJ#rrkGQZ`tBO>^Qixm)IB)Qvg8#I^W!d0XO2scL!h0uNty=J!2OR!T~$8!wrY@14hy@<!aHSM6W!OKE+aiakkA>EoOsauHM&uM(c<Vn0{XjEgk()Nm^Usw~5fdq%SzYmA=UChc{yfAoOs@W4y8$2TjMn+s_*HvB`epb#7)@VxE6|TG$EO#;MmBRaYpKYUKm2>ghFW!ybdX%~|G)*AKY%~+|$r)xWJyBrLQmbZeyL)?O>-JPqx)m*I#(kIKah((m6WDdLjE<_SgVLYDj4<5A0;`P>`lVt{v#VHeFTFO{Tr2^KuH~`q!=z1!qd=BHw8KF{LbN+gHbWEEl9eLU-Pd46pLg7uMhDQ4H0r;y7soRcWk<Vd9x@+5+m!VmHdPYmr+PpsmmDZ4KqUoeK69pm(g5>}=a<NP`rVg24Uy5NcnYLy^(ztrXdUpRyry;olg;|NsfPZ_iT2h&Evi5oj~GQE8@&(|oR}Rev~RnG)ksqf6I6X^8@hP7#ynA}7g7QH!d4AXXmRwB>7sH$Fuf*ANv{(iUqseHZH=6`t@n$-eR}P;^<H0{5*YG~NE_(FQqVvphJH?g78erewP2nA7$D#o)&5lBGHO32y=6MgEs+QG0Gw&tDIaUolQI$FuWmzD;a+vyR}|tnQYm1Gr2^TYu*#YU4xnh_Zete<d>Wln#pHMK9lrSIfTRh4TU)&Vgc2;PrHx2YDvNrJiagl@9n26WBqEovI)c!b%3q@7Wdi7yP~W5~$bzTa0Y(A!@F2<PaqL(Wn;g7H9^X|Z)GH9SAg+St1Uh+q1g@vZj;3ldjsJ$k(A2slVio*NTjOJM&zPu8j}oZ0qK3<!UfxA0FJBDz?xB$}K`q3;miE0PKsVm)ni!bpBt|53Xq^t&fkotOY>}i{!w53u3zNa6mRmqrN(dA1xU6>_kyc5H_|K3fII44B06mlp{&7V`VGraaVC)Ny^HS{adMHIe#q7O)e)%CbXNYhg*wEZ8c$?mR<#mM^t`o@?Ga#q$i}@(5LBqh3wahzmx+Z>AL{V1;$fqE?2$+>$-4}?P?5c6)edhEy!oUe0!WaUSOdOFq>al5=&T^`Kc2IN*@tb-l-tOyosNYqJsQ@S>qcIl6SHQMlT&B<f7`5hu43n}&-*_79BJ=W9-Pg4P?k#CPKtnHKGr9CcBNZND!Oi1$8*0rlK>QCytW}MP2!z}@l3m>twe(UYc(SXURSM^xa?-fWI1jiBeKtkdx^cA?K)CHG0Z}(;U13ggJ2iB!qt{xUVSOzZl3W3l%&t}w{-2#yg!{oNN%Tli1mTLRA&Y&Lp|^GvW_FfSk3ADH2tkn}e(>nkEg^HZ1+QKeJLy~&;!0nPdUjo&pU17nY8u~PwZULzuu{kyyT8Z>QE%^*(`(U`ef)GS>+4f=S`2`U9nZ?C(~lk~HPiY~qOy4#*+$S=FUgb(+6T>zcVrXDICghA^Ph4TPi9dst%ENXO^9wbH`L;VjLM1@kjcBbv(ZJ<`V7g8eAOB)kt!#@>d`rO=uMM6##$xL{ZP{kdiF8=VTj+8AwY|}(~rSyAz5h*`D_OJe>{f!{{=Nw8mI'
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
    "STRAWBERRY": 2.5, "MELON": 3.6, "MILK": 2.0, "WOOL": 3.2,
    "EGG": 1.5, "TOMATO": 1.3, "CARROT": 1.0, "WHEAT": 1.0,
    "FERTILIZER": 1.0,
}

_WEED_STATE = {0: {}, 1: {}}

# ── NPC demand data ────────────────────────────────────────────────────────────
# Town center consumes 1 of each product (excl. FERTILIZER) per 24 turns (flat).
# v1.33: removed 2×/4× day ramp; interval changed from 12t to 24t.
# Shops each consume their products every 4 turns when unlocked (drawn with replacement).
_TC_BASE_PER_4 = 1.0 / 6.0  # 1 unit per 24 turns expressed as per-4-turn rate

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
    tc = _TC_BASE_PER_4  # flat rate — no day-based multiplier (removed in v1.33)
    # Shop component — sum over unlocked shops
    if obs is not None:
        town = _get(obs, "town", {}) or {}
        unlocked = list(_get(town, "unlocked_shops", []) or [])
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
        _detect_opponent_sells(obs, step)
        action   = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), _ACTIONS, step)
        action   = _safe_market(obs, action)
        action   = _premium_shift(obs, action, step, thresh=thresh)
        action   = _safe_market(obs, action)
        exposure = _opponent_exposure(obs)
        action   = _impact_slots(obs, action, opponent_exposure=exposure)
        action   = _price_gate_sells(obs, action)
        action   = _merge_sells(action)
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
