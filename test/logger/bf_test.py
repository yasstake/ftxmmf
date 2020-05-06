import unittest
from logger.bf import *

PARTIAL='''{'mid_price': 941447.0, 'bids': [{'price': 941434.0, 'size': 0.03}, {'price': 941359.0, 'size': 0.05}, {'price': 941286.0, 'size': 0.5}, {'price': 941285.0, 'size': 0.0105}, {'price': 941269.0, 'size': 0.06}, {'price': 941239.0, 'size': 1.08276634}, {'price': 941224.0, 'size': 0.01}, {'price': 941215.0, 'size': 0.50000013}, {'price': 941212.0, 'size': 0.04345}, {'price': 941201.0, 'size': 0.05}, {'price': 941195.0, 'size': 0.01777948}, {'price': 941193.0, 'size': 0.12053788}, {'price': 941171.0, 'size': 1.02}, {'price': 941167.0, 'size': 0.0141}, {'price': 941165.0, 'size': 0.1}, {'price': 941163.0, 'size': 0.01777948}, {'price': 941162.0, 'size': 1.0100084}, {'price': 941161.0, 'size': 0.09498813}, {'price': 941140.0, 'size': 0.1}, {'price': 941124.0, 'size': 0.2}, {'price': 941090.0, 'size': 0.20210435}, {'price': 941088.0, 'size': 0.3}, {'price': 941025.0, 'size': 0.01}, {'price': 941004.0, 'size': 0.02}, {'price': 941003.0, 'size': 0.03}, {'price': 941002.0, 'size': 0.07}, {'price': 941000.0, 'size': 2.0}, {'price': 940970.0, 'size': 0.2}, {'price': 940954.0, 'size': 0.2}, {'price': 940910.0, 'size': 0.02}, {'price': 940880.0, 'size': 0.3}, {'price': 940875.0, 'size': 0.1029}, {'price': 940869.0, 'size': 0.3}, {'price': 940782.0, 'size': 0.06}, {'price': 940778.0, 'size': 0.15}, {'price': 940765.0, 'size': 0.01}, {'price': 940738.0, 'size': 0.25}, {'price': 940665.0, 'size': 0.3}, {'price': 940653.0, 'size': 0.06142039}, {'price': 940652.0, 'size': 1.0}, {'price': 940487.0, 'size': 0.3}, {'price': 940479.0, 'size': 0.03}, {'price': 940412.0, 'size': 0.17}, {'price': 940405.0, 'size': 0.05704211}, {'price': 940404.0, 'size': 0.01}, {'price': 940403.0, 'size': 0.287288}, {'price': 940402.0, 'size': 0.20538828}, {'price': 940401.0, 'size': 0.28727474}, {'price': 940397.0, 'size': 0.30461165}, {'price': 940396.0, 'size': 0.26131642}, {'price': 940395.0, 'size': 0.00754003}, {'price': 940391.0, 'size': 0.2}, {'price': 940390.0, 'size': 0.25}, {'price': 940388.0, 'size': 0.37}, {'price': 940387.0, 'size': 0.05}, {'price': 940382.0, 'size': 0.17}, {'price': 940380.0, 'size': 0.15}, {'price': 940355.0, 'size': 0.0296}, {'price': 940329.0, 'size': 0.05}, {'price': 940321.0, 'size': 0.34}, {'price': 940276.0, 'size': 0.0151}, {'price': 940275.0, 'size': 0.01}, {'price': 940262.0, 'size': 0.9}, {'price': 940257.0, 'size': 0.01}, {'price': 940250.0, 'size': 0.5}, {'price': 940249.0, 'size': 0.3}, {'price': 940236.0, 'size': 0.02}, {'price': 940172.0, 'size': 0.3}, {'price': 940169.0, 'size': 1.0}, {'price': 940145.0, 'size': 0.35}, {'price': 940111.0, 'size': 0.01}, {'price': 940104.0, 'size': 0.1}, {'price': 940099.0, 'size': 0.07}, {'price': 940097.0, 'size': 0.04}, {'price': 940057.0, 'size': 0.01}, {'price': 940028.0, 'size': 0.01}, {'price': 940004.0, 'size': 0.01}, {'price': 940003.0, 'size': 20.2}, {'price': 940001.0, 'size': 1.1}, {'price': 940000.0, 'size': 2.85}, {'price': 939963.0, 'size': 1.8691}, {'price': 939951.0, 'size': 0.02}, {'price': 939932.0, 'size': 0.6}, {'price': 939900.0, 'size': 0.5}, {'price': 939810.0, 'size': 1.008}, {'price': 939739.0, 'size': 1.008}, {'price': 939700.0, 'size': 0.3}, {'price': 939693.0, 'size': 0.02}, {'price': 939686.0, 'size': 3.0}, {'price': 939639.0, 'size': 0.0279}, {'price': 939638.0, 'size': 0.1}, {'price': 939618.0, 'size': 0.03}, {'price': 939610.0, 'size': 0.0251}, {'price': 939579.0, 'size': 0.0151}, {'price': 939569.0, 'size': 0.1}, {'price': 939568.0, 'size': 0.5}, {'price': 939544.0, 'size': 2.522}, {'price': 939512.0, 'size': 0.03}, {'price': 939485.0, 'size': 1.0}, {'price': 939452.0, 'size': 0.03}, {'price': 939442.0, 'size': 0.017}, {'price': 939424.0, 'size': 0.01}, {'price': 939417.0, 'size': 1.008}, {'price': 939366.0, 'size': 0.02}, {'price': 939311.0, 'size': 0.02703704}, {'price': 939176.0, 'size': 1.9799}, {'price': 939171.0, 'size': 0.01}, {'price': 939158.0, 'size': 1.008}, {'price': 939126.0, 'size': 0.025}, {'price': 939096.0, 'size': 0.01906704}, {'price': 939079.0, 'size': 1.0}, {'price': 939064.0, 'size': 0.02216033}, {'price': 939049.0, 'size': 0.12}, {'price': 939002.0, 'size': 0.025}, {'price': 939001.0, 'size': 1.0}, {'price': 939000.0, 'size': 2.0}, {'price': 938897.0, 'size': 0.02}, {'price': 938837.0, 'size': 0.02703704}, {'price': 938825.0, 'size': 0.01906704}, {'price': 938800.0, 'size': 0.15792024}, {'price': 938779.0, 'size': 0.02}, {'price': 938778.0, 'size': 0.0914503}, {'price': 938769.0, 'size': 0.017}, {'price': 938739.0, 'size': 0.3}, {'price': 938700.0, 'size': 0.03}, {'price': 938697.0, 'size': 0.02}, {'price': 938696.0, 'size': 0.02}, {'price': 938669.0, 'size': 0.2}, {'price': 938666.0, 'size': 0.01}, {'price': 938656.0, 'size': 0.3}, {'price': 938650.0, 'size': 5.5}, {'price': 938638.0, 'size': 0.02}, {'price': 938637.0, 'size': 0.1}, {'price': 938618.0, 'size': 0.03}, {'price': 938613.0, 'size': 0.1}, {'price': 938600.0, 'size': 0.1}, {'price': 938598.0, 'size': 0.01}, {'price': 938591.0, 'size': 0.135}, {'price': 938588.0, 'size': 2.0}, {'price': 938550.0, 'size': 0.1}, {'price': 938549.0, 'size': 0.21}, {'price': 938542.0, 'size': 0.01906704}, {'price': 938528.0, 'size': 0.0114503}, {'price': 938516.0, 'size': 0.01691506}, {'price': 938515.0, 'size': 0.01}, {'price': 938503.0, 'size': 0.589}, {'price': 938500.0, 'size': 0.64}, {'price': 938482.0, 'size': 0.01}, {'price': 938477.0, 'size': 1.5}, {'price': 938471.0, 'size': 0.01}, {'price': 938450.0, 'size': 1.0}, {'price': 938425.0, 'size': 0.3}, {'price': 938419.0, 'size': 0.28}, {'price': 938406.0, 'size': 2.7426}, {'price': 938393.0, 'size': 0.7}, {'price': 938361.0, 'size': 0.0151}, {'price': 938343.0, 'size': 0.01691506}, {'price': 938305.0, 'size': 0.135}, {'price': 938300.0, 'size': 0.2}, {'price': 938299.0, 'size': 0.02}, {'price': 938296.0, 'size': 0.1}, {'price': 938290.0, 'size': 2.524}, {'price': 938274.0, 'size': 0.02}, {'price': 938255.0, 'size': 0.01}, {'price': 938246.0, 'size': 0.01}, {'price': 938240.0, 'size': 0.05}, {'price': 938231.0, 'size': 0.0151}, {'price': 938225.0, 'size': 0.337}, {'price': 938183.0, 'size': 0.135}, {'price': 938129.0, 'size': 0.0252}, {'price': 938121.0, 'size': 0.022}, {'price': 938100.0, 'size': 0.02906704}, {'price': 938093.0, 'size': 0.05}, {'price': 938070.0, 'size': 0.01}, {'price': 938010.0, 'size': 0.3}, {'price': 938003.0, 'size': 0.135}, {'price': 938000.0, 'size': 2.584}, {'price': 937994.0, 'size': 0.01134674}, {'price': 937919.0, 'size': 0.3}, {'price': 937909.0, 'size': 0.01}, {'price': 937896.0, 'size': 0.3}, {'price': 937884.0, 'size': 0.866}, {'price': 937841.0, 'size': 0.1}, {'price': 937805.0, 'size': 1.276}, {'price': 937803.0, 'size': 0.7}, {'price': 937779.0, 'size': 0.02}, {'price': 937762.0, 'size': 0.01068}, {'price': 937748.0, 'size': 0.01068}, {'price': 937741.0, 'size': 0.02}, {'price': 937733.0, 'size': 0.01}, {'price': 937695.0, 'size': 0.4}, {'price': 937677.0, 'size': 0.02532306}, {'price': 937676.0, 'size': 0.02532306}, {'price': 937644.0, 'size': 0.14}, {'price': 937577.0, 'size': 1.5}, {'price': 937574.0, 'size': 0.18}, {'price': 937550.0, 'size': 0.4}, {'price': 937531.0, 'size': 0.059125}, {'price': 937524.0, 'size': 0.635}, {'price': 937494.0, 'size': 0.02532306}, {'price': 937471.0, 'size': 0.01}, {'price': 937466.0, 'size': 0.01}, {'price': 937463.0, 'size': 0.2}, {'price': 937435.0, 'size': 1.2}, {'price': 937401.0, 'size': 0.1}, {'price': 937390.0, 'size': 0.12073577}, {'price': 937341.0, 'size': 0.3}, {'price': 937251.0, 'size': 0.7}, {'price': 937224.0, 'size': 0.4}, {'price': 937223.0, 'size': 1.0}, {'price': 937222.0, 'size': 0.01}, {'price': 937221.0, 'size': 0.02}, {'price': 937174.0, 'size': 2.525}, {'price': 937136.0, 'size': 0.0151}, {'price': 937127.0, 'size': 2.527}, {'price': 937111.0, 'size': 0.01}, {'price': 937069.0, 'size': 0.8}, {'price': 937064.0, 'size': 0.05}, {'price': 937061.0, 'size': 0.01}, {'price': 937010.0, 'size': 0.3}, {'price': 937000.0, 'size': 0.07}, {'price': 936950.0, 'size': 0.7}, {'price': 936942.0, 'size': 0.888}, {'price': 936905.0, 'size': 0.5}, {'price': 936898.0, 'size': 0.01}, {'price': 936850.0, 'size': 0.2}, {'price': 936810.0, 'size': 0.01068}, {'price': 936782.0, 'size': 0.0300625}, {'price': 936779.0, 'size': 0.02}, {'price': 936777.0, 'size': 0.5}, {'price': 936747.0, 'size': 0.5}, {'price': 936746.0, 'size': 0.05}, {'price': 936713.0, 'size': 0.03958333}, {'price': 936699.0, 'size': 0.0300625}, {'price': 936683.0, 'size': 0.5}, {'price': 936662.0, 'size': 0.0151}, {'price': 936660.0, 'size': 0.2}, {'price': 936639.0, 'size': 0.02}, {'price': 936620.0, 'size': 0.58}, {'price': 936595.0, 'size': 0.059125}, {'price': 936559.0, 'size': 0.03}, {'price': 936515.0, 'size': 0.01}, {'price': 936500.0, 'size': 0.03}, {'price': 936487.0, 'size': 0.1}, {'price': 936471.0, 'size': 0.71}, {'price': 936469.0, 'size': 0.85}, {'price': 936440.0, 'size': 0.1}, {'price': 936402.0, 'size': 0.0300625}, {'price': 936389.0, 'size': 0.03958333}, {'price': 936373.0, 'size': 0.05}, {'price': 936363.0, 'size': 0.05}, {'price': 936362.0, 'size': 0.25}, {'price': 936350.0, 'size': 0.2}, {'price': 936272.0, 'size': 0.3}, {'price': 936235.0, 'size': 0.01}, {'price': 936234.0, 'size': 0.01}, {'price': 936231.0, 'size': 0.5}, {'price': 936202.0, 'size': 0.33}, {'price': 936200.0, 'size': 4.1}, {'price': 936160.0, 'size': 1.0}, {'price': 936150.0, 'size': 0.48}, {'price': 936126.0, 'size': 0.1}, {'price': 936124.0, 'size': 0.02}, {'price': 936100.0, 'size': 0.01}, {'price': 936099.0, 'size': 0.045}, {'price': 936066.0, 'size': 0.1}, {'price': 936058.0, 'size': 0.01}, {'price': 936010.0, 'size': 0.3}, {'price': 936000.0, 'size': 1.034}, {'price': 935978.0, 'size': 0.0151}, {'price': 935941.0, 'size': 0.0151}, {'price': 935919.0, 'size': 0.7}, {'price': 935903.0, 'size': 0.5}, {'price': 935893.0, 'size': 0.1}, {'price': 935866.0, 'size': 0.02}, {'price': 935859.0, 'size': 0.12}, {'price': 935814.0, 'size': 0.33}, {'price': 935806.0, 'size': 0.01}, {'price': 935779.0, 'size': 0.02}, {'price': 935777.0, 'size': 0.5}, {'price': 935755.0, 'size': 0.5}, {'price': 935729.0, 'size': 0.05}, {'price': 935694.0, 'size': 0.03958333}, {'price': 935661.0, 'size': 0.4}, {'price': 935658.0, 'size': 0.03958333}, {'price': 935656.0, 'size': 0.01}, {'price': 935652.0, 'size': 0.3}, {'price': 935650.0, 'size': 0.7}, {'price': 935577.0, 'size': 1.5}, {'price': 935555.0, 'size': 6.05}, {'price': 935551.0, 'size': 0.01068}, {'price': 935540.0, 'size': 0.6}, {'price': 935500.0, 'size': 0.3}, {'price': 935497.0, 'size': 0.1}, {'price': 935471.0, 'size': 0.04958333}, {'price': 935450.0, 'size': 0.2}, {'price': 935446.0, 'size': 2.74}, {'price': 935434.0, 'size': 0.03958333}, {'price': 935432.0, 'size': 0.02}, {'price': 935425.0, 'size': 0.7}], 'asks': [{'price': 941461.0, 'size': 0.18152344}, {'price': 941484.0, 'size': 0.02}, {'price': 941541.0, 'size': 0.02}, {'price': 941542.0, 'size': 0.06}, {'price': 941554.0, 'size': 0.0151}, {'price': 941559.0, 'size': 0.1}, {'price': 941560.0, 'size': 0.3}, {'price': 941690.0, 'size': 0.0392}, {'price': 941692.0, 'size': 0.54}, {'price': 941693.0, 'size': 0.5}, {'price': 941714.0, 'size': 0.01}, {'price': 941729.0, 'size': 0.1}, {'price': 941734.0, 'size': 0.3}, {'price': 941737.0, 'size': 0.02}, {'price': 941776.0, 'size': 0.03}, {'price': 941785.0, 'size': 0.12083374}, {'price': 941787.0, 'size': 0.15}, {'price': 941789.0, 'size': 0.01}, {'price': 941799.0, 'size': 0.1}, {'price': 941800.0, 'size': 0.1}, {'price': 941805.0, 'size': 0.03093296}, {'price': 941838.0, 'size': 0.0151}, {'price': 941847.0, 'size': 0.01}, {'price': 941848.0, 'size': 1.267288}, {'price': 941851.0, 'size': 0.06}, {'price': 941854.0, 'size': 0.2}, {'price': 941855.0, 'size': 0.26131642}, {'price': 941860.0, 'size': 0.34}, {'price': 941862.0, 'size': 0.9}, {'price': 941865.0, 'size': 0.25}, {'price': 941866.0, 'size': 0.01}, {'price': 941867.0, 'size': 0.21}, {'price': 941874.0, 'size': 0.3}, {'price': 941877.0, 'size': 0.05}, {'price': 941880.0, 'size': 0.5}, {'price': 941893.0, 'size': 0.5}, {'price': 941904.0, 'size': 0.13}, {'price': 941926.0, 'size': 0.37980267}, {'price': 941932.0, 'size': 0.02}, {'price': 941939.0, 'size': 0.03}, {'price': 941941.0, 'size': 0.31}, {'price': 941963.0, 'size': 0.1}, {'price': 941967.0, 'size': 0.44228517}, {'price': 941969.0, 'size': 0.43}, {'price': 941971.0, 'size': 0.05}, {'price': 941976.0, 'size': 0.0220731}, {'price': 941996.0, 'size': 0.02375}, {'price': 941997.0, 'size': 0.02375}, {'price': 942000.0, 'size': 3.0}, {'price': 942033.0, 'size': 0.66}, {'price': 942037.0, 'size': 0.3}, {'price': 942040.0, 'size': 0.04}, {'price': 942041.0, 'size': 0.0385497}, {'price': 942050.0, 'size': 0.643}, {'price': 942065.0, 'size': 0.08}, {'price': 942076.0, 'size': 0.0423}, {'price': 942088.0, 'size': 0.03093296}, {'price': 942112.0, 'size': 0.33419865}, {'price': 942113.0, 'size': 0.06}, {'price': 942116.0, 'size': 0.07}, {'price': 942127.0, 'size': 0.06}, {'price': 942137.0, 'size': 0.1}, {'price': 942162.0, 'size': 0.39789565}, {'price': 942167.0, 'size': 0.01}, {'price': 942170.0, 'size': 0.0305731}, {'price': 942175.0, 'size': 0.4}, {'price': 942188.0, 'size': 0.2}, {'price': 942190.0, 'size': 0.357}, {'price': 942191.0, 'size': 0.05125}, {'price': 942192.0, 'size': 0.2}, {'price': 942195.0, 'size': 0.2}, {'price': 942197.0, 'size': 0.2}, {'price': 942205.0, 'size': 0.07}, {'price': 942214.0, 'size': 0.06}, {'price': 942216.0, 'size': 0.07}, {'price': 942219.0, 'size': 0.07}, {'price': 942229.0, 'size': 0.0481}, {'price': 942246.0, 'size': 0.2}, {'price': 942299.0, 'size': 0.47478683}, {'price': 942301.0, 'size': 0.1}, {'price': 942302.0, 'size': 0.337}, {'price': 942313.0, 'size': 0.1}, {'price': 942320.0, 'size': 0.2}, {'price': 942322.0, 'size': 0.02}, {'price': 942327.0, 'size': 0.02783967}, {'price': 942329.0, 'size': 1.4}, {'price': 942330.0, 'size': 0.01}, {'price': 942333.0, 'size': 0.2}, {'price': 942341.0, 'size': 0.07}, {'price': 942344.0, 'size': 0.05}, {'price': 942345.0, 'size': 0.01}, {'price': 942359.0, 'size': 0.03093296}, {'price': 942400.0, 'size': 0.05}, {'price': 942401.0, 'size': 0.03}, {'price': 942403.0, 'size': 0.05125}, {'price': 942404.0, 'size': 0.017}, {'price': 942424.0, 'size': 0.01}, {'price': 942431.0, 'size': 0.02}, {'price': 942450.0, 'size': 0.05}, {'price': 942460.0, 'size': 0.01}, {'price': 942462.0, 'size': 0.78}, {'price': 942463.0, 'size': 0.20538828}, {'price': 942464.0, 'size': 0.06}, {'price': 942465.0, 'size': 0.10461165}, {'price': 942479.0, 'size': 0.78}, {'price': 942480.0, 'size': 0.06}, {'price': 942482.0, 'size': 0.017}, {'price': 942494.0, 'size': 0.28727474}, {'price': 942498.0, 'size': 1.98}, {'price': 942513.0, 'size': 0.78}, {'price': 942518.0, 'size': 0.98}, {'price': 942537.0, 'size': 0.337}, {'price': 942539.0, 'size': 0.17293751}, {'price': 942550.0, 'size': 1.0}, {'price': 942552.0, 'size': 0.2}, {'price': 942564.0, 'size': 0.01}, {'price': 942571.0, 'size': 0.02}, {'price': 942579.0, 'size': 0.1}, {'price': 942585.0, 'size': 0.025}, {'price': 942599.0, 'size': 0.05125}, {'price': 942603.0, 'size': 0.18}, {'price': 942611.0, 'size': 0.017}, {'price': 942615.0, 'size': 0.07}, {'price': 942618.0, 'size': 0.07}, {'price': 942621.0, 'size': 0.07}, {'price': 942624.0, 'size': 0.02}, {'price': 942630.0, 'size': 0.19818292}, {'price': 942631.0, 'size': 0.3}, {'price': 942634.0, 'size': 0.25}, {'price': 942641.0, 'size': 0.11896296}, {'price': 942650.0, 'size': 1.0}, {'price': 942654.0, 'size': 0.01}, {'price': 942656.0, 'size': 0.09}, {'price': 942658.0, 'size': 0.017}, {'price': 942667.0, 'size': 0.13778683}, {'price': 942670.0, 'size': 0.05}, {'price': 942671.0, 'size': 0.19818292}, {'price': 942674.0, 'size': 0.15}, {'price': 942684.0, 'size': 0.02}, {'price': 942691.0, 'size': 0.17773315}, {'price': 942712.0, 'size': 0.2}, {'price': 942717.0, 'size': 0.15}, {'price': 942724.0, 'size': 0.066}, {'price': 942738.0, 'size': 0.01}, {'price': 942742.0, 'size': 0.02308494}, {'price': 942765.0, 'size': 0.5}, {'price': 942775.0, 'size': 0.234}, {'price': 942780.0, 'size': 0.02308494}, {'price': 942796.0, 'size': 2.0}, {'price': 942802.0, 'size': 0.22633333}, {'price': 942824.0, 'size': 0.04}, {'price': 942830.0, 'size': 0.2}, {'price': 942848.0, 'size': 0.32}, {'price': 942852.0, 'size': 0.557}, {'price': 942859.0, 'size': 0.45747801}, {'price': 942892.0, 'size': 0.05}, {'price': 942923.0, 'size': 0.01}, {'price': 942925.0, 'size': 0.36}, {'price': 942940.0, 'size': 0.03691394}, {'price': 942977.0, 'size': 0.2}, {'price': 942980.0, 'size': 0.02}, {'price': 942983.0, 'size': 0.33}, {'price': 943000.0, 'size': 2.53}, {'price': 943001.0, 'size': 0.13778683}, {'price': 943005.0, 'size': 0.017}, {'price': 943008.0, 'size': 0.02}, {'price': 943011.0, 'size': 0.146}, {'price': 943013.0, 'size': 0.05}, {'price': 943041.0, 'size': 0.01}, {'price': 943042.0, 'size': 0.27471}, {'price': 943043.0, 'size': 0.1}, {'price': 943048.0, 'size': 0.234}, {'price': 943052.0, 'size': 0.1}, {'price': 943055.0, 'size': 0.274719}, {'price': 943073.0, 'size': 0.08}, {'price': 943084.0, 'size': 0.234}, {'price': 943110.0, 'size': 0.08}, {'price': 943121.0, 'size': 0.03}, {'price': 943122.0, 'size': 0.4}, {'price': 943128.0, 'size': 0.13}, {'price': 943137.0, 'size': 0.017}, {'price': 943140.0, 'size': 0.2}, {'price': 943143.0, 'size': 0.19540837}, {'price': 943166.0, 'size': 0.02}, {'price': 943167.0, 'size': 0.2}, {'price': 943175.0, 'size': 0.05}, {'price': 943184.0, 'size': 0.09}, {'price': 943188.0, 'size': 0.06}, {'price': 943192.0, 'size': 0.07}, {'price': 943196.0, 'size': 0.025}, {'price': 943199.0, 'size': 0.06}, {'price': 943201.0, 'size': 0.07}, {'price': 943213.0, 'size': 0.1}, {'price': 943289.0, 'size': 0.33}, {'price': 943290.0, 'size': 0.2}, {'price': 943333.0, 'size': 0.36}, {'price': 943340.0, 'size': 0.045}, {'price': 943371.0, 'size': 0.2}, {'price': 943381.0, 'size': 0.108}, {'price': 943400.0, 'size': 2.0}, {'price': 943411.0, 'size': 0.0329375}, {'price': 943414.0, 'size': 0.05}, {'price': 943427.0, 'size': 0.108}, {'price': 943435.0, 'size': 3.0}, {'price': 943441.0, 'size': 0.01}, {'price': 943446.0, 'size': 0.05}, {'price': 943455.0, 'size': 0.03}, {'price': 943481.0, 'size': 0.14047798}, {'price': 943488.0, 'size': 0.05}, {'price': 943505.0, 'size': 0.05}, {'price': 943526.0, 'size': 0.12}, {'price': 943534.0, 'size': 0.11}, {'price': 943537.0, 'size': 0.022}, {'price': 943541.0, 'size': 0.06}, {'price': 943542.0, 'size': 0.06}, {'price': 943563.0, 'size': 0.05}, {'price': 943578.0, 'size': 0.6}, {'price': 943588.0, 'size': 0.03}, {'price': 943600.0, 'size': 0.01}, {'price': 943617.0, 'size': 0.36}, {'price': 943619.0, 'size': 0.05835754}, {'price': 943633.0, 'size': 1.0}, {'price': 943650.0, 'size': 0.01}, {'price': 943687.0, 'size': 0.07}, {'price': 943689.0, 'size': 0.234}, {'price': 943703.0, 'size': 0.0423}, {'price': 943708.0, 'size': 0.0329375}, {'price': 943723.0, 'size': 0.5}, {'price': 943731.0, 'size': 2.0}, {'price': 943734.0, 'size': 0.13782393}, {'price': 943744.0, 'size': 1.5}, {'price': 943757.0, 'size': 0.02}, {'price': 943774.0, 'size': 0.01}, {'price': 943791.0, 'size': 0.0329375}, {'price': 943800.0, 'size': 1.0}, {'price': 943830.0, 'size': 0.01}, {'price': 943832.0, 'size': 0.03}, {'price': 943855.0, 'size': 0.13}, {'price': 943870.0, 'size': 0.2}, {'price': 943911.0, 'size': 0.05835754}, {'price': 943913.0, 'size': 0.0151}, {'price': 943917.0, 'size': 0.135}, {'price': 943922.0, 'size': 0.0151}, {'price': 943930.0, 'size': 0.01}, {'price': 943952.0, 'size': 0.03}, {'price': 943958.0, 'size': 0.3}, {'price': 943959.0, 'size': 0.09}, {'price': 943969.0, 'size': 0.02}, {'price': 943975.0, 'size': 0.05}, {'price': 943988.0, 'size': 0.1}, {'price': 943996.0, 'size': 2.4149}, {'price': 944001.0, 'size': 0.135}, {'price': 944037.0, 'size': 0.31}, {'price': 944041.0, 'size': 0.21}, {'price': 944073.0, 'size': 0.37688363}, {'price': 944095.0, 'size': 2.0}, {'price': 944098.0, 'size': 0.23156011}, {'price': 944118.0, 'size': 0.3}, {'price': 944120.0, 'size': 0.01}, {'price': 944165.0, 'size': 0.02}, {'price': 944171.0, 'size': 0.01852315}, {'price': 944181.0, 'size': 0.01}, {'price': 944199.0, 'size': 0.05835754}, {'price': 944233.0, 'size': 0.135}, {'price': 944258.0, 'size': 0.3}, {'price': 944259.0, 'size': 0.01}, {'price': 944272.0, 'size': 0.17008735}, {'price': 944275.0, 'size': 0.1}, {'price': 944278.0, 'size': 0.01}, {'price': 944321.0, 'size': 0.05835754}, {'price': 944346.0, 'size': 2.504}, {'price': 944383.0, 'size': 0.5}, {'price': 944400.0, 'size': 1.0}, {'price': 944464.0, 'size': 0.02}, {'price': 944517.0, 'size': 0.3}, {'price': 944519.0, 'size': 0.135}, {'price': 944527.0, 'size': 0.3}, {'price': 944538.0, 'size': 0.13782}, {'price': 944561.0, 'size': 0.3}, {'price': 944562.0, 'size': 0.01}, {'price': 944594.0, 'size': 0.01}, {'price': 944596.0, 'size': 0.27461641}, {'price': 944617.0, 'size': 0.1378239}, {'price': 944634.0, 'size': 0.01}, {'price': 944649.0, 'size': 0.01}, {'price': 944660.0, 'size': 0.01}, {'price': 944664.0, 'size': 1.0}, {'price': 944668.0, 'size': 0.08}, {'price': 944700.0, 'size': 0.4}, {'price': 944753.0, 'size': 0.410745}, {'price': 944784.0, 'size': 1.003}, {'price': 944800.0, 'size': 1.1}, {'price': 944813.0, 'size': 0.51621043}, {'price': 944847.0, 'size': 0.01}, {'price': 944856.0, 'size': 0.05}, {'price': 944863.0, 'size': 1.9254}, {'price': 944876.0, 'size': 0.03}, {'price': 944916.0, 'size': 1.002}, {'price': 944917.0, 'size': 0.04}, {'price': 944950.0, 'size': 0.2}]}'''
UPDATE='''
{'mid_price': 941615.0, 'bids': [{'price': 941213.0, 'size': 0.50000013}, {'price': 940879.0, 'size': 0.01}, {'price': 938461.0, 'size': 0.833}, {'price': 941663.0, 'size': 0.0}, {'price': 941004.0, 'size': 0.02}, {'price': 941172.0, 'size': 1.00000013}, {'price': 940485.0, 'size': 0.0}, {'price': 938116.0, 'size': 0.85}, {'price': 941658.0, 'size': 0.0}, {'price': 941647.0, 'size': 0.0}, {'price': 941691.0, 'size': 0.0}, {'price': 940390.0, 'size': 0.0}, {'price': 939450.0, 'size': 0.21}], 'asks': [{'price': 942920.0, 'size': 0.78}, {'price': 942400.0, 'size': 0.05}, {'price': 941647.0, 'size': 0.96667309}, {'price': 948049.0, 'size': 0.50000013}, {'price': 942796.0, 'size': 0.0}, {'price': 941865.0, 'size': 0.0}]}
'''
EXECUTE='''
[{'id': 1710560088, 'side': 'SELL', 'price': 941869.0, 'size': 0.06, 'exec_date': '2020-04-30T12:51:56.7845897Z', 'buy_child_order_acceptance_id': 'JRF20200430-125156-411150', 'sell_child_order_acceptance_id': 'JRF20200430-125156-635209'}]
'''

class MyTestCase(unittest.TestCase):
    def test_partial_messge(self):
        c = BfClient()
        pm = c._board_message_to_csv(PARTIAL, CHANNEL_BOARD_SNAPSHOT)
        print(pm)

    def test_updat_messge(self):
        c = BfClient()
        pm = c._board_message_to_csv(UPDATE, CHANNEL_BOARD)
        print(pm)

    def test_execute_message(self):
        c = BfClient()
        pm = c._trade_message_to_csv(EXECUTE)
        print(pm)

if __name__ == '__main__':
    unittest.main()