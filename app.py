from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, init_db
import os

app = Flask(__name__)
app.secret_key = 'sfu-pantry-secret'


# Bootstrap
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'pantry.db')):
    init_db()


# Home / Dashboard
@app.route('/')
def index():
    db = get_db()

    # Total inventory available
    total_qty = db.execute(
        "SELECT COALESCE(SUM(QtyAvailable),0) AS total FROM INVENTORY_BATCH"
    ).fetchone()['total']

    # Low stock items 
    low_stock = db.execute(
        """
        SELECT f.Name, f.ReorderThreshold, COALESCE(SUM(b.QtyAvailable),0) AS QtyAvailable
        FROM FOOD_ITEM f
        LEFT JOIN INVENTORY_BATCH b ON f.ItemID = b.ItemID
        WHERE f.IsActive = 1
        GROUP BY f.ItemID
        HAVING QtyAvailable < f.ReorderThreshold
        """
    ).fetchall()

    # Items expiring within 30 days
    expiring_soon = db.execute(
        """
        SELECT f.Name, b.ExpiryDate, b.QtyAvailable, b.StorageLocation
        FROM INVENTORY_BATCH b
        JOIN FOOD_ITEM f ON b.ItemID = f.ItemID
        WHERE b.ExpiryDate IS NOT NULL
          AND b.ExpiryDate <= date('now', '+30 days')
          AND b.QtyAvailable > 0
        ORDER BY b.ExpiryDate
        """
    ).fetchall()

    # Recent pantry visits
    recent_visits = db.execute(
        """
        SELECT pv.VisitID, v.VisitorType, pv.CheckInAt, u.Username
        FROM PANTRY_VISIT pv
        JOIN VISITOR v ON pv.VisitorID = v.VisitorID
        JOIN USER_ACCOUNT u ON pv.UserID = u.UserID
        ORDER BY pv.CheckInAt DESC
        LIMIT 5
        """
    ).fetchall()

    # Total donations
    total_donations = db.execute(
        "SELECT COUNT(*) AS cnt FROM DONATION"
    ).fetchone()['cnt']

    db.close()
    return render_template(
        'index.html',
        total_qty=total_qty,
        low_stock=low_stock,
        expiring_soon=expiring_soon,
        recent_visits=recent_visits,
        total_donations=total_donations
    )


# Inventory
@app.route('/inventory')
def inventory():
    db = get_db()
    batches = db.execute(
        """
        SELECT b.ItemID, b.BatchNo, f.Name AS FoodName, f.Unit,
               b.QtyReceived, b.QtyAvailable, b.ExpiryDate,
               b.StorageLocation, b.ReceivedAt
        FROM INVENTORY_BATCH b
        JOIN FOOD_ITEM f ON b.ItemID = f.ItemID
        ORDER BY b.ExpiryDate ASC
        """
    ).fetchall()
    db.close()
    return render_template('inventory.html', batches=batches)


