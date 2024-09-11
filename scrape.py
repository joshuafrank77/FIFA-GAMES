import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


# Dictionary mapping league names to URLs
league_urls = [
    ("Legends Around the World","https://tmssl.akamaized.net//images/wappen/normquad/123.png"),
    ( "England Premier League",  "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1"),
    ( "Moldova Super Liga",  "https://www.transfermarkt.com/super-liga/startseite/wettbewerb/MO1N"),
    ( "Spain La Liga","https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1" ),
    ("Italy Serie A","https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1" ),
    ("Germany Bundesliga","https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1"), 
    ("France Ligue 1", "https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1" ),
    ("Portugal Liga Portugal","https://www.transfermarkt.com/liga-portugal/startseite/wettbewerb/PO1"), 
    ("Netherlands Eredivise", "https://www.transfermarkt.com/eredivisie/startseite/wettbewerb/NL1"),
    ("Turkey Super Lig", "https://www.transfermarkt.com/super-lig/startseite/wettbewerb/TR1"),
    ("Russia Premier Liga", "https://www.transfermarkt.com/premier-liga/startseite/wettbewerb/RU1"),
    ("Belgium Jupiler Pro League","https://www.transfermarkt.com/jupiler-pro-league/startseite/wettbewerb/BE1"), 
    ("Greece Super League 1", "https://www.transfermarkt.com/super-league-1/startseite/wettbewerb/GR1"),
    ("Austria Bundesliga", "https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/A1"),
    ("Ukraine Premier Liga", "https://www.transfermarkt.com/premier-liga/startseite/wettbewerb/UKR1"),
    ("Switzerland Super League", "https://www.transfermarkt.com/super-league/startseite/wettbewerb/C1"),
    ("Denmark Superliga", "https://www.transfermarkt.com/superliga/startseite/wettbewerb/DK1"),
    ("Czech Republic Chance Liga","https://www.transfermarkt.com/chance-liga/startseite/wettbewerb/TS1"), 
    ("Scotland Premiership", "https://www.transfermarkt.com/scottish-premiership/startseite/wettbewerb/SC1"),
    ("Serbia Super liga Srbije", "https://www.transfermarkt.com/super-liga-srbije/startseite/wettbewerb/SER1"),
    ("Poland Ekstraklasa","https://www.transfermarkt.com/pko-bp-ekstraklasa/startseite/wettbewerb/PL1"),
    ("Croatia SuperSport HNL", "https://www.transfermarkt.com/supersport-hnl/startseite/wettbewerb/KR1"),
    ("Sweden Allsvenskan", "https://www.transfermarkt.com/allsvenskan/startseite/wettbewerb/SE1"),
    ("Norway Eliteserien", "https://www.transfermarkt.com/eliteserien/startseite/wettbewerb/NO1"),
    ("Romania SuperLiga", "https://www.transfermarkt.com/superliga/startseite/wettbewerb/RO1"),
    ("Bulgaria efbet Liga", "https://www.transfermarkt.com/efbet-liga/startseite/wettbewerb/BU1"),
    ("Hungary NB I.", "https://www.transfermarkt.com/nemzeti-bajnoksag/startseite/wettbewerb/UNG1"),
    ("Cyprus Protahlima Cyta","https://www.transfermarkt.com/protathlima-cyta/startseite/wettbewerb/ZYP1"), 
    ("Israel Ligat ha'Al", "https://www.transfermarkt.com/ligat-haal/startseite/wettbewerb/ISR1"),
    ("Slovakia Nike Liga", "https://www.transfermarkt.com/nike-liga/startseite/wettbewerb/SLO1"),
    ("Azerbaijan Premyer Liqa", "https://www.transfermarkt.com/premyer-liqa/startseite/wettbewerb/AZ1"),
    ("Khazakstan Premier Liga", "https://www.transfermarkt.com/premier-liga/startseite/wettbewerb/KAS1"),
    ("Bosnia-Herzegovina Premijer Liga BiH","https://www.transfermarkt.com/premijer-liga-bosne-i-hercegovine/startseite/wettbewerb/BOS1"), 
    ("Belarus Vysheyshaya Liga", "https://www.transfermarkt.com/vysheyshaya-liga/startseite/wettbewerb/WER1"),
    ("Slovenia Prva Liga", "https://www.transfermarkt.com/prva-liga/startseite/wettbewerb/SL1"),
    ("Lithuania A Lyga", "https://www.transfermarkt.com/a-lyga/startseite/wettbewerb/LI1"),
    ("Finland Veikkausliiga", "https://www.transfermarkt.com/veikkausliiga/startseite/wettbewerb/FI1"),
    ("Latvia Virsliga", "https://www.transfermarkt.com/virsliga/startseite/wettbewerb/LET1"),
    ("Armenia Bardzraguyn khumb","https://www.transfermarkt.com/bardzraguyn-khumb/startseite/wettbewerb/ARM1"), 
    ("Albania Kategoria Superiore", "https://www.transfermarkt.com/kategoria-superiore/startseite/wettbewerb/ALB1"),
    ("North Macedonia Prva liga", "https://www.transfermarkt.com/prva-makedonska-fudbalska-liga/startseite/wettbewerb/MAZ1"),
    ("Georgia Erovnuli Liga", "https://www.transfermarkt.com/erovnuli-liga/startseite/wettbewerb/GE1N"),
    ("Kosovo Superliga e Kosovës", "https://www.transfermarkt.com/superliga-e-kosoves/startseite/wettbewerb/KO1"),
    ("Malta Premier League Opening Round","https://www.transfermarkt.com/premier-league-opening-round/startseite/wettbewerb/MT1N"), 
    ("Ireland Premier Division", "https://www.transfermarkt.com/league-of-ireland-premier-division/startseite/wettbewerb/IR1"),
    ("Iceland Besta deild", "https://www.transfermarkt.com/besta-deild/startseite/wettbewerb/IS1"),
    ("Northern Ireland Premiership","https://www.transfermarkt.com/premiership/startseite/wettbewerb/NIR1"), 
    ("Estonia Premium Liiga", "https://www.transfermarkt.com/premium-liiga/startseite/wettbewerb/EST1"),
    ("Montenegro Meridianbet 1. CFL","https://www.transfermarkt.com/meridianbet-1-cfl/startseite/wettbewerb/MNE1"), 
    ("Luxembourg BGL Ligue", "https://www.transfermarkt.com/bgl-ligue/startseite/wettbewerb/LUX1"),
    ("Andorra Primera Divisió", "https://www.transfermarkt.com/primera-divisio/startseite/wettbewerb/AND1"),
    ("Faroe Islands Betri-deildin", "https://www.transfermarkt.com/betri-deildin/startseite/wettbewerb/FARO"),
    ("Wales Cymru Premier", "https://www.transfermarkt.com/cymru-premier/startseite/wettbewerb/WAL1"),
    ("Gibraltar Gibraltar Football League","https://www.transfermarkt.com/gibraltar-football-league/startseite/wettbewerb/GI1"), 
    ("Sanmarino Camp. Sammarinese", "https://www.transfermarkt.com/campionato-sammarinese/startseite/wettbewerb/SMR1"),
    ("Malta Gozo League","https://www.transfermarkt.com/gozo-football-league-first-division/startseite/wettbewerb/GZO1"),
    ("Brazil Série A","https://www.transfermarkt.com/campeonato-brasileiro-serie-a/startseite/wettbewerb/BRA1"),
    ("Argentina Liga Profesional","https://www.transfermarkt.com/professional-football-league/startseite/wettbewerb/AR1N"), 
    ("Colombia Liga Dimayor I","https://www.transfermarkt.com/liga-dimayor-apertura/startseite/wettbewerb/COLP"), 
    ("Chile Primera División","https://www.transfermarkt.com/primera-division-de-chile/startseite/wettbewerb/CLPD"), 
    ("Ecuador Serie A Primera Etapa","https://www.transfermarkt.com/ligapro-serie-a-primera-etapa/startseite/wettbewerb/EL1A"), 
    ("Uruguay Primera División Apertura","https://www.transfermarkt.com/primera-division-apertura/startseite/wettbewerb/URU1"), 
    ("Peru Liga 1 Apertura", "https://www.transfermarkt.com/liga-1-apertura/startseite/wettbewerb/TDeA"),
    ("Paraguay Primera División Apertura", "https://www.transfermarkt.com/primera-division-apertura/startseite/wettbewerb/PR1A"),
    ("Bolivia División Profesional Apertura","https://www.transfermarkt.com/division-profesional-apertura/startseite/wettbewerb/B1AP"),
    ("Venezuela Liga FUTVE Apertura","https://www.transfermarkt.com/liga-futve-apertura/startseite/wettbewerb/VZ1A"),
    ("United States MLS", "https://www.transfermarkt.com/major-league-soccer/startseite/wettbewerb/MLS1"),
    ("Mexico Liga MX Apertura", "https://www.transfermarkt.com/liga-mx-apertura/startseite/wettbewerb/MEXA"),
    ("Costa Rica Primera División Apertura", "https://www.transfermarkt.com/primera-division-apertura/startseite/wettbewerb/CRPD"),
    ("Honduras Liga Nacional Apertura", "https://www.transfermarkt.com/liga-nacional-apertura/startseite/wettbewerb/HO1A"),
    ("Guatemala Liga Guate Apertura", "https://www.transfermarkt.com/liga-guate-apertura/startseite/wettbewerb/GU1A"),
    ("El Salvador Primera División Apertura", "https://www.transfermarkt.com/primera-division-apertura/startseite/wettbewerb/SL1A"),
    ("Canada CanPL", "https://www.transfermarkt.com/canadian-premier-league/startseite/wettbewerb/CDN1"),
    ("Panama Liga Panameña Apertura", "https://www.transfermarkt.com/liga-panamena-de-futbol-apertura/startseite/wettbewerb/PN1A"),
    ("Nicaragua Liga Primera Apertura", "https://www.transfermarkt.com/liga-primera-de-nicaragua-apertura/startseite/wettbewerb/NC1A"),
    ("Dominican Republic Liga Dominicana de Fútbol", "https://www.transfermarkt.com/liga-dominicana-de-futbol/startseite/wettbewerb/DOM1"),
    ("Jamaica Jamaica Premier League","https://www.transfermarkt.com/jamaica-premier-league/startseite/wettbewerb/JPL1"),
    ("South Africa Betway Premiership", "https://www.transfermarkt.com/betway-premiership/startseite/wettbewerb/SFA1"),
    ("Egypt Premier League", "https://www.transfermarkt.com/egyptian-premier-league/startseite/wettbewerb/EGY1"),
    ("Morocco Botola Pro Inwi", "https://www.transfermarkt.com/botola-pro-inwi/startseite/wettbewerb/MAR1"),
    ("Argelia Ligue Professionnelle 1", "https://www.transfermarkt.com/ligue-professionnelle-1/startseite/wettbewerb/ALG1"),
    ("Tunisia Ligue I Pro", "https://www.transfermarkt.com/ligue-professionnelle-1/startseite/wettbewerb/TUN1"),
    ("Ghana Premier League", "https://www.transfermarkt.com/ghana-premier-league/startseite/wettbewerb/GHPL"),
    ("Angola Girabola", "https://www.transfermarkt.com/girabola/startseite/wettbewerb/AN1L"),
    ("Mozambique Moçambola", "https://www.transfermarkt.com/mocambola/startseite/wettbewerb/MO1L"),
    ("Uganda Premier League", "https://www.transfermarkt.com/uganda-premier-league/startseite/wettbewerb/UGL1"),
    ("Nigeria NPFL", "https://www.transfermarkt.com/nigeria-professional-football-league/startseite/wettbewerb/NPFL"),
    ("Ethiopia Premier League","https://www.transfermarkt.com/ethiopian-premier-league/startseite/wettbewerb/ETP1"),
    ("Saudi Arabia Saudi Pro League","https://www.transfermarkt.com/saudi-pro-league/startseite/wettbewerb/SA1"),
    ("United Araba Emirates UAE Pro League", "https://www.transfermarkt.com/uae-pro-league/startseite/wettbewerb/UAE1"),
    ("Qatar Stars League", "https://www.transfermarkt.com/qatar-stars-league/startseite/wettbewerb/QSL"),
    ("Japan J1 League","https://www.transfermarkt.com/j1-league/startseite/wettbewerb/JAP1"),
    ("Korea, South K League 1", "https://www.transfermarkt.com/k-league-1/startseite/wettbewerb/RSK1"),
    ("China Super League","https://www.transfermarkt.com/chinese-super-league/startseite/wettbewerb/CSL"),
    ("Iran Persian Gulf Pro League", "https://www.transfermarkt.com/persian-gulf-pro-league/startseite/wettbewerb/IRN1"),
    ("Uzbekistan Superliga", "https://www.transfermarkt.com/ozbekiston-superligasi/startseite/wettbewerb/UZ1"),
    ("Thailand Thai League","https://www.transfermarkt.com/thai-league/startseite/wettbewerb/THA1"), 
    ("Indonesia Liga 1","https://www.transfermarkt.com/liga-1-indonesia/startseite/wettbewerb/IN1L"), 
    ("India Indian Super League", "https://www.transfermarkt.com/indian-super-league/startseite/wettbewerb/IND1"),
    ("Malaysia Super League","https://www.transfermarkt.com/malaysia-super-league/startseite/wettbewerb/MYS1"), 
    ("Vietnam V.League 1", "https://www.transfermarkt.com/v-league-1/startseite/wettbewerb/VIE1"),
    ("Oman Oman Pro League", "https://www.transfermarkt.com/oman-professional-league/startseite/wettbewerb/OM1L"),
    ("Lebanon Leb. Premier League","https://www.transfermarkt.com/lebanese-premier-league/startseite/wettbewerb/LIB1"), 
    ("Hongkong Hong Kong Premier League", "https://www.transfermarkt.com/hong-kong-premier-league/startseite/wettbewerb/HGKG"),
    ("Singapore Premier League", "https://www.transfermarkt.com/singapore-premier-league/startseite/wettbewerb/SIN1"),
    ("Bangladesh Bangladesh PL", "https://www.transfermarkt.com/bangladesh-premier-league/startseite/wettbewerb/BGD1"),
    ("Cambodia C. Premier League", "https://www.transfermarkt.com/cambodian-premier-league/startseite/wettbewerb/KHM1"),
    ("Philippines PFL", "https://www.transfermarkt.com/philippines-football-league/startseite/wettbewerb/PFL1"),
    ("Tajikistan Vysshaya Liga","https://www.transfermarkt.com/vysshaya-liga/startseite/wettbewerb/TAD1"), 
    ("Chinese Taipei Football Premier League", "https://www.transfermarkt.com/taiwan-football-premier-league/startseite/wettbewerb/TFPL"),
    ("Myanmar National League","https://www.transfermarkt.com/myanmar-national-league/startseite/wettbewerb/MYA1"),
    ("Laos Lao League 1","https://www.transfermarkt.com/lao-league-1/startseite/wettbewerb/LAO1"),
    ("Australia A-League Men", "https://www.transfermarkt.com/a-league-men/startseite/wettbewerb/AUS1"),
    ("New Zeland National League - North", "https://www.transfermarkt.com/national-league-north/startseite/wettbewerb/NNL1"),
    ("New Zeland National League Championship","https://www.transfermarkt.com/national-league-championship/startseite/wettbewerb/NZNL"),
    ("New Zeland National League - Central", "https://www.transfermarkt.com/national-league-central/startseite/wettbewerb/NCL1"),
    ("Fiji Fiji Premier League", "https://www.transfermarkt.com/fiji-premier-league/startseite/wettbewerb/FIJ1"),
    ("New Zeland National League - South","https://www.transfermarkt.com/national-league-south/startseite/wettbewerb/NSL1")
    
    # Add more leagues here...
]


