# Historical Leave Reconciliation Report

**Execution Timestamp:** 2026-11-03 11:37:25 UTC  
**Reconciliation Batch ID:** `RECON_20261103_113724_588502`  
**Database Environment:** `essl_production`  
**Mode:** `APPLY (Database Writes Enabled)`  
**Input Workbook:** `29-10-2026 leave details(1).xlsx`  

## Executive Summary

- **Total Excel Employee Rows Processed:** 47
- **Successfully Matched Employees:** 17
- **Unmatched Employees (Not in DB):** 29
- **Ambiguous Matches:** 1
- **Approved Leave Requests Reopened:** 6
- **Reversed Leave Deductions:** 0.0 days
- **Reversed Leave-Related LOP:** 0.0 days
- **Leave Ledgers Proposed for Update:** 0
- **Attendance Recalculation Ranges:** 2
- **Overlapping Payroll Periods Flagged:** 2

## 1. Employee Matching Report

| Company | Excel Employee Name | Excel DOJ | Matched Employee ID | Matched Code | Match Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| IDS Financial Services Pvt Ltd | Saravanakumar.C.S | 2010-08-24 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Nirmala Saravanakumar | 2010-08-24 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Kumaresan.R | 2017-04-01 | - | - | AMBIGUOUS_MULTIPLE_MATCHES |
| IDS Financial Services Pvt Ltd | Devi R | 2017-04-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Vijay S | 2017-04-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Gunasundari | 2018-01-01 | 27 | 201801 | MATCHED_EXACT_DOJ |
| IDS Financial Services Pvt Ltd | Sampath Kumar.S | 2018-02-01 | 19 | 201803 | MATCHED_DOJ_DISAMBIGUATED |
| IDS Financial Services Pvt Ltd | Priyadharshini.R | 2018-04-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Madhu Sri | 2018-09-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Divin Kumar.I | 2019-01-01 | 23 | 201902 | MATCHED_DOJ_DISAMBIGUATED |
| IDS Financial Services Pvt Ltd | Banumathi | 2019-11-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Raja C | 2019-12-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Nandhakumar | 2020-10-10 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Ramesh G | 2021-04-01 | 17 | 202102 | MATCHED_EXACT_DOJ |
| IDS Financial Services Pvt Ltd | Sumathi A | 2021-08-10 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Swapna | 2022-05-21 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Geetha | 2023-07-01 | 21 | 202303 | MATCHED_EXACT_DOJ |
| IDS Financial Services Pvt Ltd | Rajilakshmi | 2023-07-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Trisha | 2025-03-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Monisha.A | 2025-03-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Financial Services Pvt Ltd | Iswarya.G |  | - | - | UNMATCHED_NOT_FOUND |
| IDS e Solutions Pvt Ltd | Saravanakumar.C.S | 2013-09-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS e Solutions Pvt Ltd | Prasanna Prabhu.N.G | 2013-09-01 | 14 | 1021 | MATCHED_EXACT_DOJ |
| IDS e Solutions Pvt Ltd | Badri Narayanan.R | 2014-10-01 | 30 | 1050 | MATCHED_EXACT_DOJ |
| IDS e Solutions Pvt Ltd | Latha | 2019-11-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS e Solutions Pvt Ltd | Dhanasekar | 2023-04-01 | 29 | 1085 | MATCHED_EXACT_DOJ |
| IDS e Solutions Pvt Ltd | Naveen Raj.S | 2023-09-01 | 28 | 1086 | MATCHED_EXACT_DOJ |
| IDS e Solutions Pvt Ltd | Arunkumar T | 2024-06-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS e Solutions Pvt Ltd | Deepika | 2026-04-01 | 13 | 1089 | MATCHED_EXACT_DOJ |
| IDS e Solutions Pvt Ltd | Chandana sampathkumar | 2026-04-01 | 16 | 1090 | MATCHED_EXACT_DOJ |
| IDS e Solutions Pvt Ltd | Lokesh G | 2026-10-01 | 15 | 1091 | MATCHED_EXACT_DOJ |
| IDS Logistics confirm staffs | Waheeda | 2023-10-01 | 6 | 423001 | MATCHED_NAME_COMPANY |
| IDS Logistics confirm staffs | Janarthanan.V | 2024-10-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS Logistics confirm staffs | Sathiyapriya.J | 2025-03-01 | 8 | 425001 | MATCHED_EXACT_DOJ |
| IDS Logistics confirm staffs | Karthick | 2025-04-01 | 9 | 425002 | MATCHED_EXACT_DOJ |
| IDS Logistics confirm staffs | Vairamani | 2026-01-01 | 10 | 426001 | MATCHED_EXACT_DOJ |
| IDS Logistics confirm staffs | Ushanandhini | 2026-02-01 | 11 | 426002 | MATCHED_EXACT_DOJ |
| IDS INDUSTRIES | Prabagakaran | 2026-01-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS INDUSTRIES | N G Anukrishnan | 2026-04-01 | - | - | UNMATCHED_NOT_FOUND |
| IDS INDUSTRIES | Cauvery | 2026-04-01 | - | - | UNMATCHED_NOT_FOUND |
| Contract | Akashya |  | - | - | UNMATCHED_NOT_FOUND |
| Contract | Rohini |  | - | - | UNMATCHED_NOT_FOUND |
| Contract | Ram mohana Reddy |  | - | - | UNMATCHED_NOT_FOUND |
| Contract | Shivaramu |  | - | - | UNMATCHED_NOT_FOUND |
| Contract | Sajad anasari |  | - | - | UNMATCHED_NOT_FOUND |
| Contract | Maheshwari/office cleaning |  | - | - | UNMATCHED_NOT_FOUND |
| Contract | Latha /bathroom cleaning |  | - | - | UNMATCHED_NOT_FOUND |