@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    db = get_db()
    if request.method == 'POST':
        item_id      = request.form['item_id']
        donation_id  = request.form['donation_id']
        line_no      = request.form['line_no']
        received_at  = request.form['received_at']
        expiry_date  = request.form['expiry_date'] or None
        qty_received = int(request.form['qty_received'])
        storage_loc  = request.form['storage_location']

        # Auto-assign next BatchNo for this item
        row = db.execute(
            "SELECT COALESCE(MAX(BatchNo),0)+1 AS next FROM INVENTORY_BATCH WHERE ItemID=?",
            (item_id,)
        ).fetchone()
        batch_no = row['next']

        db.execute(
            """
            INSERT INTO INVENTORY_BATCH
              (ItemID, BatchNo, DonationID, LineNo, ReceivedAt, ExpiryDate,
               QtyReceived, QtyAvailable, StorageLocation)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (item_id, batch_no, donation_id, line_no, received_at,
             expiry_date, qty_received, qty_received, storage_loc)
        )
        db.commit()
        db.close()
        flash('Inventory batch added successfully.', 'success')
        return redirect(url_for('inventory'))

    food_items     = db.execute("SELECT ItemID, Name FROM FOOD_ITEM WHERE IsActive=1").fetchall()
    donation_items = db.execute(
        "SELECT DonationID, LineNo FROM DONATION_ITEM ORDER BY DonationID, LineNo"
    ).fetchall()
    db.close()
    return render_template('add_inventory.html',
                           food_items=food_items,
                           donation_items=donation_items)


# Donations
@app.route('/donations')
def donations():
    db = get_db()
    rows = db.execute(
        """
        SELECT d.DonationID, dr.Name AS DonorName, dr.DonorType,
               d.DonatedAt, d.Notes,
               COUNT(di.LineNo) AS LineCount,
               COALESCE(SUM(di.QtyDonated),0) AS TotalQty
        FROM DONATION d
        JOIN DONOR dr ON d.DonorID = dr.DonorID
        LEFT JOIN DONATION_ITEM di ON d.DonationID = di.DonationID
        GROUP BY d.DonationID
        ORDER BY d.DonatedAt DESC
        """
    ).fetchall()
    db.close()
    return render_template('donations.html', donations=rows)


@app.route('/donations/add', methods=['GET', 'POST'])
def add_donation():
    db = get_db()
    if request.method == 'POST':
        donor_id   = request.form['donor_id']
        donated_at = request.form['donated_at']
        notes      = request.form['notes']

        row = db.execute(
            "SELECT COALESCE(MAX(DonationID),0)+1 AS next FROM DONATION"
        ).fetchone()
        donation_id = row['next']

        db.execute(
            "INSERT INTO DONATION (DonationID, DonorID, DonatedAt, Notes) VALUES (?,?,?,?)",
            (donation_id, donor_id, donated_at, notes)
        )
        db.commit()
        db.close()
        flash('Donation recorded successfully.', 'success')
        return redirect(url_for('donations'))

    donors = db.execute("SELECT DonorID, Name FROM DONOR").fetchall()
    db.close()
    return render_template('add_donation.html', donors=donors)


# Donors
@app.route('/donors')
def donors():
    db = get_db()
    rows = db.execute("SELECT * FROM DONOR ORDER BY Name").fetchall()
    db.close()
    return render_template('donors.html', donors=rows)


@app.route('/donors/add', methods=['GET', 'POST'])
def add_donor():
    db = get_db()
    if request.method == 'POST':
        name       = request.form['name']
        email      = request.form['email'] or None
        phone      = request.form['phone']
        donor_type = request.form['donor_type']

        row = db.execute(
            "SELECT COALESCE(MAX(DonorID),0)+1 AS next FROM DONOR"
        ).fetchone()
        donor_id = row['next']

        db.execute(
            "INSERT INTO DONOR (DonorID, Name, Email, Phone, DonorType) VALUES (?,?,?,?,?)",
            (donor_id, name, email, phone, donor_type)
        )
        db.commit()
        db.close()
        flash('Donor registered successfully.', 'success')
        return redirect(url_for('donors'))

    db.close()
    return render_template('add_donor.html')


# Visitors
@app.route('/visitors')
def visitors():
    db = get_db()
    rows = db.execute("SELECT * FROM VISITOR ORDER BY VisitorID").fetchall()
    db.close()
    return render_template('visitors.html', visitors=rows)


@app.route('/visitors/add', methods=['GET', 'POST'])
def add_visitor():
    db = get_db()
    if request.method == 'POST':
        visitor_type = request.form['visitor_type']
        email        = request.form['email'] or None

        row = db.execute(
            "SELECT COALESCE(MAX(VisitorID),0)+1 AS next FROM VISITOR"
        ).fetchone()
        visitor_id = row['next']

        db.execute(
            "INSERT INTO VISITOR (VisitorID, VisitorType, Email) VALUES (?,?,?)",
            (visitor_id, visitor_type, email)
        )
        db.commit()
        db.close()
        flash('Visitor registered successfully.', 'success')
        return redirect(url_for('visitors'))

    db.close()
    return render_template('add_visitor.html')


# Pantry Visits
@app.route('/visits')
def visits():
    db = get_db()
    rows = db.execute(
        """
        SELECT pv.VisitID, v.VisitorType, v.Email AS VisitorEmail,
               pv.CheckInAt, u.Username, pv.Notes
        FROM PANTRY_VISIT pv
        JOIN VISITOR v ON pv.VisitorID = v.VisitorID
        JOIN USER_ACCOUNT u ON pv.UserID = u.UserID
        ORDER BY pv.CheckInAt DESC
        """
    ).fetchall()
    db.close()
    return render_template('visits.html', visits=rows)


@app.route('/visits/add', methods=['GET', 'POST'])
def add_visit():
    db = get_db()
    if request.method == 'POST':
        visitor_id  = request.form['visitor_id']
        user_id     = request.form['user_id']
        check_in_at = request.form['check_in_at']
        notes       = request.form['notes']

        row = db.execute(
            "SELECT COALESCE(MAX(VisitID),0)+1 AS next FROM PANTRY_VISIT"
        ).fetchone()
        visit_id = row['next']

        db.execute(
            "INSERT INTO PANTRY_VISIT (VisitID, VisitorID, UserID, CheckInAt, Notes) VALUES (?,?,?,?,?)",
            (visit_id, visitor_id, user_id, check_in_at, notes)
        )
        db.commit()
        db.close()
        flash('Pantry visit logged successfully.', 'success')
        return redirect(url_for('visits'))

    visitors     = db.execute("SELECT VisitorID, VisitorType, Email FROM VISITOR").fetchall()
    user_accounts = db.execute("SELECT UserID, Username FROM USER_ACCOUNT WHERE IsActive=1").fetchall()
    db.close()
    return render_template('add_visit.html', visitors=visitors, user_accounts=user_accounts)


# Distributions  
@app.route('/distributions')
def distributions():
    db = get_db()
    rows = db.execute(
        """
        SELECT v.VisitorID, f.Name AS FoodItem, d.QtyDistributed
        FROM DISTRIBUTES d
        JOIN PANTRY_VISIT p ON d.VisitID = p.VisitID
        JOIN VISITOR v      ON p.VisitorID = v.VisitorID
        JOIN FOOD_ITEM f    ON d.ItemID = f.ItemID
        ORDER BY p.CheckInAt DESC
        """
    ).fetchall()
    db.close()
    return render_template('distributions.html', distributions=rows)


@app.route('/distributions/add', methods=['GET', 'POST'])
def add_distribution():
    db = get_db()
    if request.method == 'POST':
        visit_id       = request.form['visit_id']
        item_id        = request.form['item_id']
        batch_no       = request.form['batch_no']
        qty_distributed = int(request.form['qty_distributed'])

        # Deduct from inventory
        db.execute(
            """
            UPDATE INVENTORY_BATCH
            SET QtyAvailable = QtyAvailable - ?
            WHERE ItemID=? AND BatchNo=?
            """,
            (qty_distributed, item_id, batch_no)
        )
        db.execute(
            """
            INSERT INTO DISTRIBUTES (VisitID, ItemID, BatchNo, QtyDistributed)
            VALUES (?,?,?,?)
            """,
            (visit_id, item_id, batch_no, qty_distributed)
        )
        db.commit()
        db.close()
        flash('Distribution recorded and inventory updated.', 'success')
        return redirect(url_for('distributions'))

    visits  = db.execute(
        "SELECT VisitID FROM PANTRY_VISIT ORDER BY CheckInAt DESC"
    ).fetchall()
    batches = db.execute(
        """
        SELECT b.ItemID, b.BatchNo, f.Name, b.QtyAvailable
        FROM INVENTORY_BATCH b
        JOIN FOOD_ITEM f ON b.ItemID = f.ItemID
        WHERE b.QtyAvailable > 0
        """
    ).fetchall()
    db.close()
    return render_template('add_distribution.html', visits=visits, batches=batches)


# Food Items
@app.route('/food-items')
def food_items():
    db = get_db()
    rows = db.execute(
        """
        SELECT f.ItemID, f.Name, c.Name AS Category, f.Unit,
               f.ReorderThreshold, f.IsActive,
               COALESCE(SUM(b.QtyAvailable),0) AS TotalAvailable
        FROM FOOD_ITEM f
        JOIN CATEGORY c ON f.CategoryID = c.CategoryID
        LEFT JOIN INVENTORY_BATCH b ON f.ItemID = b.ItemID
        GROUP BY f.ItemID
        ORDER BY f.Name
        """
    ).fetchall()
    db.close()
    return render_template('food_items.html', food_items=rows)


@app.route('/reports')
def reports():
    db = get_db()

    donations_per_donor = db.execute(
        """
        SELECT dr.Name, COUNT(d.DonationID) AS TotalDonations,
               COALESCE(SUM(di.QtyDonated), 0) AS TotalQtyDonated
        FROM DONOR dr
        LEFT JOIN DONATION d ON dr.DonorID = d.DonorID
        LEFT JOIN DONATION_ITEM di ON d.DonationID = di.DonationID
        GROUP BY dr.DonorID
        ORDER BY TotalQtyDonated DESC
        """
    ).fetchall()

    distributed_per_item = db.execute(
        """
        SELECT f.Name, SUM(d.QtyDistributed) AS TotalDistributed,
               AVG(d.QtyDistributed) AS AvgPerVisit,
               MAX(d.QtyDistributed) AS MaxSingleVisit
        FROM DISTRIBUTES d
        JOIN FOOD_ITEM f ON d.ItemID = f.ItemID
        GROUP BY d.ItemID
        ORDER BY TotalDistributed DESC
        """
    ).fetchall()

    all_items_visitors = db.execute(
        """
        SELECT v.VisitorID, v.VisitorType, v.Email
        FROM VISITOR v
        WHERE NOT EXISTS (
            SELECT f.ItemID FROM FOOD_ITEM f
            WHERE NOT EXISTS (
                SELECT 1 FROM DISTRIBUTES d
                JOIN PANTRY_VISIT pv ON d.VisitID = pv.VisitID
                WHERE pv.VisitorID = v.VisitorID AND d.ItemID = f.ItemID
            )
        )
        """
    ).fetchall()

    above_avg_donations = db.execute(
        """
        SELECT f.Name, COALESCE(SUM(di.QtyDonated), 0) AS TotalDonated
        FROM FOOD_ITEM f
        LEFT JOIN DONATION_ITEM di ON f.ItemID = di.ItemID
        GROUP BY f.ItemID
        HAVING TotalDonated > (
            SELECT AVG(sub.total) FROM (
                SELECT COALESCE(SUM(QtyDonated), 0) AS total
                FROM DONATION_ITEM
                GROUP BY ItemID
            ) sub
        )
        """
    ).fetchall()

    db.close()
    return render_template('reports.html',
        donations_per_donor=donations_per_donor,
        distributed_per_item=distributed_per_item,
        all_items_visitors=all_items_visitors,
        above_avg_donations=above_avg_donations
    )

@app.route('/donations/delete/<int:donation_id>', methods=['POST'])
def delete_donation(donation_id):
    db = get_db()
    db.execute("DELETE FROM DONATION WHERE DonationID = ?", (donation_id,))
    db.commit()
    db.close()
    flash('Donation deleted (cascade removed related items).', 'success')
    return redirect(url_for('donations'))


@app.route('/inventory/update/<int:item_id>/<int:batch_no>', methods=['GET', 'POST'])
def update_inventory(item_id, batch_no):
    db = get_db()
    if request.method == 'POST':
        new_location = request.form['storage_location']
        db.execute(
            "UPDATE INVENTORY_BATCH SET StorageLocation = ? WHERE ItemID = ? AND BatchNo = ?",
            (new_location, item_id, batch_no)
        )
        db.commit()
        db.close()
        flash('Storage location updated.', 'success')
        return redirect(url_for('inventory'))

    batch = db.execute(
        """
        SELECT b.*, f.Name AS FoodName FROM INVENTORY_BATCH b
        JOIN FOOD_ITEM f ON b.ItemID = f.ItemID
        WHERE b.ItemID = ? AND b.BatchNo = ?
        """,
        (item_id, batch_no)
    ).fetchone()
    db.close()
    return render_template('update_inventory.html', batch=batch)
# Run
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
