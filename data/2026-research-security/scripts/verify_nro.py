"""Work-by-work verification of Canada-NRO collaborations (type:article, 2015-2025, all team sizes).

Run from scripts/:
  python verify_nro.py --pull     # (re)pull candidates + institution metadata via verify_nro_pull.py (cached, resumable)
  python verify_nro.py            # run the three checks, apply manual decisions, write outputs

Inputs : ../results/nro_map.csv (high/medium rows) (aliases are curated in this script),
         ../results/nro_verify_cache/ (works_*.jsonl.gz, institutions.json), ../results/ca_works/ (local cross-check),
         ../results/nro_verification_manual.csv (hand decisions for cases the rules leave ambiguous; optional)
Outputs: ../results/nro_verification.csv (full, with raw strings: keep local), ../results/nro_verification_verdicts.csv
         (work ID, NRO IDs, checks, verdict: published), ../results/nro_verification_stats.json (python verify_nro.py --stats)

Checks per work
  a  NRO evidence: a raw affiliation string that OpenAlex tied to the NRO institution (or, if no string is tied,
     any string of that authorship) names the organization (curated aliases per NRO; generic names need
     country context; strings that name a different, similarly named organization fail).
  b  Canadian evidence: a raw string tied to a CA institution names a Canadian place/institution and is not a
     foreign string mis-geocoded to Canada.
  c  Same-work sanity: real research article (no erratum/correction/paratext, no duplicate record among the
     candidates, author list not a merged/duplicated block), and the CA and NRO evidence sit on this work's
     authorships.
  verdict: verified = a,b,c pass; false_positive = any check fails; unverifiable = raw strings missing (no fail).
"""
import csv, json, gzip, glob, os, re, sys, unicodedata, collections

D = '../results'; C = f'{D}/nro_verify_cache'
S = lambda u: u.rsplit('/', 1)[-1] if u else None

