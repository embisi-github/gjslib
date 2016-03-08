#!/usr/bin/env python
"""

notes
errors with eigenvalues for left pencil
FOV 54
844:Error 0.000148 Volume 0.992691 == +1, lengths (1.0078140092456882, 1.0013901914673606, 1.0037499802024081), eigen 0.995977, cam [-4.118176,-22.091639,25.235017]
({'camera': [-4.118176484981601, -22.09163869232736, 25.235017329384764], 'orientation': c_quaternion(euler=(-30.3542,-1.5250,55.0333),degrees=True)}, [-41.931872286369945, -49.024723441728256, -30.951076609604502, -27.293052127230027], 0.00014757983430260937)
self.images['left']['projection'] = {'fov': 54.0, 'camera': [-4.092276484981596, -22.017538692327353, 25.19801732938475], 'orientation': c_quaternion(euler=(-29.0414, 0.0653,52.3864),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 8.25172609418 (2707.080872999666, 1213.816518356337) (2698.844445, 1213.314286)
calc.t.bl 10.0330238807 (1139.6759147671573, 707.9383892761459) (1144.990476, 699.428571)
clips.b.fr 22.0035207986 (925.7754701019085, 1916.0548138172874) (927.740759, 1937.970392)
clips.t.fr 14.1325465997 (807.5927860626681, 1332.626817080778) (811.045201, 1318.922449)
Total error 54.4208173732

FOV 55 (with eigenvalue in error)
1551:Error 0.000100 Volume 0.993356 == +1, lengths (1.005833434032479, 1.0021666921630537, 1.00306832528539), eigen 0.997367, cam [-3.969025,-21.371357,24.741859]
({'camera': [-3.9690252239724186, -21.37135722594334, 24.741859026906628], 'orientation': c_quaternion(euler=(-30.2679,-1.5487,54.8575),degrees=True)}, [-41.07583968388289, -48.11676049573742, -30.18394736025642, -26.464277840700085], 9.984178329298273e-05)
self.images['left']['projection'] = {'fov': 55.0, 'camera': [-3.966125223972422, -21.316257225943332, 24.685859026906613], 'orientation': c_quaternion(euler=(-29.2335,-0.1879,52.3514),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 6.40489597874 (2705.2197905310804, 1213.9288279902291) (2698.844445, 1213.314286)
calc.t.bl 9.01956484986 (1140.236977855537, 707.0938697855245) (1144.990476, 699.428571)
clips.b.fr 19.9902806733 (926.5077439987215, 1918.0181741933484) (927.740759, 1937.970392)
clips.t.fr 12.7483917447 (808.3774313060314, 1331.388583001176) (811.045201, 1318.922449)
Total error 48.1631332466

FOV 55 (without eigenvalue)
1947:Error 0.000022 Volume 0.996323 == +1, lengths (1.0024151285290603, 1.00067474043002, 1.0015250690005377), eigen 0.965743, cam [-4.274075,-21.118481,24.315561]
({'camera': [-4.274075080968033, -21.118481270360572, 24.3155605088203], 'orientation': c_quaternion(euler=(-33.6516,-3.7032,53.7132),degrees=True)}, [-41.77465647836781, -46.62780319434795, -30.0227812140341, -25.775680900567192], 2.2231744744901346e-05)
self.images['left']['projection'] = {'fov': 55.0, 'camera': [-4.251975080968039, -21.047381270360557, 24.275560508820295], 'orientation': c_quaternion(euler=(-29.6901,-0.4857,52.7584),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 11.3754900482 (2710.1491320243586, 1214.5814975518251) (2698.844445, 1213.314286)
calc.t.bl 15.4692667732 (1132.13881090973, 708.0386185555076) (1144.990476, 699.428571)
clips.b.fr 14.5337668572 (925.9681017038746, 1923.5451341107741) (927.740759, 1937.970392)
clips.t.fr 5.23388190926 (811.7816171299362, 1324.104264427405) (811.045201, 1318.922449)
Total error 46.6124055879


FOV 56 (with eigenvalue in error)
1159:Error 0.000063 Volume 0.995179 == +1, lengths (1.0047718738614337, 1.002149690961742, 1.0023848250299787), eigen 0.997515, cam [-3.843066,-20.645356,24.213654]
({'camera': [-3.8430661428585933, -20.64535621555892, 24.21365388496388], 'orientation': c_quaternion(euler=(-30.3705,-1.6786,54.5730),degrees=True)}, [-40.2555626912437, -47.096735096487535, -29.431111078908646, -25.600613408518573], 6.27540137933678e-05)
self.images['left']['projection'] = {'fov': 56.0, 'camera': [-3.812166142858596, -20.59525621555891, 24.16265388496387], 'orientation': c_quaternion(euler=(-29.4030,-0.4387,52.2943),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 6.72514368221 (2705.5439739541916, 1213.9006897332558) (2698.844445, 1213.314286)
calc.t.bl 6.89736545138 (1140.9670524344126, 705.0308663315398) (1144.990476, 699.428571)
clips.b.fr 16.9632506103 (926.3328713460594, 1921.065667109508) (927.740759, 1937.970392)
clips.t.fr 11.9008985748 (807.7074735685507, 1330.3457130904887) (811.045201, 1318.922449)
Total error 42.4866583187

FOV 56 (without eigenvalue in error)
1200:Error 0.000011 Volume 0.997546 == +1, lengths (1.0016133831629075, 1.0012216960341784, 1.000742059584152), eigen 0.969290, cam [-4.115170,-20.416180,23.798622]
({'camera': [-4.115169641395163, -20.416180146397895, 23.798622238269985], 'orientation': c_quaternion(euler=(-33.3673,-3.5330,53.4091),degrees=True)}, [-40.845052934252614, -45.70019773358245, -29.3251257388232, -24.982577813429913], 1.0699233645229686e-05)
self.images['left']['projection'] = {'fov': 56.0, 'camera': [-4.070269641395155, -20.32908014639788, 23.79462223826998], 'orientation': c_quaternion(euler=(-29.8305,-0.7358,52.6465),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 11.4825759444 (2710.2551715191307, 1214.5968110970002) (2698.844445, 1213.314286)
calc.t.bl 12.9784561785 (1133.3619513274857, 705.1920542104762) (1144.990476, 699.428571)
clips.b.fr 11.5773471963 (925.7345612517693, 1926.5681931463612) (927.740759, 1937.970392)
clips.t.fr 4.9008776303 (811.0090286944703, 1323.8231931385494) (811.045201, 1318.922449)
Total error 40.9392569494


FOV 57 (with eigenvalue in error)
808:Error 0.000035 Volume 0.996184 == +1, lengths (1.0035910158651673, 1.0017642388596426, 1.0015589478333826), eigen 0.998541, cam [-3.713631,-19.956044,23.711283]
({'camera': [-3.713630833448766, -19.956043944042488, 23.71128295319602], 'orientation': c_quaternion(euler=(-30.3593,-1.7244,54.2981),degrees=True)}, [-39.44407964676364, -46.15296411283099, -28.724412811151065, -24.793935508330186], 3.524519934726816e-05)
self.images['left']['projection'] = {'fov': 57.0, 'camera': [-3.7117308334487693, -19.931943944042487, 23.624282953195998], 'orientation': c_quaternion(euler=(-29.6295,-0.6924,52.3333),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 5.568812267 (2704.3847602834294, 1213.8769374243514) (2698.844445, 1213.314286)
calc.t.bl 6.66665077731 (1141.0703374886123, 704.8208568453696) (1144.990476, 699.428571)
clips.b.fr 14.3010840429 (926.95920257373, 1923.690680015648) (927.740759, 1937.970392)
clips.t.fr 9.34469231298 (808.3333725746407, 1327.8650023834425) (811.045201, 1318.922449)
Total error 35.8812394002

FOV 57 (without eigenvalue in error)
1905:Error 0.000005 Volume 0.998486 == +1, lengths (1.0011753500796372, 1.0009218944411435, 1.0004227848172174), eigen 0.976742, cam [-3.927376,-19.772743,23.358355]
({'camera': [-3.9273758760863475, -19.77274273317479, 23.358354930836327], 'orientation': c_quaternion(euler=(-32.6825,-3.1236,53.2798),degrees=True)}, [-39.86803053274168, -44.993892640289175, -28.6641351271121, -24.30046386552682], 4.708998420272592e-06)
self.images['left']['projection'] = {'fov': 57.0, 'camera': [-3.9292758760863453, -19.70464273317478, 23.355354930836324], 'orientation': c_quaternion(euler=(-29.9901,-0.9699,52.5824),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 8.6285534234 (2707.364436108155, 1214.678722036425) (2698.844445, 1213.314286)
calc.t.bl 11.4090325869 (1134.6893197677323, 704.3328757261756) (1144.990476, 699.428571)
clips.b.fr 9.88424807809 (926.7406282526083, 1928.136872866068) (927.740759, 1937.970392)
clips.t.fr 4.18200895625 (811.8856586598114, 1323.0191342249416) (811.045201, 1318.922449)
Total error 34.1038430446

FOV 58 (with eigenvalue in error)
1948:Error 0.000017 Volume 0.996857 == +1, lengths (1.0022513536455708, 1.0006967878055006, 1.0011550320478637), eigen 0.999522, cam [-3.592529,-19.301611,23.223950]
({'camera': [-3.5925292490333707, -19.301610697207092, 23.223950052883755], 'orientation': c_quaternion(euler=(-30.3442,-1.7539,53.9849),degrees=True)}, [-38.658048625092164, -45.22711027825239, -28.058206042691786, -24.02104601396928], 1.7060982075282217e-05)
self.images['left']['projection'] = {'fov': 58.0, 'camera': [-3.599729249033371, -19.254410697207078, 23.160050052883747], 'orientation': c_quaternion(euler=(-29.8306,-0.9925,52.2567),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 4.12063335042 (2702.8758542059586, 1214.1671394591174) (2698.844445, 1213.314286)
calc.t.bl 4.74597707896 (1141.482852536535, 702.625581489901) (1144.990476, 699.428571)
clips.b.fr 11.5490371131 (927.5117365442428, 1926.4236259178826) (927.740759, 1937.970392)
clips.t.fr 8.27493051324 (809.2720258721702, 1327.005166671979) (811.045201, 1318.922449)
Total error 28.6905780557

FOV 58 (without eigenvalue in error)
494:Error 0.000002 Volume 0.999063 == +1, lengths (1.0004217630722192, 1.000168254366654, 1.001027892121821), eigen 0.983354, cam [-3.755646,-19.172712,22.948090]
({'camera': [-3.7556456598329753, -19.172711693321073, 22.948090388004683], 'orientation': c_quaternion(euler=(-32.0751,-2.7673,53.1382),degrees=True)}, [-38.95275660429533, -44.31329942220487, -28.032162250836656, -23.650055624900276], 2.142207004404038e-06)
self.images['left']['projection'] = {'fov': 58.0, 'camera': [-3.7306456598329736, -19.122611693321062, 22.947090388004682], 'orientation': c_quaternion(euler=(-30.0658,-1.1351,52.4809),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 6.92340848121 (2705.6810368317056, 1214.4072622688625) (2698.844445, 1213.314286)
calc.t.bl 8.4635936521 (1137.3891049067927, 703.1503414135559) (1144.990476, 699.428571)
clips.b.fr 8.3480310113 (927.1240065005046, 1929.645174998623) (927.740759, 1937.970392)
clips.t.fr 3.99695400071 (810.8145822206535, 1322.9127442600552) (811.045201, 1318.922449)
Total error 27.7319871453

FOV 59 (with eigenvalue in error)
1906:Error 0.000006 Volume 0.998173 == +1, lengths (1.0016047554263632, 1.0001976955196454, 1.000704358843221), eigen 1.000118, cam [-3.482327,-18.650909,22.721884]
({'camera': [-3.482326702968548, -18.650908606468967, 22.721884396152394], 'orientation': c_quaternion(euler=(-30.4052,-1.8177,53.6083),degrees=True)}, [-37.89107060557242, -44.25487086547503, -27.410587042483733, -23.241005660664225], 6.475641560994873e-06)
self.images['left']['projection'] = {'fov': 59.0, 'camera': [-3.5202267029685443, -18.643808606468966, 22.66788439615238], 'orientation': c_quaternion(euler=(-30.0705,-1.2607,52.2952),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 1.8256023512 (2700.4070882479095, 1214.2581980851476) (2698.844445, 1213.314286)
calc.t.bl 4.70231643373 (1141.5672464201466, 702.6524318975127) (1144.990476, 699.428571)
clips.b.fr 9.22552692634 (928.6434328670133, 1928.789132448152) (927.740759, 1937.970392)
clips.t.fr 5.56161646594 (810.7831908950839, 1324.4778903343235) (811.045201, 1318.922449)
Total error 21.3150621772

FOV 59 (without eigenvalue in error)
850:Error 0.000001 Volume 0.999422 == +1, lengths (1.0002662449676682, 1.0003278509350473, 0.9999530345887988), eigen 0.987274, cam [-3.610837,-18.539466,22.477204]
({'camera': [-3.6108370613513863, -18.539466355978387, 22.47720359720192], 'orientation': c_quaternion(euler=(-31.7654,-2.5797,52.8451),degrees=True)}, [-38.10542013255729, -43.48946184326072, -27.413484403589948, -22.94126818090679], 5.154514381434025e-07)
self.images['left']['projection'] = {'fov': 59.0, 'camera': [-3.6487370613513828, -18.464366355978377, 22.44120359720191], 'orientation': c_quaternion(euler=(-30.3219,-1.4426,52.4957),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 5.64791095002 (2704.3410276578616, 1214.6129303642106) (2698.844445, 1213.314286)
calc.t.bl 8.33487753511 (1137.036799368963, 701.9203999616566) (1144.990476, 699.428571)
clips.b.fr 4.98953601988 (927.8112784966395, 1932.981354347883) (927.740759, 1937.970392)
clips.t.fr 1.91719699971 (812.1703937986822, 1320.4747329629017) (811.045201, 1318.922449)
Total error 20.8895215047

FOV 60: (with eigenvalue in error)
1906:Error 0.000002 Volume 0.998978 == +1, lengths (1.0004440267438814, 1.0004154766458977, 1.0001438059354404), eigen 1.000400, cam [-3.377420,-18.023306,22.235380]
({'camera': [-3.3774200436514867, -18.023306089577623, 22.235379937995873], 'orientation': c_quaternion(euler=(-30.4789,-1.8878,53.2278),degrees=True)}, [-37.15806510155439, -43.313452828502534, -26.78910363637637, -22.488249853591135], 1.5976151286166559e-06)
self.images['left']['projection'] = {'fov': 60.0, 'camera': [-3.3395200436514902, -18.037206089577626, 22.170379937995857], 'orientation': c_quaternion(euler=(-30.1903,-1.4328,52.2848),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 3.37257522605 (2702.1966902707504, 1213.6840363213187) (2698.844445, 1213.314286)
calc.t.bl 2.42178458432 (1143.3957072466771, 701.2511387480604) (1144.990476, 699.428571)
clips.b.fr 5.61433102134 (928.0063644469168, 1932.3623471924275) (927.740759, 1937.970392)
clips.t.fr 4.70706513517 (808.1587556988898, 1322.640633464277) (811.045201, 1318.922449)
Total error 16.1157559669

FOV 60 (without eigenvalue in error)
1241:Error 0.000000 Volume 0.999980 == +1, lengths (1.0004052304655555, 0.9998069030379652, 1.0003534083472727), eigen 0.992195, cam [-3.467879,-17.958587,22.049439]
({'camera': [-3.467879018901589, -17.958587176075188, 22.04943865760937], 'orientation': c_quaternion(euler=(-31.3643,-2.3318,52.5735),degrees=True)}, [-37.26723632156869, -42.73659465192916, -26.827845576443714, -22.2871883172808], 3.2679147106018483e-07)
self.images['left']['projection'] = {'fov': 60.0, 'camera': [-3.447679018901592, -17.926687176075188, 22.059638657609373], 'orientation': c_quaternion(euler=(-30.3762,-1.5908,52.3890),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 4.15174159465 (2702.892616222531, 1214.235843389321) (2698.844445, 1213.314286)
calc.t.bl 4.98243559343 (1140.1774610808347, 700.7168069374562) (1144.990476, 699.428571)
clips.b.fr 3.46870183058 (928.1163740440674, 1934.5220872385069) (927.740759, 1937.970392)
clips.t.fr 1.58128668366 (810.5899340524713, 1320.436780397812) (811.045201, 1318.922449)
Total error 14.1841657023

FOV 61 (with eigenvalue in error):
1158:Error 0.000001 Volume 0.999815 == +1, lengths (1.0002147489799573, 1.0001966667409397, 0.9997876912534899), eigen 1.000674, cam [-3.283279,-17.411709,21.729697]
({'camera': [-3.283279155103133, -17.411709071405, 21.729697456310426], 'orientation': c_quaternion(euler=(-30.5771,-1.9295,52.7120),degrees=True)}, [-36.42531718208429, -42.31637501795742, -26.2151323579798, -21.74220946254544], 6.188103634750908e-07)
self.images['left']['projection'] = {'fov': 61.0, 'camera': [-3.2533791551031355, -17.399809071405, 21.729697456310426], 'orientation': c_quaternion(euler=(-30.4178,-1.7662,52.2187),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 1.84506856826 (2700.5287205631357, 1214.0676078760848) (2698.844445, 1213.314286)
calc.t.bl 1.6314251824 (1143.5189018977774, 698.7242856974107) (1144.990476, 699.428571)
clips.b.fr 2.46745161466 (928.668783842545, 1935.6841095672478) (927.740759, 1937.970392)
clips.t.fr 2.87546998858 (809.5804227900968, 1321.396868619029) (811.045201, 1318.922449)
Total error 8.8194153539

FOV 61 (without eigenvalue in error):
({'camera': [-3.300408297580593, -17.404191212703193, 21.701809861760584], 'orientation': c_quaternion(euler=(-30.7454,-2.0186,52.6015),degrees=True)}, [-36.45438980231268, -42.221658786163786, -26.223056868254407, -21.710607857250096], 1.9937541717591305e-07)
self.images['left']['projection'] = {'fov': 61.0, 'camera': [-3.301408297580593, -17.353191212703184, 21.713709861760584], 'orientation': c_quaternion(euler=(-30.4919,-1.8528,52.2224),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 1.5932614131 (2699.94583737898, 1214.4655534572018) (2698.844445, 1213.314286)
calc.t.bl 3.07630154466 (1142.2329135583764, 698.0649432743164) (1144.990476, 699.428571)
clips.b.fr 2.10417341575 (928.9569238510562, 1936.253275574534) (927.740759, 1937.970392)
clips.t.fr 2.19927173647 (811.219885780396, 1321.1147722878216) (811.045201, 1318.922449)
Total error 8.97300810999

FOV 62:
493:Error 0.000001 Volume 1.000294 == +1, lengths (1.000122119595293, 1.0004949048440746, 1.000412438326702), eigen 0.999632, cam [-3.212826,-16.829395,21.202056]
({'camera': [-3.2128256120977765, -16.829395061879545, 21.202055678717354], 'orientation': c_quaternion(euler=(-30.8028,-1.9910,51.9694),degrees=True)}, [-35.71880484850182, -41.21841696803028, -25.704992173943793, -20.99802261011884], 6.516124319185851e-07)
self.images['left']['projection'] = {'fov': 62.0, 'camera': [-3.241725612097774, -16.803595061879548, 21.202055678717354], 'orientation': c_quaternion(euler=(-30.7688,-2.1010,52.3614),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 1.32916064737 (2697.9631503773276, 1214.309267313671) (2698.844445, 1213.314286)
calc.t.bl 2.99289834911 (1142.0029326351043, 699.2496152206791) (1144.990476, 699.428571)
clips.b.fr 2.8073088752 (930.1541128912625, 1939.4045140716255) (927.740759, 1937.970392)
clips.t.fr 2.65485990563 (812.5708339582101, 1316.749726009063) (811.045201, 1318.922449)
Total error 9.78422777731

FOV 62 (without eigenvalue in error):
1199:Error 0.000000 Volume 0.999911 == +1, lengths (1.0004866124078358, 1.0002501900837397, 1.0001000861107967), eigen 0.998572, cam [-3.226175,-16.818059,21.159484]
({'camera': [-3.2261751996668275, -16.81805942346751, 21.159484489495455], 'orientation': c_quaternion(euler=(-30.9106,-2.0167,51.8022),degrees=True)}, [-35.71987041192106, -41.1108708818926, -25.73219037678035, -20.96904846725481], 3.1735358130944113e-07)
self.images['left']['projection'] = {'fov': 62.0, 'camera': [-3.255075199666825, -16.813959423467512, 21.159484489495455], 'orientation': c_quaternion(euler=(-30.7985,-2.0811,52.4415),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 0.985684957032 (2698.3120913345488, 1214.1438487820726) (2698.844445, 1213.314286)
calc.t.bl 3.51595379885 (1141.6128442120716, 700.4050619732433) (1144.990476, 699.428571)
clips.b.fr 2.97839107443 (930.1975572036199, 1939.654124751645) (927.740759, 1937.970392)
clips.t.fr 3.74251741151 (812.4735955893343, 1315.4632402071427) (811.045201, 1318.922449)
Total error 11.2225472418


FOV 63:
1200:Error 0.000003 Volume 0.998512 == +1, lengths (0.9998350895680005, 1.000309572174737, 1.0001287819828082), eigen 1.000652, cam [-3.122802,-16.285737,20.722242]
({'camera': [-3.1228017565319814, -16.285736712003562, 20.722241720371095], 'orientation': c_quaternion(euler=(-30.7588,-1.8793,51.3079),degrees=True)}, [-35.0, -40.290410729145066, -25.242945546996065, -20.340972882038304], 2.7851091631970217e-06)
self.images['left']['projection'] = {'fov': 63.0, 'camera': [-3.1317017565319794, -16.30263671200357, 20.722241720371095], 'orientation': c_quaternion(euler=(-30.9671,-2.2695,52.4784),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 40.0}
calc.b.fr 2.01549266582 (2696.878404351334, 1213.758014355843) (2698.844445, 1213.314286)
calc.t.bl 2.19104963134 (1143.1391961560596, 700.6005187063397) (1144.990476, 699.428571)
clips.b.fr 5.38202604813 (930.9393265230191, 1942.2988293835688) (927.740759, 1937.970392)
clips.t.fr 6.21148438726 (812.0753606897277, 1312.7969849925305) (811.045201, 1318.922449)
Total error 15.8000527325


"""

