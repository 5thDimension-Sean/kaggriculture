"""Kaggriculture agent — Route candidate ep=90751101 P1 score=143,772
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
    'c-rlqTW?%fj)nh=p7mf=$+0tUic^gk?Zk#JUFZpfAi#8^fkDqhX5I$#-^a0}x*U=p7rFOQ;*OtGC{@+I??WywF8=tx7k~fxmw*24my3V<@#32gFJFE8)0>-j??1fVUEE$?{Nv~U`j7wq_@9q2|M~MT|M|E7`S|+Bi|<~3`fvBeHy{4`)4Sd7+l$MK?{}|W|8Q}+UA(>jZg=zk;__<q@czvYFTcNe_3=M1Uhgk1H@CO{cX`_HH!olO`NNyzzmFaN@nXMw_x@9}KfHeX{<}}FJ`V8R;;ryg=Oed$v|W7n-EQ~B>EyR>U%$CH>)Np`r*F%(aC>X}7|qO~S8@luDS37C!~4V7wGO<xd9gdRf7bfLuib5e&NSS--@Vnk@$jY7jdA?8=?Lu*nEbn)@aFC7Z$G?vf3lBn^+|d6`a>`}cQTx=*VpKwO}87gGmc%PrI2R@PVwP?r^hZD>a^42?3zFQdisOq!Gj_!i#k#F18@)WVsLKD+Oh?E_SeM;X2djo($K`y<E+Yyo5gu>wuIA#iE9#04<2Y`pA^=}ImpX{vrSj(@G5^4=F{Tzi1zB?o#U)E?z7#^@_eLA?*1!YI%xcUD~eaf@h!Tsrk)k&LO;AXj(BJR>;-k018Vbr-R3+^>^dAT3Dbu|%gz(_{KIrZ-hI+N`?krnrTI;!FG?*P=4^69_QG1v4LSEK%pSVmwQG74ts{JHDP4W~eb+#G=-P|duU_q5y#MJ>ySMLOzIyrZ_owS{BB-AQ<HMPh<9-bKP-q&K!`?6V?$*f*G(Fz!Uj4ccPC9pV?aUf&gf%*}2G@==ON~i5H$B8FV9~2NH>{m}>Vdx>2KwXupw~OsCYrN4o(1N(2XR}ATeaDg;{})(i#1A*gPCt@W|i949|;yYIeZuF3Z<c7pqH}MZ=Q<L0h|8#4R_~yEj6C_zw?HadumEUYa3%<8v4UFWNeRlR&v1-b>W4QkxVw{y+7zVlmsVu|1);-bhkPNsQoV8Jt>+nq=cpzOs9o9+C?}#;~bzb2LYQ-hBGRf-Mg8ZG+>J%itu=Szz%9eb9?NEJmAgkq*-?+Bi+-^<a%(MHoczZ-$YF~@NsDIV4>W-7;enNhK)7UXlwCZ(f1gh&%n1+I&rvD?kA_z?!lf@tnZ+ccfXN(3EPS<K(6kn%Q@;A%xS8$zt%R{tFG<l_KP|C`8D*}0>!x%G07$kt=?_$SaX1701D?!!imu^8xcg-2iVIoqFplK0G)QaF#(Z<6_A{x`H-xEh>rtzCgmhbdxmIFAPr>T@X~b6tn3M^B|4Gbf}!O*%!jfo<2twFi{dx|+B%F+fCaA!o<ByW9fCr7F*trCnET!+=R^gR7mwFc)kwR(o!kN4)Ofs>Ak;C~kQUSVVvl}l=rNFG&8+@i0?uv^uwlolwt(Pds{uQ-#BIA2SjD^#9?;+2y!}fGijsMtvFgl(Ky!yKF^vNUdzjb(z!xF?%<!@3Z`$yp)BcnmC#Mp*@L~qk??prMZpyJjadEZqMS5z$7Ys&V8+K=0IyQ0R2skJ1SJ%R|eIK4)cQH?Y{;-=I1oUiP53MT`i+K`D+}ej&Pa99+d~EMvsAGG}&(~T@ZyRh|k6SoRpH7tXlTmPl@%#H{>eHObWPes^y5V&`enXZRX&b8gW=}sY)7c~+llNZT{P68XVaj!%kvn+oNa|!YctBFyn<pm|!;aTuqS^N;jPKsRz1e@Wd;9jUA3OBKPtCjvQZsYtk*!kcRn0DaNK`l(mSC^%cgw@IwDf9_cXnmwaJN5<<M-0*)S|AgUy!xqS<!jh3C?Pfw73~BSL?L5B^$_T*u201c+>Dp*BkO|7fVxdU}GDQUO2&#(Rt4d-{cf{$-#wraA%SuRNeu=>1blWkTx2vdn<8M;)&a2XeUFifO!KqJQyUpCUaUo{;-?pR)@f$Ew6?3+ajkxZwf%@;iig=`;BjYY%Atd>?F8Pnnk{lo+jj3RgqDpTQkRVXuEoxXY=7O7rl0Q+X$3x+<SoMPf90`DUP;T-=GkfSMrqX>PsyJfvPxv#N7_p%60%Zq>|3`n-gl95Wn|)KE(*8c@gZGq(;4i`X61UmfeJDrEy@sN7Qiuv9!Gg<ZMmPJUi4FggOju2Ydhs3H%08gwl1>G=Uv=sIbVHBj$t~Y|g)xm7#aiK9O>VeMa*_q>Jv@y(x-$xcyy@_D-ZnA5oy!uRs3zD!_o^{Nkqq)xoj9=q<ZidCUYbI<^A?Hzv}$D0ShmZx3r_l@!pIun@**7O1^mfPM~8BlL`S(p7G8xFD>(s+#f<B4_@pvai=B)=bBIzc9+bH1tR1$d|(loj5{{SUXTEI}_fOJAqs7s<EU4L65o!#8%@muCW!l`aR&?$rg1?+-z<-K^ez>rnh=_KcOcaRPo+3d5GO?S+6}CSkE!&5zY%m8VX^kNjwzlO~`F4a_N=OipR&3Go+<PJv&$?B8_zcp>}VZV|Ti1j`SRy|8%<}IVT;K+lypDa)-^M@YubOI%<vvWwf=X_}_(yP@edKztvq&-p>50m`rUwUhhZA=XHWL;m5lf`stEcH?Bhrvxc%A2}x*z$fEt%lstQ6U^_8|xyk)f4%31FHlTyI6~kMQs2@?zE`{9k!O&dWS8~+=F6a4BZlDAmBQ;_&z`v@6v{c$yIRN7ZWe#W?yIqaI$b?BuOxUTS-y@xDQp<C1@e;{bm2jPsV(sA3eo!my%H+&zbSp*s*ZcOQeC&7vosJ*7YaONj*3Lpz%b<@Rd~!PJKo7Ea!(@Nt2S&Nt51mL;Kx$Br#0(<KAoWpj@9DjPU=+#H*kDR0bd`;kQnHV-LWz)%)3JlO@cqkIf9?bWuWogERw<?tt2Iv*KN?9t@7cw@rmgBh9~_?5C%g3@Z8{u(68wdS&HZ?td9)yl;(e^tbSd5C5yOwaVX&*z^wM5jC*;L`o5%cibJ)28i<ra`=CuSv51iw#6R&Prk4>$CCS^Ta;#?tSMTtEl;-{EyYC#MqPn~+^So!^j4`g^B?=o8#F7f4v9=G^ZH>KY*;lV!%7x<DwvD;bEUY{U|X-&f1)k2+4w+b;mPfP(rM^G_u0NAiw!Z}9CS;zmXK+GA}>Up^i%O>5!ZYsRDU}4$8W;m|E&C`>fD7LA9Nl>Osj3Z)vQ__MK9@dc-ofVJB{CZ}#&Os*9z<TQJ8;oV~1E+h}#naMR_A=5Iv+RpBU^thzN?SNYjPp8ZbUM@Ot46|a5bZsyI$G)>B+D*A!2wb_wv7LTn6=Z<4tYGg1?}|mJZeflwT<9hsm`fDc#wef>}qKAPqOB;ba0=)f1CgTzPM~xK1wzRq&bj~RgB-3sLmwqY2`qaI*H|^xTlj#CrOd+!lVsFf3K|k$>uYO18ZNY11GhF*i95J9>g0kyv*v@-efs`3C5!<u}xZ6F}~|M^@>ltq1XmYPLq>L0)oJRjqJ@{>L(DD@o9Z#U@so{VV>T+O_7=n?i5kp7JJOZo*1Z(=>(GPt~iYsE@nE*Q<bRe1O1PjtAp)tx$a02bGDodFuDP{E-XmgXfDQsjDW28%K(3YN-`0Kbz=Kk$R>8VE;%!LQbBa<x*T?o;{%{$ba+77{ATkDz9D=M^lx%S4mYE4OhnN0>fyT2Jnc@-D~LrDSnGECSh}gmB^W7mC0E3Co)1Yf_!(M5aaw>jnxaL{law>3;&5uZBj+az*O@7x3|T8Fybw8|3t+?*&ZIdf3}A(l#ZslTXx~HVUg`54{ICt?{JKK`8p&?1R%yt(ua{Fs6{mLn?nh!54Ax|Rgl;veWe=pqcbT*J==kkB{P;Q5eLyHF0H*R#<f02ntlfu+(wu@*0O^?zAZ=9uDME?}G<AG96pCTr38F^|K6%7;7`kv$pS)FcTpq}bLXvep2ntUy3}K(nj!SnsE(@<m<Llf3HD#Q%3u=7Ler<r#v;<WWV8FhGx;s0CH&jT?A*C4SeA+3`i4PKr)CR$7)9r;Yq?8Ah9W$2CkNkxqsuZgcOhUPcq$Lr!92CX`B4;q6*!%_kf+!hBR(qb2TSUp{nhHZrG@$|~fI=5m6rwI+cxJg%IyZ(U<BlL_Ar9zYk4KLox_wqj_#$DBl;8x=JH9o5t!u&ymIP3!7GTeK6fl{y*WB=fgS|3+5fq9uGD*tO$#zkswrOHC1&t13ZKR21xo%{8x22T}LdobvXGu_ktz5*`aF!AD&Y`g<PMe=D<=Xa|!0J@`Mc3Ax-fdZuR+9v!yoS7|*6k*f%tp^7p$u8oRaLGZWf<MTs$WM){B|us2}v_LkmO$*`uA6(9!+8mQPR&4PiGk%fh2|NmP$le%5;-aLCY%a9b1F|O&iyCt|WT_U}i<9)7uKW0%^9$Zuh*6(fJk-cx&a*{`ZDQF5Cn#1;sa=g|#~w(#ck05dq=McE;HONZs-)OwQ1qL1WW80jVub{PM!j^as@7)OlOO%6e$Pm$8ZF=(tEWXkmUSZ6sc~0dEaz@fKDEN``8^9!LmHXO}@6J8q~As{1P_<3~57JpD2IYO!xJ85QgCgDw1E09}p}a;jB*?K+jOEr|=a9#}BEvK&Z6R%;wMol-pjz+{ATTyEcu7C3FG5qUqEC4xDeq6D>dcoWg>qDdTTrVeSCTH}GL5mHs{Y!*7%a=V-aCZPSUtdNw5*1W?U_QL#;I4)P0hi8+&pa7elO7t@_I_1=QZu+<sl_$&Ib5MbP4&L@NlRPD#TE~%ApgvWhDNP#(rBQZ4vUOCzi#2qnc;#0;+zg+?wJhL5T?+F0v~VM4@=(5r?qw)A2Y?1ncMvqdu?_e}04UK^qt?)_kefFLok`?c9j~9HU*b@RCdLl9u1YsV;)e_34Y7srw$YScG~Q6FM1;1VsQrX<HB?DLrA0c|l=DvpXxktxn9tb5I1^UA1l9rnD0>$J2$auELTht~8nzp_EAWX7x^I=N$IS$VXUFri!5<oOyy2SFH_~vu^K{5KD1I<UMG|{TD+$G;g-j(YM+MjN4Q@>ZD&3QlLP}M5?XdD8$SOx8Sa-%5DQs7(+caSEr$XB@Y$|yLF_aD~blmTl3W({~HvS(B19L@Mtdp&dNI*WbMdGl4Fyyv{SIdmt<ZODQx;C8o3)&KZhjOOlv)d$T=SrjeM8E&_T0o0qfhLR{nQNSUJKz2)<0sA{OOY4*tmNwjkrzjd!L<PkSd|L04&<OCbby{mvJ)r}J4c!qEFH%xB>DmI8X}n*p~u&SR3Kubcn-A$0y(NQyH(2GI-Z?<bQ51fmZ&r*Z#}#c;__+d$Z%;WD_vFaLCqP*vu&5d`H*ZpUf)*ILCfN7IvM=LW4`~WcT85(CxT*F1VIQ{QM360TpKyY3Nk6Ey`UL90fn-6HeR8Epc;Wc`Wjr{R%+Oy)UhBhm&noeeLoBNrXHQdx+M0gh1%r9+NA6v(0|fZ_a-@iJ5tUrsycBk3L-``$X_XHwi}3C=tvTBdg+R^NMQ;IK;kf>4mdsM>n|(D4{wO{S(rIEXS+Gu7X{*@fD1@k=5EZ}QBHFTAXw?C^Wly|7imEN$I5ZAr_)YZ7-p}KyxS$Y3t03CJ?Ct*J4G8!--*xN;gq3bkWLYzj-HINU3uyZ?Rg$iSf5x`>FsQW%|LOg4j0GsbV{R8i#bD~sX>wu+Qf1){yKuLBpE9cMKq#LtA2dwJ!VCmxEfK2=}fW;DT$*bEpYnJAWtVJTG(l|lZn}7;D0IvlFp=R`Ur@%B3(<NjLi1uu}#fsW4_tUlr2r@M#_b&s)Sd3T?D9rlb{wGAJ_^6wGr-V&t#4o(!L%@taXN<cPetJGH^2_$8_!yX9Ng*$no_|<Kp!H&58&TR$Bq1G@sbHiTb4_lQM|5gbXf<|13<icV|YzoZG09^pvL<l!~x<)c#CbL8qm-qz8`jd3Tai4kbH1@|1$q!JQ<%l3YRuE$x#(l<*LhiHdsgGMiLyMP%Mt^o*=MxNSljA8CPR*5-ePX`#%iFuTV+B{Db6TOK6iLtaNeCW3s9>`@p1PY_Kej_+JiwN8G%yCs_(K;b9)@sx5l))@kF3L`lp{z<y@);};aHH6m4*s2RochM#tgrVp^p&fEowUY0(ErvSm9ZSJC#9I@3aYw9E5^|vcqNttHr!r_Z2lW;CF^LS&%v$j@c~1CN5Cp%3x#&27l*55@jUPk&acN;q@?ABTRoWs-xk9q8p9r2&T^hvA#?ax9P<OPQO|_FiW|2b?;y=wWR;_k@{xNC$=7$SoV1f!&z>RP{1ax5LC?(<MbUUS1;!;$t2g1tQ<5v?t*`se3#5ns8m103VAjWyrCycVs*)*+Un+5h;L=%GBsRlIyomG-htsU}y>;l4XDO+eKKAva_;&=^Sn#aK>65#b7>1k90v`PgSJpm?sR+EA!$Y;Vz9y`+EeWtEsCiv%0m-M2A(8a4;8rl*(nLWol>1$do(K*8HG&rXM#zJl>A&3E_*bFVy^`1{_uSy!wr|+MFL7O@3Ag46jqhL6z0Xq|uDl(UxNsAtYBc?^AYb2TvI_Jmxf)kvW6i-A8kpKwxp2Evxl30u)JPH-gMNyu9NWkusWAH|h0g{W!YtqAK*uz&t+00m)kn;B^YOxYZNL+XnuAnI=*Jz9zEEzPYyx|fOfn+wxk|RNuBv*nd{vj`_({VS_C<&+Qd51yrl8<+El!`D%hw#?Dv@d2bI{k>Qtqh}8G-CX!C!QtcV+#;OMj4RG)3`!EX@}3T0LYJr937IbPin}hk3kShrOUQaGb&maskZ!`*?+Yu@~;}iw<-aA0<@sjwaYRHOX5Y^kosss=Fz&RgB0)0JDCcKkEW~QGN;bt^C3^Ez(uO7`fGJNQz8?D?DbCh`wzMbM9IuJc3pfu(19dwX}$~jgvH!NxhzDZd%cT+p6g11?hborvt{<q-SgmS#NK(fmfrHe0N!(6C;qCGdLMg#8Mc7u%PqS#H4%*R5PT~Oc@Vo9B~&&QnP8#-5R)9!Th=Q40&uh@S<fKW(w~|{K0#SUNp)M&9O`qEV1GErQFb2u$8{E#>AM`nwgW{|0^X1-(@1uz98KSs;VRl1|0YetpIaRctZq>~J6?uvJthicNwGa9uMJQllH?H=RqN+-#*feGC6E#?#r52hD<lXcFGzcn*-Qns)j$p|&BZNbdCFWS&Z6x~`8wIRnt<+X9i;O+El91%YI|nTja(5_qpjc#eo}!s8A~>*#j}sescv>cI~k^$Gnxs<Wo6Vx=%Jk4DZ>@#J*LRcM9J}HmW`(I6e#69u!Zg%zK(Vat$~h+u;Ya#(q}yL+~;+^9c);SWZelo?#IQlX9sh)1GaIYMx*OxWaoV*GIW3ISpewlB0R;9o(0Iz)72`%f6mB|o&!S%BMR^kx}%1g=eWzjc|aT8>zE`RHz{+9b#};B6$Ngm06})XxkpO1m=Ygoj=GWUj&qs24vz#?tb;~42~aexT&x=)ls@X?K7S$p?pW9~nF59gkCvzXppqs~&aA9d8^HB!Qe;J}qeWG<lOzWP1F8ye1aU-w2y@1VJE@Z>o2V^NmWy&%IvG^%iMSJ;5GCw9XAZ1qx=)&9azPRX1f>>7lT6>A)BW^xJG1UuT1w%cF+0jqgeccs7P@xog7{E+R&nj@CVy^xgy+HCex)NO6tU2t69>npWJ-I-&gWD5r$qvC3Kwe&ETwck`SD|`#G^->P5Brxh;V8Eom1aEns$vMJA;N&$i~xC$jHqhC7r@Pl5-;6dWW9r0fFJ_<lA)HBq~#=ZHM(PZS6434#^VRhB!dmX9@=>(y@B}g#y%pu`ozY5Ai+1J$u1inJm|Wp)Q1*D|NR^nP^fSF6S*mPXPQCCiH2A%_G+0lC%oKV0W`*y_C-6w5r)E732T9L<$ZSUE~_eb9!Cl0lFjrQQ0|>7HHJ2FY*7ZTMKNp42u9bcs4VN%GgK<s_@pNeUiWx&X`1PDooy*gxy4H9%hs4wR%XS%=_TvqK~PMM*Kw<GOcK^(Cuw?l2adupkt|wfXk^EaIF1#(Y=e&JQg(@vrt~B6D-EUujC@7q?fX6My4y2{ofVobAO=g=t;Un0k4D7wY8AXz;z=f{HN8Ph(VE{&bhYEfIJapJ|>k*^sK_d8Fe00S^ArV<N41zS_~2JZIX%j7D?!V(unQKrcpEwJ-F9Fa8T81bD^feOis-`fo2<^<GNJx_6wzEqF8b!nF9qwhxC#ssSryQN;98(3?r)P%;FrA5MWJRXAYl+RC--+g@p%@QlooS*DX+vlGd=$+CIbEn?4Bekr0Se>OT)mW|C(@sHHUr({K@L)|9*mH&_i-?if_T3Q&FaS6x2B$ASDCEv5BTBvDwj#dYW1|2k^e$;Iq$8gSH}-4-OCRo!V2gOfU*;B$*Wmenp?NN%zyltL>}C7B@bjYAkJ`2=@iQgjY--XK;w2k~-wB$Zqta&z+fJsE&;t&$8ATAbq<+oSA!T+uDf&WDj*xEosJMQn>Ivy#L~f(*E_A`N!OR~4C_bayOE4{)H&zPS57o%m=CuA60Yo$YeCdyN8YLQ;eJY(u1Cpw&neAGxNPBB&Cd|A#yIX}_XVhWDhXTUJO>D_$uJC@E#f&TontT&lfl1n9^%6dOt1ji#<M3elG`2qj`q;V1K|TTiA^fHv0%LnW2$uIC_A&LRCHB2$76uYc|OgdlL6S7HW@XCtB8-6#uQkr~mFi!2`|;8e$z<R_Ig7lA1?-3|+u&75$WXHC8n=C<YeY%2-;z=IO1Qc8H%97u4FwxJV)PDtk{Oq0VaUfttZ7DQAv+>1a`tAI^YOQ6rbQR|e=W^5IDP>^LLiVMnc=NpHc^EWNY%{kJ{i951_KtiB%62(H1Z59MdB_&|10*cj(NuitS)`v)~cSdyjl7gRJmlKw*dJ->4G(~=?UgoebAq<df_a0!RQq!s=&SU{tC6~1cS^CGXQ0kD_NDZwW`P!1pXij8T5l~%`(WL+-c?5;JFBx(ZmZ78=dlh=<7}rpj3$RbUkI~b^Gt)I<SO(aT;}}~H84rH1s4GvQGzYhZ*7ahUG_Q#j2uxSO)AH-dd0~1@utfFYcMlT<`%J@)M6wNKCFH@}!!}MRPlENXWQxEGl);{q^!D_&!(#CtQVGvfS9q8!7_F330*Hfrxd|*0C;<&ZQb_=c@v$j9EGJOH`(&@BlE-zlQ?-VI5G_b1?03bCEiqqWnywK=a7fblOg7C_d1cnjkn=BX6*rphlP)aU6l5`of%!uUh)AK(s><un6cLj4R;WjxOD>IUL#ISPCV%A|5WNhGY*HgIp`{$_c~Ko_IL)6U`SI)-9I-a%mWl}+04GLJD&j1oJewjRNVvo?|5?Q6^*IM_GkQ^WhIK|q1^{TJOsI^knL*ih1NIVab7rH(AFG)asaTvo-OPX#nHX~zkF9J>3bNs<z;Q3cgS~2krBGIfxRTrB!)a`iOa|Hvayni|dfeeLse~s||0Q+3m1~5Z>jQnVN+Q|kJL%|EQJ>!s>xsO?6-vQNsXZ!_Bc<~5*YoWK;=b^LwmVs-358no*+JS@5iFrFGL+&ix{tLKI|VFB>Q|LFLLb^u7B-T#LpIG^i5p0`A|)w8ryRm}HTmR3gR?8YodnkynQ~wtDxo*K{F5X1X*UNH+U8Q)9euA7_$t>(&V?PCEajHYnu@?7n2_Bz1?N)%d??;4coR~{t+|R=SGLXO;PXO3_}UBSywwbQJtZUMKV&2s^@9<$1HV@rqR)+1D<pYg04iNKz9dmE3lt@}te9K##F?6sJ0|L}G9xo{9Sd9~t%qtM6s$=Sx{S^4rT3T?r0og&Kwe&yud)f8)Q#?jSxI(=e2N%pVMgEFyn8n%P;mE4=TAiS0s{OxcqXc2(NJvL_e8tXm9(Rpx0Ygh)P0GUz#zRYWmevH#bF+=totwK?DR$Hx`(et*S#J3q*7xWb7~{T@z(^b|BC@lvvSYIii#r&nfR_n=8$4dmCB3(Kc%Iy*eVpEC=?S=02)*bl`z+2eT^jIc5#Y2+E;V9IaD=-05d=X$<Li!EX^x96F;Wi$)?g@L`cX$r%h$<_ex}bIE0l@97kgQoB^7}HWT#K^W{`OdkU6JSuB8KX*%^CKh8m{ns5Pv85!W_Y^XM3mPruWdCp5`Q9!df-)?AI&T3#!Hln&z=hUVD`A$u8@<@Qt((%9_dp?jk7d*)oIsBl~c{yLR6z${wIF;@)?G+ZaYRIIpc7{yw(vxR2X=8-7yA&KPQ>LqL!`V*f8d&a9R1ZV*zL!`P;4cI}n|i_)GD4Ztr1SbdvwAZ}DL)OkxTad(UEl(O=}yiwBcKPEqBO*F=r8ZE67sQ=edwDrD*GX;5|rY58$m$&bg0+)P`!Ad?PBSj#dvsNoQ8cptZ-z~(W2=aAuQ>D5=(2Y$X1$!G0o0b%j{oGLxN?w;X)}vO++xpelm|D7D}4~8%WPSl0Fhg+s~b{Q_VU?q!rCDrHxqkOO3H(=lW}qUnh=u%6x;UU%~<s<EIV}s8C7NZei;baA9&{W$9&<^EyT`4t8BAW^cJknqVfdoC@_$_5xF6FBJjqb7@YODOGTh$Sys-Cg(oUnUS%ES&MU+xT6JkPR>K-QP~{HbZ>zug$L^<b$1DmjEYSmsyAOvGy<FoQKk+tpu*E8?>Z8g$}{H%@cB9VGY)zwJ+$@`=cL5oV>uW50O{q}$`ChkIjk4AuVw(2V35OX+LYKP!w*Ivm39)D2TyZPdg1M|qjI8KV%%nn87%&lI=avLJRoHh)@!ie>Y)Kmik4T;N*IT;L0}-!i;`{Sbjt={=l4t8<wB8M+uE6q!o!<3^LFkCCh+>2bfs(JAU%BY1Q&@|U|;A;9jR=MtAv7DNwJ*}N9)w#EhWVX;@omp++?B;xSBAa%%Inb)J-n~pV2WK9D{NuuqJzD9X1uh6;&peH4O6foaI*RK$4I?2Q(_G!OpdvX7rhJ<@RwABNoBna$!qTpoKiOv*&;#1{SsMuC54%OjAd7;aDp8)GkVul+zfJAJ)kq3AQWMPpU96y4o8O15Llz?X{C_i~-RylKX1PYiJxjp~}zz0_IDQNuo?mHb(}<DAGL73r8@wDRiQYPNX3(FpPnwypHF6sjysY*(YewO))B5NNN$(-z+x<$PC1aR#Ja9CC*>A*Fgr&B4QbIw!|Xp6dFKZ9a4<7SZ!><j>1{RWzJF$iv&iFLjWD_7+^8hOgPJ!u?z842hg*d+>7A?E?FC9k&vVyh}d7{h1%b3r@t`c&F+Fbppf^jrn0EE)7Vmjz*Zt|q`xWaB@Mt{<EeP8f~lvcCu6MGh>(t#8RL7@X6_VgTv)=B(qS9}o09W%eM#c>tR%8T(ml>wNiLy<`BqBNvqTw?Sn~J$93oX&Zx{GpjpPAM2!CJ^hze9^&Or2&K0UA;6)KQE|4iv4C~z&g@P1{PEJq0WW&=uCa&nD=LduF#Vl4$BW>b-Rf+R!4ZKyWmlrlQWyv?hGti^r09=|N10+@UupOHVX#$j+`eGVv;UIHXB7)#@}k~A(g=gC>t4Cf#h%5kQmN+cqO=Dv2kOpmazhmt7cST+u3W9~nlcGByXoiZ6o(g3CsIs@MSNp;MShh#Zaq3f*{yt0Sj%*TE*k|C#n0QNEfpdlg-iO0K`FIRwEM6y_^|10#iM7%0d+%o>s<9EM7Y+K$i{<gX|)8z;Y{c3LN7fiasO@s#~d%iVi@N*bzq5rE5wKCtUO=9hb4Z`&3D|wZYJm++YKYIKBhcu2E'
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
