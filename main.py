"""MapleLeaf 7.3: heuristic Kaggriculture agent with compact CMA-ES tuning.

The compressed action tape supplies a high-output production schedule.
Observation-driven logic repairs route-breaking weeds, protects inventory,
times shared-market sales, reacts to opponent production, and recovers value
in the final turns. The submission runtime uses only Python's standard library.
"""
import base64
import copy
import json
import os
import sys
import zlib

# Kaggle's file-path loader may exec this source without defining __file__.
# The packaged artifact inlines heuristics.py; the guarded path edit is only
# for readable two-file local development.
if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heuristics
import anti_route


_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-rk<O>Z38k^C<__d(6>CdIvRq_!oPGZZMw4ex*$46rr~81`Yjw}t=va>V|qs*H?`%=e1o40vlbTUGD-WkyCu{`h}qfBX5DfByBCv;X?>?7J@?Z{Gj(>H72im%HuR!{Y4kKmY50{{8ru$B+N~`ImqE^?x5f|9JM{<JZ4xAHMtYm!GbG`1t+x&DrAY-R<sdac;i;{9(KOH2A~k?e_iS*Sinf>-)3C<>c${w>P&xoGq5epMSc$egEa%{po*PJUskoG3?l<kMI8U<<s#^gP#3(w%dNb|Ju?YZtw0teEoF%YVu(`44=0*H>Y==Pv3cX+~8HF8N-*JK24_qy?*jCcjjRKj_vq$K1TiA|AxHj)6Mm}EgnhKm&4D^n<gzLZ`}Wv;W$p(@b#M?P77ev$H7<TN8z|`ucz-mEs5*<?cH?YOurki7`RxM(}nZ-_RDnP*ai8AU-!c3n@R836i$a`JhYQBI`!_|^?o@Xe)O~x2OUq%;%Tt#OAli({8czvV8@}UF{|IKTk?+mxPuWJ42GF4`x||>_M=V*ZuH#oemf1Hog#Hbf`J9wz&%L$X)@}7Hm>NPiKp(+Qhg-lZ{k@5L%2U%z#K*MrVrxr9mfxkC+=tTAvbWRac_C>{+D#p`#zsec$W?w{_o&TU7s6%_y&(1-zSTeV>t##Y2xze^VI3dn%Tb3-h!zmLVjuth(0ZNcYAZQeRu!UAGUY*A8$VX_xMccG<fBgB$i0|9W%|r;m#hk$K69mw`1~S=PKVk$hO~$Uj2#Lot{SPx*r?bevK9hFzt-#I55A#vK6d3#W96D0{3dauu~>7@58XSQ6Iwr1WtUy9A!=l{1iQqjRpD?K9G3>qV=e*6X1vXO)ff5{-8>hud;!tPae-d@pIaoUIk<d9|!&9gzErI`_m(>DHv~l3z!hgGHze$aiO6~P_kz>t6!hi|7r5Q4=kv)3TM|11K(D#hw~UPUrqq<$5Zd_7U49~amcP(>5#10568C-4y^p$DYm_(bEzS;IC|5KKyTM3Q-fZ!l|kWFi~~Yu+@+}X36qIh9mHHH*kW|SpYXmA6(zV;Fc>jdm^pN(AlB~(vU+{&>tla|kJX{8HZ#Wwt51J24%A0r)8h}a;E5A@x9>LID|6*EY^CTiCa{#Yz++?$RREA2B9&=BiKMqWvFw6(#^%HI-JiXV^}F#CNP!r;MniS%OL2&XW6?q@u!Ccxk4FkY6NthG{n)Xmx8?>N8CAzY8IDv8g#c`2wCql6^e`x=Sf@PbrzfJTX868=d9LFxQ)ULe&%hfhv1R*UONe?k8(tsV3J`4~%W40+w_mrrHKsP0-nh)zSbHPp^ZniR?z`>X-CuwuQ$m-*4!LiKWXtpJP?KxW9q648Gr&&Ih&H7z%7o20#+<6xrVk=i5vIAUsi7fq0+n)55=T#(*2eL}@$QZvr@?85t9P(F5wEplG_%PGnfAZ90=!<QzJ6+E)$l`~o*G(-qT0)hFxmwAb>?vuG;lV)-D~XXTSdYyG7!<G(R^7w6b?@zBo<f)#2!J1tKu_LmpsB;DwhfaB?cGZ?)LWPYmN&v@%De*PtfD}`2MVH(w*FP+}p(0($Tq)rkb%JI?+<5L+#xPVMp<-q}TFsB1G&BhKn}>!3U%s^)?hrQ^ed2EexjK*Am*)!~oO1mNo*E4RVHnm;}<APi0th>m@+snh4O*Y1B2>L<A-dXi?+Lf#zM1=)9e7bo5P6i^?`&!;C)Zg91(+ixW?CV``)>;FC<u+qtZ$i)8BSGRHrH;kR{cd4UAfv@s@fqBJL0j$uv66B!@`CE}U{Qs@2P;$;_^icu(jbTl;1*Y*Z?e#n3XH8GG)GDyIUGput~fpk~XG&_&MrGN+w4m*a7638By`RgDxnz6x;Q6-X|OcO?1tOd4jXvV0X7S57VlWPzBywTWo$>NJ3#Axxq_(moE0^4VHrS!7HY!rFAs^Eusq?zq->;<^&UArPR&bG_!xo-b*<_(3jNe4|V8Kl%!mbUUrHW~=BEuL^n3&5Bc&b7=qI}kM({>lLh22`hS=7*o<=N}%aw4{PfQ)+;mz5NXmySt#aX>X%U>$?j4id9D0W=IvZ)&Trj%F8I^Vt~7~%~0!<xOcp;hPbb1>;q$tIBrz8NHpy!)0Eq-n08c6+DJGA;IceU@WIgi{^QM`_AAfxjO;Jtw7nKMe7~ii-nSG%0trJOMrPL8DF%x!2_SHgw#Cr{FFUS7u;B%jnpCn)GTbC&k#<y+QZl|zCi>72o`53Oj^{8)B|C>WFT-ObW{`?$PN|Vx#jvP#*pP~qxDxTf+2)pknYI{_J;Ra0kJV4J=4dgpYB{j%g5f*Gx6NbDOb$&3@6^6>|5kHLB$v1Fp_(}!IYq8l)~j`78_?Oy`LcR@*op_&m36854iB6b3aW$?N!-EC%gnyOf;m$sJm(`fxQQC%ly@B4<kU_lHaW~&TGh%9gV=oU_DFeSvxWW29<AVRuf5}g{7zGqn!^tVHb&%z6TWROT&a8Ip<l{O7BROm&T@>6dzb-)O-k8iO(p%cq)#%3-LB$8jLQB*Pl43gH@X(`6TNGV*AYkul+YaND6~Qi#}?OVQNx>LJPHb?L!I7a$d+hx@0*nIhvlpfwCy!5k3{$f(8r7e3>tzw&p-~unzt2NUhrZmC{Lo7L_?#_Yyv0FBq)vs7VJu2wc3AXtDCG1Db&HXCUAi{Ch)ykrYOvONrhT6;wK>Agg69{E>VbaDaLU@=<GRM3S}~9`p`Iy&(Ny+iSrT$5tv>tp;@nk^}0RhfgfbYzU=dYN+mBQE^gaK<KjY0I_Kk}Zs@kI5+avd$$}ki^34<gC}vXu>t5w5)By65mziUAQ#Yx?N&^%|8b9KpH}sI^9Dm4;@J;W9lFHLuAIG}A47aAOWsp;CF1hPEe2W-2ZOyIXk7maTZnn2DLumFY;nW6MrHrDBv@6MSb0G29lp<a&+KRyj!eb3n0zrG1ZypL9SO(wO9{~{I^c4)C<EFli;cOcAghvuX7PgAUgV)xDN<FiSnJth|XcZ4Q!{EfxmICqw!vZ-?2j<zZ#9?}kjQ+RO6T8Gm>5imLG(VJZ<wyjWtRK`t%?BqtL%L@9C~&Dh(nVpa7E}4ARbs!8835B{W5SV94TlA!1<M`YJap7$qUlHwp>=B?qB*qD<eDP8uSvAv(m*6#$(shD%^*&{4KDz1Ef~f=YO|lj9Iv5LhiVXmgtnGPJ<B^lJ88gJCdtP~QIKlF@klVPoF2fjk#CzSU>TCScN_Z8uB+FHxnLrsVZGlJ%#aPb3y}HSj0(pzkOuj}-RGuNQs$J0016Y^uPTMIMklF$Il61Tmd(OwKGC4F{Jm1;3MpaK#((o17j98Z=!liDKXBxZ9f*ci<0P{ix+T5I8-%SuId5MO`0`!U4<arO!?_@oLLN##HZ2>Mhd@(OUgCOTb}-$+E{G*p8CWJD045#8jo`$Rh~+~4%m=B1jG$-xg%@muK0$H{TU?&HS3vD0P;=M;MX<zq2tP2Y{z6XqOOf%45fIY5W(_cH{d$XvbuUg^s;Z2Hi$-fIEn<*fDd(A-HLjheVR~%L(>EB4QH77E?Ug&&Bn+*eDB>{ZdQ#+SHneIAd?e;+rV;=%vh?yG%?Xfc(QT;ah4?tj@ylU*-UhJD{J0AsA*k_77xt}Lp?V%jotq+JE{c4^n`BxDwU6^|Itak0()sNID6)Lom5N&hlGqB;kq{8g<YbySf>x3lros(sRZ2NXobf(VC3YPjy_~nirajDfVcdq$&ugQ*D@xgkRFQ-sP4>JvG;D8J0z+d?4I^5$_`O2bWkTJL2=NZQ9nuw8`>iFr9y3Y&=p@ccoaD}hgQi9T8TUvFs<I)UtO7~QSX%?Eh5}<dVbX}w_{lNb6P{q6dESX|lq`$nG*&f~yY>3I@clSFzdRUyhFa$xeF4QNj5N~^se=)UmQ(Xm5QmG3E@IaiB^eb-m3i-;5gn!-?K0sgV&)Mlq(YMoBiN+-@aTR)62@=Bw|_QLg*Dxw*&q@3eL$k%;#<R`N*~DTDYS~4s~HW*?vi;EwSXfq?~BfT=uuTBqY)KiS`O67%2&tKLynr9gzljF;%Y?%KYX>NV(cVug7F4*?+@W|HnAw|1SfBLOwvlV1^y;V?vjeGXCy_&mrX%*A<!+5bWtS!Xp(QtmIn{o=Oh`zwyqxv71!y>FNP}F?$;bxb|_GUg%Ubw%2L_cmSi`A=s8;qZjy)qa|kxImIp@{17GOXwkDZW)+JE=?z~@pF8EWnJ=BM?AFOU+hlWx&ng}FHvVT4N!1F|UL6LIL23B+j>!}26>Xpg}@zUus#AF<$#jCHI9?fk{!pMnwwylU7CE)7iQ381C1-kh=LIN132Ey|O(`c$93LLx0&W90>1{ZpljMBFkRA@?HDEjbvm4{}b1>&qz^0+=)PVjmmlQURaLb@J?0z0W3fn}+j3PT$XbaM-r9=}Nq^Tk6;DoV~vOYK^am!VPX6U7q9Y)A_J&N>;-M1@yihx{}g<EIOW95wLEuVPnmz$-))NoS_5bhMiBBWhAsrkZJVz=aer4=U+_v?yLA219{F5#Ttlo#;}AQ(9tWl?t`#S~()mSfg?&#X<vZoCa3SdMKmtRTOx+&iMS)f%X|Ubp-7)1NCr1ULrRlom(LBB>>>XT(;-Spf}{~<9YM4Vz-xFys~Ev-R7!mH6**w5X3E3*2@vF73xYfwAg8;wm~B+8${~r^!Gr=i|4X8a<c7e8CU&#lGR9f-Fjv|Q#KjAyD<PHukD0Fzf?`Sg*}Sw5h_y}iNZyr&{Vi7)?l!*Wz-L$oY>Yq03tqml0gW1rE3@J`drk8*TkNJNK-ZbstDDIQCDgFx`bjSIm6sQ2c++I{xew}8L`SB3QGypT~~)BVUY5G_@mT;zii|~^TaTw(C9~ig+?!$eHG0irqO@q24+3_tH!odOOhfXW&ZS4nVO#K2?<0ZHq@}=??3)A)1&2i@3v!V_*2o{fu!1ncX@eBEbhu?U{RV^IRZH&xMU;cmr7EKCzsz&uKCmP8@z%$FV1PRgIa~dHUV-vB4TVKszN5>v{Cn*#g4jX(ZjJwXzR`tZ6ATQOU%*-`{MjXfkJbLA~wb7xwyD%iT4Z5N6EI^v?O3F6F)5Com8!zCpw=m{8+3s*d(+-UB6k1Us!`QD*Bn?C>QDSEL;>h-<|4dL<<U-#8UEjF>77pV)Gh}+a9&UnIDN!tbpvGPYLbkM1=VwHu%XEeSAn;N;*sE(xgU;x&l%Z7%iYQAp-S+>I<-~&E5Q_z&V056ZkI;5=T=>VvV`b3EPE4osy8ob#hnTfncc_Y8;;6)_&N#<{*G`&0}}OMTz>i80qp!5ev3>(tNp9#(|U&0v4<XSXv)$NKQDC>qxk~h;B|gtHsEm7EXjnyR7FT>{u1{_eA47!T)dLngWLQH{~Y)CqgDD(BjhV1O<>(T9Mxur0-gNS?JZrA;7I3Lu}M*lKtK2?@F0Vu^3?8SFXyn*(GMluz5Z}%wp9}@-f@)yjDCbsZGACFHqR21NOZTOU2O&i(GUoQf~@e$p+q!B8P^^?Fo#H`Z3We?U53|m=!{$k1(mfR1i<c9r%KvdPwQy{!~r2Lh?L9DBL1a7c<UASbHs_m<ikp5|8I7O%!U<m@E5dZ%WH7$pjJVE2b)2UV&nNqIW=87ow^F&ro5zPTu=#!7CF%E1Jgye$RL>g@!|@Mx#P#m7293kjYHA5K<GuD#OQ?dbctBF++{z_Jfj;_02(x3KGm@-0kRoZ<?>S)|ylT++lT^i1)(Qr%T(QK4jE8iJ6f}h0<iwX;sIl0CR2{YaQZg1*y~=Mof_^44JDtN51hwDpmu*Dg0^d29Z{385<3x(ks*>IKAsmSvu!yXP<z&z~`@J6~gqLpsK<E7)3o=h0uP_e4eh*O#)wwqqK67g^uMKh2f~N0HpjMl|P~-UI+lyEE4?;-_XlE%Jnidskh_l)s%uQ;T!VoNKDJ4ho*a)0I#pa8B=?q&;y$N!}JEISEkk`ER=inozijcCLUm!!((odT4oQc0HJxTd9_k4ou8lxAb7(QbyShgw5IxbBDIG%OjBx5xghz5lQp8|$$=hdiM8cMlQl9%`0-|wC7HWs0&FtWk6bMg`!`i%R`wy^lyMHNx`*0w#v~X(B)=}<ew`9MeMfFb<94t)d|KW85`oCV<A*1$2*64dmUqotL9$TEOQMcB7hX|?GGObg;+9kZl<6;S2~M`@tS9LqXd5-RX<ZSd)O0A7bf0X0SLNyKQy)|LFmDY_ld1D<z@F1R`7+9C1l%XiJ2fdrlk=}Lx-&v=TIf(p22zm^#UG7Lv<x9ibj)kaDA>*pbf_Zm6BGy)qm7F2V3fEMfd@3i5aL8Nu9v-&-ab^64~b8lNTo``M1^_Os(f3mDJjtj*&o*6<_ttR@|vk15f`kH^kO&}AzxNvS)xzz0tnU#$KhZq`>ZKHjOXJrLwAwfIMD%Y5R(K7bQh&%h5F&~6U4fP^HwRzSJ9xcs<zcMD&pqNgLrZ=mJl{8G*nLQivshA3n<`+GhK#~%F=Qr>}oI#ku07AX!^8gsV1G6ClYi=7Hp;Tg^;ww@WX~uFMy#Vbvh#-!qct&{}-i6PmiKXXD?7^tC~bSs-UUMu-H!@!dZjn5-NHw!FW3@-94aYH8Qe-HO+F<7z2kTsY&Ji<jGWQCX&UN>y0K;CM0F`=~qq%N2{4bf!yiui`|$j(eQ~`wGo(AH4U6;p5o?()~lII9j8*hCbafCFsrPNPMGnhlBMRXaa%{H<}K&jtv>EfD%bl0rF$4sGj>25YZe9OX+h@)YzEE90sukW)n*|ergH0X^3}2mEd@zf4$*`GA?FGv0NOkWiDfi~Qwz>|1+pv7K3jZtKE*mj^3Y|GgYXFO5GlGe!vW-alo0(UT2h?RC6^l2M0uFG?Xs`Md^Kn9aT*fsRf5JLs_8ns#E5qWG0t?=5Q-$x4VOafGV;<nlDSHcbXI~^D4O{%6>Nj!<}r@V{)N_xyF$i&(9#>}VveylksC~tm<zH~Ono~n*5;kr0#L`sTTv&{>8HFLc*Mu#UYFp1vouoHAW|-vR7Nhys<qOZ#v_-b4ng#P4#D5P2*&Riui%xOC|L+vC2B%jFR~DAp_cgCoZzM8pvj_2__iRyszz1J-TbVe=32=%9&5GF3Qj6qP}vGjRXR{D&DO)TSqUhg7nDI+LSG^Y)nBx+Ht^Q4et3^sWWtXl%QD+@mU4#4g%-AAf<Qb&OpVd6g`P;+X+i0rXu%GyHEh+Dh#(iGeaG+7pdt=MZ3v669=+w|J?sU-U@|$4mN_9};jlz6<E_O@SOG${u8ATRnpQ~$t6F?hnY92x@M~9B_t)DJI|R;^P(O#EpU#yAT=axUl0+boX)<ip>NCgbTA}#hcGe&~1+z4&5<82CD&$;im3#h<MHOch_`h!?ZBeE{PNIiF9Sn>DxBsDF*Ie`V^!z}&LjY5wY+b`odpwozZtwNFu<4$e7de0$IzHbD2ZkZoKRIJ7f!{hCKWk)^4%)-l_<n?>{8TYDByiptX6n;!yKHE;vtUQ_>?hP@deqUNO0zLLH<CD#pK@EYCsf%sK2;w3{S*)D!;^Ap<N`T+eri;W5tKm$B_e|pM7G+~J4uL&W`<SSQ@fU&K?e6NADZ}7#W@U_Ry10dg*4Yq;%IC!Wh)5_)3H!F4d6mymR_WwmG~vEeH-@i(mUuAOEH$vkG1NB@^Y*j8-1$CdK2>yDOX*}?CLTj_5@7eQECly=5!_J$lp#jV^&&ijGM^w2{i5TKDaPhZ?w6=K8eF;X;<s26sZW73RmJ%@$dpf`lgn@!f1$g4f1{pOSPUNF*3q4r3t{r&$Rv2jJlmx>?YO>b~~w5D2N~p$`6tOLQ=1hOkyC;Q_1}VIFwz$45EtiDQQKCr&+lI3PTG=Q?9YQ3`<~j56Ehz^fdh{C}#2Eg_dXN##uFm3Uv*Mo>FD`KzBTzv9yxAdgwObF09}n73rs-7#WTOYFtky)O)+igaWAVtz~xG`(^+o3z?N2yMCU@t|UZ81S$^%`y6<h3h8arvmCGneH?YB)XWjCy}|__Ux|$Yu@M_Q6bnlfBI`?Q<eJb@`O2JxTL)B8z&b;SH>|G{I_?!Ec$QdK=Z)3>C-(nJT4I|v4?L)v8UiZ2`~>C|Dc0nKHf#DS15E;eH9{UG;8o83scXn&wEzonHw7gN2)Jr^*mEjV9hDuGj7bxDf;OZ*Ee={LZ6&bvE;}HffrLKCZwbInGsRA%CvRF8D*C&stbef>gHY&=(IWatTuCdMMRqc!HIlr8{aRf*b3-=nstr=rN*l)dWO%OCvH-!-TxU>Kr36THKC$(nBQ~416IfCxjO*sbGZUJO1&OO=gXWXns5?ES=hR(8b~}6#_%muBbJM%2asGC^x4a~7Tx(+6g)fu<s3clx8j9@1`D>S$Lx)Ka;AByJ7p{R@Hg`>$XC^F&N})5NSH_UWP-&w8J6Bh+R<ekNu*6#j+_A+_v9_cET9t%IxRpev+#92k&37(B=&Zk5&H7Q_@C^)k8j=!AZu4HuENABx3SE}P>&79VJaW20*yzSZ>elYhXD$~C61<OL4hHiIe`QP=3J~)`EmCbcn&+;mu*n2QC4Jl;%aI&>^mny5g`noMjTO@{sKrPt)Y*<3rGWm$QU)X|KF@^OhyN>~03e^mb-ZFZWY$E%<&JXY28c0KjA@8K*Z3a1;HBN=O3lW`MJY)iI>RdIJJ;%O5<0Qn?Fmp=#l)r!L~j^2H(>lqqf9qU7@3L}DMMhTj9VDdCiDoUmR+3For+k6l?7?Hv<kOXrU9=c5r%Fel#sYa#Qt|FG3rE6ei}`KrR+-q+g#OMlStQ3Ya`9I<M*)F)<DdM`?%o>2o0jbLSbo~&iR+qP>e}&xgM<Rq%b}aRP8Co`$L36C-*EflrKhOSBq5urk6`#<=ROF)xfyItRzzsWX0CfKNfA%Cg~6yL3o}CVrSPpAtnxAWLUz_k@Pyu7&r{?+JUiNOK_&5$;?|xl;C_8)>(!@kQ6;nm*4b``dS6fgqFNSBJ0Bjn<@1;Ohx00Pz|*=vxu5^%2Los&w#uvF~UUd2#WwA?ESo*2u2DcXQdLsnvS=QoFkPXj1u0-%AMH@mn;+)?v(g8;jq~Ip9;d{WqU440ZxD~#&kyJB}5sPi6}3~OI+*O%VZ7H`J*^>Ebdm&WO1qcm;E!cX+N22ScRvVm@Pu>l8T+UO7GDxI|`UFHWw9dj1I~m_g9~z%gh{IC5T+wvSL_*5QyG2m1Q<!iS2YQnoW=HLF~tOlF!|syUaIr%8G7**kgcRumZ_ViP3LL_a7!J2{K#<@13n=zkGD%G@W@eWlL2^%ya-=S&?8<rvUMCKLo?n`cESnnC6zMMi89V?Q1|QEK8?(%5noZWKdIiSH7<5-88IOEL!OCyCec%3|ej?&@!CZES$+Vgjl+s^qKg3b7qe>0hm`*aQ866z&Tu{sbU(?@cXQHiXocrB~Ry&^Xp&tRLHWu>?Ym!0;-^vPxr~boI~i3F@W2kN`Cft5%ddthr*;WTSr}_skB*GUNKP;Mk@~(^V;6D<;iMfGAG+JQ`JJz?<>IXxbmGjuaTc4%$6Y4cb-a2HESQ1<zYD}BukYoleGW`E9s;>e=-!+CuVpoYLHaX^AkKV+{r||(?#5}M+c8BC`^h(i7zcVlUDrQDiUge=u&MMDK(h>(dP;IZO@G&$wl=Lv~5YYGFP28MqI_@(x^sC%ptaDxT5=|>JLh?Z%z7`irS}KLDjY`PF5ESsJ3(mx~c0pu0f&l;J{54P>x}?y7vtykAQ0&5Y$TqD8)_7f{G~Lm&O3Kln{v`Cuh$!C=Hq_uLGZ)h_2b{vsS&$hmpF>%&anLREQG<hAw_ff@<D?ztjq{)Te_D+6j4dYMofQUQb0^ti3vHDqA7^oJ~(`C={FOdZ~75%9s-CzJ}<DSg<{$5VBl}TxAC_<t90TWX}ghS3}fix7EXMHK&)?MrDf6G~K;<5e79+wN@y0F6YqeQw`5>Ng5(0h?2^KVPJ;@CML21Q-V;X5GA+ycg#Z$s<G`dX%)#dOi4{`Z1?*0`%03CttFFFwL&F-n!<je#ab(bopz>z)D@<U8|LNIG6ZQCsJTcfw7SYr3ak)YJAAuY_`9vZKdP*KlDJQohr(-W;v@Dz8j_i~LAvzUy+3dRIT$7-JsO`f%Wfc50pb#!IT}xv|3mtnR7+1};4x+nvo5R>mq1YMv2G>3f4e0uONmu(NF?CS#;b|cmAur8<&uIhC%r*S%-K|c3p*h??&1p|U3{A)!Uz=B(nw%KL}{WZTTsvF;-xzw2VwnCkSD4TX6VJ<&x_Xalj;xfblGF0iJ_w91^F5v!pyI--U)^AA{B%<9V590fX&OwQ-pRoQIHAemI*`Rn)H@1!n15y2{+}`31*D(ToiS(9*Q`0EZ|`Yj+E&EpPMwb^c6c1;jk8GEh4(8Y41cvrI<J#<btajU`+}?EXF9GRgo%@3Ob~mu87t^bw;EAELh$(iJ_pJ0ll-*xPdm1szN=*_q_^QIT;}n5)QU0^c4>+89{1?FQ+l)#`eK?pd>C6t7Zkpx->0*0sr8|*}FF@^#O1MUP80p-`#$aTji-Ac&(jcXH-1Ns}?un9CIC?t0?*8<Q-?-%ES#lIXjbnZ33Q_YMx8(VfNaJg<+cBPm<V~$W^3gR*u-KmZ74smZNw^G$`4Yh`ks(;glsBH79&GIn{!&1!Xk1yq5-q<*FmCeTHkC)clM+4f0xW%YsX5K!`Q=O6|SS6hQ`>X9d(=3;Jd)2QmSvw}JzTjVM@#`2iN{qCD?Ad9nm8DwN22Ia)L<PUotziRytKeriWVgz#EN#J)JL2oO}A$<O{X^>shPysyV)pnqT)O+ZOuoaKb;C)hDMzSDIGln<n-unfw>e;)oHVUXVd')).decode('utf-8'))
__version__ = "mapleleaf-7.3-heuristic-cma-lite"

# The promoted defaults below seed the compact tuning space. Historical
# experiments and promotion records live in Git history and docs/.

_BAKED_BASE_PARAMS = {
        'weed_replay_steps': 11,
        'town_demand_pulse_period': 10,
        'town_demand_check_interval': 7,
        'town_demand_single_shop_bonus': 0.0006157003847131392,
        'town_demand_multi_shop_bonus': 0.42366855104471457,
        'front_run_lead': 4,
        'front_run_start': 48,
        'front_run_stop': 669,
        'front_run_max_batch': 20,
    }
_BAKED_OVERLAY_PARAMS = {
        'premium_shift_enabled': 1.0,
        'premium_shift_start': 287,
        'premium_shift_stop': 682,
        'premium_shift_fraction': 2.507174265974758,
        'premium_shift_max_batch': 5,
        'premium_shift_min_future_qty': 3,
        'premium_shift_opp_ready_threshold': 4,
        'mirror_max_distance': 34.86886877003725,
        'fert_relay_enabled': 0.0,
        'fert_relay_lead': 3,
        'fert_relay_lead_heavy_animal': 5,
        'fert_relay_start': 353,
        'fert_relay_stop': 610,
        'price_floor_enabled': 0.0,
        'rank_sell_slots_enabled': 1.0,
        'demand_alpha': 0.21164025445907636,
        'opp_sell_enabled': 1.0,
        'opp_sell_start': 45,
        'opp_sell_stop': 704,
        'opp_sell_batch_cap': 5,
        'opp_sell_base_fraction_MILK': 0.12226358671010273,
        'opp_sell_base_fraction_WOOL': 0.19196433115965672,
        'opp_sell_base_fraction_STRAWBERRY': 0.26729391318181406,
        'opp_sell_base_fraction_MELON': 0.5838257424438272,
        'opp_sell_floor_fraction_MILK': 0.46780182162339207,
        'opp_sell_floor_fraction_WOOL': 0.11239281181508977,
        'opp_sell_floor_fraction_STRAWBERRY': 0.07987627492305109,
        'opp_sell_floor_fraction_MELON': 0.41240677828767486,
        'opp_sell_ramp_start': 697,
        'opp_sell_min_supply_fraction': 0.10081480241978077,
        'terminal_soft_start': 708,
        'terminal_hard_start': 708,
        'shed_guard_enabled': 0.0,
        'shed_guard_start': 420,
        'shed_guard_stop': 487,
        'shed_guard_batch_cap': 19,
        'shed_guard_threshold': 94,
        'cycle_sell_enabled': 1.0,
    }
_BAKED_FR_ORDER = ('MILK', 'WOOL', 'MELON', 'STRAWBERRY', 'FERTILIZER', 'EGG', 'CARROT', 'TOMATO')

_FR_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL', 'WHEAT', 'FERTILIZER', 'EGG', 'CARROT', 'TOMATO')
_GENERAL_ACTIONS = _ACTIONS
_ANTI_ACTIONS = anti_route.ACTIONS
_FR_STATE = {
    0: {"last_step": -1, "due_by_step": {}},
    1: {"last_step": -1, "due_by_step": {}},
}
_WEED_STATE = {0: {}, 1: {}}
_ROUTE_MODE_STATE = {
    0: {"last_step": -1, "mode": None},
    1: {"last_step": -1, "mode": None},
}
_WEED_REPLAY_STEPS = 8

# Route-repair and demand-forecast settings. The compact tuner changes only
# ``weed_replay_steps``; the demand model stays fixed in 6.8.
_BASE_PARAMS = {
    "weed_replay_steps": _WEED_REPLAY_STEPS,
    "town_demand_pulse_period": 24,
    "town_demand_check_interval": 4,
    "town_demand_single_shop_bonus": 2,
    "town_demand_multi_shop_bonus": 1,
    "front_run_lead": 4,
    "front_run_start": 48,
    "front_run_stop": 669,
    "front_run_max_batch": 20,
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
        state = {"last_step": step, "due_by_step": {}}
        _FR_STATE[seat] = state
    state["last_step"] = step
    due_by_step = state.setdefault("due_by_step", {})
    for due_step in list(due_by_step):
        if int(due_step) < step:
            due_by_step.pop(due_step, None)
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


def _future_quantity(step, item, lead=1):
    future = step + max(1, int(lead))
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
    due_by_step = state.setdefault("due_by_step", {})
    due = due_by_step.pop(step, None)
    if not due:
        return action
    due = {str(item): max(0, int(quantity)) for item, quantity in dict(due).items()}
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
    return action


def _front_run(action, obs, state, step):
    if not _FR_ITEMS:
        return action
    lead = max(1, int(_BASE_PARAMS["front_run_lead"]))
    if not int(_BASE_PARAMS["front_run_start"]) <= step <= int(_BASE_PARAMS["front_run_stop"]):
        return action
    if step + lead >= len(_ACTIONS):
        return action
    batch_remaining = max(0, int(_BASE_PARAMS["front_run_max_batch"]))
    if batch_remaining <= 0:
        return action
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    moved = {}
    action = _copy_action(action)
    for item in _FR_ITEMS:
        target = min(batch_remaining, _future_quantity(step, item, lead))
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
        batch_remaining -= quantity
        if batch_remaining <= 0:
            break
    if moved:
        due_step = step + lead
        due = state.setdefault("due_by_step", {}).setdefault(due_step, {})
        for item, quantity in moved.items():
            due[item] = due.get(item, 0) + quantity
    return action


# Activate the CMA-ES-discovered configuration (see docstring above).
configure_base(_BAKED_BASE_PARAMS)
_FR_ITEMS = _BAKED_FR_ORDER
heuristics.configure(_BAKED_OVERLAY_PARAMS)


def _route_mode(obs, step):
    """Classify the public opening without relying on hidden state or names."""
    seat = _seat(obs)
    state = _ROUTE_MODE_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state["mode"] = None
    state["last_step"] = step
    if step >= 1 and state.get("mode") is None:
        farms = list(_get(obs, "farms", []) or [])
        opponent = farms[1 - seat] if len(farms) > 1 else {}
        opponent_hands = list(_get(opponent, "hands", []) or [])
        state["mode"] = "anti" if len(opponent_hands) <= 4 else "general"
    return state.get("mode")


def _run_action_tape(obs, tape):
    """Apply the shared heuristic stack to one selected production tape."""
    global _ACTIONS
    previous_tape = _ACTIONS
    _ACTIONS = tape
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(tape) - 1)
        action = _weed_repair_action(obs, _copy_action(tape[step]), step)
        state = _fr_state(obs, step)
        action = _repay(action, state, step)
        action = heuristics.repay_premium_shift(obs, action, step)
        action = heuristics.repay_fertilizer_relay(obs, action, step)
        action = _front_run(action, obs, state, step)
        heuristics._detect_opponent_type(obs, step)
        action = heuristics.price_floor_guard(obs, action, step)
        action = heuristics.rank_sell_slots(obs, action)
        action = heuristics.premium_shift(obs, action, step, tape)
        action = heuristics.fertilizer_relay(obs, action, step, tape)
        action = heuristics.opportunistic_sell(obs, action, step)
        action = heuristics.shed_guard(obs, action, step)
        action = heuristics.terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    finally:
        _ACTIONS = previous_tape


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_GENERAL_ACTIONS) - 1)
        mode = _route_mode(obs, step)
        tape = _ANTI_ACTIONS if step == 0 or mode == "anti" else _GENERAL_ACTIONS
        action = _run_action_tape(obs, tape)

        # Shared opening: preserve the anti route's inventory while adding the
        # fifth worker needed by the general route. Grouped animal purchases
        # free the market slot without changing their quantities.
        if step == 0:
            action = _copy_action(action)
            action["market"] = [
                ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
                ["BUY_ANIMAL", "COW", 2],
                ["BUY_ANIMAL", "SHEEP", 2],
                ["BUY_SEED", "MELON", 5],
                ["BUY_SEED", "WHEAT", 9],
            ]
        elif step == 1 and mode == "general":
            action = _copy_action(action)
            action["market"] = [
                ["BUY_SEED", "MELON", 7],
                ["BUY_PRODUCT", "WHEAT", 6],
            ]
        return action
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs)