#a Imports
import math
from gjslib.math import matrix, vectors, statistics, quaternion

#a c_image_projection
class c_image_projection(object):
    delta_angle = 0.005  # radians - 0.1 is 6 degrees
    camera_step = 0.01 
    fov_step = 0.01    
    camera_deltas = [{"camera":(-camera_step,0.0,0.0)},
                     {"camera":(+camera_step,0.0,0.0)},
                     {"camera":(0.0,-camera_step,0.0)},
                     {"camera":(0.0,+camera_step,0.0)},
                     {"camera":(0.0,0.0,-camera_step)},
                     {"camera":(0.0,0.0,+camera_step)},
                     {"camera":(-camera_step,-camera_step,0.0)},
                     {"camera":(+camera_step,-camera_step,0.0)},
                     {"camera":(-camera_step,+camera_step,0.0)},
                     {"camera":(+camera_step,+camera_step,0.0)},
                     {}]
    orientation_deltas = [{"roll":-delta_angle},
                          {"roll":+delta_angle},
                          {"pitch":+delta_angle},
                          {"pitch":-delta_angle},
                          {"yaw":+delta_angle},
                          {"yaw":-delta_angle},
                          {"roll":+delta_angle, "yaw":+delta_angle},
                          {"roll":+delta_angle, "yaw":-delta_angle},
                          {"roll":-delta_angle, "yaw":+delta_angle},
                          {"roll":-delta_angle, "yaw":-delta_angle},
                          {"roll":+delta_angle, "pitch":+delta_angle},
                          {"roll":+delta_angle, "pitch":-delta_angle},
                          {"roll":-delta_angle, "pitch":+delta_angle},
                          {"roll":-delta_angle, "pitch":-delta_angle},
                          {"yaw":+delta_angle, "pitch":+delta_angle},
                          {"yaw":+delta_angle, "pitch":-delta_angle},
                          {"yaw":-delta_angle, "pitch":+delta_angle},
                          {"yaw":-delta_angle, "pitch":-delta_angle},
                     {}]
    fov_deltas = [{"fov":-fov_step},
                  {"fov":+fov_step},
                  {}]
    #f __init__
    def __init__(self,name,image_filename,size=(1.0,1.0)):
        self.name = name
        self.image_filename = image_filename
        self.mvp = None
        self.ip = None
        self.size = size
        self.projection = None
        pass
    #f save_projection_string
    def save_projection_string(self):
        """
        Save string - should be a set of 'n' comma separated items
        """
        repr = "%f,%f,%f "%(self.projection["camera"][0],
                            self.projection["camera"][1],
                            self.projection["camera"][2])
        rpy = self.projection["orientation"].to_euler(degrees=True)
        repr += ", %f,%f,%f "%(rpy[0], rpy[1], rpy[2])
        repr += ", %f, %f, %f "%(self.projection["fov"],
                                 self.projection["aspect"],
                                 self.projection["zFar"])
        return repr
    #f load_projection_strings
    def load_projection_strings(self, data):
        """
        Load a list of strings (undo the save)
        """
        camera = (float(data[0]), float(data[1]), float(data[2]))
        rpy    = (float(data[3]), float(data[4]), float(data[5]))
        fov    = float(data[6])
        aspect = float(data[7])
        zFar   = float(data[8])
        projection = {"camera":camera,
                      "orientation":quaternion.c_quaternion.of_euler(rpy=rpy, degrees=True),
                      "fov":fov,
                      "aspect":aspect,
                      "zFar":zFar}
        self.set_projection(projection)
        pass
    #f get_projection
    def get_projection(self):
        return self.projection
    #f set_projection
    def set_projection(self, projection=None, deltas=None, delta_scale=1.0, resultant_projection=None, verbose=False ):
        if projection is None:
            projection = {"camera":(0.0,0.0,-20.0), "orientation":quaternion.c_quaternion(), "fov":90, "aspect":1.0}
            pass
        fov         = projection["fov"]          # Scalar
        aspect      = projection["aspect"]       # Scalar (x / y)
        camera      = projection["camera"]       # 3D vector
        orientation = projection["orientation"]  # unit quaternion
        orientation = orientation.copy()
        if deltas is not None:
            if "camera"      in deltas: camera = vectors.vector_add(camera, deltas["camera"], scale=delta_scale)
            if "roll"        in deltas: orientation = quaternion.c_quaternion.roll (deltas["roll"] *delta_scale).multiply(orientation)
            if "pitch"       in deltas: orientation = quaternion.c_quaternion.pitch(deltas["pitch"]*delta_scale).multiply(orientation)
            if "yaw"         in deltas: orientation = quaternion.c_quaternion.yaw  (deltas["yaw"]  *delta_scale).multiply(orientation)
            if "aspect"      in deltas: aspect = aspect* (1+delta_scale*deltas["aspect"])
            if "fov"         in deltas: fov    = fov   * (1+delta_scale*deltas["fov"])
            pass
        self.mvp = matrix.c_matrix4x4()
        #self.mvp.perspective(fov=fov, aspect=aspect, zFar=1.0, zNear=0.0)
        # Use 360 as we use 'half FOV' i.e. fov/2
        yfov = math.atan(math.tan(fov/360.0*3.1415926)/aspect)*360.0/3.14159256
        # zFar and zNear do not seem to effect mapping to image (correctly!)
        # However, zNear must not be 0 or the projection matrix will be singular
        zFar = 40.0
        if "zFar" in projection:zFar=projection["zFar"]
        self.mvp.perspective(fov=yfov, aspect=aspect, zFar=zFar, zNear=1.0)
        persp = self.mvp.copy()
        z_of_w_1 = self.mvp.apply((0.0,0.0,-1.0,0.0))
        self.mvp.mult3x3(m=orientation.get_matrix3())
        self.mvp.translate(camera, scale=-1)

        self.ip = self.mvp.projection()
        self.ip.invert()

        self.projection = { "camera":      camera[:],
                            "orientation": orientation,
                            "fov": fov,
                            "zFar": zFar,
                            "aspect": aspect,
                            "z_of_w_1":z_of_w_1[2]
                            }

        if resultant_projection is not None:
            resultant_projection["camera"]      = camera[:]
            resultant_projection["orientation"] = orientation.copy()
            resultant_projection["fov"]         = fov
            resultant_projection["aspect"]      = aspect
            resultant_projection["zFar"]        = zFar
            pass

        if verbose:
            print "Projection..."
            print self.projection
            print persp
            print self.mvp
            c = matrix.c_matrixNxN(data=self.mvp.get_matrix(linear=True))
            print c
            c.invert()
            print "c, ip"
            print c
            print self.ip
            c.postmult(matrix.c_matrixNxN(data=persp.get_matrix(linear=True)))
            print c

        pass
    #f image_of_model
    def image_of_model(self,xyz, perspective=True):
        if self.mvp is None:
            return None
        xyzw = self.mvp.apply(xyz, perspective=perspective)
        img_xy = ((1.0+xyzw[0])/2.0*self.size[0], (1.0-xyzw[1])/2.0*self.size[1])
        return (xyzw,img_xy)
    #f model_line_for_image
    def model_line_for_image(self,xy):
        if self.ip is None:
            return None
        dirn = self.ip.apply((xy[0],xy[1],self.projection["z_of_w_1"],1))
        return (self.projection["camera"], dirn[0:3])
    #f mapping_error
    def mapping_error(self, name, xyz, xy, corr=None, epsilon=1E-6, verbose=False ):
        abs_error = 0
        (img_uvzw, img_xy) = self.image_of_model(xyz)
        error = ( (xy[0]-img_uvzw[0])*(xy[0]-img_uvzw[0]) +
                  (xy[1]-img_uvzw[1])*(xy[1]-img_uvzw[1]))
        if corr is not None:
            corr[0].add_entry(xy[0], img_uvzw[0])
            corr[1].add_entry(xy[1], img_uvzw[1])
            pass
        if verbose:
            print "%16s"%name, error, "xy %s:%s"%(str(xy), str(img_uvzw[0:2]))
            pass
        return error
    #f calc_point_errors
    def calc_point_errors(self, point_mappings, pt_names, use_references=False, verbose=False):
        err = 0
        corr = [statistics.c_correlation(), statistics.c_correlation()]
        pts = 0
        for n in pt_names:
            xyz = point_mappings.get_xyz( n, use_references )
            mapping_xy = point_mappings.get_xy(n,self.name)
            if (xyz is not None) and (mapping_xy is not None):
                err += self.mapping_error(n,xyz,mapping_xy,corr,verbose=verbose)
                pts += 1
                pass
            pass
        return (pts,err,corr)
    #f select_best_z_set
    def select_best_z_set(self, O, Pe, uv, guess_Z, max_results=20, verbose=False):
        """
        O = Object matrix (must be c_matrixNxN of order 4)
        Pe = perspective matrix (from projection aspect, FOV, zFar, zNear)
        image_locations = list of four (u,v) locations for the 4 columns of O
        guess_Z = dictionary of key -> four Z values to use (should all be -ve since they must be in front of the camera)

        Take an Object matrix with columns being 4 object reference points X, Y, Z, 1
        For each column have an image location (u,v) and a guess of distance from camera (Z), such that
        the image space vector would be u,v,z,w where w=-Z and z=((zF+zN).Z + 2*zF*zN)/(zF-zN).
        We can build an image matrix U with each column being (u,v,z,w)

        Now for a valid projection P we have P.O = U
        Hence P = U.O' (O' == O inverse)
        Further, P = Persp.Orient.Camera (Pe.Or.Ca)
        If we know the aspect ratio and FOV for the camera and zF and zN, we know Pe
        So Pe.Or.Ca = U.O', Or.Ca = Pe'.U.O'
        Inverting both sides yields Ca'.Or' = O.U'.Pe

        Ca'.Or' is a translation of a rotation; the translation can be determined by the fourth column
        of the matrix. The bottom row of the matrix should be (0,0,0,1).
        The top 3x3 should be the orientation matrix - a rotation.
        A rotation is supposed to be a unit orthogonal matrix.
        To test for orthogonality find the volume of the unit cube post-rotation; this is V0.V1xV2
        where Vi are the column vectors of the rotation matrix (also this is the determinant...)
        Also, the lengths of each column vector should be 1.
        So a measure of non-orthogonality is:
        NO(Vol) * NO(|V0|) * NO(|V1|) * NO(|V2|)
        where NO(x)=x if x>1, NO(x)=1/x if 0<x<1, NO(x)=1E9 if x<=0
        """
        smallest_error = None
        result_list = []
        U = matrix.c_matrixNxN(order=4)
        for Zk in guess_Z:
            Z_list    = guess_Z[Zk]
            for c in range(4):
                (_, _, z, w) = Pe.apply( (0.0,0.0,Z_list[c],1.0) )
                U[0,c] = w * uv[c][0]
                U[1,c] = w * uv[c][1]
                U[2,c] = z
                U[3,c] = w
                pass

            U_i = U.inverse()
            if U_i is None:
                continue

            Ca_i_Or_i = O.copy()
            Ca_i_Or_i.postmult(U_i)
            Ca_i_Or_i.postmult(Pe)

            # Rotation is top-left 3x3 of Or_i
            R = matrix.c_matrixNxN(order=3)
            for r in range(3):
                for c in range(3):
                    R[r,c] = Ca_i_Or_i[r,c]
                    pass
                pass

            camera = Ca_i_Or_i.get_column(3)[0:3]
            zs_okay = True
            for c in range(4):
                if vectors.vector_separation(O.get_column(c)[:3],camera)*1.1 < -Z_list[c]:
                    zs_okay = False
                    break
                pass
            if not zs_okay:
                continue

            # Rotations have a single eigenvalue - it should be 1, but that is less critical than the volume and lengths of R
            # Prune out any clearly non-rotations with number of eigenvalues though
            e = R.eigenvalues()
            if len(e)>1:
                continue

            # The rotation MUST be a right-handed set of vectors, else we are in some wonky space
            # Also the volume of the unit cube should remain 1 for a pure rotation
            v = (R.get_column(0),R.get_column(1),R.get_column(2))
            volume_r  = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
            if (volume_r<0):
                continue

            # If the volume is 1 then the unit cube could have been stretched in X and squashed in Y, for example
            # Make sure the scalings along each vector approach 1.0
            lengths_r = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
            def NO(x, epsilon=1E-9):
                if (x>1): return x
                if (x>1E-9): return 1/x
                return 1E9
            def sum_sq(xs):
                v = 0
                for x in xs:
                    v += x*x
                    pass
                return v
            v = (R.get_row(0),R.get_row(1),R.get_row(2))
            lengths_c = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))

            # Error term is sum of squares of x-1 (or 1/x-1 if x<1) so each counts the same
            # Note that the eigenvalue should also approach 1, but adding it in does not really change things much
            error = sum_sq((NO(volume_r)-1, NO(lengths_r[0])-1, NO(lengths_r[1])-1, NO(lengths_r[2])-1, NO(lengths_c[0])-1, NO(lengths_c[1])-1, NO(lengths_c[2])-1))
            if (error<1E9):
                if (len(result_list)<max_results) or (error<result_list[-1][0]):
                    orientation = quaternion.c_quaternion().from_matrix(R.transpose())
                    r = (Zk, camera, orientation)
                    print "%s:Error %6f Volume %6f == +1, lengths %s, eigen %6f, cam [%5f,%5f,%5f]"%(str(Zk),error, volume_r, str(lengths_c), e[0], camera[0],camera[1],camera[2])
                    index = 0
                    for i in range(len(result_list)):
                        if error<result_list[i][0]:
                            index = i
                            break
                        pass
                    result_list.insert(index,(error,r))
                    if len(result_list)>max_results:
                        result_list = result_list[:max_results]
                        pass
                    pass
                pass
            pass
        return result_list
    #f improve_projection
    def improve_projection(self, O, Pe, uv, guess_Z, coarseness, initial_max_error=1E9, verbose=False):
        """
        O = object matrix (4x4, columns are object x,y,z,1)
        Pe = perspective matrix (1/f, 1/f.aspect, zfar/znear, -1...)
        uv = [(u,v)] * 4
        guess_Z = base four MVP.xyz Z values to spread around
        """
        base_guess_Z = guess_Z

        guess_Z = {}
        for gi in range(7*7*7*7):

            gi2 = gi
            if False:
                ci = (gi2/(7*7*7*7)) % 15
                zNear = 1.0
                zFar = 20.0*math.pow(1.3,1+5-ci)
                Pe[2,2] = (zNear+zFar)/(zFar-zNear)
                Pe[2,3] = 2*zNear*zFar/(zFar-zNear)
                pass

            gZ = []
            for c in range(4):
                ci = (gi2 % 7)
                gi2 = gi2 / 7
                gZ.append(base_guess_Z[c]*math.pow(coarseness,(ci-3)))
                pass
            guess_Z[gi] = gZ
            pass
        r = self.select_best_z_set(O=O, Pe=Pe, uv=uv, guess_Z=guess_Z, max_results=1, verbose=False)
        if r is None:
            return None
        (error, (gi, camera, orientation)) = r[0]
        return ({"camera":camera, "orientation":orientation}, guess_Z[gi], error)

    #f get_best_projection_for_guess_Z
    def get_best_projection_for_guess_Z(self, O, Pe, uv, guess_Z, spread=1.15, iterations=5):
        """
        O = object matrix (4x4, columns are object x,y,z,1)
        Pe = perspective matrix (1/f, 1/f.aspect, zfar/znear, -1...)
        uv = [(u,v)] * 4
        guess_Z = base four MVP.xyz Z values to spread around
        """
        max_error = 1E9
        for c in range(iterations):
            # Each run uses coarseness^-3 ... 1.0 ... coarseness^3
            # So an overlap of coarseness^1.5 seems sensible
            coarseness = math.pow(spread,(1.5/(1.5*(c+1))))
            print "Run with coarseness",c,coarseness
            r = self.improve_projection( O=O, Pe=Pe, uv=uv,
                                         guess_Z = guess_Z,
                                         initial_max_error = max_error*1.01,
                                         coarseness = coarseness )
            if r is None:
                return None
            (improved_projection, improved_z, max_error) = r
            guess_Z = improved_z
            pass
        return (improved_projection, improved_z, max_error)
    #f guess_initial_projection_matrix
    def guess_initial_projection_matrix(self, point_mappings ):
        # iphone 6s has XFOV of about 55, YFOV is therefore about 47
        # FOV is currently not critical though - 55-63 is a good range...
        projection = {"aspect":self.size[0]/float(self.size[1]),
                      "fov":57.0,
                      "zFar":40.0
                      }

        object_guess_locations = {}
        for pt in point_mappings.object_guess_locations:
            if pt in point_mappings.image_mappings:
                object_guess_locations[pt] = point_mappings.object_guess_locations[pt]
                pass
            pass

        image_locations = {}
        pt_names = object_guess_locations.keys()
        for pt in pt_names:
            if self.name in point_mappings.image_mappings[pt]:
                image_locations[pt] = point_mappings.image_mappings[pt][self.name]
                pass
            else:
                del(object_guess_locations[pt])
                pass
            pass

        if len(image_locations)!=4:
            print "Require 4 object guess locations with image locations for initial projection matrix"
            return None

        pt_names = image_locations.keys()
        pt_names.sort()

        O = matrix.c_matrixNxN(order=4)
        objs = []
        uv = []
        Oc = (0.0,0.0,0.0)
        for c in range(4):
            pt = pt_names[c]
            obj = object_guess_locations[pt]
            O[0,c] = obj[0]
            O[1,c] = obj[1]
            O[2,c] = obj[2]
            O[3,c] = 1.0
            u = -1.0 + (image_locations[pt][0]/self.size[0])*2.0
            v =  1.0 - (image_locations[pt][1]/self.size[1])*2.0
            uv.append((u,v))
            Oc = vectors.vector_add(Oc,obj,scale=0.25)
            objs.append(obj)
            pass

        Pe = self.pe_matrix_of_projection(projection)

        guess_Z = {}
        # The range we need has got to cover the camera position
        # For img_1 we used 0, -1.7, ... -17
        # For left  we used -10, -12.5, -15.0, ... -35
        #Since this is early doors we can use a big range.
        # However, an exponential range may be too much - is linear too small?
        # Change from 11 n to 20 n
        # That means range is now -10 to -60, which is not enough for the pencil image right
        # So going to scale it up
        # Using n=7 for speed for selecting best camera line
        n = 20
        for i in range(n*n*n*n):
            # vi in range 0 to n-1
            # zs in range 0 to 1.7*(n-1) in steps of 1.7
            v = (i%n, (i/n)%n, (i/n/n%n), (i/n/n/n%n))
            zs = []
            for c in range(4):
                #zs.append( -1.0*(v[c]*2.5)-10 ) # was 1.7 for 'img_1'
                zs.append( 2.0*(-1.0*(v[c]*2.5)-10) ) # was 1.7 for 'img_1'
                pass
            guess_Z[v] = zs
            pass
        results = self.select_best_z_set(O, Pe, uv, guess_Z, max_results=100)

        camera_deltas = []
        camera_deltas_per_ijkl = {}
        for r in results:
            (_, (ijkl, camera, _)) = r
            camera_deltas_per_ijkl[ijkl] = r
            for r2 in results:
                (_, (ijkl2, camera2, _)) = r2
                if ijkl != ijkl2:
                    dc = vectors.vector_add(camera, camera2, scale=-1.0)
                    l = vectors.vector_length(dc)
                    if l>0.01:
                        camera_deltas.append( (vectors.vector_scale(dc,1/l),[(ijkl,ijkl2)] ) )
                        pass
                    pass
                pass
            pass

        cos_angle = 0.99 # This means the cameras are in line by arccos(0.99), or 8 degrees
        cos_angle = 0.95 # This means the cameras are in line by arccos(0.95), or 18 degrees
        cos_angle = 0.90  # This means the cameras are in line by arccos(0.9), or 25 degrees
        i = 0
        while i<len(camera_deltas):
            dc_i = camera_deltas[i]
            j = i+1
            while j<len(camera_deltas):
                dc_j = camera_deltas[j]
                d = vectors.dot_product(dc_i[0], dc_j[0])
                if d<0: d=-d
                if (d>cos_angle):
                    j = j+1
                    continue
                dc_i[1].extend(dc_j[1])
                camera_deltas.pop(j)
                pass
            i = i+1
            pass

        best_camera_deltas = {}
        for dc in camera_deltas:
            (vector,pairs) = dc
            smallest_error = (None,None)
            for ijkl_pair in pairs:
                for ijkl in ijkl_pair:
                    (error, _) = camera_deltas_per_ijkl[ijkl]
                    if smallest_error is None or error<smallest_error:
                        smallest_error = (error, ijkl)
                        pass
                    pass
                pass
            print pairs
            print vector, smallest_error
            (error, ijkl)
            best_camera_deltas[ijkl] = (error, vector)
            pass

        if False:
            best_zs_guesses = []
            for r in results:
                (error, (ijkl, camera, orientation)) = r
                print "error, ijkl, camera, zs",error, ijkl, camera, guess_Z[ijkl]
                best_zs_guesses.append(guess_Z[ijkl])
                pass
            pass
        else:
            best_camera_deltas_list = []
            for ijkl in best_camera_deltas:
                (e,v) = best_camera_deltas[ijkl]
                best_camera_deltas_list.append((e,ijkl,v))
                pass
            best_zs_guesses = []
            def cmp_camera_deltas(x,y):
                if x[0]<y[0]: return -1
                return 1
            best_camera_deltas_list.sort(cmp=cmp_camera_deltas)
            for (e,ijkl,v) in best_camera_deltas_list:
                print e,ijkl,v
                best_zs_guesses.append(guess_Z[ijkl])
                pass
            pass

        print best_zs_guesses

        best_zs_results = []
        for gZ in best_zs_guesses:
            print "-"*80
            print "Looking for best of",gZ
            r = self.get_best_projection_for_guess_Z(O, Pe, uv, gZ, spread=1.05, iterations=5)
            if r is None:
                print "FAILED"
                pass
            else:
                (improved_projection, improved_z, max_error) = r
                print improved_projection, improved_z, max_error
                best_zs_results.append(r)
                if len(best_zs_results)>5:
                    break
                pass
            pass

        def cmp_results(a,b):
            if a[2]<b[2]: return -1
            return 1

        best_zs_results.sort(cmp=cmp_results)
        print best_zs_results
        for (proj,gZ,error) in best_zs_results:
            r = self.get_best_projection_for_guess_Z(O, Pe, uv, gZ, spread=math.pow(1.05,1/(1.5*(5-1))), iterations=10) #35)
            if r is None:
                continue
            print r
            (improved_projection, improved_z, max_error) = r
            improved_projection = {"camera":improved_projection["camera"],
                                   "orientation":improved_projection["orientation"],
                                   "fov":projection["fov"],
                                   "aspect":projection["aspect"],
                                   "zFar":projection["zFar"],
                                   }
            break
            
        opt_projection = improved_projection
        if True:
            print "Optimizing orientation (which is not refined yet)... delta scale 1"
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=1 )
            print "Optimizing orientation (which is not refined yet)... delta scale 0."
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=0.1 )
            print "Optimizing orientation (which is not refined yet)... delta scale 0.01"
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=0.01 )
            print "Optimizing orientation (which is not refined yet)... delta scale 0.001"
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=0.001 )
            pass

        print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(opt_projection))
        pts = object_guess_locations.keys()
        pts.sort()
        sum_d = 0
        for k in pts:
            (xyzw,uv) = self.image_of_model(object_guess_locations[k])
            d = vectors.vector_separation(uv,image_locations[k])
            sum_d += d
            print k, d, uv, image_locations[k]
            pass
        print "Total error",sum_d
        return
    #f pe_matrix_of_projection
    def pe_matrix_of_projection(self, projection=None):
        if projection is None:
            projection = self.projection
            pass

        fov    = projection["fov"]
        aspect = projection["aspect"]
        zFar   = projection["zFar"]
        zNear  = 1.0
        Pe = matrix.c_matrixNxN(data=[0.0]*16)
        f = 1.0/math.tan(fov*3.14159265/180.0/2)
        Pe[0,0] = f
        Pe[1,1] = f*aspect
        Pe[2,2] = -(zNear+zFar)/(zFar-zNear)
        Pe[2,3] = -2*zNear*zFar/(zFar-zNear)
        Pe[3,2] = -1.0
        return Pe
    #f blah
    def blah(self, pt_data, spread=1.15, iterations=5):
        """
        pt_data is list (pt_name, data_dict)
        data_dict has keys 'uv', 'xyz'
        """
        Pe = self.pe_matrix_of_projection()
        O  = matrix.c_matrixNxN(order=4)
        uv = []
        guess_Z = []
        for c in range(4):
            d = pt_data[c][1]
            O[0,c] = d["xyz"][0]
            O[1,c] = d["xyz"][1]
            O[2,c] = d["xyz"][2]
            O[3,c] = 1.0
            uv.append(d["uv"])
            guess_Z.append(d["xyzw"][2])
            pass
        r = self.get_best_projection_for_guess_Z(O=O, Pe=Pe, uv=uv, guess_Z=guess_Z, spread=spread, iterations=iterations)
        if r is None:
            print "FAILED"
            return
        (improved_projection, improved_z, max_error) = r
        print improved_projection, improved_z, max_error
        improved_projection = {"camera":improved_projection["camera"],
                               "orientation":improved_projection["orientation"],
                               "fov":self.projection["fov"],
                               "aspect":self.projection["aspect"],
                               "zFar":self.projection["zFar"],
                               }
        print "Setting projection to",improved_projection
        self.set_projection(improved_projection)
        return
    #f calculate_map_and_errors
    def calculate_map_and_errors(self, point_mappings):
        result = []
        pt_names = point_mappings.get_mapping_names()
        pt_names.sort()
        for pt in pt_names:
            xyz = point_mappings.get_xyz(pt)
            if xyz is None:
                continue
            (xyzw, img_xy) = self.image_of_model(xyz, perspective=False)
            uv = (xyzw[0]/xyzw[3], xyzw[1]/xyzw[3])
            mapping_uv = point_mappings.get_xy(pt,self.name)
            dist = None
            if mapping_uv is not None:
                dist = vectors.vector_separation(mapping_uv, uv)
                pass
            result.append((pt, {"uv":uv, "xyz":xyz, "xyzw":xyzw, "map_uv":mapping_uv, "error":dist}))
            pass
        return result
    #f guess_better_projection
    def guess_better_projection(self, point_mappings, base_projection, use_references=True, deltas_list=[{}], delta_scale=1.0, scale_error_weight=0.1, verbose=False):
        smallest_error = ({},10000,base_projection,1.0,1.0)
        for deltas in deltas_list:
            r = {}
            self.set_projection( projection=base_projection, deltas=deltas, delta_scale=delta_scale, resultant_projection=r )
            if verbose:
                print "\ngbp :", deltas, delta_scale, r
                pass
            (pts,e,corr) = self.calc_point_errors(point_mappings, point_mappings.get_mapping_names(),
                                                  use_references=use_references,
                                                  verbose=verbose)
            if pts>0:
                corr[0].add_entry(0.0,0.0)
                corr[1].add_entry(0.0,0.0)
                full_e = e
                #full_e += scale_error_weight*(1-corr[0].correlation_coefficient())
                #full_e += scale_error_weight*(1-corr[1].correlation_coefficient())
                #print "Total error",full_e,e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient()
                if full_e<smallest_error[1]:
                    smallest_error = (deltas,full_e,r)
                    pass
                pass
            pass
        if verbose:
            print "Smallest error",smallest_error
            print
            pass
        return (smallest_error[0], smallest_error[2])
    #f run_optimization
    def run_optimization(self, point_mappings, coarse=True):
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=500, orientation_iterations=100, camera_iterations=10, delta_scale=1 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=500, orientation_iterations=100, camera_iterations=10, delta_scale=0.1 )

        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=2000, orientation_iterations=1, camera_iterations=1, delta_scale=0.01, do_fov=True, do_camera=False )

        self.set_projection(opt_projection)

        if coarse:
            print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(opt_projection))
            return

        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=100, orientation_iterations=100, camera_iterations=10, delta_scale=0.05 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=200, orientation_iterations=100, camera_iterations=10, delta_scale=0.03 )
        #opt_projection = {'fov': 55, 'camera': [18.946400287962323, -22.74361538580119, 26.758691580937942], 'orientation': quaternion.c_quaternion(euler=(10.6165, 2.6457,50.3051),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 33.800000000000004}
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=200, orientation_iterations=100, camera_iterations=10, delta_scale=0.03 )
        #opt_projection = {'fov': 55, 'camera': [18.718700287962854, -22.75111538580117, 26.84179158093775], 'orientation': quaternion.c_quaternion(euler=(10.4051, 2.3963,50.1888),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 33.800000000000004}
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=2000, orientation_iterations=1, camera_iterations=1, delta_scale=0.001, do_fov=True, do_camera=False )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=100, camera_iterations=100, delta_scale=0.01 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=100, camera_iterations=100, delta_scale=0.003 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=100, camera_iterations=100, delta_scale=0.001 )

        self.set_projection(opt_projection)
        print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(opt_projection))
        pass
    #f optimize_projection
    def optimize_projection(self,
                            point_mappings,
                             use_references = True,
                             fov_iterations=10,
                             orientation_iterations=10,
                             camera_iterations=10,
                             delta_scale=0.05,
                            do_fov=False,
                            do_camera=True,
                             verbose=False):
        base_projection = self.projection
        for k in range(fov_iterations):
            (xsc,ysc)=(1.0,1.0)
            for i in range(camera_iterations):
                done = False
                for j in range(orientation_iterations):
                    (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.orientation_deltas, delta_scale=delta_scale, verbose=verbose)
                    base_projection = p
                    if len(d)==0:
                        #print "Oriented complete at",j,i
                        done = True
                        break
                    pass
                if done and do_camera:
                    (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.camera_deltas, delta_scale=delta_scale, scale_error_weight=0.1, verbose=verbose)
                    base_projection = p
                    if len(d)!=0: done=False
                    pass
                if done:
                    break
                pass
            if done and do_fov:
                (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.fov_deltas, delta_scale=delta_scale, verbose=verbose)
                base_projection = p
                if len(d)!=0: done=False
                pass
            if done:
                break
            pass
        (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, verbose=verbose)
        self.set_projection(base_projection)
        return base_projection
    #f All done
    pass

#a Toplevel
if __name__=="__main__":
    import image_point_mapping
    pm = image_point_mapping.c_point_mapping()
    image_name = "left"
    image_name = "middle"
    pm.load_data("pencils.map")
    pm.add_image(image_name,size=(3264.0,2448.0))
    proj = c_image_projection(image_name,"img_filename", size=(3264.0,2448.0))
    pm.set_projection(image_name,proj)
    proj.guess_initial_projection_matrix(point_mappings = pm)
    pass
