--https://docs.oracle.com/cd/E15846_01/doc.21/e15222/unit_testing.htm#RPTUG45066
create or replace PROCEDURE award_bonus (emp_id NUMBER, sales_amt NUMBER) AS
  commission    REAL;
  comm_missing  EXCEPTION;
BEGIN
  SELECT commission_pct INTO commission
    FROM employees
      WHERE employee_id = emp_id;
 
  IF commission IS NULL THEN
    RAISE comm_missing;
  ELSE
    UPDATE employees
      SET salary = salary + sales_amt*commission
        WHERE employee_id = emp_id;
  END IF;
END award_bonus;
