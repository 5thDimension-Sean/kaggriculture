"""Kaggriculture agent — MapleLeaf 4.9
Route:   ep=90914286 P0 (best of 30 games in training data v2; score=137,616)
Market:  price-impact SELL sort + NPC-demand persistence weighting
         + opponent-weighted impact sort (contested items sell first)
         + premium-shift 2-step lookahead (step+1 qty//2, step+2 qty//3)
         + Town-Center-phase-aware terminal liquidation
         + NPC-threat-weighted opponent exposure (log-scale yield units)
         + order-preserving merge of duplicate SELL orders
         + pre-terminal no-recovery bleed (MELON/WOOL/FERTILIZER from step -13)
         + price-gate: day-adaptive threshold (35/30/25% by phase) floor-crash defense
         + overflow sells: force-sell excess items not in route's 20-step sell plan
         + fertilizer sell: sell excess above route PICKUP reserve
         + opponent-isolated hold: defer sells only on genuine opponent floods
Safety:  shed-projection clamp so SELL quantities never exceed actual inventory

vs 4.8 V2: new route ep=90914286 P0 (137k one-game score); fixed _fertilizer_sell
           (was starving FERTILIZE actions, -14k/game); fixed _overflow_sells
           (front-ran route sells, -18k/game); fixed _detect_opponent_sells
           (now subtracts own sells to isolate opponent floods) + wire _opp_hold_sells.
"""
import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c-rlqO^=+{afScOtY@M5phRUyQ*DSaB?=_vfg=nA191=_a285-LH>Ja&9Fb-I`^qlb#IR;n=3ZEd-{Igx9ZfXQ$PLh#lQdgm%skymy3V->Ed@kzIy%5&p*6)_x{JXyNmnFi~soZfBoBkfB59X%fJ5lm;e0B|9p7;)5W*1e*Luj;&(s(>F0O5-8UDP7vJq(zxn>+@@Dh)-M70J?=LQ|u0Ov2;`>+My?FiMlb3JqE-tU{@Bi=exZgj#dijSRe>i-6==e_;ce{7*e{J^rH*ep6`|GO@1AMo6Yxu3xk;gv9F24JAxBEeK@|(ABez-X4+MzAcx9wWU-o`$TW@g_jy8~)UUcdPM{eJ9T2VTE;x!bpY()!0=d)Ne>X?XE|_txvi$3HsW7>B<O9ibfplmD<2et7%ln;&1kKibFl{-nHn^W$K2axz5M>udC}P1z0F8HX;?QrNQsr+EL_@v$2Xb=m0=yXN<QJN<*@!GmHfi#t(|1CR%KGdS6@w`_ww`?tjz%t&bZsG)_YN36=r7n}1SwuI=y!ZjIA4<2Y|pA^<e9OUi6xk*=Q|0;hJ=F=j2M0<7r&SBOX_u1~n_I#vEE<YMC9W?&970oN-@D|-zOV5h9(DyG6Bc57-ctP#wfZBXqw>3|bxDJO)BJ^S3vUtLtewl8_hi}TWADc{DTHj>)qSVrU&K5TmFRb&qA*X&t*h7!I_MF~C>j<A(N>{)BzBG_NcJ1Yx*ROXk-~ask-P`xCUcdU+$J4bx5!BCu@gXMVupb9~C^QYr5$~5rckAc{njY_Vum83WjyiX6?ZO&e8*8+04XzzAON~i5H9gELVAHELH*B1I>Ve)56a7&?sCp-DqBX0dEHL37jN97Ws?DZ^7Z6@-)+jv=VZNi8RchaVBt+z7|F>XQI1LR3dTCqz;i)(}V9OuB!`*qlmKsm|PrM=Lo?6n-xs9>U4gJ$L6l{-mR&v1-mGDBzNG6-}(H~R}CBX^mvtTDLcdN$$weHfxlcEVjT4+kZbXurmT!j5IP5^y52-tKo#HeU?A7*ONfFp)z!sGP;3)G0__RtS|z}NSSW?f81x~IkDD!9#?US;_=Q4<b)>|5MhC=V~D8&lYDu!b6KZT{BuJ*MY#;M+N!*xxCSlT&JUZ_hc__n?yxzma+gHx*xiT-{lhbJjIj(^P4Ho!exuy0+K%pUu(VUPHfGpg6Z87TKgjtM_K`SQEf90EKHN;mBxMjR+#^1MKB7qFplK0G$@ySb)gF3Ruq3dPp`v#D{^4NjZwro*>!_NCO!-yfs}jD|^9enNFlyFtmK9`A~6Xq;osJD8dQw)?t1EB6v;k{2?+e2ny-NApA%$_thxZL<O7|PuEh_NV~mX+yURzc)FG#)G^tR7t{G{kA80GDUfB)to|ecXW0X6SXk8&5L|3EV28H2ZI=S;nD>JR^tUhG{xJnb$vp5_bzwrFxqX+I#({&~PwWKXi;#Y1_(b$KZFtjZJ*9`qsYEVR%z*m6X~^D9IaX*ct{1*YPYw8jgAv4r<&0a$X52Ue&WZcgwQytKr>9pg=JC((cauOsPv&*sx-+quC$Yt?HN<+{cnarZdwWA2+uMG>)>?YoVB3D&LNt9mQQ{{@!4byqAD^kuawb#!S*PiS*ZK4fMPg)ZsOp<N`*oR4Ci#%O_xi>6-&_=?-1ix|gNKf!PF8~lWVL<$#nHsD<Moti_G1d;yZ3Kj-2HC%_U)fObm$A6gL#u<jBI{duU7G*A5#^M24-07cf0NJIzUgz7Rk}qu^kG~l^z7sr%MSb(o4{-4!I1@weDlCW=x-!tz-~kq<gSjlp`W0uhgGx_G1oCx^e+6u33!PI>hYRZQtXDG5qea>1t7L(75L0#yAEfHd}#}&9c=j=#ZE;Jem~RN!K1}<SJ3r$gs@aG2o61n-Vf7H<PluW$aA4t)Q)F?O^NCs6AU#GZ^)BQ)NQF)RQP#SE~Es)^9{el!X#3*=T(@Epft<vhU29A`YNt5d;MS;hFk#W|0VnJiJm<kiR5)esB@=%~KC&6*u+meP?@7eDPD`+BDIBWvm^;2d3XKi?bI@$?Y(%nl=$;oQ`Amz2hgavb4Ph8Xe7=JaIH!K|Vqq2fW7)2^R;wgwl<Z4Kf|Ocx0uEocU!U5)tJ9qT&p_bJxIDMZ`rY1V~ayw(6?21ef36s6?vGh|>pr=*^oC|9m+>hsK%573k7>G7tH{J#bMxnW?SRb&s~DfcB$9UTbqY3lyzO3JkzwnqX{i^GMuPJl3S>#|r*Hyj!hJ;Q_5(0^)wkCzDJ)SeLx(wOOv<l}%>3er67RrpzynHas5)K30MaE~<}jsfWP=Zg~M=50C31j#~;wcrq>MQY-pt4d|xj6Z{?38}(j`wImE>3IX+;MhXGRSHlcl(U<Afj;@u;cHAy|(|e;aW{7s6sZ6`a&VD*=xWjqz=69@dR|c~cXJf$98YG=$(VdRtCPwH-^VF23{#+KnQ7f#tP~3}JRxD;XBX1}I55W;{vy@6OL;824fcr>FvE)>$+2U7lq@m@Z>a{U1?yHgP-+bbD+_Bhx{w#qc^5|%Lv2gcK4d2&u(T(J6iuELh+*n7fH?0(HGCu2N$RB<<x`*H+OTrF?H~d&sB@5fp{feFMv+jM*X@tm}!J|5Z*Yx+{ZPnWchE~&1M}yhzR)2#PEqJFJeY!Yvx6xHBkbRtN<qVaVhCL9;ClZ$fw>&0=(tPx{Mi#CS>mf{jhz4vDde&^;IA5tT#hI@)=z&6Q(c(s0eZ?D1*DBfALcnIcZri@f2hn%0UjLyJX>y=!<yO@^3|#UlGS`0FS%JIlmsW;{pp!Aj-3pAPz)X$g=4<z?VukfuoYw9EOE*nAXdSMz0{u@PTKL@JKTnI>C;EBfL(BjpjFr{)lN@dSn3MDxxiovS<)ECITSCmk+r=y4^;5l(=>L=3|3F8$Ep#?o&XEy!DGEX*aT2W!Fcr=auFepXy|lwyE8>rs9FK*UHrc(=X`r#DlSndTs)IVw6W3WuquQ?C^>iTjfIW?5s=S3b``RnP2Pd6IJNp|)WI6PM2P;i7ilP)!QD9=9kYbeR`+?vOQg5&v$`?PmaBuEAv^=5pcYIr7Q0xxU>*q8AG^5xJkjmv3UjE%wg1?#?aTBR9UY1O^Nd}qk;owpYb5n?KiAtgl)i}T~9H%<ITMJpRSw80&-<iO2w%J+P;-?tNp!(WLsZbRR-)5cP+*fuD#=Lp8azxM12sC%L$*2%(Gh}DfA%=2aNk33vAs#)ZnADkFp{hqv5-}ntCg|OqV0DfLV^Y#k1ENCki%<A^o0B)4MqEhRCiP3~^*Gj9Auy2uzg5s`gzzn4r&{RS&Dl_iYKml{&*muF)zOz)?ER()O_bu7u5_NX{1h-Smvr~BhWu=F7`dV%iwvF0^M}^=Jre0%;@%m!gT<su*SUgJk%O@+c#OVW$W(6VVp4b()fPL;#FK(z$S7RemlP*-NJ!}<l}C>kBZGq0#`B{Shiv$C^^|2gOocxO4?s8{qJ3mcsIQG9;xz*_+Y)3W6SG>QRf9%+`X!jqBF|WSB<xl7fTQqqbOV2d8nrR>7-Qh{KRO4BG(w7krd-PT2{4}gkF-t~j;0fW7j;rgNxRX??kXTT`Y}|-g0^vV6$z8u?&xFt-mv(+E#<HksE94v>|Txg-TCMZ(38{!6@npAp(eeJ+BAp_%6MgFt0(?(d?5ByimiHE7T3rs2z}04R#Du*-0D`(&zVx}6qsi2{+Y-a0W`8Y_+$l-ofimAo+C+rid=tnb`}aHb&i3Go6JShYFcpGYz)X!m2wCxH=~4uNghjl`l9iV)RrjF#l(zS($1EFVrrhmN2WSd4qb&!h6-%1@|>WX#1CRYo|%kMNHw#>mt4ixM!8&z5RHeMa1wY&-8TN7I3=k_xBvkVeih^HV+O$@a!wjLVSk$@8c@y&?1^Y)D1n?@fxsOpWWUDVDfcwhrU-7U_?5U>)I`XrtZ7K(d)*{V8e4&8z9<Un3jE6bJWRbBd<|i|eolk969fec;0;@7kV&cC{u7_{nDT-UsX#&0Z6wCk6mSRqQ|TEq=PRROO)I|3_G3a_Dfx*^th+U}R*w6#W#eRdO%Xkd;~fU+&VrVfm{q7b05LlFsH4s(2?+ygRIW=gW?f`ic^#Eb;4XYUlSL+iwkb6WpLNKsA~lwY@Mzv+>RmkOg*b5d!D&`|%CRbZ)eI-*UAH7OG2mICFlKRxt<&Lan&-a49E|kE*>NOfXZUE)Nf|Z!uRQ8a31SjJ(v1xP5ygho*NKDfsx(BquH%{#<4KIbzup`Tx}qi&L72n~0?~t-Qin0Yx0MMNG^PDpk$N>w7%FJFFQzrQ+ZK{WavX2bLz*Z*dHErSCgf7Ox+U$YMLYlo4W>fsF>VpWDrjFImXxWFLbm-wx{;HF=9hxXnA-)d5Hw;oKEf)PH%EZ<!qkQA`gAc)`iQ%~E8)ST)11EM{Tjw73&ECCMCf8taLUe3ioWi1_^|KMyC%M|S-W{f+(Yy_O4?+mP_9N9F$K5q0ul}csu?x}li6pujV*1?HQ=Wl3v4npR%^0KczPz#5fR?XxX9pbi2j?&Z|N?aVy&T$tdMa;k^-7IP}+V2YCT&~^Omn*F~+!N0*udqyd1F`4er^!54+IFBCkfUE_d(V&ys8nn%I8D;~ZlRoRGPeF%2R8d2nLVz7yjsgRbBOaSZROLW^Ei?WY#lNmwb$wP=X#z>QSGpr-QDlA&_23Pk`Avh|<b*FBZcGKd_Fn_*OTkz9#)xqB2COVWQ@_J_zXW?X)0HV{oJ%iVMN52dLwJpHTjC7f<%U|3L3E&)X<B_5ZK)2j0N7|keDo#ImC6t!Yxg7JeS6-vv*MPCIdi1nv3kWIZW9O|MoHL!Ao3#WyW#-y$IPD23uw&KA7^o{A&5hJy%n{H8$H0D0kP0|WR2^oQ^gBLYxuPdt|MZsl4uL5K}Yw(zHW!j3B=Of(JWd)&1K6i&39XAFj_PO~8h^2L^r$Wh^40aL7g`k9$z_DWJNcg_V?O7-Q?W37aY_K#6D@KGeT-n+UTWIz(3o%4UOU$D$v|wk;b`#cOe<Pd|zvJKh&J|-LSeFY@AO(lBlmL0iL=5b{%@q12XbKr<hqO~4rupjZFpaoyJItYm4$&M#s1-|6Hg&ZQi#<N`&D9lM%oxAv8FgyF$KH*~fef6m1RdLD)aEH?0eX*9tJGYg12LS>O1{;{d#lX3s_E;@P{(ger;&7+VxOfiDgGcyg_yWUth@lRBvdYQ%zj%0Hc;NcxJ+r9r!?AlMz3$~3m_DoLS<c&NGfclRnlDJ;C`}G(RhwFu|3(>m0k;`5%Z(4@R4Woug(=KsA{zYXv^L~Q_EOf-#FVsirHny<eJOAPFPP(xsF+-e%=0q?f;ginTQ9P$RatM+~a;}p~vHIREm^CiL&%qWJ|>507iYTD7^WQvuU#WV$vMmY81yhy8n+S=J;~d+aLz6M!&GSr_6t)9y+r(*||y<(D8H;ABJzy+D(4kD)yfPyW)n=Ms5n#*KqCANfe!rgrTf^;zvgGr6*DRIZBrl2+Z@N_dl}L&#n2Kc*0Nf=0s7hp+0mWTu)?}gy6o*bx-<96;|4fT`dCx&pO<-mLB2KIV?q@8XKjRwMRIIa>my(Wo`;!k($|LH&6^0$Q5g}mvJkyT#Sc{aczu=q>LmiOmUrLG$uLe<ni#;ea9A0u6(hpthDoK^{iO0Fhe-4eA2;tX?R$!e>^{CRdXuib?KH2?>t13iKg&14YsV>K8G>#Vib!t?{dW~xfcf#-PuNp9!4hJ4`d}m+83q(-&Axv%v~XlvfPPgF@rQwA^Gt*r5SdZ2jqvb7c-Fku?Fd-yDZZn85YkFvnDoMgbG_EODsQ{!n!_w<kz#CC<GE8#DXnA^PE-u$nG}gGCpp%V~^?U>eli}XX)b5roxM4KO?oRW<Img_TWHw<>tcR$ga%N>j)5y^L3m3M*kTQ>%?ZmYxhYIoTxW^a&@1m{72#c6WZ1Dv+42tHlZ9-wVI$jOl4`aZdQet<0A+tu%^xZl%==O`N29d9LHHwM|@|LHAW(msjf4QPOMIU0s~d#4S?r7PBB}9L#0*F5#(_+qzjo(4yB3;E+ec&!tF~XPOwNk2ocjv1EppSI&Ic;qf8{+G-7wHzA6;MyoA;bIb(i$9P+8?;5d+6HjF%SXJt4^xQi1_8E%<Z24HDiS5qU7kV%76I`R&b-bhq&6IqZR7SWYO1r5jAMNQAAQoAwFaw(Fn5-0lTE<X-_%UmMO-9U;W1lpRFEmF{g;$dF05dLs20e*Z9Z@5GH?aiVj=`3O>Lk8He5ZtkUDIU3!@R5OIUI<v2G{f{UO%7VCt>9VhqN<zC+EIC(^`cZtc@EI#Otz(wj%k;yGSqT>$yX3d7m045YXo)G9wC(Hu3AwU&Urv>o`u?sH<Vp=)}ma0N9-nvIe#q8S{}Jo$m{Xf9qM>qY?;zfT=7a0p-op&Xmwc*9CpOi$BoaHHc3Cp!{*vcMV8Sb-Crjo%)@~YI9OXBDsCVYw<kUlv#iEWU?<TkTJMeolQ3?P^5v-^_4kK2)hMP+7FGvzySDfbV$UWqcEkk?t?NaQa?G4UuoBlm-zlwRtLriaESYYo`-4%&F??3cWN@=`M0~TO5uroX6K+AonmWlD5M`m5axsi6To_O2KXs{5i+fDht8&|X1j#J&F!&jd^g|}-*Z0#DtAxl|ud7g80ajp2?rzLZ#-kwcyEX;Vr*+(!V`vaunlKhtxGPkqD9o)_=3I0dD*_)2jclGZmi)6<i%G&$&oyz)@}sYNIr|jo(q}s^VVo9Tu2V#A$#4=N(L=r}UvGeqx9(7xc&TWD9gIB{U&}PH_n-T#E%-hD4qr?)8ZF1|*))~UmnwD+F`EUF(d=;SoUn#hU#jnrcw#(Of$qDV!xPyWL{0r+<n{vL#jfPNYiCsz_kmYG*(B%pooYb2Fi!^5kx)n%b=elk#E^(L>(p8`xF(PnL`ALYy{2B)kik{+BDC@2sk|q3sdkR1x!kp<R502Qo~<}B0-~lOy3M?Dw|@8ptRnro5y4>Op!t4a0!jPiKB69B)yi^pc}YT=<3<UXSqHDS9E1vxZZmO=5CjQVCwfL8Ni$2Z>EAB~x*%z5blsBxTv|nGA?Hf~0$!Olhv6X=cQ8bJ9UQ0U+HqQ#O@#tsne*u_pC57EIE^dI=QV_wv4rCk^>aX+63dgK+!omim)p>Nko+knfa40!Ce;)YQeR7>+!u?p>h<02mfz6}n75<HVQnOCGer36Y5d%VTVNzu{nY?~yIO<em{k&go7rKOy;WBAF^L}&1+YNbCnGeWLFroB6I~}ECDM?nO{zcT1-1bu01-LJ)W{hi%N`I#_IFiX+pCGR0Mn_}N<z%Z%1)_w+1bA`+$y8g7PyeH+&a~HELC%>OqIN72<Gi$(^+f|>w36<n;gGMxVJ(hpz0(`04FTrj&Ng=g=IKJi?K7OL^ay_WzCtIXoN(_VkOxkc|pPp2y4beYU)a!c;X9+SadWzi1b7>t<;Z;ctApw!EK}eR^R_KiO6CWgwfIJmvMlhxY`)E0MBHRh+c_F7_ra_AZ@C%tVkpFn7P(@x3Thmzd2!fzGT^DN(mYG_|_90WHCXF##Hkb*&F7SJmS(k94(tQLRJ-IU?p0FI)BfV+*utgt8Jx>=!4iCBC9U(twI92d=e$18}3q~MD+E!7(@R+NE5Obs2Z(P4KcG~mzG-hs0u~F$thA!uhYmDvT9~ob+PO|J5IZ)&{3m3O=ey@4;WK8sgOyuno8tVsdkBFL@HWZx`|XNMQ5$47CXIyOkOu<n>li*py<@5uZ1NkW2RWd-IAp)B?niKf;>+`ftRd0zDioUTwPmM^C~0>=^<9a1B9|W1gJB)N0R<HRXhqcT$~~RBPW4K!i%#0fbo)OEP+7Yz{MOt?AFNs#<`Bpn!I6(adA6!YSCsocwq?!<>ef?uQ+*Q@8=ZxHqxiC<yV~aQmQDK(|oOq_70y89_eO00C_o<y1d^p1FBH%#;oc_F$#b+HcX_3772HJT6E2;#n@#(0jW`RLC^~=;+83xxv73t@Uh?&a^hIZFPc{-YjTLLzC?ZLV*u#O#pz-HR2tKah!?>fu5C4Dsjud2=eig~ebK)IocTo>*+{<OX+#>o2dZ@_IjDhT8Z*->H`g5%Bw_jzL&pQq`kUFyA7uVWr^cNx%!>&>9qcPlG*}Vvi%v;A`O!^D$Tl8dYvOW9@;6Xu82coGdr*58%#&NnoSz7fb8-o(Eiz_>7f+K?DSMVZJTh*VI0qE~^QtJGMR;kZDwx7lVg^dVY&p|ubu!9B2YY`h`wuxc7!?~0H66Bv4&2si%SF#83U7#Ufyzj&JXlm&`O5GCMrxXtCJrcp%k8L@M47sjELEb5Ja@rnkb|)D;@rg3Ba)uVRk&nHp-MVUqDUtm+vy3DRZv<4N)<k7mfFkQ664QUBhX010xlzF+!gp~!>yR_B<m<xu%IVeXs5y!$^;@MRSA|0#;F}~sZ<=>twwxK?zgW4o9CL6#}=yohzb7$1*sRxZF>?V1mBYtkO0l?!X>1lQ!5W-sP!%CGa)9VQ)JR(>YctSs4!bvPsIsua7u0q0Y{VcvMWval41{-HD=b4bM#(NE_iWx7ZWrS`6vRd!tbuhw!uANn*FI7^RD5%8zd9PezLHw3p9|>%9_iiOO>~H1mZ!JwYTO(Br3KVIcZj`$|rDR8BSDcvUv^(B$oYo7J4sgFQ|0aj$Ttob%F^lPW(j%tTV_+r+LdD@3baqJ_r<gzJnw{U5y|S6tQ&*Hfe&-d&&y#0ajz_@2E9F5OGln<($G5!>gcN>WS+J0o3Y;N#!a@L@d-W_0%AUeo`j+oVBOsTsBJy4NAOeYS4gGHKMW>Nrk=2>rN#*V)7&^OkQYubK#?$|Jg)<uC7KIwAYC0pCLKxlPWYeP2jnla5cTGoXntLF3OtXsDMW#NeRMFZqR7@qRQi7AW%)R$!GDKlq1}ob9yEqK*)8Y$4X6W{4fU(j64um&!iQYzbVw>Vjc>|wo(e}I5GICszhZ1oDqV-ia$nVwS8ZbSOs4ycdfExXJB~9?IOGwfqM-q-R^w$!I@MU?7SAfhbk4W;F9U-a3Fe$G40fUN)P4T4#SluAub^%PWY>C;qase6iMI+_gp`N&5-k#B5Y~ozyf5Ma`O!oF_Q+W;c1R=l_r{2(CTbK7{Vi@$KYAUg65{ka_TM?6#ml`RiBEPOhAe<cDNj7rmCTGLg?M`P`{d&AR(vRhON`QCd{y*GQ&+whf<di)9I%0ddTbO;(XZ9PC(tyj57yZs-InAv7$UZ+5>SJksOt3<lPj@os}QVgH?Gba$nw6taye6o91nhF6wnXLcN}aeSS5X_S=6%J`+5_uFnPYAu{2kSWHgr@SIAt5TH4^xnP;J-ooPT;0rK}<j0F=^`}d^$N(4-Lkh2KroeYKv$Jb7Gpy|dGUha_rc%HHV2l;z?mA_>u1jR}*hz$hGWD39TWEJWFD^ZPrV^=SQp9A%8Q|BYt)zn521C)wW3B6TW{fRHeVJQ_UR=rvB10DE28r?_sl+UHGwA`NT`K`IUAJ?jJ7bF@c?FKADO-aq20u<f`bafFl~ppTo`#$uafk~kq1P?}iXcC;$a`wD7V?P-x^gxKn>@Jc%Ac+7-i?zO?J9)viS2eT)faz8*?cA7>beb<Q|Uy-2P^sNc<LVf|8A<&=~3Nd39f3Eef1%DF`uWk@3<!l=Cd=80K}}T5$`@KNB*&Yv7-?bFYB4bu9?`>O`&=Q3_*ev1CTZjH|`-Ak9WRj;ig9j=~)OnjY_Qzk*Q~&Ws*8FNx*|aF&w|X&UsXlCTLVV97NHUOC&{RM&gzx6{T@mR_jx#8jV(26tBuzzYsEzlI{%d2z=Cu>MnxCg6}Eb$(Tr1&ftoQ$B8RSf^3Kivy9FH4S23gluIs90n-*DJncf0R4`P<^LX@klN;aBspT?$ng5x3O9OgX16jSgUr;rdH&cD9by+gmwrX&4q;r}cBn)P)*3~AIyUUHCr$`~K1iM{OU?;+}K~NHEt&5I6xpltmOnfRN)saA%zUhNv(2TOB3VUrK24;2~M90v3F7%Xe#;Dyz^M}-!mS9oC=^rWj2BYI~NXlL%HWmB!&0IoroX6t{*6Sm1fps@Ym>SkPNv+QZ!8H<3hvirP3Ik@yCSwdn2x$KTCCWDQ)qrxZzUnVBo<kT?e1SjUWwVx{sN=ytAI;7evtmu>NbcjkRu*bnghVaO?lXhf{Gj&&G7A#>&<a-$uNQ`f#EAt-eLCNL$k@VRkYTw7&cWtMVW_SIJ3;IKCLaPy0*H$7Y_C{&XO{q}#t*j_YYdSB;F>MNwGYSSED|P6l`#4^RFV!iQU{3s^_Z)aS1s=2f4<LAD<hUg5z`WDqbY>g_k)%AypjjyiNXM+YZIzcvK9!3737KR8ZnlF+j7(}URea>m?c{+Svn)-vX^auS;J1Uqn|>3J^+VtOTlRvpNImCKEEb3!KHk4Q^CKopAv+eWvF248(L2D6J4jNCAD319UP{5x46-0@e79?@iHrIu!&PZrf5WHq8}#w^SF^Bh*3k90;xkHX!ejJwwC2_MX2RODL>A^K*1@(8u>(=h{qp~cr2u!!ZLzJ6neH_edo&~P^!%%S~ZAdJxfDMS!hkJ)0iO!Tm9*QrnET3r^I!dhnieH6lUjSjD<60)`9PqNdI77{M{3%qQqy6qlR7)2yUPW6*f*9zNQj=q=Q${hv=ez9{2<~go*H1qlj2BH8a-enPVV;fm{nMdBtw7n}v*Ab_<rH176J<9~>-6aP%6&tcodUrB)T}$X)?zV0`$Vmx!4Taju%^id`9*@YL*}aaA+UuiUM=4f_cvBr<H{bp`T)Lgl(1YK^GWNs6IbhG&Ck%o4LDderokr0f<VaCs$1DX20e0nA9Md|80_sK3P#jD-?=KsR-5|D|Y3*bKN#J;2gSx$&(8BA@X^lE8w#gp!3)@#eaAnI;j!$r2veT(~o=y(V~7WXxcB8L#UD@TrEvEu%f5Rsk775n~iNhdh>Ps+M-;<8>Mz|012U1d_##^wDnhdoN}ekT1cjqQ0LC4ZAH;C!c*nv@7}M(Y*dvv9PvKlP6xVv;dRve_75&@H!e+?@|;-Jdnw9p`vhUnWmKzS#to31xA8$_?qM{fqSL<0Ti@K`nA1umYY7+ro^5hUyp>sFfF53H+_7GR2G4gsb;fTjB|ch3(?~ZODoVT?0i?({>J#Xt&0ByY%{CSYpN{nk8KlFUje{*L<A^yt_<?b!JUVX&RZJ3mdR(wiG444g0)c_Omd}>4R6v;$hYzd!nq@T;^OVby3X+j?#9T<@x<P)!}KA;99%2-PV~xQP(AeIs-!=0gdS}D?>Mm7dq`Lspx1S8ugh#A?}aEK(nIremP!aE0HiR-wWKPnD1ZP~Ym(zeqV%rz0J`L__+X46&TNNEaQo@i<@2CQtR~Qwa=QPU=v8=rYP0LnHN1*tC9Z5hS{TsKvF#?rjZqoYRIkEg;S(6ar!m^6ni;k}W*e>9ngz#v%~#L2eA|cAny(fY`u_g`oG8@4'
)))


