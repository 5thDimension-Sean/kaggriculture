"""MapleLeaf 6.5 -- Filip Strzalka route swap for Kaggriculture.

6.4 (Nikita Lugovoy 8C/4S route + widened premium market-lead) was
submitted and started climbing the real ladder (2645 shortly after
submission). A forensic pass on 6.4's first real losses -- all three of
them, HealthStone/cf696666/Efnutrrionpy, essentially the entire loss
population at that point -- found real signal:

  - vs HealthStone: WOOL revenue alone was a $9,669 deficit (us $18,216 vs
    their $27,885) against a final margin of only -$3,092 -- i.e. without
    the WOOL gap this game was a clear win. HealthStone ran 16 animals to
    our 12 on the SAME hand count (10=10): more output per hand, not more
    hands.
  - vs cf696666/Efnutrrionpy (same opponent script both times, identical
    sell quantities in both games): we actually out-SOLD them in revenue
    (133,801 vs 116,493; 155,367 vs 137,242) yet still lost on final
    money -- the deficit is in spending/timing, not production, and
    wasn't cleanly reconstructable from observed prices (large multi-unit
    sells shift price mid-batch, so a step-start price times full
    quantity over/under-estimates real revenue). Recorded as a real but
    imprecisely-quantified signal, not chased further.

Given 6.4's own docstring already proved "add more animals" is a net
loss once bolted onto an existing route (Fibonacci-scaled daily re-hire
cost), the HealthStone gap pointed at needing a *different route*, not a
patch on top of this one -- so this session surveyed the current
leaderboard directly for a stronger backbone, checking self-consistency
(majority-vote reconstruction only works on players who play the same way
every game) before trusting anyone:

  - カワシギ (#1, 3198): 62.7%/38.6% self-consistency -- too adaptive to
    reconstruct, ruled out immediately.
  - researchstudio.site (#2, 3161): 48.0%/48.0% -- same, ruled out.
  - Filip Strzalka (#3, 3154): 98.7%/99.3% across 10 real games (6 P0, 4
    P1) -- higher than Kaito's or Syed's own consistency in earlier
    versions. Majority-vote reconstructed and independently benchmarked
    with this project's own benchmark.py before adopting anything:
      - vs the actual shipped 6.4: 18/20 wins, +1,692/game.
      - vs main_inspo (5.9): 10/10, +29,448/game (6.4 itself: +29,788,
        i.e. statistically tied, not worse).
      - vs models/5_6.py: 10/10, +33,774/game (6.4: +34,428, tied).
      - vs models/4_5.py: 10/10, +17,084/game (6.4: +17,542, tied).
    Net effect: a real, validated win against the thing that actually
    matters (the previous shipped version), with no regression anywhere
    else tested.

Tried and rejected before finalizing: pooling Filip's games together with
9 freshly-mined real Nikita Lugovoy games (99.7%/99.7% self-consistency,
also excellent) into a combined majority-vote route, on the theory that
combining two strong, high-consistency players might beat either alone.
It did not -- the pooled route lost to pure Filip 0/20 (-877/game),
though it still beat 6.4 (9/10, +904/game). This matches the same lesson
from 6.3's own history (pooling in Erfan Eshratifar regressed the
Kaito+Syed pool): pooling a real but *weaker* source dilutes a stronger
one rather than improving it. Nikita's route, while excellent by
self-consistency, loses to Filip's in their own head-to-head real game on
the ladder -- the pooled vote pulls back toward the weaker source.

Also checked (not adopted, needs real route-design work rather than
mining): カワシギ and researchstudio.site's *actual play*, since their low
self-consistency ruled out reconstructing their scripts but not learning
from their strategy. Both currently sell roughly 2.5x our WHEAT volume
(~1,200-1,265 vs Filip's ~479) while running with far fewer hands than we
do (8 and 4 respectively, vs our ~10-14) -- i.e. meaningfully more output
per hand rather than more hands (which would cost more anyway, given
Fibonacci-scaled daily re-hire pricing). This is a real, well-evidenced
lead for a future version, but building a competing hand-labor schedule
from scratch is a different, larger undertaking than adopting an
existing high-consistency player's route, and was not attempted here.

Everything else (weed repair, the repay/front-run state machine, the
widened 9-item `_FR_ITEMS` from 6.4) is unchanged; only `_ACTIONS` (now
Filip Strzalka's route, used for both seats -- his P0 and P1 routes
differ by only a handful of steps, matching the same near-symmetry seen
in every majority-vote route this project has built) was swapped.
"""
import base64
import copy
import json
import zlib


