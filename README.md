# GLOW글로우:갓생사주 - 운명을 읽고 나를 켜다 ✨

<p align="center">
  <img src="static/icon.png" width="128" alt="GLOW Logo">
  <br>
  <strong>우주의 기운과 당신의 갓생(God Saeng)을 연결하는 프리미엄 사주 서비스</strong>
</p>

---

## 📖 소개

**GLOW글로우:갓생사주**는 전통 명리학의 깊이 있는 분석과 현대적인 AI 기술(**Google Gemini**)을 결합한 차세대 사주 분석 웹 서비스입니다. 당신의 타고난 기운을 정교하게 계산하고, 갓생을 향한 운명의 지도를 프리미엄 다크 테마 디자인과 함께 제공합니다.

---

## ✨ 주요 기능

- **운명 설계도(사주 원국) 추출**: 태어난 순간의 우주 에너지를 만세력 정밀 알고리즘으로 시각화합니다.
- **5원소 에너지 밸런스**: 나를 구성하는 오행(木/火/土/金/水)의 분포를 분석하여 삶의 조화로운 균형점을 찾습니다.
- **사회적 페르소나와 본능(십성) 분석**: 십성(십신) 판정을 통해 페르소나와 내면의 본능적 기질을 심층적으로 해부합니다.
- **인생 대항해(대운) 가이드**: 10년 주기로 변화하는 대운의 흐름을 읽고, 최적의 도약을 위한 타이밍을 제안합니다.
- **인생 4계절(근묘화실) 리포트**: 뿌리부터 열매까지, 내 삶의 기승전결을 시기별 성장 곡선으로 예측합니다.
- **제미나이 AI 갓생 코칭**: **Google Gemini (1.5 Flash)**가 사주 데이터를 해석하여 지금 바로 실행 가능한 '갓생 액션 플랜'을 제시합니다.
- **데일리 갓생 포춘**: 매일 한 장의 길상 오라클 카드를 통해 우주가 전하는 오늘만의 특별한 행운 메시지를 수신합니다.
- **프리미엄 다크 갤럭시 UI**: 미드나잇 블루와 골드 포인트가 어우러진 럭셔리 디자인으로 신비로운 몰입감을 제공합니다.

---

## 🛠️ 기술 스택

- **Backend**: Python 3.9+ (Flask Framework)
- **Frontend**: HTML5, CSS3 (Custom Luxury Design), JavaScript
- **AI Engine**: **Google Gemini Pro / Flash API**
- **Deployment**: Vercel (Python Runtime)
- **Library**: `korean-lunar-calendar` (음양력 변환 및 만세력 로직), `google-generativeai`

---

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone https://github.com/tinleygarden/godsaeng-saju.git
cd godsaeng-saju

# 2. 필수 라이브러리 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env 파일 생성)
GEMINI_API_KEY=your_gemini_api_key_here

# 4. 로컬 서버 실행
python app.py
```

---

## 📁 프로젝트 구조

```
├── app.py              # Flask 서버 및 라우팅 제어
├── saju_logic.py       # 천간지지 및 만세력 계산 핵심 알고리즘
├── ai_analysis.py      # Google Gemini AI 연동 및 프롬프트 엔지니어링
├── vercel.json         # Vercel 배포 설정 파일
├── static/             # 이미지, 스타일시트 및 정적 자산
└── templates/          # Jinja2 템플릿 (index, result, loading 등)
```

---

## 🎨 디자인 시스템

- **Main Theme**: Midnight Galaxy Dark (#0f172a)
- **Accent Color**: Celestial Gold (#fbbf24) & Stardust Rose
- **Concept**: 고전적인 신비로움과 현대적인 고급스러움의 조화 (Premium Glassmorphism)

---

## ⚠️ 주의사항

1. **API 키 관리**: `.env` 파일에 유효한 Gemini API 키가 설정되어 있어야 AI 분석 기능이 작동합니다.
2. **배포 환경**: Vercel Python Runtime 환경에 최적화되어 있습니다.
3. **데이터 소스**: 한국 천문연구원의 데이터를 기반으로 정밀하게 계산됩니다.

---

## 📄 라이선스

&copy; 2026 GLOW GOD SAENG SAJU. All rights reserved.
본 프로젝트는 **별하(Byeolha)** 사주 프로그램의 핵심 로직을 기반으로, GLOW 팀에서 **Google Gemini AI** 기술과 프리미엄 UI 디자인을 결합하여 고도화한 서비스입니다. 

원본 오픈소스 제작자분들께 깊은 감사를 드립니다. 개인 프로젝트 및 비상업적 용도로의 활용을 권장하며, 상업적 이용 및 디자인 도용 시 별도 협의가 필요합니다.
