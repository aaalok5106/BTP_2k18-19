CREATE OR REPLACE PROCEDURE TEST(X IN VARCHAR, Y IN VARCHAR)
IS
  BEGIN
      --ASSUME Z+Y > 10;
      CURSOR Y IS
              SELECT A
              FROM T
              WHERE B = 50;
      BEGIN

          INSERT INTO T(A, B, C) VALUES (X+5, X-5, Y*(Z-2));

      END;
      --ASSERT A-B+C>0;
  END;
