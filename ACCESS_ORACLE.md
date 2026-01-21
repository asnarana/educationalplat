# How to Access Oracle Database Container

## Method 1: SQL*Plus (Command Line)

### Step 1: Access the container
```bash
docker exec -it oracle-db bash
```

### Step 2: Connect to the database
Inside the container, run:
```bash
sqlplus system/Oracle123@localhost:1521/FREEPDB1
```

### Step 3: Useful queries to see your data

**See all tables (includes Oracle system tables):**
```sql
SELECT table_name FROM user_tables;
```

**See ONLY your application tables (filter out system tables):**
```sql
SELECT table_name FROM user_tables 
WHERE table_name IN ('USERS', 'QUESTIONS', 'QUIZZES', 'ATTEMPTS')
ORDER BY table_name;
```

**Or see tables that start with your app's naming pattern:**
```sql
SELECT table_name FROM user_tables 
WHERE table_name NOT LIKE 'MVIEW$_%' 
  AND table_name NOT LIKE 'AQ$_%'
  AND table_name NOT LIKE 'OL$%'
  AND table_name NOT LIKE 'SCHEDULER_%'
  AND table_name NOT IN ('REDO_DB', 'REDO_LOG', 'SQLPLUS_PRODUCT_PROFILE', 'HELP')
ORDER BY table_name;
```

**View Users:**
```sql
SELECT id, username, role, created_at FROM users;
```

**View Questions:**
```sql
SELECT id, grade_level, topic, difficulty, prompt FROM questions ORDER BY grade_level, topic;
```

**View Quizzes:**
```sql
SELECT id, student_id, grade_level, grade_quiz_number, created_at FROM quizzes ORDER BY student_id, grade_level, created_at;
```

**View Attempts:**
```sql
SELECT id, quiz_id, student_id, score_total, passed, submitted_at FROM attempts ORDER BY submitted_at DESC;
```

**Count records:**
```sql
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM questions) as questions,
    (SELECT COUNT(*) FROM quizzes) as quizzes,
    (SELECT COUNT(*) FROM attempts) as attempts
FROM dual;
```

**View quiz with attempts:**
```sql
SELECT 
    q.id as quiz_id,
    q.student_id,
    q.grade_level,
    q.grade_quiz_number,
    COUNT(a.id) as attempt_count,
    MAX(a.score_total) as best_score
FROM quizzes q
LEFT JOIN attempts a ON q.id = a.quiz_id
GROUP BY q.id, q.student_id, q.grade_level, q.grade_quiz_number
ORDER BY q.student_id, q.grade_level, q.grade_quiz_number;
```

**Exit SQL*Plus:**
```sql
EXIT;
```

**Exit container:**
```bash
exit
```

---

## Method 2: Using SQL*Plus directly (one command)

```bash
docker exec -it oracle-db sqlplus system/Oracle123@localhost:1521/FREEPDB1
```

---

## Method 3: Using External SQL Client (DBeaver, SQL Developer, etc.)

**Connection Details:**
- **Host:** localhost
- **Port:** 1521
- **Service Name:** FREEPDB1
- **Username:** system
- **Password:** Oracle123

**Connection String:**
```
localhost:1521/FREEPDB1
```

---

## Quick Commands Reference

**Check if container is running:**
```bash
docker ps | grep oracle-db
```

**View container logs:**
```bash
docker logs oracle-db
```

**Restart container:**
```bash
docker restart oracle-db
```

**Stop container:**
```bash
docker stop oracle-db
```

**Start container:**
```bash
docker start oracle-db
```

---

## Your Database Tables

Based on your models, you have these tables:
1. **users** - Student and admin accounts
2. **questions** - Quiz questions bank
3. **quizzes** - Generated quizzes
4. **attempts** - Student quiz submissions

---

## How to Clear All Records

**⚠️ WARNING: This will delete ALL your data!**

### Method 1: DELETE (Safer - can rollback)
Delete records in order (respects foreign keys):

```sql
-- Delete in order: child tables first, then parent tables
DELETE FROM attempts;
DELETE FROM quizzes;
DELETE FROM questions;
DELETE FROM users;

-- Commit the changes
COMMIT;
```

**To undo before committing:**
```sql
ROLLBACK;
```

### Method 2: TRUNCATE (Faster - resets sequences, cannot rollback)
**⚠️ This cannot be rolled back!**

```sql
-- Truncate in order
TRUNCATE TABLE attempts;
TRUNCATE TABLE quizzes;
TRUNCATE TABLE questions;
TRUNCATE TABLE users;
```

**Note:** TRUNCATE also resets the sequence counters (IDs will start from 1 again).

### Method 3: Drop and Recreate Tables (Nuclear option)
**⚠️ This deletes everything including table structure!**

```sql
-- Drop tables in order
DROP TABLE attempts;
DROP TABLE quizzes;
DROP TABLE questions;
DROP TABLE users;
```

Then restart your FastAPI app - it will recreate the tables automatically.

### Quick Clear Script (Copy-paste ready)
```sql
-- Clear all data (keeps table structure)
DELETE FROM attempts;
DELETE FROM quizzes;
DELETE FROM questions;
DELETE FROM users;
COMMIT;

-- Verify everything is cleared
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM questions) as questions,
    (SELECT COUNT(*) FROM quizzes) as quizzes,
    (SELECT COUNT(*) FROM attempts) as attempts
FROM dual;
```

**Expected output after clearing:**
```
USERS    QUESTIONS    QUIZZES    ATTEMPTS
-----    ---------    -------    --------
0        0            0          0
```

---

## Common Issues

**If you get "ORA-12541: TNS:no listener":**
- Container might not be fully started. Wait a minute and try again.

**If connection fails:**
- Check container is running: `docker ps | grep oracle-db`
- Check container logs: `docker logs oracle-db`
- Make sure you're using the correct service name: `FREEPDB1`
