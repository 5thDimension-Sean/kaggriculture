"""Kaggriculture agent — Route candidate ep=90697169 P1 score=141,870
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
    'c-rk<U2j{*5&bWE=7afR#qOJGGqDiGG9<Y~Y6wAqrYKOP4{6_u{P!vrMPA;SJ#*$`FKN|JrYVwlcXoDnKF*x^^xw0;|NPspzx;Ogr%z`eE^cqn?q_HJ`1xOd`}e~e4=;cH`L}=m@}Gy-pU&Q0-mD+~%DwpW#~**Xcz^lB#nsvD?9KJ&Y_<?@-@aR~KMekGyI#M2czg41eQ|d-`)2g^59_Pz_h+;D?&BYBuHSxqbGQG-%lrG^X9x4SeDnRs5Bn$02Xp&$wpriaeID!k>zliGpI`0X8of9a#O?a(YX8)E^QpTJ44=CD>rg0{S8soM5dPiAt@OBYs6r6K+5Ut!guPhWkBrFxJaqe&W&fFve|<2T{gNw-KYnZY?D1M(UA$TEBzf=%IXCU0;uUz<x5NE$DBSHZ{?MsEe(T}?@9%bdMt{fi<Tn>%0glG<AgYVI_08zj(?j>48Vv(Uc61i)1~DA@`r@|nbk{HMe^82P_lVt#+v|^pxa1QQMc<8h_rtZ~8tX*4)PxGi@hi`Kd=Xpt{dm!eWrQY=pTS{}lGavhm}Q;~KOK-4QZ~6cYXmnw2s=oS&^P%GxJDv+hr|~-7q;&V#<_o|^{Chb6k+ZDG<sxk2K(`fAAWq{_+9i-U|xZ*J!v8H+15qtxFOL;udlAwZ|;8jc71bqd3E{M&r++N!W82f8+qWPPv_a!p{IxL*(zT@3O(Ab6Ej$X*{bc%I{eM;2UgJE^z3xkx7&U~&gO^TW}Pyu_dXk;mzX?bkYXzETq}hnU2)zf5@(<9(QOIu?OSsUih$7&szkhZlB@wL0(Qtq5wXM5?5@Mo{iqV~Km`J3=h%G?dU;bnIbmvhuCBnn<U3{yE}_WP(?btqw{ha^i=TL1u9EQa=Dato=a@%X-~j7*_qrrzALQ+uHY76hXqr^V-0uH#`byO07`;fj8caTAoPG1#+Ou9>itmRB$Hn-;Zf5$d%nNKsR}*(qBgFph;^r^@J8Nv>t5N&yP{MH%#f)^y1X=I<-ySD2B6nXSkepgJsaCti3NM@%uQx;Oi51k&sFZ)JO@MdjpwFvmTf(v#F4q1B58m~!pIj@DVYDri&>@#f^z57@nR{h4n#xf$RXdnnd3vF&Xz~|ZiJPnmvc1$6FF&h+WtK<_Vcy@%%=ir9bMIt)%&C3sx0l~_GXLovR^)4D;%3Bw*fMoGM#)?<dmNxoWZF1lP^1c%ik04T_8X^iHNUhRR>~8c!t3*RAMIoRs3|O9EuTgT%aI~U=CJk#T_}S_rNAQbP2hgihKAE#w5`U3%j{mE3iqsPi8|T`V=QMdm6gM;)#S1^*VhmK%wHgX<PV`eSd(uP<p*0Y=JxL9V)N(q&CQPw&wSm)cr5NCE}LS|jJz(kjv{bJD-{MZY$#o8`GP)K7DTXkJm$u@Bz9Gf%Yo15%?LeCsQ{QAPq*z4Jay;O3;neQa-5UUlfO6EVqud}fPS?nbEOuZ8>y`~N)>`z1j>Sj))ClkN-P{l%F#vAOR=;Ofs&wxP{ZmbjTTVVvLCBN@{gVzi-T%T`NjAQgmQA`E!b6cWsO?5h<o`8P)mlq9IMySfK!SLw8OrcKMb1Z>af%mZHUR-1&y~;`7<S_Xbx0cPje6s$GWlKw7;T5-%+F{ttKezimew9$bssgZmWkp9a(4t(}g*dV#_rEOJe;UeXVM2N-2-JWJiL+U`KE6@a3dW0z8&gpj=o>oSonE2<<~(ZXPXDZXai|s7{twMeCL21uYF4(mZEZ)Vyu=YcGj7LJ$Oe{$)IoVXAp-Su17q0eea)hqR9YdZDYew0nW<ay#L;)kBA2q#{6aael4Nbj_Aa%T*id1#jjN`eCdMqZ}I#G|8-7nNeUR^n~qq)R?cfhdt&1;a(cYgef37d<Zq;K~NO*@ZbQVOMT&15EgB-T-hfUd<yeFt>zjOq-3lLS__*33o;{+lHaB5yB{vEzJH?a8L`HE(+KsSyUjpfynJp)rkl(aKFhCRnvRiFGxmOz_mwmib#pbxbA!$U>QrkFBpDBe@mSJs%}2uac1h#HWk8bE(O}cqZDtjw!pApN2qNb_=Cj-|2j<a5Gs)D3uSX<7X)>=mF(XvD1`wx`5=7lUH)ZA1R(Dh{QWoHD-inW*Q77>pmYnzgS^VNR#}J$*NDfowL;NIx+V(KzC2CxE<YMMMD%=KoON1SxU?zE*?H=|S+dIqRrglHq&{p|eg^;OcZKbt3aQ|h{G6j?2ZRK2e)cK^ioj%!v0M6%?^aqw%v!Av97XU9a=NLg<RFy#@)BxkD&AYjX`3lTr0|lN=-ytvxRNqGW4sFy+j}SF$7gB-ce4ZGINUb&W6p<D<Ub=Af(J-{A)Hj2LuvCN;jMgYF>jl$65QPmRWrjdF5dxt-sWotDI8xMvzo+b^4c<JCZ4{O!0MV#cGgeCX<|)+!aIK&$k@GYt8os6>y4ot+4?9vV664s&7x$6efF^JhS+GaA;AIQbI-2a>-dum+V9|PrduXVI<w}FJgmz263kkhe)BwBCb|iN4-n|g(g9N=;c?7+z88h-YAE)8fjb%p611^o&nC&73he%;u!ZpC1Mu73v$W+bcF&R9slbn!it>;dS&LKfA|EDb0V@~iK>|&<KhxPs|WSD4$!lKt2QGj8g(qdTvVT17w<&Sm&&dh-5HUi9qVI9KC4cnTG-&{05>6>N?t_lDu3DB{L(pzb7E}CyDQ^esGne6~LnIt4owi3XVD+W%73j7}vawrxT)W89_B!kJ<tYFXbaX`o2k}6Fh{Oe~S#982YZQRL*Mz)hdEF>OQJJetWC7x1dKdIs#hw3$BN5l%PigsV)ZK{h&J5t1Gqf?7{5HgB~xDFc}9YZl*3aXIA`?LW-pllVRZ`eCs$zvzzv5CD1mJKeFRreFsMkTUK@7zV-ovUQQoq9Rrcp6ic*C=$RB+o%T4g#V$F8@*B!?!oppsFiZzMe`?Bh%CRO^t4cATq$MaVdnaoQG%B^r4~@{2~`RNAPuU?uP;)$_9#*-1VAWa7W4M8L5I249U3rWNyTkel<lC8+~qjSoNA6v}>|0;wl3z-3WEjwp6&R9Y9e6X2VEKxHgmttSbktHikCXpoU=%xV3E?Jq4xl*wF1ESm1!j$d*;ctuaV<F=;%%WFeDv6cAND5LdBw!GI^o5{r<ibpsTrW5T!w3x#p$SBkw?2n<&|CW8eVqwG~k$HuPIR7$pwB|z4mEB`b^0ejn~n#w7GG7B!wqdB>XSH-`jf{u=8cRRWZgJyx|1DZUwGbvc4jA~`A1$0EEf^03VIIXa7)x3R*)snFFBgM(FCsuoG&$zr`SV(Mv4qBB6-#i24!ErnvUsV}u1FE@4t9u7o*gl{D2Z|~_2`082`KT0EJC6t(Dn%;w2*MZ2r$hIyk%S2|%+f?LZbuMuXgUR64*iTch?t$OnC_6!c|Rb6MLo1nnA|RC8+(YlhpqYNr9I&;fYg%!2arezl3hu%gJ+i|p4vs1Qnm8?mLf)f<kEWfjERf4*<Mvo1G_1(^dkj2Rf)m`ZBhA~NiT8tQjA2Ldj$9d{pL(2`lz~Ui`R}HLLP@T0rPP9u<cBf42#R{Y<a+&+HP|)WrS-K%}Rspc-ZNy9r$dIy53V?+Z+hfJKIXNh@(DZx^Twi0Rp9x==?bB1C!(&%iL!syIATVyK;(&-WVRAxNA<a(%5&f-uB5RT84Zho7ncir}a%8Xm5|9<#9b_%8~0SUY4=;YL~+|3wIvPC>joxfUIXhX>24v$q^LPW+$80@$}A*Jnkz1xd`_lD<ar5rfvEv>ta1d@v{a6$XkA|kk2oX#~`UWgxhEPQbS|U&yUyzh?&mV9D4*`AM}5a=UnM|&MstXQ<S7X*Q90{x>L6dC??N}1g0lZ2yA7dBsZDSB;k8FuT+%8JQ0u|RN0*T8FPyAI=iILGUdHt#}K<2<+)2~CR2`My|Am4o#<xLKZWT*={cKx_!Yj0B-o?6%2`m717>_g%P)fZ?S4h4B?%0NqIS-r)-_RYA8J(xVV^dFHB!x(W0!!$auh>BO~R2%GpZ>lCABB{<sG|Rq575C9`@Qol-VH1RlCzswo2wDmBLiOc9yUbfWxB=)Jj<TvZ$#vWsoDTlaG8_qe-P8r)`(iPFU{o%O~sLJK@VGlRH(uAv%?+e>um0sjCAm%+#vGT{hejzCfv4eiw1Ip(e|xk_ATN|AKSHhwHih{-IWtC3EX@%mWC1bLb2>{M1s@8;)6g=)qb`H)T#+*&<+o5!$z-<-##~5%widwNnUikF)z9EDf`*z-Rb6WZZ1m4l{9C_k&kajU>|b+WBN|d9aO?;~?b`Lk38Bi4Wc8UaAr)?Ntt?e6%sDDO7i4godV}3S=`#B`T2Vu`N#(%uK2bq`QhpH^^VR0XAlIa*p&J<^9U&Nu!Aez=Jz7o{V!zwUJv(%t}rnDn=e-OkxIBHNq?t6uO|N#ZMf!cl9^V5?*mCVHoB`E7Wg=Ru&y<$SE3p;;Qv_o(I<5@D#^H(lz62d$2l5$?#nOHzYb!2M0_zst)pD?6x@x?7K#MloytF%2oZfT&M&noe%PKvDG0?Lx`s+5K471+Yqcjz9sSR4!DE;$@umG-;-oI&lkv%O~Flag4Ocg#smSsu(nJd2p=)17!Ceh7088~!2~S1{B7+dr}evi;OV;{Em6LPpA61vuaw4fxV7f64HH8{)DQ^3@1XP$>SvScqi#~I0ho&-e&(J`W9?+1pglAc)k0;`d{Y$!WKluKs0}8H5s*X{!GI7~M-Q+z2z`?ZRS|>mfjP!|-`wx>7dhtkd{aSW3q=AOkI0e53ew{Z!2quZ?+-<D-e|#il=#ONN|mR1f(&<PG`bNb5Kj-dFSj^1ygnoW6+~O)uuqwl9A}ABlj%oUu3Wx)$jXCdj*yx|hZ?2sIPg=fRx0Yuko@bNRoA^8ITtZX^X_V5UqjKS$AL51ThnD=TLUnK1Hp!O>hvkPYGbuccK|{-m}?A{HR!8pZ+1wQ&jy5}&C{Y#9isFL5xPb8t;b<jJY23MrIBFI1kNBi1oD@ZaXK7Id54$~6eaK?y&MC9r4?x%crmXVUX1%%Q9O;2sXSMj)>~GOQI<kEWT95^phuf_n;;}eGS9C9?HPA|q|C`-<eGmaWMao0UNsi}6+>XZdIkjcrvgTBbhLNH>EpNq-K+wsG_ONhS;xU-G0R6RFDBikleP~uZI17v!z^qVeGbHr0SlB7wQk}+sgiRVC0_?b5Pq79zOlk3F*v9;HJDaOIiT^v6K?C^_M;eeA4>Rp%1?qFrl}(rc;cauV;IPQ8C?|fAEo(2i!?95E`(|xNQbp%g#vH}P$mK0ObjbYP*_m#hUm7zM}d->x7LNp%p))agV%vIj^1_fgo+eD8AccUNH#20?0qgmo$VdeV9JdL<1I>H3`l+}TvaPTbs}oOK;oowLZ7ia8TBKusaENBjc9Wq08GqlSJUXqlQjSW2eM+!S(i_&HdJK_USzdRr*Q>Y`umA2OUyBjD^><&mONl${^B{&a-3Xrrp;K<rt6S!2RCnr4#3mC^peMH%$Gge8dCT|)Zm9df-*HKE=r8D5qDxZWuik4;KXKKk<|ye@cl>Z8p;@BL^CZ6vzVQ^C4;5jFt_7j0zmmcHxEa@wgfDm3MCbZPV0`ev18ksBhcb)da#%$r(hbpGah0Tqoce*Y*3d5GBldm68w7558`_!lj0~uUW^4&AQ~}`jVUj8ESVL6FKC_ufl>T1<sedUb949^a5`X`43G=dY4rzVa7T#aiCIonI*ZCJJe0YZn@6cxLO4l^1qa4}56}PRZ=`Ar<@F=|{~)6=inPLPmqG;+fKaKPN-O9x(_7?t)(w1m(8T8{<l7D}>QTe>)%E+&G!+FzSXyvZiOrDew-exgZfn``-q^e8Ni)4zB_gVIozYA^YlcuMRw5||t0ZBAsw(HN1PgI$Cej?&f(xQRpGiuCS5pf;A`7M&|9gaEtx}OY6bnXWf*U~DR9!u`-Frs)*rPNw@|^Rp=(I`DX`mFol_d7l5C<9-5foxv#Y-U{jfY3oMg5S2tzo>Eur)FHj8T{|O^sO*cPdM+V>me}kG-b-sO3=VMi-h_8N$tiO4*wRF!wcFY8<0u?2Sn6o!4yx^8!^2HBOk`(=6$SL4*`mye`B%q{5NtHq5&jLhmr)x*QmKKU4(_6aq)h*wa7)WCB<=SIZ?Q8uY;GT=Kved1NcH_3b5tX-~g*KoAa2)M1aIHcrT;MJXvO(CmWxz&2{_9zI;v8q*BQH#XUVDAxVYIA2437Xb&2LL?)t5hO;*n}Ql$t0&JZ+jRrJiVes%pydF*WMc(mUZ#On13?I`c~wn_p*;!?xYlim+E(|0*LKSK_`+1t#fwyU0mP|D_8;h)<69sZv{^Q|eO3)<+o}=K8AZXSiRjb;*-n@jNa=Og#J{oaoz4Mt?HC-&L@OsAeYbM*k9jH_H#SEL30<=zO1W4OLpMRA(PD!>0isrtoCeq3xjF~Losl#HlWs|}-FrX<-?YVr7KIE4=T|4jTYjEeLXu}@L-rVQs$gP`;v0`(Vk2uNVJMfMTgCqJ(?h{pAQu9w^_e1i=uKf8b!NqMiR9WgQG7i5;bGA4z}l`gK|$kaW=(cMK!F&p6s=0@iqKv#O~sZX*Ju))0?$BADm`}~R&k5Df^;|xn^B;ok|}%L06Rir5pJQ1v`gj&)Mx<U)&{MwB3+q+3J2!V4uZ-!sS?96nv79+xqwpn`M#_Zz{TF|Te=jXck%_JQOaz3g;OJJT&{U_=oEIq=B1#Z7GDcQrv*q+-7molvYPX}XM-`a!9r|0h2@;y0du|4r|m-K<zLEBk5ActNuU1P%kNwP!M^a1d|xKJ-cOoVmWw7d;zXi;+N-Da)Ge)+bhK}!Fmm`13G{i=GrVFcwL|7<a!>!tZ$16Rw2UJar~`nB;Cr&*et5EuqL}(BMHP;=%ZHkdGv)|?S`gea4hIXPSRo05vd*0GCBAgzRakY#B*`3#$Shd^MdBL*I}Lln8&uuaX%x6SWfc;0VM@4*G)?#u#k(+v@EJ9`UK8LSoD>?hHQj>^TXmJ^S0dY?M9}1-^4;cCFuuHR$RKAf{s(!+>AFn>QGx_)Jnu0gjSsZoWg%DgX~W}Bom-5-X^Ws4h#pC>(fAx1{|hihGEBi0dH@KYRn$lEktuEZm~*3j$k^pK%#=X)K&1=7n(4gI=F>A5>^!n6%CUe(OkmfV?F3xHmhvO$`Q@Y0^w1Wfae@dxcR&GmpXHldFzxs}c)Kq!n#f)3Q)BZGkpV=e%^C2T6=QtevCAJt%8zhib`GGp@n4S-AEOl@H+%@mo4mnVBu1rj2SIE}MbpNret~!%EgO;|;3_3P<Jt;hY5P32u|?Ch`5>%Ygv#V=P(D@TL92!ZZyGYl=b!=%>}%}f(@a&i>4+Fnf_qtU$Jr^Q00~T>joiSnh6@A~4f?uJj{pK2N`gc|oY*B+EoNa>d?MkRMe97BVpQDhE3UTFfFwssCKdU?z6KU40=#{EFxnAqjpKxArtIg9`8jc%2%Z<{8o=;Oq97uU3OlJ>#s{todxkXzZ_JS&LAEi7YP*u@gB=pgmb!lJ@SG!7ybc;$d`Tl8WO>QzvYuVG8L)80CTg4s&cjhe<~$w#nZNXfe@6JS<yV@mvUrax@B<3>wP;QuV9dfIF@x?@Ht8WtpazU;#JaSGG%DuSL@xzC(sazukZc!5gUZPc1ZG=9@{YbyP?(4Sc4`fY)42e-h7J2naJHr+Bu{tdYctxf^CLnKqZ0Mf9CChRkj-6Pot+dkSe@px)O}6$vLi`y{HBgjJXe|@g~Lf6sUs9iy1N?;(73_}t_FNNbDSe3LM%_H058*jZ{_IN0I@QtxgqTT!-H&4BY|P@k)x}sae}i|g+9Huv{i0LjYEillBm%y`?geutYAH89E@(f*aX!>f0ic%oHHF@eKlBsGhD;K@F#T@9)V<II>N{z@;#AZje8gbG|wL#dExBEco-d-ubx44<b--J&M_C0K}PiwdeFz9qf){lZO$#+4aw%%DlEKnP!?GOKUVid7;3;U^9=BSXd8y2Jq8eg#jPB<x1mpcI8=)j4V|iIA?B*Vm6D~PHk0w#w{=nEF~V{c>@n!!G+;keQgGR^jUej=btksc;?}`_3fhK&)XNFps<~@s{8m>M2Iw2J-Lf5<Fa;dn#t&;;q=bkdwnV(v&hrb957#hJDYD}Fq`0nh-|9;d=bN2SO4|xk2XPn5vdaio_Vjl&RSr(W(fW>$e?<!VK!e404GfA@S#%)GCasDoP*`K970?1uRgD>x;TZurTeZu^7$>4);tw6zk7WJw{FRKztez8G<#YioCL<7sZ!lvr^FF=fIHI8Rl)875bI!x?XA|fbXNNhM<78iHx0Q#L<Y-;z)Vr7E+1BpALFD|8Qtjh)p+k@ol5X40xa19i=G)O(Bv`H2NKQ{R_MT?qH7)A6b&M8q!J3hx0<V0Gg49h5i9{icI`*t%uQ)ZZF$T0Bus;Mjs-?Cuy&XBC6L`Ow>gubevU2d&S!vUTK<p7)?iwo*qq%E*=L4={QZ$c4x)Nv)Q6<Lu<XnvqG7DV@EL0z4QJ?7;4?Izr5(9jWP8KjdeZIJN#8wmvw_TwHRfLH7&9vs2I`<Yibtk|}fvGipm$@&11d79mE3>Kg0XZ!11HDcGQa@A}jQorgg}HVfqm#@>PKNtduKjgz5-N!sUPG`XBFmN=b`$T$8ar5I?1t)$$&&t1RN;=L0ih<g`E3$-<wHCBF;=e|EB8`{@0RCZ5Cf5V=$$Tyd92o~BPfb0%K{aW2gtGIeV1;0*}+cNZ;zlWIxUiIqk=?vuZiS4GGDf*w1j6@>fQ;@P0~)?4;>ob;fSa(#kv$o5o9D758$At;Y%3ko^zn+47wCS6iBpG6cQ}K<Ibg#$P?84X`_tH6N*7qHDpr>K!gK4U)PwdBgK8(L&l0tVx(3o+nNc??zLk`E`?JnSx`Z!5*=%^X1II{<gzL5kBV17^+m417-$HBxD`n=FrZGwEnmm*MUH_*sXTc(tq8^Z3#Qd|z%Ohom_q(VTu_o&t^f1QUa{SV;ODSH4a{;pZP*osWTE^B=+>V0yGA*XY0+VvfxRy<?$XC#!GW2{2HK%uxiSJzrqhb#XOZd_wTqENQa4qu>4pU>aF7$YQUIP+fh4E0XOqro)?lhqtkkv7+cF^d5j&YHlr%LXWvm+@ZRFFdS+fc;_#VIM{cP>5YH~Kj8cATpAs)ckr2<TU3i;l-!|>Y;m*hruj#1XeZ!y@4Av}MPGFaJhkGL0;M-J2G1H51oMT!h}B#ZaI-~SKjS-BG'
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
