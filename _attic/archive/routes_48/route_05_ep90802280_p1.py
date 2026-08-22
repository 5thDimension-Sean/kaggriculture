"""Kaggriculture agent — Route candidate ep=90802280 P1 score=149,313
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
    'c-rk<O>bM*5&bV(a}j<>wz^YoCN`p2h9s9r10e{|6a|WOk#<+~zgMv+^6|~gnKLu@K2nBPrYVwd?%c2WICJKw|DOH*m*0Q;_4l(s{dD&6>hA9BVRrV9U;g#Ce?PwQ`0}@3e*fpM|9O1<)7iWCx9i8haxeb;>Bpb1KD__o>iTSU_U2}DHd~0d@7}G~9|wQ9Td&_fzP)+3zPdk~y&Ap!!}|K>!`W=U`}oJ(o423d-0#0}{_ya>*}-_;zxn>t$NiJ$gR%W|wpriZf0p&b&F%fW&#!iGjb0oo;%<F?y?^T5eCqB4!>8{4I#kO0>$g8YD*yh|R(m-)EWHQ`x4)`Mwbzs_g(?pJh^<u1%FwxSj(>e1&3?|6*&n|J#`*F3>dktmw}VH>v1tz#ufW5;9d3|A<!;6JV^RI_TaW+$aKGC$`a6*)zquMKa3ss4s;=(Wx1(3j58Z!iBnHy#=rGy|F_e6Lb!R+1^vnAnlxo^NV)x?i=98l?`2=O5?<C&+a9eea*F<xzi6tQASDyLwA~*4SdC`njlqQd#!C_F+)^^n}(>xn~I-xJL*yQGHqqy-w*g=EDdXw+)R~EJIkoq#`!uFkkocnjIN97)%C~Nnp(Ib;1*vl(^_~}L9chN_IeFeVuyb77mS{H5LhD0B|xxQY%x&Qgw_3i!p>-T^CthLrdm_nYhkq18de4c$3y)1fUt9<<^bZNI9)L;r`E8Cw9IGo!Ltf0dg+3BHg+kQgL=7-;Aoie=cV>UuBHAQ5QYHHxQwp5aI#d(`ZoPDuJ+Zx{6x2_C|f{_TVRJ?bR;<1j1juaIKJk9QFSh^pr6g*f03A1zTJ}14rsh?ahwIf$o;$Dg!vkfkx%+=Fl9p-N1!r7NU@w!|k>EkVUZ+OpfkFvx8*75EQY0N*!?VC2GGWTejbd81G|1aq)S(jt<qU35Y`IK?`EpBVidU+|aA0`|Z=Lfr)>9b~DpdDQ;+(|}={oU2=U*dPx*u+<(_FGZXaT3Lh4C(|~@B7~#Co(d3pAkqdO`BX+yU9vVoEEQlL+ynb)Xu1qf2$3EcjutbtF5+zWiy<t{SO|z8=pTpS0KaaTPCSPu9WE6IY~12%B*NAM`14QWOn8Gg)*bXU$hc82n@1#$QUKhU;Yfua19k{GtB$@ofR)4eG;CG*EzM<{r3HLog4ys&o%NsE0Hwfh_sBKj&ZY)&YlE}sZ5h22Tp3?WU<=&l0C_(oX?k*)hhXhQ}}@qf5blakDAm1_VZ~ZwE{_#VpeN!;-zwGR8lMx@dOS@+hB3oulAQQ;Y5dLsD;DUYKl7A2V-<+GPzYlv$e@?ZEkKJ|CxU?@JDtI&MXy6{X@l%w&z=~NMY;P+}+<^ZT`Hzz5Ve~j7t*;vUte&b&8F{*I0z^Xr<^t1`?&SEnm<l%Yq0Wk7YLGl4w>bR{*ikn-O~CQh_uFp6=Tpc<8~WH}uyGEIFs4XMb<7pVB6yfB|by=87*OH<G<>l)8kl3X};=%_Feel;}8)ouiAS*TT{y0!2cGQq#*#8ZDsCWiPA5_K%*Ni;QYc`PKLggn9~QGT2!S<&msgBs_f$a7>QA0<+iAfK$p2w8P%aC??HwRV;Nz4K=yDz<9fqQB$&vuAtg{x<UjTYh%A@e?^CWplnTAO;Fb@wq8CU2kL>k%^vb}Wa$k|Al7h;mLCA7#QQt?S}WO<;vRL%js%XurRVd2<0gF);IXU{1;kq7?BapPY#;h^^K9X=eVoZMJ6Uj*tzecHv@~c)^PHVg_qNrqy&?t)ffDffSMfxK$>*_UtrXTL>?yH0q<swV3|+0I-3w%w`w7SGIt&;_Dkh{B=hrGv*K7f`oVDS);LSW@eK>Q&ERIbCtmM|R%qaL0dcyWQYRp&L!x3|Ua4(%>!c~wIAA-+#SQG_DJUD>p;$OHGghgu>Fvrw_PhtM2)m(#uoy^rmYhhDhK~@x!``vM1{yc>|`r-Zc_j;gzZbkYp!iHfif<E_S)h4?IZwnrbf8m&~W3&}b_#^K$X-?`UZH*lVof*{0XA4q{8N-+@Y1`JLWqaGjxRe=aW$TEsYY>~6hpABY<`RN<`-q7xH_U+vb!8@^Y|wi~6VyuPmrl-5Rjvxe#H0jT_s=bP0<>kGT^A)QaW`(o577vhcrQ$jd;ctc@=Y0%!vqOrs_2LxBv`gR%zcS9*PXqb3xLYK!MY_vlUcx%Jk53w`;7mcRk2mOpEFjge6B*{)Mjp_MLP%)$iQX^O2gaJwGe9XNqJ7Db`KgG`OAkqI_P!P4`3aF1%TAdIUdmvzh#m>HNlhWlXWg~u0n!1l&K00x(*2`P*EJ|I@rLN9#L%8ETm%3^;9xaky@Y_sXT4qcj?N}rD3>Ksc$B$XQ?16kk+Y4EAR+M!957ruwfLxY3Mu9j?^0XGaQp@LB)y(sBEqc-cNy@m0t@s^hUL#@j4Cfr-I~iX@Hvs<(7g6M8_4PuViKWVb{tcL&lY-vjQY|1N<#z*D2f2moP$<j*>x|?%v+seB{8?dKh?UyQTF?L%YQ4mYx_=dRtWk#Dncx?DV~RA?61uda;s<UYas5+sKT3(5GQU*G5Ur15S>d%#3?Ss}x2mLIUnq1dy+dPSp$`llQB;&9q+I`tp=?0S$6F!l%i4HJGcXv{@k&xGx9lp|3*!6c*oR1ObM1ON(U#kQ)qlD1Y=zbY>2S*9b48rLi(sTnb<}?1eIZb76imHgXH&3Q#SC{qWEZ?6=b1T$pbvgT^5lnGgYRn<BDM_9(ywFb>>@$_*S7xhN(Vl+ppzB?Il(%;L!Oad^qylq%gO;`8SL%~||8F}F(v+4A&WHI(H8GVSyd3&e*t7HtrU62&R=sZ>c(V5OR|Ct^ZZjW(<CHq}kV4n8r9H@N6|=rf9^gw7@$a6@5Z3j9z+5ZRC-P%Mk_JgiZmWX20L-Nar5(*`HWt2WB6MkO*#@7zV-ovY;4gX?m}@kN%x;VAT`q~k#q5Q4S@Y=u$aB(^uzplm4nzMg8GW`?Kry&ByPNvuJ5#g%ZyavTw<=|e>+Ge&NCjaKa7+)o8klns<A^y@Xc<c^ZVb5adWP$}asm^F#L^<}CiCw*;ucvYeuR@Y=(BvgFbbR)Ej;FUsfcDzLi!VLpA>55b)Fs~f6nhZ96p$)GcaBFQFy@bw**wD5J9^N1$*|L>!>j)VxVa?~KJgl=0ETRe$@=MGvL5KudauE`>5`hAROc>W-(KUhfRpJa53d41l#bCk4DYg~b@v$#$>ND+Q36RFuicTF>z#hA$=5|V;%mbhY`rA`=wu*mC1swyyaXY#TgJy{)2%0{%GbvdbjVg4#2@FJ~k{mHsoK{%4YTm!ZrAgTOnUd(-6I*+1FRfr<Sb?m;MqU-lpD%_#SE_9|B{0Kr9G_U38tO)>c}J^<07Kb6o&W_!C8PxXTaEEls>@Cz!oE(K(m#S_hH~l9wd>?y(zLcTJ5AURgv6aeg*QizX8c1;iPxB8ky!I__ymiQuuquUF0gGq#23Vp2=LmTa2G(nO8^5X<O9i8C{^LvX~}1H(WTUS@yDhj$GH?*_3RmwSFhRSRnG#4dAIZ<1^QHlx(01h`I||vnU8XoWPE#sAq8#kT>AU$a@8i!4j)2dh&6%o2)M9zqDe-@<#zTQ;7!}6cQRvys~+7#g{nO4@YP0uzC+#KQD6I{3e)@AO0h|xykoj(Mw|G6QeAZMHRBlL_r~5clUr=+ABQrEg?=0nm$++2v8AmaVA}1IOZ4n`BbR79;M2OM0jzh#&Wd=RGU3Q|HgA@%j;^kNYnJYIT3Ki~QUY?G4GL>B*-4J^plxo_G>)hDedKZ90*;GN53(MDO=9|%uQD&*V-z=QP`<q73ro5D5_b$znnSR?+a0@NE5`X2yTCBZ_UW-D`1+uin&n(oQ<`1K*`}yx|58($&7hsSVL%aswn$$_(uBZNCdzk<`AibKhqFqJQkW-#@PkXXrhmqoqMXhy$+JprZ`v=!UPklGrL>YMzp=ftTP=2?flB`bW(1-a>?;yq@QpZ!BTH8~3z}qr85hxWi{SbWzoL_p1cF0ZcEO6)HBoGz>W&97pFVswQ_5IlqJXS)6g@$kbR(5yR1;82Vo%c52X?ta9V~M_?6rj$xIu=i?M_FzDw&m3s!{<}TER*H4v!|Nm#&QEP)kY5B*9!K7x}cLDJ39}=G7kppWCpoPZ;EQIhj-C8=^O=`j-p*mv%Lv4fC|BxJ$z;;fs^HWp@$L8*1x(Dmh>z{|n9(AI|6Y`-iKlSt_@EhIxR$H$`WV;is0E-f*nsLkHHIx+yc-$`%0vrWoRml?lhtMc4_w)SV&0Th8u(Fg47!0-xb)ka2roKgz`A+z(!5S0s_F*Ul$*%Y$vC90w(b7?MTGOMK`x_gX5MvR>s-ss|ghD~0OEjG)joP=RbMsRRWoUA^V0f=NsjLAoyy=?29MH^9cs4la<rqnuwEJTV%805EtU;mJ6cR8zXOM6A>nL<`AtY)On@tt70nK%onITJ%JfBmY%73iD#Y6$fKkz63-&^TG=Kd$E>9hl+BFXP>xx!ERDpUjTD&c&uYq={EA&F0Ia3GJF@H4~fRtNr4H^HNZrS{kS0ceb*3>^1^dhxf(#rrz&97`KV79;~nBQgnAl9MyZx)8-fBTHYM@h0e5gbId32EJsGF#<bfRX6x<{ySUVr>Qjl;I+ZN3O<s&{7r(0mC9=YLWZ~;sq2V6VJ>Gf?Nc=|3VYm~3(C!=-RE2WDa?$bH!^Td!6843Y-9+WRay>Lox+Fjl?0DDo?&)kz`?467p*rK5@7b=?OJFFmJiwZ(UJvC9#fTXoZMu@nodVsw_Xq-~)iVz|O?ilZVcfZfSsnNLCI}~DDNI{)kYV9^N5s)X)$wB*0$)Pt?*2U2RA}E6M5(@euI)Gso&4xR&^x|cK`!bJn;`JdBXu-opihatQ<v5RA8caVzbLBSHV^|TebB6L9de|tr$HAj=#Z+1EhGb{&ymZ6ck@Fd|B=BMpqn2)M82t3Wa3#O%`Veg60H(4a*$z(~K1F8j%(m+vK#&J>jlsGHeK!5g4yp9n2ywQxS{BSh)P^Cxx6Hncc+iT=%hjwHDfmhx4U$JN<sc|B%Q_)T-%e8G+_`67X@#yo6R!Z=gUjgcqIjnxi+S#))|u6k^O%(&43+Fx8}>FSxu8lx^rLJvgd*M`)%k0;Aj72}bL1np@XimS6btC1r>aM$@y?g6Q56%z6;N~*;1yDZy&N*ZIT3@o^tK63KdVmZvna8=igX`O8bi?5Ilj*h^R#KeI#54`G*DL6+JuZ!Md~!Lz8zFSIBqIF$BUoj5Tx4BVB)3Zk>+bvxUGY`m13ZN3K9^hSV=adrjA_Tnx|rrX{ZC{fRP3(1OlWcY2E<ckSdcPJ=iuglmI+{$_nU7VBkrC^nwCFWVa1I3Y6r%7jt8B_Z(b;V#eS;zHUNCp`58O*bqkaFc)`XMF;4@lsgTg3LyJKWFZ6U4%CqWN4;~`F@;uEZ_7A~sRDygOxMxob2r@U2onfZ>5XC-#AeKe5FC?{ZFCM)+@#<`Wi&|k`)(_lQ)g6ab>EAGW4MkNGQ2W>Nn9KiJjAI)Tx{YBmgQo_&~@M!>bK8bZA)mze9^PHA(r=oWzQm;EsVz7uy`eh;;0T`@h}ZHY8LI`zOpL!B4f_MTJ|5|DM4aoyew!Pj&;_V$TC@29%NZ?(wutkR7QtWnrhGhf!)){s#B_ktsJWQPK%uqI33iirBSVy<!y0u-l3h+2q&bx;a5RZhltNt0PY3m-fmE66ow<gX1gI?1n8jp1RWVKRR&e6gd3dW9lUek?(h??{K<&)!Jmx94a3EB<<3zKC*NBNXn?q+vK%WY8KNs9bQ>J5hCs`goQdc#6#+f$Aq--6N%+bBXk1_4e6ZpFNj0EzkH4~gkQdYYHNLpf7+rK^t}GL^QjjPAZvJD&&eK#M0865JKrwNO<~qk41&xDEqxwV);R^BmsDKS;=Z{sJtfB*F5v~D?aVZW0Gh#p6CVz5F4F5ffc)GkdUS`S~qqEPlFhs9NP||5LTtqmCOY{pqeq${Ch25W53HQ0wLiO0PtgcgtpXb9Xce`X3rv>Lbyc}LOsE^|GvF<e9cQ_0QpFecz7{&HghzzU9|C4M-LUB;w_NX{i9V9-Hb}I&`H4}UG68gMC%T>2-Dr4`|F7~<CrbFc5SZgKdkeWd8LJ0mAW5T0kZk-Jh7~3vW9!Yir0)QQLMlqHs9vLKi)a5z_ZP=<+)5SWi_$S07q9h*(__~}+5mZwEZit}Lq)$&c4g6^c+n6OVyl6UL{h71Fyn#_%SW?_NSvw9M?SWCSyO?MGKaZXWM1ZJ?bJ$V9-N2z}32i3?p&@$UW>Pm2%#?2uk^^<K0TUoNg15OHrQ)Me$gS=ES`2O);n=MHVMU2?FoJKx)mrq+#sLg9#4>zSmLpPdxUIO$jJRmtK`;ezZXubQNC-)_RLe-p_N3~z{7{G}ieiBBIt}7b)l9`lDmTz&hqh(P4L?E5D%g|kB?YPI24+hST^($0cJ2~S&3p1}2V2$JP|yHJU8Kg<<^s(Q!L+O!2e%kT5;z7_Mv)uD?D%ZItP6(~66!~hS3^ANl_3;zGL}?zZks4yzCzU_CW3HNXRL)_SfoUi<TKi&F%e+VHl4-%=CyaTHf=gUMD>1KuiPdi-U;qKSRhJuAzI(1v9gha3pm}Kk`cHTGSHzZL(j5|^pyATi!QF%p_?+%f$qqb#5_7Ub^Ck+U=in1YQCP~m=XD0h^!Pwx8QU&SftAkqKjv0_kw&a0DUzkKJTF6$j)&oQ>zsj;PQjn1tkIzY)V%@D_zqEXVKZDwHo<BMB<qRCSwyW_|rZRKnRF|Y%w2>VgKF1rfJS$s4mx4^O(r9s2-qkdGw}w3|6o`I<8gYy$K7fzX$?5s%0#A!I9F>&wB<3$tEPZ;WVsljtY!Kr;?o`I)k1a{G!ZcHI{x0VA&Mv7b8B`_4EuSW2?A%UZax;lez?ZCgC{Y;EE;HQYRf^rZkk$CA-tU#jlJ&0XII)5>46Ep`jWysjBCH<+q;ylC9dx6m5r+BL2+A0GOaOv*jva5sNfCJW6mqPa=kHQsGx_xcxdwq?(~9yft8Zs4+Yy|BvAcOu07L<|a8<a5re@T%JR6D@z3J$XxNHW!B{Q8qi}OfGJiL2)r~(={}2|;ikiCLMIx+{|^`OIj;h;0-28cse4bZe6lA7JK$AhSbWo30yt@e-cTtE37k3)Ts_Jn<g%i0IJ;@ntyGdJ=aAb!c)!RfB+=ZKoFjQ0J&$*H@2+`>a(cVrJ5ULPNsOa5I%HQ^^#CnLs^qymht_P4sju*z9?($Z*3m_=a33}gfqh8qDh<1sK31OZbBH7`w=@za=b~L0uuLCV>KnqBA`o&ZON$ql04Ef7{bHi6Hb9eNG31D>y4Duk7u4Vw&_=mnhlJvNeY=KI-2G%{jFV_6N>#Kg10wreo=mS%vZN0CZ%+66se6&)eu?a$C@-sbzfxGo73DsRv=nUE*VLnFR83Q}@*T-MQFl{}VU2Xf4Ga#^geG=-jvxxB=7^%h<N(vVpF}TG+ia8RbGg2&ZFe7wNbwW;Z8O$(Lyt{lw=)nL%rj;ZCS*HP462#gTOR@o-8qRT-54{I3@0h^02G>W@{19e4eYXkr9U`EY#SJ@7KfrT<rcHCFNQc*T`3e$_i5FFSocM!--(F~nMZ)aTBHMka5GyNbpS!=8xFWq$p)Q2l-i8QNF9mg-F;E1zP6VVNj|nBTA{A|fh$2R@3_S=B?yMG`!^*qrxFaR1zmxVLnG_)zBJ-|U{i~XjS^#eEt}!KN`<|i_x^>RFMHu(tm6c&LM=jq0jZ0JF8yw~jF#z5PuArYCq-aDhG8+vH@FR#I3^-q$82lMR;vPlR>x+xxYX36o7=RdnCsKP76(j7lvBqxwGqq;86`bJ6I!N(4)sQ^gr`C)9yO}aU7<jBKth}9YZ^HgPL*W<(7UQPk&sK9tW=w<2?Wo7mEvjBc4vs1J2)Ih&&b_#Iy^KKl<&oh9TYO;-LSI)6V0>9-o20wJaFR9G?ZU4!k{<CU`3^i9TysgAYH^9tSZIJB@Nm+kNEP6gRIF60%m5tXbVAc`5<BqqZq{!&0IIBs!mFpOvPim&XoKje@9y(jrmH(G|nqAjms|yhjS{#{to%sBGE*4<t2NL$dqOa9B+2ZL?)Y*Mg}>CTl6a^^>Zx?p79+cU0EH*n{|XWU=v5m9J#xy;`p-WEvBrSvOy{iq+}<vDI~}xBO>wZIT8}gDA22&X%L&Dtu`HBRB4GZVWU!t@lQSTn$USH9@@c-T<_RovC1Hks5Q<NiKWXHT&K>(O2Voq3VGsM+pk4Zmm<ywoN6wFAJt+;yZIr=L4wX;S!@~*2%ZqENO8tf0>!enqlKUe3>BRXoIN4Jfyh>?x2A}-hz}ez)cnY(BG;Y^$AFw-(-ONFY8i<Go+v;R(`zJ6q%0qmsf{K?Wk5PH0OWZ4=eVo<tzgrlp~9|4taLzf<>?*;9T|^8{aQ|hA*=!8WHKx^C|mnV4>lS02efd84WEL*pv9t38%)%7XR`)oOl(NqJ7c18#8}B=_@^$tF<HDzQ1sJnkBMPvF5tu=Drggy%CyPEm3WvBZT#;b=k~`tC)6@CQmMnRJ2CG7kF;?GABq=KTvgF>r4jv8y^JrmEBOj52LH++OD61_$x-Z)1cWg}Qvmmq!V)@IA9<;U4j9d|zrZcp4@>z21l@7umOmvL+`rv1Ll#_I8roU-JY90k**GmTY*?-rJhKc^eT!Tpdk>Q+KC;~`W`@tA<#5Cjt_a9Rqm%;r((*b>9(Z1Dk-WW>iGbELQ50*SmPSV()n*>fk9TP~#dS`E&%r=O=`-2p@<EhVkP9hfJSj~d!7;=(sigPgDhI-pRCtiXpNkL!1)`w5u?tCH<Hl|c3X9~p7(zU)a86Gh(NRdD6w~)>4AG|+6RQDE(%_;mO)5qn>%)+Y`UP#Ka|sfh&)Gd0s))QqZC_t_{Pa}Ngup>W`~0xoYDXX-Bk0sUP$^!^O}x^vRaeuPSf|;hl&FGjgRW^v;6-=i<oU>^>l%t`>OA55Hv&~fwzCIaiU6sGoz(m%$bi~4*d#cxOU>z$(T{kqTAtYiw*$n=aLUi^plc|ws4Qi!(Ii=nm)W%8tOFhPk(U>IR$(`X3<{Xo0$eV9DLo0>@%mPeEdC@E$0qIu2eHHvS#IZ)U=PdVom2+P4?6|a%U2ly1=Eh$#qD$)ZURVF*)3kbM3+{pgjVpqmjOlq6cKh^!Rn3cSjbHtn<31#A*g;lN}|tSrRWWCy&ETC#42;O!*n0aKAfw9%W<e^;C9u`VTorP?q>#H;yu=*Gm+k049)CVzZ;gpCPQ&ZcJOk%gj`vv?`L><QCLLAR~Fe({$^kb6cnU6L^l9VmK!<hhEAX?lZ3wgo+@DpU7m`1eHkUQ@|sa7Dqx2vwcnzhMjVn590IVviO7bZul;qDNsQ_3f-vQ-uimUjk@I0X=kp&2{Gq$g?^z|)pE!JP!J5xo;LPQvVG|zy<=H5_yiD1whcdo4$6|be9@LYr4n==nP)X7C8CrG|SDTmnn;)+3Z^rMwxw^f*x##C_posmO>+ilBzcqAwz$$q7KZlwMi2'
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
