# Feature Engineering

Feature engineering transforms raw employee activity logs into meaningful attributes for machine learning.

## Features Created

### login_hour

Extracted from the login timestamp.

Purpose:
- Analyze employee login time.

---

### day

Day of the month.

Purpose:
- Analyze daily behavior.

---

### month

Month extracted from timestamp.

Purpose:
- Analyze monthly activity.

---

### weekday

Day name extracted from timestamp.

Purpose:
- Compare weekday and weekend activity.

---

### working_hours

Values:

- Working Hours
- After Hours

Purpose:

Identify employee activity outside normal office hours.

---

### is_after_hours

Binary Feature

0 → Working Hours

1 → After Hours

Purpose

Useful for machine learning classification models.