def _compute_fert_reserve(actions):
    """Total fertilizer the route will PICKUP from shed, step s onwards."""
    reserve = [0] * len(actions)
    running = 0
    for s in range(len(actions) - 1, -1, -1):
        act = actions[s]
        for unit in [act.get("farmer", [])] + list(act.get("hands") or []):
            if (isinstance(unit, list) and len(unit) >= 3
                    and unit[0] == "PICKUP" and unit[1] == "FERTILIZER"):
                running += max(0, int(unit[2]))
        reserve[s] = running
    return reserve

_FERT_RESERVE = _compute_fert_reserve(_ACTIONS)

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
_PRICE_GATE_FORCE_DAY  = 28    # always sell in last two days regardless of price
_PRICE_GATE_SHED_LIMIT = 90    # bypass gate if shed is near capacity


def _price_gate_thresh(day):
    """Day-adaptive floor threshold: stricter in early game, looser late game."""
    if day < 10:  return 0.35
    if day < 20:  return 0.30
    return 0.25


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
            if cur_price < _BASE_PRICES[item] * _price_gate_thresh(day):
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
    """When shed is nearly full, sell items the route won't sell soon.

    Only sells items absent from the route's market in the next 20 steps, so
    we never front-run planned sells — depleting the shed before the route's
    window causes _safe_market to clamp route sells to 0 (net loss).
    """
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    total   = sum(max(0, int(v or 0)) for v in shed.values())
    if total < _SHED_OVERFLOW:
        return action
    step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
    # Items the route plans to sell in next 20 steps — don't front-run these
    route_sells_soon = set()
    for fs in range(step + 1, min(step + 21, len(_ACTIONS))):
        for o in (_ACTIONS[fs].get("market") or []):
            if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL":
                route_sells_soon.add(str(o[1]))
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
        if item in current_sells or qty <= 0 or item in route_sells_soon:
            continue
        market.append(["SELL", item, qty])
        current_sells.add(item)
        slots_left -= 1
    action["market"] = market
    return action


