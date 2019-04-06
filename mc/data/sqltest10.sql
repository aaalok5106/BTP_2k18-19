
PROCEDURE bill(p_reservation_id IN NUMBER) IS
        n_o_visits   NUMBER;
    BEGIN
        SELECT SUM(WEIGHT) INTO MY_WEIGHT FROM LOADS, ROUTES
            WHERE X=Y OR LOAD_ID IN (SELECT LOAD_ID FROM LOADS WHERE CUSTOMER_ID = CUSTOMER)
                  AND START_TIME >= SYSDATE AND START_TIME <= SYSDATE + 7;

        nothing := 6;

        UPDATE ROUTES
            SET PRICE = PRICE*((100 - PERCENT)/100)
            WHERE LOAD_ID IN (SELECT LOAD_ID FROM LOADS WHERE CUSTOMER_ID = CUSTOMER)
                  AND START_TIME >= SYSDATE AND START_TIME <= SYSDATE + 7;

    END;