# ---------------------------------------------------------------- normalisation
ABBR = {
    'univ': 'university', 'univ.': 'university', 'inst': 'institute', 'technol': 'technology', 'nat': 'national', 'tech': 'technology',
    'sci': 'science', 'engn': 'engineering', 'eng': 'engineering', 'natl': 'national', 'def': 'defense',
    'defence': 'defense', 'centre': 'center', 'elect': 'electronic', 'aeronaut': 'aeronautics',
    'astronaut': 'astronautics', 'polytech': 'polytechnical', 'med': 'medical', 'mil': 'military',
    'telecommun': 'telecommunications', 'lab': 'laboratory', 'labs': 'laboratories', 'coll': 'college',
    'acad': 'academy', 'res': 'research', 'ctr': 'center', 'informat': 'information', 'phys': 'physics',
    'organisation': 'organization', 'hosp': 'hospital', 'sch': 'school', 'dept': 'department',
}
def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[’‘′´`ʼ‵]", "'", s.lower())
    s = re.sub(r"xi\s*'\s*an|xi\s+an\b", 'xian', s)
    s = s.replace('&', ' and ')
    s = re.sub(r"[^\w,;()一-鿿؀-ۿ]+", ' ', s)
    s = re.sub(r'([,;()])', r' \1 ', s)
    s = ' '.join(ABBR.get(t, t) for t in s.split())
    s = re.sub(r'\s*([,;()])\s*', r' \1 ', s)
    return ' ' + re.sub(r'\s+', ' ', s).strip() + ' '

# ---------------------------------------------------------------- country context
CN_CTX = re.compile(r"\b(china|chinese|prc|p r china|pr china|beijing|shanghai|tianjin|chongqing|harbin|chengdu|xian|nanjing|changsha|hefei|wuhan|shenzhen|guangzhou|hangzhou|mianyang|taiyuan|zhengzhou|shenyang|dalian|qingdao|weihai|luoyang|shijiazhuang|yantai|langfang|jinan|kunming|lanzhou|suzhou|xiamen|fuzhou|changchun|nanchang|guiyang|nanning|xuzhou|wuxi|ningbo|zhuhai|xianyang|baoding|qinhuangdao|sichuan|heilongjiang|shaanxi|hunan|hubei|jiangsu|zhejiang|guangdong|shandong|henan|hebei|liaoning|jilin|anhui|fujian|jiangxi|yunnan|guizhou|gansu|shanxi|pla|people s liberation army|xijing|xinqiao|daping|changhai|changzheng|tangdu|(second|third|fourth) military medical)\b|[一-鿿]")
IR_CTX = re.compile(r"\b(iran|iranian|tehran|teheran|karaj|isfahan|esfahan|mashhad|shiraz|tabriz|evin|velenjak|islamic republic)\b")
RU_CTX = re.compile(r"\b(russia|russian|moscow|rossii|ras)\b|[Ѐ-ӿ]")
CTX = {'CN': CN_CTX, 'IR': IR_CTX, 'RU': RU_CTX}
FOREIGN = re.compile(r"\b(usa|u s a|united states|america|united kingdom|uk|england|scotland|wales|germany|france|japan|korea|australia|india|pakistan|italy|spain|netherlands|singapore|taiwan|turkey|turkiye|malaysia|brazil|mexico|sweden|norway|denmark|finland|switzerland|austria|belgium|poland|egypt|saudi|nigeria|south africa|new zealand|israel|greece|portugal|ireland|thailand|vietnam|indonesia|bangladesh|iraq|jordan|qatar|emirates|uae|hong kong|macau|macao|ukraine|czech|hungary|romania|chile|argentina|colombia|peru|ethiopia|kenya|ghana|philippines|nepal|sri lanka|lebanon|algeria|morocco|tunisia|california|texas|new york|massachusetts|virginia|washington dc|maryland|florida|illinois)\b")

# ---------------------------------------------------------------- NRO alias table (normalised-text regexes)
# 'p' positive patterns; 'acr' case-sensitive acronyms (count only with own-country context);
# 'ctx' = True -> generic name, a positive match also needs own-country context; 'neg' -> match is discarded.
SKL = 'state key laboratory of '
A = {
 'I24185976': dict(p=[r'sichuan university(?! of)', r'universite (de )?sichuan', r'university of sichuan', r'sichuan daxue', r'\bwest china (hospital|school|medical|college|second|fourth|women|clinical|biomedical|center|centre|hosp)', r'\bhuaxi\b', '四川大学', '华西',
                      SKL + r'polymer materials? engineering', SKL + r'hydraulics and mountain river', SKL + r'biotherapy', SKL + r'oral diseases?'], acr=[]),
 'I2800091995': 'I24185976', 'I4391768003': 'I24185976', 'I4405255216': 'I24185976', 'I4391768043': 'I24185976', 'I4391767678': 'I24185976',
 'I204983213': dict(p=[r'harbin institute (of )?tech\w*', r'harbin in\w*tute (of )?technolog\w*', r'harbin gongye daxue', '哈尔滨工业大学', SKL + r'robotics and systems?', SKL + r'urban water resources?', SKL + r'advanced welding'], acr=['HIT'], neg=[r'^(?!.*harbin institute).*hit robot group']),
 'I4391767639': 'I204983213', 'I4391767770': 'I204983213', 'I4391767836': 'I204983213',
 'I150229711': dict(p=[r'university (of )?electronics? (and )?(sc?h?iences? )?(and )?(science )?(techn?o?l?o?g?y|technolgy|technology) (of )?(china|, p r china|p r china)', r'university (of )?electronics? (and )?(sc?h?iences? )?(and )?(science )?(technolgy|technology)( \d+)? (, )?(school of [a-z ]+ (, )+)?chengdu', r'\buestc\b', r'(?<!guilin )(?<!xian )(?<!hangzhou )university of electronic science and technology(?= (, )?chengdu)',
                       r'(?<![一-鿿])电子科技大学', SKL + r'electronic thin films?'], acr=['UESTC'], neg=[r'xidian', r'hangzhou dianzi', r'guilin university of electronic']),
 'I4391767659': 'I150229711',
 'I162868743': dict(p=[r'tian ?jin university(?! of)', r'university of tianjin', r'tianjin daxue', r'^(?!.*nankai).*collaborative innovation cent(er|re) of chemical science and engineering[ ,()a-z]*300072', r'peiyang university', '天津大学', SKL + r'hydraulic engineering simulation'], acr=[], neg=[r'^(?!.*tianjin university (,|tianjin|school|college|department)).*tianjin university cancer institute']),
 'I4210151209': 'I162868743', 'I4391767769': 'I162868743', 'I4391767736': 'I162868743', 'I4392021117': 'I162868743',
 'I48379061': dict(p=[r'(shahid|shaheed|martyr) (be|ba)h?e?sh?ti university(?! of med)(?! medical)', r'university of shahid beh\w*', r'(shahid |shaheed |martyr )?beh\w{0,3}sh?h?t[hi]?[iy] (uinversity|university)(?! of med)(?! medical)', r'(?<!shahid )(?<!shaheed )beheshti university(?! of med)(?! medical)', r'national university of iran', '(?<!پزشکی )شهید بهشتی'],
                   acr=['SBU'], neg=[r'beh\w*sh?h?t[hi]?[iy] (university )?(n )?(of )?medic', r'beh\w*sh?h?t[hi]?[iy] (school of (medicine|pharmacy)|university of medicine)', r'\bsbmu\b', r'universityof medic', 'علوم پزشکی'], medctx=True),
 'I133529467': dict(p=[r'sharif university', 'صنعتی شریف', r'sharif technical university', r'arya ?mehr', r'sharif univ\w*'], acr=[]),
 'I82880672': dict(p=[r'beihang', r'beijing university (of )?aeronautics? (and )?astronaut\w*', r'\bbuaa\b', '北京航空航天大学', SKL + r'software development environment', SKL + r'virtual reality technology', r'tianmushan laboratory'], acr=['BUAA']),
 'I4392738276': 'I82880672', 'I4391767781': 'I82880672', 'I4405266553': 'I82880672', 'I4405287588': 'I82880672',
 'I125839683': dict(p=[r'beijing institut(e|ion) (of )?technolog\w*', r'beijing in ?s\w*tute (of )?technolog\w*', '北京理工大学', r'beijing ligong'], acr=[]),
 'I17145004': dict(p=[r'north ?west(ern)? polytechnic(al)? university', r'north ?west(ern)? (poly|ploy) ?tech?\w* university', r'northwestern polytechical', r'\bnwpu\b', '西北工业大学', r'xibei gongye', SKL + r'solidification processing'], acr=['NPU', 'NWPU']),
 'I4391768207': 'I17145004',
 'I9842412': dict(p=[r'nanjing university (of )?(aero|astro)[a-z ]{0,12}(and )?(astro|aero)\w*', r'\bnuaa\b', '南京航空航天大学', r'nanhang', SKL + r'mechanics and control (of|for) mechanical structures?', SKL + r'mechanical structure mechanics'], acr=['NUAA']),
 'I4391767839': 'I9842412',
 'I16609230': dict(p=[r'hunan university(?! of)', r'hunan daxue', '湖南大学', SKL + r'chemo ?biosensing', SKL + r'advanced design and manufactur', r'national supercomputing (center|centre)? ?(in )?changsha', r'changsha national supercomputing'], acr=[]),
 'I4391767752': 'I16609230', 'I4391767846': 'I16609230', 'I4405257734': 'I16609230',
 'I139759216': dict(p=[r'beijing university (of )?posts? (, )?(and )?(tele ?)?com\w*', r'university of posts and telecommunications (, )?beijing', r'\bbupt\b', '北京邮电大学', SKL + r'networking and switching', SKL + r'information photonics and optical'], acr=['BUPT']),
 'I4392021250': 'I139759216', 'I4391767763': 'I139759216',
 'I36399199': dict(p=[r'nan?j?n?ing university (of )?science (and )?technology', r'\bnjust\b', '南京理工大学', r'nanjing ligong', r'zijin college'], acr=['NJUST', 'NUST']),
 'I4403386710': 'I36399199', 'I4405279362': 'I36399199',
 'I170215575': dict(p=[r'national university (of )?defense (and )?(science (and )?)?technology', r'\bnudt\b', '国防科技大学', '国防科学技术大学', r'guofang', SKL + r'pulsed power laser', SKL + r'complex electromagnetic environment', r'national key laboratory (for|of) parallel and distributed', r'changsha institute of technology'], acr=['NUDT']),
 'I4391767685': 'I170215575', 'I4392021190': 'I170215575', 'I4391767751': 'I170215575', 'I4405279573': 'I170215575',
 'I151727225': dict(p=[r'ha[ir]?bin engineering university', '哈尔滨工程大学', r'harbin gongcheng'], acr=['HEU']),
 'I151075929': dict(p=[r'army medical university', r'third military medical university', r'(?<!air force )(?<!naval )(?<!navy )military medical university (, )?chongqing', r'\btmmu\b', '陆军军医大学', '第三军医大学', r'daping hospital', r'xinqiao hospital', r'southwest hospital', SKL + r'trauma'], acr=['TMMU'], ctx=True),
 'I4391767916': 'I151075929',
 'I177933477': dict(p=[r'nav(y|al) (military )?medical university', r'second military medical university', r'\bsmmu\b', '海军军医大学', '第二军医大学', r'changhai hospital', r'changzheng hospital', r'eastern hepatobiliary'], acr=['SMMU'], ctx=True),
 'I4391767733': 'I177933477',
 'I9916479': dict(p=[r'air force (military )?medical university', r'fourth military medical university', r'\bfmmu\b', '空军军医大学', '第四军医大学', r'xijing hospital', r'tangdu hospital', r'fourth medical university', SKL + r'cancer biology'], acr=['FMMU'], ctx=True),
 'I4391767982': 'I9916479',
 'I2802541053': dict(p=[r'academy (of )?military medical sciences?', r'\bamms\b', r'beijing institute (of )?microbiology (and )?epidemiology', r'institute (of )?microbiology (and )?epidemiology , beijing', r'state key laboratory of pathogen and biosecurity', r'beijing institute (of )?radiation medicine', r'beijing institute (of )?basic medical sciences',
                        r'beijing institute (of )?pharmacology (and )?toxicology', r'beijing institute (of )?biotechnology', r'institute (of )?military medicine', r'beijing proteome research', SKL + r'proteomics', r'academy (of )?military sciences?', '军事医学'], acr=['AMMS']),
 'I4405260518': 'I2802541053', 'I4391768116': 'I2802541053', 'I4405261396': 'I2802541053', 'I4391768248': 'I2802541053',
 'I4210158522': dict(p=[r'academy (of )?military sciences?', r'academy (of )?military medical sciences?', '军事科学院', '军事医学科学院'], acr=['AMS'], ctx=True),
 'I2801345734': dict(p=[r'(china|chinese) academy (of )?engineering physics', r'\bcaep\b', '中国工程物理研究院', r'institute (of )?applied physics (and )?computational mathematics', r'\biapcm\b',
                        r'laser fusion research (center|centre)', r'research (center|centre) (of|for) laser fusion', r'institute (of )?fluid physics', r'institute (of )?nuclear physics (and )?chemistry', r'institute (of )?chemical materials',
                        r'microsystem (and )?terahertz', r'shanghai institute (of )?laser plasma', r'southwest institute (of )?(applied electronics|chemical materials|electronic engineering|environmental testing|explosives|fluid physics|general design|machining|materials|nuclear physics|structural mechanics)',
                        r'ninth academy', r'software center for high performance numerical simulation', r'national key laboratory (of|for) shock wave', r'science (and )?technology on plasma physics laboratory', r'institute (of )?(electronic engineering|materials) (, )?mianyang'], acr=['CAEP']),
 'I4387155340': 'I2801345734', 'I4387152340': 'I2801345734', 'I4210090923': 'I2801345734', 'I4405255966': 'I2801345734', 'I4405281335': 'I2801345734', 'I4210145278': 'I2801345734', 'I4405256023': 'I2801345734',
 'I4210139958': dict(p=[r'beijing comput(ational|ing) science research (center|centre)', r'computational science research (center|centre)', '北京计算科学研究中心'], acr=['CSRC', 'BCSRC']),
 'I4210143697': dict(p=[r'high pressure (, )?science (and )?technology advanced research', r'\bhpstar\b', '北京高压科学研究中心', r'beijing high voltage science'], acr=['HPSTAR']),
 'I4210141749': 'I4210143697', 'I4210145869': 'I4210143697',
 'I4210130940': dict(p=[r'peac institute', r'peak multi ?scale', r'multiscale science institute'], acr=['PIMS']),
 'I4402554102': dict(p=[r'chengdu fine optic'], acr=[]),
 'I4210103894': dict(p=[r'physical sciences? at (the )?micro ?scale', r'national research (center|centre) for micro ?scale', r'microscale national research', '合肥微尺度'], acr=['HFNL']),
 'I4210090176': dict(p=[r'institute (of )?computing technology', r'\bict (, )?(cas|chinese academy)\b', r'\bcas (, )?ict\b', '计算技术研究所', SKL + r'computer architecture', SKL + r'processors'], acr=[], ctx=True, neg=[r'shenzhen institute of computing', r'beijing institute of computing']),
 'I4391767888': 'I4210090176',
 'I142078773': dict(p=[r'shenyang institute (of )?automation', '沈阳自动化研究所', SKL + r'robotics(?! and system)'], acr=['SIA']),
 'I4391768281': 'I142078773',
 'I4210107660': dict(p=[r'information transmission problems', r'problems of information transmission', r'\biitp\b', r'kharkevich', r'\bippi\b'], acr=['IITP']),
 'I1301411061': dict(p=[r'pasteur institute (of )?iran', r'pasture institute (of )?iran', r'institut(e)? pasteur (d |de |of )?(l )?iran', r'iranian pasteur', r'pasteur institute', r'institut(e)? pasteur'], acr=[], ctx=True),
 'I120514687': dict(p=[r'ba(q|gh|g)h?[iy]*a*t[ao]+ll?ah', r'baqiyat', r'\bbmsu\b'], acr=['BMSU']),
 'I2802500176': dict(p=[r'iranian research organi[sz]ation (for )?science', r'\birost\b'], acr=['IROST']),
 'I135714990': dict(p=[r'north university (of )?china', '中北大学', r'zhongbei university'], acr=['NUC']),
 'I4210110558': dict(p=[r'xian technological (, )?university', r'\bxatu\b', '西安工业大学'], acr=['XATU']),
 'I4210163363': dict(p=[r'army engineering university', r'(pla|people s liberation army) university (of )?science (and )?technology', '陆军工程大学', r'army engineering university of (the )?pla'], acr=[], ctx=True),
 'I4210104252': dict(p=[r'air force engineering university', r'\bafeu\b', '空军工程大学'], acr=['AFEU'], ctx=True),
 'I4210162215': dict(p=[r'naval aeronautical (and astronautical )?(university|engineering)', r'nav(y|al) aviation university', r'naval aeronautics (and )?astronautics university', '海军航空'], acr=[], ctx=True),
 'I4210148107': dict(p=[r'space engineering university', r'aerospace engineering university', r'pla equipment (command and technology )?academy', r'academy (of )?equipment', r'equipment academy', '航天工程大学', '装备学院'], acr=[], ctx=True),
 'I2800710378': dict(p=[r'naval university (of )?engineering', r'naval engineering university', '海军工程大学'], acr=[], ctx=True),
 'I169689159': dict(p=[r'(^|[,;(]|pla|\s) ?information engineering university', r'zhengzhou institute (of )?surveying', r'zhengzhou information science (and )?technology institute', r'national digital switching system', SKL + r'mathematical engineering (and )?advanced computing',
                        r'luoyang foreign languages? (university|institute)', r'pla foreign languages? university', '信息工程大学'], acr=['PLAIEU'], ctx=True),
 'I4210111482': dict(p=[r'logistics (university|college) (of )?(the )?(chinese )?(people s )?armed police', r'logistics university of (the )?(pap|capf)', r'pap logistics', '武警后勤'], acr=[]),
 'I4210134428': dict(p=[r'engineering university (of )?(the )?(chinese )?(people s )?armed police', r'armed police (force )?engineering', r'engineering university (of )?(the )?(pap|capf)', r'pap engineering university', '武警工程大学', '武装警察部队工程大学'], acr=[], ctx=True),
 'I52604927': dict(p=[r'army service academy', r'logistical engineering university', r'army logistic(al|s)? (university|academy)', '陆军勤务学院', '后勤工程学院'], acr=[], ctx=True),
 'I4210167189': dict(p=[r'academy (of )?military transportation', r'military transportation (academy|university|institute|college)', '军事交通学院'], acr=[]),
 'I4210167232': dict(p=[r'air force aviation university', r'aviation university (of )?(pla )?air force', r'\bauaf\b', '空军航空大学'], acr=[], ctx=True),
 'I4405280021': dict(p=[r'national defense university', '国防大学'], acr=[], ctx=True, neg=[r'national defense university of (pakistan|malaysia)', r'taoyuan', r'taiwan', r'washington', r'fort mcnair', r'\bndu (, )?(usa|us)\b']),
 'I4210126933': 'I4405280021',
 'I2801618472': dict(p=[r'rocket force (university (of )?engineering|engineering university)', r'high tech(nology)? institute (of )?xian', r'xian (research )?institute (of )?high tech', r'second artillery engineering', r'\brfue\b', '火箭军工程大学'], acr=['RFUE'], ctx=True),
 'I37448385': dict(p=[r'people s public security university', r'(chinese )?people public security university', r'public security university of china', r'\bppsuc\b', '中国人民公安大学'], acr=['PPSUC']),
 'I4210158717': dict(p=[r'criminal investigation police university', r'national police university of china (, )?shenyang', '刑事警察学院'], acr=['CIPUC']),
 'I4405280979': dict(p=[r'railway police college', r'zhengzhou police university', '铁道警察学院'], acr=[]),
 'I4210151975': dict(p=[r'northwest(ern)? institute (of )?nuclear technology', r'northwest nuclear technology', r'\bnint\b', '西北核技术'], acr=['NINT']),
 'I4391768030': 'I4210151975',
 'I2802505932': dict(p=[r'china aerodynamics research', r'\bcardc\b', '中国空气动力'], acr=['CARDC']),
 'I4392738141': 'I2802505932',
 'I4405277710': dict(p=[r'china academ\w* (of )?electronics (and )?information technology', r'\bcaeit\b', '中国电子科学研究院'], acr=['CAEIT']),
 'I202334528': dict(p=[r'beijing electronic science (and )?technology institute', r'\bbesti\b'], acr=['BESTI']),
 'I67636235': dict(p=[r'university (of )?international relations', '国际关系学院'], acr=['UIR'], ctx=True),
 'I4210119087': dict(p=[r'north china institute (of )?aerospace', r'\bnciae\b'], acr=['NCIAE']),
 'I4210094568': dict(p=[r'sattari'], acr=[]),
 'I4210086765': dict(p=[r'aerospace research institute'], acr=[], ctx=True),
 'I120234788': dict(p=[r'imam (hossein|hussein|hosein|husain|hossain|husein) (comprehensive )?university'], acr=[], neg=[r'hospital', r'medical (center|centre)']),
 'I4401200389': dict(p=[r'dalian naval academy', '大连舰艇学院'], acr=[]),
 'I4402554050': dict(p=[r'army command (college|academy)', '陆军指挥学院'], acr=[], ctx=True),
 'I4402554129': dict(p=[r'(pap|armed police) (nco|non commissioned officer)', r'non commissioned officer (school|academy|college) (of )?(the )?(pap|chinese people s armed police)', '武装警察部队士官学校'], acr=[]),
 'I4403386709': dict(p=[r'rocket force (research|equipment) (institute|academy)', r'second artillery equipment', r'rocket force academy', '火箭军研究院', '火箭军装备研究院'], acr=[], ctx=True),
 'I4401200391': dict(p=[r'rocket (force )?(sergeant|sergeancy|nco)', '火箭军士官学校'], acr=[]),
 'I4387155616': dict(p=[r'navy submarine academy', '海军潜艇学院'], acr=[]),
 'I4402554106': dict(p=[r'nav(y|al) research academy', r'navy equipment academy', r'naval equipment academy', r'naval research institute of pla', '海军研究院', '海军装备研究院'], acr=[], ctx=True),
 'I4402554066': dict(p=[r'xian fl(ight|ying) (academy|college)', '空军西安飞行学院'], acr=[]),
 'I4402554061': dict(p=[r'communication(s)? nco academy', r'air force communication non commissioned', '空军通信士官学校'], acr=[]),
 'I4402554119': dict(p=[r'harbin fl(ight|ying) (academy|college)', '空军哈尔滨飞行学院'], acr=[]),
 'I4402553999': dict(p=[r'army infantry (academy|college)', r'nanchang army academy', '陆军步兵学院'], acr=[]),
 'I79995938': dict(p=[r'china people s police university', r'\bcppu\b', '中国人民警察大学'], acr=['CPPU']),
 'I4402553996': dict(p=[r'jiangnan social', r'jiangnan institute (of )?social', '江南社会学院'], acr=[]),
 'I4403386620': dict(p=[r'46(th)? (central|tsnii|ts nii)', r'46 tsnii'], acr=[]),
}
# resolve child -> parent alias sets
def alias(i):
    v = A.get(i)
    while isinstance(v, str): v = A.get(v)
    return v
NRO_COUNTRY = {}

def compile_aliases():
    out = {}
    for i, v in A.items():
        if isinstance(v, dict):
            out[i] = dict(p=[re.compile(x) for x in v['p']], acr=[re.compile(r'(?<![A-Za-z])' + re.escape(a) + r'(?![A-Za-z])') for a in v.get('acr', [])],
                          ctx=v.get('ctx', False), neg=[re.compile(x) for x in v.get('neg', [])], medctx=v.get('medctx', False))
    return out
CA_ = compile_aliases()

EMAIL = re.compile(r'\S+@\S+')
MEDCTX = re.compile(r"\b(hospital|medical|medicine|dental|dentistry|pharmacy|pharmaceutical|nursing|midwifery|paramedical|clinical|health|cancer|surgery|pediatric|paediatric|endocrine|gastroenterology|urology|nephrology|ophthalm\w*|cardiovascular|tuberculosis|infectious|virology|student research committee|students research committee|rehabilitation|nutrition|toxicology|neuroscience research center|proteomics research center|medical physics|loghman|taleghani|modarres|tajrish|mofid|imam hossein hospital|labbafinejad|masih daneshvari)\b")
# Shahid Beheshti University's own (non-SBMU) units whose names contain medical/health words
SBU_UNITS = re.compile(r"(sports? sciences? (and )?health|sport rehabilitation and health|biological sciences in sports?( and health)?|medical radiation engineering|radiation medicine engineering|institute (of )?medical science (and )?technology|\bimsat\b|family research institute|family health department|clinical (child and adolescent |and health )?psychology|faculty of education and psychology|faculty of physical education and health sciences|exercise physiology|motor behaviou?r|psychology|faculty of human sciences?)")
def names_nro(raw, key, country):
    """key = alias-set id (parent). Returns (status, how): status in pass/fail; how explains."""
    raw = EMAIL.sub(' ', raw)
    v = CA_[key]; n = norm(raw)
    ctx = CTX[country].search(n) is not None
    if v['medctx']:
        # evaluate each ';'-segment: the medical-context test applies to the segment naming the university
        best, sbmu = None, False
        for seg in n.split(';'):
            if any(ng.search(seg) for ng in v['neg']): sbmu = True; continue
            hit = next((p.pattern for p in v['p'] if p.search(seg)), None)
            if not hit: continue
            if MEDCTX.search(SBU_UNITS.sub(' ', seg)):
                best = best or ('ambiguous', f'name match ({hit}) in a medical-school/hospital context (Shahid Beheshti University of Medical Sciences?)')
            elif not ctx and FOREIGN.search(n): best = best or ('fail', f'name match ({hit}) but string places it in another country')
            else: return 'pass', hit
        if best: return best
        return ('fail', 'names Shahid Beheshti University of Medical Sciences (SBMU), a different university') if sbmu else ('fail', 'string does not name the NRO')
    for ng in v['neg']:
        if ng.search(n): return 'fail', f'names a different organization ({ng.pattern})'
    hit = next((p.pattern for p in v['p'] if p.search(n)), None)
    if not hit:
        a = next((p.pattern for p in v['acr'] if p.search(raw)), None)
        if a and ctx: hit = 'acronym ' + a.split('(?<![A-Za-z])')[-1].split('(?!')[0].replace('\\', '')
    if not hit: return 'fail', 'string does not name the NRO'
    if v['ctx'] and not ctx: return 'ambiguous', f'generic name ({hit}) without {country} context'
    if not ctx and FOREIGN.search(n): return 'fail', f'name match ({hit}) but string places it in another country'
    return 'pass', hit

# ---------------------------------------------------------------- Canada
CA_STRONG = re.compile(r"\b(canada|ontario|quebec|british columbia|alberta|manitoba|saskatchewan|nova scotia|new brunswick|newfoundland|prince edward island|yukon|nunavut|northwest territories|toronto|montreal|vancouver|ottawa|calgary|edmonton|winnipeg|saskatoon|sherbrooke|fredericton|moncton|charlottetown|kelowna|burnaby|mississauga|guelph|gatineau|trois rivieres|rimouski|chicoutimi|sudbury|thunder bay|lethbridge|kamloops|kitchener|oshawa|scarborough|etobicoke|longueuil|nanaimo|antigonish|wolfville|mcgill|mcmaster|dalhousie|simon fraser|university of waterloo|waterloo (, )?on|laval university|universite laval|polytechnique montreal|uqam|uqac|uqtr|inrs|universite du quebec|sunnybrook|sickkids|hospital for sick children|princess margaret|lunenfeld|perimeter institute|triumf|wilfrid laurier|lakehead|ryerson|toronto metropolitan|carleton university|memorial university|university of manitoba|university of regina|university of victoria|university of windsor|university of guelph|university of saskatchewan|university of alberta|university of calgary|university of ottawa|university of toronto|university of british columbia|western university|university of western ontario|queen s university|york university|concordia university|brock university|trent university|ontario tech|uoit|unbc|cnrc|nrc canada|national research council canada|agriculture and agri food|natural resources canada|health canada|fisheries and oceans|environment and climate change canada|mila|vector institute|fields institute|centre hospitalier|chu de quebec|chum|sainte justine|ste justine|lady davis|douglas hospital|montreal neurological|mcgill university health|bc cancer|vancouver general|st paul s hospital (, )?vancouver|alberta health|ottawa hospital|hamilton health sciences|london health sciences|lawson health|robarts|population health research institute|ivey|rotman|schulich|sauder|telfer|haskayne|desautels|hec montreal|ets montreal|ecole de technologie superieure|universite de montreal|universite de sherbrooke|universite de moncton|university of new brunswick|university of prince edward island|mount allison|st francis xavier|acadia university|saint mary s university|university of northern british columbia|thompson rivers|university of lethbridge|athabasca|royal military college of canada|bishop s university|nipissing|laurentian|algoma|university of ontario|kwantlen|ubc|utoronto|ualberta|ucalgary|uottawa|umanitoba|usask|uwaterloo|uwo|mcmaster ca|mail mcgill)\b")
CA_POST = re.compile(r"\b[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d\b")
CA_WEAK = re.compile(r",\s*(ON|QC|BC|AB|MB|SK|NS|NB|NL|PE|PQ|YT|NT|NU)\b(?!\w)|\bcanadian\b|\.ca\b", re.I)

CA_FA = re.compile('کانادا|تورنتو|مونترال|ونکوور|بریتیش کلمبیا|مک‌گیل|مک گیل')
CA_LOOSE = re.compile(r'canada|toronto|montreal|vancouver|ottawa|calgary|edmonton|winnipeg|quebec|mcmaster|universityofwindsor|univeristyofwindsor|ontario')
def names_canada(raw, inst_names):
    raw = EMAIL.sub(' ', raw)
    n = norm(raw)
    if CA_STRONG.search(n) or CA_POST.search(raw): return 'pass', 'Canadian place/institution named'
    weak = CA_WEAK.search(raw)
    nm = next((x for x in inst_names if x and len(x) > 6 and (' ' + x + ' ') in n), None)
    foreign = FOREIGN.search(n) or CN_CTX.search(n) or IR_CTX.search(n)
    if foreign and not weak:
        return 'fail', 'string places the affiliation outside Canada (mis-geocoded to a CA institution)'
    if weak and not foreign: return 'pass', 'Canadian province code/domain'
    if nm and not foreign: return 'pass', f'names the Canadian institution ({nm.strip()})'
    if CA_FA.search(raw): return 'pass', 'Canadian place named (Persian)'
    if CA_LOOSE.search(n.replace(' ', '')) and not foreign: return 'pass', 'Canadian place named (run-together string)'
    return 'ambiguous', 'no clear Canadian marker'

# ---------------------------------------------------------------- work-level checks
ERRATUM = re.compile(r'^\s*(correction|erratum|errata|corrigendum|retraction|notice of retraction|expression of concern|author correction|publisher correction|addendum)\b', re.I)
MEETING = re.compile(r'(annual meeting|meeting \d{4}|meeting:|conference on|congress|symposium|lives \d{4}: part|^\s*\d+(st|nd|rd|th) (annual|international))', re.I)
RETRACTED = re.compile(r'^\s*(retracted|withdrawn)\b', re.I)

def load():
    rows = [x for x in csv.DictReader(open(f'{D}/nro_map.csv')) if x['confidence'] in ('high', 'medium')]
    id2rows = collections.defaultdict(list)
    for x in rows:
        for i in [x['openalex_id']] + x['child_ids'].replace('|', ';').split(';'):
            i = i.strip()
            if i: id2rows[i].append(x)
    W = {}
    for p in sorted(glob.glob(f'{C}/works_*.jsonl.gz')):
        for l in gzip.open(p, 'rt'):
            w = json.loads(l); W[S(w['id'])] = w
    for p in glob.glob(f'{C}/full/*.json'):      # untruncated authorships for >=100-author works
        w = json.load(open(p))
        if S(w['id']) in W: W[S(w['id'])] = w
    M = json.load(open(f'{C}/institutions.json'))
    return rows, id2rows, W, M

def row_key(i):
    """alias-set id for NRO institution id i"""
    v = A.get(i)
    while isinstance(v, str): i, v = v, A.get(v)
    return i if v else None

def check_work(w, id2rows, M):
    nset = id2rows.keys()
    nro_links, ca_links = [], []          # (authorship idx, inst id, raw strings tied, all strings of authorship)
    names = [(a.get('author') or {}).get('display_name') or a.get('raw_author_name') or '' for a in w['authorships']]
    for k, a in enumerate(w['authorships']):
        raws = a.get('raw_affiliation_strings') or []
        affs = a.get('affiliations') or []
        for inst in a.get('institutions') or []:
            iid = S(inst['id'])
            lin = {S(x) for x in inst.get('lineage') or []} | {iid}
            tied = [f['raw_affiliation_string'] for f in affs if inst['id'] in (f.get('institution_ids') or [])]
            hits = sorted(lin & nset)
            if hits: nro_links.append((k, iid, hits, tied, raws))
            if inst.get('country_code') == 'CA': ca_links.append((k, iid, tied, raws))
    # ---- check a
    a_res = []   # (status, nro_row_id, raw, how, authorship)
    for k, iid, hits, tied, raws in nro_links:
        cands = tied or raws
        if not cands:
            a_res.append(('unverifiable', hits, '', 'no raw affiliation string', k)); continue
        best = None
        for raw in cands:
            for h in hits:
                key = row_key(h)
                rws = id2rows[h]
                st, how = names_nro(raw, key, rws[0]['country'])
                r = (st, [h], raw, how + ('' if tied else ' [string not tied to institution]'), k)
                if st == 'pass': best = r; break
                if best is None or (best[0] == 'fail' and st == 'ambiguous'): best = r
            if best and best[0] == 'pass': break
        if best[0] != 'pass':
            # does it name a *different* NRO?
            for raw in cands:
                for key in CA_:
                    rws = id2rows.get(key)
                    if not rws or key == row_key(hits[0]): continue
                    st, how = names_nro(raw, key, rws[0]['country'])
                    if st == 'pass':
                        best = ('pass', [key], raw, f'mis-mapped: string names {rws[0]["list_name"]} not {M.get(iid, {}).get("name")}', k); break
                if best[0] == 'pass': break
        a_res.append(best)
    # ---- check b
    b_res = []
    for k, iid, tied, raws in ca_links:
        m = M.get(iid, {})
        inames = [norm(m.get('name', '')).strip()] + [norm(x).strip() for x in m.get('alt', [])]
        cands = tied or raws
        if not cands:
            b_res.append(('unverifiable', iid, '', 'no raw affiliation string', k)); continue
        best = None
        for raw in cands:
            st, how = names_canada(raw, inames)
            r = (st, iid, raw, how + ('' if tied else ' [string not tied to institution]'), k)
            if st == 'pass': best = r; break
            if best is None or (best[0] == 'fail' and st == 'ambiguous') or (best[0] == 'unverifiable'): best = r
        b_res.append(best)
    # ---- check c
    c_st, c_why = 'pass', 'research article; CA and NRO evidence on this record'
    title = w.get('title') or ''
    if w.get('is_paratext'): c_st, c_why = 'fail', 'paratext'
    elif ERRATUM.search(title): c_st, c_why = 'fail', 'erratum/correction/retraction notice, not a research article'
    elif re.search(r'\b(corrigendum|erratum)\b', title, re.I): c_st, c_why = 'fail', 'corrigendum/erratum record, not a research article'
    elif len(w['authorships']) >= 100 and MEETING.search(title): c_st, c_why = 'fail', 'meeting-abstract compilation: authors belong to separate abstracts, not one paper'
    elif RETRACTED.search(title): c_st, c_why = 'fail', 'record is a retracted/withdrawn article (title prefixed RETRACTED/WITHDRAWN)'
    elif not title.strip(): c_st, c_why = 'ambiguous', 'no title'
    else:
        nm = [re.sub(r'[^a-z]', '', x.lower()) for x in names if x]
        dup = [x for x, c in collections.Counter(nm).items() if c > 1 and len(x) > 3]
        if len(dup) >= 3 and len(dup) >= 0.25 * len(set(nm)):
            c_st, c_why = 'ambiguous', f'author list repeats {len(dup)} names (possible merged/duplicated record)'
    return a_res, b_res, c_st, c_why

def linked_ids(w, id2rows):
    """every mapped NRO id (institution or its lineage) on any authorship of the work"""
    out = set()
    for a in w['authorships']:
        for inst in a.get('institutions') or []:
            out |= ({S(x) for x in inst.get('lineage') or []} | {S(inst['id'])}) & id2rows.keys()
    return sorted(out)

def agg(res):
    sts = [r[0] for r in res]
    if 'pass' in sts: return 'pass'
    if 'ambiguous' in sts: return 'ambiguous'
    if not sts or all(s == 'unverifiable' for s in sts): return 'unverifiable'
    if 'fail' in sts: return 'fail'
    return 'unverifiable'

def main():
    if '--pull' in sys.argv:
        os.system(f'{sys.executable} verify_nro_pull.py')
    rows, id2rows, W, M = load()
    name_of = {x['openalex_id']: x['list_name'] for x in rows}
    # parent row for any NRO id (for reporting): all rows containing it
    # duplicates among candidates: same normalised title, same year (+-1), overlapping author surnames
    bytitle = collections.defaultdict(list)
    for wid, w in W.items():
        t = re.sub(r'[^a-z0-9]', '', (w.get('title') or '').lower())
        if len(t) >= 25: bytitle[t].append(wid)
    dup_of = {}
    for t, ids in bytitle.items():
        if len(ids) < 2: continue
        def sn(w): return {((a.get('author') or {}).get('display_name') or '').split(' ')[-1].lower() for a in W[w]['authorships']}
        ids = sorted(ids, key=lambda i: (W[i].get('doi') is None, -len(W[i]['authorships']), int(i[1:])))
        keep = ids[0]
        for o in ids[1:]:
            if abs((W[o].get('publication_year') or 0) - (W[keep].get('publication_year') or 0)) <= 1 and len(sn(o) & sn(keep)) >= max(1, min(len(sn(o)), len(sn(keep))) // 2):
                dup_of[o] = keep
    manual = {}
    mp = f'{D}/nro_verification_manual.csv'
    if os.path.exists(mp):
        for r in csv.DictReader(open(mp)): manual[r['work_id']] = r
    out = []
    for wid in sorted(W, key=lambda i: (W[i]['publication_year'], int(i[1:]))):
        w = W[wid]
        a_res, b_res, c_st, c_why = check_work(w, id2rows, M)
        if wid in dup_of: c_st, c_why = 'fail', f'duplicate record of {dup_of[wid]} (same title/authors)'
        a, b = agg(a_res), agg(b_res)
        ap = [r for r in a_res if r[0] == 'pass'] or [r for r in a_res if r[0] == a] or a_res
        bp = [r for r in b_res if r[0] == 'pass'] or [r for r in b_res if r[0] == b] or b_res
        # c: CA and NRO evidence must be on this work's authorships (always true for tied strings); note dual affiliation
        if c_st == 'pass' and a == 'pass' and b == 'pass':
            ak = {r[4] for r in ap}; bk = {r[4] for r in bp}
            if ak == bk and len(ak) == 1: c_why = 'research article; CA and NRO on the same author (dual affiliation)'
        verified_ids = sorted({i for r in ap for i in r[1]}) if a == 'pass' else sorted({h for r in a_res for h in r[1]})
        if a == 'fail' or b == 'fail' or c_st == 'fail': verdict = 'false_positive'
        elif a == 'pass' and b == 'pass' and c_st == 'pass': verdict = 'verified'
        elif 'ambiguous' in (a, b, c_st): verdict = 'review'
        else: verdict = 'unverifiable'
        reason = []
        if a != 'pass': reason.append('NRO: ' + (ap[0][3] if ap else 'none'))
        if b != 'pass': reason.append('CA: ' + (bp[0][3] if bp else 'no CA authorship'))
        if c_st != 'pass': reason.append('work: ' + c_why)
        if a == 'pass' and any('mis-mapped' in r[3] for r in ap) and not any('mis-mapped' not in r[3] for r in ap): reason.append('NRO attribution corrected: ' + ap[0][3])
        rec = dict(work_id=wid, year=w['publication_year'], nro_ids=';'.join(verified_ids),
                   nro_names='; '.join(sorted({id2rows[i][0]['list_name'] if i in id2rows else i for i in verified_ids})),
                   nro_raw_strings=' || '.join(sorted({r[2] for r in ap if r[2]}))[:2000],
                   ca_raw_strings=' || '.join(sorted({r[2] for r in bp if r[2]}))[:2000],
                   check_a=a, check_b=b, check_c=c_st, verdict=verdict, reason=' | '.join(reason) or ('all checks pass; CA and NRO only on the same author (dual affiliation)' if 'dual affiliation' in c_why else 'all checks pass'),
                   n_authors=len(w['authorships']), is_retracted=w.get('is_retracted'), linked_nro_ids=';'.join(linked_ids(w, id2rows)),
                   title=(w.get('title') or '')[:300])
        if wid in manual:
            m = manual[wid]
            for f in ('check_a', 'check_b', 'check_c', 'nro_ids'):
                if m.get(f): rec[f] = m[f]
            if rec['nro_ids'] != ';'.join(verified_ids):
                rec['nro_names'] = '; '.join(sorted({id2rows[i][0]['list_name'] for i in rec['nro_ids'].split(';') if i in id2rows}))
            rec['verdict'] = m['verdict']; rec['reason'] = 'manual review: ' + m['reason']
        out.append(rec)
    cols = ['work_id', 'year', 'nro_ids', 'nro_names', 'nro_raw_strings', 'ca_raw_strings', 'check_a', 'check_b', 'check_c', 'verdict', 'reason', 'n_authors', 'is_retracted', 'linked_nro_ids', 'title']
    with open(f'{D}/nro_verification.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, cols); wr.writeheader(); wr.writerows(out)
    # Published, reduced copy (no raw affiliation strings or titles): the file the analysis scripts read
    vcols = ['work_id', 'year', 'nro_ids', 'check_a', 'check_b', 'check_c', 'verdict']
    with open(f'{D}/nro_verification_verdicts.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, vcols, extrasaction='ignore'); wr.writeheader(); wr.writerows(out)
    cnt = collections.Counter(r['verdict'] for r in out)
    print(len(out), dict(cnt))

if __name__ == '__main__':
    main()

# ---------------------------------------------------------------- summary statistics
def stats():
    rows, id2rows, W, M = load()
    V = {r['work_id']: r for r in csv.DictReader(open(f'{D}/nro_verification.csv'))}
    out = {'by_verdict': collections.Counter(r['verdict'] for r in V.values())}
    out['by_year'] = {}
    for r in V.values():
        out['by_year'].setdefault(r['year'], collections.Counter())[r['verdict']] += 1
    out['by_team'] = {}
    for r in V.values():
        k = '<51 authors' if int(r['n_authors']) < 51 else '51+ authors'
        out['by_team'].setdefault(k, collections.Counter())[r['verdict']] += 1
    # per list entry (row) and per OpenAlex ID: link-level support
    row_of = collections.defaultdict(set)
    for i, rs in id2rows.items():
        for x in rs: row_of[i].add(x['list_name'])
    per_row = collections.defaultdict(lambda: collections.Counter()); per_id = collections.defaultdict(lambda: collections.Counter())
    for wid, w in W.items():
        a_res, b_res, c_st, c_why = check_work(w, id2rows, M)
        v = V[wid]
        linked = set(v['linked_nro_ids'].split(';')) - {''}
        ok_ids = set(v['nro_ids'].split(';')) - {''} if v['verdict'] == 'verified' else set()
        ok_rows = {n for i in ok_ids for n in row_of.get(i, ())}
        for i in linked:
            per_id[i]['linked'] += 1; per_id[i]['supported' if i in ok_ids else 'unsupported'] += 1
            per_id[i]['work_verified'] += v['verdict'] == 'verified'
        for n in {n for i in linked for n in row_of.get(i, ())}:
            per_row[n]['linked_works'] += 1
            per_row[n]['verified_works_any_nro'] += v['verdict'] == 'verified'
            per_row[n]['verified_this_nro'] += n in ok_rows
            per_row[n][v['verdict']] += 1
    out['per_row'] = {k: dict(c) for k, c in per_row.items()}
    # child IDs: works that reach a list entry ONLY through that child (main ID absent), and how many verify for the entry
    child = collections.defaultdict(lambda: collections.Counter())
    for x in rows:
        kids = [c.strip() for c in x['child_ids'].replace('|', ';').split(';') if c.strip()]
        for v in V.values():
            linked = set(v['linked_nro_ids'].split(';'))
            if x['openalex_id'] in linked: continue
            ok_rows = {n for i in v['nro_ids'].split(';') for n in row_of.get(i, ())} if v['verdict'] == 'verified' else set()
            for k in kids:
                if k in linked:
                    c = child[f"{x['list_name']} <- {k} {M.get(k, {}).get('name')}"]
                    c['works_only_via_child'] += 1; c['verified_for_entry'] += x['list_name'] in ok_rows
    out['child_only'] = {k: dict(c) for k, c in child.items()}
    out['per_id'] = {k: dict(c, name=M.get(k, {}).get('name')) for k, c in per_id.items()}
    # NRO country split (CN vs IR vs RU), works
    ctry = {i: rs[0]['country'] for i, rs in id2rows.items()}
    out['by_country'] = {}
    for v in V.values():
        cs = {ctry[i] for i in v['linked_nro_ids'].split(';') if i in ctry}
        for c in cs:
            out['by_country'].setdefault(c, collections.Counter())[v['verdict']] += 1
    # China NRO works per year (what the China analyses use): candidates vs verified-with-a-Chinese-NRO
    out['cn_by_year'] = {}
    for v in V.values():
        if not any(ctry.get(i) == 'CN' for i in v['linked_nro_ids'].split(';')): continue
        c = out['cn_by_year'].setdefault(v['year'], collections.Counter()); c['candidates'] += 1
        c['verified_cn'] += v['verdict'] == 'verified' and any(ctry.get(i) == 'CN' for i in v['nro_ids'].split(';'))
    # false-positive reasons
    fp = collections.Counter()
    for v in V.values():
        if v['verdict'] != 'false_positive': continue
        rs = v['reason']
        if 'meeting-abstract' in rs or 'Spine Society' in rs: k = 'work: meeting-abstract compilation'
        elif 'duplicate record' in rs: k = 'work: duplicate record (translated edition, co-publication, abstract reprint)'
        elif 'retracted/withdrawn' in rs: k = 'work: retracted/withdrawn article'
        elif 'erratum' in rs or 'corrigendum' in rs or 'citation of another paper' in rs: k = 'work: erratum/corrigendum/retraction notice'
        elif 'SBMU' in rs or ('Shahid Beheshti' in v['nro_raw_strings'] and 'Medical' in v['nro_raw_strings'] and v['check_a'] == 'fail'): k = 'NRO: Shahid Beheshti Univ. of Medical Sciences string matched to Shahid Beheshti Univ.'
        elif v['check_a'] == 'fail' and 'Collaborative Innovation Center' in v['nro_raw_strings']: k = 'NRO: joint Nankai-Tianjin centre string (Nankai author) matched to Tianjin University'
        elif v['check_a'] == 'fail': k = 'NRO: other string that does not name the NRO'
        elif v['check_b'] == 'fail': k = 'CA: foreign string mis-geocoded to a Canadian institution'
        else: k = 'other: ' + rs[:60]
        fp[k] += 1
    out['fp_patterns'] = fp
    json.dump(out, open(f'{D}/nro_verification_stats.json', 'w'), indent=1, default=dict)
    return out

if __name__ == '__main__' and '--stats' in sys.argv:
    o = stats()
    print(json.dumps({k: o[k] for k in ('by_verdict', 'by_team', 'by_country', 'fp_patterns')}, indent=1, default=dict))