def _fertilizer_sell(obs, action):
    """Sell genuinely excess fertilizer — above what the route's PICKUP actions still need.

    Root cause of V3 regression: old route had FERTILIZE actions that consumed
    fertilizer from shed via PICKUP first; selling before those pickups starved
    the farm and collapsed crop yields by ~14k/game.  _FERT_RESERVE[step] holds
    the total PICKUP quantity still outstanding so we only sell what's truly excess.
    (New route ep=90914286 has zero PICKUP FERTILIZER, so _FERT_RESERVE is all zeros
    and all shed fertilizer beyond the route's own planned sells is sellable.)
    """
    step     = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
    reserve  = _FERT_RESERVE[step]
    private  = _get(obs, "private", {}) or {}
    shed     = _get(private, "shed", {}) or {}
    shed_qty = max(0, int(shed.get("FERTILIZER", 0) or 0))
    sellable = max(0, shed_qty - reserve)
    if sellable <= 0:
        return action
    market = list(action.get("market", []) or [])
    if any(isinstance(o, list) and len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER"
           for o in market):
        return action
    if len(market) >= 10:
        return action
    action = _copy_action(action)
    action["market"] = market + [["SELL", "FERTILIZER", sellable]]
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
_our_last_sells   = {}  # what we sold last step (to subtract from total delta)


