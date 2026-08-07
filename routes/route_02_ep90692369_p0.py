"""Kaggriculture agent — Route candidate ep=90692369 P0 score=154,377
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
    'c-rk<U2hyoa{MoR=7Z*g6zMmvG-nCN6$MK2;JhFf3-}BJ#`$6GH^cwkI%%f6r!z7#GOKz-t?q3=&U9C0Raa+5Mn?YfzZd`h+wXt->+cu;^vlKjyAK~Oo-Qx`<G26%xBve9htD7X_S^6O`PcvX{P~xQH*X(zpZ}|U`03MMe!YA5_UF6%i_42w5BrPDwfXahH@n^Y$v-~qcCSDGdH-g2_wnNL<?PQt@9rPoU0kk)ufKnMc>U?s$MF|ePf!1Mc`~23um1e${bT^c%znAp?>>C|GSYVsk00NB`E;26<ag5%e*M9zN#HQn^I`n->FxdNUq4^{<EJmynT%q*IUB}s;qiOZam;6ZfA?y4n6!Q~^G|YzgY71lo=*|p!u=At6|vp0f}bb+ZnXcY2@kgTx{!_bJKpE(PW-Yb?mq4wPw)7rzwg%Rs1DywnRC4EILYG;Ufmsxclc5#<BgLV?lgSIZvAiuc1?h-?1q^AjIYwk4MgkN4H291c)g_ghMmx0KDyP0ouF^E`E^CBjXR->vG9XBpKxTg`P)jg+T>5V+03mvSqsd;w}|=I<l!n93mC+=k?=s0shAI)Ok_VeM(Z~2nXS5w`}D*4FMBvk9M=!}IUCpA8orRap7EOw2WZnZ=11$d8b`st<{C$r>JKrQ-Cg^_^ccshhx_~8tB=3_Y4`Z??fu(-J$-pquK3~MQ~NUYAJ*%~hxf}qO&@mme-G;>L%#HbwH_NHJb_k?*LyZk95Z}*=VbP6ubY6FHo2Qr^r5i292JNo$N5T6FEcvp`t|1L+sXCN3K$Oynsj_P980a9!T@C)2=ITcPuFm7Yt+#RvqtSY?I!!jMo1ivIfx)OLgv;apewC?uW5s@<p-TNI7t?oxEm35y7$}(fYTj5eEs%vxBdZU&0pk7EWDTv$gTgFCMbmV&-KoIum3$=ZRX!@Gyd&X^>4YOyTu7O#j{e9Vuy<<s3UWrz%Ayt7b2yUtD3xJo4HQ1NHuSNj*|Aa6$*fuTRHn*<(Afnc19p42@l$;6Ho3~m}2Hl#$N078xos_5PT2VO}t-ARJiH*(oVd{5(6^m$u}6ovoi`vZ2s^z0f+8CjM6Ks^(=?*T_*;Yx~!Zl^!#M!?cc?NzVaw(eLU!CfY#fGraZ2Noalk+(&R)Fs#C*MfL9$uh|5{ePI9CPDGpKs9B0(A29#WI2c@`0nC@mVfPDDho4dz<Q61rpfRrAbe?E1cR5J_@-UG$6^UYo59opfKV^Jt=)-==K<A5162FYEJFJ&$>m`jTC1TdT#X}<oMeCzn9=_hdMXwU@8Ml?d4$r6}Zgo1gz-*nOKOyJX(SpmW*^b&OPvuCY%@&s5zj%ya%F7&|7#K4X?P&$VH<+j8y0dVE{oWfHYX6uu4rn}!+&Uof&ME3ZKxpL;U2?`xnybNIl9+ZN^Q~(lFuY#`^Nev7wQEHfB)ZoU>sd1*skit(q&@VMGo7M^kmb7`rfNniRI9wMKYd9E_6ZR0OmZP~EGXE$)X$kGG+CzKz>+8Ou`=)=yezrKhTZ+rRA{GtG`xuB#sA3;BZe*a2WHf@DbY=wQ0>!TEj2sQiuHgBm9k2E#kvXx`W+0M&hHP?4VC7-Vpdt!!E)lx;QCM++3fHKKy_NM}>{yfGS_XBn7gQp2J+5muhqX0Xxqa)v$+Z=`*uh4m;i_5Y?#Wdc<32pxA8YA>7j`}Qd&T{_zkB!kBCPkH>jT7r+q|A1`#Z>85Z%PvS>orz$H%+<PrJv*zg%42#BXF;2JdHomP^~rSxDpg>q{IY#Q?l87GG~X8Z-A$EInQs{O>rBAp<h|&eGQQs?L32D}3!RyAKziXXa2AVzS3u*8r5epm%j&+AMHjfF(fEWU$1-JaS~{lYy|!JfA_QQHqg_C!cY8vIQHdg_~_Q-LQ_shj{`u$ig%@<?_;k3MF&|3gG&duzV9sYORJ2;_N~u2FEaw(aplv1Y;J~^-9+XQj;<6Dx*)M*DD0$iNOK~p1f42<{L*8A0-{FhjxBw(Rs|!X{>~hXtH-jzE{tEXUEn=MXQ;kNmfFgA*r>}@5ZQ=a_Ds?4%>B!sm3MJrqRka5l&5ybNGT6g~%H4`PGZ~jWJ4V*)o4T@Z={U3b=U^GpEj-hB*L#v~6U!PkMlW?lcUWeyhTd%Pg&tPn*9Xc5_DtjIGNc$-;u*#;&U!P2j$W<Dw!1ES5xyVV-pXd2XQv=iX;XPl^mJXO3QEU(P(jWyps+;7<D#lCLK2&5pa<nB~;PrU1=04?JQ#Im9bR1}&^Q(oS~By#%X1@sxZvn#QaYhG|7keHNbc=%5qR6&1jl(o&KIY(bWdr7YqCxm6<s3a2PoRQtcSG!)n5LyX+Y2;>BXeXby{Qxg5G3=4*k{#~Vd%dQz5MlqK{s^&ac^2Tf|A@n?#664o(cP6~~*K5P@>F2lie+En*cuw~l5DBX(+cjsTC_E*pNHRdjV)=C8;f3x|eQRY`jy^aDW?$xm*|i$Xu9||`uODgzFe|9g62s0fmwGqOw2E<jl?z#m$-`NVQULV#8wtrY*nG$_!KcN{PR?Y!Qf;Y#JEg};bif7bvRyW^kba`Zk4g%pZ5xWm_5np>a;RLvC+V$u6iF7f;$wjwVV5vWWr}&`yvL&@EHewNCnH!6Hr$1%s>R3CRPVLfUqsK~F844t!si5^)EFd-2ww}kDcoeCvz8hm^luSI-Bm+hV)Y_;Oj@SSYuTj1(rXaJ?_X{VGh*L%Il+%!W@?d!IoBTkF|E>+)@0nC%Z8AOWj&NAZ-f4Lr3ZW%;9h4UKg+$u=}V9rS%@9V9L-@AG@aQn97PF)WheVmXC)B}8ztMna2j%XrL40*Sj4WB%(<*`1v#JBu9cOJ@UtFE6i7j!9PD*5gV>X*iVO%mNwl`U7)Jxg5%^GaVDz*~5%xCy^vn3d+prdXU)rAu3M7lcD9FYTpS~1QxgZ9eFyH_{oVu>uL-B!PnMZg?bseNCB!WI!UJ1yGFE&nofR7^qJ_5s{=3~6p%eFNg6EwsisXP0?hnswC0v-lJh{nSTkDH~*rj1g0SSU&mMffS#W{LM~{7{2^B`@e)B}YjzP7_@RdtM91vp0_te7QdlQ(-y3<8b2{u*#XRBDNbuBjILA`fkr!$%FMaFP!A(Z7KPwl}MW2$1&K1NWHxF5dIe(gH^inG?lv!n|5sj((lwp2vQd!#E{om=P?UHBVG}rkJvIVfK8l5)C+~p(_$XK=8;9J(uC0bD>D*AA1pT+Sd%Uc3*OQb(YIH`_67O$xSlQGKY@Aq#c+MZ=P8|$*54r^P1Zs<$OJpKk=*nqS(0HPS>>}%qox4~$=HuJGZlTH#d6o;)#+BBojTE~g#>i#644W?R_~kvKYW~vJkj&U+HzKW{GnVuK$J=wzzN{30_ZbluB%jDYQu#pQ32sp<zVO=nv%W41Kx*MI)(U}u;gX2ESE(aI8N6IKz;3?%jz)dkVK~k&$>>e$!NvCbf^FFsY>9F9t^K1e1;%FN!40?M1v{jGjQB(^<j|c7dnxP*f++~G8@9yON6^r(8{9BnQ=}LWGfNaEi{ui15eOIYgOk6F~XP!+;m!bT!~eDDdbp4qiIL%Eq}~J4E;^hj?jzjrRO4Udny;U$+Z(;`g+9+)eX;Ybg5!w0g@2_|8sk_^T1ObSyLYp+7gQpmcTiDQq3|&dXFVEJ=7Y~MJ!iE@YXVnN@{qkZKZNwLbQ5QnJnlv4g=Mi%SAv{M8du#LAul@PxJv}+2U9tQGvR&uB=Q1N4km*omVFG9+}QV3+X1aa&{jDoR$`>>8dP(kn_f3%Qrx&*E*!6>8ESuQ>3ws4tk~JubJ{mO*3t+n-2QqOa;Y;51=7bC#x|{1fNKnQ<>mTSYjD-j}DW`$Ta`5-rbmKWxhSa|B9vb!~4Kz7yvv=f6P`*ailV+guPotviVkxbA$~-)R6e4JQ5*MAy4*DF-aO|cij?HSb@K+lG*{pS~F4*Q=}m!LpLVoNwaRN5_?hWG|gsdUXL5{jnPlviWR9QWgVA_@MbhU<O;GuU6x+bB(+9~(Y;6%EPS(B$JYBRD*(b0D(1V_-w%@g&0Bz4Kl5r-tPhL5?cVU9>6-1el6>NSRhyX7bT;{u%TQ>Rp`rsxavw7NUC3>z?)OesLXdRy8MCNy`m6vQZ7l#30|PLv=aSr(U&;}x92O1$O2^<29I;uUXXd3m7Rmr@j}MrZdw+QlS{R@;RdD+(^ythZY0BV+(}mIKR0PrxS{Gwnz)XOmpvnAlNUn#?WaYDB6-q*Q5C(%J$vxd*`QWFq$J18p@pNtCx?3;pwJs&Ogsf3VwYGI!$KNK#HVw4qF8^X3DBZIAK85wPMt2rX^hrF$nUjoB*EQVUtB~)LMq<?f)TSK^+-V&J-@Rq}F)F$B(+~5c=W?~wBpOMzV(HXzhnb=)Et(cYFxNHS6-|v*0B~YG*LYJT2(wH!BM8zPl8V<)8RctQUK_7SVi;0+s;euq9A^{7uc|hPc2lXW)!wsTD^i_9Uy8)Sa%=ELBCOP+WLQ`-5C%Mv!5yh#0X~Zi1n8Xwm?RVz5X&pbs;r+{qkx7=<?kn<v0P?D%yHxicW}JTi4cTJtCGZtgh6Y*<V?eCO{++4YXj!m;@KB95y9~4J}XY|%3O{NjJRYbM|Bq|PIiuj5AkB?vg~BUvpp%)p|JQ2xg$0!;801yT=xW1)|9kXsbeb26Hf}Baw>cjnlq3?rl}d8FlV_FKkL>vr;|>6(f*|aHAqt9a%ewDvWFZ=;1OY!Ewm;nk+H(qJsDo2c92>dcPX1qv<oqirg=3<d0=Bp9}~*ebo2*oW5_9#I)NqSpt9RV&+5rCDAH_}kYATJK`wF!4{wjDaCyXNrGdH|seW6a3$RSCZBRFBU{*HwvC3E1eK{je<Oe&X8JlbA)`Il5^qXy~YWVi4ONw$GR=F)L8%|^4lMaE$p-(r$l{3BRcQ(sqKrJd^y`{i_wnVf!kw+A5AlfD|{?ybSS!w{?*r6)y%MNSkoQ7mP!#C$q;PB_=Q?yhbnF1AY-Bw45=g<d2c$2_LUOvx=qh1huobHC{&%_Op880dPvSl>DuP2gTrp+oJb1q=wpQx<fzCqQ0lPKlG{60pHJY9MC_tvsL(v-S}pjFW?0v6`_9VF<&4)6q8R(MaKo*&E9_!*TXSUs7o0~J`sG5|!ur<giwW9xFj1wlDTDw?jL`Bkn%ma;6dMjaTXp!A(P7wN!QXW=Bhz#54WCqmo!vSk_D$o(NAd;}?0NsQ^9!rmu!ejrj^y8dt5DP6vPj_Gp#3Bu6Jq{N-LGR`yi&W@V5Z?=2z1mQw+S}l+YXKocup!P|7yBs;UxfJEWo*~U0wEEEEqe@;|doR%jK2coUDUD4U?l{`Yi4-RA$d%$WJc6)I&#s~0GA*Cn(WD8j8A`c=jMlC-CM#Gg`CccO3inW_RA-3)&{E3EnpQ;C(Rgu&tg`Q<Cd*(f=ryleJM_7)W5*+iB>ABgjz8CrNYBt}1^IZLiK=Qoh|yWYoY_V?iLe)A_6g4?Gxdg0%E((vLFKoY8Hdd`BsIk+iHE~qrk!?fIzhj1f(TTCXDoP9TiPK<m`D@PV_|xMU2nnSde**{`?UhZC*7JlWrIDb)tAnFug}3$FV~wc$WNDhS?3bJaW1o*ylyLSjZ?sDDNWqk5V}<GnT+Hq`V~#RcU|tzZH627v=-|kI;Wsn^I-}FQBLJTz04)TK_Ed%UZGT3WT6scvtv+_Qqkq`o#Qj*xOrU%NNdZHnU@~v+a-t<ID!Y0B@UR!>gFpuO#=ie<c#Gd8D8|q7{H4!3fMnPvkYxZn-y_r3<AxfSCbLB1+Q4<A<#VojZbY-b)hSCIGmavlzMtPuI&Oe>H6YWAIa@B(H9qyI(mZNF{`pxGhd5n*H4LB-X<%DY@-6fm}P<~{?DqGP?x((*r;q^xX%&|#zZ$Mw==wO##%cHx2YtgtX`GhCauYO@Jy9T_Jh){+y+aCSg>YIL?wCnP}?|Dlw!M>LUMfGO+PdrF=^_=sTD5$u1^1;Pqfk}$S)Q{a9}!H6duUdrZs>CB)MguauR;i_hZY5GmT#0Ud>W6$UAeP?&yrPaZ0TQbs?B7aXyqLo5Kp$ffndz`mi)1Hd50koVJhPCl`q7)YzNF&{XR#MM^5u)|&+Cq@*eiiu23Tw`K(B+-X7tbk5*gCB&&oD^CKuVZ;m<MWZd8p;@?E$DuRJ<1z*kf}e0~d$a`SHRLSv4Src#v`klTi?HjFaC|(_mGe7>hh@PxLW@=%527!mNLm5^mGR>gXJIQqpdrJ}EkNM(lcvT-NBKUINRN6AuX+Wt0I!Qy6Wf$XX*l6|d$yXxy<kPD_J67+wq2Q1Vt0oXv*Z(3%P2wmD~X4Mjiz)-$AZ9%E)FU5m2N=CwanWtmfXk^gBT9<^_!F}Dno!|$lkWmp||U1V$$?#t7}#QWVi46)hi0pn(H%zT|R|{*Wz5O1Ru(cGFOzazg58;<u?t{b`UvSK?TsJnFUtmMiHS(q1knxva-rd>@K$4B8S)tfS|b0yxuaej?giZ6tAX2!2~E93$?uZfOV`Y%x<z+;+*TN?z?m*-X=DjM=gkeNa!n{UP32BOJbod;cws-ak|e=(VL_=R93pRYdZqAgDIlMDi+w%S*&9@U4PhN0&w8CZm9Q@IAj!6QMAmGswOFFu13ph$4+EKaut3=KZO>6v8Y6=iRBL>=}at0=;-BN(F&dZE`D#<TAZS{a!@W~cYr&^a&Jz(j*#gXQG5|13A^BxNA;Ey6`BA@h^4^X+VW`g?6oR%fMr$<&(0KT?wB|W!H<FjP5`57oGC#uIvo7mL_G?7J%?Z7c!fYz^6M0iv?Zi^fqKA_C2|LxA_*PWvS3bO(JUV2J<tSnlYy~}L=ssI!hf@srA1*`8THdwE6h%K5mUP34X-%7aw{FpP}VP=AA@cE%^7UvBE5B(VMrFib!@6bt0^^BnDD1=9d#_+!IcEKI6M{;TA;%YkU$kxVd%E$++qjpfROj04YZ|I2y$fXHc-u}^i8iVd!VNXQ7dlJ2$58xU`8y1mX(`zNBTGT|A{@3u3C~=OQcbK2+3qR2{QUvmQJzPc>}>WYTFw<){cU(WO)y8&?LyErWUbOZ^YV`pTMXxxvWw{t6HOYGI|7wR!~Y&nREng&|2bT6mjffk&}KLQ(8YG!lcb?h)td!pV9&jOZ22_0BxcPfXyz6jpjgOCq>jqLRLtp@}GD25ASBdnpqo9*-Mpn3S^W#Q7lEyDT;H$F!d%5DQtNeeEr(5&0F;1Ke_*73%2%1ftyu!nS>JU2r2-ui<<s-z3Y_Ak4l1YW<LN;B(|TZfZSYMn`5~pJltU>isM4CsCcQGs9Re~a5d~0Cw2S1aJn|n6aHBxSS~(ui8W{HMbo<KgboSv(*A#*EscxT!x6LOd0dHY)Q8t4RmCa3YMRBBDnoecf?R<)I?gVue}e1gr|r9LJD;lMF+{Y+xqhu#tte~r)YODJSwu?NOEk=_(bqDZCfcT&DfoI2h^m_0z-zjCYU_IqRo-AMN#&kMBd9*R^rcW?q4lDcMZVJ<sCXT368ltIM-^m=SJ#J2_yWS&+&m@vJaNuVRG3OXxs1AySy*k^-OwyJK1JdOuSTQO&O3<`BIRWS5Vq7OAt*vmoZ+mrDIk5s(IRR`E_ES?J4sc5W6y$p$OxW!Q?Hu!HhWkA#?&6E2jXWl^e0E5vhX9>&#y%DWdKbk-x<o9$%rHT5l&!ui_E4X6f1Nq_SJiQ>C7ndMujSJ{L!mW+_dva>m})eXLkIR1VL_H!sX!Jklt4=IZc*kaDdRXT-o8$n-?a9apTd!UVz+2J4$$U7L-tuIr9+GZzzAJk;BU9U=#8OG|wm?<O5vU%D*P2m@WPb8cEeF6q~jK(L@h<2yNrcH5d#f%@|6M6>=}J!vY7y;x*X5q%<<aG|-r0h#?sJPk}?vN~q+}l@Z727Gw{l%*penP;TxkccTj2ARy|hi3`P5zVW()$LRIjfA%~{E+qrzriV79m{%8%wriYFNQ~0WnIK1P3$1lgtlPix3Oueqd;Su9NDWY^@MKx1Yj0cuH73|1V(`_ai#ap@af!m2;RDI%Srz4@9bkyfg_i~9!ZA+JXu%?=6mM#eDK$q0`FaLNiCR>Q7<OLmbimB2FjFnruh8gV8;8!;+YL}CupmGH4WCA}j&vu&Ot&peHKx=S5#jr`+l#%*<M9~2$VURC@p<?bYZ>tTMHbVtUYfml%QUt;QKfdsWtHk-xSaA<x2A!l*%$;Jw(ftfT4`Hr-l*`b>RPrKDoxv3KMPGN66UjpQe9|SZByA)^p^LzQUlr?NZHGMSXdATqAFQhV?rvD##MWpb+t&VKgRN*m5G7^`0~nHsZNSAYlrOMAQ7Ba`j%C*v{vc+TxWIK%bD>3)%mX4Xl4v(jbb}Vi(lBN>n3heqDM8NIZ6r~Nrki;p-!t=U=L=h86aL=hKegK-(f~l<JINVww(GC6crwPeX;vPatq_KU9eAC$PukdjzLp_NK@D*8;-+fqBuCvilL)svr8PRs}~uvpffQBO7b&EOIna$)>(rd<APV%dId}Y5?L#=)lsBq#}ybf^iOS?UOZC}mDQ3m&75i}SNW<iYL4fdpavJdn<T+~WsyoHaLThpXy-}kv3&$7CsJDTKk@J&2Ajh=gJ_$b{?0Bd$vsL!Y^^2Kdd|oBGpH{QU{Y%Yv8zJ3m)C}&wd$+%zs9_-*)1=@d$t{ly#97IqMMlgwOxw+<x`=Wi%A=rW0uKb626!&7F>=M27p0}>*QHsO38kW7{ub)26~u~J*?5hqzw@aF3|=l<3qP%$(%f4qEhBo_SqXWKOC^QNn|G1NhM^fCHZ$!>=`62DFWakEU5uA(39_Q>gwWU8a5Nr>7Bi&6=;oues;r$Bq7$LiR^iO-=NaWoyaPS6$_76X3A7ztzd2r!BLi|PS6Q+w*J6{26LryIse+jC*&q;Ccr=|nwSwPq1%bPGP8m9DrIyRRr~Z%5vK=F9EGZL&_^!IQt$OxnK?*^W`|BbMrz@$sr9O=uo5Y+fkzb*_q({~VsqO>G(JiKV_dbEokNg<TR{R(gz6}tO;$Yxzb#Dby4>0_+;4KMkW`TC#5%O?7yIe6i+pHH%r3CS>^x+_`Ms}{$6n&KVPk}73v>><DweI8q@}|VT7n1n?a-(5E0p!7x_y_jWUG)}^<AlsrDx(p21{v-N#wTrJeJ|MvHC|wY~%7i3G&TS+lm38(wmYBap{frw&b8M$%*kshjf7~vm^$X*xWWctBuuG#?fL}fGwAQhEjcM3rK}R!`DUXt}0TxMChhL4KC7k64d<2nlSd3({-V%gczZ%A<@B5xW25lmHK`T$O@a!h60kbq8I}!BP^Hd%D{+C2_R9<t`K^Zgn8A}#8}xOd;KuhmA1Lqw@Q5qar<b2SYlHF>GmLOm5a!zT@OiXK$8SOlkxaDEpV2xY%D+*B_VzLxDQn$Q!^^HM1}IwMVNCAUO8QArk!(@a>O(xSw=`ItV5urM+ZC{`Qh7z&Nd`ZZDK-LSlB6$|KQt9*I)s_ai%$>+SbIjx2%c&%l#05Dde`0$ME#V0mu5%z;3A!nC&Cb5r?~ZK8*r^nb%8^!0HlUWvTd%oG-|e%Ajsgy{t0=S3pFDs`Cz2q)I(zqh1(sv(nQ2S|+i#ei(ZmL}jeD;W9>8keFthgyLwakgBQsBn-?rC>GR^C4{p}GT88Bu_TLJ00l%*LOxzf7A>KVa+r!8z_4gcE}DyLx2*?3cvvhPr~*n=#}PZFCg4p&<4Eu%p!}oS-yyS_m#G8TZ`3)q2Inw~?+GH+xB`?W%W02ci`HFA|2fB`@*h`nWK-K}hHn$9(?Ie7ZK8Xfja?6_xsF8CophfftWZH_)|H}4V2gQndUIF8EKf$Gam4c?jspU>A|a@~uX6HWJRdS~_DR)x+g;PrZ!*0g+ZDjJHVWU?6&14eiICl9PXHp?mM2>BE{1Et9?;Qbky2C`Xy=!bd21H2yM#$fXr1u%8s-uoz2NOMF8T3A*=h22s-pOP3isNqJa}y@AY#{cA#R%RqCY4DEsyIo*D-dck0r;rC`P4J>(FG*8HDVW24M9u79v?|t5MrvK6qBHo{_>j7wW`{=BT1oMr>cILA0{d4l#x5j)^s(4RB13Rz-*hl;Q`R<J_L*@tMDYwU(KR(p!-|V@=012YRg?)i29pjYhJ<?%yy(lYtFM(4*9rl5<K$E@V{aR@xBAIH({iK$oLKgz_J<n_@3%K1YZm-3q*EM-AygW{og3wcVFiZ`;ApXc7SosuqoAb~3;O<-#Ko`{Nq=Y|f3X1!Yi8)XM_gjeXSfaqDs#E-igp*-DBC5mms@l=t->1!brrUp-17PgU<-;uGgo_vG$;O!7Y{N(9s6_>|E5dwuOSz@sn>W#(Y9u>cS=cuItZ>Le>bZ{oixd)ky&f8|)(I~{I89U@$lGL~UCZKAyv(}^{QoCs1_z)=Dn+FD}tZGRePK`NmUf#VyNX5FmTyRXD1nHC=5hRj(Ol^hkjs7fvD!?&F(g`5afGv>uNBMxehL?M^c$uMDc8cHButGD50@;o6|n7*@mU?m*4Ex+|xw|JW}ByKaWtCRRrL8?mRAagP~ciR=e7KBtFiA38FM!8*Z3zCPl%aqa=F}3t_Vsu=_;itvCVT*|}ufEi}H_IjKjF4tvA0m-a8{7AOeRLW;{Xgc%0k8'
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
