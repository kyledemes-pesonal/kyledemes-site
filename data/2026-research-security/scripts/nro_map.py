"""Map Canada's Named Research Organizations (STRAC policy) list to OpenAlex institution IDs.

Inputs : results/nro_list_saved.json (from parse_nro.py on the saved page; live page re-parsed to
         nro_list_live.json and compared: identical 103 entries, dateModified 2024-04-18).
Output : results/nro_map.csv  (+ results/nro_map_verify.txt, a dump of each matched record for review)

The mapping itself is CURATED below (MAP): candidate IDs were found with nro_candidates.py,
OpenAlex /institutions search (English + Chinese names), the ROR API, and raw-affiliation-string
checks; this script re-fetches every ID live, fills ROR/display_name/works_count, and lists children.

Confidence:
  high   - the OpenAlex record IS this organization (name/alias/ROR checked)
  medium - same organization under a predecessor/variant name, or a record known to be incomplete
  low    - no own record; mapped to the NEAREST PARENT as a proxy (do NOT count it with lineage as
           if it were the NRO) or to a record that mixes several entities
  none   - nothing usable in OpenAlex; use raw_affiliation_query (raw_affiliation_strings.search)

child_ids: OpenAlex lineage descendants (filter lineage:<id>, excl. self) PLUS, after a '|',
  units the NRO list names as aliases/sub-units that OpenAlex does NOT put in the lineage
  (count these separately / union them in).
"""
import csv, json, sys, time
sys.path.insert(0, '.')
from oa import get

D = '../results/'
LIST_VERSION = 'STRAC NRO list, dateModified 2024-04-18 (live page re-checked 2026-11-16: unchanged)'

PLA, PLAAF, PAP, AMS = 'I4210160531', 'I4402554004', 'I4396570617', 'I4210158522'
RUMOD, MPS = 'I4210150315', 'I1302611135'

