-- ==============================================================
-- SFU Food Pantry Management System - Complete Setup Script
-- CMPT 354 Group 5
-- Creates all tables and populates with sample data
-- ==============================================================
-- NOTE: Run this on SQL Server (cypress.csil.sfu.ca)
-- ==============================================================

-- Set database context
USE psa167354;

-- ==============================================================
-- PART 1: DROP EXISTING TABLES (if exists)
-- ==============================================================
-- Drop tables in reverse order of dependencies

IF OBJECT_ID('dbo.DISTRIBUTES', 'U') IS NOT NULL DROP TABLE dbo.DISTRIBUTES;
IF OBJECT_ID('dbo.INVENTORY_BATCH', 'U') IS NOT NULL DROP TABLE dbo.INVENTORY_BATCH;
IF OBJECT_ID('dbo.DONATION_ITEM', 'U') IS NOT NULL DROP TABLE dbo.DONATION_ITEM;
IF OBJECT_ID('dbo.PANTRY_VISIT', 'U') IS NOT NULL DROP TABLE dbo.PANTRY_VISIT;
IF OBJECT_ID('dbo.DONATION', 'U') IS NOT NULL DROP TABLE dbo.DONATION;
IF OBJECT_ID('dbo.FOOD_ITEM', 'U') IS NOT NULL DROP TABLE dbo.FOOD_ITEM;
IF OBJECT_ID('dbo.VISITOR', 'U') IS NOT NULL DROP TABLE dbo.VISITOR;
IF OBJECT_ID('dbo.USER_ACCOUNT', 'U') IS NOT NULL DROP TABLE dbo.USER_ACCOUNT;
IF OBJECT_ID('dbo.CATEGORY', 'U') IS NOT NULL DROP TABLE dbo.CATEGORY;
IF OBJECT_ID('dbo.DONOR', 'U') IS NOT NULL DROP TABLE dbo.DONOR;

-- ==============================================================
-- PART 2: CREATE TABLES
-- ==============================================================

-- Table: DONOR
CREATE TABLE dbo.DONOR (
    DonorID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    Phone VARCHAR(20),
    DonorType VARCHAR(30)
);

-- Table: CATEGORY
CREATE TABLE dbo.CATEGORY (
    CategoryID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL UNIQUE,
    Description VARCHAR(255),
    IsEssential BIT
);

-- Table: USER_ACCOUNT
CREATE TABLE dbo.USER_ACCOUNT (
    UserID INT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Role VARCHAR(30),
    IsActive BIT
);

-- Table: VISITOR
CREATE TABLE dbo.VISITOR (
    VisitorID INT PRIMARY KEY,
    VisitorType VARCHAR(30),
    Email VARCHAR(255)
);

-- Table: FOOD_ITEM
CREATE TABLE dbo.FOOD_ITEM (
    ItemID INT PRIMARY KEY,
    CategoryID INT,
    Name VARCHAR(100) NOT NULL,
    Unit VARCHAR(20),
    ReorderThreshold INT CHECK (ReorderThreshold >= 0),
    IsActive BIT,
    FOREIGN KEY (CategoryID) REFERENCES dbo.CATEGORY(CategoryID)
);

-- Table: DONATION
CREATE TABLE dbo.DONATION (
    DonationID INT PRIMARY KEY,
    DonorID INT,
    DonatedAt DATETIME NOT NULL,
    Notes VARCHAR(255),
    FOREIGN KEY (DonorID) REFERENCES dbo.DONOR(DonorID)
);

-- Table: PANTRY_VISIT
CREATE TABLE dbo.PANTRY_VISIT (
    VisitID INT PRIMARY KEY,
    VisitorID INT,
    UserID INT,
    CheckInAt DATETIME NOT NULL,
    Notes VARCHAR(255),
    FOREIGN KEY (VisitorID) REFERENCES dbo.VISITOR(VisitorID),
    FOREIGN KEY (UserID) REFERENCES dbo.USER_ACCOUNT(UserID)
);

