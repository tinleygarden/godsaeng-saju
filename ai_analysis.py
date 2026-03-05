import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIAnalysis:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.free_model = genai.GenerativeModel("gemini-2.5-flash")
            self.premium_model = genai.GenerativeModel("gemini-2.5-pro")
        else:
            self.free_model = None
            self.premium_model = None
        self.knowledge_dir = "saju_knowledge"

    def _load_knowledge_base(self):
        """saju_knowledge 폴더 안의 모든 텍스트 파일을 읽어 하나의 참조 문서로 만듭니다."""
        knowledge_text = ""
        if not os.path.exists(self.knowledge_dir):
            return knowledge_text
        
        for filename in sorted(os.listdir(self.knowledge_dir)):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.knowledge_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        knowledge_text += f"\n--- [{filename}] ---\n"
                        knowledge_text += f.read() + "\n"
                except Exception as e:
                    print(f"Error reading knowledge file {filename}: {e}")
        return knowledge_text

    def get_free_analysis(self, name, day_stem, ohaeng, ten_stars_list):
        """무료 유저를 위한 간단한 AI 사주 요약 (Gemini 1.5 Flash 사용)"""
        if not self.free_model:
            return None
        
        ohaeng_str = ", ".join([f"{k}({v}%)" for k, v in ohaeng['percentages'].items()])
        prompt = f"""
당신은 'GLOW갓생사주'의 다정한 수호천사입니다. (코다리라는 이름 대신 '수호천사'로 활동합니다.)
이름: {name}, 본원(일간): {day_stem}, 오행: {ohaeng_str}, 십신: {ten_stars_list}

위 데이터를 바탕으로, 이 사람의 타고난 매력과 장점을 3~4문장 정도로 짧고 다정하게 요약해 주세요.
어려운 사주 용어는 피하고 누구나 이해할 수 있는 따뜻한 칭찬의 말로 작성해 주세요. (JSON이 아닌 일반 텍스트로 응답)
주의사항: 첫인사말에 '사랑스러운 OOO님' 같이 첫 줄에 '사랑스러운'이라는 수식어는 절대 쓰지 말고 담백하게 시작해주세요.
"""
        try:
            response = self.free_model.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(temperature=0.7)
            )
            return response.text.replace('*', '').strip()
        except Exception as e:
            print(f"Free AI 분석 오류: {e}")
            return None

    def get_premium_analysis(self, name, gender, pillars, ohaeng, ten_stars_list, current_daewun, birth_context, oracle_number):
        """유료 결제 유저를 위한 심층 AI 분석 (대표님의 비급 지식 RAG 주입, Gemini 1.5 Pro 사용)"""
        if not self.premium_model:
            print("Warning: GEMINI_API_KEY not found. Skipping Premium AI analysis.")
            return {}

        # 1. 대표님 비급 지식 불러오기
        master_knowledge = self._load_knowledge_base()

        ohaeng_str = ", ".join([f"{k}({v}%)" for k, v in ohaeng['percentages'].items()])
        
        pillars_summary = (
            f"연:[{pillars['year']['gan']}{pillars['year']['zhi']}] "
            f"월:[{pillars['month']['gan']}{pillars['month']['zhi']}] "
            f"일:[{pillars['day']['gan']}{pillars['day']['zhi']}] "
            f"시:[{pillars['hour']['gan']}{pillars['hour']['zhi']}]"
        )
        
        day_stem = pillars['day']['gan']

        system_instruction = f"""
[System Role]
당신은 'GLOW갓생사주' 앱의 다정하고 지혜로운 수호천사입니다. 
당신의 목표는 급변하는 AI 시대에 적응하지 못해 좌절하거나 존재 이유를 고민하는 사람들에게, 사주팔자 데이터를 기반으로 그들만의 고유한 가치와 희망을 찾아주는 것입니다.
반드시 JSON 형식으로만 답변하며, 값은 항상 문자열이어야 합니다.

[Tone & Manner]
1. 말투는 곁에서 어깨를 토닥여주는 듯한 다정하고 따뜻한 경어체(~해요, ~습니다)를 사용하세요.
2. 절대 단정적이거나 무서운 경고(예: 망한다, 사고가 난다)를 하지 마세요.
3. 사주의 단점(기신, 신약, 공망 등)은 '채워나가야 할 인생의 여백'이나 '조심하면 더 크게 성장할 수 있는 도약점'으로 부드럽게 재해석하세요.
4. AI 시대에 기계가 대체할 수 없는 인간 본연의 장점(직관력, 공감 능력, 끈기 등)을 사주 데이터와 연결하여 칭찬해 주세요.

[특별 지침: 마스터의 비급 🎇]
아래 첨부된 내용은 마스터(대표님)께서 직접 정리하신 파워풀한 명리 해석 비법입니다.
당신은 사주를 분석할 때, 반드시 아래 비급 자료의 핵심 개념(격국, 강약, 조후, 용신, 신살, 대운 등)을 최우선으로 적용하여 깊이 있는 결과물을 만들어야 합니다.

<마스터의 비급 데이터>
{master_knowledge}
</마스터의 비급 데이터>
"""

        prompt = f"""
# Input Data
- 이름: {name}, 성별: {gender}, 나이/생년: {birth_context}
- 본원(일간): {day_stem}
- 사주 원국: {pillars_summary}
- 십신 구성: {ten_stars_list}
- 오행 점수: {ohaeng_str}
- 현재 대운: {current_daewun}
- 뽑힌 오라클 카드 번호: {oracle_number}

# Output JSON Structure
모든 답변은 다음 9가지 키를 가진 JSON 형식으로 출력하세요. 각 항목은 따뜻한 위로와 전문적인 사주 분석이 결합된 형태여야 하며, 최소 7~10문장 이상의 정성스러운 에세이 형식으로 작성하세요.

1. "reason_to_live": "[Page 1] 세상에 태어난 아름다운 이유 (본질/격국 기반 칭찬)"
2. "energy_charm": "[Page 2] 나를 움직이는 에너지와 숨겨진 매력 (신강약/신살 기반)"
3. "mind_healing": "[Page 3] 마음의 빈자리 다독이기 (공망 결핍 위로 및 조언)"
4. "lucky_action": "[Page 4] 나만의 다정한 수호천사 (용신/오행 행운의 실천법)"
5. "daewoon_wave": "[Page 5] 인생의 큰 파도 타기 (대운 분석과 방향성)"
6. "wealth_roadmap": "[Page 6] 갓생을 위한 재물 & 커리어 로드맵 (재/관/인/식 전략)"
7. "love_mate": "[Page 7] 나를 빛나게 하는 소중한 인연들 (연애운/귀인)"
8. "this_year_chance": "[Page 8] 올해 당신에게 찾아올 빛나는 기회 (세운, 월운 하이라이트)"
9. "oracle_message": "[Page 9] 뽑힌 오라클 카드 {oracle_number}번을 기반으로 한 위로와 축복의 다정한 메시지"
"""

        try:
            response = self.premium_model.generate_content(
                contents=f"{system_instruction}\n\n{prompt}",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Premium AI 분석 오류: {e}")
            return {}

    def get_android_free_analysis(self, name, gender, pillars, ohaeng, ten_stars_list, current_daewun, birth_context, oracle_number):
        """안드로이드 웹뷰 앱의 무료 유저를 위한 빠른 심층 AI 분석 (Gemini 1.5 Flash 사용, 2개 항목만 추출)"""
        if not self.free_model:
            print("Warning: GEMINI_API_KEY not found. Skipping Android Free AI analysis.")
            return {}

        master_knowledge = self._load_knowledge_base()
        ohaeng_str = ", ".join([f"{k}({v}%)" for k, v in ohaeng['percentages'].items()])
        
        pillars_summary = (
            f"연:[{pillars['year']['gan']}{pillars['year']['zhi']}] "
            f"월:[{pillars['month']['gan']}{pillars['month']['zhi']}] "
            f"일:[{pillars['day']['gan']}{pillars['day']['zhi']}] "
            f"시:[{pillars['hour']['gan']}{pillars['hour']['zhi']}]"
        )
        day_stem = pillars['day']['gan']

        system_instruction = f"""
[System Role]
당신은 'GLOW갓생사주' 앱의 다정하고 지혜로운 수호천사입니다. 
당신의 목표는 사주팔자 데이터를 기반으로 사람들에게 그들만의 고유한 가치와 희망을 찾아주는 것입니다.
반드시 JSON 형식으로만 답변하며, 값은 항상 문자열이어야 합니다.

[Tone & Manner]
1. 말투는 곁에서 어깨를 토닥여주는 듯한 다정하고 따뜻한 경어체(~해요, ~습니다)를 사용하세요.
2. 절대 단정적이거나 무서운 경고(예: 망한다, 사고가 난다)를 하지 마세요.
3. 사주의 단점(기신, 신약, 공망 등)은 '채워나가야 할 인생의 여백'이나 '조심하면 더 크게 성장할 수 있는 도약점'으로 부드럽게 재해석하세요.

[특별 지침: 마스터의 비급 🎇]
아래 첨부된 내용은 마스터께서 직접 정리하신 파워풀한 명리 해석 비법입니다.
당신은 사주를 분석할 때, 반드시 아래 비급 자료의 핵심 개념(격국, 강약, 조후, 용신, 신살, 대운 등)을 최우선으로 적용하여 깊이 있는 결과물을 만들어야 합니다.

<마스터의 비급 데이터>
{master_knowledge}
</마스터의 비급 데이터>
"""

        prompt = f"""
# Input Data
- 이름: {name}, 성별: {gender}, 나이/생년: {birth_context}
- 본원(일간): {day_stem}
- 사주 원국: {pillars_summary}
- 십신 구성: {ten_stars_list}
- 오행 점수: {ohaeng_str}
- 현재 대운: {current_daewun}

# Output JSON Structure
다음 2가지 키를 가진 JSON 형식으로만 정확히 출력해 주세요. 각 항목은 따뜻한 위로와 전문적인 사주 분석이 결합된 에세이 형식으로 작성해 주세요. (마크다운 코드블록이나 불필요한 설명을 넣지 마세요)

1. "reason_to_live": "[Page 1] 세상에 태어난 아름다운 이유 (본질/격국 기반 칭찬)"
2. "energy_charm": "[Page 2] 나를 움직이는 에너지와 숨겨진 매력 (신강약/신살 기반)"
"""

        try:
            response = self.free_model.generate_content(
                contents=f"{system_instruction}\n\n{prompt}",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Android Free AI 분석 오류: {e}")
            return {}

    def get_today_fortune(self, name, day_stem, pillars, ohaeng):
        """오늘의 운세 분석 (JSON 반환)"""
        if not self.free_model:
            return None
            
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        ohaeng_str = ", ".join([f"{k}({v}%)" for k, v in ohaeng['percentages'].items()])
        prompt = f"""
당신은 'GLOW갓생사주'의 인공지능 운세 전문가입니다.
사용자: {name}, 본원: {day_stem}, 오행: {ohaeng_str}
오늘 날짜: {today}

사용자의 사주 데이터와 오늘 날짜의 일진을 고려하여, '오늘의 운세'를 아래 JSON 형식으로 작성해 주세요.
반드시 JSON만 출력하세요.

JSON 형식:
{{
  "one_line": "오늘을 한 문장으로 요약 (예: 배숙빈님, 오늘은 귀인을 만나는 날이에요)",
  "keyword": "오늘의 핵심 키워드 1개 (예: 성장, 휴식, 만남)",
  "good_point": "오늘 일어날 좋은 일이나 행운 요소 (1~2문장)",
  "bad_point": "오늘 주의해야 할 점이나 마음가짐 (1~2문장)",
  "advice": "오늘의 실천형 조언 (따뜻하고 다정한 에세이 느낌, 2~3문장)"
}}
"""
        try:
            response = self.free_model.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Today Fortune AI 분석 오류: {e}")
            return None
