# 1. Database Normalization

## (a) Functional Dependencies

Here are the functional dependencies (FDs) we identified for each table in our schema, including the ones involving the primary key.

**DONOR(DonorID, Name, Email, Phone, DonorType)**
- `DonorID → Name, Email, Phone, DonorType` — the donor ID identifies one person/organization, so it determines their name, contact info, and donor type.
- `Email → DonorID` — we made Email UNIQUE, so a given email belongs to only one donor.

**CATEGORY(CategoryID, Name, Description, IsEssential)**
- `CategoryID → Name, Description, IsEssential` — the ID of a food category fixes its name, description, and whether it is an essential item.
- `Name → CategoryID` — category Name is also UNIQUE, so it can identify the category on its own.

**USER_ACCOUNT(UserID, Username, Role, IsActive)**
- `UserID → Username, Role, IsActive` — each user account has one username, one role (admin or volunteer), and one active/inactive flag.
- `Username → UserID` — Username is UNIQUE so it also identifies the user.

**VISITOR(VisitorID, VisitorType, Email)**
- `VisitorID → VisitorType, Email` — a visitor record has one type (student/staff/community) and one email.

**FOOD_ITEM(ItemID, CategoryID, Name, Unit, ReorderThreshold, IsActive)**
- `ItemID → CategoryID, Name, Unit, ReorderThreshold, IsActive` — the item ID determines what the item is, its unit (can/box/kg), the reorder threshold, and whether it is active.

**DONATION(DonationID, DonorID, DonatedAt, Notes)**
- `DonationID → DonorID, DonatedAt, Notes` — each donation event has one donor, one timestamp, and one notes field.

**PANTRY_VISIT(VisitID, VisitorID, UserID, CheckInAt, Notes)**
- `VisitID → VisitorID, UserID, CheckInAt, Notes` — each check-in has one visitor, one staff member who logged it, one time, and optional notes.

**DONATION_ITEM(DonationID, LineNo, ItemID, UserID, QtyDonated, ExpiryDate)**
- `DonationID, LineNo → ItemID, UserID, QtyDonated, ExpiryDate` — each line on a donation slip is one food item, one quantity, one expiry, and the staff who received it.

**INVENTORY_BATCH(ItemID, BatchNo, DonationID, LineNo, ReceivedAt, ExpiryDate, QtyReceived, QtyAvailable, StorageLocation)**
- `ItemID, BatchNo → DonationID, LineNo, ReceivedAt, ExpiryDate, QtyReceived, QtyAvailable, StorageLocation` — a batch of an item is uniquely identified by the item plus the batch number and determines everything about that batch.
- `DonationID, LineNo → ItemID, ExpiryDate` — this one is inherited from DONATION_ITEM and is the reason this table isn't in 3NF as originally written (explained below).

**DISTRIBUTES(VisitID, ItemID, BatchNo, QtyDistributed)**
- `VisitID, ItemID, BatchNo → QtyDistributed` — for a given visit and a given batch given out during that visit, there is one distributed quantity.

---

## (b) Normalized Schema (3NF / BCNF)

Looking at our FDs, most tables are already fine because the left side of every FD is either the primary key or a UNIQUE key (which is a superkey).

The one problem we noticed is in **INVENTORY_BATCH**. `ExpiryDate` is a non-prime attribute, but it is also determined by `(DonationID, LineNo)` through DONATION_ITEM. Since `(DonationID, LineNo)` is not a superkey of INVENTORY_BATCH, this is a transitive dependency and breaks 3NF (and therefore BCNF too).

To fix it, we drop `ExpiryDate` from INVENTORY_BATCH. It can still be looked up by joining to DONATION_ITEM on `(DonationID, LineNo)`, so no information is lost.

After that fix, here is the final schema:

| Table | Primary Key | Other Attributes | Foreign Keys |
|---|---|---|---|
| DONOR | DonorID | Name, Email (UNIQUE), Phone, DonorType | — |
| CATEGORY | CategoryID | Name (UNIQUE), Description, IsEssential | — |
| USER_ACCOUNT | UserID | Username (UNIQUE), Role, IsActive | — |
| VISITOR | VisitorID | VisitorType, Email | — |
| FOOD_ITEM | ItemID | Name, Unit, ReorderThreshold, IsActive, CategoryID | CategoryID → CATEGORY(CategoryID) |
| DONATION | DonationID | DonatedAt, Notes, DonorID | DonorID → DONOR(DonorID) |
| PANTRY_VISIT | VisitID | CheckInAt, Notes, VisitorID, UserID | VisitorID → VISITOR(VisitorID); UserID → USER_ACCOUNT(UserID) |
| DONATION_ITEM | (DonationID, LineNo) | ItemID, UserID, QtyDonated, ExpiryDate | DonationID → DONATION(DonationID); ItemID → FOOD_ITEM(ItemID); UserID → USER_ACCOUNT(UserID) |
| INVENTORY_BATCH | (ItemID, BatchNo) | ReceivedAt, QtyReceived, QtyAvailable, StorageLocation, DonationID, LineNo | ItemID → FOOD_ITEM(ItemID); (DonationID, LineNo) → DONATION_ITEM(DonationID, LineNo) |
| DISTRIBUTES | (VisitID, ItemID, BatchNo) | QtyDistributed | VisitID → PANTRY_VISIT(VisitID); (ItemID, BatchNo) → INVENTORY_BATCH(ItemID, BatchNo) |

After dropping the redundant `ExpiryDate` from INVENTORY_BATCH, every non-trivial FD in every table has a superkey on its left side, so the schema is in **BCNF** (and therefore also 3NF).
