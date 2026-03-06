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

- **사주 원국 정밀 계산**: 년/월/일/시주 자동 천간지지 계산 및 만세력 연동
- **오행 분포 분석**: 목(木)/화(火)/토(土)/금(金)/수(水) 기운의 밸런스 및 분포 진단
- **십성(십신) 판정**: 사주 8개 글자 간의 관계(비견, 겁재, 식신 등) 심층 분석
- **대운 흐름 분석**: 10년 주기 대운 흐름 및 인생의 주요 변곡점 가이드
- **근묘화실(根苗花實)**: 생애 4단계(초년, 청년, 중년, 말년)별 운명 리포트
- **AI 맞춤형 해석**: **Google Gemini (1.5 Flash)**를 통한 개인화된 장문 분석 및 조언
- **프리미엄 UI/UX**: 미드나잇 갤럭시 & 골드 테마의 고품격 웹 인터페이스

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
개인 프로젝트 및 비상업적 용도로 활용이 가능하며, 상업적 이용 시 별도 협의가 필요합니다.
