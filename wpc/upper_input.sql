CREATE OR REPLACE PROCEDURE ATM_WITHDRAW_OPER( ACC_NO INT, AMT INT) IS
BAL INT;
MIN_BAL INT;
BEGIN
	ASSUME BALANCE>0 ;

    SELECT BALANCE INTO BAL FROM ACCOUNT WHERE ACCNO = ACC_NO ;
    MIN_BAL := BAL - AMT ;
        IF AMT < 10000 AND MIN_BAL > 0 THEN
            UPDATE ACCOUNT SET BALANCE = BALANCE-AMT WHERE ACCNO = ACC_NO ;
        END IF;
ASSERT BALANCE>0 ;
	END;