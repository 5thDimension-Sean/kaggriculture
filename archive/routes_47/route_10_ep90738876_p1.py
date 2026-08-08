"""Kaggriculture agent — Route candidate ep=90738876 P1 score=144,544
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
    'c-rk<U2hyoa{MoR<^$)06zMmvG-nCN6$MJV!FfR}7VsGcjPt|VZ^r$1Yei0XPiJIgWLEVowYs;#kkeh2Rb8DK85#N0|DFBEFTei%Z@-@X%TH$?Za;oJdptk;&tLxg-~Z>!7hgX9{g+?=>u>-2<?~NxZ{I!azWi1D@Wbc7{(SrX-H*3-XXj@h-|luF&d%5753ld{ldnJSc5l9XxqrL6{d9KzYWDSyySw}MXXmT+<KsWhk4F9O^`Ad~m|Sfb|4(Q8-N#Q~$MgRF;nUl%pPnZ<`Q3DQPd_-G_-}*w@Noa;^XpIJ@XRoN`26nf&Cg%1{^|2q8%#zq-kc3%xbXOY({apaeRunM_dIF+X6BFN4$romTzWo5cnkNR$gPO&h86rW;rFBck4^Y&i>HNbwBO-APy6lbp1A$AdpN%1pMKku(@{PDcgmdOb;n5_Zt(i{*?7<Y)X8|`q=q{U|6{j)I0L&Tz*crc%znmK>F5Tc_3Va-&3L$8(tN{CXfPk$YQs*@x7z%=qSeNo(8XBzL7h)HvfBKeBwB6qm2Nh3t4`JebMP%<{xo^G3dRBk@ogkLkYp<6Lnjm25025gjeBORZsR`waQe$WpCyii2mPFl>uwGIkh-4no1PEQrfbZP*57L!1^b$799*hD#AJ52?F-Xm9Ix;1?sl&~{rsoh!>4z5@BZ!h<yE=j$NSIi%hZ2ZZyxSHEc-Nl+}-^ax=n^WMsSO4i0}kjHD2$<JaNqM<(-q+x4muxV%p?xQZa_Y>T*;djvVJJJ-y86tn1gCpKnLkLn~lBENIg4;czUqdJF@UaUj6|wLV?Ly{%D4C(IhP>$IEf9~&WYIOZUN*a(?hlYp+Y_PwSJ!j|uJ-ryuzXyR@})al-HCjd@&`0(`K%ia1rm^FWqE3xomHXyhDW1654+P~C0_r3nNbhVj(yUqBwTh+hij_wv`(-hB2Ns2vROhFx)0|jm|zr7GCrCinIE!)g>ltrp}`*W1Ex2;eB#N5i+-zvAXMzk{mIZ1fXR-Jfq$HEjdZ!-2;uiuc^G=$)Lz;5FGTB5>D$Cq~EMV1(lK~H{%F}ygVfW+o^Zxe9n{?jPEvRW^42;X#KaH-46xkArRcHaJ7Jm^c0c-F^*o(5>WeQ3(#TF8kWm@Z9DG@&{*Oa*w=F@(6B_3R`^nvmikCBSh;9cw_z1$R)2TZHLu76ZtKzrDSE_>1ZYZv>?D+4<*F*GV<Q@ZddAJUidqRo<Z;{x}we(q>IF{XGttF=LS21^H6uGK0CKC{F;xnUUt}pUJn5Urj%OOGkqyP&T3w;!Kvn%pw%b!~Ld<Zf63YzRU^`MxmFWlb=0n#iJ*{8gg8-*mj`@ZYBnH#51L1_*-sE3=;rXp3f;frD3){IcK{2o#l*Yo<?L3ub4|`UK_uh0pqL&IW-ST!C@)@iK$n?(?wDPLratzW*9ZNv2$viX)>hn6A$!D4a}ys!ht1iUNN9s4-pR6#l#v8#^i)O1ghm|u7=Ft%THQD`^)yw9{&2OZ|J`1AF-b-PVbiDvag6mgYrHGViT&^hm9K<s3RGTASay}LAgM&D?1}c!?G)Qx@pI&y-8$F?6et(q@N+1ToPD$7&EAdLYzy4E`AhN9H7EAYGQ9?{TDmdWVn_=9qa{_2wjisn$2NtO;&E-I&gAr#V&TR5ox$;mbrU!8OFHx_jg|_=5dI7HTk~ce%;-^f0Hlvj{~=PJwNt$kh>tdi8r&v&&N*>xBDM<4-bDmJHL+K$g~XJ&;Bfzwwbe##`D*gI7o^CcwsEQ-gq=-?x9$EyfXOPVIV^WWcEKxTidHT_kpeOwZrT_TzsCHLs^K)9&cR(Q0{`>)qQERz<~jl07;X<5)1Rlk)e+U!Z!1K2AxJJMlzm!#_`D(Y@`-$w%K&UIu0M^3Dh79)8LfLOA9KL&=Dwr>s!L|O)ROk8ajxx3z--k!$d|m3tJP6Sy<Og!tN+0W876npGL1&2*wkG1r9uUsZPx|jwn7#I$96y{LrHFn4!~H2_eyB?}~h{p8L*@t%-_OGe?uGggQe~Yo*_fQ7h%p>qH#3s}fU<3!zP;m2D!NnjYuy1uqJbHQ@8Bi};N(N^99Ne?0KyCm{;BeiSpO&Ygxi0DrV?WH*m`fPn5a44eK}g&&t$S|gt}e?#o%jtm%EmqC(+1;LG7S38=(eG$h+MFv<bi4?;;>jLuJLJQ8l&yb!J8CuR9U1VR*Ji=wjhdba-`xKI|ChpCSyW5!M)WxO%%{C7_Vmvv-D@O(`tUA(8cF4U1t3L6Rd^VcKtQ3Z6d^p0wa~>UZV!EONI8$0mvVbkfvays!Tp+h<gh1gG1&eC`)|Q6intX_nTN#0zps>#s<aJ7-pOs<35YoS^RBzcegTpB1Qb^UD2TR_VjU|Mh=Tc()y6(<|H-EY|44-~{clT$&<bmgOzX6f3nzCJUMvB5yl8Ph)bS#!n7e2qxH>IGJi+WFk)>lqGa+MEe*J?1kY6@nbKGX<cR#2fOhMiw7^=_PL7326S7qS+UhqD@`0O;>G5|U}K`H(|`Pm7tIoXL2l+EM{`N{^N3fD6=RyKH13{X~r)l@v(ZHWZKT1B%AvP`QFn(p&Q=k}PV)#{xUTE@7C;6!Xk^k4H;bW)@gaMz9=gxC>ELi;t(N-fOeJh@Qb+?qO_%&j~)MF-R5>z7}><xXD6iEj2>u-y)8>tA@VB>P7IFv`n4XvPpxb*C2@BzuXvR#J=rvf*-xi)FKUYsy+ODTBTXWKN}+|(KO3?C{f-9eR-(|d>G(fXCgn#y~OEDkQ!Nt9m*WdVH7l-*)SYM34~=Q`%-5m5epk7+iy4xxx7-=*&i%oS4!qwR=I+l&uiDpN=Nuvk0lDEAW#nWx|l)iNmWG#1fC>XTVIT$f#V2#C^|5DTBQhkn|}IbeBo_a3;$o*p9u;ii@_+!#t@&r6jHe$2AweA06?6&uG~ZMfnu3Qct~{}q$(tWK3QG~$cisEPJV!oBLO}F!=mP6ywc0IH60T)#2~3V`@n~rd~5<9211C&!wQd^rOAeNsOM2wC`u4T_$k+BiT7;$P=kFXFX&t)N3!0u0`4h`ro1Wb&7%Zg?(1PHEawL%aQG@wITKdIc7tdn+$>4o?O7}NY`x8e6RX~olA>CPWYpmpfK7<h%WDteU(qpGr7KTUyz8)O*ES&iPHluBbs<6wd5v`*vmi9$6(RbFE%O4{#92hWP}n>z=J9JDS)?jW2+hATBSG}Ra+85I>B6w!Ej<x^dqr$tkWY{6*#iC(n3rD+*GGJw(iv&}9TL)HErf$iuwxs^O>dGV85WXNKI=4U8jz5T{b(~&(Fa;AcP(C>ZuQxz6RlcEK({UtJ)vs#&KdB-$GON8J#VZnXT`@K%GCozsk8x{0NyHqK4a#(O68?CT&NNi5KdJNhQ6UG**iSoeR!o)h_4Ato)^n<S+s%Ube#ay*ABX@4x<i9bb9ct>qMH2R_rTx`mY|V1pes3@Or{$2ojW3t<^^~m|{Ky$K6&R28n*56S;_eV=OJRA#A-wxJw1CEXtf2=M+J<5`o=9GkG)c1WmM7b&e1tjCsIKr<KQ*SjCq@j)gRucEsND$4tb~-!$zAy~tjAF5<SQa$%cXI{~JzSG-W&@cc%XDn=F{83FJ=w^ut4Jk^mk^&z1xv4{?Xi}7E1^(Ply)Ed%7ESE*_)-sGrYIv({rE*_Fw0cvSEa){31J#<#ML<<V!oDOyy3{96^Z{ep;#eY4fx5J=tV{$)x{3~+S0?lxna)EC=_a#sb{_?tmKLn(vMhp-^TuM!H$bUZI;5oOr)%X?q_K<+dZpyAnes_ZGi|M#4*KLw1;vIBpdnNzt1(RkpGcZhncz=YVi|Lf4wK2qH2<>R-I!@*zCFVKily|!`@m-y06a^7%vMctq%x?4y<0@G`Bsf{gbhN}kocuM5+P9`PxeqTNg8N(-4aw-fxoPh+5yB`Gg1&!q#-3k*D>L#(wZk75wbO;HcRt*Y=AdAKDN1_FCE=&^3mNYZbs8Xt{@xKW$7hNQfrhL-HSxQ!Z(|BY`wp-0w64*V!nI*{UF)jyalNBGp|O)`mosB?hOx`uGwBI$tV6-wTUTBXOpj7hC;Ip6&*;D`;h7HLT*cSzjv|{f~2F*m_?1#X9ehJYXO)T7=UR#m*lqmQjSpNuy6oSItG8>h|LN;GtcF*PzGRoe89Ba`^$sS!T_zQg4<`IM`s>MQwBGjE{sN}B9MmAx)|dEW&#uiP3D(Fay@J&E1wmsP!hs}Fc>6B?&${02S1HHp0-+#C!6HD@seEYQj$x^8g*1_TgP?$ZDMTGKx^*uFV=z5ExYeiSWjzoXVFBT#8aF($ryEA!|lBa`95hRRt-RH+Ofc$)=}`?Tc#hQl3PFhFi(0eS4&NzkyI;|P91lcDZ0|4X+Z>YUE^KR)K~=oC)RU~H${Rl%VaZxAiW`}c=ec3zNY21@ropdA(f}Px+2SQHc|YlYJ+GumC9P}J^QsH)j9N~NGvS325%(7N`3MZ*Y&neIe(o0j*d_i2S$KeWHLbbEC45=+<;hc(K8G%rOMW*f5aTea>))c?UCo;!SOcdMi5Y~suU-32(2lU6AiO9(;{`U4ajVZCuG#z1cR{qtT??Z^FlJn;*!Z7)q|wa*(q{B#Id2vvXep3_B>ICTH_O>lh~|)k0r%--E&S^Q_}LKj@c<sPbqlHsTNXb&OjlVW@~s3ouyO!L|orAPdXPyTbd4RAxWT1mp)=g5_m*du?sCzN+hu`oKJ?AC?}-W#*NEn6Yatkq?un$WgghrGRlMsHXRTG+ZfUerRHEsg{bUy(Gz{LGKw^tB^24EO^^%b!Nc2QDqJx!T4^BoMhfB<Xbdd#Z5ss78pxK-t*!C}cVEwl)w*xyvAMi%EvRuzzuC45iEkgfWG&ZW;oH(m;xraMY8rSL`g9{)I@6o}&t|!#s6{2Lw-gxAmXkK;_K3(0MB5}1pqlL?OAVkKJ5+^`*<lTx(~yj3_|JJ1IDEZ))|M(JQ=lR)<?5*V9Qr^AZxTq#%cmZ3)C*#d<J~a*nYbY`<0Z9Vwz3BJ^+e^%bYA6S&IL^T6II&VHwgW264iZ}^2ZpH$14xNZ>{treX45+S{3~wU}3HWLV`i;08gNch4%#NX~Im|pAk-i1(n&-P=RPH13(mfirJ(#wk`);5R`*Fqv;x&U*(!+Da#Ve)`3xm9fmi_bCC{=H5*Q*eyx!hmm;){uVj|7jodOK!bgyZl|-WMsr7wS`UfJ_rAq?0ozms&mzXZ+pCAmqOiJ8|E8{$K@9d~~`(_&oPY^CNr_}<faOPIg1ZtnOw@aII`%O`5><QA`LH7?WKC0xkwf7S3=@Z4pozmE(2ahASoJe5;k6fu&!y^bg_v{*4Fw=_49Zj0hGNP0#$e8Y0ud;%*lJ9kbsc;W<%6^9U53R1OtZ7Ae9gP=f$SV6z>bnfaf?o5gwL_o#Dt0`ANRl5~;rMeciu4SvR-=#CnFy`sgBYDi%$aSZxd?kPW}onUGE?snrHs6#I#hm(nQ_>BLsDkk>R3*j?_76+e&GZWs07bg@T9hMNRBX(CZ5N_^a8uyg2nZ$eJ%HEHHnWJICaVfds?fnocms#f~j6EL0yoaF1NSNC4S>vW;uD?R`VLCfY(x*xV1-gsRlF|$y4+zntJb2-JRPXH*Rw+)<twqL9>3u6bho8%7xmSON4_!m6E(dso2OuRmWz>pd_Ut)!{qGC(3d2x(<-mmLoGSJ<_*v5UY6v4<<_-Fpt&ES9Y2P2vW!y%S$r6=#Mdg7he>xf0&FJ+Lkse;?Nibnnka^BXU<>vCKoDdj_(f+NA2*SLkp!Hb1EK^rT(eHEGf%$FXFR+kB!gE+RGg1ixceEiiQT*4xykA-AY7SeEytXg{k_LT&CcLE>}y@H&=_g*zB-v_#V}(ND@v$%|*~0z~mPm5G!Ut@1mkHCqoJs!|z$P}`N;a|vM!*1(A<Cl4QL8)phrY!_2ajt{))hvri!&7C;5LYC04)E)ejKM|M6F9zYje72}OkS$JYKnqBA%Rc2K{-&?YmJw%~zrekk<z$d|=0Y9Q8EfO1TMY_BFkRwwFikdz6|4iT(9iT{X@YE|Mo>6!AK_0f64j~MHw&Vv{#}ZdROYQWiPlM3RU8%Pm!)sf2++RMlnCgY!GDz?rzZV83GId<Gh7snw{U_6;%Xs>PA!k?7#8aZ&MU@Q<Qx1lxk6vV;3K|pq0_g8*!4&_J|5`G`CY`ry5MV}ZL1Cl(HByrt$@E}1Ubc7*a{eENO5y35IFy&OS2=ANslm(V%Q4cxoGXM1&MNo0!(fDq^mjJ3s#i&14zxouHiAWyTck<_K7QIlwkdp)I&lPQ5SVAD7@(MkV3EN26$Xcz3pPnjVv>W;XqISN$H|81W1PLZ5thWyJ}`8O|Q1P0-LgjOodljbP8?F^@+hQpTok7ajsN`4<$#LD@xeks$h=tn}&!xh$OC{1ZdMt1FMpwh*G7{0J~3JS!E`67h7_X!)ygWP+VzVZ=+X7=om|ims6o&0@RI#VqSf~I#w2DH(4xu&IMNYUAh%-6C2Ls7DPZK^q!9|p|hbSwa}LEH}Hx$-)E-?PEs5ytKHhQMFHEv6j5U(3vB5u{IQ(YKkPaINN`*@)cZ*sM2fN~T4qU=lN3c)qh+;YCpsdz5<eoKLMy;nRH7Bd@&}Q0D;6|#^!l%8g^qt0zqe~`PtjXBsF$%jz@1{bU#DJ3$b^h2z6g<oUGU1Ig3E~#O#mdsT3~K*d9-=<S{XXPGOLDXX9_iU%$$YbM?nK8fKfHhlpq-$4t{Q;9+kbG!!L2XLLe&n?-Y)-HKclldO(vUdIy{}2_4t6VoqVvEFR@O&;)dofw7E65?Kwxf3u~fMP*qT_0v~N%}#6|TbtnUlEX{4)Un87I|SkvCt<Lye|H93xk_&xW*CxHa2>nq&~i$R6()Sut)-5IJGhhpSBJ-HLJPFm0UD^HEDYT?oqOzn9T4(9w1Kwt3PFyH-3F>Tm0s$#We)@uA!@}<8X=NO6wHWa(6Vv^???a#|2?rM(q&6BYl$?k4<VV<CKjVnHkp_>5c~(_59r$)J=Ttduw;1;aL_c!rLGpSR&T`GmY=|=G`TEOL(5vDcrtnfiC9odQkirKZ4g`HWE64iVUd%598+39Bf_N3Jd%3?KRzV}99Hc~)d1Q=69AiC5*y8d&Q6M|k%X+U?&W47e%#&Nzdw$#JZUdg+bPgd@>H=DJ*Ozn4a3yyIHa)UW$^WD|83s37k}mc4M)IF%d_4(vF>J-T_&MMJAw)T?4qXsUGF;O@}rU<oY@aR6N&97N+35&Q|DN22@iLeiQ>2rEGk~AqNtQddEJr}?Q)#1%}F?2o0kdytP(62pSi@kGxefrU3Nl;1bu1$FE5tHMeE^+S@Jxt#5U@~>yoPC6kj#X;!2evJa$2@z#JWCm(@SPb@S8qUALW2)$$l3TIXE9)~r^PwRvpnLY*ukrR*gd=GN$I8BP=JQ_UoNJqSdVO>W>dT|TxozJ@YyFqWixPoxu6pI!P&sIbtQQOhddX%1Apj@OBODy^dmvc#+F!zFwH;cTuS6OEoY=O!vlrJr0zUC1n~_Uvxx795`<@q<^R(P`(ML<y1dG6D!&YLpNZp(oC8R@xMhKH_K*^&^+ski(s%O2Dya!9HYNRMWh@9oBm>bw}!O_{j_XK~b11`~>#XDbaix9z)ZcGpO@AEo&wtj_^k~f#Iz>o10Lq(5?JeZ}O!xqsSW-s>r1tJ&EF`oljabNf$h`<F6zLa_bT<2ls~b#&XGN#z}?EV{@yw=f~P)Fg6z+9qa<+Hrmm{%afplon_8Mz_VTcOe2St(ZMF<4``lIK*$HUvXy^LOfg&h7j%-US12}Z2O^3d@(|j_nd>kZN}4g0AgknFVuu9|h{bELeMxC#hH0QN#SlX<_MZZWo|RC^p(`Vf(JjaxN|}@AO`+V~S8hiYxIsYFRTCGAt9;{i2anO4cmL{nl3ZK{%uSDVNHMRjCvDd_p^zA*n=_<NwJ)^RMzL=H$}8}&{_Ocn@F6uop~918t**Us1=N^ei-^Hjmp10i{D&n9XNC_XpJ!E+k9L3|HWywNm<z`^K_d&M;xj&&YrGOd%~3(op5arX78N6gomM*?FtaMmR7>_NDD-dR(Aj#s0SW~c1PGwv)2P;x?ns#FriH1-l-eR9eBXY1u~&IG9>W*;NPsjx58q-f1D?OgVo~^4W-s0_@uYTWWwln-wiw@RIpwWxT?0wCF$g+r-M?J6(ze#TQ{hR~wQMm|nzprm5t>va%x4{?y3n%Prn0H%E$?%s2DCenvX}d?upkaZRkF0sgj6JrtM)eQYLQ-ljO9Zs69onE<(0KktrTU}4%xv$)md8UTUO1|dZq7kt<`BWXT}Fq=eug7nK7U>itQvVeqp1oo484dCe?`MC@F9x71C;iI<01bJ(#I(fOvHoDz5Z=S4ng^X)UMN1ciXlj=k9GLE5kJ9%SJ}Wbqt3rUHMe8DpoS*J7J&$PSx{;^06lhR%#xAaSU!E;3|6XJQPL<Y$nUv>?B%vj#oJ1+TF63YY>UvQ}oRqe#(?D==v2S8bYJJW~*r)siyJoN6go`KmB#4ridC1{c1YB*A@UkxC_S%Ckgh=Sk_YeFP~dQd;w`cz6(l&0(EEw9SrxXP1@a9wi~R))Hzx=i_`0>dOO|)EYtTsu1Fa>&HIDp;yk6afA|%@6fpevFZRwUj2R*p&Q!3s7JrfZKboJp+YqmlQuNRER(||d@)@txEw1C0D~6S$+N<glKmPnh{dxF^e`cNSfhza8zLB7qA^m&hi=7^IeEeas?4qIvo~mdIAC#;$V{%2O2}4A^6#YBGe}xeP{2i4QUhk7C*R@J)y2y+Y$jc&mnwsUG28tea)MY(CbGr#ZGtK>cOr=_7AQOzl?hRarGdnwxDv`sgQF}_ouCuuZ2f@?4d!-P&cF8X3AxFd2{6zSCuW37=yoEn%<QPWN*Ucn)jmB`#Oc8kN1^H*^pVT5)O$TvW)2df*`cG5ky?0bYQ3r|tVGId;8BId{Vwjg*xWV|jgOMR7*{Q3=a3lpMv%Z0p*qTElT}Z_Zwu49Dz~-__nRCmBo*X3u?}tf#eVwiA|KikvkPo7I}cfKe(x*gv6pyl*cc(&8Z>Crwb|r$%_J=yj!<WQ+yM!CF$mS^HOqRF-@ZwqvQ@~p`lfWq(lhZvgr!u+B)VID9?P)ZSVbhGx^cmu1RZCoZN(r_>D@`Cx%Ae1TXOW51jcylL%KkgeiB1YY;GH!=f<in<M=Tw$(9R3L-9VfDdbilfAMvZ`mKs2uQa-o)`yFfo&<eAvL=kr<@90bDk?^ZY)FPMl(H|YZ>9b}2W^GzXhTU!T4Ri%mJz5+b@gCWrv$Vp=UWJ2N<zVE`eLjQk-dHx4@=uz?7vE#3vokffofut1L+PTY?X^xsa+3AeLxclK$GzpJ1qd0v1}|!7o{bA`?wEP>M3WL7usi&Kf|=hgw~z(5Pl0g?@-p5rY*}TN`-X@wDstKha*3HyU^K&bgE5E5erK_1v(&no9U`707}lZi&Pt(*oK$2HUM&m1YioeQRE>!y>{TTRWmC0go3?tsA4yun))2peKaC-*Dt4aK!2jx`Xn-8WjXndyfDb6%HVKN;jA+zSHMVy%JdGErb^9bqox>fywdXiTDGyb#u$4ZMD?t;;WE}(ki2G_gd%IHAgifEB@ER#OcvCcCB(H$QrYliu|$kqNCkvbLe5@FIxV50@;ntgfML;?q%;@cZd(t6`LO6XP!5zTlOqO8P2`&f%aJHbP!@pdgNN*EUdj%j!BKbF8o<LWz9$$};|fqJEvH6?ZCrOLjp!WP%70wRkxgx@8NN--PJ_(@{E6;$Hg-MC=2{a`2h)9u)Ivp@S?7u>$t~vM=?!2B`#c$+!Wif%h`EU4fWWOth;HwzygeA<hisjFQrX^i;ItH-Ouxu>m9VXi%eQsag=`HYWWd=IfC#(g$(R<8FwB&|9?;Qbky2DVXy=!bf@>DKJBMjY1(C3)*D#m(=ml@5amf!a%1)EFQxygBQ~b2e$`Hk_u^2uA<-oIeox_p74^CPh*J-YG>`W+2j&V_pN-6Q7>75gZ-78JP>SHWKves6k{=t0ktfW07mvt)Ci51pS)vJskzf`AarKugN3e_eP>qHyim>kiHP!TBU4>-rUJ<H=We*<f6H5E0uBA>>Zj%N<^0zIm6mc<&4tcBgbVTdLJ8<OZpsdXi1nTqVls1~lYA&_xU(N=&iM~4VyL}WL`Uebk*5JkEbcw>(m(u2$zVQ6YgFs(?pgQ3wR0vJ>+EY0j>fC<XQNh0>gb@thu8~YK;pqi+u1=t*nh-yMwlNp{9s+Fyz2o+J43{9P1?_*GgD)JSk1oBih;U$J~PMJ^c;K$km1ci%WdK{k;`h%~pDBN-^-z0K%upn6gh#5R3LPK@h6(BtE-;_OV%Cx@(QkK}FH}aZno8T9_X%j8Dn3k+L<V29d0*(^s(AGAiZ;RA83sMP<2pr$AH0x$X-+d)E$+Y<hH)PJTs0gXpX;o@-AHMBWx#UEknlUfF8F5g1Bnr6(Plg+-(@+9|TfJ2;)AR}1!}Oii11sUUZTYRoI?CIWA#s~|rJcl=3Q|=fE1A>F`RiHnYe7f_l1Q{wVU*hiw;*{)yG$t!5>s72r%K0#9e!HO8@8Az^D0iQd$U}!&NSr->_cQUYGeD>uWu8JkN<f5f2ukNR{'
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
