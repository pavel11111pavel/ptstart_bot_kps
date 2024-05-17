SELECT 'CREATE DATABASE replacedbname' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replacedbname')\gexec
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replacerepluser') THEN
        CREATE USER replacerepluser WITH REPLICATION ENCRYPTED PASSWORD 'replacereplpassword'; 
    END IF; 
END $$;
ALTER USER replacepostgresuser WITH PASSWORD 'replacepostgrespassword';
\c replacedbname;
DROP DATABASE IF EXISTS base_1;
CREATE DATABASE base_1;
\c base_1;
CREATE TABLE IF NOT EXISTS email(id SERIAL PRIMARY KEY, email VARCHAR(100) NOT NULL);
CREATE TABLE IF NOT EXISTS phone_number(id SERIAL PRIMARY KEY, phone_number VARCHAR(100) NOT NULL);
INSERT INTO email(email) VALUES('asdd@mail.ru');
INSERT INTO phone_number(phone_number) VALUES('+79001237689');
