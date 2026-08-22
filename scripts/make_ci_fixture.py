"""Generate a TINY synthetic CERT r4.2 fixture for CI.

Goal: exercise the full pipeline (ingest -> features -> baselines -> detect ->
alerts) on data small enough to commit (kilobytes), spanning >120 days so the
baseline window has post-cutoff days to score. NOT for metrics - for proving the
code paths run and the security guards hold.
"""
import csv, os, random
from datetime import datetime, timedelta

random.seed(1729)  # deterministic - CI must be reproducible
ROOT = "backend/tests/fixtures/mini_cert"
R = f"{ROOT}/r4.2"

START = datetime(2010, 1, 4)          # a Monday
DAYS = 160                             # > 120 training days, so ~40 scored days
N_NORMAL = 12                          # ordinary employees
INSIDERS = ["INS0001", "INS0002", "INS0003"]   # 3 synthetic insiders (one per scenario)
ALL_USERS = [f"NRM{str(i+1).zfill(4)}" for i in range(N_NORMAL)] + INSIDERS

DEPTS = ["1 - Software", "2 - Sales", "3 - Engineering", "4 - HR"]
ROLES = ["ComputerProgrammer", "Salesman", "ITAdmin", "HRSpecialist"]

def dt(day, hour, minute=0):
    return (START + timedelta(days=day)).replace(hour=hour, minute=minute)

def fmt(d):  # CERT format: MM/DD/YYYY HH:MM:SS
    return d.strftime("%m/%d/%Y %H:%M:%S")

# ---- LDAP (employee roster) - one monthly file is enough ----
os.makedirs(f"{R}/LDAP", exist_ok=True)
with open(f"{R}/LDAP/2010-01.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["employee_name","user_id","email","role","business_unit",
                "functional_unit","department","team","supervisor"])
    for i, u in enumerate(ALL_USERS):
        w.writerow([f"User {i}", u, f"{u.lower()}@dtaa.com",
                    ROLES[i % len(ROLES)], "1", "2 - ResearchAndEngineering",
                    DEPTS[i % len(DEPTS)], "3 - Software", "User 0"])

# ---- event generators ----
logon_rows, device_rows, file_rows, email_rows = [], [], [], []
eid = 0
def nid():
    global eid; eid += 1
    return "{X%06d-T%06d-%06d}" % (eid, eid, eid)

for day in range(DAYS):
    weekday = (START + timedelta(days=day)).weekday()
    if weekday >= 5:      # skip weekends for normal users - realistic rhythm
        pass
    for i, u in enumerate(ALL_USERS):
        pc = f"PC-{1000+i}"
        is_ins = u in INSIDERS
        # after the training window, insiders misbehave
        attacking = is_ins and day > 130
        if weekday < 5:
            # normal logon 08:00-09:00, logoff 17:00-18:00
            logon_rows.append([nid(), fmt(dt(day, 8, random.randint(0,59))), u, pc, "Logon"])
            logon_rows.append([nid(), fmt(dt(day, 17, random.randint(0,59))), u, pc, "Logoff"])
            # a few file events
            for _ in range(random.randint(0,1)):
                file_rows.append([nid(), fmt(dt(day, random.randint(9,16), random.randint(0,59))),
                                  u, pc, f"F{random.randint(1000,9999)}.jpg", "filler"])
            # occasional email
            if random.random() < 0.25:
                email_rows.append([nid(), fmt(dt(day, random.randint(9,16), random.randint(0,59))),
                                   u, pc, "a@dtaa.com", "", "", f"{u}@dtaa.com",
                                   str(random.randint(5000,30000)), str(random.randint(0,3)), "filler"])
            # normal users almost never use USB; one normal user uses it sometimes
            if i == 0 and random.random() < 0.15:
                device_rows.append([nid(), fmt(dt(day, 13, random.randint(0,59))), u, pc, "Connect"])
                device_rows.append([nid(), fmt(dt(day, 13, random.randint(0,59))), u, pc, "Disconnect"])
        if attacking:
            # ATTACK: after-hours logon + burst of USB + big file activity
            logon_rows.append([nid(), fmt(dt(day, 22, random.randint(0,59))), u, pc, "Logon"])
            for _ in range(random.randint(3,6)):   # USB burst - the anomaly
                device_rows.append([nid(), fmt(dt(day, 22, random.randint(0,59))), u, pc, "Connect"])
                device_rows.append([nid(), fmt(dt(day, 23, random.randint(0,59))), u, pc, "Disconnect"])
            for _ in range(random.randint(4,7)):  # exfil - many files
                file_rows.append([nid(), fmt(dt(day, 22, random.randint(0,59))),
                                  u, pc, f"SECRET{random.randint(1000,9999)}.zip", "filler"])
            logon_rows.append([nid(), fmt(dt(day, 23, 59)), u, pc, "Logoff"])