countries_url =[
    ("Argentina","https://www.transfermarkt.com/argentinien/startseite/verein/3437"),
    ("Brazil", "https://www.transfermarkt.com/brasilien/startseite/verein/3439"),
    ("Colombia", "https://www.transfermarkt.com/kolumbien/startseite/verein/3816"),
    ("Uruguay", "https://www.transfermarkt.com/uruguay/startseite/verein/3449"),
    ("Ecuador" , "https://www.transfermarkt.com/ecuador/startseite/verein/5750"),
    ("Venezuela", "https://www.transfermarkt.com/venezuela/startseite/verein/3504"),
    ("Peru", "https://www.transfermarkt.com/peru/startseite/verein/3584"),
    ("Chile","https://www.transfermarkt.com/chile/startseite/verein/3700"),
    ("Paraguay", "https://www.transfermarkt.com/paraguay/startseite/verein/3581"),
    ("Bolivia", "https://www.transfermarkt.com/bolivien/startseite/verein/5233"),
    ("France" ,"https://www.transfermarkt.com/frankreich/startseite/verein/3377"),
    ("Spain" , "https://www.transfermarkt.com/spanien/startseite/verein/3375"),
    ("England" , "https://www.transfermarkt.com/england/startseite/verein/3299"),
    ("Belgium" , "https://www.transfermarkt.com/belgien/startseite/verein/3382"),
    ("Netherlands" , "https://www.transfermarkt.com/niederlande/startseite/verein/3379"),
    ("Portugal" , "https://www.transfermarkt.com/portugal/startseite/verein/3300"),
    ("Italy" , "https://www.transfermarkt.com/italien/startseite/verein/3376"),
    ("Croatia" , "https://www.transfermarkt.com/kroatien/startseite/verein/3556"),
    ("Germany" , "https://www.transfermarkt.com/deutschland/startseite/verein/3262"),
    ("Switzerland", "https://www.transfermarkt.com/schweiz/startseite/verein/3384"),
    ("Denmark", "https://www.transfermarkt.com/danemark/startseite/verein/3436"),
    ("Austria", "https://www.transfermarkt.com/osterreich/startseite/verein/3383"),
    ("Ukraine", "https://www.transfermarkt.com/ukraine/startseite/verein/3699"),
    ("Turkey", "https://www.transfermarkt.com/turkei/startseite/verein/3381"),
    ("Poland","https://www.transfermarkt.com/polen/startseite/verein/3442"),
    ("Sweden","https://www.transfermarkt.com/schweden/startseite/verein/3557"),
    ("Wales","https://www.transfermarkt.com/wales/startseite/verein/3864"),
    ("Hungary","https://www.transfermarkt.com/ungarn/startseite/verein/3468"),
    ("Serbia","https://www.transfermarkt.com/serbien/startseite/verein/3438"),
    ("Russia","https://www.transfermarkt.com/russland/startseite/verein/3448"),
    ("Slovakia","https://www.transfermarkt.com/slowakei/startseite/verein/3503"),
    ("Romania","https://www.transfermarkt.com/rumanien/startseite/verein/3447"),
    ("Czech Republic","https://www.transfermarkt.com/tschechien/startseite/verein/3445"),
    ("Scotland","https://www.transfermarkt.com/schottland/startseite/verein/3380"),
    ("Norway","https://www.transfermarkt.com/norwegen/startseite/verein/3440"),
    ("Slovenia","https://www.transfermarkt.com/slowenien/startseite/verein/3588"),
    ("Greece","https://www.transfermarkt.com/griechenland/startseite/verein/3378"),
    ("Ireland","https://www.transfermarkt.com/irland/startseite/verein/3509"),
    ("Finland","https://www.transfermarkt.com/finnland/startseite/verein/3443"),
    ("Albania","https://www.transfermarkt.com/albanien/startseite/verein/3561"),
    ("Georgia","https://www.transfermarkt.com/georgien/startseite/verein/3669"),
    ("Iceland","https://www.transfermarkt.com/island/startseite/verein/3574"),
    ("North Macedonia","https://www.transfermarkt.com/nordmazedonien/startseite/verein/5148"),
    ("Montenegro","https://www.transfermarkt.com/montenegro/startseite/verein/11953"),
    ("North Ireland","https://www.transfermarkt.com/nordirland/startseite/verein/5674"),
    ("Bosnia-Herzegovina","https://www.transfermarkt.com/bosnien-herzegowina/startseite/verein/3446"),
    ("Israel","https://www.transfermarkt.com/israel/startseite/verein/5547"),
    ("Bulgaria","https://www.transfermarkt.com/bulgarien/startseite/verein/3394"),
    ("Luxembourg","https://www.transfermarkt.com/luxemburg/startseite/verein/3580"),
    ("Armenia","https://www.transfermarkt.com/armenien/startseite/verein/6219"),
    ("Belarus","https://www.transfermarkt.com/belarus/startseite/verein/3450"),
    ("Kosovo", "https://www.transfermarkt.com/kosovo/startseite/verein/53982"),
    ("kazakhstan","https://www.transfermarkt.com/kasachstan/startseite/verein/9110"),
    ("Azerbaijan","https://www.transfermarkt.com/aserbaidschan/startseite/verein/8605"),
    ("Estonia","https://www.transfermarkt.com/estland/startseite/verein/6133"),
    ("Cyprus","https://www.transfermarkt.com/zypern/startseite/verein/3668"),
    ("Lithuania","https://www.transfermarkt.com/litauen/startseite/verein/3851"),
    ("Latvia","https://www.transfermarkt.com/lettland/startseite/verein/3555"),
    ("Faroe Islands","https://www.transfermarkt.com/faroer/startseite/verein/9173"),
    ("Moldova","https://www.transfermarkt.com/moldawien/startseite/verein/6090"),
    ("Andorra","https://www.transfermarkt.com/fc-andorra/startseite/verein/10718"),
    ("Malta","https://www.transfermarkt.com/malta/startseite/verein/3587"),
    ("Gibraltar","https://www.transfermarkt.com/gibraltar/startseite/verein/37574"),
    ("Liechtenstein","https://www.transfermarkt.com/liechtenstein/startseite/verein/5673"),
    ("San Marino","https://www.transfermarkt.com/san-marino/startseite/verein/10521"),
    ("Morocco","https://www.transfermarkt.com/marokko/startseite/verein/3575"),
    ("Senegal","https://www.transfermarkt.com/senegal/startseite/verein/3499"),
    ("Egypt","https://www.transfermarkt.com/agypten/startseite/verein/3672"),
    ("Ivory Coast","https://www.transfermarkt.com/elfenbeinkuste/startseite/verein/3591"),
    ("Nigeria","https://www.transfermarkt.com/nigeria/startseite/verein/3444"),
    ("Tunisia","https://www.transfermarkt.com/tunesien/startseite/verein/3670"),
    ("Algeria","https://www.transfermarkt.com/algerien/startseite/verein/3614"),
    ("Cameroon","https://www.transfermarkt.com/kamerun/startseite/verein/3434"),
    ("Mali","https://www.transfermarkt.com/mali/startseite/verein/3674"),
    ("South Africa","https://www.transfermarkt.com/sudafrika/startseite/verein/3806"),
    ("Democratic Republic of the Congo","https://www.transfermarkt.com/demokratische-republik-kongo/startseite/verein/3854"),
    ("Ghana","https://www.transfermarkt.com/ghana/startseite/verein/3441"),
    ("Cape Verde","https://www.transfermarkt.com/kap-verde/startseite/verein/4311"),
    ("Burkina Faso","https://www.transfermarkt.com/burkina-faso/startseite/verein/5872"),
    ("Guinea","https://www.transfermarkt.com/guinea/startseite/verein/3856"),
    ("Gabon","https://www.transfermarkt.com/gabun/startseite/verein/5704"),
    ("Equatorial Guinea","https://www.transfermarkt.com/aquatorialguinea/startseite/verein/13485"),
    ("Angola","https://www.transfermarkt.com/angola/startseite/verein/3585"),
    ("Benin","https://www.transfermarkt.com/benin/startseite/verein/3955"),
    ("Zambia","https://www.transfermarkt.com/sambia/startseite/verein/3703"),
    ("Uganda","https://www.transfermarkt.com/uganda/startseite/verein/13497"),
    ("Namibia","https://www.transfermarkt.com/namibia/startseite/verein/3573"),
    ("Mozambique","https://www.transfermarkt.com/mosambik/startseite/verein/5129"),
    ("Madagascar","https://www.transfermarkt.com/madagaskar/startseite/verein/14635"),
    ("Kenya","https://www.transfermarkt.com/kenia/startseite/verein/8987"),
    ("Mauritania","https://www.transfermarkt.com/mauretanien/startseite/verein/14238"),
    ("Tanzania","https://www.transfermarkt.com/tansania/startseite/verein/14666"),
    ("Guinea-Bissau","https://www.transfermarkt.com/guinea-bissau/startseite/verein/3701"),
    ("Libya","https://www.transfermarkt.com/libyen/startseite/verein/6602"),
    ("Republic of the Congo","https://www.transfermarkt.com/republik-kongo/startseite/verein/3702"),
    ("Comoros","https://www.transfermarkt.com/komoren/startseite/verein/16430"),
    ("Togo","https://www.transfermarkt.com/togo/startseite/verein/3815"),
    ("Sudan","https://www.transfermarkt.com/sudan/startseite/verein/13313"),
    ("Sierra Leone","https://www.transfermarkt.com/sierra-leone/startseite/verein/6187"),
    ("Niger","https://www.transfermarkt.com/niger/startseite/verein/14163"),
    ("Malawi","https://www.transfermarkt.com/malawi/startseite/verein/8988"),
    ("Central African Republic","https://www.transfermarkt.com/zentralafrikanische-republik/startseite/verein/12933"),
    ("Zimbabwe","https://www.transfermarkt.com/simbabwe/startseite/verein/3583"),
    ("Rwanda","https://www.transfermarkt.com/ruanda/startseite/verein/3855"),
    ("The Gambia","https://www.transfermarkt.com/gambia/startseite/verein/6186"),
    ("Burundi","https://www.transfermarkt.com/burundi/startseite/verein/13943"),
    ("Liberia","https://www.transfermarkt.com/liberia/startseite/verein/9172"),
    ("Botswana","https://www.transfermarkt.com/botsuana/startseite/verein/15229"),
    ("Lesotho","https://www.transfermarkt.com/lesotho/startseite/verein/13962"),
    ("South Sudan","https://www.transfermarkt.com/sudsudan/startseite/verein/33192"),
    ("Chad","https://www.transfermarkt.com/tschad/startseite/verein/13978"),
    ("Sao Tome and Principe","https://www.transfermarkt.com/sao-tome-und-principe/startseite/verein/15236"),
    ("Somalia","https://www.transfermarkt.com/somalia/startseite/verein/13974"),
    ("New Zealand", "https://www.transfermarkt.com/neuseeland/startseite/verein/9171"),
    ("Solomon Islands","https://www.transfermarkt.com/salomon-inseln/startseite/verein/15740"),
    ("Fiji","https://www.transfermarkt.com/fidschi/startseite/verein/13955"),
    ("Vanuatu","https://www.transfermarkt.com/vanuatu/startseite/verein/15238"),
    ("Papua New Guinea","https://www.transfermarkt.com/papua-neuguinea/startseite/verein/15233"),
    ("Samoa","https://www.transfermarkt.com/samoa/startseite/verein/15235"),
    ("United States","https://www.transfermarkt.com/vereinigte-staaten/startseite/verein/3505"),
    ("Mexico","https://www.transfermarkt.com/mexiko/startseite/verein/6303"),
    ("Panama","https://www.transfermarkt.com/panama/startseite/verein/3577"),
    ("Canada","https://www.transfermarkt.com/kanada/startseite/verein/3510"),
    ("Costa Rica","https://www.transfermarkt.com/costa-rica/startseite/verein/8497"),
    ("Jamaica","https://www.transfermarkt.com/jamaika/startseite/verein/3671"),
    ("Honduras","https://www.transfermarkt.com/honduras/startseite/verein/3590"),
    ("El Salvador","https://www.transfermarkt.com/el-salvador/startseite/verein/13951"),
    ("Haiti","https://www.transfermarkt.com/haiti/startseite/verein/14161"),
    ("Curacao","https://www.transfermarkt.com/curacao/startseite/verein/32364"),
    ("Trinidad and Tobago","https://www.transfermarkt.com/trinidad-und-tobago/startseite/verein/7149"),
    ("Guatemala","https://www.transfermarkt.com/guatemala/startseite/verein/13342"),
    ("Nicaragua","https://www.transfermarkt.com/nicaragua/startseite/verein/15351"),
    ("Suriname","https://www.transfermarkt.com/suriname/startseite/verein/15359"),
    ("St Kitts and Nevis","https://www.transfermarkt.com/st-kitts-und-nevis/startseite/verein/17760"),
    ("Antigua and Barbuda","https://www.transfermarkt.com/antigua-und-barbuda/startseite/verein/16028"),
    ("Dominican Republic","https://www.transfermarkt.com/dominikanische-republik/startseite/verein/15232"),
    ("Guyana","https://www.transfermarkt.com/guyana/startseite/verein/15736"),
    ("Puerto Rico","https://www.transfermarkt.com/puerto-rico/startseite/verein/17759"),
    ("Cuba","https://www.transfermarkt.com/kuba/startseite/verein/3808"),
    ("St Lucia","https://www.transfermarkt.com/st-lucia/startseite/verein/17761"),
    ("Bermuda","https://www.transfermarkt.com/bermuda/startseite/verein/15735"),
    ("Grenada","https://www.transfermarkt.com/grenada/startseite/verein/14175"),
    ("St Vincent and the Grenadines","https://www.transfermarkt.com/st-vincent-und-die-grenadinen/startseite/verein/17762"),
    ("Montserrat","https://www.transfermarkt.com/montserrat/startseite/verein/17754"),
    ("Belize","https://www.transfermarkt.com/belize/startseite/verein/15919")
]


