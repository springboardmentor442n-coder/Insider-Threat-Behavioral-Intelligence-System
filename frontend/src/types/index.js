/**
 * @typedef {Object} User
 * @property {string} user - User identifier (e.g. USR0001)
 * @property {number} record_count - Number of days monitored
 * @property {number} max_risk_score - Peak final risk score (0-100)
 * @property {number} avg_risk_score - Average final risk score
 * @property {string} latest_severity - Latest severity level (Low, Medium, High, Critical)
 * @property {number} total_off_hours_logons - Total after-hours logons
 * @property {number} total_device_connects - Total USB device connects
 * @property {number} total_sensitive_files - Total sensitive file operations
 * @property {number} total_external_emails - Total external domain emails
 * @property {string} last_activity - ISO date string of last recorded activity
 * @property {string} status - Monitoring status (Active, Monitored, Under Investigation, Contained)
 */

/**
 * @typedef {Object} BehavioralRecord
 * @property {number} id - Record ID
 * @property {string} user - User identifier
 * @property {string} day - Date string (YYYY-MM-DD)
 * @property {number} logon_count - Total logons on day
 * @property {number} logoff_count - Total logoffs on day
 * @property {number} off_hours_logons - After-hours logons
 * @property {number} unique_pcs - Unique workstations used
 * @property {number} device_connects - USB device insertions
 * @property {number} device_disconnects - USB device removals
 * @property {number} unique_device_pcs - Unique PCs with USB activity
 * @property {number} file_activity_count - Total file access events
 * @property {number} unique_file_pcs - Unique PCs with file activity
 * @property {number} unique_files - Total unique files accessed
 * @property {number} sensitive_file_count - Sensitive file (.doc, .pdf, .zip, .csv) count
 * @property {number} email_count - Total emails sent
 * @property {number} attachment_count - Total attachments sent
 * @property {number} total_email_size - Cumulative email size in bytes
 * @property {number} unique_email_pcs - Unique PCs with email activity
 * @property {number} external_email_count - Emails sent to external domains
 * @property {number} http_request_count - Total HTTP requests
 * @property {number} unique_http_urls - Unique URLs visited
 * @property {number} off_hours_http - After-hours HTTP requests
 * @property {number} ml_risk_score - Gradient Boosting model risk score (0-100)
 * @property {number} behavioral_risk_score - Rule-based behavioral risk score (0-100)
 * @property {number} final_risk_score - Combined final risk score (0-100)
 * @property {number} prediction - ML Binary classification (0: Normal, 1: Suspicious)
 * @property {number} prediction_probability - Model probability of insider threat (0.0 to 1.0)
 * @property {string} severity - Risk level (Low, Medium, High, Critical)
 */

/**
 * @typedef {Object} RiskResult
 * @property {number} prediction - 0 (Normal) or 1 (Suspicious)
 * @property {number} prediction_probability - Confidence probability (0.0 to 1.0)
 * @property {number} ml_risk_score - ML risk score (0-100)
 * @property {number} behavioral_risk_score - Rule-based risk score (0-100)
 * @property {number} final_risk_score - Final risk score (0-100)
 * @property {string} severity - Severity rating
 */

/**
 * @typedef {Object} Alert
 * @property {number} id - Alert ID
 * @property {string} user - Target user ID
 * @property {string} day - Date detected
 * @property {string} severity - Critical, High, Medium, Low
 * @property {number} risk_score - Risk score associated with alert
 * @property {string} title - Alert title
 * @property {string} description - Detailed alert description
 * @property {string} status - New, Investigating, Resolved, Dismissed
 * @property {string} detected_time - Time stamp
 */

/**
 * @typedef {Object} Investigation
 * @property {number} id - Case ID
 * @property {string} title - Case title
 * @property {string} user - Subject user ID
 * @property {string} status - New, Investigating, Contained, Resolved
 * @property {string} severity - Critical, High, Medium, Low
 * @property {number} risk_score - Risk score
 * @property {string} created_date - Date created
 * @property {string} assigned_analyst - Assigned SOC analyst
 * @property {string} risk_factors - Comma-separated risk indicators
 * @property {string} notes - Analyst work log notes
 */

/**
 * @typedef {Object} Report
 * @property {string} generated_at - ISO timestamp
 * @property {number} total_users_monitored - Total user count
 * @property {number} total_behavioral_days_analyzed - Total user-days
 * @property {number} normal_records_count - Count of normal days
 * @property {number} suspicious_records_count - Count of suspicious days
 * @property {number} critical_severity_count - Critical count
 * @property {number} high_severity_count - High count
 * @property {number} medium_severity_count - Medium count
 * @property {number} low_severity_count - Low count
 * @property {Array} top_high_risk_users - List of top risk users
 */

export {};