# list_name -> (openalex_id or None, confidence, note, extra_alias_unit_ids, raw_affiliation_query)
MAP = {
 # ---------------- Russia
 'A.A. Kharkevich Institute for Information Transmission Problems, IITP, Russian Academy of Sciences':
   ('I4210107660', 'high', 'Institute for Information Transmission Problems (RAS); ROR 013w2d378', [], ''),
 'Autonomous Noncommercial Organization Professional Association of Designers of Data Processing Systems':
   (None, 'none', 'ANO PO KSI: professional association, no OpenAlex/ROR record', [], '"Designers of Data Processing Systems"'),
 '27th Scientific Center of the Russian Ministry of Defense':
   ('I4210156133', 'low', 'OpenAlex only has "27th Central Research Institute of the MoD" (27 TsNII, a different MoD institute); its 55-63 works mix 27 TsNII, the 27th Scientific Center (Zelinsky, chemical) and even 48 TsNII. Most 27th Sci Center papers sit only under MoD parent I4210150315. Use raw-affiliation search.', [], '"27th Scientific Center" OR "27 Scientific Center" OR "27 Scientific Centre"'),
 '33rd Scientific Research and Testing Institute':
   (RUMOD, 'low', 'No own record; nearest parent = Ministry of Defence of the Russian Federation (proxy only). Raw strings "33 Central Research Test(ing) Institute" ~24 works, assigned to MoD or (wrongly) to 46 TsNII.', [], '"33 Central Research" OR "33rd Central Research"'),
 '46th TSNII Central Scientific Research Institute':
   ('I4403386620', 'high', '46th Central Research Institute of the MoD RF (alt "46th TSNII Central Sci..."), child of MoD RF; small (84 works) and also absorbs some 33 TsNII strings', [], ''),
 '48th Central Scientific Research Institute':
   (RUMOD, 'low', 'No own record; nearest parent = MoD RF (proxy). ~40+ works with "48(th) Central Research Institute" raw strings are mostly unassigned or mis-assigned (some to 27 TsNII I4210156133).', [], '"48th Central Research Institute" OR "48 Central Research Institute" OR "48 Central Scientific Research Institute"'),
 # ---------------- Iran
 'Aerospace Research Institute':
   ('I4210086765', 'high', 'Aerospace Research Institute (Tehran, Ministry of Science) ROR 000m4se28', [], ''),
 'Baghyatollah Medical Sciences University':
   ('I120514687', 'high', 'Baqiyatallah University of Medical Sciences (IRGC-linked)', [], ''),
 'Defence Industries Organization Training and Research Institute':
   (None, 'none', 'DIO Training & Research Institute (DRTI): no OpenAlex/ROR record', [], '"Defence Industries Training and Research Institute" OR "Defense Industries Training and Research Institute"'),
 'Explosion and Impact Technology Research Centre':
   ('I78323350', 'low', 'METFAZ has no record; nearest = Malek Ashtar University of Technology (its host). NOTE Malek Ashtar itself is NOT on the Canadian list: proxy only, do not count MUT as an NRO.', [], '"Explosion and Impact" OR METFAZ'),
 'Imam Hossein University':
   ('I120234788', 'high', 'Imam Hossein (Comprehensive) University, IRGC; not Imam Hossein Hospital (I4210159370)', [], ''),
 'Institute of Applied Physics':
   (None, 'none', 'Iranian IAP (SPND-linked): no OpenAlex/ROR record; generic name - raw search needs Iran/Tehran qualifier', [], '"Institute of Applied Physics" AND Tehran'),
 'Iranian Research Organization for Science and Technology':
   ('I2802500176', 'high', 'IROST, ROR 017zx9g19', [], ''),
 'Pasteur Institute of Iran':
   ('I1301411061', 'high', 'Pasteur Institute of Iran, ROR 00wqczk30', [], ''),
 'Physics Research Center':
   (None, 'none', 'PHRC (historic nuclear-weapons-linked centre): no record; not IPM/Institute for Research in Fundamental Sciences', [], '"Physics Research Center" AND Tehran'),
 'Shahid Beheshti University':
   ('I48379061', 'high', 'Shahid Beheshti University (ROR 0091vmj44). NOT Shahid Beheshti University of Medical Sciences (I58048189), which is a separate institution and not listed', [], ''),
 'Shahid Sattari Air Force University':
   ('I4210094568', 'high', 'Shahid Sattari University of Aeronautical Engineering (alt Shahid Sattari Aeronautical University)', [], ''),
 'Sharif University of Technology':
   ('I133529467', 'high', 'Sharif University of Technology', [], ''),
 # ---------------- China: PLA / AMS
 'Academy of Military Medical Sciences':
   ('I2802541053', 'high', 'AMMS (军事医学科学院); since 2017 part of the Academy of Military Science, but OpenAlex has no lineage link to AMS', [], ''),
 'Academy of Military Science':
   ('I4210158522', 'high', 'PLA Academy of Military Science (军事科学院). OpenAlex does not nest AMMS (I2802541053) under it: union them if counting AMS as a system', ['I2802541053'], ''),
 'Air Force Medical University':
   ('I9916479', 'high', 'Fourth Military Medical University; affiliated hospitals (Xijing, Tangdu) mostly separate records not in lineage', [], ''),
 'Air Force Research Institute':
   (PLAAF, 'low', 'No own record; nearest parent = PLA Air Force (proxy only)', [], '"Air Force Research Institute" AND China'),
 'Air Force Xi’an Flight Academy':
   ('I4402554066', 'high', "PLA Air Force Xi'an Flying College (child of PLAAF)", [], ''),
 'Airforce Command College':
   (PLAAF, 'low', 'No own record; nearest parent = PLA Air Force (proxy only)', [], '"Air Force Command College"'),
 'Airforce Communication NCO Academy':
   ('I4402554061', 'high', 'Air Force Communication NCO Academy (Dalian), child of PLAAF', [], ''),
 'Airforce Early Warning Academy':
   (PLAAF, 'low', 'No own record (Wuhan Radar Institute / Air Force Early Warning Academy); nearest parent = PLA Air Force (proxy)', [], '"Early Warning Academy" OR "Air Force Radar Academy"'),
 'Airforce Engineering University':
   ('I4210104252', 'high', 'Air Force Engineering University (Xi\'an), 空军工程大学', [], ''),
 'Airforce Flight Academy Shijiazhuang':
   (PLAAF, 'low', 'No own record; nearest parent = PLA Air Force (proxy)', [], '"Shijiazhuang Flight" OR "Shijiazhuang Flying"'),
 'Airforce Harbin Flight Academy':
   ('I4402554119', 'high', 'Air Force Harbin Flying College', [], ''),
 'Airforce Logistics University':
   (PLAAF, 'low', 'No own record (Xuzhou, 空军勤务学院/空军后勤学院); nearest parent = PLA Air Force (proxy)', [], '"Air Force Logistics" AND Xuzhou'),
 'Army Academy of Armored Forces':
   (PLA, 'low', 'No own record (Academy of Armored Force Engineering); nearest parent = PLA (proxy)', [], '"Armored Force" OR "Armoured Force" OR "Army Academy of Armored Forces"'),
 'Army Academy of Artillery and Air Defense':
   (PLA, 'low', 'No own record (Hefei; former Army Officer Academy / Artillery Academy); nearest parent = PLA (proxy)', [], '"Artillery and Air Defense" OR "Army Officer Academy"'),
 'Army Academy of Border and Coastal Defense':
   (PLA, 'low', 'No own record; nearest parent = PLA (proxy)', [], '"Border and Coastal Defense"'),
 'Army Aviation College':
   (PLA, 'low', 'No own record; nearest parent = PLA (proxy). Do NOT confuse with PLA Air Force Aviation University (I4210167232), a separate NRO', [], '"Army Aviation College" OR "Army Aviation Institute"'),
 'Army Engineering University':
   ('I4210163363', 'high', 'PLA Army Engineering University (Nanjing). Not Shijiazhuang Tiedao Univ.', [], ''),
 'Army Infantry Academy':
   ('I4402553999', 'high', 'Army Infantry College of PLA (Nanchang), child of PLA', [], ''),
 'Army Medical University':
   ('I151075929', 'high', 'Army Medical University = Third Military Medical University; Southwest/Xinqiao/Daping hospitals are separate records not in lineage', [], ''),
 'Army Military Transportation Academy':
   ('I4210167189', 'high', 'Academy of Military Transportation (军事交通学院)', [], ''),
 'Army Research Institute':
   (PLA, 'low', 'No own record (陆军研究院); nearest parent = PLA (proxy)', [], '"Army Research Institute" AND China'),
 'Army Service Academy':
   ('I52604927', 'high', 'PLA Army Service Academy (former Logistical Engineering University, Chongqing)', [], ''),
 'Army Special Operations Academy':
   (PLA, 'low', 'No own record; nearest parent = PLA (proxy)', [], '"Special Operations Academy" OR "Special Operations College"'),
 'Aviation University of Air Force':
   ('I4210167232', 'high', 'PLA Air Force Aviation University (Changchun)', [], ''),
 'Dalian Naval Academy':
   ('I4401200389', 'high', 'PLA Dalian Naval Academy', [], ''),
 'Information Engineering University':
   ('I169689159', 'high', 'PLA Information Engineering University (Zhengzhou)', [], ''),
 'Institute of NBC Defense':
   (AMS, 'low', 'No own record (防化研究院, under the Academy of Military Science since 2017); nearest parent = AMS (proxy)', [], '"Institute of Chemical Defense" OR "Research Institute of Chemical Defense" OR "NBC Defense"'),
 'Key Laboratory of Information Systems Engineering':
   (None, 'none', 'KLISE: no record (the "State Key Laboratory of Information Security" I4391768012 is a different lab)', [], '"Information Systems Engineering Laboratory" OR "Key Laboratory of Information Systems Engineering"'),
 'Nanjing Army Command College':
   ('I4402554050', 'high', 'Army Command College (alt "Nanjing Army Command College"), child of PLA', [], ''),
 'National Defense University':
   ('I4405280021', 'high', 'PLA National Defence University (国防大学). NOT NUDT (I170215575), which is a separate NRO', [], ''),
 'National University of Defense Technology':
   ('I170215575', 'high', 'NUDT (国防科学技术大学), Changsha. Changsha Institute of Technology (I4405279573) is a separate small record, not in lineage; listed as an alias', ['I4405279573'], ''),
 'Naval Command College':
   (PLA, 'low', 'No own record; nearest parent = PLA (proxy)', [], '"Naval Command College" OR "Navy Command College"'),
 'Naval Petty Officer Academy':
   (PLA, 'low', 'No own record (Bengbu); nearest parent = PLA (proxy)', [], '"Petty Officer Academy" OR "Naval Petty Officer"'),
 'Naval Research Academy':
   ('I4402554106', 'high', 'Naval Research Academy (PLA Navy Research/Equipment Academy)', [], ''),
 'Naval University of Engineering':
   ('I2800710378', 'high', 'Naval University of Engineering (Wuhan)', [], ''),
 'Navy Aviation University':
   ('I4210162215', 'medium', 'Naval Aeronautical and Astronautical University (Yantai) = main predecessor merged into Naval Aviation University in 2017; list gives "Naval Aeronautics and Astronautics University" as alias', [], ''),
 'Navy Logistics Academy':
   (PLA, 'low', 'No own record (Tianjin); nearest parent = PLA (proxy)', [], '"Navy Logistics Academy" OR "Naval Logistics Academy"'),
 'Navy Medical University':
   ('I177933477', 'high', 'Second Military Medical University (alt "PLA Naval Medical University"); Changhai/Changzheng hospitals separate, not in lineage', [], ''),
 'Navy Submarine Academy':
   ('I4387155616', 'high', 'PLA Navy Submarine Academy (Qingdao), child of PLA', [], ''),
 'Rocket Force Command College':
   (PLA, 'low', 'No own record (Wuhan); nearest parent = PLA (proxy)', [], '"Rocket Force Command College"'),
 'Rocket Force Research Institute':
   ('I4403386709', 'high', 'PLA Rocket Force Research Institute (alt "Rocket Force Equipment Research Institute", "Second Artillery Equipment Academy")', [], ''),
 'Rocket Force Sergeant School':
   ('I4401200391', 'high', 'Rocket Force Sergeant School (6 works)', [], ''),
 'Rocket Force University of Engineering':
   ('I2801618472', 'high', 'PLA Rocket Force University of Engineering (former Second Artillery Engineering Univ., Xi\'an)', [], ''),
 'Space Engineering University':
   ('I4210148107', 'high', 'Space Engineering University (航天工程大学, Beijing)', [], ''),
 'China Aerodynamics Research and Development Center':
   ('I2802505932', 'high', 'CARDC, Mianyang', [], ''),
 'Northwest Institute of Nuclear Technology':
   ('I4210151975', 'high', 'NINT, Xi\'an', [], ''),
 # ---------------- China: PAP / police / state security
 'China Coast Guard Academy':
   (None, 'none', 'No record (Ningbo; former China Maritime Police Academy / 公安海警学院)', [], '"Coast Guard Academy" OR "Maritime Police Academy"'),
 'China People’s Police University':
   ('I79995938', 'high', 'China People\'s Police University (Langfang). Its OpenAlex alternatives include 中国人民武装警察部队学院 (former Chinese People\'s Armed Police Forces Academy), which the NRO list gives as an alias of "People\'s Armed Police Command College" - expect overlap', [], ''),
 'Criminal Investigation Police University of China':
   ('I4210158717', 'high', 'CIPUC (Shenyang)', [], ''),
 'Engineering University of the CAPF':
   ('I4210134428', 'high', 'Chinese People\'s Armed Police Force Engineering University (Xi\'an)', [], ''),
 'Jiangnan Social University':
   ('I4402553996', 'high', 'Jiangnan Social University (MSS-linked), 67 works', [], ''),
 'Logistics University of the People\'s Armed Police Force':
   ('I4210111482', 'high', 'Logistics University of PAP (Tianjin)', [], ''),
 'Ministry of Public Security\'s Institute of Forensic Science of China':
   (MPS, 'low', 'No own record; nearest parent = Ministry of Public Security (proxy). NOT "Institute of Forensic Science" I4210139944 (Ministry of Justice, Shanghai)', [], '"Institute of Forensic Science, Ministry of Public Security" OR "Forensic Identification Center of the Ministry of Public Security"'),
 'Officers College of the PAP':
   (PAP, 'low', 'No own record (Chengdu); nearest parent = Chinese People\'s Armed Police Force (proxy)', [], '"Officers College of PAP" OR "Armed Police Officers College" OR "Armed Police Officer Academy"'),
 'PAP NCO College':
   ('I4402554129', 'high', 'PAP Non-commissioned Officer School', [], ''),
 'People\'s Armed Police Command College':
   (PAP, 'low', 'No own record (Tianjin); nearest parent = PAP (proxy). Its alias "Chinese People\'s Armed Police Forces Academy" sits in OpenAlex as an alternative name of China People\'s Police University (I79995938)', [], '"Armed Police Command College"'),
 'People\'s Public Security University of China':
   ('I37448385', 'high', 'China People\'s Public Security University (PPSUC)', [], ''),
 'Railway Police College':
   ('I4405280979', 'high', 'Zhengzhou Police University (renamed Railway Police College; alt 铁道警察学院)', [], ''),
 'University of International Relations':
   ('I67636235', 'high', 'University of International Relations (Beijing, MSS-linked)', [], ''),
 # ---------------- China: CAEP / labs / CAS / industry
 'Beijing Computational Science Research Centre':
   ('I4210139958', 'high', 'Beijing Computational Science Research Center (CSRC); also a CAEP alias, not in CAEP lineage', [], ''),
 'Center for High Pressure Science and Technology Advanced Research':
   ('I4210143697', 'high', 'HPSTAR (Beijing HQ record I4210143697; Shanghai I4210141749 and another site I4210145869 are its OpenAlex children). Also a CAEP alias, not in CAEP lineage', [], ''),
 'Chengdu Fine Optical Engineering Research Center':
   ('I4402554102', 'high', 'Chengdu Fine Optical Engineering Research Center (CAEP alias; not in CAEP lineage)', [], ''),
 'Chinese Academy of Engineering Physics':
   ('I2801345734', 'high', 'CAEP (中国工程物理研究院). OpenAlex lineage children are few; listed CAEP alias units with SEPARATE records not in lineage are given after "|" in child_ids (IAPCM, CSRC, HPSTAR, Peac, Chengdu Fine Optical, CAEP Graduate School): union them for a CAEP-system count', ['I4210145278', 'I4210139958', 'I4210143697', 'I4210130940', 'I4402554102', 'I4405256023'], ''),
 'Peac Institute of Multiscale Science':
   ('I4210130940', 'high', 'Peac Institute of Multiscale Sciences (CAEP alias; not in CAEP lineage)', [], ''),
 'Hefei National Laboratory for Physical Sciences at Microscale':
   ('I4210103894', 'high', 'OpenAlex display name is wrong ("...at Nanoscale") but alternative 合肥微尺度物质科学国家实验室 and raw strings confirm it is HFNL Microscale; child of USTC. Many HFNL papers are probably assigned only to USTC (I126520041, NOT listed) - undercount likely', [], '"Physical Sciences at Microscale" OR "Physical Sciences at the Microscale"'),
 'China Academy of Science – Shenyang Institute of Automation':
   ('I142078773', 'high', 'Shenyang Institute of Automation, CAS (child of CAS)', [], ''),
 'Chinese Academy of Sciences Institute of Computing Technology':
   ('I4210090176', 'high', 'Institute of Computing Technology, CAS (not Shenyang/Shanghai Institutes of Computing Technology)', [], ''),
 'China Academy of Electronics and Information Technology':
   ('I4405277710', 'high', 'CAEIT, child of CETC (I2800372957)', [], ''),
 'Nanjing Institute of Information Technology':
   (None, 'none', 'Nanjing 841 Institute: no record. Not Nanjing Institute of Technology, Nanjing Univ. of Information S&T, or CETC 28th Institute', [], '"841 Institute" OR "Nanjing Research Institute of Information Technology"'),
 # ---------------- China: universities
 'Beihang University':
   ('I82880672', 'high', 'Beihang University (BUAA)', [], ''),
 'Beijing Electronic Science and Technology Institute':
   ('I202334528', 'high', 'BESTI', [], ''),
 'Beijing Institute of Technology':
   ('I125839683', 'high', 'Beijing Institute of Technology (not Univ. of S&T Beijing / Beijing Inst. of Petrochemical Tech.)', [], ''),
 'Beijing University of Posts and Telecommunications':
   ('I139759216', 'high', 'BUPT', [], ''),
 'Harbin Engineering University':
   ('I151727225', 'high', 'Harbin Engineering University (HEU) - separate NRO from HIT', [], ''),
 'Harbin Institute of Technology':
   ('I204983213', 'high', 'Harbin Institute of Technology (HIT) - separate NRO from HEU', [], ''),
 'Hunan University':
   ('I16609230', 'high', 'Hunan University (not Hunan Univ. of S&T / Technology / Normal)', [], ''),
 'Nanjing University of Aeronautics and Astronautics':
   ('I9842412', 'high', 'NUAA', [], ''),
 'Nanjing University of Science and Technology':
   ('I36399199', 'high', 'NJUST (not Nanjing Univ. of Information S&T)', [], ''),
 'North China Institute of Aerospace Engineering':
   ('I4210119087', 'high', 'NCIAE, Langfang', [], ''),
 'North University of China':
   ('I135714990', 'high', 'North University of China (Taiyuan) - not North China Univ. of S&T / Technology', [], ''),
 'Northwestern Polytechnical University':
   ('I17145004', 'high', 'NWPU', [], ''),
 'Sichuan University':
   ('I24185976', 'high', 'Sichuan University. West China Hospital (I4210089761) and other West China hospitals are separate records NOT in lineage; only West China Medical Center is a child', [], ''),
 'Tianjin University':
   ('I162868743', 'high', 'Tianjin University (not Tianjin Univ. of Technology / S&T / Medical Univ.)', [], ''),
 'University of Electronic Science and Technology of China':
   ('I150229711', 'high', 'UESTC', [], ''),
 "Xi'an Technological University":
   ('I4210110558', 'high', "Xi'an Technological University (西安工业大学) - NOT Xi'an University of Technology (西安理工大学)", [], ''),
}

