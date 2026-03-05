import re

path = r'c:\Users\Hi\갓생 사주\templates\result.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Page 1 and Page 2 with unlocked versions and the Premium Banner, removing Page 3 to Page 9
pattern = r'<!-- \[Page 1\] 세상에 태어난 아름다운 이유 -->.*?<!-- \[Page 9\] Bonus\. 당신만을 위한 우주의 응원 카드 -->.*?</div>\s*<div\s*style="position: absolute; top: 50%; left: 50%; transform: translate\(-50%, -50%\); text-align: center; width: 100%;">\s*<i class="fa-solid fa-lock".*?</div>\s*{% endif %}\s*</div>'

replacement = """<!-- [Page 1] 세상에 태어난 아름다운 이유 -->
        <div class="glass-card" style="position: relative; overflow: hidden;">
            <h3><i class="fa-solid fa-seedling"></i> 1. 세상에 태어난 아름다운 이유 (나의 본질)</h3>
            <p style="white-space: pre-line; line-height: 1.8; font-size: 1.05rem;">{{ interp.premium_ai.reason_to_live }}</p>
        </div>

        <!-- [Page 2] 나를 움직이는 에너지와 숨겨진 매력 -->
        <div class="glass-card" style="position: relative; overflow: hidden;">
            <h3><i class="fa-solid fa-fire"></i> 2. 나를 움직이는 에너지와 숨겨진 매력</h3>
            <p style="white-space: pre-line; line-height: 1.8; font-size: 1.05rem;">{{ interp.premium_ai.energy_charm }}</p>
        </div>

        <!-- Premium Outlink Banner -->
        <div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(255,140,0,0.1) 100%); border: 1px solid #FFD700; margin-top: 2rem; padding: 3rem 2rem;">
            <i class="fa-solid fa-lock" style="font-size: 2.5rem; color: #FFD700; margin-bottom: 1rem;"></i>
            <h3 style="color: #FFD700; font-size: 1.5rem; margin-bottom: 1rem;">더 깊은 운명의 비밀을 알고 싶다면?</h3>
            <p style="color: var(--text-main); font-size: 1.05rem; opacity: 0.9; margin-bottom: 2rem; line-height: 1.6;">
                나의 10년 대운, 재물과 커리어 로드맵, 소중한 인연 등<br>
                나머지 7가지 프리미엄 심층 분석과 우주의 응원 카드가 <br>
                <strong>'글로우 갓생촌'</strong>에서 기다리고 있습니다.
            </p>
            <a href="https://godsaeng.world/" target="_blank" class="btn-premium" style="display: inline-flex; width: auto; font-size: 1.1rem; padding: 1rem 2rem;">
                <i class="fa-solid fa-gem"></i> 글로우 갓생촌에서 전체 운세 보기
            </a>
        </div>"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Replaced content! Pattern found: {new_content != content}")
