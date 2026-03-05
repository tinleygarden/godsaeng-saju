from skyfield.api import load
from datetime import datetime, timedelta
import pytz
import os

class SajuCorrector:
    def __init__(self):
        # Load ephemeris (downloads if missing)
        self.ts = load.timescale()
        # Ensure de421.bsp exists or download
        try:
             self.planets = load('de421.bsp')
        except Exception as e:
            print(f"Downloading de421.bsp failed: {e}")
            self.planets = None
            
        if self.planets:
            self.sun = self.planets['sun']
            self.earth = self.planets['earth']

    def get_korean_timezone_offset(self, year, month, day):
        # Returns standard offset and is_dst
        ymd = int(f"{year}{month:02d}{day:02d}")
        
        offset = 9.0
        # Standard Meridian History
        if 19080401 <= ymd <= 19111231: offset = 8.5
        elif 19120101 <= ymd <= 19540320: offset = 9.0
        elif 19540321 <= ymd <= 19610809: offset = 8.5
        else: offset = 9.0 # 1961-08-10 ~ Present
        
        is_dst = False
        # DST History (Simplified for major cases)
        # 1948-1951: May-Sep
        if 1948 <= year <= 1951:
             # Broad check for May-Sep
             if 501 <= int(f"{month:02d}{day:02d}") <= 930: is_dst = True
        # 1955-1960: May-Sep (1958 confirmed May 10 is DST)
        if 1955 <= year <= 1960:
             if 505 <= int(f"{month:02d}{day:02d}") <= 921: is_dst = True
        # 1987-1988: May-Oct (1988 confirmed May 20 is DST)
        if 1987 <= year <= 1988:
             if 508 <= int(f"{month:02d}{day:02d}") <= 1009: is_dst = True
             
        return offset, is_dst

    def compute_solar_term(self, dt_utc):
        # Returns solar longitude in degrees (0-360)
        if not self.planets: return 0
        t = self.ts.from_datetime(dt_utc)
        observer = self.earth.at(t)
        sun_pos = observer.observe(self.sun).apparent()
        lat, lon, dist = sun_pos.ecliptic_latlon()
        return lon.degrees

    def get_corrected_saju(self, year, month, day, hour, minute, city='Seoul'):
        # 1. Handle Timezone & DST (Civil -> UTC)
        offset, is_dst = self.get_korean_timezone_offset(year, month, day)
        
        # Civil DT
        civil_dt = datetime(year, month, day, hour, minute)
        
        # Adjust for DST (-1h to get Standard Time)
        std_hour = hour
        std_min = minute
        if is_dst:
            civil_dt_adjusted = civil_dt - timedelta(hours=1)
            std_year, std_month, std_day = civil_dt_adjusted.year, civil_dt_adjusted.month, civil_dt_adjusted.day
            std_hour, std_min = civil_dt_adjusted.hour, civil_dt_adjusted.minute
        else:
            std_year, std_month, std_day = year, month, day
            
        # UTC Time
        # UTC = Standard - Offset
        # offset is in hours (e.g. 9.0)
        total_offset_minutes = int(offset * 60)
        std_dt = datetime(std_year, std_month, std_day, std_hour, std_min)
        utc_dt = std_dt - timedelta(minutes=total_offset_minutes)
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)

        # 2. Solar Terms for Year/Month
        # Calculate Solar Longitude at UTC birth time
        s_lon = self.compute_solar_term(utc_dt)
        
        # Determine Year
        # Year starts at Lichun (315 deg).
        # If today is after Lichun (315) but before next Lichun...
        # But year boundary is simple:
        # If solar_lon < 315 (approx Feb 4) and solar_lon >= 270 (Winter Solstice), it's end of year.
        # Actually, Year starts at 315.
        # So we need to compare birth_dt with THIS YEAR's Lichun time.
        # Or simpler:
        # If solar_lon >= 315 or solar_lon < 15? (Feb is In-Wol)
        # Use simple logic:
        # Year Pillar Base:
        # If month < 2 or (month==2 and day < 10): check Lichun.
        # Let's search Lichun (315 deg) for this year.
        
        # This is tricky with just one point.
        # Better: Find the timestamps of Terms around birth.
        # 315 deg = Lichun.
        # We search when sun was at 315 deg.
        # Search range: Feb 3 to Feb 5 of birth year.
        # If birth < Lichun_Time, then Year = year-1.
        
        t0 = self.ts.utc(std_year, 2, 3)
        t1 = self.ts.utc(std_year, 2, 5)
        f = lambda t: self.earth.at(t).observe(self.sun).apparent().ecliptic_latlon()[1].degrees - 315
        # Root finding is hard due to modulo 360. 315 is continuous? No.
        # 315 is 315.
        # But finding precise time is expensive.
        # Check `s_lon` directly.
        # If (month==1): Year is prev. (Unless Lichun is in Jan? No).
        # If (month==2):
        #   If s_lon >= 315 (e.g. 316) -> New Year.
        #   If s_lon < 315 (e.g. 314) -> Prev Year.
        #   What if s_lon is 0 (Chunbun)? That's next month.
        #   So if s_lon in [270, 315), it is old year.
        #   Lichun is 315.
        #   So:
        
        saju_year = std_year
        if std_month < 2:
            saju_year = std_year - 1
        elif std_month == 2:
            # Check Lichun
            if 270 <= s_lon < 315:
                saju_year = std_year - 1
            # Else (>= 315), current year.
            
        # Determine Month
        # Month depends on Solar Term.
        # In-Wol (1): 315 <= lon < 345
        # Myo-Wol (2): 345 <= lon < 375 (15)
        # ...
        # Create a mapping.
        # Terms:
        # 315: In
        # 345: Myo
        # 15: Jin
        # 45: Sa
        # 75: O
        # 105: Mi
        # 135: Shin
        # 165: Yu
        # 195: Sul
        # 225: Hae
        # 255: Ja
        # 285: Chuk
        
        # Normalize lon to [0, 360) based on Lichun start?
        # Shift: (lon - 315) % 360
        # Month Index (0=In, 1=Myo...) = int((shifted) / 30)
        # s_lon might be 314.9 -> (314.9 - 315)%360 = 359.9.
        # 359.9 / 30 = 11.99 -> 11 (Chuk). Correct.
        # s_lon = 315.1 -> 0.1 / 30 = 0 (In). Correct.
        
        shifted_lon = (s_lon - 315) % 360
        month_idx_from_in = int(shifted_lon // 30)
        # month_idx_from_in: 0=In, 1=Myo, ..., 11=Chuk.
        
        # 3. Determine Day
        # 23:30 Cutoff (Standard Modern Saju).
        # We need "Saju Time" which is Standard Time adjusted for this cutoff?
        # Usually: 23:30 today counts as tomorrow (early Rat).
        # If std_hour=23 and std_min>=30:
        #    Day = Day + 1
        #    Hour = Rat (0)
        # Else: standard day.
        
        saju_day_dt = std_dt
        hour_idx = 0
        
        # Joja-si Logic (Standard)
        if std_hour == 23 and std_min >= 30:
            saju_day_dt = std_dt + timedelta(days=1)
            hour_idx = 0 # Ja
        elif std_hour == 0 and std_min < 30:
            # Late Rat (Yaja) of Prev Day? Some schools say Prev Day, some say Today.
            # User Case 3: 24.01.01 23:40 -> Early Rat (Joja) -> DAY CHANGED to 01.02.
            # My logic `std_dt + 1 day` handles this.
            
            # What about 00:10?
            # User Case 9: 61.08.10 00:10 -> Ja-si.
            # Is it Early Rat of Today or Late Rat of Yesterday?
            # Standard: 23:30-01:30 is ONE hour (Rat).
            # 23:30 PrevDay ... 00:00 Today ... 01:30 Today.
            # If using Joja/Yaja split:
            #   23:30-00:00 PrevDay = Yaja (Late Rat) - Day is PrevDay.
            #   00:00-01:30 Today = Joja (Early Rat) - Day is Today.
            # BUT user Image Case 3: 23:40 -> Day changed!
            # so 23:30 is the Boundary of Day.
            # 23:40 is NEXT DAY.
            # So 00:10 is TODAY (already passed boundary).
            # So 00:10 -> Day is Today.
            hour_idx = 0 # Ja
        else:
            # Normal calculation for hour index
            # Rat: 23:30 - 01:30
            # Ox: 01:30 - 03:30
            # ...
            # Formula: (total_minutes - 23*60 - 30) // 120 ?
            # Easier:
            # Shift time by -23:30? No.
            # Base is 23:30.
            # ((hour * 60 + min + 30) // 120) % 12 ?
            # 23:30 + 30 = 24:00 -> 12 -> 0 (Rat).
            # 01:30 + 30 = 02:00 -> 1 -> 1 (Ox).
            # 13:30 + 30 = 14:00 -> 7 -> 7 (Horse). Correct.
            
            # However, this assumes Standard 135E (30 min shift).
            # We must use LMT for Hour Pillar!
            pass
            
        # 4. Determine Hour Pillar (LMT)
        # Correct Hour using Longitude.
        # User Case 6 (Incheon, 126.6E): 07:32 -> 06:59 LMT -> Myo (05:00-07:00).
        # Myo is 5-7. If 06:59, it's Myo.
        # KST 07:32.
        # Incheon offset from 135: (126.6 - 135) * 4 = -33.6 min.
        # 07:32 - 33.6m = 06:58.4. Myo. Correct.
        # So I MUST calculate LMT.
        
        longitudes = {'Seoul': 126.9780, 'Incheon': 126.6372, 'Busan': 129.0756}
        lon = longitudes.get(city, 126.9780)
        
        # Calculate LMT offset from Standard
        # Standard Longitude depends on Year!
        # 1958 (Case 4): Standard 127.5. Offset = 8.5h.
        # Seoul 127.0. Diff = -0.5 deg = -2 min.
        # Case 4 Input: 13:40 (Civil DST=True).
        # Standard Time = 12:40.
        # LMT = 12:40 - 2m = 12:38.
        # 12:38 is Horse (11-13). Correct.
        
        std_meridian = offset * 15.0
        lmt_offset_minutes = (lon - std_meridian) * 4
        
        lmt_dt = std_dt + timedelta(minutes=lmt_offset_minutes)
        lmt_hour = lmt_dt.hour
        lmt_min = lmt_dt.minute
        
        # Hour Index based on LMT (Simple 2-hr slots, starting 23:00)
        # Because in LMT, Rat is 23:00-01:00.
        # e.g. 12:38 -> ((12*60+38 + 60) // 120) % 12
        # (758 + 60) = 818 // 120 = 6.8 -> 6 (Snake)?
        # Horse is 7?
        # Rat(0)=23-1, Ox(1)=1-3, ..., Horse(6)=11-13.
        # Wait. Ja(0), Chuk(1), In(2), Myo(3), Jin(4), Sa(5), O(6).
        # Yes, standard list indices: 0=Ja, ..., 6=O.
        # (12:38 is in 11:00-13:00).
        # (12*60+38 + 60) = 818. 818 // 120 = 6 (Horse). Correct.
        
        hour_idx = ((lmt_hour * 60 + lmt_min + 60) // 120) % 12
        
        return {
            'year_base': saju_year, 
            'month_idx': month_idx_from_in, 
            'day_dt': saju_day_dt, 
            'hour_idx': hour_idx,
            'lmt': lmt_dt,
            'utc': utc_dt, # Added for Daewoon calc
            's_lon': s_lon # Added for diagnosis
        }

    def get_term_time(self, target_deg, ref_dt_utc, search_dir):
        # search_dir: -1 (backward), 1 (forward)
        # Scan day by day
        t = ref_dt_utc
        # Get initial position relative to target
        # We need to handle 0/360 wrap.
        # Normalize diff to [-180, 180]
        def get_diff(dt):
            lon = self.compute_solar_term(dt)
            d = lon - target_deg
            while d <= -180: d += 360
            while d > 180: d -= 360
            return d

        # Looking for diff crossing 0.
        # Check initial diff
        d0 = get_diff(t)
        
        # Limit search to 35 days (max month length is ~31)
        # Step 1 day
        found_interval = None
        for i in range(35):
            t_next = t + timedelta(days=search_dir)
            d_next = get_diff(t_next)
            
            # Check Crossing
            # If sign changed, or if absolute value increased drastically (wrap?) no, diff is normalized.
            # If d0 is positive and search backward (-1), we expect d to decrease? No
            # We just check sign change of diff.
            if d0 * d_next <= 0:
                # Crossed!
                found_interval = (t, t_next) if search_dir == 1 else (t_next, t)
                break
            t = t_next
            d0 = d_next
            
        if not found_interval:
            return ref_dt_utc # Fallback
            
        # Binary Search
        t_start, t_end = found_interval
        for _ in range(20): # 2^20 ~ 1 sec precision in 1 day
            mid = t_start + (t_end - t_start) / 2
            d_mid = get_diff(mid)
            if abs(d_mid) < 0.00001: return mid
            
            d_start = get_diff(t_start)
            if d_start * d_mid <= 0:
                t_end = mid
            else:
                t_start = mid
                
        return t_start + (t_end - t_start) / 2

    def get_daewoon_term_times(self, birth_dt_utc, month_idx):
        # month_idx 0 (In) starts at 315 deg.
        # month_idx 1 (Myo) starts at 345 deg.
        # Pre-Term (Jolgi) degree:
        pre_deg = (315 + month_idx * 30) % 360
        next_deg = (pre_deg + 30) % 360
        
        # Find Pre-Term Time (Backward)
        pre_time = self.get_term_time(pre_deg, birth_dt_utc, -1)
        
        # Find Next-Term Time (Forward)
        next_time = self.get_term_time(next_deg, birth_dt_utc, 1)
        
        return pre_time, next_time