def _detect_opponent_sells(obs, step):
    """Track market-inventory delta, subtracting our own sells to isolate opponent activity.

    Market delta = our_sells + opp_sells - NPC_recovery. By subtracting our
    known sells (from the previous turn's action), we get a net signal that
    only fires when the opponent is genuinely flooding, not in mirror play.
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
        curr      = max(0, int(_get(inventory, item, 0) or 0))
        net_delta = (curr - prev) - _our_last_sells.get(item, 0)
        if net_delta > 3:
            opp_sold.add(item)
        if net_delta > 20:
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
    global _our_last_sells
    try:
        step     = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        thresh   = _clone_threshold(obs)
        opp_sold = _detect_opponent_sells(obs, step)
        action   = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), _ACTIONS, step)
        action   = _safe_market(obs, action)
        action   = _overflow_sells(obs, action)
        action   = _premium_shift(obs, action, step, thresh=thresh)
        action   = _safe_market(obs, action)
        exposure = _opponent_exposure(obs)
        action   = _impact_slots(obs, action, opponent_exposure=exposure)
        action   = _merge_sells(action)
        action   = _price_gate_sells(obs, action)
        action   = _opp_hold_sells(obs, action, opp_sold, step)
        action   = _fertilizer_sell(obs, action)
        action   = _safe_market(obs, action)
        if step >= len(_ACTIONS) - 13:
            action = _preterminal_no_recovery(obs, action)
        if step >= len(_ACTIONS) - 3:
            action = _terminal_market(obs, action)
        final = _align_hands(action, obs)
        _our_last_sells = {
            o[1]: int(o[2]) for o in (final.get("market") or [])
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
        }
        return final
    except Exception:
        _our_last_sells = {}
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands":  [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs):
    return agent(obs)
