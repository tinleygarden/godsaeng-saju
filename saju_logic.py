import datetime
from saju_corrections import SajuCorrector

class SajuLogic:
    def __init__(self):
        self.CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        self.JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
        self.STEM_OHAENG = ['wood', 'wood', 'fire', 'fire', 'earth', 'earth', 'metal', 'metal', 'water', 'water']
        self.BRANCH_OHAENG = ['water', 'earth', 'wood', 'wood', 'earth', 'fire', 'fire', 'earth', 'metal', 'metal', 'earth', 'water']
        
        # Initialize Corrector (Skyfield)
        self.corrector = SajuCorrector()
        
        # 60 Gan-Zhi List
        self.GAN_ZHI_60 = []
        for i in range(60):
            self.GAN_ZHI_60.append(self.CHEONGAN[i % 10] + self.JIJI[i % 12])

    def get_gan_zhi(self, year, month, day, hour, minute, city='Seoul'):
        # Use SajuCorrector for precise astronomical calculation
        corrected = self.corrector.get_corrected_saju(year, month, day, hour, minute, city)
        
        # 1. Year Pillar
        # corrected['year_base'] is the year number (e.g. 2023 for 2024 before Lichun)
        calc_year = corrected['year_base']
        year_idx = (calc_year - 4) % 60
        year_gan_idx = year_idx % 10
        year_zhi_idx = year_idx % 12
        
        # 2. Month Pillar
        # corrected['month_idx'] (0=In, 1=Myo...)
        # We need Month Stem.
        # Year Stem determines Month Stem (Year Gan Index).
        # Formula: (year_gan_idx % 5 + 1) * 2?
        # Checked map:
        # year_gan=0(Gap) -> Month Start = 2 (Byeong-In). month_idx=0 -> 2.
        # Formula: (year_gan_idx % 5) * 2 + 2 + month_idx
        # Let's verify: Gap(0) -> Month0(In) = 2(Byeong). Correct.
        # Gi(5) -> Month0(In) = 2(Byeong). Correct.
        # Eul(1) -> Month0(In) = 4(Mu). Correct.
        
        month_idx_from_in = corrected['month_idx']
        month_start_stem = (year_gan_idx % 5) * 2 + 2
        month_gan_idx = (month_start_stem + month_idx_from_in) % 10
        
        # Month Zhi Index
        # month_idx=0 -> In(2).
        month_zhi_idx = (month_idx_from_in + 2) % 12
        
        # 3. Day Pillar
        # corrected['day_dt'] is the Solar Date (Standard Time 23:30 adjusted).
        # We calculate Day Gan-Zhi directly from ref date (2000-01-01).
        saju_day_dt = corrected['day_dt']
        ref_date = datetime.datetime(2000, 1, 1, 0, 0)
        # Using simple date diff is risky if times cross.
        # Just use .date() difference.
        
        # Wait, standard Python datetime subtraction might ignore leap seconds, which is fine.
        # But we need "Number of Days".
        delta_days = (saju_day_dt.date() - ref_date.date()).days
        
        day_cycle_idx = (54 + delta_days) % 60
        day_gan_idx = day_cycle_idx % 10
        day_zhi_idx = day_cycle_idx % 12
        
        # 4. Hour Pillar
        # corrected['hour_idx'] (0=Ja, 1=Chuk...)
        hour_zhi_idx = corrected['hour_idx']
        
        # Hour Stem
        # Formula: (day_gan_idx % 5) * 2 + hour_idx
        # Gap(0) Day -> Ja Hour = Gap-Ja (0). (0%5)*2 + 0 = 0. Correct.
        # Eul(1) Day -> Ja Hour = Byeong-Ja (2). (1%5)*2 + 0 = 2. Correct.
        hour_gan_idx = ((day_gan_idx % 5) * 2 + hour_zhi_idx) % 10

        return {
            'year': {'gan': self.CHEONGAN[year_gan_idx], 'zhi': self.JIJI[year_zhi_idx], 
                     'gan_idx': year_gan_idx, 'zhi_idx': year_zhi_idx,
                     'gan_element': self.STEM_OHAENG[year_gan_idx], 'zhi_element': self.BRANCH_OHAENG[year_zhi_idx]},
            'month': {'gan': self.CHEONGAN[month_gan_idx], 'zhi': self.JIJI[month_zhi_idx],
                      'gan_idx': month_gan_idx, 'zhi_idx': month_zhi_idx,
                     'gan_element': self.STEM_OHAENG[month_gan_idx], 'zhi_element': self.BRANCH_OHAENG[month_zhi_idx]},
            'day': {'gan': self.CHEONGAN[day_gan_idx], 'zhi': self.JIJI[day_zhi_idx],
                    'gan_idx': day_gan_idx, 'zhi_idx': day_zhi_idx,
                    'day_cycle_idx': day_cycle_idx,
                     'gan_element': self.STEM_OHAENG[day_gan_idx], 'zhi_element': self.BRANCH_OHAENG[day_zhi_idx]},
            'hour': {'gan': self.CHEONGAN[hour_gan_idx], 'zhi': self.JIJI[hour_zhi_idx],
                     'gan_idx': hour_gan_idx, 'zhi_idx': hour_zhi_idx,
                     'gan_element': self.STEM_OHAENG[hour_gan_idx], 'zhi_element': self.BRANCH_OHAENG[hour_zhi_idx]},
            'meta': {
                'utc_dt': corrected['utc'],
                'month_idx': month_idx_from_in,
                'year_gan_idx': year_gan_idx, # Useful for direction
                'year_base': calc_year
            }
        }

    def get_ohaeng_distribution(self, pillars):
        dist = {'wood': 0, 'fire': 0, 'earth': 0, 'metal': 0, 'water': 0}
        for key in ['year', 'month', 'day', 'hour']:
            dist[pillars[key]['gan_element']] += 1
            dist[pillars[key]['zhi_element']] += 1
        
        total = 8
        percentages = {k: round(v/total * 100, 1) for k, v in dist.items()}
        
        balance_text = "오행의 분포가 "
        max_elem = max(dist, key=dist.get)
        if dist[max_elem] >= 4:
            balance_text += f"{self._get_korean_elem(max_elem)} 기운이 매우 강합니다. "
        elif dist[max_elem] >= 3:
            balance_text += f"{self._get_korean_elem(max_elem)} 기운이 다소 강합니다. "
        else:
            balance_text += "비교적 고르게 분포되어 있습니다. "
            
        missing = [self._get_korean_elem(k) for k, v in dist.items() if v == 0]
        if missing:
            balance_text += f"부족한 기운은 {', '.join(missing)}이며, 보완이 필요할 수 있습니다."
            
        return {'counts': dist, 'percentages': percentages, 'balance_text': balance_text}

    def get_seun_list(self, start_year, count=10):
        seun_list = []
        for i in range(count):
            y = start_year + i
            cycle_idx = (y - 4) % 60
            gan_idx = cycle_idx % 10
            zhi_idx = cycle_idx % 12
            seun_list.append({
                'year': y,
                'gan': self.CHEONGAN[gan_idx],
                'zhi': self.JIJI[zhi_idx],
                'gan_element': self.STEM_OHAENG[gan_idx],
                'zhi_element': self.BRANCH_OHAENG[zhi_idx],
                'ten_god': '' # Can be filled if Day Master is known
            })
        return seun_list

    def get_wolun_list(self, year):
        # Calculate Year Gan Index
        year_cycle_idx = (year - 4) % 60
        year_gan_idx = year_cycle_idx % 10
        
        # Month Gan Start Index formula (Dunjigen): (YearGanIdx % 5) * 2 + 2 (conceptually)
        # 甲(0)/己(5) -> 丙(2)寅 start
        # 乙(1)/庚(6) -> 戊(4)寅 start
        # 丙(2)/辛(7) -> 庚(6)寅 start
        # 丁(3)/壬(8) -> 壬(8)寅 start
        # 戊(4)/癸(9) -> 甲(0)寅 start
        start_gan_idx = (year_gan_idx % 5) * 2 + 2
        
        wolun_list = []
        # Support 12 months starting from Feb (In-wol) which is the start of Saju year usually.
        # But simple calendar display: 
        # Feb(3), Mar(4)... Jan(2 next year)
        # Let's list standard Month 1~12 assuming standard approximate solar terms.
        # Month 1 (Chouk) is usually end of prev year logic, but for simple table let's follow lunar/solar custom.
        # Standard Saju Wolun list: usually starts from In Month (Feb).
        # Let's generate Feb(寅) to Jan(丑).
        
        months_order = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1] # Indices of Zhi: In(2) ~ Chouk(1)
        # Solar months approx: Feb, Mar, ..., Jan
        
        for i, zhi_idx in enumerate(months_order):
            curr_gan_idx = (start_gan_idx + i) % 10
            month_num = i + 2 # Feb=2
            if month_num > 12: month_num -= 12
            
            wolun_list.append({
                'month': month_num,
                'gan': self.CHEONGAN[curr_gan_idx],
                'zhi': self.JIJI[zhi_idx],
                'gan_element': self.STEM_OHAENG[curr_gan_idx],
                'zhi_element': self.BRANCH_OHAENG[zhi_idx]
            })
            
        return wolun_list

    def _get_korean_elem(self, elem):
        map_ = {'wood': '목', 'fire': '화', 'earth': '토', 'metal': '금', 'water': '수'}
        return map_.get(elem, elem)

    def interpret(self, pillars, ohaeng, user_info):
        day_master_idx = pillars['day']['gan_idx']
        day_master_pol = day_master_idx % 2
        
        ten_gods = {}
        for key in ['year', 'month', 'day', 'hour']:
            # Gan
            target_gan_idx = pillars[key]['gan_idx']
            target_gan_pol = target_gan_idx % 2
            ten_gods_gan = self._determine_god(day_master_idx, target_gan_idx, day_master_pol, target_gan_pol, is_zhi=False)
            
            # Zhi
            # Spec Polarity: Ja(1), Chuk(1), In(0), Myo(1)...
            zhi_polarities_spec = [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0]
            target_zhi_idx = pillars[key]['zhi_idx']
            target_zhi_pol = zhi_polarities_spec[target_zhi_idx]
            
            ten_gods_zhi = self._determine_god(day_master_idx, -1, day_master_pol, target_zhi_pol, is_zhi=True, zhi_idx=target_zhi_idx)
            ten_gods[key] = {'gan': ten_gods_gan, 'zhi': ten_gods_zhi}

        # 2. Daewoon (New Logic with Nested Years/Months)
        daewoon = self.get_daewoon_list(pillars, user_info['gender'])
        
        # 3. GMHS
        gmhs = self.get_geun_myo_hwa_sil(pillars)
        
        return {
            'core': self._get_core_trait(pillars['day']['gan'], pillars['day']['gan_element']),
            'advice': self._get_detailed_advice(ohaeng),
            'wealth': self._get_wealth_text(ohaeng['counts']['earth'], 'earth'), 
            'love': "사랑은...",
            'social_analysis': "사회생활은...",
            'today_luck': self.get_today_fortune(day_master_idx),
            'gmhs': gmhs,
            'ohaeng_analysis': ohaeng,
            'daewoon': daewoon,
            'ten_gods': ten_gods
        }

    def _determine_god(self, me_idx, target_idx, me_pol, target_pol, is_zhi=False, zhi_idx=None):
        me_elem_idx = me_idx // 2
        if is_zhi:
            elem_map = {'wood':0, 'fire':1, 'earth':2, 'metal':3, 'water':4}
            target_elem_name = self.BRANCH_OHAENG[zhi_idx]
            target_elem_idx = elem_map[target_elem_name]
        else:
            target_elem_idx = target_idx // 2

        rel = (target_elem_idx - me_elem_idx) % 5
        is_same_pol = (me_pol == target_pol)
        
        simple_names = [
            ['비견', '겁재'],
            ['식신', '상관'],
            ['편재', '정재'],
            ['편관', '정관'],
            ['편인', '정인']
        ]
        return simple_names[rel][0] if is_same_pol else simple_names[rel][1]

    def get_daewoon_list(self, pillars, gender):
        meta = pillars['meta']
        year_gan_idx = meta['year_gan_idx']
        month_gan_idx = pillars['month']['gan_idx']
        month_zhi_idx = pillars['month']['zhi_idx']
        day_master_gan_idx = pillars['day']['gan_idx'] 
        month_idx_from_in = meta['month_idx']
        birth_dt_utc = meta['utc_dt']
        birth_year = meta['year_base']
        
        # 1. Direction
        is_yang_year = (year_gan_idx % 2 == 0)
        is_male = (gender == 'male')
        if (is_yang_year and is_male) or (not is_yang_year and not is_male):
            direction = 1 # Forward (Sunhaeng)
        else:
            direction = -1 # Backward (Yeokhaeng)
            
        # 2. Start Age Calculation (Daewoon Number)
        # Find Pre/Next Major Solar Terms
        # birth_dt_utc must be offset-aware (pytz.utc). Skyfield returns offset-aware?
        # My corrector sets utc_dt as aware.
        # But get_daewoon_term_times expects aware?
        # get_term_time logic uses compute_solar_term(dt) -> ts.from_datetime(dt)
        # ts.from_datetime handles aware.
        
        pre_term, next_term = self.corrector.get_daewoon_term_times(birth_dt_utc, month_idx_from_in)
        
        if direction == 1:
            # Forward: Diff = Next Term - Birth
            diff = next_term - birth_dt_utc
        else:
            # Backward: Diff = Birth - Pre Term
            diff = birth_dt_utc - pre_term
            
        days = diff.total_seconds() / 86400.0
        # Rule: 3 days = 1 year.
        # Use Arithmetic Rounding (Half Up) instead of Banker's Rounding
        start_age = int((days / 3.0) + 0.5)
        if start_age < 1: start_age = 1
        
        # 3. Generate Daewoon List
        daewoon_list = []
        
        for i in range(10): # 10 Daewoons
            step = direction * (i + 1)
            next_gan_idx = (month_gan_idx + step) % 10
            next_zhi_idx = (month_zhi_idx + step) % 12
            
            gan_char = self.CHEONGAN[next_gan_idx]
            zhi_char = self.JIJI[next_zhi_idx]
            
            my_pol = day_master_gan_idx % 2
            target_pol = next_gan_idx % 2
            god = self._determine_god(day_master_gan_idx, next_gan_idx, my_pol, target_pol)
            
            daewoon_age = start_age + (i * 10)
            daewoon_start_year = birth_year + (daewoon_age - 1)
            
            # Generate 10 Years of Seun for this Daewoon
            seun_data = []
            for y in range(daewoon_start_year, daewoon_start_year + 10):
                 seun_entry = self.get_seun_entry(y, day_master_gan_idx)
                 # Generate Wolun for this Seun
                 wolun_data = self.get_wolun_list(y)
                 seun_entry['wolun_list'] = wolun_data
                 seun_data.append(seun_entry)

            daewoon_list.append({
                'age': daewoon_age,
                'gan': gan_char,
                'zhi': zhi_char,
                'gan_element': self.STEM_OHAENG[next_gan_idx],
                'zhi_element': self.BRANCH_OHAENG[next_zhi_idx],
                'text': f"[{god}] 대운",
                'years': seun_data # Nested Seun Data
            })
            
        return daewoon_list

    def get_seun_entry(self, year, day_master_gan_idx):
        # Helper for single year seun
        cycle_idx = (year - 4) % 60
        gan_idx = cycle_idx % 10
        zhi_idx = cycle_idx % 12
        
        my_pol = day_master_gan_idx % 2
        target_pol = gan_idx % 2
        god = self._determine_god(day_master_gan_idx, gan_idx, my_pol, target_pol)

        return {
            'year': year,
            'gan': self.CHEONGAN[gan_idx],
            'zhi': self.JIJI[zhi_idx],
            'gan_element': self.STEM_OHAENG[gan_idx],
            'zhi_element': self.BRANCH_OHAENG[zhi_idx],
            'ten_god': god
        }

    def get_geun_myo_hwa_sil(self, pillars):
        return {
            'year': {'period': '초년기 (0~19세)', 'pillar': pillars['year'], 'desc': '부모님과 조상의 그늘 아래 성장하는 시기입니다.'},
            'month': {'period': '청년기 (20~39세)', 'pillar': pillars['month'], 'desc': '사회에 진출하여 자신의 능력을 펼치는 시기입니다.'},
            'day': {'period': '중년기 (40~59세)', 'pillar': pillars['day'], 'desc': '가정을 이루고 인생의 황금기를 맞이하는 시기입니다.'},
            'hour': {'period': '말년기 (60세~)', 'pillar': pillars['hour'], 'desc': '지난 날을 돌아보며 결실을 거두는 시기입니다.'}
        }

    def _get_core_trait(self, gan, element):
        traits = {
            '갑': '곧게 뻗은 소나무처럼 리더십과 추진력이 강합니다.',
            '을': '강인한 생명력을 지닌 꽃초처럼 유연하고 적응력이 뛰어납니다.',
            '병': '세상을 비추는 태양처럼 열정적이고 에너지가 넘칩니다.',
            '정': '은근하게 타오르는 촛불처럼 따뜻하고 섬세한 배려심이 있습니다.',
            '무': '묵직한 태산처럼 믿음직스럽고 포용력이 넓습니다.',
            '기': '비옥한 텃밭처럼 실속이 있고 현실적인 감각이 뛰어납니다.',
            '경': '단단한 원석처럼 결단력이 있고 의리가 강합니다.',
            '신': '반짝이는 보석처럼 섬세하고 예리하며 미적 감각이 있습니다.',
            '임': '드넓은 바다처럼 지혜롭고 유연하며 창의적입니다.',
            '계': '촉촉한 단비처럼 부드럽고 친화력이 좋으며 총명합니다.'
        }
        return traits.get(gan, '당신은 무한한 잠재력을 가지고 있습니다.')

    def _get_detailed_advice(self, ohaeng):
        counts = ohaeng['counts']
        advice = "전체적인 오행의 균형을 살펴보면, "
        zeros = [k for k, v in counts.items() if v == 0]
        if zeros:
            advice += f"{', '.join([self._get_korean_elem(z) for z in zeros])} 기운을 보완하는 취미나 생활 습관을 가지면 좋습니다."
        else:
            advice += "오행이 비교적 골고루 갖춰져 있어 안정적인 운세입니다."
        return advice

    def _get_wealth_text(self, count, elem):
        if count >= 3:
            return "재물에 대한 감각이 탁월하나, 지출 관리에도 신경 써야 합니다."
        elif count == 0:
            return "재물보다는 명예나 사람을 좇을 때 더 큰 부가 따라옵니다."
        else:
            return "꾸준한 노력으로 안정적인 자산을 형성할 수 있습니다."

    def get_today_fortune(self, day_master_idx):
        import datetime
        # KST Timezone (UTC+9)
        kst = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(kst).date()
        # Reference Date: 2000-01-01 (Saturday) -> Gap-Sul (0, 10)
        # Wait, reference calculation needs to be precise.
        # Let's use the same logic as get_gan_zhi for day.
        # ref_date 2000-1-1 is Gap-Sul (Index 10: Gap(0), Sul(10))
        # Wait, in get_gan_zhi: day_cycle_idx = (54 + delta) % 60
        # 2000-1-1 is Index 54 (Mu-O)? Let me check.
        # 2000-01-01 is indeed Mu-O (54). (Checking calendar... 2000 Jan 1 is Mu-O).
        # My previous code said 54. So I stick to 54.
        
        ref_date = datetime.date(2000, 1, 1)
        delta = (today - ref_date).days
        today_cycle = (54 + delta) % 60
        today_gan_idx = today_cycle % 10
        today_zhi_idx = today_cycle % 12
        
        # Calculate Ten Gods
        me_pol = day_master_idx % 2
        today_pol = today_gan_idx % 2
        god = self._determine_god(day_master_idx, today_gan_idx, me_pol, today_pol)
        
        # Mapping Ten Gods to Fortune Text
        fortune_map = {
            '비견': {
                'title': '나와 같은 친구를 만나는 날',
                'keyword': '주체성/협력',
                'good': '주관이 뚜렷해지고 추진력이 생깁니다. 동료와 함께하면 시너지가 납니다.',
                'bad': '고집이 세져 주변과 마찰이 생길 수 있으니 유연함이 필요합니다.',
                'msg': '당신의 능력을 믿으세요! 하지만 독불장군보다는 함께의 가치를 아는 당신이 멋집니다.'
            },
            '겁재': {
                'title': '선의의 경쟁자가 나타나는 날',
                'keyword': '경쟁/승부욕',
                'good': '승부욕이 발동해 평소보다 더 많은 일을 해낼 수 있습니다.',
                'bad': '예상치 못한 지출이 생기거나 노력의 대가를 뺏길 수 있으니 주의하세요.',
                'msg': '치열한 경쟁 속에서도 당신만의 빛을 잃지 마세요. 위기는 곧 기회입니다!'
            },
            '식신': {
                'title': '맛있는 음식과 여유가 있는 날',
                'keyword': '표현/즐거움',
                'good': '창의력이 샘솟고 먹을 복이 따릅니다. 마음이 편안해집니다.',
                'bad': '너무 나태해지거나 말실수를 할 수 있으니 조금만 긴장감을 가지세요.',
                'msg': '오늘 하루는 당신에게 주는 선물입니다. 마음껏 즐기고 행복을 누리세요!'
            },
            '상관': {
                'title': '톡톡 튀는 아이디어가 빛나는 날',
                'keyword': '개혁/언변',
                'good': '남들이 생각지 못한 기발한 아이디어로 문제를 해결할 수 있습니다.',
                'bad': '직설적인 말로 윗사람과 트러블이 생길 수 있으니 언행을 조심하세요.',
                'msg': '당신의 날카로운 통찰력은 세상을 바꾸는 힘이 됩니다. 부드러운 화법으로 매력을 더해보세요.'
            },
            '편재': {
                'title': '뜻밖의 횡재수가 있는 날',
                'keyword': '재물/확장',
                'good': '생각지도 못한 수익이 생기거나 활동 영역이 넓어집니다.',
                'bad': '충동구매나 무리한 투자로 손실을 볼 수 있으니 지갑을 잘 지키세요.',
                'msg': '행운의 여신이 당신을 보고 웃고 있네요! 기회를 잡되, 침착함을 유지하세요.'
            },
            '정재': {
                'title': '성실함이 보상받는 날',
                'keyword': '안정/결실',
                'good': '꼼꼼한 일 처리로 신뢰를 얻고, 노력한 만큼의 정당한 대가를 얻습니다.',
                'bad': '너무 계산적으로 굴면 인심을 잃을 수 있습니다. 때로는 너그러워지세요.',
                'msg': '차곡차곡 쌓아올린 당신의 노력이 단단한 성이 되어줄 거예요. 오늘도 화이팅!'
            },
            '편관': {
                'title': '호랑이 등에 올라탄 날',
                'keyword': '책임/권위',
                'good': '카리스마가 돋보이고 어려운 일을 해결해 리더십을 인정받습니다.',
                'bad': '과도한 업무나 스트레스로 건강을 해칠 수 있으니 휴식이 필수입니다.',
                'msg': '거친 파도도 훌륭한 서퍼를 만드는 법이죠. 당신은 이 어려움을 충분히 이겨낼 수 있습니다!'
            },
            '정관': {
                'title': '명예와 신용이 오르는 날',
                'keyword': '승진/합격',
                'good': '시험 합격이나 승진 등 명예로운 일이 생기고 규칙을 잘 지켜 칭찬받습니다.',
                'bad': '지나치게 보수적이거나 답답해 보일 수 있습니다. 융통성을 발휘해보세요.',
                'msg': '반듯한 당신의 모습이 오늘따라 더욱 빛이 납니다. 당신의 원칙이 정답입니다.'
            },
            '편인': {
                'title': '신비로운 직감이 발달하는 날',
                'keyword': '아이디어/눈치',
                'good': '남들이 못 보는 이면을 꿰뚫어보고, 독특한 분야에서 두각을 나타냅니다.',
                'bad': '쓸데없는 생각이나 의심으로 기회를 놓칠 수 있습니다. 단순하게 생각하세요.',
                'msg': '당신의 예리한 직감은 틀리지 않았어요. 자신을 믿고 나아가세요!'
            },
            '정인': {
                'title': '든든한 후원자를 만나는 날',
                'keyword': '인정/계약',
                'good': '윗사람의 도움을 받거나 문서 계약, 합격 등 좋은 소식이 들려옵니다.',
                'bad': '너무 의존적인 태도는 성장을 방해합니다. 스스로 일어서는 연습도 필요해요.',
                'msg': '사랑받기 위해 태어난 당신, 오늘은 온 우주가 당신을 돕고 있답니다.'
            }
        }
        
        date_str = today.strftime("%Y년 %m월 %d일")
        pillar_str = f"{self.CHEONGAN[today_gan_idx]}{self.JIJI[today_zhi_idx]}({self.STEM_OHAENG[today_gan_idx]}/{self.BRANCH_OHAENG[today_zhi_idx]})일"
        
        info = fortune_map.get(god, fortune_map['비견']) # Default fallback
        
        return {
            'date': date_str, 
            'pillar': pillar_str, 
            'ten_god': god,
            'title': info['title'], 
            'keyword': info['keyword'],
            'good': info['good'],
            'bad': info['bad'],
            'msg': info['msg']
        }