## 2. Leave Balance Report

| Employee | Leave Type | Excel Elig | Excel Avail | Proposed Credited | Proposed Consumed | Proposed Available | Validation |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| 27 (GUNASUNDARI  D) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 27 (GUNASUNDARI  D) | SL | 4.5 | 0.0 | 4.5 | 0.0 | 4.5 | OK |
| 27 (GUNASUNDARI  D) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 19 (SAMPATH KUMAR S) | CL | 1.0 | 0.0 | 1.0 | 0.0 | 1.0 | OK |
| 19 (SAMPATH KUMAR S) | SL | 26.0 | 3.0 | 26.0 | 3.0 | 23.0 | OK |
| 19 (SAMPATH KUMAR S) | EL | 31.5 | 0.0 | 31.5 | 0.0 | 31.5 | OK |
| 23 (DIVINKUMAR  I) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 23 (DIVINKUMAR  I) | SL | 8.5 | 0.0 | 8.5 | 0.0 | 8.5 | OK |
| 23 (DIVINKUMAR  I) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 17 (RAMESH G) | CL | 6.0 | 1.0 | 6.0 | 1.0 | 5.0 | OK |
| 17 (RAMESH G) | SL | 19.5 | 0.0 | 19.5 | 0.0 | 19.5 | OK |
| 17 (RAMESH G) | EL | 20.0 | 0.0 | 20.0 | 0.0 | 20.0 | OK |
| 21 (GEETHA KV) | CL | 6.0 | 1.0 | 6.0 | 1.0 | 5.0 | OK |
| 21 (GEETHA KV) | SL | 6.0 | 0.0 | 6.0 | 0.0 | 6.0 | OK |
| 21 (GEETHA KV) | EL | 6.0 | 0.0 | 6.0 | 0.0 | 6.0 | OK |
| 14 (PRASANNA PRABHU N G) | CL | 8.0 | 0.0 | 8.0 | 0.0 | 8.0 | OK |
| 14 (PRASANNA PRABHU N G) | SL | 27.0 | 4.0 | 27.0 | 4.0 | 23.0 | OK |
| 14 (PRASANNA PRABHU N G) | EL | 50.0 | 0.0 | 50.0 | 0.0 | 50.0 | OK |
| 30 (BADRI NARAYAN  VR) | CL | 9.0 | 0.0 | 9.0 | 0.0 | 9.0 | OK |
| 30 (BADRI NARAYAN  VR) | SL | 9.0 | 0.0 | 9.0 | 0.0 | 9.0 | OK |
| 30 (BADRI NARAYAN  VR) | EL | 47.0 | 0.0 | 47.0 | 0.0 | 47.0 | OK |
| 29 (DHANASEKAR V) | CL | 3.0 | 0.0 | 3.0 | 0.0 | 3.0 | OK |
| 29 (DHANASEKAR V) | SL | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | OK |
| 29 (DHANASEKAR V) | EL | 9.0 | 0.0 | 9.0 | 0.0 | 9.0 | OK |
| 28 (NAVEEN RAJ S) | CL | 8.0 | 1.0 | 8.0 | 1.0 | 7.0 | OK |
| 28 (NAVEEN RAJ S) | SL | 17.0 | 0.0 | 17.0 | 0.0 | 17.0 | OK |
| 28 (NAVEEN RAJ S) | EL | 8.0 | 0.0 | 8.0 | 0.0 | 8.0 | OK |
| 13 (DEEPIKA JAGANATHAN) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 13 (DEEPIKA JAGANATHAN) | SL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 13 (DEEPIKA JAGANATHAN) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 16 (CHANDANA SAMPATH KUMAR) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 16 (CHANDANA SAMPATH KUMAR) | SL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 16 (CHANDANA SAMPATH KUMAR) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 15 (LOKESH  R G) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 15 (LOKESH  R G) | SL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 15 (LOKESH  R G) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 6 (WAHEEDA BIJOY) | CL | 9.0 | 1.0 | 9.0 | 1.0 | 8.0 | OK |
| 6 (WAHEEDA BIJOY) | SL | 12.0 | 1.0 | 12.0 | 1.0 | 11.0 | OK |
| 6 (WAHEEDA BIJOY) | EL | 16.0 | 0.0 | 16.0 | 0.0 | 16.0 | OK |
| 8 (SATHIYAPRIYA J) | CL | 2.0 | 0.0 | 2.0 | 0.0 | 2.0 | OK |
| 8 (SATHIYAPRIYA J) | SL | 9.0 | 0.0 | 9.0 | 0.0 | 9.0 | OK |
| 8 (SATHIYAPRIYA J) | EL | 15.0 | 0.0 | 15.0 | 0.0 | 15.0 | OK |
| 9 (KARTHIK C) | CL | 3.0 | 1.0 | 3.0 | 1.0 | 2.0 | OK |
| 9 (KARTHIK C) | SL | 3.0 | 3.0 | 3.0 | 3.0 | 0.0 | OK |
| 9 (KARTHIK C) | EL | 3.0 | 0.0 | 3.0 | 0.0 | 3.0 | OK |
| 10 (VAIRAMANI P) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 10 (VAIRAMANI P) | SL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 10 (VAIRAMANI P) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 11 (USHA NANDHINI  S) | CL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 11 (USHA NANDHINI  S) | SL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |
| 11 (USHA NANDHINI  S) | EL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | OK |