def write(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header)
        w.writerows(rows)

write(f"{R}/logon.csv", ["id","date","user","pc","activity"], logon_rows)
write(f"{R}/device.csv", ["id","date","user","pc","activity"], device_rows)
write(f"{R}/file.csv", ["id","date","user","pc","filename","content"], file_rows)
write(f"{R}/email.csv", ["id","date","user","pc","to","cc","bcc","from","size","attachments","content"], email_rows)

# psychometric
with open(f"{R}/psychometric.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["employee_name","user_id","O","C","E","A","N"])
    for i, u in enumerate(ALL_USERS):
        w.writerow([f"User {i}", u, random.randint(10,45), random.randint(10,45),
                    random.randint(10,45), random.randint(10,45), random.randint(10,45)])

# ---- answers (labelling) ----
os.makedirs(f"{ROOT}/answers", exist_ok=True)
# insiders.csv: dataset,user,... (the WINDOW convention)
with open(f"{ROOT}/answers/insiders.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dataset","scenario","details","user","start","end"])
    win_start = (START + timedelta(days=131)).strftime("%m/%d/%Y %H:%M:%S")
    win_end = (START + timedelta(days=DAYS-1)).strftime("%m/%d/%Y %H:%M:%S")
    w.writerow(["4.2","1","synthetic","INS0001",win_start,win_end])
    w.writerow(["4.2","2","synthetic","INS0002",win_start,win_end])
    w.writerow(["4.2","3","synthetic","INS0003",win_start,win_end])

# per-insider EVENT-DAY answer files (the stricter convention)
def answer_days(user, scenario_dir):
    # NO header. Columns match CERT: event_type, {id}, TIMESTAMP(idx 2), user, pc, ...
    # Only column index 2 (the timestamp) is read by the ingester.
    os.makedirs(f"{ROOT}/answers/{scenario_dir}", exist_ok=True)
    with open(f"{ROOT}/answers/{scenario_dir}/{scenario_dir}-{user}.csv", "w", newline="") as f:
        w = csv.writer(f)
        for day in range(131, DAYS):
            d = START + timedelta(days=day)
            w.writerow(["device", f"{{X-{user}-{day}}}",
                        d.strftime("%m/%d/%Y %H:%M:%S"),
                        user, f"PC-{1000+ALL_USERS.index(user)}", "Connect"])
answer_days("INS0001", "r4.2-1")
answer_days("INS0002", "r4.2-2")
answer_days("INS0003", "r4.2-3")

# report sizes
import subprocess
print("=== fixture built ===")
for dirpath, _, files in os.walk(ROOT):
    for fn in files:
        p = os.path.join(dirpath, fn)
        print(f"  {os.path.getsize(p):>7,} B  {p.replace(ROOT+'/','')}")
total = sum(os.path.getsize(os.path.join(dp,fn)) for dp,_,fs in os.walk(ROOT) for fn in fs)
print(f"  TOTAL: {total:,} bytes ({total/1024:.0f} KB)")
print(f"  users: {len(ALL_USERS)}  days: {DAYS}  logon rows: {len(logon_rows)}  device: {len(device_rows)}  file: {len(file_rows)}")