SEL = 'id,display_name,display_name_alternatives,ror,works_count,type,country_code,lineage,associated_institutions'


def short(x):
    return x.split('/')[-1] if x else ''


def main():
    ents = json.load(open(D + 'nro_list_saved.json'))['entries']
    names = [e['list_name'] for e in ents]
    missing = [n for n in names if n not in MAP]
    extra = [n for n in MAP if n not in names]
    assert not missing and not extra, (missing, extra)
    rows, ver = [], []
    for e in ents:
        oid, conf, note, alias_units, rawq = MAP[e['list_name']]
        r = dict(list_name=e['list_name'], country=e['country'], list_version=LIST_VERSION,
                 openalex_id=oid or '', ror='', oa_display_name='', works_count='', confidence=conf,
                 child_ids='', note=note, raw_affiliation_query=rawq)
        if oid:
            i = get('/institutions/' + oid, select=SEL)
            assert i['country_code'] == e['country'], (e['list_name'], i['country_code'])
            r.update(ror=short(i['ror']), oa_display_name=i['display_name'], works_count=i['works_count'])
            if conf in ('high', 'medium'):
                kids = get('/institutions', filter='lineage:' + oid, per_page=200,
                           select='id,display_name,works_count')['results']
                kids = sorted([k for k in kids if short(k['id']) != oid], key=lambda k: -k['works_count'])
                lin = [short(k['id']) for k in kids]
                extra_ids = [a for a in alias_units if a not in lin]
                r['child_ids'] = ';'.join(lin) + ('|' + ';'.join(extra_ids) if extra_ids else '')
            ver.append(f"{e['list_name']} [{e['country']}] -> {oid} {conf}\n   OA: {i['display_name']} | ror {short(i['ror'])} | "
                       f"wc {i['works_count']} | {i['type']} | lineage {[short(x) for x in i['lineage']]}\n"
                       f"   alt: {'; '.join(i['display_name_alternatives'])[:300]}\n"
                       f"   list aliases: {'; '.join(e['aliases'])[:300]}\n   child_ids: {r['child_ids']}\n")
            time.sleep(0.05)
        rows.append(r)
    cols = ['list_name', 'country', 'list_version', 'openalex_id', 'ror', 'oa_display_name', 'works_count',
            'confidence', 'child_ids', 'note', 'raw_affiliation_query']
    with open(D + 'nro_map.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    open(D + 'nro_map_verify.txt', 'w').write('\n'.join(ver))
    from collections import Counter
    print(Counter((r['country'], r['confidence']) for r in rows))


if __name__ == '__main__':
    main()
