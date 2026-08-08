"""Kaggriculture agent — Route candidate ep=90637595 P1 score=146,106
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
    'c-rk<O>bM-4gD`(YY|C~lXT}MuZ>Yp9N12U>A)Ba&=v)Xb}{X)=zp)rk)@|c^6-$n_epVQ6-AcxczM70ad`N{f6o5;)6f6-%g<-O`QhyI<=x%c!{Y33KmGI1|9X7m@#Q~$`uXpF`S;`NAI?5r-42g`<zD>u%lAKCe!BYZ^7?FX_WovbwpfX`?>-L0=g}YThT+5G+nbNW<^9>>&E)OxhU=S8XN%?T<DYMDK74t9zyHSThll?z4#so!{tsV1@1L|BjqQiC&2V@BB<rV}+xw4CuXb-uUK}doZn(bQKXqw7b@zesQ+IzIE9L6?!;g>3zyGq;9w&#Y1R>7$Co~cEYOx=g(*bzs_ABfDBcJ~INSghWE0aHcYy9l#Twh<lA9k8Nc!V6A_E7N(JnVPl{c)(=tr)+osb7BU@&BLhcY8*EC-UU?ms15!WO-E8<^6CwdG-9z{ih~kAk9wBqMZ<9$%o53<LRMa-v6Lf)9w+w7k4*b9CgVjC<}cj@$QG)s%yF?nrlrg0V%)o%&#wU6Tg=i%~(Zg^7t7Y1|@B6R}C}Gi}9xu`a+9MZq7D}n;wK6G)SyB`3|^7GV2bhFLN$z-x<ldf5&=M?g5Ijc7K{YGC6|1yyAzyz6ks-`Y153z}KEvA@f=5q7B@T=%Y8+*Teh!AAdL8-d|l`{pm?-t%op&JX0eNeDwJ|`&IO^=#j1R>qntSyLDnlQ?NL<-PwS@x&6R7^fx0rJ@jqcPpH}a@Y}3YhSz<}M(CxchzwFq4LsMDN|LTPZxe~LFZO6#!+ZPIl|fN35}}of_fC>0prYV_juaIKJk9QFSh^pr6g*l23A1zRJ}14rxu0AxwIf$o;$Dg!vkfkx%+=Fl9p-N1!r7NU@w!|k>EkVUZ+OpfkFvx8*75EQY0N*!?VC2GGWTejb&ZAH|CjWYtjjTZQF1kye9AQY7Pqw*y}Xpz4-<}y^Ml>Y^hGl-(2lMa?j$3`{_*nmkMTQeYT~O=`>iPHIEi9L26ck0_x*2A6B(Ji&j=)!rcExZ-DIUFPK(#Oq4vTIYG+i*ztsl7yK~Uz)mB@<vKdd-{s#}<jnAK)E0AIIEtAwCS4#BkoFtihWmYtmqcE3tGQ0BpLYdLxFItJ4stK~a)K;&bmVsxMNDE=v-^;A{4C!<4WPHrIee4fczwc!J(>tt@uUUzk5eK4W>U4~fg>?2+z?jN3IdV{>7A_U5y_f7a&gE);YdNfvCpd@K7x6yqWB;frEMP64MhYvCA}Qvu_6A)lgGQymGVx8|ezXk@m%V6z851sZc!pZIXRW5FqkS;Nawbz*HSAiaT-LLra&z<e&+^r?8}evPekhb5Y`vJf``gRSZ-?94?;n5ror&>SJ!D)q#h{sZU2Gji;*M4-3}o0)y4LaqeX^{GVDVIDLoSJ3m2w5}`MepS$0-#6bKvQ|{eg!be0oEF%|MQG8hZBkMq4axG78YI_GGTqB61_y>qe<U2&+Ju(9}EvyG@CO<48HWNO~<SO(IYdWGFSg+@#S0s#^B4N+kc}$+<YF=9FJf&p@cBVBUhA)lk;Rx<$g%*8sKT=qoUL9Su08$Ur;n&HQ1~JXgh1XVg%Wy9<oBOZhV;r|1f*&8I6wz_B*=oAy_9=m(0_q}2p<-D2zI19G7Hr`zlyPe&Hoz;s~^rD(YZU`o8dqp!7+O)2G3r|d{j80_dR1HPQ}Nr1<4o+uaA5@#0=JVN`>ms@7bl<nh87S+k}s%*Woyr88)Lz?I8jJmh2e(e<zM+ky|&%cT%GEOy5Eo-HWK4DLZ#UbrufL`coE$v<)yWCGWZr5SJFj5g9wK%_4XF9Ou(sI_u>w-7)i1p#j4YN2l5onTIxw4?ZO6UpO@2D|fZ4XDx0m8j>jtN&mQhW$C<3Ugq^zh&SqDy_@RuC4gS*{#Y3qFPUpH_1X3Q{sx1+9fmfdyGnNR!`<;Ea}U44l!$=>6}muK(~%@e?uwWAXB(ADK3pD`J+PVVX{nR15Zgl=qc16?Jp9#&d(t1L{<>1u4dZVLX<!TkDaqy<K8lxC}_Lbu`#DcFnB9T=;l%2|?t1#C(<;=D<9<G?Pp=d_AKHY9;eaCuf8z*8t*FQi7=a=a#H|+Um}(i;@Mn8@J+PXw*r(hb70oe-=OarVPnpg5)q&KEw|aEZZKYyhM%bj$F>XM}^y9-4bEPESO22X1j+yVS5)<+|=&pjMXZis}M4^nOkYCj@*A4v@F47cw4y^9t}PzZ>P`pAl)H&!t=ZxBYZ}bkQK9^wf|QDFSFzrK|@rPNg~t)<EhWPxytzp%wQ7*o<ZLsAqA>$BYg)O_0l6m&Dw=jV7Z<rMk-Qk4I@RQ4ID3BIl43qEh_cRWFagSAqCPp#bv!<ItZe$VYJK;2p2*iv?nzHhlV3XE%<xNPTJtj6WB&+Z2}ODYBl3U8Qwfi*8#XzP?jio8Z;7LTOs<gRkj~?q%0ESoaC#AOm09^IEpOz60UgN!nBU2yAQWFpE+2xD&c{lmewl`(h{p%`dvurZB-4h3$`P%)A#O$m>;C*)p<nG>ozhYkMrv=qHAMaQS*pPBPX+8q!3Ukj7x+B+^q;8UmKmOxjZI=7j=>gdTr~uQ_=-ANV)skWPQ!^U4UK86#1~;e+wNJTA{G$H6sczE>v2r8$j4#yhHh;Ux2f4Ai73?nJ}zVSh;aqlj)l)^OLb*T5weWP$__pU6kIr_U6ibQyC%-x5#V<z{wOLfwGkVu3T|&I#l5Qn2<v;xu6CPz$F<>zGekSrjG+U?xs{}3K5?_4<XJ1$J@r8d}ySd3}PYiu-c&wR#4(8W%iRQ?g=bCGj>GG(0QZXXS_{yF|i{>%xVm-VjhHy;vu2K21mzGjF*Bc6!AVb00@+=V)PArrz?5v0zEdd7s0f_N%HD`va3;v?9w}T)pzGAS@7VxTyQ*%rOIm*I#ZJ8pdJSSQ399$B=8a2n`%%slq(<RTBn)eY5k@qw?h&c5MFU5gs&V&L~8m_Q3`&M3tc1lIym=Jfe>W_WlHXPjV`&P<nWwSK@$wgwEJXDVsCw!s>w-T+a6xMW{1@^+ZG9xfi~R;?V@d^aG4!IQ37V;NKCpmlnJaW2dyT94K`@QFbCXP+eR-zX(BeXErJIQ$Vj$sW!ySKhKot_`6UmTtfPRa@`3ykvkL|yL6%&EM6Da3Kpiv2HCQN2V11R?dxgSq#bYs8uyM*>g?4=GN}Eba`&a^G?X~hxM-{NQZK<i85-9WF;yjv@t9VuXTPo-nh<4l2T^KY=G#}9Pshvs5B4t!7>rG%FDwSkwvEsDC!d3J3C00wq*3T3t=bqTwWBb1<FBn%Fb1;NAF93OP9M30KRfgJtYVOhbLx3!7A5egTqKZ#~iLFLHD%EA@5n)56Or;({_(J(~=-zdbFlmNankXjh2tp3cpu(F&KQj&@W~XaRcSx-HI3R*WJ=iBqZ5P<a9-{7HYyNp{&$tU9^(4Rn6cU1DSCXpm?6l-lyXaDCz4&8Ok)uBft$Oy1$*b3Fud1hk!xUKhkpi8nLSce7sr=2Pm$*kMMl#Ml0(^pgb1oBocDZVkXU7jAkHbK~JOVzfooSL`ak-s64|vnI+nh`p;TlD^(x562JAAbRpYKt(_tXcU17Ut=Td5Wa)Mv~W&X^-Wa1ahqDv2(R!#*%e&as*M%w!jvI>@1%Vxc!i#3$~WQ*3GM2Uu_WWD`9@-pD4}9{9YzX#njVF|;DCr%X9=J;j@4tfQ+d;G3m8k5(2M4wZncXM@t%On#ChC}^9VG_B+LogaDJw*cfK+=Hx$VAGhs>8s3(_ZY>`8WkXK`Mpv;zeFB`q~;iIU+qf`jlDQOVizE0Ib(Bd34VRh%gl3{Zp<jF*@aAPj*|43n$&ED?$j*<ipjG@0yB~*1hz6!l3UDZlJGs8S89~RJQ0u|T(UL&Gv*ZKb#_UgRmywQjv;n4n&&R1nM^s3?UmhXu@l`)`lm1>D7|2lkNARbL=qfXy2@G5BnQm+h@M{r*LV08ot7jp9Lll_7PSsUy?v@x9fW=Q2-ZwBV~t$`63bBx1#J?JRGLvuK`E&{$uA$+<qFlW%=WO?7NX1sIj*)l9c8OzUQ#Jc1#D*pD*-q>nxJ07GL}Uxr74pfah-hR(~_o?f;=94`Fw_MNgab>-%jpS`G)9Js{Z8y|D|0WXv0jcD(>2FOZWn%Zuwor)rOiZpGp=O$^Q-KiVx>=`~AaJ)hwCYKF2(Q;G3c|;P6vRO>a16@v#T%P2HS1ZDor90W-93N6Up{^djs_UTUY1;2vl9KbRV3TY=B;b;!8ct{-ONvhD}3vMZ8E*K6mKyXC<)QjUX?M+_Mt<t09Ln|m#lOlhxjDAl8l*_A?dM@DF98md4xgH)mdl^)yjRKd)oiXh#Wh;)PEwHsh#W(OBY-%;MLjGh=xJOCa%knv=kORA0BATcYo1<^wC9AgqASStyuOi<{8o)<qcM=)j_VQEt#e%kPgQwhT`FRW0%7g||$s3E6l@QJH7+Ib#WcjHqW6G^v`&-P$-l9KVe0B%ThrcMe>II02iVeGaA3GBN@e3TcScgj`$SuRuol+Fivy4dOvry<nSC=g0@G20NVKd~u^?+&<w<H>mYfbU5%UFQqr$fn>XIl*fAXk&teU)Z)x9w;9%s5lM&LKVmjH-igU3i;dGNlveC`@qw8L0O}G4L=#2(_Sf!=WuJyaT_LvhR9F|!0({+5b9@B>Z9&btpS*eqJHL{EMx6tpuiRlMYT|wG~ZMO0a;YgF=~T}Vgw|SMKU17)zJg24MN|PLREwiF)+t;@4Neb`Krd;UT-RhY@s~L<e-n{c)%A1{Nx=&p0_?){No#?%F{eShC4JH-N+J%mj&+2EzXJ8ha{i{(H1H8DYKH}EOBWt{V2<o%U2IsMX<~nQgi4~qtqP-e#+HKWt|z4f4%e44R1%zMa<H?hnm>8q3F}&z?JN+>oTyd0hq#pWWzgk_!M2WGuy5^03jUAH3rKX^x5<`J0#0z1H#$nX<4WaQTl}l-7@<&;xH>7E?1IbB-kr~Ge{1B{3S)sfI}(o5Ep`?1YV?<;~=oKA}z&RSqpFFUG!Q}JdKH|yi}UjdsdHAmO>5X;-P}9kWRIBn;;}eG0(38?HPA|vY3lv)S7=4bmGSxtP+s7(&IiLvD?>=eB%W6rvgR@bhHn}>GQY)-K+wsw5UVbvW|nvVm6mpUQD`6Cv6{S+8p0ShgsM(`W&bq0~RPFYB2GiRLMDwl5Yn@5Pq79zVX5(IXI{`G?-Q?IiUH%6K?C^_M;eepGx>g%1@FVrl}(rc;cy$V;abS8C?|fAEo(IleBDrT}ahDkPd5`8A`wzK$!$|Gcl~BKw&|_8?xI59|cNk-kTRDGmpR!3|<G;I7a6o5-L*sWEfqDBiXQ4$1cap_dco4_5o@z<;H{Y79}tSG{04@x+*|*B5J@u;-qRyU$8qF^&{}9R_S()XmcO{OwMap)9A{RH2?w!vSQ5HkWZ{ORAmZYWVKBvxsojX{Zv*Z=9tD6TLxv;=N2!=tM&w(r$ozfa?u%^vBIY7kZ^}EZ-)-R)4ueY$80RuJ=+>m_(Ig+hd+WUH7X%WjAjydVmM`@LjmB#W@wSs2f6V5NBkPf9Aku;7KT~O&fJp8Qg4{si7)}6{9l-dqhDJB7EgteibSXNK-xI4ZCwepc$*$9=E*6T#_o)Vn8oNQZx9<av;r9#&1wmLd(aQ!dnS|OC`8^E3#33aavmE~ULKe-F96@5c?twZ@yAqvNFmJ45of^ZfN63-E^tk&KbV6%LL3iO(a0$<vRF|UN;@c-X6KPrOE~;M5#hi<)8Q3h{zfhDAZ{QT0`QPN8wLW1NQcn`!n5W86LFr3Vj}lKbzEcTDD&x91US2ZJ)6h_2r=7sza$c@dpbkMaDDUXiK2sm?lJ8#{OgQn>e0?<8-kZ5bXS?RfbSYvlu8kn-OLoHYXW6`a=9pWn-cGHxoPy1M~gfXhl+88(1=2%Q-ebt9Sh9LNo-w2w%vQ@D*->#7;|1!JoNM+X)fV?3(Da{bE4o?9|(0t8D}C)sQ^Ts5jDuBLE!?BX!BHyHDW>4R<-VJ4Snm!Y8<F!GStD&l>liTvdP~8&dzm^byV&>QyC{W1nJWOL$AcX!ZsSKBFyM=v;tzTQIL&JW{|~dNh^}*YKwYw4HUG;3hrimMzv~f#BAM|j7l&gwx~TGI@hF$m1lX8&{%N6Nn`{Gd+qZ&T1uuk)F8DHN6jgU9slm`sj0r`j#4eISKx%Lg#&W#dkZMxjQmZleTL%H$1ySbg&JZmR|HX{<QsSZtw98l9V7tYr;1p*?vmgl8w%aN@eu{YlCJ#M9oUw*2D8+}G}oAimnw|Y$~_k%Q26#G5Z0VrWP$=mhq?>}F<P&W!uw0I=i9$3FlqtLtVmU!%}tmcf@!$b!XOMo0>s}?tuK(w$EOx0fp4%VEW~u5Z*kg?ay0%Ps5hIp6ix>YdG;K{GTMX=je0MUWJ4sgk0!XE(VVvsE_9%9MCr8^*kXS<8_k2-!HH&ao7QI<Q5t7!RbU7f*Qx3%t92XVx+d}bWHiamhKUqL8d)2ue=3aZMbEk{J|6<XFt4K$u*?LNmQxgm6sXJu<pZTPh1Bldu1@G}GvqMXofa7CV9yzGRHwEM%SvJoVNEzHz?QLsC{if1$PiVX&G@4xZkU)>5X$F&sDOl4*rJ`?PgUR{=CH=i)mk-vVn9I3Xi5RTX5F<C<7ygOyD++oD|A!8RyNKD@}b%`x>vVbhIrAlGZxtyAUB+bb%;@cxu)Lpw$I|m;Ke68HPs@?g;9ycK`!#@_o1rF8tkKAJ0TZiW0Ln0J|x8F95MQ*y?UNdC(&*!gKU2#4q#R2Poz(boJ#GCc^=&Jzw%qpe{pT(Oy%SV`oY!DS(C(6Nuq+-#^rUY<-f<AN4!z-;(0<aOa})ICB}i<sFK~rLtakr@HG*T=O$RWfz+yh%!^|c@T>z(0X76881^!EDzLoMC~<d=P5={eqo7kIC`g(n{E@<wZ@pDuI173i=Og_pC37bF<z1uI^Q(~dV8CNEZ<C5Om)8xMFmUf2^(uvSCZy|g?_LmJh8;Z<k?}yb3Dmwi#8&=!!}Dk|Q{#0U^CC(pek7UFrzerPLP7Q4LGWT_9xZD>;-Ik6gT`YT^l$K+)}uD|mQ5duNGYR0H2Vr|{lK&eu$?n^mI&H<DV5FAuE>OD#BK#Q-FC!43??w&NMYh#d@bN$v)*-q6t4IiJkGE7ifBAHGA&+i5c0?^=^)+7;G)<}1eq6ueAlsk9mO`UgwE7qE|1#kE;baRuISiZ@F<E1giA~e=$P&Cc+#m(lh>+y9v%{`t?_4i&i;B1wULA8fKm0HP57|>(M;&E<wyg;nOgG2n|tTj_+pSKmYU0pDd2cwjIJYBg_c9NB0eb;2E=^uwO;11X45_wJb+QCu|Tp3-zL&;6ER!qLni<?0e~P-y^<^7OET3%7K|~|pHZ%VXKf;O0+f@ZkTQTGEH(jJU<<!;3d+N9*$^;G`%T&RK@k=mEm1zSR+K+zc(%i}r239#F`5aqAMW%dX9x5%^qNj0r_gLKf9QVsXRC*A08B|whcI(?srbf-9SivN0)&@T$VbMyko0;UjtumqgTYLvN~Xv(S`O|;rdCU)9ivEkJ;z?wClsW5F|jF%wj&sTI)CWWrID=l@>?U$)}^t5#68<I;>!y4o^d2R!A6akPY0W-{9IJqG?I-Xd8W}5>eCqQ@&rOir_-d-jY9avtefHV`ZRJr8A4JASX>&nWz2L?aM-{@E<nqj!c--KKt|55bk_`Zk%V;Ks0yy!m5rl702rH4zr3C44w*jy7K(%eCOZ}qT;HJG0)z`;R(Ir_2a1hQAAoUSiEoOEIxFrbGjNuWd_&5T_n-|5*`p1qK}9ltJUX^lD<}=Bw+JxrV$r~49U82M0oMPVRdb48qAp*S`z}P0m3yHdW;RyqC`E`ysfqY=%X-7rt6)3DNf>JR0-`D>)IM=((HlDb4I#Cc>CE+K=OP)%&fQ~<U>s{$fyl9>2Kwd9-~TW=gowvgYH$eKRzcJ`?dl%6IUzYhYWXy+SIBf3)Z`8JO^R4jE!zrG9ruV8mn8m5_6cNr$48Re$0Q|}CxGIwf*}M`_bu75HlSpt+_*H3q$-3j;Yczi!ls*Af)r}77SJNzdN#nTwCP3|BXB1uK&ew8*rbk+LPE9g<9T8uqW}xM(lb>3+C`Mzdlrd<kI^bo2qAKR2`qOoarojYLCHdW1dyj1R%%PG9Y09qZ$pZEirSZLA`FO19^pL@zfoIN<ECykuBbevdAlG@17QG4=71aBs&#8m3w4qhm(wFw2gUppSz`<bvwGd99UL_t$ljVE9&g_&4#H#l4W!;kj>>?O^tmt*aB6MlXu2zyGYcgq=WIlWYy_Sj$|Es(dM_IHthc4ZL*bO*GoA3oCvAGz(S6d`x(JYN_x-TmE$v(q3#wl`$DK4|i#u`z6z4Tgz%nT~*uXph<Kdd3K@42=D1k!(aRCVE*)U0#)Cr;HF$vh47VBsT0D>_+suIS5f555?oCcF6B^y)$69Z#0L3WaBEJ*JGtDQi_Eg4N@-eFV~E8#-vSUa*vVlm+>aB@zmgS;a}!r1(-mNIk5wO~f(WMWbiOZ9bzE^oIdUCl_AxkP^o>dbP_o!36v57pl4#P3?U9uAM<eMnO5)~y*B9Ys9_QWm8*9ydUx%nZ+rhL)ZZ0#u1U^|`c5$_^<HW1UmA7^LazgfM#`B-;nOWtC<sK&|zgZ-}f(8Pc26BZv2if0CDZxbq>5gl#yu_QgZz-iART`}8d==<Iap$(^9ZDfJfg90M2Oew@C62*tqjTr}$i=m!c#a=c5yRH#?LCL<ePt3dbPBT<i;%AtB|JlIDyL?er+t2YDj+fF>J)cT2RnxUD^>bBJMnk?lB!`Rg1PNr~?>Xk)zW&@XU;&Mflrmz=_5zmU}>lLH}STB4J%79xWg~CV%pCMOGn9PM`Xf`!R15W&ZJ{oZI9AH2WVx$TK%KGgK;OmX_tCjZ}w((pHN6eqY8E%jT=_W^rZlJ$73}%LF&N(FL^3;fw(_94;d_wvRCM`qLWx=3ZP9TW5rFn4^&DYDg<V2(!P^MJo%v)2QHw?cY;*D{t_?=}=5+Y}3j?I#yroD=)+RvN|lkn0l8K;Rmi&5SS_;%SO0CQP_Q+!4#&}rF74C=~;rGJs~eMJ-{LkRgF$<L#D{pZNrE5Fm3<Q7z(A5)Jf+*1<vt={QsGJx}d6|3~@0z<0GF9}oLDe|vM@*@Ll|4NP$bS8Ng>~%N6WSVdi9zk;bqOXVl0XGK30R'
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