def scrape_data_countries(url):
    url_detailed=url.replace('/startseite/', '/kader/') + '/plus/1'
    response = requests.get(url_detailed, headers=headers)
    time.sleep(1)
    player_data = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        player_rows = soup.find_all('tr', class_=['odd', 'even'])
        for row in player_rows:
            jersey_number_tag = row.find('div', class_='rn_nummer')
            jersey_number = jersey_number_tag.text.strip() if jersey_number_tag else ''
            player_name_tag = row.find('td', class_='hauptlink').find('a')
            player_name = player_name_tag.text.strip() if player_name_tag else ''
            
            td_tags = row.find_all('td')
            position = ''
            if len(td_tags) > 1:
                position_tag = td_tags[1].find_all('tr')
                if position_tag and len(position_tag) > 0:
                    position = position_tag[-1].find('td').text.strip() if position_tag[-1].find('td') else ''

                    if position == 'Defender':
                        position = 'Centre-Back'
                    if position == 'Striker':
                        position = 'Centre-Forward'
                    if position == 'Midfielder':
                        position = 'Central Midfield'                

                    if position in ['Goalkeeper']:
                        position_role = 'Goalkeeper'
                    elif position in ['Right-Back', 'Left-Back']:
                        position_role = 'Defender'
                    elif position == 'Centre-Back':
                        position_role = 'Defender'
                    elif position in ['Right Midfield', 'Left Midfield', 'Central Midfield', 'Defensive Midfield', 'Attacking Midfield']:
                        position_role = 'Midfield'
                    elif position in ['Right Winger', 'Left Winger']:
                        position_role = 'Attack'
                    elif position in ['Centre-Forward', 'Second Striker']:
                        position_role = 'Attack'
            
            
            birthday_tag = row.find_all('td', class_='zentriert')[1]
            birthday_text = birthday_tag.text.strip() if birthday_tag else ''
            birthday_match = re.search(r'(\w{3} \d{1,2}, \d{4})', birthday_text)
            if birthday_match:
                birthday = datetime.strptime(birthday_match.group(1), '%b %d, %Y').strftime('%m/%d/%Y')
                age = (datetime.now() - datetime.strptime(birthday_match.group(1), '%b %d, %Y')).days // 365
                age = age if age < 0 else age
            else:
                birthday = ''
                age = ''
            
            player_url_tag = row.find('td', class_='hauptlink').find('a')
            player_url = f'https://www.transfermarkt.com{player_url_tag["href"]}' if player_url_tag else ''
            
            market_value_tag = row.find('td', class_='rechts hauptlink').find('a')
            market_value = market_value_to_number(market_value_tag.text.strip()) if market_value_tag else None

            club_tag = row.find_all('td', class_='zentriert')[2]
            club_name = club_tag.find('a')['title']
            club_img_url = club_tag.find('img')['src']
            club_img_url = club_img_url.replace('verysmall', 'head')

            height_tag = row.find_all('td', class_='zentriert')[3]
            height = int(height_tag.text.strip().replace('m', '').replace(',',''))if height_tag and height_tag.text.strip() not in ('', '-') else ''

            foot_tag = row.find_all('td', class_='zentriert')[4]
            foot = foot_tag.text.strip() if foot_tag and foot_tag.text.strip() not in ('', '-') else ''


            contract_date_tag = row.find_all('td', class_='zentriert')[7]
            contract_date_text = contract_date_tag.text.strip() if contract_date_tag else ''
            try:
                contract_date = datetime.strptime(contract_date_text, '%b %d, %Y').strftime('%m/%d/%Y')
            except ValueError:
                contract_date = ''

            player_data.append({
                'Jersey Number': jersey_number,
                'Player Name': player_name,
                'Position': position,
                'Position Role': position_role,
                'Birthday': birthday,
                'Age': age,
                'Market Value': market_value,
                'Club name': club_name,
                'Club imag': club_img_url,
                'Height': height,
                'Foot': foot,
                'Contract Date': contract_date,
                'Player URL': player_url
            })
            pass
    return player_data