## 3. Approval Reconciliation Report

| Employee | Approval ID | Leave Type | Leave Dates | Current Status | Allocated Leave | Associated LOP | Proposed Status |
| :--- | :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| 6 (WAHEEDA BIJOY) | `6ae5924ac635b46ae1004a45` | SL | 2026-10-07 to 2026-10-07 | APPROVED | 0.0 | 0.0 | PENDING |
| 6 (WAHEEDA BIJOY) | `6ae59260c635b46ae1004a47` | CL | 2026-10-22 to 2026-10-22 | APPROVED | 0.0 | 0.0 | PENDING |
| 9 (KARTHIK C) | `6ae58ca4c635b46ae1004a35` | CL | 2026-10-16 to 2026-10-16 | APPROVED | 0.0 | 0.0 | PENDING |
| 9 (KARTHIK C) | `6ae58cc5c635b46ae1004a37` | SL | 2026-10-20 to 2026-10-20 | APPROVED | 0.0 | 0.0 | PENDING |
| 9 (KARTHIK C) | `6ae58cfac635b46ae1004a39` | SL | 2026-10-21 to 2026-10-21 | APPROVED | 0.0 | 0.0 | PENDING |
| 9 (KARTHIK C) | `6ae58d13c635b46ae1004a3b` | SL | 2026-10-22 to 2026-10-22 | APPROVED | 0.0 | 0.0 | PENDING |

## 4. Attendance Impact Report

| Employee | Date Range | Current Status | Expected Recalculation | Impact |
| :--- | :--- | :--- | :--- | :--- |
| 6 (WAHEEDA BIJOY) | 2026-10-07 to 2026-10-22 | Leave | Absent/Biometric punches (Reopened request) | SUCCESSFULLY_RECALCULATED |
| 9 (KARTHIK C) | 2026-10-16 to 2026-10-22 | Leave | Absent/Biometric punches (Reopened request) | SUCCESSFULLY_RECALCULATED |

## 5. Payroll Impact Report

| Employee | Payroll Period | Payroll Status | Affected Attendance | Action |
| :--- | :--- | :--- | :--- | :--- |
| 6 (WAHEEDA BIJOY) | 2026-10-01 to 2026-10-31 | OPEN | 2026-10-07 to 2026-10-22 | ALLOW_RECALCULATION |
| 9 (KARTHIK C) | 2026-10-01 to 2026-10-31 | OPEN | 2026-10-16 to 2026-10-22 | ALLOW_RECALCULATION |

## 6. Exceptions Report

| Exception Type | Subject / Employee | Details |
| :--- | :--- | :--- |
| `EMPLOYEE_NOT_MATCHED` | Saravanakumar.C.S | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Nirmala Saravanakumar | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Kumaresan.R | Status: AMBIGUOUS_MULTIPLE_MATCHES, Candidates count: 2 |
| `EMPLOYEE_NOT_MATCHED` | Devi R | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Vijay S | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Priyadharshini.R | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Madhu Sri | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Banumathi | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Raja C | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Nandhakumar | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Sumathi A | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Swapna | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Rajilakshmi | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Trisha | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Monisha.A | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Iswarya.G | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Saravanakumar.C.S | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Latha | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Arunkumar T | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Janarthanan.V | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Prabagakaran | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | N G Anukrishnan | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Cauvery | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Akashya | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Rohini | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Ram mohana Reddy | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Shivaramu | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Sajad anasari | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Maheshwari/office cleaning | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
| `EMPLOYEE_NOT_MATCHED` | Latha /bathroom cleaning | Status: UNMATCHED_NOT_FOUND, Candidates count: 0 |
