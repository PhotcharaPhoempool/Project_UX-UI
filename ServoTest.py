from gpiozero import Servo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep, time
import json
import os

# ====== CONFIG ======
SERVO_PIN = 23

# ปรับให้เข้ากับเซอร์โวของคุณ (ค่าเริ่มต้นที่มักใช้ได้ดี)
MIN_PULSE = 0.6 / 1000   # 0.6ms
MAX_PULSE = 2.4 / 1000   # 2.4ms

FRAME_DELAY = 0.003       # หน่วงตอนเล่นกลับ (ยิ่งน้อยยิ่งเร็ว/อาจกระตุก)
SMOOTH_STEP = 0.005       # ความละเอียดการไล่ค่า (-1..1) ยิ่งเล็กยิ่งเนียนแต่ช้า

SAVE_FILE = "pose.json"
# ====================

factory = LGPIOFactory()

servo = Servo(
    SERVO_PIN,
    min_pulse_width=MIN_PULSE,
    max_pulse_width=MAX_PULSE,
    pin_factory=factory
)

# ค่าปัจจุบันของ servo ในช่วง -1..1 (gpiozero)
current_pos = 0.0
t0 = time()

# โหลดไฟล์เก่า (ถ้ามี)
poses = []
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            poses = json.load(f)
        if not isinstance(poses, list):
            poses = []
    except Exception:
        poses = []

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def angle_to_pos(angle_deg: float) -> float:
    # แปลง 0..180 -> -1..1
    angle_deg = clamp(angle_deg, 0.0, 180.0)
    return (angle_deg / 90.0) - 1.0

def pos_to_angle(pos: float) -> float:
    # แปลง -1..1 -> 0..180
    pos = clamp(pos, -1.0, 1.0)
    return (pos + 1.0) * 90.0

def move_to_pos(target_pos: float, smooth=True):
    global current_pos
    target_pos = clamp(target_pos, -1.0, 1.0)

    if not smooth:
        servo.value = target_pos
        current_pos = target_pos
        return

    # ไล่ค่าแบบเนียน ลดการกระชาก
    while abs(current_pos - target_pos) > SMOOTH_STEP:
        if current_pos < target_pos:
            current_pos += SMOOTH_STEP
        else:
            current_pos -= SMOOTH_STEP
        servo.value = current_pos
        sleep(FRAME_DELAY)

    servo.value = target_pos
    current_pos = target_pos

def save_poses():
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(poses, f, ensure_ascii=False, indent=2)

def print_help():
    print("\nคำสั่ง:")
    print("  พิมพ์องศา 0-180  -> ให้เซอร์โวไปมุมนั้น")
    print("  s               -> บันทึกมุมปัจจุบัน (keyframe)")
    print("  p               -> เล่นกลับทั้งหมดแบบเนียน")
    print("  l               -> แสดงรายการที่บันทึกไว้")
    print("  c               -> ล้างรายการที่บันทึกไว้")
    print("  h               -> กลับ 0° (home)")
    print("  q               -> ออก\n")

print("=== Teach & Playback (1 Servo) ===")
print(f"GPIO: {SERVO_PIN} | save: {SAVE_FILE}")
print_help()

# เริ่มต้นที่ 0°
move_to_pos(angle_to_pos(0), smooth=False)

try:
    while True:
        cmd = input(">> ").strip().lower()

        if cmd == "q":
            break

        if cmd == "help" or cmd == "?":
            print_help()
            continue

        if cmd == "h":
            print("Home: 0°")
            move_to_pos(angle_to_pos(0))
            continue

        if cmd == "s":
            angle_now = pos_to_angle(current_pos)
            entry = {
                "t": round(time() - t0, 3),           # เวลาอ้างอิง (ไว้ใช้ต่อยอด)
                "angle": round(angle_now, 2)
            }
            poses.append(entry)
            save_poses()
            print(f"บันทึก: {entry['angle']}° (รวม {len(poses)} จุด)")
            continue

        if cmd == "l":
            if not poses:
                print("ยังไม่มีข้อมูลที่บันทึกไว้")
            else:
                for i, e in enumerate(poses, 1):
                    print(f"{i:02d}) {e['angle']}°  (t={e['t']}s)")
            continue

        if cmd == "c":
            poses.clear()
            save_poses()
            print("ล้างรายการแล้ว")
            continue

        if cmd == "p":
            if not poses:
                print("ยังไม่มี keyframe ให้เล่นกลับ (กด s เพื่อบันทึกก่อน)")
                continue

            print(f"Play: {len(poses)} จุด")
            # (ตัวง่าย) เล่นตามลำดับที่บันทึกไว้
            for e in poses:
                a = float(e["angle"])
                print(f"-> {a:.1f}°")
                move_to_pos(angle_to_pos(a), smooth=True)
                sleep(0.3)  # หน่วงค้างแต่ละ keyframe ปรับได้
            print("จบการเล่นกลับ")
            continue

        # ถ้าไม่ใช่คำสั่งพิเศษ ให้พยายามตีความเป็นองศา
        try:
            angle = float(cmd)
            angle = clamp(angle, 0.0, 180.0)
            print(f"ไปที่ {angle:.1f}°")
            move_to_pos(angle_to_pos(angle), smooth=True)
        except ValueError:
            print("คำสั่งไม่ถูกต้อง (พิมพ์ ? เพื่อดู help)")

finally:
    # ปล่อยสัญญาณ (ให้หยุดค้างถ้าต้องการก็ได้ แต่โดยทั่วไปปล่อยจะดีตอนทดลอง)
    servo.detach()
    print("ออกจากโปรแกรมแล้ว")
