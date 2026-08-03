# CERT Dataset Data Dictionary

| Dataset      | Column          | Data Type      | Category    | Used In Timeline   | Used In Feature Engineering   | Used In Machine Learning   | Description               |
|:-------------|:----------------|:---------------|:------------|:-------------------|:------------------------------|:---------------------------|:--------------------------|
| device       | id              | object         | Identifier  | No                 | No                            | No                         | Unique Event Identifier   |
| device       | date            | object         | Timestamp   | Yes                | Yes                           | No                         | Timestamp of Event        |
| device       | user            | object         | Employee    | Yes                | Yes                           | Yes                        | Employee Identifier       |
| device       | pc              | object         | Computer    | Yes                | Yes                           | No                         | Computer Name             |
| device       | activity        | object         | Activity    | Yes                | Yes                           | Yes                        | Type of Activity          |
| email        | id              | object         | Identifier  | No                 | No                            | No                         | Unique Event Identifier   |
| email        | date            | datetime64[us] | Timestamp   | Yes                | Yes                           | No                         | Timestamp of Event        |
| email        | user            | object         | Employee    | Yes                | Yes                           | Yes                        | Employee Identifier       |
| email        | pc              | object         | Computer    | Yes                | Yes                           | No                         | Computer Name             |
| email        | to              | object         | Email       | No                 | No                            | No                         | Email Recipient           |
| email        | cc              | object         | Email       | No                 | No                            | No                         | Carbon Copy               |
| email        | bcc             | object         | Email       | No                 | No                            | No                         | Blind Carbon Copy         |
| email        | from            | object         | Email       | No                 | No                            | No                         | Email Sender              |
| email        | size            | int64          | Metadata    | No                 | No                            | No                         | Object Size               |
| email        | attachments     | int64          | Email       | No                 | No                            | No                         | Attachment Count          |
| email        | content         | object         | Content     | Yes                | Yes                           | Yes                        | Associated Content        |
| file         | id              | object         | Identifier  | No                 | No                            | No                         | Unique Event Identifier   |
| file         | date            | object         | Timestamp   | Yes                | Yes                           | No                         | Timestamp of Event        |
| file         | user            | object         | Employee    | Yes                | Yes                           | Yes                        | Employee Identifier       |
| file         | pc              | object         | Computer    | Yes                | Yes                           | No                         | Computer Name             |
| file         | filename        | object         | File        | Yes                | Yes                           | Yes                        | Accessed File             |
| file         | content         | object         | Content     | Yes                | Yes                           | Yes                        | Associated Content        |
| http         | id              | object         | Identifier  | No                 | No                            | No                         | Unique Event Identifier   |
| http         | date            | datetime64[us] | Timestamp   | Yes                | Yes                           | No                         | Timestamp of Event        |
| http         | user            | object         | Employee    | Yes                | Yes                           | Yes                        | Employee Identifier       |
| http         | pc              | object         | Computer    | Yes                | Yes                           | No                         | Computer Name             |
| http         | url             | object         | Website     | Yes                | Yes                           | Yes                        | Visited Website           |
| http         | content         | object         | Content     | Yes                | Yes                           | Yes                        | Associated Content        |
| 2009-12      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2009-12      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2009-12      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2009-12      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2009-12      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2009-12      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2009-12      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2009-12      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2009-12      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-01      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-01      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-01      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-02      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-02      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-02      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-03      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-03      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-03      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-04      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-04      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-04      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-05      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-05      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-05      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-06      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-06      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-06      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-07      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-07      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-07      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-08      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-08      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-08      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-09      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-09      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-09      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-10      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-10      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-10      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-11      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-11      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-11      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2010-12      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2010-12      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2010-12      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2011-01      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2011-01      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-01      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2011-02      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2011-02      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-02      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2011-03      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2011-03      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-03      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2011-04      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2011-04      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-04      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| 2011-05      | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| 2011-05      | email           | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | role            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | business_unit   | int64          | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | functional_unit | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | department      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | team            | object         | Other       | No                 | No                            | No                         | Description Not Available |
| 2011-05      | supervisor      | object         | Other       | No                 | No                            | No                         | Description Not Available |
| logon        | id              | object         | Identifier  | No                 | No                            | No                         | Unique Event Identifier   |
| logon        | date            | object         | Timestamp   | Yes                | Yes                           | No                         | Timestamp of Event        |
| logon        | user            | object         | Employee    | Yes                | Yes                           | Yes                        | Employee Identifier       |
| logon        | pc              | object         | Computer    | Yes                | Yes                           | No                         | Computer Name             |
| logon        | activity        | object         | Activity    | Yes                | Yes                           | Yes                        | Type of Activity          |
| psychometric | employee_name   | object         | Employee    | No                 | Yes                           | No                         | Employee Name             |
| psychometric | user_id         | object         | Employee    | No                 | Yes                           | No                         | Employee Identifier       |
| psychometric | O               | int64          | Personality | No                 | Yes                           | Yes                        | Openness                  |
| psychometric | C               | int64          | Personality | No                 | Yes                           | Yes                        | Conscientiousness         |
| psychometric | E               | int64          | Personality | No                 | Yes                           | Yes                        | Extraversion              |
| psychometric | A               | int64          | Personality | No                 | Yes                           | Yes                        | Agreeableness             |
| psychometric | N               | int64          | Personality | No                 | Yes                           | Yes                        | Neuroticism               |