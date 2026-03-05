from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
from saju_logic import SajuLogic
from ai_analysis import AIAnalysis
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "glow-saju-secret-key-123")
saju = SajuLogic()
ai = AIAnalysis()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sw.js')
def sw():
    return app.send_static_file('sw.js')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/.well-known/assetlinks.json')
def assetlinks():
    return send_from_directory('.well-known', 'assetlinks.json')

@app.route('/loading', methods=['GET', 'POST'])
def loading():
    if request.method == 'POST':
        # request.form contains all input fields including 'city'
        session['user_data'] = request.form.to_dict()
        return render_template('loading.html')
    else:
        # GET 요청으로 직접 접근 시 메인으로 리다이렉트
        return redirect(url_for('index'))

@app.route('/result', methods=['GET'])
def result():
    user_data = session.get('user_data', {})
    if not user_data:
        return redirect(url_for('index'))
        
    name = user_data.get('name')
    gender = user_data.get('gender')
    birth_date_str = user_data.get('birth_date')
    birth_time_str = user_data.get('birth_time')
    city = user_data.get('city', 'Seoul')
    calendar_type = user_data.get('calendar_type', 'solar')
    is_leap = user_data.get('is_leap') == 'on'
    
    try:
        if not birth_date_str:
            raise ValueError("생년월일을 입력해주세요.")
            
        year, month, day = map(int, birth_date_str.split('-'))
        
        # Lunar -> Solar Conversion
        if calendar_type == 'lunar':
            from korean_lunar_calendar import KoreanLunarCalendar
            calendar = KoreanLunarCalendar()
            if not calendar.setLunarDate(year, month, day, is_leap):
                return "존재하지 않는 음력 날짜입니다.", 400
            
            solar_date = calendar.SolarIsoFormat()
            year, month, day = map(int, solar_date.split('-'))

        if birth_time_str:
            hour, minute = map(int, birth_time_str.split(':'))
        else:
            raise ValueError("생년월일을 입력해 주세요.")
            
        year, month, day = map(int, birth_date_str.split('-'))
        
        if calendar_type == 'lunar':
            from korean_lunar_calendar import KoreanLunarCalendar
            calendar = KoreanLunarCalendar()
            if not calendar.setLunarDate(year, month, day, is_leap):
                return "존재하지 않는 음력 날짜입니다.", 400
            solar_date = calendar.SolarIsoFormat()
            year, month, day = map(int, solar_date.split('-'))

        if birth_time_str:
            hour, minute = map(int, birth_time_str.split(':'))
        else:
            hour, minute = 0, 0 
        
        pillars = saju.get_gan_zhi(year, month, day, hour, minute, city=city)
        ohaeng = saju.get_ohaeng_distribution(pillars)
        interpretations = saju.interpret(pillars, ohaeng, {'gender': gender})
        
        now = datetime.now()
        age = now.year - year + 1
        birth_context = f"{year}년생 ({age}세)"
        
        from collections import Counter
        ten_gods_all = []
        for p_key in interpretations['ten_gods']:
            ten_gods_all.append(interpretations['ten_gods'][p_key]['gan'])
            ten_gods_all.append(interpretations['ten_gods'][p_key]['zhi'])
        counts = Counter(ten_gods_all)
        ten_stars_list = ", ".join([f"{k} {v}" for k, v in counts.items()])
        
        if interpretations.get('daewoon') and len(interpretations['daewoon']) > 0:
            current_daewun_obj = interpretations['daewoon'][0]
            current_daewun = f"{current_daewun_obj['age']}세 대운 ({current_daewun_obj['gan']}{current_daewun_obj['zhi']})"
        else:
            current_daewun = "대운 정보 없음"

        import random
        oracle_number = f"{random.randint(1, 40):02d}"

        # AI 분석은 이제 비동기로 처리되므로 메인 로직에서 제거 (504 타임아웃 방지)
        interpretations['premium_ai'] = None
        interpretations['today_fortune'] = None

        now = datetime.now()
        current_date = now.strftime("%Y년 %m월 %d일")
        weekday_map = ['월', '화', '수', '목', '금', '토', '일']
        current_date += f" ({weekday_map[now.weekday()]}요일)"

        birth_dt = f"{year}년 {month}월 {day}일 {hour}시 {minute:02d}분"

        hanja_map = {
            '갑': '甲', '을': '乙', '병': '丙', '정': '丁', '무': '戊',
            '기': '己', '경': '庚', '신': '辛', '임': '壬', '계': '癸',
            '자': '子', '축': '丑', '인': '寅', '묘': '卯', '진': '辰',
            '사': '巳', '오': '午', '미': '未', '신': '申', '유': '酉',
            '술': '戌', '해': '亥'
        }

        # AI 호출에 필요한 추가 필드들을 템플릿에 전달
        return render_template('result.html', 
                               name=name, 
                               gender=gender,
                               pillars=pillars, 
                               ohaeng=ohaeng, 
                               interp=interpretations,
                               birth_dt=birth_dt,
                               hanja_map=hanja_map,
                               oracle_number=oracle_number,
                               current_date=current_date,
                               ten_stars_list=ten_stars_list,
                               current_daewun=current_daewun,
                               birth_context=birth_context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error occurred: {str(e)}", 400

@app.route('/api/ai/premium', methods=['POST'])
def api_premium_ai():
    try:
        data = request.json
        res = ai.get_android_free_analysis(
            data['name'], data['gender'], data['pillars'], 
            data['ohaeng'], data['ten_stars_list'], 
            data['current_daewun'], data['birth_context'], data['oracle_number']
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/fortune', methods=['POST'])
def api_today_fortune():
    try:
        data = request.json
        res = ai.get_today_fortune(
            data['name'], data['day_stem'], data['pillars'], data['ohaeng']
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
