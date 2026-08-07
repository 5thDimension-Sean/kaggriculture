"""Kaggriculture agent — Route candidate ep=90681284 P1 score=155,112
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
    'c-rk<O>Y~?5&bVZ^I%f4?9EMU&#r}NEklw+Yz$$sKoSH9lEWsqApbpzB$C6a>Q}EmdPq4wi6ALXb$4}leY|@0<=-cN`SrKI|M|C*-+ejx{`2M4`(Hj?+}?e@8BXpOCx89*AAkDi!zT|f|NiT5fBW;l9$tSr`EdF8sq@A6pMU=4;^XB{7gr~XliLr&@abf+5+A&~UXR|s9ftQ0Z>~QK7k4L%H<P!28m_KCo-9u9@BgzH598D2yWfBQw0p{OG?FhT>*4n9QJ|04H+LT%Uv1x#FCHf2_T+wl{8EJPHj;h1xqkoo-Q7;+*Z=$EcDTCQy|rx0yZypg-tDKmsd*AACb*DLi1Yjtnh3iIh0lgU7?S~>{`@bePm{f`s-5Pdxg*BvqbQQ{mK0*D23HsFhV3NpJxh*Od%E_@eCiM5Ew(@J&+`0F?;d~Z>f+<wR_FD1LL$7on9l7)sE1j+xEpRJuQpHLeM^zhob;!yG<x>4G~*Er7q>tR|070oBP8BFYy0B%`ZGI|@=?k@*-E~BLZ_LWDp0=(75XAaq&$2#{)Cq7<VLGnGN1Bb8yzz>6FJf~LML|L&P*jzQMucT=X84L_MBWoOXWMvZ5Gj1G_$D_M;a%)chG7ko}|p<_9NxlnK4a%1-x)P0DTqMhTz{ey32gGWdS&DZ1mOZtE=JN-7h~3H+Pp;mw$YmzUm>&A<xt>1z+9lpKqe4MfYr#Z(jvp-8x>QC0LxbU3JBiHIAk;=w^F%y6eB&4vcU{Ts{c=Z`OardavBa2bd<0404(#_Q|0qNrn%AfY#aPdvtq-clMMigEGNLgsLgtIb@cA$^<*+NSWfPpL<9hev+lf1dmj}6j1T}CO&)6ZJhhbQ?t3#)fKpxe8+6TB^0@Odgx*7Hcp&<@e{AhRT4hlocD(H9P=m(9AF*qUe}D-2YLIZ4NaMOG|j4G;rPPW@Gnu9WAY;9YAgt=bedW8+uDm>UW)IB3CG3w!ER>yqRb0y$7B<CQX_c(;o{~G{yS@G;;Z?9XHmj&62**k&Iz*KcfUQ&l|=5oMzA@xY*MYZixpltEy{1k<r6EYolz<ORvQ5C&Ox77)3$_VGhVFS5AMC|Uq884AgyUzCZR*lv3|fwl6gr+qp4&?Q?-Nnmdy)gMU%hSO66otkmpNnHOAw#%@S!LEc<(z8J{71?j4PfIk%7f{_@98=0Cl|ihRvX+>AI7Tc%FOD4A={o&@wwnI=aJBURy2v9tFz`;BwCnlCMfmGT7V@cKO7NBh`6XbKBh%g2$za->L-Ijo&Q7s{YfDX>U<6SyC>q2aU_ZL2ZiGP_r(!ab{6qK@{#6gL`7W!c;40J*G<qjG)y@MrmI<Ayv~lkZ)n6>0^=?cL4A`upML=I4jsZdWU;?jtUn3G!e0ibY&^v{D`+!-mqemM`d&Wkm#wr!qI>lF(Nv*EC>MVn*n3N(CeBc)D$W;GsL8Ug)niQ0m+aZT!8_77Lq<0wJtDnJWhI+(>P`QHmklQ=lwpXdQvwro_T=q#Ru&y%bB62$V53CN->X(r5uyHal5mMZo0Au{fyalwVBGKsZm%yal_euB=h(7I80M0cy#ZFURV2G~kp%1nsbI<`0ABxhj^rqK#=XcR}OrRQ^oKDVl<6>uCz%aI72qP5Trb`i>Ggr2q!ab;Z_;2jp<gP@mO9o{p@+f$72=N)eUBG?v8r9Q|9BY)VZ}Nx@eU6b3tbONTEfeG=fYoRO8y7PRL4o=0f!`*KVAx%6=+EAV7_6|AUsUC`2?A<c7kMa|n*zxI-dBLqRf=U>JX8K;`3mbFs)AF!u{a!C6apclGYOWPO7F1Hho&wA)Ej8p_jF3zvjqPFq(=BkbLf;aOB{V>*sQI53-nq*e4EGV!NdcyPns4-t{4|~i3!o4((33Gy^_z-HwgP<tr;obp6m-@o3AS~Ku0kdyfn96nLr`248f|QI^L2F@CtEf6SAtk>{*>^u(Uj6>zq+cntKW`e)qjR?z=!=&x?Z`AD$8cDF4byarq*}1|qr9)Asi>Q)PQ%r49#E%RTaaWt7{+5syEPvP+u0?J3zq>&R!4(PW4D=Am<u1@R3V6*_n6Oe!|a(y7tJJ78@?Wy2}+ZB)rlFQ$~Azfos=Nz?zt%|pSHTAdXcgKx8qiP42`CV_ps!+chBM%zbQj-m>@Y!l@IZQ1ZvyEl$WS+-I0r#_o#3i=q(X;jDnfuX|{dXBer*u#Z7I0uA!~+xe9wz&Du(9bxP3$_e@z7w-c*U;KeaMNQb~Y;(6Xmf8aE0_Otf?3gBgyG!bg+h2;gTOzzixD%ItRXP~jULRT?gff;O|z|-kF1f)RqZKUteM!ob1QL}a-6<E&aiP03PwT7M|(gMdzpB!BphB1-)&tM@e6(I%E8pUP3U^)n*ux4giI~S*<$B7UK?MV&5p=lGa7WsS1PFmy5<Jd;w*#saO)oR8{>E1l0dH}8!lqGVW21Vj)8ltPMvi-0l)uK?2Nxr&|<OZ|}N09|v!WBQaFs-A_-TRyCPaG^-4{?tTweY;sAT6QY((gi(UOUwQyU=zdw)4GxA=U>?^y<tr(Wf;sBaicG7+&2t%}n!@P2Mdt(}{qdQW%$T3Aoh=AYaX#s<}KSgXeXU6Z2Z@xl__PW{}JODU0=#6FdjIm?`pMz5j|itmyaR>;R(_Dy>cnAZ#$+p?qi;;4BP?ZX>`<7}g=I+_)#p^vzZCo4#ST;Hm(ik^mi>D7`c7%~kVFWr#T3BC{O;CzFH($_50ua>c;uP=WtLLJq~^f*Lpgmt-*cnicF>J`U)(T~ei$gn#`kgg6TvuZ=s|(8zW&h=s(%YKI!Epu|(k>?c*+<50b3?1)&Qv!dPCc$?~df?M@i+UV3`9)yhIA+Ey)N5@c%mx3xJ@jh(;5GY&4=o|J<SMt~idTe4Zf@On?WYzsdwNZ)e(mQw6cjqcuaHn1_IG)B-<uwYODamtCkAr|Hj?15Kp`?he231|T@?kDLjSNp~PBpn5g2({3#-$LxavUD1=|e>+_(d*sj^JzW+z$mplnoRqx$8B$;Es~RGg1X57?NpQ%$&rQel@2iCVg&uSoNA6v}?94;wl3z-3WEjwp6&R9Y9e6X5&aqxHgmttSbktCPN!+P{S|>+}gH{o`TYNZ0NQK7C0ax*=dz=YY6EsCXMHpEM&5d0;0+X;wsiI81MvHVi6LxZh!)H%ox{Tp)d~pO0oBf3BwhS$zZ|SD0>yNV`EopDka;;5+G~Om46yj0sG&kn#w7GG7B!wqdB>XSH-`jf{u=8cRRWZgJyx|1KNCQXHu|88P&>K3+RYS1=(6!aav*Fs(Jeqt0iIUM~ahUPptOX{;$dl#-+s^4B^dJfIK*i=i{p?Lv27c_vq~2K^C?PC_q6`#V5hUmLngP)78!+!iGwbN<D(`h4Sgpy=x?4!VI%CQH<LWgdCdA2``6!MjS-UPFGBKNa(yD5W%7z+9ynI7qpE%MBT&I{PVLt<1T>IlK=;hNC=W$NwUJT%MwrRqD!e-`F%?fqd#(KJ$uH)r?=T&RZj!EDX{b-1v*uU!USzm`I|{EaraV;M4WpB_yqmtOeXrMx@wEpjvqoEhk<~3IDFW4rb&jy<#x6_;B{@cIhiuTHHv1XK~^4i_-Y3}+oP`c)CZdbVSZ;@sTOh6XUrGQm?J>27Y<M=iOvthJ}^tpvCMsDvWuk-vMZ;U=#Am=iM!?$D~){z>usNGqGiZ8vWaaEd|uzwf%f(oS{~O^rX0DR;$<0YuXZ_nvvB9pjH2OC3CMaDl*UH#lN>=oZFaJ09nbIl$m6~Okc)5+vLb>_W7?*#vM$zR6hCWJfc(tw74rEd@)#sF$8h^>UutOV`S}sM05Q`Un?p<R?Ll8>o>L|-rDM~DOl^*m^shCkS%&V^Edz?lvm$}%NfZKGnJCFkW;99o9?mNjB{7c#<OfwYH~)+|MR}cF(r20S-mqhc-Hh_wr8JW%$FY90tCXGSX3{@}=|Sl^n|$~czKA5)qq@pjP?7^?d_>DHg8J=#MW-bR42Pn2&Z5?VsJ9Qbs)Mjk8^Ic>X3VimKw>$Hp`a$=NTnIo6qJ(Mll=0IU9M35%4`pNZ6V5RkmIV|=_p$z^O8zoDquTHSP8)4(FC;;mcA@%Doq*Wi0kAdAD1+#6y&_^lG+K&9n|?~9egKz`Dk*d%72JXrRpc=_>;Oi(85fuD(-2+E#V84y5)BfR~u@wd@NaDB>xM}74NU-^Z)N_Rar8(KF2(Q;5S8Qz~RT1nqG6v;$siiTDm!N+R7FI0!C=x4wehY=tbC<Jk?Giz&+0Hf3P&nwgTVb>yUA?T|3OgW!?8)MKzL0*K6mKx#ht&QjUX^M+_Mt<t09Ln|rBBq_kH#l=9KWsHRZekr5i2hANQFAeE><rpLBCRWLKDB1m@?k#3N`b^~n8=-?dbJIec&(UV3K4}b@EWIP$?l4>J2NX$x3Au1$~F(xsBRY{m-f<hPcy!eU3_O5>ORl+NdB@Dy7XodQ%(8{Vq4LL=FPh7R$&hx;!8=vBsNV-P8wg;<|l#Jg6a6_Uqbx>f!QFV|HW4FyoVBa<3qr9-ZQ?BZ-<w7Mu>3oo<i>(fE8e)2i0-;nFvo*o`<69E{?tnYkpNwxG@I6VU^L&9E*%aI)M_4WIZA=jG3v0{d!Q>+b6{EqQs{*-jGnjxSm%pu@<g|Xb4?KMrq-T_`;U|N0+AF2;9B!>SZo_nT?;%Gwy3eB&7OT0b*eGo7!xXwPm!l70_q;lo7@G~gqrjHJC9RvNsA=M37XIAf$ZeHR351b4ZQ)JURM*l+$(O5?4+_&1jDsroM^y|VSM}bJNwBKRU?`Aj9&gLH0%OuDGx?5T(>py_K;&g{=QSY~B$sG3+7TrbhyHhf{Ir;BoD;7PX+XlSkcTLg`j|<|^~g`raJq4rW41q%DxrYm9QxO|fPh0o#fqoe8g0O8NJjR~+8gJC#Fp7m0n9)>+>&lQjtgh9xh7jPvZ$?&u@3MAnmm;!4Z$X0O#|I<5qew99cK8B`eNE!9dhTh@nLR1B;hZ*?(m#`xLgG9T2H6~x$G7<UnAk338ZPmW}JGaekRgIW5iUk@qPXL4y2x`r5+SHc*qg93O;Z#5YW#VGU+%&HGe{1i6qT0#8yKwvxwq2pWmll?^ir;{ql9%)jmq%`eOkhI6B$8;`4F5f!=8eq|m&sR%QJLlf5jLSl&FkXD5vuXdaY1uWoM!W?#dob1?lFs6g3ELlgH&m73G&_&NZBaL82DjTIM(!9ca4!OTj^(~K9Ka9anr9mQz-P@>;cb`tC?O&z)NWK6A79Ke8?T%_Xy)BB-CS{7gyLbVQLm+zVt3cwgZd4#es=)A7kJRGbcx^3`LprqujSQ?X&=Rgn?zXkX8p@dXIIa49cg&U{CT-*VTc94E4cN&BZKn@3wA_D>r)L8*nO~$Tc3WKcPmVPo)B^$1ou9MAYZn(D|J`bu~8$~CG%@~Ui7$zgzu^dcs38F!zB?va|u9eIv7E1N3uf#O0C_;_rz{*#}sBv@wmNwZ0%S>^`P;B5A>VLmB;S|eN&klrGx^p@}Kg?TR0!b`jS!qV%PUNIG=g;tUI9U~98F`S#-hG8<;P6$=vY_!9X(EGF+fE7t#VE9^n=rnyUpE1EHzM0gDZFhZDAjiYO7Ga$YF58d_!eb6vC_1j{B{&!qr7343sc+QF6;;Ab(ex1H);pAp>@#(K$p+vt%yvA3{zxzC^%Qvc{f1SkDO)_;Ll_AxNSS!@>>O8YjQ&<M+`t4oH-VqxIv=qBE~ZmbqO5a)X+Ren8C$E>2VTlfqJz-${V0TKyGWXi2|J9U`!xi4tZ$7*2eFSP(sXMyK&!#tLu-NlLmoh4A@?YBF5;8q$)tR<s4%aR(u!ji~&6$%GsPD@xeYeFtRF0?6=jtwyEsXJ*73QoWHhThaz|;8H<tklFArpbZg<?EQifShQm~k=@2ev?cUxWkg*2EM{3w?_7i3cSq8Y6&d9lpjpn&<j-bBlg=5XuR?4?q4H$h5#H3Gh$~d@CNxr!zVO|||1_cJ-a11Z04=BpGTh&-a;I5kPp{_onwr`WdqNq`P%d>X%Fyh=$H85vq^&(Yra{F+7e{h60o6lz(kwyJ16uAHaJme_O9l^sph^-%_d38J(7an|OA+izOXJ9cH@EPAp7qoIUW|;HtebcW%pDGb&EnlbMEd*g_$djeQ3lPnS7-9mw`4DR%q&_2soKVIF0{}2HVni^JPi6V75y}rmhviDCVGH9l6yFa?=crUe7K}la1AskGJIxO+13sbzVKwWwFliE&+~og}Frw4QC;)zs!g;lmzA>Pes<pvRPTgcnMqc!xxh1oU`_5&AWhDbKXAPv9)UfZO1%UYwOkL#V=wdM>9P89VwmQ2*y*?~+v9sA{8<*!GgZI=Iw%HY<Ludxya<LtT)&Yu)YzIo_BOphGXdC<~)gUB3Xn)Wr)Dep;A_b*$^H%loR7lX|S4YMNfIL-v&@V7LEe|Q6Pi~FkyN=<N^>B@}I|sW)SVB!~Y&JveXja?I3>Q_?*)bVwSE3LNUu)~>FcWOl%)`eF-<@t?kgK@U<sleyU^Q^L^4Tn0L^{kFBJZk0h=Ph|fYwE%j&MD68&EF@F0$@jRox+mb2c5rRM98`OvRHa%(WBB8-ZZAn}y?QbL03z033&MS=NFDvuU3JAdJEQa2ODh4>Mhhy@555u*9^uYg{-Km1FWcsy<wda+OwlzM_CjXW!~P=LI)W{U=Q_LbFKoyl0?{>~;_vPGME1S75F?`MiC=yi7>m8q`BIK+=c*{_;mxMQIM9(!Vp3U6qH>QC37M5uoTA0~~Q`Jg=wi{%Tqf?G(j<!ZMwf)FGh420100zw*B}p9I<*wVifXB;H;krt+1lAFC;y)1hUEoelfGn<XgY+tqU83wE<kujOT|UR3|y7ApWF-K?HtXCAXzHEIQ!M&)fgY{jR=Vh7W@0|B8TB^BRS)>2wB`~k$1kG-|gpIShOrB@%};pB=}9!rTE)v_iOqA5o)q0Q2Sj;v-hEr;geD(}{IM47*e0frIc^-@)#NDo;|o4u52Mo^+Dk6GX9r=*vQxYh3+9&K{uO#cF9+(QplveP5#G9}rv`(5UUX`e@lVhvYpMQQ7|T^C6+38R7SbT@G?EUfEY*?2H?)+`Q{V*%UI{*o`7=8IIeu&ibrRM}b_p7e>(Ev9F7tg+P_Z~01Zj`!6C91jy-WC+j*syY1Kl^JY&Q&(KcjEH|xO`S#n@VJ74CMds%35{^}y@CeNcJ<x%*svRmGfNF`mG8c1n!BpXz*^&W+o$5HLkruYe{P0i97#N~!Vvd6Qvm%;>K-#9MTicIY6`=h*U8d7GyO}I6<RylN^BTtJ_ouW!d=h1?MRnABMT@L$0*a-#RgQ30I(pqVsJUgjG5L!i(Cc}T_7NVF$y1Ye;Ui<Nb6C+xj;)$r5}=uVK2mOuL0)hU?L=eY(&{6m397xXo|m!I77IejRuFKuQHhgi!#j=*Tl{;;I5GqoH5yD1W%bbjt@3jb+4%*e?datF{Ka`*W4=_{Kkdurkg^N%xTa)36xIy82U*b1La3M)J`_}`<DjPOT_axk)N}Jg<f80XGBPT?utiffs{hf7T?X?jtI=w9uW&lHG%5V7|~tkg{-k7Y=?-Fh;Vds^gu+;6b_UGR$;F0ha}H7bPJED=OLt)%957N*ys?Kk!c0)9I&ZxM?)M7F`2Xd{$ip2BhNg5C30}f(|rk9ayJBvvTsr;s^WV@dGI-wcjJt))dF}_pi<EA|1cE7cCH;%Sw^Y`rVRo_!m$32?}Pz8DvnA$D5PRD8HsG8ud1idbpraKI3>(6gzOJC4Zn&x(+DU)@&q~}gmP+~A}O+I&<p+!^7-*dA^@cTWNrFlzDjw-;X*f_RE~-<G+P1gK|H8xvgMm20(HF55CehSP@H#XlfW~J=xcWJC95r=MGtTAQ}wPeLw)>E;KIJ=IyL#@G7UM=bItp(g~sF{+xUp%Z_8)kJ-AlarOe=wW_uw{D=X@6r(!D`=s8>DQRAd^)+R=%>ZNCB6WL(BW9>w|C0-i{<WNH0gDI`Pq-$bYE)8f|7;KW}*>JGye26`cSs>^CnS)MJN8<txf77;guGJ<^;}3zXj1^3<TlWR#St$~tOa*-fhFhzjgD-cll?J&sE_o=Gbzk!_`q?U_9T!BGt>jVU+zQg4#6dqErE06Zk@N^j3Uhx7|B{JQP_i4rXpB-Kw{A=3>T~AkN*#+Eniw(-S_r6>0GWCq;>E<WeCU>D$3VSB+^&9S4_NZ{zLcwI^P>y&;2e3;QAV4N4&s71aL|R?j2W2mrL#U=+K~K(L+akS4T6s#w5LBOF>dF^HVw1D@tpL>*5{2}B+P?kBu9^{`J492N6oOAfZb3Z-|>cVD;vL=?b0kg#x+BePrLVsbFK_%4M8kpgq5_QT^#SQT5y>m-Y>Xkw>VU=f=UASi5F~wt{@Y(1N&(}Qxp#dbTe}w9$a^Hxru0^Xp1U0dNin6T&DTEWb25wnll&|30M?+WM~XpRNtWGy(eBt=Kj0`gHdGiXyHZ&pjm651Z4YN2^)@|C(1?Og&P{1P4>4Z%X+uN+<U{nK3PU<z*`MDpQuw5PXQu+fkzN<vK6?F0VAV$T(k>+VpqrFFC;Syf{THFV;F}>w3&?6oYRffPGz`-DP>ebwsK_7=A?>NtnCi$!7#Q#<Aw2eGWuo!9#hRMsbC*$kcdHP5JpFPEB<KU8z-C4zLu^|k2Wf(jOq2uYzG*r6{|#xaS6SFGM~=x=jzGl6Si~Tz3>zsPiH+}K=k-p<>9{K73FKy-S8mRJc{HmYk9{acU;1C?N!I2FbPINzn%sZ*6^!RwIr1xbzS0=obV9W=S6EZ7NEC4MmEWaV@1KOFsXgFBO!^Co~;Vw)8|?t7|R}KeU6&BBmr8M!w;!4AnPzNOwF@|pkbv-Zdwi9lfn?>u#{h93zOu1Mg8D;DQ4?k^-Tu13?N$Frf*T0Sytb@T$)^S2V-O=I$c|iXb`hWTMWel*z5@F-XhTc2<$)Qs0GSR155M~;_l{HaWKxoBZ6LV#?WqZcm#*vATvewuZH}=kTqoVIivk&7iR>$I*8LiS8d({!G|WXaZrpTN5|>p8MJ!&=E@jY*aqy?8)Lgzx6f+k(9U^)%)`-ny-hp8&Q*;<NF-0Q^@_!R?odj|pb3c)F|m115wzz`7eVHz(XuRwwrH~B2Y9g_n68qnh5M9m+@mJk*tTyS#OWaQfc8|*Fkzk!7j(@`+9>9H|6dO3$>I'
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
