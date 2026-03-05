
import sys
import os
from datetime import datetime

# Add Saju directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from saju_logic import SajuLogic
except ImportError:
    print("Error: Could not import saju_logic. Make sure you are running this script from the '갓생 사주' directory.")
    sys.exit(1)

def run_tests():
    saju = SajuLogic()
    
    # 10 Test Cases from original requirement
    cases = [
        (2024, 2, 4, 17, 0, 'Seoul', "1. Lichun Cutoff (17:27) - Before Lichun?"),
        (2024, 4, 4, 16, 0, 'Seoul', "2. Cheongmyeong Cutoff (16:02)"),
        (2024, 1, 1, 23, 40, 'Seoul', "3. Joja-si (23:40) - Day Change?"),
        (1958, 5, 10, 13, 40, 'Seoul', "4. 127.5 Era (DST?) - May 10 is DST"),
        (1988, 5, 20, 10, 0, 'Seoul', "5. Summer Time - May 20 is DST"),
        (2024, 3, 1, 7, 32, 'Incheon', "6. Incheon Correction"),
        (2024, 3, 1, 7, 25, 'Busan', "7. Busan Correction"),
        (2024, 6, 1, 13, 30, 'Seoul', "8. Time Boundary (13:30)"),
        (1961, 8, 10, 0, 10, 'Seoul', "9. Standard Time Change"),
        (2023, 3, 22, 12, 0, 'Seoul', "10. Leap Month Check")
    ]

    print(f"{'Case':<40} | {'Input Time':<20} | {'Result (Year/Month/Day/Hour)'}")
    print("-" * 100)

    for year, month, day, hour, minute, city, desc in cases:
        try:
            res = saju.get_gan_zhi(year, month, day, hour, minute, city=city)
            
            # Extract Gan-Zhi string
            gan_zhi = f"{res['year']['gan']}{res['year']['zhi']} / {res['month']['gan']}{res['month']['zhi']} / {res['day']['gan']}{res['day']['zhi']} / {res['hour']['gan']}{res['hour']['zhi']}"
            
            # Print row
            input_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
            print(f"{desc:<40} | {input_str:<20} | {gan_zhi}")
            
            # Optional: Detail check for Case 1 (Lichun)
            if "Lichun" in desc:
                 # 2024 Lichun is approx Feb 4 17:27. Input is 17:00.
                 # Should be PREV Year? No, year changes at Lichun.
                 # Wait. Lichun is start of year.
                 # If input < Lichun, then Year = Previous Year (Gye-Myo).
                 # If input >= Lichun, then Year = New Year (Gap-Jin).
                 # 17:00 < 17:27 -> Prev Year (Gye-Myo).
                 pass

        except Exception as e:
            print(f"{desc:<40} | Error: {e}")

if __name__ == "__main__":
    run_tests()