def get_transfer_history(player_url):
    # Extract the player ID from the URL
    player_id = player_url.split('/')[-1]
    
    # Construct the transfer history URL
    transfer_url = f"https://www.transfermarkt.com/ceapi/transferHistory/list/{player_id}"
    
    # Request headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # Make the request
    response = requests.get(transfer_url, headers=headers)
    
    # Check if the response is successful
    if response.status_code == 200:
        transfer_data = response.json()
        return transfer_data['transfers']
    else:
        return None
    

def market_value_to_number(value_str):
    value_str = value_str.strip().replace('$', '').replace('€', '').replace('K', '000').replace('m', '0000').replace('.', '')
    value_str_lower = value_str.lower()
    if 'm' in value_str_lower:
        return int(float(value_str_lower.replace('m', '')) * 10000)
    elif 'k' in value_str_lower:
        return int(float(value_str_lower.replace('k', '')) * 1000)
    else:
        return int(value_str_lower)

def get_team_urls(league_url):
    response = requests.get(league_url, headers=headers)
    time.sleep(1)
    team_urls = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        team_tags = soup.select('td.hauptlink.no-border-links a[href*="/startseite/verein/"]')
        for tag in team_tags:
            team_url = f"https://www.transfermarkt.com{tag['href']}".replace('/startseite/', '/kader/') + '/plus/1'
            team_urls.append(team_url)
    return team_urls

