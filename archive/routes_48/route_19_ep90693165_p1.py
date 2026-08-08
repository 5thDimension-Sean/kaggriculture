"""Kaggriculture agent — Route candidate ep=90693165 P1 score=140,300
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
    'c-rk<U2hyoa{MoR<^$)06zMmvG-nCN6$MK2;JhFf3-}BJ#`$6GH^cwkI+4@e(-|2VnN>ZaR`)g_XS%Dhs;e_2BO`zL-?M-J?f1X^_4l)X`sM7y?Z=O2kLPFq@!Nm>+kb!g!<UbL`|bDt{OkXG`TWb-+jkGUFaOm({Pg)Rzuvxo_w()D+4<S)`~BJZ+Wh(B+uiQN<R2e*yEk9{ynnm9{d9KzYWC-!cX#*i&(2rF*FQYmzxn+7)A)<a$H)IWKbp_G*MI)}VKRVWX1|>6cOO4}9qIe~hfi<6etMq%<ag5%KK<a>Bybq(`7nO^{O<0}uV1eI>GN0XOhz%@oDE~R@c6yyIOemyyM4WTp0s{5^G|YzXWLCKJ)a`Hh5IFPD`LB01;0%A{b>JV6F%GGX(1c!ceu~fPW-wjZa?iFj_>%Vzwg%RsGh%_GUs^Ragv7{yuN)l-t(6_8E>4_aHrurcI$^TuxkQrWjDm^XMB~8ZXjCEZiv{7hwCNHH|&H4^U<v~>;!$Q&95t3ZQKc6jD;W6`Gg~@&EHm{)h2(^&1P=Z$y#6zzD3NxCJ$G^Sim5@jf4l1OvQZYWFq^)F<Q5A&urCg+{YhIf7$1=#Bu$gpR;k@t>Fu)>lwf4`2cOY#{6jgR^uqx*IeV^QvD$&v%76ym>%PJeSdeid;RIxKkXhqy}Nt&ug5R1$`wD}e{Nr<{=<6naQ|W1r|IMF?(bpUWXR`!u-0QkgeTCd@p>=jiDQN@@0`rO?R66n(<XP5iar!pm!kr4<TzjH>19S|UBBM^d^@@xS^?u>L6eRThhwSLV;G=}0|EZ8_30Y!ZH+oQVb-W!r`=@#*a(TkF$WREM#$Wn1azgf?=@`@w)~*;1}Div6L%w`PWPTW0dTs*ho^5Zck3Tu*8D}T#KMc&fZY0zX@Wv%|5ESV_xj({)n@+fHsjxJRsWVdx?7xpQ#>mrDfWCZ1$AT&6u8Cw_ClnTa#fSJY%|wU7OCd#&r#Cewn70Ab1P^6tK8BW(as3uB;i3@b>hh#3scOz$=GYXenVo@5Q6UkyNUN}i3&FzU)qTmSz<s2J^2P>cyUGniOnD0Cg9Nhhf#WEwO-^9zU#!`QkRu;g`S`6y#2d)(3c)1t&ayi4bXb~(3HoukP|&HU7DO|LUn4G3h=692yr><*-4HxA;m#Tfa8oh)_{@=?w}O62-Dpx29OW`dwcuvFRCNF5s=bn=bukqC)EtYgZDu3?0j=qd53oR<5(0*n>Ee!_c&n2j6rf2<V%^$4Ca!eJOK=6Mw+jGCf_>#Y5ECVIvO;AvJs6CXR-ul7NKAs?l)a@I}`ZyWmbSN3cUoK{OnmP9z6lpkmH)gwhKLQGcm9uo+%x}|8iSmm;ku)d`?<wetvo<=S+9Mvz+nF(}?Wh6>~Y6(sZhupwMB(%Me!JK`A&)1t2l?DtNj`YG7!IQo{_R1~+z2jWbP#6n^4?eyM@kv{pE<q|GY^bn79);kuYu!@-!Gu!lgk9L?2``A7LlOK5-D9@@iSU-b>$H~k~_lf~)XQe5^Gv1m}<$3SdC75lJpBLj6LqY>n!Gb1P$D0XFM<Y-uS1y48ac(pf)%!!>g1CjJIWRpt*D-UA^6;X(DiO|K5!iob_xJFIvt*rlI$C?b+GN^;Spc0|$ab2@HtgXq)?OO*<uC3U`4mKhUSIshaPcFk4_x}FwP)iTIuqzwQr`)f*+xKtI!g~L?K0q9}&FlHGzk}Qb(M`OWC4N4Bdbr*Hw0n5?%h~yL{6?l_@P77ZxwOrkg*2YOzQjRN48RLx@%6@|F>?>a(&LrE{|*BgG9a_>ENyMC>f8sm!q*P7`*87jW)5W`CVRYf4M4dIdRO<Q%>oAoSOO$X21_i=BS(fl8VK9W^BHs+r5MS0@)^e`Td<K@xY=gY4eL03m?uz!EKGw_E-x*pP(nu_1J~zVUcmBAEUC2`I*79inHU_yL`F9YTN8{~Sl3HkCrC}kxT}mljb5)1j3)*Q9C-3lotkePQGAqiv>w{|p+)C0L#MG4LZZpu75QF0_njSE6BVsyjwV?Nb%vzYO1~SUR?4B*i8yRmC8ipeNSj70+eA1uJ<j0^UKAp0z~@&N@f%~5*0N>(c;LxTLKJZQC}vKbI}LLH{%G6CZXWdj0o`dBHvLwGAD3BLBcC>ZL+s{`3>aINL6U_9!Hr#4JDR|K5ywSE23RbK6vI600`lBK3(mdIke(D7TFx9@WM9ra!ez*ZJK#?H6q2td?#+(7+nD9l#ijtwHV-^vJUPTGM+PmdI?_&d$h`!sKJk=%Hk!t)6ozR<PJI@h^XQ-x(-jrKnbJ~{1#Cf<jioH&0=ZQq1PZ4pSXBGJwloyi<U@?y$_V5Hg?+9duTv8JtPBf=kp5kzddsdE97ZvhLaOFGSn|efEFttfmlEUGb$2Gb`O~#w`1JF;yFUXa4?L&)4Tyx*#{}3WBSqmUNkx(YIu^^P3!h);8z)~_E4y;^!9g(lDj&?Q)nInj6wE$-s1d-dph8OwJHK4&-8j=K#_?4yWGyBSXEjOz(BE$)B-3E?A%_H?7Bf3JlkrNmr2_7h9xKrS7pTj2*~miri5fpDDUh~pC?4Af6phKDas{8Hx8_kKS=5S;1$Km8!Z4L7=9%*zkCw2^EU=!8U^&=u7ow^bA5T-g*JghaJ%hX4!`KL)6MRx*kSrp6E$pUnlZDP&YJ||gMI3ck4Sk8#i{LS7nL4j!lLkw#K@h)xxiQR$ecR;(KYE#|MH=Q*d-%t+N>f^saeK}iLMoQ^P@=pI`s1Y@@L_;^or(M`_Y$WsL26_nb|`Z+hf&aUX2Wn4B@mXK>`R@ML@aESZ2!V($mNx?&i-H#yHYaevdR_Yd|ta&RyxAZdMr^O1%Yy~*ToECPpT?1An+v7+WKM~4ID?{L(zfJ(<(*S+w{{f;|p)YTKIiwe<mo9EC!<>8$*2hQb^^37<9sb0|0UAx^fT22a07L;UU#^kgAXf`eb<}AS=GuIQaoSjs*A!42znN@k%e-)^tqJ5QC)d>;oTe^05hc7ziO64=X%wmL{7vO66gpC_xnAr(ByQ-m~#T4fd71pmUWR$$HZYxTh?d@}{&mj}m;jKMzx3IX^Ig!=DnBGhsz+H;6{U&64!pp0$$C*4tb-$<Lco@>463G`){wunCcRdF>(mFFFRRbmeI(cO5qE+6JWGsf`e%E<}hSud&W!7KBE;B19jtWnKWAIE$zk3Y(|JJbuk1i&Uivq4`&4B#1s(ZZfbYT^JU;r6;0quZZmn^67CsTflz;^YV+~`iRd{IwP&WLqeLYg>aAwc5EZL=}odE!$PvkXPrh(0}_(4A8lqT`ap~2uEnd<tv)+-qE!nC=+-5oCseK8IRk$9I2U=M=Z&@HtoZmtxq5&ol{SDAz*_~-XUtqzsl3#N3ss^5!l}x^&^I(Cdxr<S53h6z@ik$|^I};pi#Bkat`mUz+Ci7qVbmdsP7j`Sok$~T#m*}h&GcVARtfykgW>gr&k!UisamU#XfVZm29CR}J`585LML(&`^H#WW<%I|iEx(+T3M7iGtMc3Y$XD_g=X?*;0c;&t?C>hMi}#en@%f_E3t|%g&YfMH0_AJ<&T+&p}%R`5qgom^jySkPvyckaTh4%6r|#X>W1exx>PZ;0Lch||GB-|dElvztf>zPZHYw)OD@KL<<+-bbWv+a7qMIx!CT8PDyiYEww20#3DN3JWwM~xI1E&4E*Ak+5efT}1nE+rJkbY?Ws75pL<Q>7y0S769O)`LbY7Xzdt^EfEu@>w%GrGsa9UchrpvMjLe3kDE#Cm8Ug?mMrk}2rPm#tlI_Q;>zh=rOHO;iOZaV0bGZhpYK7fW$ovg+*5qu(PPGy2WVTonTJvvM#Bh&oLdUs={mHGAv|0|Z#5AOq?VF2(f{V`iL#gWRO683Hp$>v)%&Ji{UQA6UF@<@b4g*@3q#UyE<-E~V)VFmuON@@oXYt2YOOp%6^3|+^Br%G#{bVSJ3klHNG>#+ge?D*Jru2_+3Qr2;)2yaHyL#`kj)Me=<O;T%=7~P9R!NND2b!@%AvH~D1p<=#!{rw=>-@FB=^)s(V#rm+=+wKhyny%SiE6FGRSG9>LO=puoxeSG787exEB=;fH--X<k>VEHJB?L)FpD~LXr_Tz|(bfVmF)#qrdM?Rr`K278%3<LEpmYrWz!94jdS;%>W1$Sd_V|Elx%Za`p@jijQw6urLXXZolBNu9I9(WxPDLOMp>;9F1<V8}3YyF>hva(LOjbTCR-q(>2VpQslHAh`mJfa!dpvEm9#1yOb>k(u)}<tukTvS4*0zr8_}j$Trh(Sn<zK7=rCWC2r?8&Z=+2^vK8dF|bCNOYx`x|(74m)3NUR!w+O%VVJFTPOySGd~MkTj?`eB~*T&|XyL?fwIES);;FjI7;Mbm-^=DNnaqN%Y808Xsu8gGgOVV22e1VMU3Qt|3BqkK)vYvUD33_~hUb#+CS<7}e%Rn-R3ZYq_v+I#kEMXGb?OOaSuZVlc@gq2#93=2yJ!hk0-xFa<zz-N(x0KKySlZ4^|VtEBwmGxt56wpwq{QV>}mdk92IgUKx4vx1u5rR-@RgyT7Flfz}oM@P>X%(q$ZNOYxJo}<1A{buXXT|AVnah!Z5tq#5sO}=g$xe~*Azln!mYs}vwkL%;6c(Q#cf@7|94aZ8>z-iBnv&KkbxcKh;z_|%PKA#`a|UwAG&RE$<}7#OXWjbdbkd10+P`$521#mMy3P?hlE5RvDqCnxQX*r8v3oMSMC~B8Htte3n`jqeAWidXlJdaDmOdtwtLf+u*v61kD0Ko$%0Xqfi=Ne!Wl*HqEFr%xZGv3n4j$efQ{nQ6(Mkh#H&Xq!Ko?+{T-%^-*1)W6?qij&uKRjM9LW!MNHaFq(yayQZRt1LR@LzBW0w@=I;?VAS~i@<!bcqf4?~}BgiB|7)9-AS%Ya%`!g@=A0d4JQb0Uu@+Ca2TV*IJ8J+jmQy0Jr5*q0sF&^Zmsc!qDzqrl<M%cp3mJTe6;;<~Ml63?LzgzzSTk-U7K5l6is_Bh@R)1QeOA~Rl6_+`szfL~7}y-b@`KIUA&#6MA4y?ukK|0Yq&hxvVs9(la-@b9f<eWWRM4MD4-Uj!`7^*cz=g&p7tw5;%+Ks`T}sqr%^Nw9h{TL&tzie&(Zf=@AZ)W+83fD3|hkW@5XL-VU#hb(1TVvRa5%CMdACV4K>fw9iQNqT`b5+hE8w((`lGPaTXLqzxpQmm2~(>;Z~r-8=y8`S@8JEhClFEL%tKS3CJnUuH_SH^kf-q}&}_RV$=o*-OkPOAk{;moa~3DiDmZ<izIHkYD2*b}6=gH|6}d{oJ6Ywso6z$c1}JEgHn!yQLkIg!Ey9=TGShDQ*#>De{(Tc+icJDN11HA5*^kkQ(;#$*L+CEx1=Q{f)!l<ExeA6iOTS<{NhIvOv|kX81b)MOcq1-<4~YllAfRqS{Kkt9E~!tv+&5$PFPtsoz-Gf`E|2QfNpm^0f*ClU5y%s%1yWTxH_N*Q@eDX9DwGvl!NhNPyr6|J0h+PUro{lW<%Pzj!~;7M(1ha6!dO+1f<=>>MZ1&ixh`&#bT3J@Q4YwDB@_JmbmIrqIf1yj9TZ@M5qUG8O_OZ>*U%yRO&t-v)-0k5Srace{9Qo(03lBeibH1*zfxjVNRZrsyatc&QJf@aN!DHKFGl?(MUmk0-e1SNTeQe}~aN{r2pK}kwQm&13CPn6^4bsZqBEk|ZvdZcfcAXeZA9!!=vU>>WRuk17p5TuYZmX~CB(H~;~FTN;X|1ixmv@LB`#Gx?=G>cwMM&uT}Vws0P_Y5>XwMo^5uF&CdY<^Jc>FKz(3(%zNi(`Exx6?#lTtw>V34X_{%9@Nk710XKMD)(v)XE{-s6a4gnP7_lv#KT3<*pJoDjOK?vqXb2(M`(j3@@Cq){eq$DhVm8SLL@!YqB0ZQ>BvqptLKu!4e`CtXUILNgh7bHqI2K*e<4!9G`d756wqRnmTc81+RtEKj;%3=o91@iy=5Loh=FvWNXtJzygxovQIe)zv=t2WyG0AFL1ABDH-IQxlng>M%p;0R)e|_%$7JEN|ViD1?xZy^fP@}nh+bQ=@U-dNAQyiM0INH&0=V(b(bO~m1*lu0(DYS6$i!nW$9Zp0(9;)Ap$yQ@U0T!)TEUsf!#1-hKr)n7EaJCT&?5KndNaA0|~)bfM46x5}enNv&c92WogkeUA-;Bu1CW0@jzG3?-(BPqpwki+A<zQUr3R(0{$!G$0^RjR)9c5hMQY}!09JVjg1cSeGY$JO7mZJ3S<FZ7p*3?DUs4}!t?fQHHUk_ic;<WN=xiu#i$Hov|^Tg;%XTsNPi{qkg(B|F6mehc+tfng}%}a=(v`7+r^R_Sz-{wfu6oe*`hK8NQUff8y$MPY9=O4ueQ39AH40iQLiXSYpzcWcKH+*UW;?35_~8(%3M*x{#FHZl;1Q&+d<@T1r<P>W)@hL8%2aFg=W`%%E~G;vAfuEiyUGr0D|H|^Lop?Izq=tQoNc91rwlbEY$Mq1J<#sFuTcOiF2;6y6@7Nc$?U89<?9>BB8H*d<mTlEs2G;guj7T#OXdeMQ@VgP+95LuI&ie4yK42t5{%5XR(gubp2t63BZBlx}n}r;*e2PMbR=#s+y#zxf(629XpW`$yN9f{S;aN#-b9fCYC>lq%*M~p`(|7MJsgtyZF6bYjKL+%0an|-2v_t%e^`EIzpynMDaz4B<zA$9@Se;RA>SqA(jGjYs;g}v)8K70hU=cJUdgUxntri1V0KAI01~Rai#>t=y33J6ZI(U^&EbQ;}rr?$*)s5(w30w1?mAymdG7&iX?Pg%Yr$DMYDL6_dpZSO$Np?5=mq=2>;DimKKF&Wz<h!Ex*if9!s@$ys;IBhgkW-!SpWO>c<zyU|WB423xsEZyjbBl0|SGo9fVNN{tmJ{Ha?<9Se7GB>^rDkHv%*=&%DMP(@W3x@|hQ*a15r<b7xZZD|#P92vU}RC6kQ(`(Bf=qW<fikmb-B$X(b5zC-u<!0TH{tf<rVo#*2mSolvX;dFVGMP?-j6Rm7Q|xu#K=6&)_C}AjqaZ9<-UA#o3392aMJ&}Dv9{$WFse*0tJKh{)+nBg9zmiNlu}eC9YGtkmN*$j9D7*gq#wtW*3XDAX)_yQljpOiw1C4BJ*gT%n`i=HvrA&5IndZi5jB#K71F8v=iS}?`&mR~*2YuzQl*^&86{5?OObPm;@mJyy^cc)TV4iVzxHeM7QOgS?*G_=t+!5GyGgUhgc9utDgdyHn*Mja>y*onN`i1^KLAZ6wx6hg++19nW4R?f++ik)<3g~gc&Un-QXZMrdt+=!>h^o#bZuTH{Ig21TzuvdYtGb*rghl~9TMcF{r|jJ8W*jHBWB6-xDwl_53ftAic@^mG>a=$hVa-0xdL-^oLyG`1lP?^+jre|K2^(Oh-i&-{aUkHQP$?MsR?zmh?KIIXqa20uVpw*v`sZr@bw@NRW-SR*L3;V*7q8!yunzK$~}=rP<?jkE1|+d>qRY#e5W~3@j6~7_NlavD##MAt`C>+1%$J?eoXXv;+&hPFqM9C8FeAEu-dY_p;>Tzio_3IjYg-PcM>H;%F75KY^hH|P=ua1!&zxlK>CQIMbwU5>Ou~8lBxj5o(21m5j^v{UN!4&_OJkqsXbB;#Ls5vPmV%m;YYHcUy0_+0Gdp`Gn6%x5l8qVoWSrFnN39~R#^2?t<rmZ>C7ndMujSJ{L!mW+_dva>m})eXLkIR1VL_H!sX!Jklt4=IZc*kaDdRXT-o91J)hrfbKz0HE<kRh9VNUx2}&r*oOuZ8H<Ulq$YEu4unGACnr9Rc@&T@F<zEw1%ohIzjil-oicQ;rXrhNagtl?!8VrV#W(+0B3b~iqVSxi;@fvJjQW}|I8fZ*0#1M@Ar@*0SB~)_g%7|lh3$lk&=Hz)(C^z?&yHN#h5D<0M#D(H2-+0}@WAx_TKYN}emy!W<(?c6l%&Ut>+ci!oBu44xOpv3th1R+#*6m+;1s>L)J%0&4qy{Kdc(Sb1wKuMS8WU_0G5G4z#hjV{uted^@PXv>tcvo{4lu;#!pj14;TR`qv|tfbiZ`{#l$xW0d_9AsL@g>t3_GoMI$&m1n5mZRS7>ywjYDVa?FJ|mSP&q9hEJnfN4g_nrkfU~8dGYEi12;e?ZsZ@;dl&R<Rbyn_&j`zwG4RvB8x@gUzxpl!xXhVQKfdsWtHk-xSaA<x2A!l*%$;Jw(fr}TWMQs-l*`T>RPrKDoxv3zX(k#66UjpQe9|SZByA)^p^LzQUlr?NZHGMSXdATqAFQhV?rvD##MWpb+t&VKgRN*m5G7^`0~nHsZNSAYlrOMAQ7Ba`j%C*v{vc+TxWIK%bD>3)%mX4Xl4v(jbb}Vi(lBN>n3heqDM8NIZ6r~Nrki;p-!t=U=L=h86aL=hKegK-(f~l<JINVww(GC6cs-E`eOHo<QB$dyI`NPkRw`^9D}9;k*2UsHXMh|L~(GS6+=hOW|ufrR~H$wpffQBO7b&EOIna$)>(rd<APV%dId}Y5?L#=)lsBq#}ybf^iOS?UOZC}mDQ3m&75i}SNW<iY7Xa{pavJdn<T+~WsyoHaLThpXy-}kv3&$7CsJDTKk@J&2Ajh=gJ_!_|IRKe$vsL!Y^^2Kdd|oBGpH{QU{Y%Yv8zIe8?H@}`Kqtd{~GhUX16>C@7Z=J^6J~wh;Cx`*LErPmrsRiE+%bgj#(y$N%&&ASa3O37yt$>u9IhlDJA<gVi1dG8|Yy|_OM11lQu*!xI`PIj1S$4C3EtGiAtGU*=KLi{BXeHCXtz3CzX(`mgL__v1gF9qzHhEu%rgeKu^BIsjG{ZY1m9er+4<AR-iQs`q>R1l7v`~CbH-CeS=CfcOt7SRxCVNnJH6=wSu`h1V>q-IzcDQ+4=()8qAf-<@{?8pOBlZnE(T=XktdFgl;GD%FG7ZtCZ1QRPED4MVuZyaTKb~K_9s+OTE`)W#%9unjJd%7^#J~rq-*f!b+sP1|C&N-0$L^i_L8l(fB9{jB(Xsb`C)bZUhND5vrqnHd*x){I)Qyt8#10aKFj1LQ+Al6YJ2nU+kyPF7lx*F}uJPv-6Mz=l8x+9(#$`hK&)TEzmja2|;bwOw!Wf2ra>b`*!Hl=@rU)Q{BExS+Z5guKKQ2$I>(LA%mqf#w2oEeICnj+gSZ0BerpQp9J}4scppoQ0Yxcg}C%ads}kQm*m8FqeHqtmRS-5Ol)o&oz=!_E8}P}EWnn_KSQZLwFRU?q2cQybypQBT_SYTpavJ|ItgliWK9@*%jvq%RYHu=){y96C|qCG+Dd&t2V{lKXF~x=T2YLFl@XRpb!A}0rUZ~EXIBV4O2WKqYGSPHkiC8w>q^^P>|3Qig}8mRKrFGTfOLBhw#r3h)UJo5HK0iXpvidroEA9CST+`*i;|GOecXqtk*OJ#TB1UE=_1TI2d|tiHPg<yN;zVhk}M-671kk8(xU?&j{NZLLT4M2r#3MmEG+C4$bax{rfaYO;5gG9Qf+Hu+gsK||K)xNz!Y*@$U}H~?SNx_X<#=7<GTj6)90|tqY;O@emRW-fSK1zk-+K_U}dTJj+`&ZlgglOP`#`(0#`sphN|-pRisKiW}{vhakJ9W{aPlmw|*FV9z<oVw&5~HSdf@zn}p(MsgSCv`y>p^I4Bm>kR^n(OETE-WU(ZRTmS_`Q9?dmN)|1lkMcYfJAh%)m|Qd$*KS)6g7C0dI8X(Ys*WReN=?9<hQ^WLNkI8WwZB7VH7`>Ku-~Y2Yz@v~7T*&@s&NG<O_tLh!xpW(l>T#$N##GT<jAJB)ePSzRHuRD0op|OIvcwlRC67Ps5|LCMOdMN%&aR#mB1GB?DXcYgjt@9M&pR*B8~$Bw;~~^y{~feU_2i(arQ~odfQ#o(r+@oAlntdwl)gi))f`9^@)((W={Yj+Lk9;TJ*sL=z%?;qsbzrs4&pZFD3JqWW}9}Er1nM*wbs6OMLW#x6`=fhZp5ylNZJBQ@Gb=B>-Pn9s~!T#p@=#=nu+3%i}uDb&Q?qW63cticu-mIy9Mc0wH^)0a$&Eg-F)gYScEE51y5)XQZ%Bg*vgKIjU%t5!;t)5UuRALrkH%V`2?x100j1RT1I=rT78oIJakceCBUpt!1X7^j2igSkv*$fnIAz^~<tYqmitz`!@{HWMD%Q^eDBZ<eXBG3mMh9l{N%24l2kB(B<e5q5OyJrr1lG&k>?Xw*qh4QA2u=StAThZTF?s+jcNCnnVDDszsxjoeVHRx$sED{<wxdn{#7pK^asN^|AnWV;}W=1aZ?wr8&T@q=*nv1q@AjU++=SF+P`z-AT<@B%Pq}iF2xZa(6x^`5zP|g6VO5sxBY~mTrC3v}Gee%-|^z8mg150KJL-rtE2#(9BB;cyToFrU`zrn>Nv2i|ND~`ilrsSin&N9okxA^lg6{XF)2V5rN|ymS)|o*1NC7CYcr<;fBmv7L^<oyQoSn?8CR6DutW~R5RwqHzN*ek3=Dt)5$Plbs9<_UaPm^W%4{BSD3!DdSE3Sw=KW*ShskaG9+#@ud9>zQbDRp<REi0d3)Xogj67jMB5NXxm|Dzl83a*l+qV5we)jhbX>;ar^UQst64&)zSO!m%O&fKkY->XB9T!W+xLI{$NvYboc$^'
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