_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-qxnU2j|05&SQD=7ag6uf8cZ(+E{8LzYXV24MtfiULLYkoK+Uf3GZ&m%MjpXJ_{uTIo|1nc_Y7eC*ksot^#spR>RH{M)a;{C4(-&u1TQK7Ksg&d&b+^FROkucu!;{rKz8zy0Hve?R^F`Ruz-KYjV|aR2Vp+sCun+2)7!&C`G9tL^Ob*$=l5>$Bj8uYZ2?{`SY4yQjZ?d%t=5Tl4FWKdjdu&StCqKYU!T-#z{M$MxO)`?J~k<k!0)oF5*u{qJn_KDTfG^y$OV<Ayi;e70GCe0(0)@Wb1i-AIQ&8-_EUh>z>LyTjwJ@nDyDunTvL`w1P5^8Nk8;}6e+I{dU-CHtr2aZaAIdrkGbzx#B1_wLKn|2}?to>>2jC!f?ue|PhCeVF7qd&d5=U>%?S>HXs{?c-++EBgJ{HDC{T`M_v@+&r!yyzhJYfqdWYlW;EfBYs)6(f95?#Aaf0MA6qBhF(}sJMzQVfuoXHL^Jf^`^c1pOJ@iC@&40ps=-VYmd<Xm!@&1nTUoiI(V6$}vvPxt8=ll@<&-HYtei9>;R@Q}4sQ)6;$`5u4Y41}VW&-hm7C2Yn>d-)!am5oe&asa4{v>wUVbu8I}a_Um%V=a>&C7CbUVBaQ<&LP|4HF2onl~~>0*C!e|NWj`}pPi^~2-s-R)nV7uMdlDUYbKx4<yS7wo-&)Ihx*-7q`JVejo+&jqR&%J^?8bCo}?U7qr726l=+;c?<FJUUwU;}C5c5}Jtea;qEkvMuWVw_bSczUDj^2oCO5Y%XjpV*^F}Mb1z!wu$IQFlT{b*p0u%gdgtuoGpe!QwHMO_3BWDSqKg7-m9t20+>QP36*h70}$!NgabT^?+Rl&Ol)Ot{HQ^GAFy1`jE4hcv2Ve?4O3IT0Bg^6-oM2{rybjtJ8TT`%_qP9`1o+M`ELF2@Y7dR@bxaJRII`SZuw4&Mku|eb}>$V=ypNQYA!m$KKtK|t+(Vp&_3FuIp1KuErm!k0I*h`#_wHn`-G!D*g`x-&G8RFCBp9naTvX=n=Y#81q^zdoguJz2)YG9U&HnQCn%08=}28<zv}QE_CxHUSZ87|tP`|8Wgre;GJ(vBe&_@qtf7Lsi@`xV{c`77MJZ4tM^H^;R`08tBS$VS=?lv@7>TQ=4pur0l%7(FMI!T?m^qfAH8!F4g_EH2>xR2|`14vln<!$o6YZsLx`g5&rB(TM@HHEG8i1jjhNQUx?yMs}CBKiA(xcbo@h0Zt@Mk!xwb|}<{c7>=+{PeyxbIS{Ci~7{;qpsKg0oK3;f0coet`0A4dF`WF(>jn9Q0sCcvKw-Q1wt@>W?fk-bx`}N4`TLj}NTu>B1%7CFzIGI>A^kr=!LKvrb32RD|zUnnt^W)M<=EIf-@?PoVVy4wv3=o4ou`+vC%(>j7Ojk$<N=dhYshv&F{~SQuFZ1ob4O^tr(b2ml+S{3XPpI4p(yqKnK`tu9Rmw;+Ltd{Y==nTH`1*Bd<Mn_S-Yl{$90vmi_&UoQh44Bu@49wwY&4@V!9)#sPn^3|BQZyBnTU@}Bgj6=*yUf234C8q*F`i0bkh$*>ynI;@%RKJ(=lJGn1*WeWnzv$h={Rd}(i7$0HEcf?!yTT4&q=(9mr%UIZG0XNHEGU2;ZNs{S7}hOvr&o6-c~m!i&#+_kZzj>g;cE>{HM!jrjA%cc0L2}Nea0>~W!V#Evyif_cq1=c|LK|#tGZGJUkmqkT@(?8=dWFY;BuBol6c3_jB-V=nQKf2S?aIclIF1~sWJmWK}nK7ofJ+%&y8ZXM)rj0AkCOZkeZ#P?v^r>1cCzRU953W;!1WKO>I7%lNqK0KpG*uqLaI6dP5+4qA@}gJJ0-2Feh{qCD(-|hCmWa-X1LkPn%NWiO-ODqF>;4CBQZ{{teuk#e)JUJzz6h@69^2jl2;TC={Fz=Hsi|fH=-9V;LIb@=>uSY~sn`^@pi-Aq>>YWq{){lgLQL%bz|L<xl#}wmk-52*VzEcl$>?lvZDd)F!)AJZmXcs@wuiPg8y{C936RO+7YI$dCqGF9RO;vKHUuP}@|d^uVG+pEIaH&j0p98zEAmF@hVBEvi<DI{(LZcbG8&8(nNW6j4S2Nhb18ii&WwVVxL#C!8l%TMsB)pC(QAOPWov2EzvFTtEwb#o?*mt<jvEw|C*xJ!yo(kCJ!ztuqB#3RM$$pl<Zol|142QInmk>>uD@1E=xuykXW&lo@XmhQ3=r2Ifd}S1o%WbX_7tSt)$5$C=_5MjoeF-R3gyJT%}i4RGIJDtISr<a>%EZ=!+gVr>pWaHK_;-p3c)im-`&6u?$m_z)~5)k~;^#2i*=rL!K+E_X)XL<HTk9{K!DYucfOlFEXfY>gs!>lfHn;9h;TG?Co!k@sB7AdtK`b&X3tvYb6fkG3n`vsM$__o17t8ggbgFSi9B4~?<J*^pQfkRGoU!1b>~wNqeyb{*Sq+ZDrxjP^mPX3;N=%|QL}qeVoYx(sc69`F$0ht1GQNFdk;e#novcYgvmAd3QkBL?<eODY37eMkZ=3hLrR58QLK;9(%?PEJyG1fcTvS7NPk0nkL`Cm60Yg(B8XIsR%Ev6QQ2Qbjq3-5eRS7G|;H$LT(~Qhgj9oDTKMnpfK4{TK)6YRq#xwP&upsQ2nf=meAZ<`*R%(^%X2vJ<?&aI)@tAYikOAX~sb)WqbT=mlv{2nI{pDoxd10O>Mb07!ywglI_oSbx0PtJ0WpS_cQp8(+mbA{HE}2153IS++-f<y!DegIeIyTQuxQJXu>0md(<`u&HJ>-2Z6z@bHa#_<A6>DhG0Ca|u2HR0}7f@+z=fR?`8}E44EMs;|(?(uJGML`5TZ=7FbXTWgC$$v26pak|Jbok1k2(X84x7~oV8cR2Mc>$pN;=ZL%jrcT=aijYQ~{u+Y1kX0y;NO*o~Yw{<~uW8<l2+_x+G==NH!s;0Qp9LSM!6<rPK{eUm*6!5g0ZEoI9sY6H`yj5TuQc7~7yed0Cnw;d=Z0p$O>RR|_c1$FrR|DM5Z{B;xdCT%Vgaccvp|Dlo53cuw#ITc;fn-#los<Rh1%4e$F3J^30*r(ebPeC3tjkN-wZ|og!9pm2_^tqZzu`N!Jz0Hj?I=G7eqUK{DOUFlj5Fdl6>$e+)BiWW{V8aM#s7b%rA{0?!O@Gl%#-8%0?@651DoP;Y7?^WnZ2G4fCtp1USq(SXm{2Re}bI23^I78nG=j6oziKj-&=#g^rPbcwtEH775j0suLvayTLdJq11BsexXoz#pmD>f(cj?9a8WmF^A3MIl{)GI-_tC6q4C)wOx8!@}#VV^{VuOFp?*TEfw|1(WjF%1P+rC<w*{6qAb)R_H7tOU=Iz&xig5j9mtU@zpJrgPAi?)oL0>|F-dXglsYKDR+j24*=%Ze1jO1aJPAtLme2=APt~|pNs(TL?~;^-+vKrGC(&favOgFbQ<GL@!7}Zu!bexoD(M?ubYsWp{N8Uc5e2qNhvLWoqwtarJf(n#N!K95g#_-z=yLej@#Vg7|7EU+pI5r#2bAptWNHe4QdVY5YaO{%(_>;5N76(LXLrhpBWCo{GG|jIc(jxS;?+w89M-WN{zy!6z#T8u0)Zu_VR6RSla&;4gagT&gu|8KV-tyDJ4JwvtW|x|j6BAFpIOrv{Ui#5lvGSWQ%aQLj2o2#31^d9fXpGb8xl3A@WWbAkU?oMO&bv(3J`q2j59n%?V>BnF%i}l&7W6&>39f%RDlidI1B}>ADjG)8RTg}cp@0v=ZH>zd`aj59qO6ZAS`6v6oKiH)PF*Je#SLn)-QJ;>^?HWF8~GA>pF&S8?R>N3|I_JYkFhZDXvPnF1BL^ml>Nv;*~O$@%ma}+|($#)L3Xbq&q{m`dx>ur^$h~R0b#Voj{RP%fsgcVbq^apY@a#N^#vt@3c~?4mri47D$XNL7s!k8Hu%)*;LtQ8<%?CxxEBY^<iawsotfFew_#6c#UAjVp2<+Q<AVjN4A-RTG5dSijPV5JcHni6|yw{;wGi4-Z=Qe1c5U5RQolAGc7%{P<+iHo??m+0AkgRfD~qZO4H;w<r-;)aE{NLZr+yLraEc}6xZU@ROKnFhq6U2eU-d(wa5`cIjR+E(0~fFXZ$yv(|pP!3))PC7it4Z`y0lBeKudK?Wt3GEw8B1!^@qk7MZ+Vmm+CDZ`aiF!~a^~ss_bhh4vJJjrDpla!%1}wRW(B)QERMJOIMG>-J9Hk!HT$DV(`?^@d?$S|RzbsgrU{U;`PynVPmv_`mE3u<Q{{5B5ti*sUHj)<|7{#WRzjN)HPkLGpHjGVJJt3#T=7X9at-0JGpt^Yf#4tnE{P#sIukCUK$DE7DCnLO}-_g%sHQOb8`BWRP=vyxAMBzjQE$1#TO8zNEVaQzk<_VvG%ogLMIYV-#GwnZtx(rrA;$h|#VL(M|_lRVHN4+OiP{FGK{j1jk4p>Z&wNheukSSxRLkC7sVZYM!b~vFzD`pjZzzlUF5bvRcU~7E}cir(#?VSXbe4TF<$_<z#It#@tOxVVX%bgq*6`LuslIztSw46R$RkUFF-qtDI3PWGr>Rz`Aj(ZCU44(U;|NX%%l!x;{%~Vhyg3xc@Vq1E7}_tbOH3*!9HXSCmgTI3zs|2hlH`1z~Qg_C)2#u|h&m1Bz5P<wQ;xB{U+k5^`S#?_dI0B<V#Hi@Dqq!zPhJi`v6RXfIc72G5wKkxEUf)myNO=|qXi*b;6xi`;6h2@syE!N=x3QeuwwTnN}G@^Yx|rmh?fe{*$~>u`NkjHsm(PfE`*rhHZyoD^aic8J7l4fAG%KdPYm#ekFwxJg2=GIR-Vw0vARFUEzyGhMub4s)hxuR(5E$eE`D%T%(lj|L5lCztNOgu>47ug>#brKDEjej%f7v=mjIKAA-!;Ym1rLS+37l%82kn9YAu9i%25<V>5LT0->Lfp_vu>~htjE#_SvbBO_z95)vcwJ;KazSMaYL_W~}W95-5J*=fXp0#t<$}>@-3&#p#?A^-g4&_vtC_6i%OuMesAP1osD7m8pbKZGn8FV>NS}0kxu;=3}XlO3##&Z+Z3S2;d6PpztNK-zuuxX^mI;1QNBn=^m?3s7GHRCE%rlr)BndZsYwP04YZ35t2JcZy|(G%K~SR=9$U<h`#&AbmgtU=}*_gR9rM-g_x#ZNQ%j-U>l2nPj+JCHQSr^9Om+5j}$HZF2mY*fBYHSCl;_$hjW+xJDm0cNT(N@7DL8^;$AfyI2t8?mdQ93JS^F-qyRC@yugwT$UD#*mh+9#c_PV%Z~ULKZU@vWisQ>uSF-VLaKXYlQwVB0*1dr=`4B=9CvpAd^%8H;4$C&zB_|3d(GQKqApXwi<<jN>;)X+tiZ9l5DV`2}0m-spu_VPo!)&y&9Nmn$RxAFWm(fwY%H+PLvlj$>o&Ff*Us@?}0?4(M<Pac^62TGGYIUI@F~CRmF^mtR*#OG3yS-h29h|W`g(LHdV~QCKbG@I*fWqw2=jxKa8=&Jk?QRVkLxS;F00dfeQq_7uAM&wtTB?;siLj@>(E~u(?ZMX|CSfECYuIQ<PwgMAR>)j&u~=!2mhRC2HdeLj1Hu(`5f#XGSG6o<P@TGJgfsA2?-<nP}sO@w6%chYi?{a;R4GNyhF$0;59Q56N*}74eMX1!O~CZY%AeN7v-lYm(AC(GFf&Mwm5xHavie^etrBw$P6@op|4p=8tSh%cJU`2n42%8BVTQ*=Mk|I0d|jEHWH|?p@l;Xq9~tYM4{`%_YiI0d7nfXOS##4|+l|ZVIx7Wxst@xbzZ$i0BQR+PJImDGnopDtzxE%zagK&{o?LBPKj>c(cc8t%7dhJVR{bOlVp)(bx-yF{U??^zkO7aC23tUIHB(#zaWzA!j%vc_DGu43}x2G3FxM4Gp3TQt=2?!&doGJjpsnmy1|Mh!9}ZEbvE3N72e;LRdgjp!8C|nR<7zd9DL5`t1SIQ&&KgwR9=d-L@9(kpCs&ht1dP<?8cAhOi;^lA>h`QtPD}M*!-B+g7~Idd8z2eEs_RWU0PQy(<&i6VJXnSgFi_877~!@6-<HDdb+AauvuURr8)shgamKH)&#~G|aB`15vdw(*z3c5vEU?D^-=!=(-jbn)!XVN*dksy5oAl0ZSlp5rJL@K?;>o5V)TJWj&HQX|(Df>fq{4g!g)<(pTdNc~ZzPHe0O~u7)wwc>45wrLU_M=%J9-NKT@Rs*^Dfk0?M3)NyRI9C_YJ!;b51sv)Tzy50muE6Q@)?sn4ji`uYh6*#n>iBuZ#MKOhvu<o_7gDkt=12GY)Cat2OSGfd%Ehe^0>&Tapv|eOj7k2{J3jFEhfVI+$Fu5s(i17~4y%t)55fEr<PF9fLE3%n@kLyiN;f|+^Kp<RrVc^3ow)^gQB2>1lbhur@qY4byw>?9}B0tcnSO9jpLK%tzv%)cD`hjluf<|3?I&qENu3w;{*e+gdD=oZ6ypcCXso^3G!~o`V0Me8?C{#-q8dWY<7r#H9d=4m`7lkTnxocU8FwbF$`@$BF^Fj4U=(5T$uDn9K#Kw1sVR~FmVmML&CT9@&%hsGA$KEGO(89E45U8>%T#^;UYq`F=e=ns$!PXBPqcnd;^H-V_FG!WDJycK%jVi;7N$S*6NNN~Tdp1@!?Sw{-&)I{dRRpCG{iRhb2K?$kq&1TUb^!5;cFQ_nB$|MWVmw-(IhJdmm>5MQD&MqLxFNk8400w(PiJhBS%HOj>a>0lRtgWKt;CR>85ZFUthxYug@7c$`1Ydgr4!b-RhAG?u&D{@u#VwA<FwqcNW|G~5&c@*E|Skg6&<tXaNhe&N5bh;9&*ad1cM}FtjSf{iXs;fevJ7y<Dp^CDz)RdF3C=!HLmnz*B|7P*c?Eh6~m*kjO;X%QiZu}Rm_;($Byr9YlSxXyk2lk5-k!D9R|84(~OQ%HN|?jT9%fj9qAciUKpBTeqJ4)hTRo<zD>Ls*I%*kAJ%S-me#MfBbqVRE&~x3h$JnV;kr4R&{ZeqRIRNkV=&esxEQ(@tHa*jZ}vtRiKU;eFUdk};N>J&73T#GpMy`ms9Sy5IKYvQDq#30V=h+>_SYMpPz^vbJd)W3s>?w=bfY!~d^2cHxxOp@z%y;)+cixQ6gp#WzN|D4&nb6k5`|R!i)wvDq~g!u!D~qimL&j+$C5`h>_v_mp6zHn%nNrZKGU<=Tevm|1n`t{Cr75lMS+Y|0U8tw6Y8YpiQ=sk*%RyXfA{J3?%kIskLB^xL#!XjOL@o(plWp4kN~gv>5t#8M?OtT8OR0+V5Iv=FICd*o`6gVx%ptiG{7v$tSijn=td1wzVpaU;ANobUpWxdrGqd*!-FU|67&`u0ZD)mDUXJ5Vw9o)FvxzFk9`%x%T7pf&fnNDP>}G0%P%yiQZ0PkLMzz}X?GR8DJQ1!t{N6oETxPnOkH&ig1rAmbCrqYG0{GbYn3@hwo&B{L3^b=TIKadOO4Zt=IE6c9FQV>Fp@HysFTecf!$WbX8GpZwT(R`cS<`uIcC(dfAw7o9VpVAIKUD!)O|3fSO-M3OGJRBB2Y2!z)fNebRxD<hS0B4jr2~Zy4J1F@DJ^h&~uPA$_u*%3)S@5UWqdF#~oiLz9WGkwWEYY=S<EmXnsJdf~p4w&5$l%taQR?PzI7K<-Ed>L}$NbbI%g6nC+6_x$C)sDE-iaULzGfNZK5Olx773AiZvK(;{spy%LM9BkP@I?Asz&SxGk+t9K(n0mEUQO;Ds1mB6BD$DicjB-#qTrigN~7$oM70=o|Qy+Fb$N;AXglWbyfd?dF#1LZThIW!xONwJWY+a&Z1ojtO@M1d9*p)%c>%GOfURM|KR4OKd*%&uNDm~HN1QYmWM^H@$4=$=;tUHEMmYJ1n1@qE(uD9o`UztIBctUeO*c!D-6UW%J?ulbbxUb?TSJ?A1eSyRInG->)RMniA(F_TP8wCOqDR?_JZ0a09C)u&`E*hKUfaa)($idYj&33Gf+%~K_E+b1ociOR}w0zWBVW4EiAYL>`}eY$lz{raMSBH1!FcELb8orK&Q!g>|?M53C*X03I*OvLS8aIAB(X+eqzf5i<m1avdZ=t5KCRK-x7g3B3+Iyo7+2FpJZ2`7v&&!p9o_CUysIy+A8O&S1O)UP6CIIO-}I7YfO@&?ppRH})oUFF82K=5E%f!squ{0RHC)BqGsTMAHSXueb?L<5zgDew;ug#?dkADwo$!Ila3nNq%Pv`Y1E%u3fUP{ku4l0kDvD@|;-vD=X<=SDb(e_)jwC`)0Uf?+eiV_K|UMf{1A1M1;r5|Vux@Q>3^<-{2kfoO{xfngB6W;;~1i{a@-np+Sy(k{5Iyr-$5lMk9Liw&M=J)~0TQtaoHp^1pPG6eQ=oa<!q4Rov}`9i9g(y#hPYwMKKJ?Rg=VRtsl%%G4>)ZR(CAes*pUBI$RuY3A3sW9HtiTkgdf6Zfek+HMf>SSgvrRy39Hq5LLrQFpCN={5UW<;lqMAEG|Rdh6g-^Ii@pfOfLC9;c!UQV7|Oss||V>wLDQY=e7&+xkFli{9MlMkIZUg#&gnM1i!UDJA^yjZ1!`A}+DBL+QizeXT=HkV4TnFwDw)MoIeaU8Mp1!Id63mZW-AT38kdxA|&2v*xxBJ5E7x5m6fCw(dmRcuA<QrR-fl0@vPwHsWZ63le^Lg13|&aBa}sttCc_9tps9Q%VH(=83~I-@x*YH<)o0ALPzMZ7Vz^`=)NDrLa5ZkrY1E^;iM3g=}E_;u_MePX5F#&VREhxjU_oMpsoX+j#34Vp#H4P}MugOhUp0i#A7o$JD$fH%X6RNy<v-fOatmj|xTFB9b<hz6uq5Ku^qd0)*1RtcVrNS?6wL$7X3K5swZTyOOJOd(@)?kKc(h^#d&d@-Re%Bl*@QI~2b%zRmxz}6ykCfYSTp<$P;W1&4<)?)6Nl5L=Ux)A&+a(qJML!kh~eqly>X)d9WL63I7ds6`UpMcXrxbkwdEG_zFAyGmQf4R+6Z6xaEI8T?xqmuW2d@zK2o1#@w$v+c2qO{3k;+s=Zfl16(-RVuqF6wNO4F&mt=`2a>rcdmYa(gb>pg<pt5%!76<jT;w4b@<J7*B@TdCI0EHIq)8JD&+7HlHH!0yrUht5w#=j48fmG8jO_7!_A3q9=JbQd}ZIdAZiHDW$lPMjWYc`=$>q#KMN8y6R;0R_$<2H}#NZND!gCN$qyJj?-r{7bMvwiG6Q4?$x%l8i_X11Cw-JkgPhbIEl!eWw(+3GRy7j>6u6iMJkX8MJd-0N#eiLa_~r0vk|l+UKUR|hY4niP!&Yy=(sG#>FDD7(Kn&BX1N|>i{aBMsd%+5DxejIwNhUhothI#s%(TsQ~<0ZM#bSTO`{{gR7(R4`_k~1fYcnK^IWP=q3dEVs)-s=WMaGxk*hgjwmNtJ@Q8DxFjNz)Aujz0UWQAZ8vliLe5#<nQHL8x9yryrE@5>NRm6!bmjda~$UY(x(VmwSLMx<33HljSSTG7^Rj)-EU$_-`ff!TlAJ@p##;HNGe%cSrI_ZyE7%8YR0emTG%z_FH7lKI!bu8}5j3q1HQqif|YuwEIEa+>AuO?v=F#OAIRW_2IV!(`XKezOe6}=8bt*Rl7;gX^&L9{x$jRa*&k#kc@MA7=_1`>=a@e<Is17(kRoWRLZ)wj7<#>$0?ds1w@jN6A7@t9V;g2`5H^oBIbdPsblU|UAgE;P~*@t%O!`V3V8ZYZhX;LJ6Z7DQsqT%K0#3{E><gY(m}53ys5Ge<HqS%o%x>{O~<m8roAO6%IHjMNfIT2MzR32LF7(hEA?B#kWusAy>JmfEPA?=)Wk&wT3q+r-{R5ef#FfGw6^=lMFv{VHEf=_=C{C2%*wlO0vsg6617C#-7~m$s`B!2T?W4~iXZSE7`Xqa7ZLN0o*fEC%0%xr=$Gyd|uABM6IaDIaNa!CK$x-kuA3cy=(PY{F_#kVO!rm;KpPMnhm`X*8yqY1_brSY7l9^}8t2w(%jVt_Drc23^(M7=G^laT6~&h~ltcu0(k~d^Q%(B*Jt`$1Ju~-w2`)SwYdM$rHG4;fSLKaJX46bCjq@mr*`R3R#B9Q+=uvrdiqpthyQbvi?8ja*l!iMC4LSRYSSCNws4`$D|Z1<{5`5S0&lG0tTa}5{XQpB0Cg}V;VdbHEDS0IW08D<u%-R=U^1Md*@oFg=;l6juK9EyOAC&Gj3e~R#jl%o^KNc|CIj0OZ&yFZZT))=efP5CW-}d{k#xB3{IzIBT?fElsbu6!({h)OsuOoU}J1_nj3}9UP&L2<}4=#MFTk%znxDi9&03>yTV5Kn@eGclOL4!9Y|Afd>k$k+pF+saa6&j#a`fi**PH{Mvu83&!HFLoHRFUJ(4(@Z;QYwyPfO+U3sZYGaTlr1yVy~ex;#F1zpTpRJ}Jv(IrKR3v_TY;>60*jWY4>!7B0z=sfX-5Bg4zslLjg;4Lm?IY6~R=5&ZxsqS`>ZyWO4X`;5uj^zh{ayi+qt`k=jaYr$WofuROS3r-@d&eSAJT<hKR1zP9_<ATJn5^8SwRLH7=9tD?T-q8VGAVQhZu<xhjAoAh4gKTPhC}<E^$K90(%}~XE>MqwvXO1ZE|Y?>>}qjvs;X{?V@;ybyuvOWFi7wc6+H0i>EH2d(@5<sl=&qCIRyLWp8#EFN@1qSw}sHQd-pIJ1d<#j5!F9RRE1ICG7|<C`bLr_pcQ$guc5{Ee|tY8$p')).decode('utf-8'))
__version__ = "mapleleaf-6.5-filip-strzalka-route"

_FR_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL', 'WHEAT', 'FERTILIZER', 'EGG', 'CARROT', 'TOMATO')
_FR_STATE = {
    0: {"last_step": -1, "due_step": -1, "due": {}},
    1: {"last_step": -1, "due_step": -1, "due": {}},
}
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8

# Tunable knobs for main.py's own overlays (weed repair + front-run demand
# forecast). Defaults reproduce exact 6.5 behavior; configure_base() lets
# evolve.py's CMA-ES search patch these without editing this file. See
# tuning_spec.py for the search bounds these are drawn from.
_BASE_PARAMS = {
    "weed_replay_steps": _WEED_REPLAY_STEPS,
    "town_demand_pulse_period": 24,
    "town_demand_check_interval": 4,
    "town_demand_single_shop_bonus": 2,
    "town_demand_multi_shop_bonus": 1,
}


def configure_base(params):
    global _WEED_REPLAY_STEPS, _BASE_PARAMS
    _BASE_PARAMS = dict(_BASE_PARAMS)
    _BASE_PARAMS.update(params or {})
    _WEED_REPLAY_STEPS = int(_BASE_PARAMS["weed_replay_steps"])


_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _align_hands(action, obs):
    action = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands = list(action.get("hands") or [])
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


def _trace_actor_action(step, actor):
    trace = _ACTIONS[min(max(int(step), 0), len(_ACTIONS) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, step):
    action = _align_hands(action, obs)
    seat = _seat(obs)
    game = _WEED_STATE[seat]
    if step == 0 or step < int(game.get("last_step", -1)):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game.setdefault("active", {})

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - int(transaction["start"])
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(step - 1, actor)
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
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[index] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    return _align_hands(action, obs)


def _fr_state(obs, step):
    seat = _seat(obs)
    state = _FR_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due_step": -1, "due": {}}
        _FR_STATE[seat] = state
    state["last_step"] = step
    if 0 <= int(state.get("due_step", -1)) < step:
        state["due_step"], state["due"] = -1, {}
    return state


def _town_demand_now(obs, item, step):
    pulse_period = int(_BASE_PARAMS["town_demand_pulse_period"])
    check_interval = int(_BASE_PARAMS["town_demand_check_interval"])
    demand = 1 if item != "FERTILIZER" and step % pulse_period == 0 else 0
    if step % check_interval != 0:
        return demand
    town = _get(obs, "town", {}) or {}
    single_bonus = _BASE_PARAMS["town_demand_single_shop_bonus"]
    multi_bonus = _BASE_PARAMS["town_demand_multi_shop_bonus"]
    for shop in list(_get(town, "unlocked_shops", []) or []):
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += single_bonus if len(products) == 1 else multi_bonus
    return demand


def _future_quantity(step, item):
    future = step + 1
    if not 0 <= future < len(_ACTIONS):
        return 0
    return sum(
        max(0, int(order[2]))
        for order in (_ACTIONS[future].get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _pickup_reserve(action, item):
    reserve = 0
    for order in [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and order[0] == "PICKUP" and order[1] == item:
            try:
                reserve += max(0, int(order[2])) if len(order) >= 3 else 1
            except (TypeError, ValueError):
                reserve += 1
    return reserve


def _existing_sell(action, item):
    return sum(
        max(0, int(order[2]))
        for order in (action.get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _repay(action, state, step):
    if int(state.get("due_step", -1)) != step:
        return action
    due = {str(item): max(0, int(quantity)) for item, quantity in dict(state.get("due", {})).items()}
    action = _copy_action(action)
    market = []
    for raw in action.get("market") or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and order[1] in due and due[order[1]] > 0:
            requested = max(0, int(order[2]))
            reduction = min(requested, due[order[1]])
            requested -= reduction
            due[order[1]] -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        market.append(order)
    action["market"] = market[:10]
    state["due_step"], state["due"] = -1, {}
    return action


def _front_run(action, obs, state, step):
    if not _FR_ITEMS:
        return action
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    moved = {}
    action = _copy_action(action)
    for item in _FR_ITEMS:
        target = _future_quantity(step, item)
        if target <= 0 or _town_demand_now(obs, item, step) > 0:
            continue
        stock = max(0, int(_get(shed, item, 0) or 0))
        reserve = _pickup_reserve(action, item) + _existing_sell(action, item)
        quantity = min(target, max(0, stock - reserve))
        if quantity <= 0:
            continue
        market = [list(order) for order in (action.get("market") or [])]
        existing = next((order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + quantity
        elif len(market) < 10:
            market.append(["SELL", item, quantity])
        else:
            continue
        action["market"] = market[:10]
        moved[item] = moved.get(item, 0) + quantity
    if moved:
        state["due_step"] = step + 1
        state["due"] = moved
    return action


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        state = _fr_state(obs, step)
        action = _repay(action, state, step)
        action = _front_run(action, obs, state, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs)
