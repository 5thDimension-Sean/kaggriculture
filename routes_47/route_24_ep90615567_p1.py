"""Kaggriculture agent — Route candidate ep=90615567 P1 score=139,143
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
    'c-rlqNsnY#ZiW9#u5+P`$QtBbsuT?sI;ASq;6PhQ2m-nd14erxduRB+yQIvFc=1SnJmkGmLwD^0ImF`~A9;9q`1Ai>{QIxJ{rzvhUHr?>7vH^qdHek@uW#PId;ey4ad&y~AHV+BU;q2VZ$5nd`>((K=imP4!{?tbet7xEZ@VA9d;gbT-tKnaUtC`NxVwGz)5Ya>_2c~yyPJ0xmsgv|pWpoS^2eLo55IZwYJYLLxx4$n%cb3~U%vSB``5=`9}WNcV!wO)?vKa*^y<yKAO86CVSsN}KMMcqbmZ1XYvS7<cDvV(k>9_0_4?w(wBxfJ+tzF0T5D~LX69g(Y=Ac<w>Lk%JB(d3;P&Rl?(qDRr$2t%{U+#4!_B+h8_kTze_C#g<9{1NXotY$-|vLiZ(e=>{>8h+KEBf@<?XBY!RXw{a7?eS(c?2+GiYZVO{AreX9Z62;djep7Y%jV>2Y?=pMF36!Sdii5tc=rsD}Z#2YEF(_sQC_1$*}Q#R+D_JbLk<iKoX|l@~Xw^Wba=$ApP%5>5{uXl0)i*2p=?>w~jRSL*O7e--A_;#fp`_3)G9tTpbl-Oc)Zq)YDpDqcEx_`_BduZ-i5=*F6QR-6m{@ZmV(p#`uP)L{<jnGfqW=WSxw;dn_H8xBu)-ms^COgH5HU%F@CJ~DmM{70rAN>4h>+2jY=3+sGg$Z1?*_RzzwJ!dr0I>M)(($yc|?>b12roDJ|d%Jt_?w3F9-n@Hx`|{r&PS@c?kevnR!<m%hehh3VJQ|k6-Y*Z~*5U)Y9&dNIzwd*EamUcktkFhTqr=nS+Hq#7F$t%xhj<07teSJf+Q}yi{QWRskN1V1b*@h|XLURe%n1+TXRU74=A)b_z<gM(QF<KAd|NlG^nCr5V3Cu<|AJqkJSZ6GrR?>aw_<d_roVo}-FdzzHQxB2`Gb^uYRZGo?TmeW&_C^ijPEheOD=e#F1%23lF8?MhzGrZlHdgIcg9bi9#+QywQth>o1zIrN@$9~bXusRU4+9s&H?&z5U?3!IHRK3y`QN`1GX5V2#?nX?4U+8w?{kV0dMXm&AKxg>7I5b*Mr-%>GeGSCThZokHZrW9?JcP;fHzHu<?c(&szPj7<&xQXAs*dMjY;xhsh~D_u$Vd-gjW+{dc5M!nP6%P^dc^a*l=ua~@UNU*~q&tD)`Y?yEcc<vr+&1&VVoVv<i9dcE7=wdMfJ02I!dgoV>E8xcg-2l&e|qFr*~0G)Qsn1IN_3P{1xd`Q+n#K(a<ld{Oto*>#2NCO!-ymnnPFMGmji9w{dVCeY{^P%j@xWTPVqj7wFZMw(DX)$U-;g1PuhlkJ@C3*GUDCdCx%7>5lq^d7=t)uUwrs=-M$9odwItCx4C3U_!q+cKOF`#A5ul_6%XV(IJu;W%+L~yd(fCjCB+b#!I@$Z9I_YXI3{xwBK$#KwVb!I}~aR-x_$AN=AOzZ&Si<o}q5?S~+eelX?e@c&&Q%PNTNdvNb^&ojS<zS(>xLW=qJv9&v1|zT!c4u5VHu1v|aZci|uJ3DYAD&)!F_&L|*i8-udNQwvrz;bSg%WGv+Q(Rz4^Q!YeBQx@$LFp8zV@{Aw!vrXi3{h^%ZYNnGRlrHfdBALeUej|?AI!fZp5P>|3Q`+X&+RL+MfKeOed3ktlqo5`RV(M!j$XLBpY}%Bn`3}L?G$en{O5q!-3bwgtH%N7~j5obF=?$_vX!CJ{a_kUz>Rq)Mn<`BYUONr<z~-SgEiWmf)}Nck9Eo_Vj9)cXnmwc(*@{z5Lp+sH+<m_>b{W#=@gzm{m;UpI8*vKQ0GR@{BCx=L9u}KQfck<gjEups81i_JR<}#?GJ@X9Uj^*QjSl<{I-=kvgaDm_$+!rA?}P59mbcwCCimqGM-IUtaMQ8`^M3Y~`}Ziz(FNIfa1EaNVM}20H@y@YaF*Vjcy6wDlI9M}f;)uDSv5#rIN_LLJ9a&tY(;bM@}%t=D1hoY#$YO;$%!pUqRJZd38b5pazxbILgfuLlSDa|%Y+(>YY_5jez!TgG{lI15fMv!P{$OaYJ+qB5Q#QHP0PO*2X0&G!;zXvG{J1ipIsRW-DcpyBQqC{FYC?c!ZLfIE729}6?>{cwz<U%k3rVhQnE!9^JqMvRjd8KB8)&X&F2l3?)R4@(Q{B^11y$(w$SF-}GHW`syDmN5J*x{SgqnD#X?UOWAcQ;>#A=`pgCN<Q5hfF77W`(AZ?os1hka83?;$9ewR#jNwQH89-<TKUEx=P8NbSI%eYA?y1S%HRjQ?yI{7LnWf$e_ST^nJ5%rzxFdBW@nK0x1s}2E>Vt><__T23-7w*Ot&`5H_~2eeeg<B{cy2k^YRU?Ov6N4D5n;Y4b!ue^y24fh=Jq!5>To^a`1RYy49E<@kZi_>7;A8H69D_yW88|j)d|B&R^%VO=YJfsAqlKa88;r?m89>R=@>v8x#`cR>--Mf(^{?$QTeYlO@Y>)J#eZ@uCu&<m?7v8VM$!EqU2SP0B36U0pFFOEhuHfr<}~pH?Z*?tyZ~oCeRK5fbiXolW~K2V3l~oXi3#CU)$hJTs7U96)P0=-P^&t5Wby-~ogDBcg!t!QMrMDm$q8h7UH!!xfhi!>N{i`g9y0IYipj1VdF=9qYv^r&MDVX^49OYoj?cB$*MsCm(r;<x%HcozQdrmvV`{N&!pg7-vD#SQst7>cwE96R<i{;62xygI(Ysl%V9}!w%chBQ8TM5$)3f;92({$+M2QDafsv>{V)|)Y<BH7S{PfowJQDXD)f2rDf~}L(Yv2*F8<{PSK_wI$1vt7OF?tvBI?AxJ+Qy#Fe$z1>Z(zK{y`rVicY$!7@xb`5jUe>;ZV3sRXsG(wY*+1`(7PbdK|_MRv@OFK_>RarsnScXSx-Dbn8edRnX`dF50Eg_`s3!~43hV3m?Gk1F_kGh@?)-sMI$5iu(v+D1c@X7h<P)!Y1KUsKVVD^R<3-ZjqJ+z>Gbk9-~==cSNHsRe|EVD?#3!Lsfm7If|sf;)%9m&C@NoMRZ&K=JryQh4h23&6<Bp_wJwkM-NMne-5IZAz%NBCH;ZT!*t?^6X%mj3R&m*-~$kY!N?h(KG?=&*eY^1qU{93e|V%Ws)pTODI*F;w(n=3z0du+RbEYZkp!?xP|$6?98_`(~XWRVm$)RzwLbR8K|b)uwYYuT~IN+69FB*CrzT}3HAEMK$Iiq-}$>H)L$k{Y1}w>DlMDPA<Qk<nvs?@miOjSa3|+>^t`=+`IYfG*puuF&v8FF8P_F7We8XLGm$_;v-ggXx_E5GDWg?ftu~mm*2OV#D)s;AC^T3{zLRRlTLkM4o7Up`#u)NymsqZJDDpYL7&v0|iJ-Px!$C!XIVB4^0N6LQvx?5t!}Q4)*07*m)FR9W96)58Dp}^yoFyw$tYQj-*CpPc8=Rn|FywVZnnN+GEobU$i29}oQ`A!TECuawSa>4caOZFw%p)e&qs72T<cZ>!n4L4+m4rehC#JP2b^PBseLb{9d|Vip;5~&tAa?n!TS0n*PJ~CGk4(etSHL-j_<?>_8|42#@Tqc|NS3Mf!cVsplvoVzpEa5Q6=Nxv$f1Q7@xYqgiUd7zY$nDdf9l^0*=}&oGZI&+Y|ln;knO_k<O8U`xhwem)^!q(R7#3<0EB+WDOBL2EaqCU5i5VxMmYBF9!NK&eSTPpi_(45OH-k-ZAPD`iBG{Ebz!``v=R!*4RYxqI|D1W83OYk4)+p!x<{k7MJ>TpI?*4AA_KUdlX@lcG;`-F{R3-8@8`9;h-$XhRVSms^$;T^L>gG|PG4O%eX*6t+7840n#H>38>Vifmpzx2KF`zkKzU=;_VV0PYG*&6xnRIWUf4llN}rCsV73hTf=%K`P$<5Q$~va=No<PB#sdy^!2B8u$!dj}BmGf>PGSN$L)B#>k7!76jAI-T%%Kvp5RK@}y?s{`*rCP9)PEqV)tfB|7LrQ*pxR4kc(p*t2<j*yl?s4hK`gWtphC1b4NA+lf)R%8*fj8s%k>L~Rx5IHwuxs8=`K3hhF%+{z^{r_0z%#oua>R83S+_pVxrO8^MnDK3$`Zanw%NOXsId|an2z_#Ui&QYPQNdXKfK0M2QY4Oj2F^CPnJ~0PWEx5?qZmy~y47SIvUJWyp|67mLcY#h7qp7?i-zat4y-b4V-4+5H6_0y_kk(<{g-4xEK_&eK0|QfWGWCe;Za)0PsyK7))i;&Y>~fOMz&#9DP<W#=k_uuCZ-kXDbTG%?#I0TxuYR1Z^voTt1yxEj!(a;Xe5gtUhAH&P$Yv4lMSgm%##*C=u49+Lbvf+VlbR$m0JybctpLha%|7ZJ6>km9_pDvTm&Sj_R8ya%{xY<jUvs%Qg2mDa!-y=-T6pTKHFmMH3X%%5ZR_O8LvIlTFkLMYUv)_MV+hxUX)pX0RQ)=J4E6s_3ZXpvk|W%@E9apcPD&p~)y4^^D4ogn|JsA!C6wxTWBow4dE*7wC?CERy?9Fj;=nYfC)l{!3s>ytORRWkF!o?hpSVa>$^>?Ch8&|eSklv}92rJe=Zrg3JH$-%LqxzJ3kdXw#n1UJi@@{O3S>f_YIYrNgvj<+K%MD;3^P!#c!<w2aws;eBYi%wZ?6ZFKfzNKe8ZKC>6obzczV<=0pq&w&_TUJKAF7TUVj+<0~lQT*n=zXSkW>p#<NC1Tt<d1WpDy2kZ5|kO8yV(Hft2B5)^#dm<vM`-%^EpbhBxIeitfI~}%4(n1+?i>TEA9`m^4rTJRH;lgBAn&MV6CPKb1}%#s2ETvKP-zU0x%RPnwW47Jp*~n=+WTL>2!yb67QmJ5T;k1oJoH#Xv!TZErK(d!=kk*jj729Kw$z4S7++finUjYs8EB7F>pVur=71WiN&V0T<A*S6a*Jk1ap^DXJ*kaV}2Q`3Q-wr*lcw=YVVX%siaJrY$ONuy1JnWY$<osjU~7y?U0bt;bt9JH^Li9ymFoGLM46dV*u3S90}kqO)BFfv+cYCf=nrizMz>yRFHjZ(h=wMcZMiNS*CN;x)M;E*{Q}-y102efk8-a;nfD)O-5W@g~<aFS-N;BpDRyl_Iph2^=n~|*sF*5+9NNgHx4na{2fPxFfEiV)u)vYTLy0vRBWNyYzH`XTjLC&f!;1B@X>XILY@sj!fuye2=(T2Ad*sjO6td@k@TI{L9@ESx(K0Lent{bsc3{=CQb-Kl$Qtz==cG&`$5x<-sV(Yu=+~D;_JHtquS<kWF2BI)!5DGjY?4{c4WoEo%JtgZ(PT<aO^3P$2#cBrWNrAFTr46MCv637S1Q`!9F2Id732$BG=ro8lemE7?N}<`mU2(7$H*RxW>M)ky4vjF?M<WAIwc_T<8sw4}NTJVGpL<z0(n@jjijHLwz!w(B8d7vbgeeWE0|D3tSA<*GQ1i>PoaD8leIuSDID^tk&X9K^e8~=rVrb@|)fBAfk2xy0H9uDou+_@@BN$rMXu9L<zRsI8|G&-6UF(I8qv_C0H(4Kg~F9Rkw@rbWxBSuk7POde*KEhP>l|%vhtMt^%IX9!Fe_^!y8C)M%mW%u=Hcm?L(6NxoX;$4r&f@J^>ocg1`WAVD>ffl9#<=`g5eF`(SDE4@!5G$Sp<m@8L`(~TA-8$y(o%{K(fV*#H<<;HOGc(qK^IRzBSIEZ~y85nDk3Vsm_l~9y`B1sb_nQGYqx+_T0if!lIWZY0*OEgAo--cL9KO^S^EG~v&Z#zlefa_oeXa)X^qvnB>B>+tj2j%J9+;mQ{jMYai<-~kU?VK};rFqNG7_Q5en_i*VX|drP<v4CT<kj^yuBoh(4M~3A-~LzM45j@N_pk$o(gFcxr3eW*dx-NXD&0h&&&?^jrg>r#rOw$nIez%299Rl}52e$q3QE$kQiwBBE>7&+h=1nZ1)csWy8Kgs9M|9q&VK3xksBu@WZ{y_phKoJ1!7K$ca~(8V;_dKR{N8P(sI&LaG}mQQAK8uz;ZUWidHGrK|)YkMpBIlN^*NF7KvX`4FrVV(qmkDt#uaQARKLy)dQKAUhgC)!A~@yk>vk%1$YAXjihLdVg6JZ8IrZ}TRmaFEdp51BhC%tCC*e6?h~!d8RBwk{@pH#N&?&hJeFl{MUPhlKUyNR9yA71nKFhlJgRYFT-9RkBuv#VU<Li{(JE>_E0sVN1b6IBG^Zd0>$DQRA6J0qWNyN*9Pq*`aXwvbc^74m^xDmwYqX-A4rP@_B|-X$QBXP=(H`*Mp->ncoVX4XK#`{oPu}w3DQTr3+AEofKT7YMt{Bx?=%?D&E4_ED_8s*bEs$6ojaH>R<T37jUhb~uXWj({2Qf-eSUuC$>2!Th@@n<#m6lVt)M<!fmer9_RNoJaVk`HZ4u%#xmvw-dr!off<m|;noi<NX%8mv=nZOryn?jZ9Gs>hBZope_f>p59b(g5q4#V2M;NC#`vxXfw0xBdQA@!`7Ew79{YcO+<zDbAGyRD!ePLFtsyG5BFBFLTGZBIuUC1y$th$JvMC+?q7aP^#U()EiG?3F;Ku+XQoU9cIpQ}_UtRbYHv3UPiOPEuj#5-_E1B(>&3E(wHyb>=1b02?8G1LdO5+XqoDJvpB`pqP<MQ}phnBgx7Q)YqUZyrXzPb71UjBga!E>}0$5?f9qax#4m|L>*szKS8D%J>fJimvdhbO%b#4I*#SeO_$`F;tYV|C(x}}tyVq8DD{^`gMK%RG@%otvnPzFWe{gXG!^Aq5+cF^Z0{1V`odJP3S{1e7v~IaqYf@3po06EUk5qnOCWy<%3B%`l%i?f_R=!7g!$WscMHrdACpgBDluj{T&IihS;rG$<<QL5ArxrKR2&C{wb#r*z12S)H>Z+O7g;#2CYII&c1p;DJQo{9_=y;NbL2kl^u9@;mWM(v6y-FGz8WKrB$1}bVrazj0%RotZJPAyc~pIr7Rw}^q!8OjD`+;gdX6NNC#@VV%9|fr(uQF@6p1S*Q5R>6B?9S>x*%ty88^(FeMtRlJ7A{mM9ag-a$5My`2;E=KnIaJ|1?`r`BSMLF$h4CE=4md7-VITU7dqOAy=tBfYMLy0;gIYPS632BmFeGLJdeJv0aB+432uy3&aTb0l~F!QIhKK!OJ!Bq4rjFa!Gi=72M>Ro*;r8z(}t}VFn^{pw52-om~GOA*Dmi+lc}CoT5sSi_A~2OY;!X9F@Ct3RiWzrln9q#O%|H;;K5&C4LR^X7ODRY<;8{q<G@<y9(};v-9X0aKcM}sd7%-6NA}2ok|V5ubMpv6X<iH1W65(XbCn`X+oz!eWfm0=hN&7lyUW{yonnvDa8vwY`E?F)Ki!@WV#bHqi6uT&GC#(lDV-|4YgvFQM*&m`Q#asP&#CRASfqhIA)Ye#bF2Oo-%$2(y0vr<4sSfM?qypo>QrPGsO!NCNRmm&a9b3#TRF<M!|e(|1>)_*L2O&nT_Qp<{UChMuJX6(YzuhvQhoHz0=FPu+6om16@i!lSInWl{txpw|Xq>>@6mYMg4htfas7Km0c#e9y1j2NxmTIcV1Y-0nAiSOrzbE?&*cKJKdb$n$4-mIcMYYH&{mU%6{MG7|GHg$!(AvpbU$y)iry>%o1qf1}Bv@$g6=$K$ukO=)D{rIMV4Itiq8}ATAsNfKA<*mjvsa_ywr<%b{Eg2RS(gmQ03}Gr4@%;V{>`UU6wv)bRUhsd0<UBSKyhjxFuKM`ezu>piE})z!0z(D*Ev({E=hJp*Cz9P}jm_AXH=9THVMY4uzZAHs5(&aPpTG&PnKOU!>x?_=wLTU4VX>G9M#GTRm%3Bz1uaT6J-uazrtkx-7QC<rrQqRAb}{5I?~MVLsV?f9lO*>>sm5RZvTLu4vs2<kmTSw=>V<<p9yMC*w9US_eH7-jcFaTUzWZ7sdbkEPK9ZSOt6K$AORx%G-Jzl1}$7%{3DjNI~ylqM!$Vn}UHgQlo=lBzUJsefITb+)b$sMBZ~AEh4yWvjWR?5vWAwc2VbIQLE6vK-@5uXmIXGH+m^XxpWK@ka3~LlvDQNoL5r1ZwXh>iyxIL{S_<Mj1yFAkhYd)2e*fj~JIX<qFs&b4`2@s_`uB&<`bI<y<pS`$D(8_G9S|pI_effSYU_-Q{hBrF>)1xo2}IK%bK5GhJ~x<?*yy3k*o&tbWgo9i8lyE*g?@v_2<@;dbiQv{IRb?V41vk#{b(1M7=vij;e-LXw+W?d!aI>Td1NEA4Bb)5u`ObpiKG<4dG@Y6zIn9S*Q&Eia?7VIYET>a-J8i?pAT3L|*?$ElYI=ucklpS+_oHa%3{)!c4T7ayz5)6MUU<_v1xNt!ob9bF}P9Z1d5f}(&8jR5_skfVf3qgR!39H$YV_00X*SLAr@Vv3bTM&e_D^uiD{w@GIVgZ5|Xs?V4vIb$$nyz!V*<QYn(HI;NkA@eJsrGR}f(J}(iMEdjCrEQS{@<9-{M5~>Y2a+DmD0<vF1i}`Im<T7?1;rTN{+~!yIf;gYrD91Q9r&<DS_H&y$iq*dR%kh*C!GN~&YHDEZ{|lY8MSW^VH}TTsQDg6A{EpYp1$k!VB2>E#lE~atutXG3;RU3*K+<gU&%IS?au|G%C0VuM%mv_@a3hZU0MkPa&=<pw!^bPae4=RAQBGx@i7(SY%B{6f+O|Z(Rw;%y1C~te4v8c7!m8hL<+wwEd@ZKLnx7&ojTVg2_TE>jusfheQt=_ys4Y3=`=}C|3HcN5<TFkgdeib1PI2maHTMh8Uks|zAU{Sg9#;QlKh53t;SxhJt*iYq`jO0>8B!IF0Vq8Pd1WP!Xjb7$StM`XpeV@@bYWI2YN8)h{O@)7$qSli_@pq3o)cd^4lcbtubPlw|YjJR8>%^hTGe#Rn^%N)w9HeWc3(hv3=P{XSY?X6?J-51EaH{6Y4tMv9QWA6(^IrV|m|FKZ#1$%Y?QDo!QpaR}*!>Hzfu#zDlIdV}z64|B(o@B2+a`<HyeGJsPx`tOGQW4aC^tM`Q@iCI%sxfRvhm((Hw91VfGz0Q``47b~Jt&a)0wZ3?6hs=7)*5h?9fudms5gk};24o^`MF1AU<HBz?~VhY<oDs1b1B^K@Rp!h*;=&td0`g;W{3^m1gcUlt;0O$7w8)2%P)^<Bd;(5R8Gd;FV8Gq`-zSl2{UUe7>Q)`9o`czVub)QMCM&8@AR)(DA>>}0*K__$*2JD+II7<;xP^IBS3rVK2n?j_Na8`cOg=d!|aMJuta4B&x%2G!xy)QFs#dFmn<vLP0abX1pJQY!+-hGt;4O76J)MF@M!+z>R)dvY%fbWZ%_Iq_%R3@7<9rKqhvpNy6AM5lu*6t}#9wwL?P>y&>)7$IY3TLNxrjJqeBb1TW3hJ#vbo#8tMqx$|zdG1lsQy%Bj2^Y3eJtd<Knq^5O-_5iyHjsJc$)`CFcUA@TpRB!R;SwjBX*2;A&41J(Y#`@YF~{R?ct?DAWcjNRb$3_tP6}9OLhP$TxVpwAPpp|)C*Y(qA^S4%TP4>!ngFAtg&8eX`5pp<W6P)ZF@T4vI;BKhgn%W<}jVaFV72o?G=r15^&fzoaSso`oiHz)aBq*>X58zqz{}6Pdi!`klpvCNV%nQCz+l0xXs!UB4IK7qO@KP^L%+zZ{-Mxs!y{-=9hDkMRO_Sg`Lu7v@A#9RL`$tu{e_6<UqZk$L4jFYjO~?g4ih?o(k6j_I*m5+~*=vL-ZzRGl`Y1B=wpimExi9aIs`$O((Nv(Dx+Ei{!A(s;)|tz-hIc2I{HA+C_v}6i5NdDOShk000EjV9|t7s99w$4k_!y2o}r(#b~O3JRFm{TJt@CaqXuA67}j+BFxapX>|6F@;QXDZi*w@PSS7Q%5%I40k%($A*F!Hr{^1WgnQM7P@*H&Qx{U&a7#3i()$FXfJqfvn)nTfKxY2^6rmxK6w&)fa`&AO*+|<pc1cne3jlygE=5<vtl7LHB9>%=ttkTI2%nd!4&6TWnQ_j|L%hL6wPy}zLzNI?Fg|MsKBa85qDt%4eTY;O0F(6WltzrN<S?_s!Gv+uR2CHy+*omp9l{)3e(gO^YZJwp4NPe3O`<@5t;tL(wMVn>0@4<7BEe$BQ7v5PQOKMz=tXzl`M}NFP>i`IH3{)vR?7`-US0QUocTja$}q_2zFRQ;pVEP{+GSPJs9S>QxGYDahIwB&DlyLg)zphx2hH{_Pkq7+rP-SW^`vkNDx!$}SUlsT)@P$~S18Emk|(Fc3(BGFC|6{c6g4YJOzF>M;KlwVt>$`K6x6w{jLX`ij7$H}xZ0oQaZNOfpUV8^8>kG3oo?UDVM*$b!I?_*PPsIX{#k~?rjn*K=}iJDoS0<3n6_l5@A4MZ_Xj{Ds7lL1Tw*1mNNq#eM?mQ;P=q<qM8YQ*E9&SGfvAu79Ov-j;L=W46WWAzTHIC(=g_AeYRG}Pe`+q5(L@Hs&4(*RAv?~500+%guo4Pg_ev8pJ(_1)K&O-r<jDM+z(Z<dS*;47(Cr`Kmv$!jOm;U!Y5s~<QVI=rONHvPR7o$Qm>4{<v`(9@674i&TD25%st3s5C{Cwrj~TvGm>N8XqUxy)+Yl#kh6>S4QYDztI~0C@ZCSupO*Vl3TnGQ{d5|eDo|$$lIe&iGN~c>hMOmWI@!6d|D4f4Y&f!FT7`Px11#3D#nwg$!U~LG@)@}5pvtm33xefN|^gF;1tkyIVx@ZXY1NBxL9l?-cD<G2XvS4QqoH;2=8o+ZW(3j4G-%NyU&hf)EjXp^Z8<mi>SJ57o*Rw`yok};&!oAkFILUS^Ar=%`DGJM^%`{WzL5OFb-nBX(B?3K)Xp`7_Z%!SY4GF2}q(D_qHd9|7$%!kI5YkZ|2jTa0-E0_p4m`>&e~7t<gw9gxxW5i!?|LZbv+bX<V85~qLp*@1p)PLJM$S%%EZh<^UM3Z@@LNF^Z3jZ>lvd|V?Hhh!5bFu$C-x(4!W;GrlbNY)X~RfmI<JeHt14bDcRuyTQ;Mgx%c09&(<`tvfG?>V9+RD+$|8~Tr5B^`q)H_P{33d;m309o15{}>56g0MJ;$<?fk8V}k$^@i42V$`z{9llI+T@cZ6L4@!dOrG#4HC3L8ZbH<%cCjB|PX^p-2n~wmmLP0U)j!Hb~add2LUM;Lo-&;StU5tQ;i1aju84tECEc<X(Rf;8llyq&E{BZ%&7C!d`%znmT@S+OsFRp(L#{<j^+cfwGDri*woRFL_i=n5rZkL_7;?w$4pIL)8<gW68B!@<?1*p_r*w3)Qv-o&*Yu47V36)E?Bh1x>bu%vnl=k#@zVDV^<ErD)ZaJ+d}~$uLfRTR|d{iX%9_*40E>lETDPStNPm#DTM~GCGRLjOgILHhPc}Ngz{4L3yGARYE?Mj9GIm1Tchcn|Z@u%6$9uKHlrJNiHd}@rpL4JQ3X0WPrtS@ErRJhDf|Hw5R1-h{~#2#N9&+42mrc4I;<p8rewE5*e(G?BK&tR$o;L&1pXEON8JA!g0JPwmX$HabU4E&(TpPi&Mjt`Y?OpXJXkA7iP|6DmL4yW;#s~3f3y4YS?dqm)y2KhpT9=f(j{s*aT~fwa|nRZBDwtJ+vseQem~VGc_TBP=U5<Im!wR4*pgev)a9;;CFv<gDni;Y-2s&mf7z<gXJk0A+6*>QhI13-~B&vXp7e'
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
