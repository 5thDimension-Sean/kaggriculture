"""Kaggriculture agent — Route candidate ep=90625734 P0 score=152,559
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
    'c-rk<O>bM*5&bV(b74}lY<H*HFR>8CG9<Y~Y6wAqrYKOPi?q9<|GkP#k&ka?&YYRK_mNhzGEI?ubLW1|$C)#q|9kTHpML%2=U-3$^!eoD#qI6M{o>>wKmF@(|9*Jm;pHzs{rb<J|MT$r^U3?mo8jTF+>1Yd`r*fm50~FxT%9aV-d?Xy7Ax`g?fYT)IQqlwFuZ$sd;Na6xI0<An!Nq}aCQCRWU<_S{Nv5_yH9WLcHek;fB(P5-gqwGe)s9)?n%qh*gl`EhugbHSwCFg+`WH%wS8;yVqX!r!`0R9sY~;z+YgMNy8Y`|DVJC8etb~=-KUNAI5|`$2yr$)p^30li~Y!)4!}b<UpehR^69USq}ffmGWpZD#?PM4_0`4OVXMi#N64{h4;8P#!@e2skA3BC#Q1GZ{q|cA|Nn5e-81?-kte^sm@050%Y&*e?uMJmtEY$VJ~a^oX?AiJZG{+1K3v=yPY?a_?gyoswvX7pxV`@5s7pRUS?F7dw?EugUDGwuTx((pNcoj#etD6b_?^6H#wtpa$Is|6C~0f6YM5zWj6a>w7g}s`bGA|3^dRh@L1Mkhcfd80S$9Z%nR8+D&PdMPJJzFe4^Wh~{nO-;$r0@26+istMc{YQM}c_-zV@^Vna^4mZQzDPAHBZ18s6Uh_|0&0cX@UB*GH|j9>N^*OpQG7(Wmq557En_N4ClzAB7(6#)%nC!Q#wzX9ND`<^yNY-;C_^(6?<rp=R^LZ?jGrUiUE@p_iH>GDtNw@LXFeNxI^^O(f2~*rRO?@9bMw21UV0gjOovIZ2*?ih=_=QdAu9G`p{1>3+0Q@MsAn%+9I%ob>YMesaOoj$B=ddntCzHn@Z`S5J?1n7fS&XJ7ur>vEN(kGJ5x;XTJa$`S`y$GbPAG5;X9Z`zc~+@opMH5PXNpVL>eF303W$<<);Dbws*+}2+7@={_yOgJvi4|X%t7tOptJGxr9lZ+7i`-_{u#P6)BiLXZOH=?BDB#Ids)CscQcfUPNWMu9>BamF0Ho2^}la-!0Ene@2+6yzNolzzKRvQ5C&Ox77TWtl)W;|KDAKZI4K7VqqK!(w`Oj3tjDbcfal4S0cS<zIE!d%+P?8?&%Wk!p?XeDl{CdlSeTfKZ-2A)|WErex%FSFt^q|d#h@iFK2vEN;O+sXW=cUU7|vl2HW4n)h;=@=yo>FkSuF_md@<e*3`Tq;(3&)ILB%hmkaa#$r#a1O68;(gf1{y|e%z*;_z6jmTbQp{oP47yYXjY@%K;+w$zXd4<Xd(r+fCS2z547G62T1`<$`(TRYOs2AG*tIsfto8Nv!#~Rx$RGJlX%E)qyF&TF#*4YVySZ5ZdAPax;o+HYOpM3sKI5_}2F=9lV(TapceGMrAj5{zwU#gFlVwE&i>ERha!Kr}lq-PG=gkN`PN@Kx15fwu4?OhX(;ND026CL!(38J6+G1&wQGkB6Cv&A1ksHZgH%b*kSOv<2rsfgYZAvU0N6OJf(raO95`mH+L#gTICXE(Q)v}XSBKapz&c#7Br~G1i20}dr^A_x^hO$Q1EfSu-2B;-RUxC@{Xuv5&2HIh7<`0wRxhj@AqlTK?U0}Rj%AYAYMORR5K3yRKj<vDhw7;T5KTxD5ttP1J7F#bLkOS2}-DVGYI<n9PrVDE*Mawk+Q{w#{eXW&jN-2*zWe0-7U`KBm@a3dW0z8(pM7gk*I6J@R5!(B{+%j9HY#(Q`s7{twW$TsY1uYF4(mZEp)V*!>Yp;knLJ$Oe{#87YajJQ0Su17q342N`4rw0)^g>r_Y5M}%<$l6(vkn7>k%|DR#rd^5(}69Qma{fq7rdEAtPf{yn8mS<K$G0cl?4S>LQmLyM~(SvdpKea5bmXOOt=b?;zOtz4}zkghkFMQUFr+Bg0N`Ka^;v>@F~pyw3=&BkdnD7Xf13CEXayNn*1(h-+h01_1zO~&xAGRl@aPc51WCpc=^(gOq<LVG0V>|O{Ykz1$#fr`%0RMy1828xk2Xvb*kBd6yw1#9!uJ-^+?#xE-@}#1|-=!8tfXoW>#S?e7w1YAaXupKFbZWXC7UcNhTY<p3wxglKG{RGeVVX0C6fQLDb!IOIAK@b!XQ_$pYMtTk$b8>LlL7lH=Yzi=TW`hU73oa+oR~;s*(qZ4XmkqQ-ScE@$4O!fmi_iLhf9%p^~<?ZY0iy^AVtYWs7>YL(Ab2$|Z<t+ZB0?!OFLmS8fxty~L_2A`C-(`S1S!1=tE{=jL~>}T!&6~N0ZIY!VBRb`S0HNkl5^KPzkz5+AYM1g0}cSuNq>f1=)!A8CG2vM_kAr)Az=ZTSu)LO$x5orU*OIMCA4MU4ceKT1IOGQY5v`%qZFPIL3D6APRGX%ng5D4u_4Zxw{NKp&^p0bnHc=H6dQCgb-M59{Gcu|HoPt$b(t`(Fe3Z4dy#Mf4czHF84haD-4#5gDU>OPYj&=ig$3%-OaUbir<qv`J5&GknP7OjW4$A(&3uQW(YtZwOdA*HufHNY;|j>J~q+ZSSfkfK*-5k;T2kr{cMUxpD~8>baDkGM2)GW$ge0hPkIL`cBxiU9Jp(W#otV={PAC%K^4ww^mBT|k3e{!f{#FFC<;u#1@@AJ+SCp~FHe6c)W^L;=QyN~_Zb5H=X^Q2yu_;4B=7t`T4+4C@qDZrs*n`sT{~WNergTonLR3ZP>brFW*ixia5WhKR#0GTQ-gGDS$BY$bpzR~(!U75G0S<WNj5sDT4;Nd}XzS;3L%<A9FaDOH+6#OKdLh_k@)ws9vP8fhnkSV%mqc4&hYlz2*+{iKR}0!z<~9T78h)@b(`Z&O`N>_`!_8iT8t2O*<)Na(P^(J>U`rJxE$ypIh40%fZheZ$`AN*=pFk4@}FFl}&>yt<$4YE&Y-^v+%N-MLB@Jh(0w98Y7Z@*0KCl;k<6$3Z}pz~w&)e8l#q8dMGC%7?kuX=Zp@zp2UXkVFQAS6m6<E5{L$nm$yNf?wo9*9gA$&izy%MA<-@lDl4`OYSH+JSSDq1Vb|IK3S94TVJMXa?;nfhgYxJVRg;6MM7nuO*cZjXj>^<W(QD|fY~?_ldcVA0_(~_tI1%44caiw0k_t+(MwR8hz)Iv;DG}&lAX3PZXF@R#iaTCl7~#zQ9xArKz@nY1p|>FOD;m9)(udgjv3<`EEFcNzDn%9LSeY#u^22^J7upzJ3e-$O{JuLECI6iTKT7=3fSAW)KpFhlzDJ*9?i*Byej@J6?6<lyY1*M44NgH4`}+-&ZK0KGOCsJCNL0{O0u<Baav*Fs(Jeot0iIUXNr?^Pi*b6{jSOj#-+s^4B^!?Kpq^%^NCfJp*EnJdvtamAPd_C6riA};*(%vtC5dNb=i4D*ib1`sYejLP(B^Hcbz0mnqihEiU~V{kV7-5@aE9ZjDv{T=^E1=5^FvVh+t6<_6bwl1-7w=sC(F&e_q=&?gB_X32*>~gdo|Kq$)f+E&0?gx|CWk{@7IH=#N6Ho;_po>NVS|>S^FG1(trKK&Prun4nE6e>3SN?oo=7jB}3wpP=8I%S4}DuG-|;@k7YtFc2`0fDdbDnq*j9ZfDN}UbpQwCsRhaM$xS_sLI0*U+uu>d(`bc^}**rnBUn}szn0z8S{lR<_Hk%g#(mIqVvPB56qHtZ00^Q*~O*~aww-*=#3HaiM!?$TN?WT*4sYWM9+{nvWd0_KCf>YKzm0Ft%&O>Q;u9u@n#w8=;{jiX6eqOm4${wB_QkBpfom<pX3M%+GZzB>v(?WM;`Yr0J#YFAS)u+G^TI*D)Zt!M)9*o1;`tIuawU(k;fpZIfmO;`%*(=FV2tH1&CSB*c@7dKOXcv^PHv|Gs<dqAyb>9B>lN2HJhP3b<2Qa@@$d7j3f$ytxS~U7BiY8d=KZ98YMB01mp*oY)$`+IYoJ$UD9Wj^4_##h~13lxl3s#Q;uVMWw%=FL^qTEDa;5;FWBTGzTg{?1V@&xauzhn0W&_L=NG~C9ezcpB?%0Nvh0FItpibSpK4VHVV^#NHB-%4W0!!$auh>Bn}j2kW>iy9N@`E?%LjJ3LiH=NJ?yoGD6>J1tL;ul*(#ZrR0>l8+gZU%01l5PsF$#eWl>9M$|OfzCm;E^q$#B!XN4~-4V0wsf3yyM5Wajgxl`pEqEo5*mvj7=c6Fc)GqtL?r-oa?7btbh?;@@?)MWWsvcO3GuQ*q{KcAcL@2{$6$=voi<`D$n6rBNwA6sgA%`uCQJy>t*=FDj;TLcK0p?y18E*zs5VPEo6JB0-IIJ^JB)G*r$e1@+>#?5y9FcX(`-+Pr^kwm&)JD=Pw54MqV9F#m_$N(uX@v+<7YpG;PdzC|}9&OC76skKiLPOI~1+p2W5*4WQ*p{aXW+qhx>Apmy8x*hI02?zqxIp@j@_uFX#AxCH@Zf=rC*xdFZR7@tS*b0E7Lw-}lNiBTNmylqLKpPB_=&^zu733_;T6XchGAY<p?)v4vg%MnPSM~KS8cTOJh1M@r#L2(ZX=)V!RjO><97kvkmyXE6qs;S1LVWlZ3`0Eca8WcFFfy*tNOECr~)XR5At-e)gewpsHagNl<H!(CRl%BQxe}Da0kbe@%91VlVrNi7s!!K!A)|6)$-BC1PQ;eZJ9h!K4MUD8vKPSkQ;6W7qArax3!a;Uf=eCr|*KYM)?|kGB~HbQX0?U)|%rsObiW?p%8%ILFpmX&!*Hz-KAOsFc(Gr%spAg+Q~qHEgFhyp)zT{sR{zJsGwui1{1{yNFs}5K!~fO2Ur_~zA1&O2q9u%j_KZa_xtiijk&$vR1n!hd6dasAI)*<{|zL`8>{BrXu)`p_{UdDm8W@v40mWYx{)OiFALn4TbvWG4@p1^qAgPFV`e4CS>n=Q`calEm#-eOieQ;Dq~_3}MyWdv{FJMe$~rS7|9a=88{Uqbi<qT(4>hrGL(!+lfh*Zt*JWT^12BaH$%c38@F}`#XSQ8;075vJYYdh(=(Fi>c1V`b286TC)3Q(<qVx+9x@Gol#9>xET&^U=NU&D|XOJ8M`AdqN0f$oFAua?(3A{)z$3b9eMOu5_${WM4312IUr!g^=mrB!m&+2i?QcTAS4kd)FkWRIBn;;}eG0(38?HPA|vY3lv)S7=4bVAmC>_s6gPW#u=2R}O^FhaSR*MY$ZfsXc}IDH;>pqo`7l@@g<Th?(fS<L1V%Zo{O>7?xgO`F5J=r9YLMxO)qW55DsL=7hXlPWo<QS$A82*OWO(KlYWBnJo8h6d9rB?mNLc*1QR+<p|J?o$c>Ncl;!!!&i|0#7^@a!dmmFr$lN{-ZR1YLb=>unVc02hw3}GeZeD11OV#ZYGA66euhxctdvE;G;lE&3p60WabeVg2C&+8pr57L_$T1pA4f5aU>hoD)v5Csm}HRYB1%-gYgz6Fa|WgQLefwKy@N&z(C@pYD!<QI~nyO@Tpemc8zFrAOK9xYgg0g%9Aw!0td2U%-N7ntTt3-3SMNjO((gMEdBjdRwd?`#uckUnep{<Y5^veFWM7u9uqCc(M4x$#tNIRL&6=xyd63KPy5nK9<#AL?b+6l!WW_jKl~9?sZj}0Vl<Pu6T>MJ9SQ&^)<cV|KFEddKH}F<<`^T)v@pzKcIK8$mU_e7PJ{^n<^RGw9R1o7uy`tzR3tjB2hzrYZR<*)#oP2?F;7mxG<Ih^#4JWfd4t%Xp%uu`XjV(`+k<`(-!qvMM<MdYSRe(Wk@MJ?^76oxc>(wa%~K#Sia(|TL<(VUjyMBO2TYR#a)E1F{lOgE5#o5LibhU>k;RI-P})JsG&_&1TEgK6iU<b=n)a^%^EYaF2XO<*5P*mDSu+qoL^_Nn5S}$=SnUha;_N=MjDh1fc3flUDD&x91US2ZJ)6h_2r=7sw<Hp*d-~K4SJxjNDLM$~9@8Gfzs_i;9_@^_A$VCrca>QS_^y#fsT5(^%}jB+CQ#NVmy2SzDe*p+n?^5KRsxTKGbIZsR2nrn%+ay9tQ=qK8nVsSJ6nl!RU^!KR^ia&L!`NU_bnKQ6TOLoH+>+|6(yXB5TybPbw<=6nFa+5K%&i4EY^qwRa@1%vo-WBAFENIlDSX^I#<G@dB7%r2RJ*|0oGBe_e^1&+z_No2kg8O`3l=-tO_urtI-O8xkfQII+sD#swIs`qNy!v(KS%W9xJw+Z5h?7vk|j(V=^kSjM$>~Xy{y%CRUy01wv!71t*UY<m<K1>u4pJ;!lIjMjSM!D0ck2+oz`5qB}~ps9r(AjBI{N6i1<aGjcbz?iq?tABV)~7ix&OToFW(lJDOEv<3l0c8maEpDJSMx=Uh<Y$SC1zDE=eOS<x3c3@lH8cb3X(_CvB-c68?s*Lk0K%W6$&Cx|BC~S17$xslY_3|LJza)9S{i_0^7NE?E6y@2}gxMjOhFdKR!Vn}t_zl(h0?B-MW>FIN25Z7XMECg)rwtiL<L`lTvw17wbli|<&p{}o&F9dl^%BW7L=yXGg8K>0dF$Xp2MWiNUR!}J_LsBKJft0*XePC3eWnqkakf+ihG21-s;;tHvmvf&5>HP?bKI<%NMWRpwUPO!!pL6qtjpr_5fBXVI;sH6Oi*b#MPW#R!c0&-P+C(+?cVL`gx=Oe4uaijfuRQWoDoMgYU{A9B=iuLgroXv87qhag))l_G1b|GKWgHJiD?CqeEx?DKxl<5+S&b70UpB0H14g|s_zqn0a8X&3h*^+u9X;9%j(AEIqo`M<d*uQurUepp}ID@SGQY*c;2%y7TFjeH=KrLh*5#Lp5F6z&*H}5#V0!T)FQcsQH8}`F7oo*P*G(K_R+7Kkc+V~xqAs865?|X82!^;Jx!>SXg8KYw!IPuuqw1C(kDhvrFO<V4ese*`K_nFxHfX8aB>9w;L7K$Nn(m5Q9W$q>N?f(-$BkJ-l%x-G$9zKgM)?>L<7zJBFSw$<mL1ZKP3Y4+ypB(kXrPQX>n+n2f)~@2}Ce#W$qMUd8bk0?i`%}CgMgxr%F(eG)?#;h3DRSt<+a7=w+Ob^s9`_ndp~yjaJXELfV4?kI}SED%M<HH)O)Vy>ry76xx}Pt<SxCL3|lD^h`v?1KB1}`s(mn`R5H!qsdH-*Ko{>D53a~Buby2MB)ks#eaLj3!5E{Km#gd^q}vU2K^iSp7p4Uy=BvfB2vmI5X-*8T0bzI0&M5ZouzYsDx_34NxLEwni0Db+;rO!15vLwjT$Ty@8W9#2b=V+3#4$x-{5h2wHHJ`x{+z|e1nh&?nnpOP6ijnW+KSE804Fd-Rmf_c_nnF4s&_XPIs}P5Oqa|Zh}WKL?B#ZVnB!Nj>mIOb(*|Z&GYb(U~P>*({r}hbC``BJO_-b_w2!k^^aykk1a>~2hP-yFW%cbN5&U}M6t|VUQ7YU6Ju;0xhk|Ax)sq$p)eq(gRiwRhc%n_x!?heLVX32J^0p<cAJRUN*_7_xCsCRf$Ei90bi1-9<pGJnf8ow{X1(Du@j)29EFqt3}LYe&;ncdl~Yh2hRcS4S=w*PwhxN1=xB-3p|zs?LBq2ht|irWG>g$pp#5;8CpkNyouSur5;=ubCxj(I+~(mM08`TAA<UdzD!wsd#{zo20N*7Q@{zGFB)y)8BLh9@U@+6Dk|{Fvc>cnXsnrrDx14T_tJ5P2Qazj46h+$+3_zXTcWKf{)_VD!5oc@C*g)c*T^jLag<8)z5*}fnM$D&!O;vs_s$Ck%K9M}p=n=JPj5c`!A*AE!(db4Y{9@MiaC~hVIiCz6sRJx7jk_{t8Ynnq;2{^F<xXL$5<ws%=U2LGhPp^XI&V}3S8mG2Q6K<}O{iVo)^vx=9{>wQ!U3B#EIbQzTYzvOOzMuD^FXl?Y6CD1Eb%>2QDepJWCqR>l5a>^@*cE7A$znTHK<6&k4MM$Y6Yc1wH5*9T`U@ytV4tKFu?ksvuaN9OVs7da^Hn0vT`r<!_3BN9i#}+C^Zp(Zdq@*GMXlO{S}|=<mEGnsvJ@G#HB@V=(IP4)Ly1D*Poq>WFR|pk2!*ItYHNr$C4UomotC+!{`tq9#^TqA?#WOQRlR)d*I%L<Or$d)3jb8(_~PSH`q2QVo9~^Do8clBUW6J_$%2akZm0wNp2sKlw6(wioXhm5KP^-WW!p6l9_Vf(m0Z;5Wa*X$&?72ZfXfqsKHu5hj{DR0I$-f8DWgTouB}vPJv*LIz9>s)xL}8iH(c`EbvOtQ1xpUQFiZHBo01Ct3)A$$o(a-+`+`*i>m}B3-u8|o@!XBExC65Ad$ZfDeft1U$%)bAS!u;_dxtcZB?z&^(P)4_4j8B(lihTpkz#X^}e)FM~QJcK4NuH%ukUu#&9sJmwnp7QR9K^tr_C+_O0R|Jf`13>W$>63^+-j3ljmy)@F{TyMj5hP-1e<Ms&zV;OU_}5|hXGqH)i9TRJ=xP6<BK3158DriUHfCylL(0O@w$59{61&Ly#++O>1sNi(*%BS%1SUgHETlY)c&%L6bTt|=PCz*UbDI1~^UfPkJglVnMq5Ng(vfW2w4j)njr7}KLFVI24etjfS?Fj-QvMinqIFcuSJ4|0u>r6{o42~^yY(M0AQMpdyAE|iY7Ba0*!6TSi`=af3gJ5nT!&F^X{GlyIYW@Jt#Cbh{@ed(K?+db)OMzYK$`cqJ6Rs!w!@;*>|s}sL#<$5?giuWN&v0JxhV00Aq6i8W=-gw*ql`=CtGa6cYN(fLT`qbyrE-BlmJdAZt)nbsQuM@)Tfskw;?3T6l&Xop>uf8I(CS^#kj*lGPC;mxZ=HbqVFcJprto=39xwm0Z$Uc1w3pzU<dU7XdaZJ4hJ;%UBxF4o(AVM+lJQvM+0s4VLksR+*Fcs<*u+GTF*DBEc_ej)ZrgEs>8V~kS4bjLV>gx4C{I(MhE46+in`UTcv$`!cy(UX}!Z0>9xsxeeq<Ur1o!P*poVZ*Or77&iV#KrJ`FaKE0M-lNgEHV2Nue;3!Dq--6DD(E8JbPa!GIIL&qssUi-rL?eQiZap95cSq+hMP*RYM}VmM;{9L{iqEJ!ywLUaTD#bGcrTyxGLL6@gSq@3m|nBWuAXE13Qnl1|l-Esm!#4XK>n`pjX#w8~r-GDNsGH2eJ^1NaA{Sa@AQ^oHrbCM7_J9BK76gBNtRMmdwT$qHHZpk=J+*yqBUck4@CIOhs5}e{QN`X$xMq*G`HZ1*%l<zB|C>cV?|44ow)$2b+-d^~f&Lp>>^8A>3JmDUbu&-ef_GtiTH7oY&;_a}X`h0q8lnE9e-^)4dzjvm*_e%X7nS+%X>8GK;YBKcAuf3M)IGuUyJDjxJlrHJ2XyVR4zTd*#_x}g#%kGE'
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
