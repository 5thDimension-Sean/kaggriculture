"""Kaggriculture agent — Route candidate ep=90747835 P1 score=140,789
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
    'c-rk<U2hxNk^L`v=7UMelD%(=&BR7DmLbU@vIAi-z$OR~BoC9kE%v{!Mxw}8SJkOgAKj#!c`{8>?A!O&y<H#Yoci&9PyYJzFaP+<FDL)?<H^^{+uM`-#mV1({^$Sv>*0-um;d<rm%snz-w&^UJo)tbX8rIf_u_Zo{`}MBm(M?3UY#sXK3s237Ax`g?Wgtn>)?ai_4?z(+nZ18%e#}s#pvxH)>qeGP8Q4E*T3FefBg30ZvPi=@9+O_@#20yfB56Kulp-42lw{l$!2|f_c+!s*Ee^c9$)R=8ohWq5x48BtNm4%=2drJ7+!Vv>2Oj$Uw!=PVe;?3ZD)@ghdK#jINP7lhOnO&`;zLl`Acj^bvpfhj(>eHn*9PROFe!ow$@jdAJ)5>d~s2Ex7skoD=^K!AMTHr)4d(WuQv7TZ$13~%iV6z=<h_X{NZvurK7PtOy1?)`eyX%`J(%8jfMd(IX;VagBXr{eR*qKJ@m`_AC%LyyTtCr?e#Zjy5toU)8CDF_rtx@HMWWNSraB8$FE%T=|yhg_v1w?R+%(;APtU((rj(5hFRvt@Y{*`LdGUHXV1iq55fs%kgzxT4*w9N><&#|=3LmmGZ^Ro9qUrL3n-Jd`)G8@<Q?qCD}MOtMc{YQSAly4{_NQbneSQ;+Q1VMef9e4YW?Bvr{Aw{?ml0A{_n?G>%N6K#xr*Nz*nEov)_hZ9(rV}{PtBC(Qcjl!4fRa>~J;^Z*ISE2II}hP7nRH9VgU$e)!jHn1<~><|9lsO_4FkX=;dNJ10p7=e$oO&c4{C?HS(tx9%8}2}VQcn&N$s6wiJ{=17_1K%_aj4a@MOYk~(RkZ?Q4;d3&|oBPTIS3C0PN<5ch$85txDD&u<!VYs!<HFgOKk+7cl%$Wh;B&*fj(e0P4zLNIy`dTN4|4lSo0>BBXqwf=!r}k-^e5SnWAvgFYA_X+arG_kYcHmXQer<$1TM}GPUfaB+M+-^yIOcA87cNpmp6ZkKeNUzzM8e)4keu@QQXMjoFMOg|J&n2M&{XPB$7+ZCe3QMSm}k+^7U@2y|9AX8C8mJwHx5WIT-V5)>iOrhKsfT!58nw*H5k$s4)7TN$QX*6?%3-lB~Tl7ERSCOw&$QSDs%eD_Z<Tt8i0wLADRI)!Roi@Z1vVAuOklGAl7d`rJF37<29z`{U<7OyvI4JFF?ztmMsz1JQDICd`tB=Im*Ju_@EWk%J<2gjDS8ea~^@T%qP`t6`NQ!8xM7Nc3SJ`v)yy0dM&@N?3ssNwJ2tcj!_TG^zxa$!~)2qc=5Nj-q`tCPL=$3U!2MT}w2fe=x>!CQDg0>{?GPYjb`5@XzwibGY%~HGVA647SnA?cL4g=6CCxn?FDN_Ine{vAWNMW{Tr7imq6`MB-VjFbQOOP=?U*1$~07%uvyPtc~x*7_Y>x%JCw^e%g)D^OOpJIdFB~|G>8%yn182W+2D88G4TQ23s%fG78YIc4dxg5qToncB8Nm!c(9uXlfmS-=^fkai$zSNTxC@ZA5@1WK3$>+@#Y2SS|apN+kd2%DFtK7L;F(&p<d&!MX*zs-dcp^>hg@Uju5%nXka=P3XWWBm?cRH|vK<_go#8x}wH3xx2u4yHr0@YKrbawe@rd5eTe}{ic124*dX0O?pjmt~<6~J|PF#Ka;H<igYB=29^tJC`Bt|088S1j{dA`Yzmb}U9tl~VQ>Jr48(XcCIJ!4S&Bd`3uou|JVN_rjJKq(OCM*FR43_GS-!G-Kud>)bkErpb)UBSW3PxfLJ$Oe{#7E8VX1lSSu4c)gg+&WL;A-6y)db_w0nX4a=+lXwZnj8q#{6Sd47#&x@PIpa@B@*!Mk~ceK>2w7{?|8O>&tl3ks}+uCV<ZHRr4C;fOmxgqO}S;ZBeoK7^X_ASeoY_~HPfslIS42#?mJE61h<pThi4tF;CNDVbwIYiU#9K~^TD<##Fn?uXA;e|(nh8L6pU82RM$up1c5qc8o;w5ePX^ZX3gbd020u+K;Nyppb>?yd$M*T8u|ooe<#iuquek0t%qdM0e|mlzLR1|->?4R)Pfv#Kx`KHfATh@6kO&vL`OaE~s{B9jeY&&&j6$-L?0oKWR4fHakqB<lXUB`=@$y0dms@&I@Dt;86bbP^w7$@|`4i(h<m49VLBMPrIS#NQ+^+bLXmi5k}fxtx2Ch}*z!iL_%D%p^~<-NhcUy^AVtYWH)7waV)%f=oSYE4|f0_%D-|C72BFE7#Ja!7Jtc^u7y?UHa4eJo4wF>h-hk{|dlpmYg7HNV_trgPIUL^@TWBxlkb?3d-<1gP}uW6o}qNh7LC9Wr_?n>lRXZ<$9SIO_549jBrRB;x2u1^wBV?sMKF3d9YN16pYs4mQ97yK?sEnGs}#wZXp9g2U2Sg&v2Tkg>X;VNgKR*0^2A(n*c+jI?dQ9!<(no4!~mt6^VkULDTRx3(?J1*?u^VvNVjb-$obBsnUQp;V7}-k8s7$Ev)KjbNBJ)`YVT))-&8gM~$_J)qNJDC9GS9U1-vKry4*P>^NdK-@6xLeb7X&&LR_i+B0Spa6a8e)HY5l(>##U$c@>L<pNU*(-NTp?koa~uV+rxQXW&ltH#KIdF>6{$q0Ut1^dy9^;8l(2fLWz{;<)1#~c<qp|IdJBMUI(FRe}+5Nt5tp?v7`Zx#+h*T^puj&%wuH|%OMesg7hGj^L6S{2|^3YcRTq<5yhxia5WZV{(jWU&LlWQvGD*+~EsR~(oQmG?g+;!rFupuhpNBm>FUyx_?4aX81_k}5qR;_K%D#97>UZ{EpAM%uL?77-804n0so38$3BPm0?UFg-JOM6A$R)9y3grka@8nIgs-gI3IAkWoG)blBkR7|QWdNQENY$HxBv)+z?yu+Ma*j9pO2CiWs&Hn>P0?I&xEN@kbdxvOb+u2KXK+U0_iX)F=1QR+;oodY@!!l48n{-eZ4Y;USb)ljK?J(rzkZcl4BHF`QEfdOHQD*=4veMCl0A1Vsp7lqI@eXkeieku{7Y@iI|ZmPRW?kIVCPN|>;LNabXSsSruU*^>0Mqk?=9$j++>zZwggjk@h8=)`TR!W!I2^1w^Hq6ANsi90_T{&pAG1y>(9)UR!*4jRL2}%?3q3t1f;DF4?PP?32XOLkoX}-SX0h4tU5XBzIo0!cPh$LBZ84{H?K!G}D%xkbvn1Fqi#CyerVZviES+H?fuVQw5>`D(&(ms}eR(p;8=}ZM|ZCmOorzFZew0NM=JVkg_;#(@|7|3?p*<F}4OY|Pl=2JV9k{o43mGu@dkd;b`wODyt;o+)v`;w?7;p=C($+;_bM{KWzT~L*i;Xnr$-v`cM#HBb)<P#&6p)R0Wcyx9j&<fip6yQJ+;gb+zt7(tQ>9XsHu%A+fs7L6%P%#~P?m9&nUU)XE6B7;up@e2|!rP&rnE(-s(>1Fd5;h+PM6jp_`-G|O0^8X`$~`RQpP%g+cL7wM1UP^~L6B@pQXM?IEcwzddMI@pe{3mo>PI1~XU~}Y^qSpO^)hf+0ZTtpU{F;cCTNSwKbdrfdsJa06Wk-fCule43e;!KRa-nee+Xq9)&$HW5X0J)CYctO+u4hNH@(f~WXT9~6kVo4bv*3ts}1=4h`K*gU;7dW^9S1sTO`2Gm@l1?CNI2*`p@nQ{SeO&BR()o$+0bZW{Qig@o}i6Sm=xq35h2yDR%n$0nOWKiiw^dZxj>l0DRuiGywLF_*s$2Q&t?gj^b?v>!@`FLbG(=(TbtrObIA@HZWr|<w;JTptm?_I>+<JKJvKlz~ds=gCs<-RZQRWRo2D3j1p!I_{UpyuT;n{fybbxIYir6yHZ16FRqR_2@bRDpB{Pyzg_4*pv-yJz(t;}rdg<Rj!L($y{6d)?$kX4O2@OKei^9~0$-V6<Q5B>Bzg~*m6~dpM}qN#CR>|-#+{;~&Pl3g6?ShrFvMX-d+AcT$yDIjKiOTzPV_RFzJeJ6=>=PS#0|blA~<5Y%307-0%l@FFD`=i9ezbuB?$<JVs=4J>zbh3ryA8k)Ta+%&5#*u;u26-juI&7sW(zpMzsQ^RQ9C0d|;O=O24w$!#=i<U^Xam_3m_3tdeC(g_jD%&I(=v2!XVLdiBa!5w%pMOiIK}6eAzkXi62x0~9B<CQ6S$-*-nH@dx3|M^idg{z9}VRX;h$pY*Xn8w<7Sa8He>gr_G>R^CNQZK%WYu@r&P_+N3U_~m+T|Nf;_wbgR_OUwfRzBzOT8h&h*=?$kVJ`7;JrJJ*)t!xo6z>MhI!Ajv6y9k?-mzpUgl*ifq50-}6R^U543mJFX^|MS|(f!4%tVI&ldhL92w>;QJ%5hK%h@t+Ye25RD=BZ32L+n)!rFyb4YbjJ~WQ2vLkqTrdNF^yyX|OF%6|76D3}kW>kzr7rxdAq2_T~cBJ1Y2<$rGc62S9@d3Z6`GN%fFhOUO#iAUZ~#(@SCo)-}Sa4itJo&kLV8Y~$*S?-g%x6loadg_Y^|QY)(o803@)KJloHww(vw-S8C0GSWTcvm;ntqGb3kKpPTmsgnaH0@Z-@Fb>;-^7WHue3Tbnbjor5tPrYzN#~P1llbZorXi-MDG^HbFxwECKd~i=?+&<w<F$DEfS*!gx~>+;Nln2`a)ey@Xj_6rT-ZyJ2a}KVQ=ImGA^vgWW^nOJp?F(6$!Ytx4?KMrlxLJ@@RP|o?UmAY4mZ{uHeouuk4U3Ct>;k*i?!TRZWOlmVR&xL!!d@h+pZ3l#b%T5D6yp|N$V~uYMJ<0g+C7jay#Qw5@DoGdvKEt)wA?*<jYkl28Cq`CP0<@qbr9{<GfF(BiPkrFqO!3kGJK!LB3;%2zXC7@H<HQqf0sO^g!tk6JkLsiDt7MSvheSe<!3*o0Z17;Z36%P>3t!Aqq!*%o62#=BMd)CQ~rST7RTcLW9CNjIS|&fI~y&xKp-8JFps3k9}h6&8tCT&urZR%s?I7ieWs?3s<VSu2wVhsJ(u%0q_KxJXIwP!6qQ3fo``5qb=qc=ERQrV)|PhD(AELVQxPZ;V-)F@QQwzErNG#BvpYzc2AklD7aS=Y1(ZwK|MpC$@I_|2vt1CzHxa6(#}+-heXUP@l7fa_V^x{3k2+QhDtiFP|aV^S29WS4`OGbSXe{}oX_veq4ygRVlUsy82j}5(5pWRtU;h%Jx;@0{Ri6M26~$%P(h1ETAlO_rg+&tV)@|F13T&CK<}VEb`1wJu=tt=orCGeI0edGTAQ#>ifB%Q<NNRjA|6vgH(pvKhXU1Z4Hi~Pfo7g>!fhSga}<N^Q+56b>m=D$nmTgj$yi#aJbnS|xX8E#R`*kjv}}MZq^J&Li|?KlN}w13J3?6)bYAyt9uC!z-8T3rP%83XDvc?~a~KFp-Gcl2x<yh#Ia8s?MHr^TJh&4U9gzG|o@o#@02Le}h79C4P+J8|n#?_pshB{0TE?YFm14N!x{fxVyW!qN)I2D*HcCzqn=zLla9l>VT{)QI7C?ilN|5Z@-8(XeD^zM&->;APGOzMo>1G^Ve#MrQVD%@?7$FV(LjCKvE@<Kf;b(a4tyWXEAH>5xr}OjcdD$gU!veBOD<hsrniQA(8M%(2s6wtF531PvukZpKG14rH8J|%kGD+GFDi|nEp-*nY@W$zS39!2n`Bn<=)~Zjc?<9;qu&>pkzQKFT3Z8gX+DLgj3$Rh%@Y%xD_V;=H;JluMj}r#%z#g<AwE!6M`LY$6>5yrPstg4e$_Aee(DXB>nZ)<=P(5zju5bCRf*)&gLnucK1RL;+PCP-f;v&v96mv-&-qfu{oG?d<hqB`$)&g~Efr>Z4g21@F#U}VS$(wO;d^O;qhguuHI{*nWhwXD*zrMQuqLthsu8hIjD_O*xdXY2*sI^=ZjKYQ=Qk`+22Lzifm=a(6#|8#gC3XFFmS?-lG22u6!pixx<2sbVbG2BUx|cM@M3-9+{^kX2AuSw+Jf<VKn6-O%e?Y++lppC4v)Qrz7XA7*$HC%y&A_saSH~Umx)x*mJvWk;XZMpd9U^qVqBmNUlnF?ol5%sVUS6Ma1_cJ-a15`h3n;3%dt|I8a92<7&`=jqKej1hQPeEH7g>io7;#~!nwayedKr?O+&)~_ADp4B*7MmmWZ5_iWiCJh4+V;IXYlY2V(EjltWE^u!h_E|L^e|UOe_WiKI8l7f<~^+40F+aZ2A@GQzzogigk==AqhJ}kt~&7fM`Y}5R>T4heQjZ@)<eEkz#Bz0RSr_P6iXjR9@VgQT$MBSgw?sws1~E@%_~30z@_B!8l4e0NC@i)8gPV5Kc-EmPy~jnn`%%fbH`XL!V~G4A6QMs>?3%f&@Tnq+xIz2VzU)n~+L$>V<x5?lhj&xqjy|hF_f-)KrOId!Lowspo3?QZz@Gv?0M*ryi~~*c$5XVP%VhjXrI-UO)*x!Y;I>6|=WsX6b5~9Y)gu4jFk4)R>Pz85Lq}@TXLFko--@Q$DG7SR{oM5a;IQ^zk}K(BW6_j8FeWID9ZFaJnq7OE90>8s&E#BPtsa8nL?uhwiXNm)O~C&aksJZMQDm#HI5yGTyF42^yYh8)+|-Y|_kw$DGKW?p{#i+v(#W<Z&PuxZU`C2`-`-7EF*&YC}kWikE-Zhe#dadg3-=UJzR3J$F@ehX~HuYz*r}qx>(GO{NgnK_G7ifNeJl$6Ryg_(JfTfN^==f(Np(&j64`Vc<6m1Sy7??nT}}1|%eyHn)sRXQFB{UPsl0i!rY08g(uILs*^$Ve!rJprEMcldck>%iTPmGEqjhI>_BlBPTODV6HX!yiLHOI!I9l>Y=(H>9_y!^B+Qd(i%Qx`nE_uCl6txyo^*KK{06#aG<EMT~9y!)vO@fCW?cERoX16w}5C3a!Q{6m4Eg8NutM*9khos@%|DqyjO}n)<c}rfn`XW4adIEOHdKpH8x_n&&D#x4b{K5!v(;+Hfz;5bkFG{O75raWUcs`SMJmaP}LWrG`{fA5w@eC+zFN7SC&`0GW-d|YmdG2!Jk@2h!s~Kz~Q7-be>C<og9{NP?V<v>_T6*37ukQf-M5?;fQw|Kc&n+ivffY!u3j|P-KTJq|INrvLGnYlE<aD#s%r+BJQkt4@VmvIpcqU>Ae685u2`{R*$sIl={p5cbP-SKA{TijZhv&Y4f*RDXBXN6NGjJJpQCmHXh8KncPr0a<Co!FU87fu~el6Wpxvw%GToGq)$R`IjeGie08q(#QW|tj)zGjGBRg`(j5No%1tU>7^uwUn?7zObF2J|ZsjxrfyeO)OiX^05E>EfM+cgK+x7R_WAkn-(5!TOt9tJ}*WFc322zdfrcceJLl4}df9~dD0#!VcV2Hb&DS&>ac8>*-GCGG%l)`l1b&|Q~)_*Bhp|_L0%7z2y3&0C9()E0hj%+D%X9<Ji1Z9j}>|oUh1Pj6|CYOUOnQ8sA$YlW81p*V8Q}7}8r?WhPx*mm`OEd&k+98Dm_EOUJ8e)!4CPEEJBd0bZ*2UYQDe*3n4B<L9IuedCVls&qWm+k2h@Iu&T{9;*<Fd;Po-%Qq9Bh$vubCnLfP}JR3J(-h?iCBZ2*JDQmXM@y8Vpa^{&Q~$L9&o=KPhjZ{3zm7Zu2p9R^?kq-fCZ=dY$T42hPJ_QV^{a{4%|AK248AN3O?B2h7$Q5f7AV05wTd#4yPVxnf7y3K7){;oZ&A{}4q|I7^aPg}FK(k{a7ECOo2khfr3kDp)pSlS51*)9CFStZCYAhBy)8s%FQ7#YX!_VR;=}gmmTUo`kHh8-hvsPf|HlCGf~<;ByM^&KcvI1qi1APtXbeFb=|xtOGJxPMrqU3=$&3kp0JZ!GPfuC!?Mmq~bF<RcxoHYNW??0p+0tCCo8|{137QpA4iCNPv_G3}gr8%m#;~j7@`G@Q<Lb(!az`nD^tuDc&4XCL7~2M=k%FnPeA7gy(prc?1=IvBW42M^x$5Eq|vKmkdtblmxRBs)cE!I4RwXk~%lD1l@J|h$1+a5dlMw__(!3esG9+9K>;U<Rfo3*bb_o@G?;+KJ0vBH$2jFuCtw9uH{V#1eQ)|COhe++i9h`Zyi_1JXmOgU4;Bw?!l1pHF-DK&Dk!OL#p+{%P2;X(rixRhQYEB$OL&FlKSivH6+wbE3zwND1cNSJLpnCX41MK>#Y>hL2|FYF|-4s7rdpXb+QddVEtOzPqDHOlD7AThMjD3SH#qoQplqKb{Ce>JVdN6%G4<)G~5S1JT}}aj|SgG8+>764@ym`+!`MN5*nL+!iTa^*-XfYiBn0vbP0@uVLqWz-q%@365_HvQ!-d@zNZWp(m=A-f1WIt->3si199@XYR+mkO|!S;9TgRU`y0S<I!91EXew=Erzsr5Wx@~P$RnVNgY}A|MXAZV-@kf<{T!}$92dZ_UFS%_nrI5R-apPCVq7L`1lXFft6YfkZuCtde!}|EdR8o(Lcy;%Th4+mrtCVW)2LW_5=v!?<0X^vB7hJKYmbBTHy$SF=A_b*r)D2)JZZ^UxmDwf`#^%Ficdno3Y@Wv=~X3pMY0#Vhp&n90D<eMJeo&}JUS)+t@(b6jHG!DK2<KjBlP!WFgGLU?&7?#+oL;7B>b#1$wcHT8mcycvlrWTin<)Vk=SRM?ScBZnq|mBDP@c($P`vu#|mp9D$Yo6!!=_?&JA~h1!oE-tV0$PAq+->M5Gz-(R%)t)$ni3DuX76Qul~m*RzO@5l@dpNk~r6-A*<q6^&xdxU|^&=!xq(DLG`@3&@p%Z#z4E)!9Lg{5Z4vc}}p$6Ca!eaJF$Hn)#af^$e=1UmvT;y$MUF&Zx`H-ULLVADP5<7#np=o%Hl?hDaZ64fA52Y)9vsjD8o#t|>7*sw!Myh$#3=YO~grwJ;e7>xzU76Xn%>`V*BEPjbviWgP{L>#Gp^$?14-8$S7A$XH~)0pU@Pg7kPFP8~7vghw7bDCkrD6uXEzEIb4BgX$WJO{&Ye>W5+m{WgYIIR=)2HR5&2&~^2CHFq<yorVD*dY$JuKrXvJ)^I%oX^kOF4mkroqlos{W%WQJPSXZXgC~L7I1Wnrj+bNwB;hbSj?-}s3SMSfFb5Pcl&#}<;FB*7>?fOC8}FJf+bPGlQha2`9F*d!JGPv+p4k~P6UX-z0V*V!Okex82?49z#buW+ba6<Fvs)jsRaJx5DLovr`t2a<o~ue|l-n`Ai;QXf!wcs_2{I=}l<Tr0aT0K_T2-AH<I~!{S76<%fcvT-Ezn@)5J8RVc|1#_DEcllPQ}+%R@qeQKm*lU(g_^>uW}dn{||~iwDS'
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