def get_team_urls_with_names(league_url):
    response = requests.get(league_url, headers=headers)
    time.sleep(1)
    teams = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        team_tags = soup.select('td.hauptlink.no-border-links a[href*="/startseite/verein/"]')
        for tag in team_tags:
            team_name = tag['title']
            team_url = f"https://www.transfermarkt.com{tag['href']}".replace('/startseite/', '/kader/') + '/plus/1'
            teams.append({'name': team_name, 'url': team_url})
    return teams

def scrape_data(url):
    response = requests.get(url, headers=headers)
    time.sleep(1)
    player_data = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        player_rows = soup.find_all('tr', class_=['odd', 'even'])
        for row in player_rows:
            jersey_number_tag = row.find('div', class_='rn_nummer')
            jersey_number = jersey_number_tag.text.strip() if jersey_number_tag else ''
            player_name_tag = row.find('td', class_='hauptlink').find('a')
            player_name = player_name_tag.text.strip() if player_name_tag else ''

            td_tags = row.find_all('td')
            position = ''
            if len(td_tags) > 1:
                position_tag = td_tags[1].find_all('tr')
                if position_tag and len(position_tag) > 0:
                    position = position_tag[-1].find('td').text.strip() if position_tag[-1].find('td') else ''

                    # Normalize position names
                    if position == 'Defender':
                        position = 'Centre-Back'
                    if position == 'Striker':
                        position = 'Centre-Forward'
                    if position == 'Midfielder':
                        position = 'Central Midfield'                

                    # Determine position role
                    if position in ['Goalkeeper']:
                        position_role = 'Goalkeeper'
                    elif position in ['Right-Back', 'Left-Back']:
                        position_role = 'Defender'
                    elif position == 'Centre-Back':
                        position_role = 'Defender'
                    elif position in ['Right Midfield', 'Left Midfield', 'Central Midfield', 'Defensive Midfield', 'Attacking Midfield']:
                        position_role = 'Midfield'
                    elif position in ['Right Winger', 'Left Winger']:
                        position_role = 'Attack'
                    elif position in ['Centre-Forward', 'Second Striker']:
                        position_role = 'Attack'

            club_name_tag = soup.find('h1', class_='data-header__headline-wrapper')
            club_name = club_name_tag.text.strip() if club_name_tag else ''


            club_img_div = soup.find('div', class_='data-header__profile-container')
            club_img = (club_img_div.find('img')['src'].split('.png')[0] + '.png') if club_img_div and club_img_div.find('img') and 'src' in club_img_div.find('img').attrs else ''


            
            birthday_tag = row.find_all('td', class_='zentriert')[1]
            birthday_text = birthday_tag.text.strip() if birthday_tag else ''
            birthday_match = re.search(r'(\w{3} \d{1,2}, \d{4})', birthday_text)
            if birthday_match:
                birthday = datetime.strptime(birthday_match.group(1), '%b %d, %Y').strftime('%m/%d/%Y')
                age = (datetime.now() - datetime.strptime(birthday_match.group(1), '%b %d, %Y')).days // 365
                age = age if age < 0 else age
            else:
                birthday = ''
                age = ''
            
            # Handle nationalities and their flags
            nationalities_tags = row.find_all('img', class_='flaggenrahmen')
            nationalities = [img['title'] for img in nationalities_tags] if nationalities_tags else []
            nat_url = nationalities_tags[0]['src'].replace('verysmall', 'head') if len(nationalities_tags) > 0 else ''
            nat_url2 = nationalities_tags[1]['src'].replace('verysmall', 'head') if len(nationalities_tags) > 1 else ''

            nat = nationalities[0] if len(nationalities) > 0 else ''
            continent = 'N/A'

            # Determine the continent based on the first nationality
            if nat in ['Wales','England','Italy','Germany','Spain','France','Belgium','Portugal','Denmark','Russia','Switzerland','Netherlands','Türkiye','Austria','Croatia','Poland','Norway','Sweden','Cyprus','Czech Republic','Hungary','Greece','Romania','Scotland','Slovenia','Ukraine','Azerbaijan','Slovakia','Bulgaria','Serbia','Bosnia-Herzegovina','Kazakhstan','Finland','Georgia','Albania','Belarus','Armenia','Ireland','Iceland','Kosovo','North Macedonia','Moldova','Lithuania','Latvia','Malta','Luxembourg','Montenegro','Faroe Islands','Northern Ireland','Estonia','Andorra','Gibraltar','San Marino']:
                continent = 'Europe'
            elif nat in ['Korea, South','Gabon','Chad','Afghanistan','Israel','Japan', 'Saudi Arabia', 'Iran', 'United Arab Emirates', 'Iraq', 'China', 'Uzbekistan', 'Kuwait', 'Jordan', 'Thailand', 'Bahrain', 'Syria', 'Qatar', 'Oman', 'Malaysia', 'Vietnam', 'Indonesia', 'Palestine', 'Lebanon', 'India', 'Nepal', 'Singapore', 'Hongkong', 'Yemen', 'Turkmenistan', 'Philippines', 'Tajikistan', 'Kyrgyzstan', 'Myanmar', 'Cambodia', 'Chinese Taipei', 'Bangladesh', 'Maldives', 'Mongolia', 'Macao', 'Brunei Darussalam', 'Guam', 'Laos', 'Bhutan']:
                continent ='Asia'
            elif nat in  ['Morocco','Algeria', 'Egypt', 'South Africa', 'Tunisia', 'Ghana', 'Nigeria', 'Zambia', 'Cote d\'Ivoire', 'Senegal', 'Réunion', 'Mali', 'Tanzania', 'Zimbabwe', 'Mozambique', 'Libya', 'Angola', 'Burkina Faso', 'Togo', 'Guinea', 'Uganda', 'Ethiopia', 'DR Congo', 'Kenya', 'Cape Verde', 'Congo', 'Mauritania', 'Cameroon', 'The Gambia', 'Burundi', 'Rwanda', 'Madagascar', 'Botsuana', 'Eswatini', 'Benin', 'Lesotho', 'Malawi', 'Mauritius', 'Liberia', 'Sao Tome and Principe', 'Sierra Leone', 'Niger', 'Somalia']:
                continent ='Africa'
            elif nat in ['United States','Mexico','Canada']:
                continent = 'North America'
            elif nat in ['Costa Rica', 'Panama', 'Guatemala', 'Honduras', 'El Salvador', 'Jamaica', 'Nicaragua', 'Dominican Republic', 
                         'Grenada', 'Haiti', 'Suriname', 'Antigua and Barbuda', 'French Guiana', 'Martinique', 'Puerto Rico', 'Aruba', 
                         'St. Kitts & Nevis', 'British Virgin Islands', 'Trinidad and Tobago', 'Guadeloupe', 'Turks- and Caicosinseln', 'Belize', 'Curacao', 
                         'Cayman Islands', 'Cuba', 'Bermuda', 'Guyana', 'Barbados','Anguilla','Bahamas']:
                continent = 'Central America'
            elif nat in ['Brazil', 'Argentina', 'Ecuador', 'Colombia', 'Paraguay', 'Chile', 'Uruguay', 'Bolivia', 'Peru', 'Venezuela']:
                continent = 'South America'
            elif nat in ['American Samoa','Australia','New Zealand', 'Neukaledonien', 'Fiji', 'Papua New Guinea', 'Solomon Islands', 'Cookinseln','Tahiti']:
                continent = 'Oceania'
            
            player_url_tag = row.find('td', class_='hauptlink').find('a')
            player_url = f'https://www.transfermarkt.com{player_url_tag["href"]}' if player_url_tag else ''
            
            market_value_tag = row.find('td', class_='rechts hauptlink').find('a')
            market_value = market_value_to_number(market_value_tag.text.strip()) if market_value_tag else None

            height_tag = row.find_all('td', class_='zentriert')[3]
            height = int(height_tag.text.strip().replace('m', '').replace(',',''))if height_tag and height_tag.text.strip() not in ('', '-') else ''

            foot_tag = row.find_all('td', class_='zentriert')[4]
            foot = foot_tag.text.strip() if foot_tag and foot_tag.text.strip() not in ('', '-') else ''

            joined_club_date_tag = row.find_all('td', class_='zentriert')[5]
            joined_club_date_text = joined_club_date_tag.text.strip() if joined_club_date_tag else ''
            try:
                joined_club_date = datetime.strptime(joined_club_date_text, '%b %d, %Y').strftime('%m/%d/%Y') if joined_club_date_text and joined_club_date_text != '-' else ''
            except ValueError:
                joined_club_date = ''

            signed_from_team_tag = row.find_all('td', class_='zentriert')[6].find('a') if len(row.find_all('td', class_='zentriert')) > 6 else None
            signed_from_team = signed_from_team_tag['title'].split(':')[0] if signed_from_team_tag and signed_from_team_tag['title'] != '-' else ''
            
            # Collect all player data
            player_data.append({
                'Jersey Number': jersey_number,
                'Player Name': player_name,
                'Position': position,
                'Position Role': position_role,
                'Birthday': birthday,
                'Age': age,
                'Market Value': market_value,
                'Club Name': club_name,
                'Continent': continent,
                'Nationality 1': nationalities[0] if nationalities else '',
                'Nationality 2': nationalities[1] if len(nationalities) > 1 else '',
                'Height': height,
                'Foot': foot,
                'Joined Club Date': joined_club_date,
                'Signed From Team': signed_from_team,
                'Player URL': player_url,
                'nat_url': nat_url,
                'nat_url2': nat_url2,
                'club_img':club_img
            })
            
    return player_data



