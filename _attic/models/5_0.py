"""Kaggriculture agent — MapleLeaf 5.0
Route:   ep=91128753 P0 (score=132,583 — freshest top route from 30 training-data-v3 episodes;
         #1 of 60 candidates ranked by winner score from recent top-player replays)
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + Town-Center-phase-aware terminal liquidation
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + price-gate: hold sells when price < 20% of base (floor-crash defense)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -10)
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 4.7: Kakuteki route (ep=91128753 P0) replaces stale wheat-heavy ep=90794783.
        Market: _price_gate_sells now wired in (skips extreme floor-crash sells;
        was defined but unused in 4.7; threshold 20% of base = rare-trigger only).
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rk<U2h!65&SQFz6bO8Au4aQw2lbVqCiqPI09i9h=Txu^Wfwy$bSz--reqPS65f}%u=!AH-bFw&CbrwbXQkZfBN^)Uw{1N=bwH#`opKAuRmU0zy0CE<=y?q+u`V8b@aC%|M8c9KK|wL$De=v<?lcJ>+$DLNAIql{)&G1`s4RMT)w~h?(+I*b#(V`7(N`WPR$?Q+-#0k$GczO4a3{VUw$`S-@HFsoy~r|c{g0%fByBue^%46ez<z`?Z*$}w;WG~`{`&i+}%G7=>5&@{kx~1o_}?CCzJ1ab9sAvbN~4|^Dnx-d^7C7=ipnw7$(0Q?{Yhc>37e*WH-#(Equ7WdHeCr{Wx3e`AxV_*8XYwh4H}eZa&TjK3r}GzWdwL9KOHbKVx=1{#eJ6?Vif#Nq(A|%lqM$UU@s8e1^ddt5ZzYi8~Rgsj)Y(pXu%0OY=aM!hZ6%_jnpDzjzgY^ZD)KcmDikbWzOy7d^ww6zo2W#yLK#=h-Ef*-k$i&3Kj4D>PqAXbHvB_PC`D&RuT*RC{m6f8O10I8|)z&fdb>(zTb<=LsxZxU<jKny_NGU+(T<2OoO;&E?%)dF4*tfapbi{vP;Dw|^4G!nSI*DsQf@hd1{>d^6nMUtM4Q`S5-cYv>DqN8+RI(U90&mblx*cO*V)UZ*97K3~DVfAlx<QM!5_&%xpPa|SV4FON}5?h-JZJN^nMG|xZ8yRa5Z#s|+l+FIdvBzHv2PljSFxAfTb^9zJbX5RCo16S=ex-opKP95JVr{6IDu449<38+EhfYTp2xY$NDQF5YR&_<x+I@#Z|y^6P8JcQ%j$7ST|dWy=@5;a4$V;mRbF8phW<o7>3UoG`?XaB3rmQ8OeL9B^{XaD=_x`-Z6!K2hi*}#h}Ex}a?7arn#>)EgG?r$$QUk|sp-yf|`5(_$kT95>n0U~{N33O~#MvR`j$@lvV*{1)|QKo(u+5hywg)EA36AgDLySebNLK#_fgpVg~CWvGQTLQ5Fq1g_fn7o7SfZ%wO&gFI71`HWQFX4%1H{SU_*RCSP7x5twJ%qwF!TlAkGW*}wq5R*T+4+ojoyb+S%2Gq!1H6SDaxuDdj2N#upL5#<*eRcnk8+miA5-cfNVCWBr*NEl!pKtFhEeb1gv_9AOpg!SSrAegGEZ7*aHHIc_TqI7%<xDv!GxXvQh|-Wz3(n>|Fpa4{^#7qrkAi)l<=%Z1)tq^ZGy05%(T0XezJ}?gRYY}=usij-d59P4ko_kLUT-L`OCb$z4?%TR{QgJ`x>4+eXBi^&Ffjn#CLD{x$_;T>1_Hex94fes6ytMrtPO*rk_ZT^+X)a#&k59q;r4B6eu{w+@J5^HSBP#5VuDs>@K=a7q}mg9xrl7fWXvthFXeM=~UGtI&cSJu5Q^ZDD3RRLz!H~vgJ%*+5)NAh-*GKsVRZ4tj?v0hU;&@)v!i`a2zzI0ogeu=Oth$VH@K&Rjp~xA7gRX^+-J{!u+XLOu>~)Lv}EW97j)vLZo#7f?@#{Nl<j0;~|Q%AjSeCc=wQ!o)X)7D%Z2oFF~8V*lHK2-rQV2F(%5p8%_qjGyHK4zCFSu@^vz)r}yktRzVb*3SJS3AU=HLA`d8U%mR)+VG#n1oFP^24#gPzvwG<pG7*2j8r-Dlgg-D3fqLJZ^R;@l-o|e*9ot`UyVu|s>R=B!b28n16}XZofFpfBG#BUA)7f*J&K^G`$ncP@Jcdlgn%4+p*q~ZwjhG_4J=pDSjNhD#A_)(9ddW!XAtS!#>)b7~SRFY|%pS;1`b{5=>oran3Fz$lO5ls;zcW<NFcyn~5V?3?q_j|2?huI5_7NKi!rj*|>aC*xC_n>j5syD9z>`Cje}3C*U|CoP(Lpx32s*ekG>vezNh;E5%%BKC&U*`NA+syiM#zKUdng)G!Qo)Z6a0ii_xSsG>al;!^sd0CniN`q57UTvNSwPws&J41w!lLsw^|YUZ0oJ^m4x8e7#sB8R&YZ!;#yffW2>$d;HQ&E+mJQc7}8~5<-l7If0OG4WVG3@=VPrY0m*Ras;a02qZ?6v=)*KKQ$9gTol<@)KTUgxt8Q#G8gi4xMsV0J%sTh>7T~M#1pne8i}!X6#^(@Xx^#WgDd~ui85Y3HmK^DVIO1DC?G1Me01++$nw7%?VAv*Z0&_<T)H*?NzmC7Vy8d<x13@B)3|*153eL~|?FAnj(Y)5&=Ge1q(WzoUl5X`qVC?KzWjlbnvdM&N5i>i^8bBhsicJn@zn~EmVC%UX@XW9%nixy!0D+4h#VQ!DoS=XMAO>$iBH3N+lk~j|DXQXwC*cJllzAC#3ALBZU55TJQR)Ne-#NI{jx4IE(Knxds>G3%(Od8aHJ+`k-VAVpFr*&hVKsB7(Y(iU8Ixn=Y+W!q33O^;!LU3d0c=tAd&uFydl~t3%e0V$gS}A|+H#730tm$ROi*&8dL2j^-AH-rni?u!?P;mM<aFpibY>P^<nqk+ki|xP5qY4R7^Xn%Amy_!vW9wx%tpe|#pRW-1jIPr4UxP}Q9%t11j4MImZ%FIU@xb7CdyW5Fw-C`(<ECN@l%rK#qiW@;Z0(Q1*x*+J%XmxPMIH(c6Ke<lXzg|C@LS4AdRfpixRnqzF3@v*HG~#QzwS1G$9U2S)}L(;&ri*lR?9()1>EIQbj1?%Ot}rU;^U<B`%$ppdsQz0m5Z+?p9)I%JN5-c6gL4Swg7J3zcvRNsX(owEtfek_t1g{i-Y-O_Y09RgEW66WHsB>8Ygdlq7}h`H=68^H9Y!EZ}vyNi%(Z{-9ZITd`XU)f@cF^~x=v7q_K=iTl?5tx&1wcv1t}J?4{2hA6t-EmRmhs1QDjEfQSjDjiQC+=BE>MXOQObK7Cyn8Dd+V#Qa|!7@U2isjZ6<ikUPCg#kqKB5qYsX_fl!YVtd;W;ewAmb+XPYr<zE8a1<Aj(q{o>zb&<WuBODQa90R>1{lFow1HIt7uxUricEhm~dt{uVQ~ktB5PAUfE!puy>h3L=}%3s2)r`sredvcZx%n#t27aBzi2+f9E;*LWsytW_ru5o@9|3|Ow1mC7?tVFNnDhh7hs6O~Uhc`8{<Rx~!}*hUB^c!Vbe`NSbXCg1@ZG9$eB#>{zFG|~u#!C|19K0dDf#H)s2{)?sYpi-0_X0c@RwYkA3rwvR_iAdU@43#FEHnlW^7zclFN{}0YZ%EhShLHyM2mxC`k4)6xVP<82=3AmMy@TYQ+7l~@t*Fy;UQhJ9Ws9;bES>3oWui0NUXIsIql_QB1r3(6B=st|EpS~=Xd~FrUo8l1aI~W<#zEZDQc(a&Orn~7D9CT8@D}{`c?v`6r4$pWRE;ENGzhcRluDKq)~VdAbgPln`>ls{f}_d8Tv(z`mx5C)M3LV}p);49*V_P3%wIP?T+-B^$MxR}$*P3C*wa`~COeg9t)Q}Gj7>Rz?>cb>Q@aQnjM(6|a2x1yrSnti=fFk7bgt=5^&D(=IqI8Z34gS(1H@oQXyxjU9wb2!w8S_fp@Oek9_yH)?1CE_r60Fwvo3;lzC(Mhi0-zd#lMo%Nxi$0hI@k%*er(6W(&n2nL7omvy&%v>IYl90K$Yg*F$&KJhrx!SVHdp7s=koC$_Brs)_eK!=_~`AF<CxDFaRrm%&SG%arg=!hB5rFIojCwXURg(lqVp(Tk54J6VYV)QZDtp8s<)uL#0+Fxpg|6Y-tp1no4{j|RnWQM6`Z4)-YT)TS#y4RrIS3J-t{hK?`$sw52GxhR{wBBgGobOmY3YthZBE8>*8{Z#;|W&EdPU9F=a8K2+w(_Z1rH4E#5fkjEQ<td<g>fv38AZ2QHSrW~k{orzF+)`p?C5GO!`)6xWbdCa$hL*znF?}$03P6<{fDSO#UJm!Rql*Z5G*7ij2FX&ZH4?Qt46Cy?G17BZmU5^AV3}khLFCMQ6=~>1a`r9Az~w+&$FyD5W@zKa)7+8B*>iY69}J?XvUrJ#?oL(bFm%2$oH#M_tvS@jn`C<$%c?V==?pA4>jE|2fJ&Sz0QI5Hv1rKQIomnr)GInH$OMO~QfFSGlEU=h;2t<dngxx0f&nqBp!{SUgV(1Rge+R&SPWkE(jH^l2hw0x|11@<wPtSs?_pS!2wAl2IkgV&&NRjD+hx_i<ULFZbKpamblKD>wS6e9c}1!aE3p9haCHf`R%9iv%{~h@Y$lZGKr_7%*!^{Pkv%2StM0ToOr{IkICl;5Nd`*yUIPMbOkdcrCR-qKD!qm)<>9QjS)uEC-d#~4n<l2sLTAMldOFM607J@mi)Az+DvVz+zTCz%OLFbbs#((WoP>g;RJqUmR#W!<53{+4(|XvjO;mf$<5|rcY$gJqK1!psYH2E{7^e2fqmeiSmZ}kG<&?dnVsT(Drq#f6W!53-fU`mb@MUzIEaJiXputz|vih&u2drvsMm)M*yHFAp9VdFjaUuXKZ&Hk+!s?TI_C(xIsVEDG8l?AJSemuT4qKh2q);o=cHp=3VkeWX`32u%>nu(ZPn(%l`a^TzZC1)mfg_7mw?$dR48fb;2%p9_ph+WjSc19aiYcf2tZB42D<tG)Vxb<I3dSw2@Ly;#nSq|k&6xFNV$Eei^gG`bx-<r64$FB0wr3682ap1(M(o5-)d7<3vXOU8mGw~}X(2CX#r}@?^K}-z8XIX!5PvayYl|#|UfbQr0A?a|-R^Oi#tdkuGTcd4OX|fYW$cm^wq(MX$bm*RE+Ek*8-<;PdSV=%?7<Q_r{!GEvQKg;bWyGFP;i1$5v>PmCGC*BzDOF(7X&dQOEd{*LSwZnYN1b4N?YIDE-fUN!h|3<qi%Ega7JnEzEj07+d+jTBH?VtB_BpJmn6zqfUD@HJM^~#Ba_YJIdQb5SZ0B>P^eK7o;S3cu8#*7_ry8u`N$Kp^O}&qDhw&SHytNRS=M0!-etC2F*6>A!xkt3LB+P8HWc9XVOS(hbV63ZG?0tIZwvedd=u{;0&NDMu(@g0vJyO*6oJ{~0+w}KA#?qZkSKF&cAJFe#vP}7jZ$eBFHp$S(@6^%)CUfFHY>hx+Z(TD#r@Z|O1v&MVRAY*E};SD@?=g<c9GED!w#P;_vcJ1rudWu%4Rs!b(z%4!qTi#lcChTk`h()%riQcklOgoEw%LN#=;wwavvMcf<nEMnVPOr)7Sl@MTRnYaa8hpj?v5vrUyE!s_{_t-x+td8Kj!`i}1vyV3wnCtCr=BeOtMwm-saD1@g&6H3aba+1hz6Ni!+yU3xW+r)_W<lS6?B(-A%uxVQv|a9`E+TcB#_teZY3TtF~q`f^=~fuQ3`ju_(PL@~u!vkvP3q!@>vBn``hbvC^Y1P)|fi0&0~ICiQiFTC!c)It35#-~7~R;txn!Y@6M+fVASkaWZkX<n~FY-1U5a#j!M^Tx<y7|&$y2_=a{gC+%ON*A>B`l(X@jy)!X`0e2rQ7@{H5V<SuDbVJHM5}`=(IWZI+Tnn&%XEJ52to4(YDy}R5X`lxNU4Pi!5G9vY$)4NqXY|C^vAILJt4;-26VPaM{fAomJruhv~fE3-yG1(172K529o`(!WhiMAr@5QQLI})F-Bvw)Q}1xKI^SeEQoTY1ZhsILQg|4NA{Cihs87nhcvT`Wcf{W6RkNn_b+DjRh?u>(uPXiQ<wf~IGJY5pz?qkSXSb$MS%v^VlQ;5?qd*W@fSLFhFog*)n{3u;WCIOnthMtj~7|1cw<#Hb>e6hYmXUg$h5xkIWUuM$^J}>l*3@tp#F88b^*B3ckk3jWdktngILIE@FRp69Qb}>xE)ywM1cU`=_2x6)pt)B4BU)8#TSVoqGQ+1!h3kZX}uL8$w712jd@qaA_&7*Tp#)nsm6J;*W4pzTU0O|)`riyC<SI16RDD*B*q2<rHcEZ4)qWR3$<$p?%SG?zwh@5@UL(M<-8`fiUD|e;iAcyN_4fPWFjZa4@;?%G#wBCq0Ysq%s}xm1I_ZFj*o!}#+d_yo%a;oEJlXnuv-9Uakfw%7CL#!eh<u(8Qb*eU_@K%L(MfSWrM|X4BDZ9H3LvrM}yReIfej66>jS#GQ(t+NjVb%cQbSP4l$OB)kNz4J7rj<Tu^k>q#S_WngF%}<yNR#XEo8hgY6O}g<Jqj@|Q)%^HQxTd`BobHDk$*Ym|YKDtl0rgme^AWZOV6ybvQ+*JP)+!*yfQ_qII$(3_lkWr@OgtbHWsCIv>G0XEi)p{z992su9Jez{DF<3%xhOVd|s?R1!)$}<FVpLAni6Od04n;Le60KSJce2524(p!dcsQn(Kal6@OFRLH|<j7J}oG4Is6ZL7)o(^%q<iL|}WQ)hDB<c-M#oh=g*4qWap)@Y~B0s<!I~=h+?m`z&#Q;TX@wt6JDf@md(K=a<u+@531u9f`x0;u4-q}I2cVVHbuatHuQ;FWeB6(E=j8MF_1d4O;l6P@g4dIuU!`duFrI4t&s|q?HoOPE<Byy1tYr<eRQdvMFx8T&vt*JI8taA#W2o<_b_~}xg1~&jgOPDnUofXv^*9yiJ`68782(Fn-0a(#z)$_D~d&E14I&2x1;G}v@z<NeR{R%lgiu_XRT9w$K0+=kcj8z3{?em*++=?h4A~Ig-mP&~*U^BHGH~D@TQrD0&Qa@X52bD`iIBn}sSEId>r~oU)!$B$Wcu_;WYNNA~WIu<If*6C>9AI(Gr@(mdWV+=Il~NLtGNvng1V3Lp+aNxsf>r8@LXYa*l9Cu&`uq|;jK+W72u*f)pMbUnqR~hqU8sof36QSkKlrp9GUt1U1t5vs+mW`04rEUgjHM<A)m(xtv=k775T++NVW%u8kkD<qbr4)A0zuIZWl=Qel<;UmN?)8_ppi~-TDCXt0Zepmmaa!$Ix~n6pgx@>By@`rnA8?Nm^xTMi87S!#bt>0P7Ig>OWBkY;-gJ+Au^S?z=+W9=fHqL?iODWe4IQ~nw(5_^k^9h0kr6oog*iJ{>G%clE1PF5RWVGN&;Hifh$|J;vi?g1|z>Dn6!Ds^*XMV?35gAZs84}*HU<oI=kWc%TH9ZD$1pP);<C0a=)aku_oB@z^}MydUv)D*EjEHWue1TpDu`iEOy=_kKu{_<Mf}7Qka!`cQI-W$<k+0ZG1W|({S7#-hsUmt0QdGy(@dFgHt*XEd?s}g!HU#>a9Bj!Y`%{$LyH&%US8Y2tEyhHf)kSt%M(V2fTt}JIvC776=_KOdbz%@PGEGV|^l%32j=BD#=hnEuiN87Mf;Th#Dh!Gj5VMKWxR8<@8)d@)P{+p<Nsf+?o`;C8$fsOPD}!KiPqwIet-QqLhA+-MVDOC8Jt)YU~`jq|m&LSQaaa!bU(dI<u(IYuC9w0pTpeBO<U=ibtfvMqbAJ0vH%;OdPRW6}Axx3&KNW$>u+_kZs{2x@QV@mTjD(<Z}ZW7@u6EyEr5W_>4HjI&SIuC_3lC8Q9ySMrMPkrs&Lzp}`4+OFxO(nFS%V);1f>B}l2a5TzILRf8083HlBkx_V=E{F#8p<<ZOOZ_2w$H%o3jmn$XBw=ca;>5>F3fCmz{fA0tr<ILH3odeQOOdVu25JmaAC>m~y;GkLJP#`Sn#&5aJTfEVTae|YIOf?2n;0%W;<3iuVS{jUr20<_fvqQD-B-mV@J|yh^Wec@PmZ&==qPLE4abm;q=-CNWa$SrloCi^4!i55YI9qu-sC^^n9CLeCw{kP2UFErlG=cK)#7gf+$%fC8o7gaE*PQSzXOAJpjH<of&DJXt<4Kf}Q~?(lN7!da2yPllD~ie^bh!aF)8R1(*p~d*N8uz0Z2@GaJ+JjcPcqfo6WE;^>eM-Kje2D!cl|}!RArL*?<A{`WW@;-3d;6nX;#+P)no_#9m0E)tSE6m%Tnq_suJx_0^F&)F9=ByJ=<l!5u>5v)3!VfN}Xi$NHxTZD{eE4U|CfTUn$^0kc8AEttiRpP-50BfT$m>)M_!z$kYd+K=koy01qQjG!8zp-&5wx4Z5T{Eblwn!L;A*L9l;9ApFBKA3&rf=cqLNM9L$Pts228f-_G$A@ZP;*7sBsP)8P7aeWF5aC!loi%GgH@FBCewh=AP<5UZYhX&Q3UT!<;PeMnh^OSm#Nfv_ojt86c$b6p{0KW&&QAtMA3%xPPAy~2Znz3G0WC9Fat|hot>>f7Ow4%x2UiM6)8;J#7#LEi+A^<xgZ>rXA#in<KQI9nCd2_^=gGY51DQ9p_&pYi303AR$uEUZY(bRLPkF;&`l2DL@n2=#=c*;xm`y+j4DW;zi%<1eXmgm&%Oo_sS9JOBe6vB4b%Ws6m8SA)+7BHT`&|1mg`ZM)v0o&5rI@uCaEN_zTrqGia+X+dCC#yyX{}R6jX|<L$iAb>kX#5aaC;+a@GO0daHNIpqa{FemURo!(j$we^_lY*?pijUcvg$?C@+C38h<1WuV7n{EkO}?Hm%3doQpLBgpE&L-*CXW+*~knrH!Gax=meH1`^J#8Nne{$Pjx~C1S{C(Jfyc2&dDsh=V#5|IAoV$;xJ5zvcb4fH|!clP%-qp54PMMKqDFy6IfH0Pozlog32zO2_JlkIA64iA~C9T(5B6epDFf2v=Sm9gv?{(TKDLvW5*5`jWDV9OHsq?A`J?8KVz~=ViB@o0Z>O2l{lD=0B0o>H-*y;5w)$tFU$`Zr;7n$Iv1>nA?ik3th=9Lbmgy-rTna13YH~Tomv3yqSdfl&>$^gea@h<7=)uoh=a$ytPi^ArO>wp5(g|ra(V7>VNg`03gQM0RNd%DgMDxZ=FI>GCfs0j!r1&?ma6pOCj@D?+Tcz}=lyGSD8mx+KF??X&4)CuXQZ}T(J~;ZVb64>ag^q;UTMRpnZnRkah!m||Ef$l05m8SQ)N97USQy!RhMI;Hu6Xq0ZR6>TIE~}NHLyZVP+bmb_LlOt4^-;<B5qtMu;)zp&Zh2lx#hbnXx2N)s|}y{4fq%NcK5rDCx~o4LdZY4ij2;YMGElLw)g;=JnJ;smC1#H;R>$))zicxS7pGk9UfCVKT=#p{EKftxNa~>2y}<YsS4C!FdhBGv<Xw5qw0Jsz?Uy#5uTTguxMqqNp6@1LEmDQCD(re0dnSDT!HSA2j&4*lpLMGdwgycJ9u5MUDF{4mrbYmJtB5*CTI~1yD4t&tv7epjFZK1Bxunhn^?uML@D`Z@{&Kn_U>`;)TV{&Jtp}Wo*0xO@?mSwW0qaV?8gVOmxHWxviJPT;-tO2|uS&j3J9>NK`Gfr{&;1TD;R3Tg>o^)>Q!{BKAzFLX52IT^14KnhY1b>eE+|kBlfu)HdWa0WW0$G`+9PY{HYRI)NfUMBK3i1UXG6F7ySg^zQO*sb)0})!z&V-!Kru%bnQUR_(b3w&d7)EA6_QYqb?6DWXkvz^*C7qRdEn$SXypx#ek{m|dM_*j{X@as+ylse2UXnerrtm<=KT6|Ho@Lh1@I<y5~C3}mxslbZg3AqC*?0)DA<#p|MF1xbY1?U9S9sR8IbAIy6?E6P0yg%tU895oL01FVTE?<OdAG6txW?%5$h0F?b?VKRo70gU?zn<?<Od;uQs5eT3O$h~HyB@0-{P;6HLo}{xo@km0i%M!TXG%ZM^TYmu-P$U3X^T0gVLnVGmkEYH{AbL`1J!mL;vKT3d^mEX_1{jDY!~&g|K5mVah;MKjOENG@XsX~^3i*fCz_}HssXcSaL;rTzvMF&r=?cgNxm!9-#Chyh7KNCasgl-|Jr4MYHI?-uCT)c%(?%d{L;*`_rCBJOWH5$UK|^l<A=5^bJ^1i3N&!syWlFq1GZd;`x=9+`ErKRiG|h{qM(`b}5g{q^%e3ZTAx0$H=rHI=LrGXS(zG@(KO(y#GOzB3$+IWJ01+xUBx=9h$Th1<pTQE2l-9~fhP=!9DwFTDal~LCAq|_8jNCMtcAL*hOM#;^QcNS0=CcIHbxI(OJb*aDX&E6Jf!l?`s@$?eyx}xO$(3YOL?nh50K@tM;CMll8zD-APkEvMR0Me|8oJi@f6|j1!_zD%S9Uo+?u)UlDaPj7ULo-9nNf87+o2Bym>RE3|GEf7l<Zs;-NnZuV_&e+bri%#ZSGySsy-Yd7Fh&6y?a+#CDss=^@}uk(f_P!Ma2{+EEu5N41E?=?l||u=25Cd;i(bxbaT4UikUK7HgeY<tvXBFTLm5`%HUIW{{aUgk-5?kIMD+$eAVe28({V^1z}m{653h_f-Y`T8Ko0lqk%oSPM86&QBF52wd-;SjH+SUhSN?2FPS0J63sExv%O4sQ7jXn!G_l1P3(u1XR9*7l`GQ;<M|8R30>;cN~j!>*WpH^>9IOsyoNZoYad01Ov-vAcpMP;Ft$PB`9py=55Ai^+A}UqfYW--8)sdtzRI*>p)j$|Oa^KG>>-Olj`t|24sxT6C)6V_pX>ScQv4-|Gl1nnG)n-SvJ*`_xZSmp1|oK!yYRNCQwNqir@P!U4sq%x&V>1>2pra(v-ZHGCQ4=Fy@-!EMGIy84Y_eup6Y3llh>I(@6^1P6{M90neK>~w1{d4nAdIOn^T&*05B8F(}HnmX&z}9F1Pri7U2oV?o_HcNB)ypxq>)%N^L^wHOq<5pqwUlYnZ#8nE8E`;Qr|HES;ytruUUQ>U9sV4_ObD?BJ_+3}6N~dKagRIw(Q|5}h1_)?am41rRzV?|p7>H~V~%P|EAW;8iCOWG<>!#720|VO#nDU?8(qujHOcTX`Tg4f0BWSp?{gz<5vOmH~l)Hl>&iooz0!GaQY$2WQGYFazmv9G{3i=$z&7I`BRx`mD%YHkKjioFH4K4lp4~$Zek$JB-i(cffa$m=Ct{&rWjklWeP^bYZr4H63n>3ADA)6VCaeOB_+~Oy4LKx=mhI9Q8TWzc$A&4br{*A(x?Vc6+4Cx=GGl6MJ%_ZN??4>!v}o4iAhdhZ=;Yv&Fs@h0Xz5pD*R?wKPoe{4emQm1+Sm(X11J9-CI0e|RT+>MdZ!640@Od`R&yn-I;wteuu-&6baNZBcS0vyr=4i=&vAH&@d?fl2q!{;)9Al2S#xII&Hu{V9$#>D(6G-|XK=rD}n>Qu;S2jaCy?`))H;7==>i@*YWh%USy7f}^jO*<j0zz5E!y)I>b|7k|TX8~'
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
        _detect_opponent_sells(obs, step)
        action   = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), _ACTIONS, step)
        action   = _safe_market(obs, action)
        action   = _premium_shift(obs, action, step, thresh=thresh)
        action   = _safe_market(obs, action)
        exposure = _opponent_exposure(obs)
        action   = _impact_slots(obs, action, opponent_exposure=exposure)
        action   = _price_gate_sells(obs, action)
        action   = _merge_sells(action)
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
