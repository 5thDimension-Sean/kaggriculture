"""Kaggriculture agent — Route candidate ep=90630506 P0 score=144,167
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
    'c-rk<%WhjqlKmI0wJ@nixn`%f*=?g$mLbVQ^b~|b0n?2J20e@F-VNs8M`cOm<&B6FCmu;s9<NMOByVJ9WM({0ocQ^FPX6}mZ~yq~Zzuou^U3F{yStNz)04md`rrTg&&M|&U;g9Q-~Q{b|9X7=^T~&gx2wm$axeby<uAWnefs#*)%D5g$-A5N$>~zOefMFt`aJo=-D>sz@$L18)z$sU=?}BFe_CDNd^$N@Y(D<^_U8SUclX<GTs%Dd@9EBXKEC_&m(SZLEhc08`DDGiyZ<Wdr<>dR4_{wx-kQDGort^D_4W3t3-hU)4@{rB`RjC2K3>27<#F=wzdX+#Cx<!-LY(KH&_viyi~Y#l9Ds*Df8}ia$mhR4k!HK(%Hq%8nm&8J*4J0>R-2jJd4wFB_E7N(JnWCt{joc_&tm+pQ@{V#<NrV1Z}yD-PUOk&uI3XsljU)$uI^X2vsW(<-F|8&2AbK~S+o&iD*5W_&Ukw0m$yGCr)l$u&5OI6FV1wyCn$=(k$CgNz0)<<iS}6&Dj?-op8515xA0qe(TY_jO&&j!!=N-<&sxJQ^Xc@{iTOgxCO2o##LW-F0W(PGn|udcBN@Fz)0a6Hp5K|sxqZiaRPF)FWNrR5dt`D1TY1F~KfMV2F8U}iufW${w2=9%b<qZHNc7R0>+99K`(OUJy1oB+{qaA(&RX{n_94&Q$O9jJInTa}UKTyFRla`|dbH0@%w!2p&uw=$;BP*E;2ip!k)0m;w(Td>Y<~D{)+xh!AF~lgO;bb$IZX|oYv&|MSDd$r#Mu{nv^~RH`_`2~nP4PB*A#D^Bu_wPf&+7;OmV=|9InIC{pgzDi3%jl&bj-X^z!!o<btUkxw;bfQtX&*xP&rS&j>xt-NuEpFMr|<xk}Q<TkziSp5q>6i34ol-5Z)Q{~)(-+SHV}N7G()EbRV&OJB*l9J3cCSA)r?%(HKCTl;jBmlFG7!f|naaG05X+U5n?(bdA8WQ5p1T;2YA{LY%2_-fStS(J2~L@^_SbAqh*?QhQ$8JWA!2qc%5O{&#qvC<2t#p~Trdtn8&Gpgj@Y6IZiIq36h+E%b^ri-=x!JT*G>nGO=WEg$RBz4G@5<MFyN#<S|jiz!GrfMg%D=#mU6)pavmAI*zAkUZD^5Ux+cxH*T5EkRT%!<#DKKG8s$K1D%{r=;h2ATi#4r}r?D{(X8K(tJqfl;#1oIME`n=(y~92BX;rDA9ATlO3G<!ZjR99GE_+=tf}@jmQh|DY)>U@ad<3M-HzDdw=Y23;zHMy0?q@lD`<^oEAZUbL^qgv%UWp$_+~Yl#Nh2XicEGL==st_{j%y*Mg2H;?};-n_UWkJjY-Lixe77jt)id$s<<>h|_8kH7t+iSbxIWL!4IpqY7HY#l}7j#erRWY|!;*75~?vMh;U@myv@E{R>0as}}Dycwa#DHQ;7;OV~ofrlP^dZWK)Aji2Gdhz!rTP$rd3ed0iWUkaAawFM#qf{Y;r$AZI)H(vYO^Jo$NIAMlMk$si5hw{VCN-^Y(r5uyEn8V7l7IH(TpUz$%CF{UAe^UQ-hy4#P}a!0MZ(M1fLe0qE3kS44LGI9Ks)Ts{9)2OSH)6S)R-oB7Z`7s@@Gm;(G^r%PgjV5V{Pm=?XT$24-~0Ms|n6^$JWaS<UsY$u+>AJjx4l+>B1UH(Q*yIl6ZedU+a=hDdka@>_AW$?C325zMS+)fX8y4C>PceXO|B=LVMSjTV%_W?c+=q)yeXzY`wC)prt`Wn&<3_y0@)<?G+J62!epmzltX^O*PLgYo&}nVNVI=koGY^FATMoHZPD}?k60d^)O%<sR)o-oL{RmU9siTa@D4K!JB!6emHBxD91ViO>!$&PARYwdcyN})R?cfha=_y;a)n&ggZe}d<Zq;K~NO*aOVJ`OMT&15EiXjt{j^dd<yeFt>zjOq-3rNS__*33$ijHEx#MV87+P=a7LGt_ka3${pS~opO6_Ci<d9_$h65^5wrYAt|QxK6*r{3v81u68>}^^8+0O2=b9}@F(M2jvZUo&kA-b56XVKdV3OVOVAtF=^9uVy$eStzvGWlFT5gyf1L?|4GuZ(4%uG<4%&Sh$3{@@y#Hyr(QMb=6+4;2Hoz;ty4Y(P%;$>*$NxY9G$Gv?PzxbvM$zg)@FjYXr4-%;D2xDI2#&uUNXW*mKZJ@VA;4uqllBe0`VPDa`r&Z+C=I0D;mCscunR?b%+N+ZQfDBuffHJ(bTnmr}pOm-M_x2#<5}XN;&)cfu&w2n$NQk-QSV2Q{m2*$vyiRXQl5ED^0%lZ+YR;gWkdOiuvypCs4RIL}k7i9kDvDfB3Zp4f3kxF^qYXZmJ~_HH3<oOp&1BUp6%GZ`I+bMIn4B$fBSIvsnR#9}x&^e4v;wY5itto%*p&UT##^F&a{$bjYU5(P3hTd1{47^cDwtSPl*0*b-(jx#6+l^W8#<4`LaJ!&2W?7`U#|%_Uurr=3G)(C-`?NeeC9yOs(d?^Q(k5}*`)Xtiq8>}xm7-y!xv(1rg-y0C<vO{<@u<&HPn~!MYbb&8dRThEF%bwi2F3xB)3F>n_tCIpHOW?1l*_xkgsP-ovNKK_p~sp(r0GUdsP7!`BD^mwVu*!mva4<ks2G;_3j8g6grWx;4vdZH?0#|o;4uI)b1OT?W)Bh{2G{32PJDncnNFdA_G@L172#MObpXPi~@{E0rx8|*=?v(8;TA3b)y|JuK+M9Ir!ZU5!1{%M}-A=2uSb9A?yw3r!^CpO$38cWPtFRDIQrzgf6uG6p(<RSJ4A!vzYDPD3Cp7nYUxn=diGVg5}YgYwt=grxGi-3FxKygoA8N=15|i*)R$kRBRp+EaM<x(-Maf4r`%UEQKEEg5cQ454#iT>s`qy?{il|_%4bHH0z`ie%<@tg=MEfO+4l35|eOBWFu>}E})>$Q&jERpFJxkJ4h{TR8YxA%i*o|rHPqQvH|~OO1?qM3Q<r5RbXDwr-@R1iyZ12+m?D^<>DjCKFbus6(JEsKs7WNCsWWNGB^Q3qI&vdDsHzz6<;(TZ3hC{q>D1^P@VmQZ>HfB2a~VHnbHNBXAc2jAC7g|N&g;NH(*wSlw}3dvIv;Uz%OvJ_8G~}nygpe(r?D=16n&*6gAo3!mntnu<y6#T73eIQla`341-vZ^CksiP1b;Zl_+ypcSK=KTQI;&<%-$y0VqA?iT1Gs7}9Gsm(EnchO(tjZc03ik0$n%nJQi`6;}*IyKQtm42mTf|F!wl&ZJ~zFe*^>7LekoDp90(9=AFZbJw=tMlMtY=bqT?qJ7JV{%Jw);*5bB{LlveKPJ4vVLYE$As6bsskukz4*`ZQGb?^h7g-YYXEnx8IbC*gA9gXy6vq)PE0j-%?p-I>lBRW~*;&GlAeli3v@^?q`WhWXObOS_F-Yiq91y{x9_$mQwhL@y5Ao%&W%m4R?{ODEzDJPiFJ%14Rv=a3*=5ON<k6+nt^Bd2$Z-yZw4Oa<^3!YfG(A=8kHfrE`jG;is!BD2vZ(ycq*vTTSv@k&JxX7LCT}kNdsbbw#k1pwkUC*Spg96Qtewk~VR5;gJr8)@+u}_o?{KZ4TVPO?haJA!_RjaH`#trQPdl)GXIrVk2oyN%FPyRW0D)3Xba|M9|GnfK+uUa+yV&X=hjNPR#-dhWkPXc#b{hKus@XBwM9+{nvWd0_zF*(ePdD08gC^HgrX0CO-fbD{sCET>vvj-9ilX6A3CMbmD>a4r$u8!ANOsb+j`#2U$m71F?;OHC$WjhAjp>`d%DQ-uQT(h)+3_=_R?6p>Oj#hQxpffg&7h&N7pEjV7WCh7N$~wa{}1w<=X#!V2!GiaSSgq0eC<iiHgu<M8BpYz9SO`xq7c~1L`iNjqe;T|a9*h?iFqU-Kd7>``De^2%Ih4GJ}VXWW*tN9X0+!nrI}1Qj{TF}rR+otk?|?a2ud&5StG9SO}xAj)m6@dmK-qSBYJ)j)bH@CeBJKaZTub9U;q<}W+)@DPanaWsbj3MODF@^a(_rGTM~{`no&(bDXBe4=^ohS3gxcM_ORC$VyOl>uHK!FvQ;uKsT80BlCy%90304oP%mK_%c7Rjlu72bK|b<vNz=pcws*IFm+G#EseF&Yu-B72RlXtGgQ|bI#DD3l1C0Wml|iavo*C{4UzpSbd`1;TNW7N3Te6rH33%uvZ~`=`);m3aYgcR91~?Q7JyAAu6b%0RP{?S#)Rv^-_gAhdRXvrGNhvCO1<2Y$>6YI{_P)YcMA+IpQYyS;D7jfz+0Cg@OTz3X@EN|s827GCMu#A6+xAsfC5enYLQ$i#<QOAgHXNYKVqe!&$9R;=WQupC-_7)IY)}fS!7#!$>$!_kLq)~S@9$Jy&Pyor4p$u1Y7E2QwU};b0D;t;ypI(j$q*G8$_wN*DZd*~TiIm;6L?5X4+=vFvb$-}7Duje0>%b`F73n7PmKz_m=PAOzrf|U6m>b4@C)<83h{d(mF38g3aW-8Zscg2cVPZa4|Yr?-6Nmv*6QRW(1ujqC6`1$CNSa2LKzi*kD@YqO|c-j4vJP;JW59!2ZA-9Ft=KW0O741uMCD~ji!HrWol?fL6r@21l(rbW;1JG#L=P(VC4wZHOLff<olKvHwwqI#k-Twjh;x_IHsm|MNqrA4g2O6V4w<}UWfu>C5~qBt_x+7=sjQ`l=@C_X5UqH9$G_2_t+bOiRCDU<-9?h1LZ*pB`B3wx#TD{M2=B$1!cN%T->%%lRem(%pD3fNjQmqfhITsG=NT=jflgIw9o<&;L8|tNWPFMt%2y080aHV&qdB*TZAURy6Snb(^>8ua^_8u0zZmKiNdaTcCfI>D`n2pyhMgdG#m8D@`;xP9!oXOi8qEbpn-jkl=_%C%30uh3%sI@!JI@>M1aj>7|szUy9pK*uAWki0Fq$(xND}+T&tiQ#!rxLO|)7{_h#+3dzsv>OU7(Pm4H8<BOM3xWe1%oK2^MyuBDGA4G?(H0>J2F1R}GpR#IuDA*r>5Vj?qw?%@{Mi4c^dtd|z$psDx*4HXb9C&M8UYunism=P8k>ak_M74p8+LA%Kg$Kwa#i=1nyJbBjj-f?W5!c5AEI}=Xa`9rCU0(CL;JCk)G3X;_(U$;-IKfP1Lu~Xf#5RUel;Xcon=e0T1M~5>Aw51P)*z?{s!f^&O;Defat%<Dt+U*0C6`Ax+R6hkac0F1@n?Rn^L{ZRsf=J&Y!dCHPXqfy!a6z5;f$)V`P7w$<U>1U5f#6^SxEHdEBPcYz9=1m~(hK4ih$QP{l<;&_#)`3)om_W*jS{r>HGY10ZsT>ybV_3|2FlE%<2IBpM2G^W;WoQ_!;@Jk>DNY(P;(Rz(6ivf+Y7`g`eDRm<M%m7zv^O~hp0AvqI>-<O5-zL9KIBBND-?#+m$mVVu}=)3DFnJ08~;{amOHf4@FvUua+tpV`=?0kxi#KL7L$PW<PQ^6tX!3_?^FaQ;XHea8t5ZyAmIuVoh%!%JG%AR($16KPl!>7Hu3|c*SPSsIh7QGhO}C1rL;1oCWB+$?6d0gtx`?FM;;<+KA^%FW#_1VjOW~Om6Ab>M})m><HSB!T`F+2Ve>Zg;vn;BD@`ZPwqlBM^irm#n7gPO2)tN&z0OIdt+vr80edWD&@o}Rizl0NoD52Q(jO3R%c0RA<+Y~wmu1ipD6XVyz1mIu0F-jp^L8&_=Cx-)Ka5v2dR=9j@s4n2y1ACjpbY^uPGL>Ghat`1@<!x16|>roLNB&g33f!$q2_vg`1<{+@d<G1dl2QT&C_B;+V>mQwV8oeb+)TA<g6$3ip=8-Ndn0E7f$e|BI4P4CycqR>iKT3^>ONS{i@fmMo!YeQ3!YZhd?C6r6;PS&^exqG4uEe!;TE1(jb3_}U7fPr&N>=95;t1qU1`^NyXQiqZlMB{i2Zl@?10+&|RQlo=z#OH({|c@AgEh#a;6DMeMLFO+)&F)}#>ugHvwteUuIBM?jDG0{*Q!9z81TC7^eZqad(qQ7}MS<a_qH`74tC9Dg}ReKE$tiDnboEV>gmFV0JZ=OF4={y9J_CV-C5VcIrOq0C%+L^v7Jn|A62v1P8DgqG9wjS~jThL@36#wh%J{0yb^)TWdIuTK%BDtAAs#ZiKi_%;HlTEy-o<2-_Gso1=HcJZdEK_K`GBS}t?s;KKspmY~=E`(6syH{7p2jj^-8hSf$4MaH0&S+;KrarVC1(@Tv5@q9_SGMntBsb~Av&~~P$UXR9BTm@X3_KDYm>x-;h9Y~)J6^o<A_Qy4iysHMFP6>4l6H#zp8kksK$!#7NXMPDL+jTsc`jjC0t$6t2h1pV(nWa)6A19`q-=GLu+}QJUm{)ofgRJT!tXNh5EQ-iA6wkOsIQMuvgN>VflPHR1k)Bod?mT&0Uj%LogkaJ@!!|x>bioK0KK&S$qdU_#yPg0V#I*2n(Kq!R?)s9hWd65C~r>u0bZGl5Dv|mjgLekCDXPAsaEF21^;*WPW%ZTP#6m-O$0vOLaFD4A#3f;iclJX3M>WP<d4boEeV~m7*(7(mvF)4Kf0CX<Uvxh~Nff55x{7svyg>iY&T^n^Q|iHTlj5P!af(CU4f~Uo(dZM8hDhM7`@_0sw&As9N2TkTF<bPK6Z>XfxXZDR$N&LaJSkAABxQaj=MOlv63sI+B41-h4oTJv8c)f>pa};aHd3u8QW)Y7v`^$5Euz3FWC(Qa**^el!|iRS2n$67%y4dSW3iL{OL)Y?HOP7!X%OsWHf<7#hyl&RI}kt^@etn`t42p$b*@_#RtcX7~NaKM}F09DwA&owszwM8#U3=eggAMyB8V%W~>Qt_AbZzE#3#b+_zdEAccncp2Qwzw%oze@U3hnKoXq&8@XWOw}QpnbLB~R#O<I=|z#`CH=Alv7WlHQt6bYQISO~{x<cLc>_v-F>k!WN{omH<-~C$$WT&EG5wH4(W1x!RJipgo8QFtkPPwCF5%CURGlb5gsRn6rN-v^g;zam3fH7(A;{%$hpkkM`QHJ@5yiBvI*M-tdyq(3E60O|=CPw>uyv<<8LD@@ef=p!cIsiKHH~-AkAD2B^s2p$Rw-x)#8UI)MqHVs@;x=<&JJFQm^q>6%}A7>n2hc)CysqQsYM;i9Gvw|fys?V6TJK67*r8QNLa8lHA?@Lzj`M5zPlio5A6{{W#W}#DQ`(V<<Wd;wenSV@tvma$QsQt{9?$27GO8OIBgbdTnuba7aASrky~Kc$o_iT#TE)yXLRtGHTJ!u1_X)OY%=+yY>o$eQE*hYTz{y2H_*dm_i<J&kAiMLz4l<M0><idvJ0`Ax^%TMUL218%`4yK`4kRah|H2PN9p1M%nYCk3YIN<2vrX-0}0WHDl||U7i<&gpf&MMib17&)+N*k2XV)MJ%#{4v7>@&eE{=qq|&IJf(TelpdFsQCN8d2dht#wbe+a)!X9jq)zJuTG<zRnwDA7HogL{2HZt3}ME@Ee4Jg@(anOnVp-hF61yQ+qsEv%FaTJT4ER@^zSKNG`7IW32@{BJ+)(y+a#7>A3M7S^pyd*%UsG|k#l)#WPI^x$EUPd?y*fR^B<7&w|W@6!w0*H-gNF*gGm{c4USx22EZi|9tsU4=oVY0?*sF{VjMj%WztjB`J0QTma1PC5WtS%DX@#1e65B>csV-h#z$y04BmCpovFAVBciR*|Q(jY!xeefog(7a}@w*JPH_!SAvdj;JnG3i#e8)&f!r9;=_&3>U5=ssIdA`8)phB9ja%6I7cQrMC`4pRt7m@EiI#850OEjPK!3;_)fwgxOtYpfp9!#SdA&+6RKnn@MRAxZt40~VHgn#wVhRi_eGhazeWe5vW_i2&q3NS3C0a9n;b(<YCAvAd``JAVXg1I@U1#h{^KObR{()1(2sl6wq=95ki%piPoyGI%+`BiwvYc2AU6Ovo>13l(9)wlb-R{EWhV#pQ7~-*Rb%DHjZ*_!BDWd-Na?Jy5|cOHAEGG;#ELEd~HU{Y@8RfEYa5%dveGDN#+b)xES%%!)XW5h&Ol5n4i2)_7FeTvr1`WNqU5$sycYndXH!tC4EAbOgN!Ir_F3odoU?)U(5a%?Ke6Q?R33K_iveHF;EcmNU)H<kFj@aCy?P3LhN|6CL06)ImIC;fDOdLCQ%D0i#>em8K9@kU31C;!$)up(E2>Ek%(CUY+<>s;C%8(?&-`A#osyqw8odNefKTEivH6{V`^_n*=uQaf0c#ArbPwJxfv;)f8wH1T`66qY|O{R0#rM>tH9jPBJ4M`=?}FWCV$!Wa^nrZ+{++3#v{?6$+J9Lr4xW)z@I&@{JNZ`p!(%A5}tJM;t#W0jW?K-v@QE%MOSLh3vn>9YNeQVl?^wcPNPp(`Gn)z}sF&(jQOtx~ruhu@rZ<haN{orM=SlQq1>yHd7kU;Z)^OwNuPH1|Lg%^F5cLf5kd&KE9>D2rS=>k7AedhJ}&~fjTNgj!ZHARLUiY%CS`qnIMmkrk0f~rZjVw$lau2K)^+&VUwKdk1^+h&R!?))Y$%kgHj_s(NmJe>JxP?I}0yrz`Xhgc6T9M2iwL?5)K3#>LH$1MJNM{LnvYxA{etmBuO7pdbvfDpduWAyaN{h4s(&ab{CnoOTdvZn;O@@6&Hbn+Es7{r3<ta5Q`TBbcl1n0AMSuK#3O3&`!2bBrOtbf!glFFzzL7oB(j^Q!YuMRh*WNQ?eKXJx9x=)QhIM^<<E|Ia23h0z+8jS_jDKq48EJE_+SXP}b#e>_qdG+NaJYj5&eSdH?ZYY_r7(YtbGXD#8*scsU$r+eE^lI66*qd{yU)n1;7HjJzA5Lu+ekXv4rEq@xmsN;D#LirSLJJ|lYyI!xX3KPO|!$x1JWIK#GtvlTyUtoTk22?pA7HF9L<4~5`DOUAU-7P9#e6e{zAO@UjK>Nv-ri>S;eKs3Vy=^>`YDJ}`X!^2(07^bU0Rmw0gl=6p0NwX)g#CI8vM+QHTd(N~}yZ9C;Q~Z)&d~X^FgH^r(7-GG`1v%rNkNcmriJ)eH;<G?dw^i4HNu;(tpKtNY_kZ_Y3?-81o0Co+B`plA84lJV=#l4I9TPsN^Q|OProTK+=2P8QxsD|3kpJkgOC;PkueKfb4s3IEz5R$A-SqmgAY};NDb@YMPL3(EuvjdYdp-meu6NV%dP^w-nI}`jY&GHb)h0D#w+lfsz0L3gDovcQkcy_xGG$)NxVhA>jFOd;l+|qC1Vr2^{eKB+z6n^bYnxRRip_|Ks0b1ga`0QL%@ESX-^F?OKiZ|Y0s'
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
