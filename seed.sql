-- SFU Food Pantry Management System
-- CMPT 354 Group 5 - Seed Data 

INSERT OR IGNORE INTO DONOR VALUES
(1,'Alice Smith','alice@email.com','1111111111','Individual'),
(2,'Food Bank Org','foodbank@email.com','2222222222','Organization'),
(3,'Bob Lee','bob@email.com','3333333333','Individual'),
(4,'Community Church','church@email.com','4444444444','Organization'),
(5,'Carol White','carol@email.com','5555555555','Individual');

INSERT OR IGNORE INTO CATEGORY VALUES
(1,'Canned Food','Non-perishable canned goods',1),
(2,'Grains','Rice, pasta, cereals',1),
(3,'Snacks','Snack items',0),
(4,'Beverages','Juices and drinks',0),
(5,'Personal Care','Hygiene items',1);

INSERT OR IGNORE INTO USER_ACCOUNT VALUES
(1,'admin','Administrator',1),
(2,'volunteer1','Volunteer',1),
(3,'volunteer2','Volunteer',1),
(4,'manager','Manager',1),
(5,'staff1','Staff',1);

INSERT OR IGNORE INTO VISITOR VALUES
(1,'Student','student1@email.com'),
(2,'Student','student2@email.com'),
(3,'Community','community1@email.com'),
(4,'Staff','staff@email.com'),
(5,'Student',NULL);

INSERT OR IGNORE INTO FOOD_ITEM VALUES
(1,1,'Canned Beans','can',20,1),
(2,2,'Rice','kg',30,1),
(3,3,'Granola Bar','piece',50,1),
(4,4,'Orange Juice','bottle',10,1),
(5,5,'Soap','bar',15,1);

INSERT OR IGNORE INTO DONATION VALUES
(1,1,'2026-03-01 10:00:00','Monthly donation'),
(2,2,'2026-03-02 11:00:00','Bulk donation'),
(3,3,'2026-03-03 12:00:00','Student contribution'),
(4,4,'2026-03-04 13:00:00','Community support'),
(5,5,'2026-03-05 14:00:00','Food drive');

INSERT OR IGNORE INTO PANTRY_VISIT VALUES
(1,1,2,'2026-03-10 09:00:00','First visit'),
(2,2,2,'2026-03-10 09:30:00','Regular visitor'),
(3,3,3,'2026-03-10 10:00:00','Community support'),
(4,4,5,'2026-03-10 10:30:00','Staff pickup'),
(5,5,3,'2026-03-10 11:00:00','Student visit');

INSERT OR IGNORE INTO DONATION_ITEM VALUES
(1,1,1,2,50,'2026-06-01'),
(1,2,2,2,40,'2026-07-01'),
(2,1,3,3,100,'2026-05-01'),
(3,1,4,3,30,'2026-04-15'),
(4,1,5,5,20,NULL);

INSERT OR IGNORE INTO INVENTORY_BATCH VALUES
(1,1,1,1,'2026-03-01','2026-06-01',50,40,'Shelf A'),
(2,1,1,2,'2026-03-01','2026-07-01',40,35,'Shelf B'),
(3,1,2,1,'2026-03-02','2026-05-01',100,90,'Shelf C'),
(4,1,3,1,'2026-03-03','2026-04-15',30,25,'Fridge'),
(5,1,4,1,'2026-03-04',NULL,20,20,'Storage');

INSERT OR IGNORE INTO DISTRIBUTES VALUES
(1,1,1,5),
(2,2,1,3),
(3,3,1,10),
(4,4,1,2),
(5,5,1,1);