-- Table: DONATION_ITEM
CREATE TABLE dbo.DONATION_ITEM (
    DonationID INT,
    LineNo INT,
    ItemID INT,
    UserID INT,
    QtyDonated INT CHECK (QtyDonated > 0),
    ExpiryDate DATE,
    PRIMARY KEY (DonationID, LineNo),
    FOREIGN KEY (DonationID) REFERENCES dbo.DONATION(DonationID),
    FOREIGN KEY (ItemID) REFERENCES dbo.FOOD_ITEM(ItemID),
    FOREIGN KEY (UserID) REFERENCES dbo.USER_ACCOUNT(UserID)
);

-- Table: INVENTORY_BATCH
CREATE TABLE dbo.INVENTORY_BATCH (
    ItemID INT,
    BatchNo INT,
    DonationID INT,
    LineNo INT,
    ReceivedAt DATETIME,
    ExpiryDate DATE,
    QtyReceived INT CHECK (QtyReceived > 0),
    QtyAvailable INT CHECK (QtyAvailable >= 0),
    StorageLocation VARCHAR(50),
    PRIMARY KEY (ItemID, BatchNo),
    FOREIGN KEY (ItemID) REFERENCES dbo.FOOD_ITEM(ItemID),
    FOREIGN KEY (DonationID, LineNo) REFERENCES dbo.DONATION_ITEM(DonationID, LineNo)
);

-- Table: DISTRIBUTES
CREATE TABLE dbo.DISTRIBUTES (
    VisitID INT,
    ItemID INT,
    BatchNo INT,
    QtyDistributed INT CHECK (QtyDistributed > 0),
    PRIMARY KEY (VisitID, ItemID, BatchNo),
    FOREIGN KEY (VisitID) REFERENCES dbo.PANTRY_VISIT(VisitID),
    FOREIGN KEY (ItemID, BatchNo) REFERENCES dbo.INVENTORY_BATCH(ItemID, BatchNo)
);

-- ==============================================================
-- PART 3: INSERT SAMPLE DATA
-- ==============================================================

-- Insert Donors
INSERT INTO dbo.DONOR (DonorID, Name, Email, Phone, DonorType) VALUES
(1, 'Alice Smith', 'alice@email.com', '604-111-1111', 'Individual'),
(2, 'Food Bank Org', 'foodbank@email.com', '604-222-2222', 'Organization'),
(3, 'Bob Lee', 'bob@email.com', '604-333-3333', 'Individual'),
(4, 'Community Church', 'church@email.com', '604-444-4444', 'Organization'),
(5, 'Carol White', 'carol@email.com', '604-555-5555', 'Individual');

-- Insert Categories
INSERT INTO dbo.CATEGORY (CategoryID, Name, Description, IsEssential) VALUES
(1, 'Canned Food', 'Non-perishable canned goods', 1),
(2, 'Grains', 'Rice, pasta, cereals', 1),
(3, 'Snacks', 'Snack items and bars', 0),
(4, 'Beverages', 'Juices and drinks', 0),
(5, 'Personal Care', 'Hygiene and personal care items', 1);

-- Insert User Accounts
INSERT INTO dbo.USER_ACCOUNT (UserID, Username, Role, IsActive) VALUES
(1, 'admin', 'Administrator', 1),
(2, 'volunteer1', 'Volunteer', 1),
(3, 'volunteer2', 'Volunteer', 1),
(4, 'manager', 'Manager', 1),
(5, 'staff1', 'Staff', 1);

-- Insert Visitors
INSERT INTO dbo.VISITOR (VisitorID, VisitorType, Email) VALUES
(1, 'Student', 'student1@sfu.ca'),
(2, 'Student', 'student2@sfu.ca'),
(3, 'Community', 'community1@email.com'),
(4, 'Staff', 'staff@sfu.ca'),
(5, 'Student', NULL);

-- Insert Food Items
INSERT INTO dbo.FOOD_ITEM (ItemID, CategoryID, Name, Unit, ReorderThreshold, IsActive) VALUES
(1, 1, 'Canned Beans', 'can', 20, 1),
(2, 2, 'Rice', 'kg', 30, 1),
(3, 3, 'Granola Bar', 'piece', 50, 1),
(4, 4, 'Orange Juice', 'bottle', 10, 1),
(5, 5, 'Soap', 'bar', 15, 1);

-- Insert Donations
INSERT INTO dbo.DONATION (DonationID, DonorID, DonatedAt, Notes) VALUES
(1, 1, '2026-03-01 10:00:00', 'Monthly donation from individual'),
(2, 2, '2026-03-02 11:00:00', 'Bulk donation from Food Bank'),
(3, 3, '2026-03-03 12:00:00', 'Student contribution drive'),
(4, 4, '2026-03-04 13:00:00', 'Community support initiative'),
(5, 5, '2026-03-05 14:00:00', 'Food drive participation');

-- Insert Pantry Visits
INSERT INTO dbo.PANTRY_VISIT (VisitID, VisitorID, UserID, CheckInAt, Notes) VALUES
(1, 1, 2, '2026-03-10 09:00:00', 'First visit - new student'),
(2, 2, 2, '2026-03-10 09:30:00', 'Regular visitor'),
(3, 3, 3, '2026-03-10 10:00:00', 'Community member'),
(4, 4, 5, '2026-03-10 10:30:00', 'Staff member pickup'),
(5, 5, 3, '2026-03-10 11:00:00', 'Student visit');

-- Insert Donation Items
INSERT INTO dbo.DONATION_ITEM (DonationID, LineNo, ItemID, UserID, QtyDonated, ExpiryDate) VALUES
(1, 1, 1, 2, 50, '2026-06-01'),
(1, 2, 2, 2, 40, '2026-07-01'),
(2, 1, 3, 3, 100, '2026-05-01'),
(3, 1, 4, 3, 30, '2026-04-15'),
(4, 1, 5, 5, 20, NULL);

-- Insert Inventory Batches
INSERT INTO dbo.INVENTORY_BATCH (ItemID, BatchNo, DonationID, LineNo, ReceivedAt, ExpiryDate, QtyReceived, QtyAvailable, StorageLocation) VALUES
(1, 1, 1, 1, '2026-03-01 10:30:00', '2026-06-01', 50, 40, 'Shelf A'),
(2, 1, 1, 2, '2026-03-01 10:45:00', '2026-07-01', 40, 35, 'Shelf B'),
(3, 1, 2, 1, '2026-03-02 11:30:00', '2026-05-01', 100, 90, 'Shelf C'),
(4, 1, 3, 1, '2026-03-03 12:30:00', '2026-04-15', 30, 25, 'Refrigerator'),
(5, 1, 4, 1, '2026-03-04 13:30:00', NULL, 20, 20, 'Storage Room');

-- Insert Distribution Records
INSERT INTO dbo.DISTRIBUTES (VisitID, ItemID, BatchNo, QtyDistributed) VALUES
(1, 1, 1, 5),
(2, 2, 1, 3),
(3, 3, 1, 10),
(4, 4, 1, 2),
(5, 5, 1, 1);

-- ==============================================================
-- PART 4: VERIFY DATA (SELECT statements to confirm)
-- ==============================================================

PRINT '=== Database Setup Complete ===';
PRINT '';
PRINT 'Total Donors:'; SELECT COUNT(*) FROM dbo.DONOR;
PRINT 'Total Categories:'; SELECT COUNT(*) FROM dbo.CATEGORY;
PRINT 'Total Users:'; SELECT COUNT(*) FROM dbo.USER_ACCOUNT;
PRINT 'Total Visitors:'; SELECT COUNT(*) FROM dbo.VISITOR;
PRINT 'Total Food Items:'; SELECT COUNT(*) FROM dbo.FOOD_ITEM;
PRINT 'Total Donations:'; SELECT COUNT(*) FROM dbo.DONATION;
PRINT 'Total Visits:'; SELECT COUNT(*) FROM dbo.PANTRY_VISIT;
PRINT 'Total Donation Items:'; SELECT COUNT(*) FROM dbo.DONATION_ITEM;
PRINT 'Total Inventory Batches:'; SELECT COUNT(*) FROM dbo.INVENTORY_BATCH;
PRINT 'Total Distributions:'; SELECT COUNT(*) FROM dbo.DISTRIBUTES;
PRINT '';
PRINT '✓ All tables created successfully!';
PRINT '✓ Sample data inserted successfully!';
