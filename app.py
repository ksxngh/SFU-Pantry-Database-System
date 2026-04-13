"""
SFU Food Pantry Management System - Flask Application
A user-friendly web interface for managing pantry operations
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import pyodbc
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Disable caching for all routes
@app.after_request
def add_no_cache_headers(response):
    """Prevent caching of all responses to ensure fresh data"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Register context processors to make functions available in templates
@app.context_processor
def inject_now():
    """Inject datetime and timedelta into template context"""
    return {
        'datetime': datetime,
        'timedelta': timedelta
    }

# Database Configuration
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'cypress.csil.sfu.ca',
    'database': 'psa167354',
    'uid': 's_psa167',
    'pwd': 'j3Tf67A7Ye3TNMej',
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['uid']};"
            f"PWD={DB_CONFIG['pwd']};"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        return None

# ==================== UTILITY FUNCTIONS ====================

def execute_query(query, params=None):
    """Execute a SELECT query and return results"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except pyodbc.Error as e:
        print(f"Query error: {e}")
        return []
    finally:
        conn.close()

def execute_update(query, params=None):
    """Execute INSERT/UPDATE/DELETE query"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Update error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Dashboard - Overview of pantry operations"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('index.html', stats={})
    
    try:
        cursor = conn.cursor()
        
        # Get key statistics
        cursor.execute("SELECT COUNT(*) FROM INVENTORY_BATCH WHERE QtyAvailable > 0")
        total_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM PANTRY_VISIT WHERE CAST(CheckInAt AS DATE) = CAST(GETDATE() AS DATE)")
        today_visits = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(QtyAvailable) FROM INVENTORY_BATCH")
        total_qty = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT COUNT(*) FROM INVENTORY_BATCH 
            WHERE ExpiryDate IS NOT NULL AND ExpiryDate <= DATEADD(day, 7, CAST(GETDATE() AS DATE))
            AND QtyAvailable > 0
        """)
        expiring_soon = cursor.fetchone()[0]
        
        stats = {
            'total_items': total_items,
            'today_visits': today_visits,
            'total_qty': total_qty,
            'expiring_soon': expiring_soon
        }
        
        return render_template('index.html', stats=stats)
    except pyodbc.Error as e:
        print(f"Dashboard error: {e}")
        return render_template('index.html', stats={})
    finally:
        conn.close()

@app.route('/inventory')
def inventory():
    """View and manage inventory"""
    try:
        query = """
            SELECT 
                ib.ItemID,
                ib.BatchNo,
                fi.Name as ItemName,
                c.Name as Category,
                ib.QtyAvailable,
                ib.QtyReceived,
                ib.ExpiryDate,
                ib.StorageLocation,
                ib.ReceivedAt
            FROM INVENTORY_BATCH ib
            JOIN FOOD_ITEM fi ON ib.ItemID = fi.ItemID
            JOIN CATEGORY c ON fi.CategoryID = c.CategoryID
            ORDER BY fi.Name, ib.BatchNo
        """
        items = execute_query(query)
        
        # Check for low stock items
        low_stock_query = """
            SELECT 
                fi.ItemID,
                fi.Name,
                fi.ReorderThreshold,
                SUM(ib.QtyAvailable) as TotalQty
            FROM FOOD_ITEM fi
            LEFT JOIN INVENTORY_BATCH ib ON fi.ItemID = ib.ItemID
            WHERE fi.IsActive = 1
            GROUP BY fi.ItemID, fi.Name, fi.ReorderThreshold
            HAVING SUM(ib.QtyAvailable) < fi.ReorderThreshold OR SUM(ib.QtyAvailable) IS NULL
            ORDER BY fi.Name
        """
        low_stock = execute_query(low_stock_query)
        
        return render_template('inventory.html', items=items, low_stock=low_stock)
    except Exception as e:
        print(f"Inventory error: {e}")
        flash('Error loading inventory', 'error')
        return redirect(url_for('index'))

@app.route('/donations')
def donations():
    """View and manage donations"""
    try:
        query = """
            SELECT 
                d.DonationID,
                d.DonorID,
                do.Name as DonorName,
                do.DonorType,
                d.DonatedAt,
                d.Notes,
                COUNT(DISTINCT di.[LineNo]) as ItemCount
            FROM DONATION d
            LEFT JOIN DONOR do ON d.DonorID = do.DonorID
            LEFT JOIN DONATION_ITEM di ON d.DonationID = di.DonationID
            GROUP BY 
                d.DonationID, d.DonorID, do.Name, do.DonorType, d.DonatedAt, d.Notes
            ORDER BY d.DonatedAt DESC
        """
        donations_list = execute_query(query)
        
        # Get list of donors for new donation form
        donor_query = "SELECT DonorID, Name FROM DONOR ORDER BY Name"
        donors = execute_query(donor_query)
        
        # Get list of food items for donation items form
        item_query = "SELECT ItemID, Name FROM FOOD_ITEM WHERE IsActive = 1 ORDER BY Name"
        items = execute_query(item_query)
        
        # Get list of categories for new item form
        category_query = "SELECT CategoryID, Name FROM CATEGORY ORDER BY Name"
        categories = execute_query(category_query)
        
        return render_template('donations.html', 
                             donations=donations_list, 
                             donors=donors, 
                             items=items,
                             categories=categories)
    except Exception as e:
        print(f"Donations error: {e}")
        flash('Error loading donations', 'error')
        return redirect(url_for('index'))

@app.route('/api/donation/<int:donation_id>')
def get_donation_details(donation_id):
    """Get donation items details via AJAX"""
    try:
        query = """
            SELECT 
                di.[LineNo],
                fi.Name as ItemName,
                di.QtyDonated,
                di.ExpiryDate,
                ua.Username as RecordedBy
            FROM DONATION_ITEM di
            JOIN FOOD_ITEM fi ON di.ItemID = fi.ItemID
            JOIN USER_ACCOUNT ua ON di.UserID = ua.UserID
            WHERE di.DonationID = ?
            ORDER BY di.[LineNo]
        """
        items = execute_query(query, (donation_id,))
        # Convert pyodbc rows to list of dicts
        result = []
        for item in items:
            result.append({
                'LineNo': item[0],
                'ItemName': item[1],
                'QtyDonated': item[2],
                'ExpiryDate': str(item[3]) if item[3] else None,
                'RecordedBy': item[4]
            })
        return jsonify(result)
    except Exception as e:
        print(f"Get donation details error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_donation', methods=['POST'])
def add_donation():
    """Add a new donation"""
    conn = None
    try:
        donor_id = request.form.get('donor_id')
        notes = request.form.get('notes', '')
        
        # Validate inputs
        if not donor_id:
            flash('Donor ID is required', 'error')
            return redirect(url_for('donations'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get a valid UserID from the database, or use NULL if none exist
        cursor.execute("SELECT TOP 1 UserID FROM USER_ACCOUNT WHERE IsActive = 1")
        user_row = cursor.fetchone()
        user_id = user_row[0] if user_row else None
        
        # Get next DonationID
        cursor.execute("SELECT ISNULL(MAX(DonationID), 0) + 1 FROM DONATION")
        row = cursor.fetchone()
        donation_id = row[0] if row else 1
        
        # Insert donation with explicit ID
        donation_query = """
            INSERT INTO DONATION (DonationID, DonorID, DonatedAt, Notes)
            VALUES (?, ?, GETDATE(), ?)
        """
        cursor.execute(donation_query, (donation_id, donor_id, notes))
        
        # Add donation items
        donation_items = request.form.getlist('items[]')
        donation_qty = request.form.getlist('quantities[]')
        donation_expiry = request.form.getlist('expiry_dates[]')
        donation_storage = request.form.getlist('storage_locations[]')
        
        for i, item_id in enumerate(donation_items):
            if not item_id:
                continue
            try:
                qty = int(donation_qty[i]) if i < len(donation_qty) and donation_qty[i] else 0
            except (ValueError, IndexError):
                continue
            if qty <= 0:
                continue
            
            # Add donation item
            di_query = """
                INSERT INTO DONATION_ITEM (DonationID, [LineNo], ItemID, UserID, QtyDonated, ExpiryDate)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(di_query, (
                donation_id,
                i + 1,
                item_id,
                user_id,
                qty,
                donation_expiry[i] if i < len(donation_expiry) and donation_expiry[i] else None
            ))
            
            # Get storage location or use None
            storage_loc = donation_storage[i] if i < len(donation_storage) and donation_storage[i] else None
            
            # Update inventory batch
            ib_query = """
                INSERT INTO INVENTORY_BATCH 
                (ItemID, BatchNo, DonationID, [LineNo], ReceivedAt, ExpiryDate, QtyReceived, QtyAvailable, StorageLocation)
                VALUES (?, (SELECT ISNULL(MAX(BatchNo), 0) + 1 FROM INVENTORY_BATCH WHERE ItemID = ?), 
                        ?, ?, GETDATE(), ?, ?, ?, ?)
            """
            cursor.execute(ib_query, (
                item_id, item_id, donation_id, i + 1,
                donation_expiry[i] if i < len(donation_expiry) and donation_expiry[i] else None,
                qty,
                qty,
                storage_loc
            ))
        
        conn.commit()
        flash('Donation recorded successfully!', 'success')
        return redirect(url_for('donations'))
    except pyodbc.Error as e:
        print(f"Add donation error: {e}")
        if conn:
            conn.rollback()
        flash('Database error recording donation', 'error')
        return redirect(url_for('donations'))
    except Exception as e:
        print(f"Add donation error: {e}")
        flash('Error adding donation', 'error')
        return redirect(url_for('donations'))
    finally:
        if conn:
            conn.close()

@app.route('/api/add_donor', methods=['POST'])
def add_donor():
    """Add a new donor via AJAX"""
    try:
        name = request.form.get('name')
        donor_type = request.form.get('donor_type')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        
        if not name or not donor_type:
            return jsonify({'success': False, 'message': 'Name and type are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get next DonorID
        cursor.execute("SELECT ISNULL(MAX(DonorID), 0) + 1 FROM DONOR")
        row = cursor.fetchone()
        donor_id = row[0] if row else 1
        
        # Insert donor with explicit ID
        donor_query = """
            INSERT INTO DONOR (DonorID, Name, DonorType, Email, Phone)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(donor_query, (donor_id, name, donor_type, email if email else None, phone if phone else None))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'donor_id': donor_id, 'name': name})
            
    except Exception as e:
        print(f"Add donor error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/add_food_item', methods=['POST'])
def add_food_item():
    """Add a new food item via AJAX"""
    try:
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        reorder_threshold = request.form.get('reorder_threshold', '10')
        
        if not name or not category_id:
            return jsonify({'success': False, 'message': 'Name and category are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        # Check if item already exists
        check_query = "SELECT ItemID FROM FOOD_ITEM WHERE Name = ?"
        cursor.execute(check_query, (name,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': 'Food item already exists'}), 400
        
        # Get next ItemID
        cursor.execute("SELECT ISNULL(MAX(ItemID), 0) + 1 FROM FOOD_ITEM")
        row = cursor.fetchone()
        item_id = row[0] if row else 1
        
        # Insert food item with explicit ID
        item_query = """
            INSERT INTO FOOD_ITEM (ItemID, CategoryID, Name, ReorderThreshold, IsActive)
            VALUES (?, ?, ?, ?, 1)
        """
        try:
            cursor.execute(item_query, (item_id, int(category_id), name, int(reorder_threshold)))
            conn.commit()
        except Exception as e:
            conn.close()
            print(f"Insert error: {e}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        
        conn.close()
        
        return jsonify({'success': True, 'item_id': item_id, 'name': name})
            
    except Exception as e:
        print(f"Add food item error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/add_category', methods=['POST'])
def add_category():
    """Add a new category via AJAX"""
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        is_essential = request.form.get('is_essential', 0)
        
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        # Check if category already exists
        check_query = "SELECT CategoryID FROM CATEGORY WHERE Name = ?"
        cursor.execute(check_query, (name,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': 'Category already exists'}), 400
        
        # Get next CategoryID
        cursor.execute("SELECT ISNULL(MAX(CategoryID), 0) + 1 FROM CATEGORY")
        row = cursor.fetchone()
        category_id = row[0] if row else 1
        
        # Insert category with explicit ID
        category_query = """
            INSERT INTO CATEGORY (CategoryID, Name, Description, IsEssential)
            VALUES (?, ?, ?, ?)
        """
        try:
            cursor.execute(category_query, (category_id, name, description if description else None, int(is_essential)))
            conn.commit()
        except Exception as e:
            conn.close()
            print(f"Insert error: {e}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        
        conn.close()
        
        return jsonify({'success': True, 'category_id': category_id, 'name': name})
            
    except Exception as e:
        print(f"Add category error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/add_staff', methods=['POST'])
def add_staff():
    """Add a new staff member via AJAX"""
    try:
        username = request.form.get('username')
        role = request.form.get('role')
        
        if not username or not role:
            return jsonify({'success': False, 'message': 'Username and role are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        # Check if username already exists
        check_query = "SELECT UserID FROM USER_ACCOUNT WHERE Username = ?"
        cursor.execute(check_query, (username,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Get next UserID
        cursor.execute("SELECT ISNULL(MAX(UserID), 0) + 1 FROM USER_ACCOUNT")
        row = cursor.fetchone()
        user_id = row[0] if row else 1
        
        # Insert staff member with explicit ID and IsActive = 1
        staff_query = """
            INSERT INTO USER_ACCOUNT (UserID, Username, Role, IsActive)
            VALUES (?, ?, ?, 1)
        """
        try:
            cursor.execute(staff_query, (user_id, username, role))
            conn.commit()
        except Exception as e:
            conn.close()
            print(f"Insert error: {e}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        
        conn.close()
        
        return jsonify({'success': True, 'user_id': user_id, 'username': username})
            
    except Exception as e:
        print(f"Add staff error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/visits')
def visits():
    """View and manage pantry visits"""
    try:
        query = """
            SELECT 
                pv.VisitID,
                pv.VisitorID,
                v.VisitorType,
                v.Email,
                pv.CheckInAt,
                ua.Username as StaffName,
                pv.Notes,
                COUNT(DISTINCT d.ItemID) as ItemsReceived
            FROM PANTRY_VISIT pv
            LEFT JOIN VISITOR v ON pv.VisitorID = v.VisitorID
            LEFT JOIN USER_ACCOUNT ua ON pv.UserID = ua.UserID
            LEFT JOIN DISTRIBUTES d ON pv.VisitID = d.VisitID
            GROUP BY 
                pv.VisitID, pv.VisitorID, v.VisitorType, v.Email, pv.CheckInAt, 
                ua.Username, pv.Notes
            ORDER BY pv.CheckInAt DESC
        """
        visits_list = execute_query(query)
        
        # Get staff list
        staff_query = "SELECT UserID, Username FROM USER_ACCOUNT WHERE IsActive = 1"
        staff = execute_query(staff_query)
        
        return render_template('visits.html', 
                             visits=visits_list,
                             staff=staff)
    except Exception as e:
        print(f"Visits error: {e}")
        flash('Error loading visits', 'error')
        return redirect(url_for('index'))

@app.route('/api/add_visit', methods=['POST'])
def add_visit():
    """Add a new pantry visit"""
    conn = None
    try:
        visitor_type = request.form.get('visitor_type')
        visitor_email = request.form.get('visitor_email', '')
        staff_id = request.form.get('staff_id')
        notes = request.form.get('notes', '')
        
        # Validate inputs
        if not visitor_type or not staff_id:
            flash('Visitor type and staff ID are required', 'error')
            return redirect(url_for('visits'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get next VisitorID
        cursor.execute("SELECT ISNULL(MAX(VisitorID), 0) + 1 FROM VISITOR")
        row = cursor.fetchone()
        visitor_id = row[0] if row else 1
        
        # Add visitor with explicit ID
        visitor_query = """
            INSERT INTO VISITOR (VisitorID, VisitorType, Email) 
            VALUES (?, ?, ?)
        """
        cursor.execute(visitor_query, (visitor_id, visitor_type, visitor_email if visitor_email else None))
        conn.commit()
        
        # Get next VisitID
        cursor.execute("SELECT ISNULL(MAX(VisitID), 0) + 1 FROM PANTRY_VISIT")
        row = cursor.fetchone()
        visit_id = row[0] if row else 1
        
        # Add visit with explicit ID
        visit_query = """
            INSERT INTO PANTRY_VISIT (VisitID, VisitorID, UserID, CheckInAt, Notes)
            VALUES (?, ?, ?, GETDATE(), ?)
        """
        cursor.execute(visit_query, (visit_id, visitor_id, staff_id, notes))
        
        conn.commit()
        
        flash('Visit recorded successfully!', 'success')
        return redirect(url_for('visits'))
    except pyodbc.Error as e:
        print(f"Add visit error: {e}")
        if conn:
            conn.rollback()
        flash('Database error recording visit', 'error')
        return redirect(url_for('visits'))
    except Exception as e:
        print(f"Add visit error: {e}")
        flash('Error recording visit', 'error')
        return redirect(url_for('visits'))
    finally:
        if conn:
            conn.close()

@app.route('/distribution')
def distribution():
    """Manage food distribution"""
    try:
        # Get recent distributions
        query = """
            SELECT 
                d.VisitID,
                v.VisitorType,
                v.Email,
                d.ItemID,
                fi.Name as ItemName,
                d.BatchNo,
                d.QtyDistributed,
                pv.CheckInAt
            FROM DISTRIBUTES d
            JOIN PANTRY_VISIT pv ON d.VisitID = pv.VisitID
            JOIN VISITOR v ON pv.VisitorID = v.VisitorID
            JOIN FOOD_ITEM fi ON d.ItemID = fi.ItemID
            ORDER BY pv.CheckInAt DESC
        """
        dist_rows = execute_query(query)
        
        # Convert pyodbc rows to dictionaries for template access
        distributions = []
        for row in dist_rows:
            distributions.append({
                'VisitID': row[0],
                'VisitorType': row[1],
                'Email': row[2],
                'ItemID': row[3],
                'ItemName': row[4],
                'BatchNo': row[5],
                'QtyDistributed': row[6],
                'CheckInAt': row[7]
            })
        
        # Get available inventory - group by ItemID
        inventory_query = """
            SELECT 
                ib.ItemID,
                ib.BatchNo,
                fi.Name,
                ib.QtyAvailable,
                ib.ExpiryDate
            FROM INVENTORY_BATCH ib
            JOIN FOOD_ITEM fi ON ib.ItemID = fi.ItemID
            WHERE ib.QtyAvailable > 0
            ORDER BY fi.Name, ib.BatchNo
        """
        inventory_rows = execute_query(inventory_query)
        
        # Convert inventory rows to dictionaries for template
        inventory = []
        for row in inventory_rows:
            inventory.append({
                'ItemID': row[0],
                'BatchNo': row[1],
                'Name': row[2],
                'QtyAvailable': row[3],
                'ExpiryDate': row[4]
            })
        
        # Create a grouped inventory structure for the form
        inventory_by_item = {}
        for item in inventory:
            item_id = item['ItemID']
            if item_id not in inventory_by_item:
                inventory_by_item[item_id] = {
                    'name': item['Name'],
                    'batches': []
                }
            inventory_by_item[item_id]['batches'].append({
                'batch_no': item['BatchNo'],
                'qty_available': item['QtyAvailable'],
                'expiry_date': item['ExpiryDate']
            })
        
        # Get recent visits
        visits_query = """
            SELECT TOP 10
                pv.VisitID,
                v.VisitorType,
                v.Email,
                pv.CheckInAt
            FROM PANTRY_VISIT pv
            JOIN VISITOR v ON pv.VisitorID = v.VisitorID
            ORDER BY pv.CheckInAt DESC
        """
        recent_visits = execute_query(visits_query)
        
        return render_template('distribution.html',
                             distributions=distributions,
                             inventory=inventory,
                             inventory_by_item=inventory_by_item,
                             recent_visits=recent_visits)
    except Exception as e:
        print(f"Distribution error: {e}")
        flash('Error loading distribution', 'error')
        return redirect(url_for('index'))

@app.route('/api/add_distribution', methods=['POST'])
def add_distribution():
    """Add distributed items"""
    conn = None
    try:
        visit_id = request.form.get('visit_id')
        items = request.form.getlist('items[]')
        batches = request.form.getlist('batches[]')
        quantities = request.form.getlist('quantities[]')
        
        # Validate inputs
        if not visit_id or not items:
            flash('Visit ID and items are required', 'error')
            return redirect(url_for('distribution'))
        
        # Filter out empty items - validate all required fields
        valid_items = []
        for i, item_id in enumerate(items):
            # Skip if no item selected
            if not item_id or not str(item_id).strip():
                continue
            
            batch_no = batches[i] if i < len(batches) else ''
            qty_str = quantities[i] if i < len(quantities) else ''
            
            # Skip if batch not selected
            if not batch_no or not str(batch_no).strip():
                continue
            
            # Skip if quantity not entered or invalid
            try:
                qty = int(qty_str) if qty_str else 0
                if qty <= 0:
                    continue
            except (ValueError, TypeError):
                continue
            
            valid_items.append({
                'item_id': str(item_id).strip(),
                'batch': str(batch_no).strip(),
                'qty': qty
            })
        
        if not valid_items:
            flash('Please select at least one item with a batch and quantity to distribute', 'error')
            return redirect(url_for('distribution'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        items_added = 0
        for item_data in valid_items:
            item_id = item_data['item_id']
            batch_no = item_data['batch']
            qty = item_data['qty']
            
            # Check if this distribution already exists
            check_query = """
                SELECT COUNT(*) FROM DISTRIBUTES 
                WHERE VisitID = ? AND ItemID = ? AND BatchNo = ?
            """
            cursor.execute(check_query, (visit_id, item_id, batch_no))
            existing = cursor.fetchone()
            if existing and existing[0] > 0:
                # Update existing distribution with additional quantity
                update_dist_query = """
                    UPDATE DISTRIBUTES
                    SET QtyDistributed = QtyDistributed + ?
                    WHERE VisitID = ? AND ItemID = ? AND BatchNo = ?
                """
                cursor.execute(update_dist_query, (qty, visit_id, item_id, batch_no))
            else:
                # Add new distribution record
                dist_query = """
                    INSERT INTO DISTRIBUTES (VisitID, ItemID, BatchNo, QtyDistributed)
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(dist_query, (visit_id, item_id, batch_no, qty))
            
            # Update inventory
            update_query = """
                UPDATE INVENTORY_BATCH
                SET QtyAvailable = QtyAvailable - ?
                WHERE ItemID = ? AND BatchNo = ?
            """
            cursor.execute(update_query, (qty, item_id, batch_no))
            items_added += 1
        
        if items_added > 0:
            conn.commit()
            flash(f'Distribution recorded successfully! ({items_added} items distributed)', 'success')
        else:
            conn.rollback()
            flash('No new items to distribute (may have been duplicates of existing distributions)', 'warning')
        
        return redirect(url_for('distribution'))
    except pyodbc.Error as e:
        print(f"Add distribution error: {e}")
        if conn:
            conn.rollback()
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('distribution'))
    except Exception as e:
        print(f"Add distribution error: {e}")
        if conn:
            conn.rollback()
        flash('Error recording distribution', 'error')
        return redirect(url_for('distribution'))
    finally:
        if conn:
            conn.close()

@app.route('/reports')
def reports():
    """View reports and analytics"""
    try:
        # Donation history
        donation_query = """
            SELECT 
                do.DonorType,
                COUNT(*) as DonationCount,
                SUM(di.QtyDonated) as TotalQty
            FROM DONATION d
            JOIN DONOR do ON d.DonorID = do.DonorID
            LEFT JOIN DONATION_ITEM di ON d.DonationID = di.DonationID
            GROUP BY do.DonorType
        """
        donations_by_type = execute_query(donation_query)
        
        # Items expiring soon
        expiry_query = """
            SELECT 
                fi.Name,
                ib.ExpiryDate,
                ib.QtyAvailable,
                ib.StorageLocation
            FROM INVENTORY_BATCH ib
            JOIN FOOD_ITEM fi ON ib.ItemID = fi.ItemID
            WHERE ib.ExpiryDate IS NOT NULL 
                AND ib.ExpiryDate <= DATEADD(day, 30, CAST(GETDATE() AS DATE))
                AND ib.QtyAvailable > 0
            ORDER BY ib.ExpiryDate ASC
        """
        expiring_items = execute_query(expiry_query)
        
        # Visitor statistics
        visitor_query = """
            SELECT 
                CAST(pv.CheckInAt AS DATE) as VisitDate,
                COUNT(*) as VisitorCount
            FROM PANTRY_VISIT pv
            WHERE pv.CheckInAt >= DATEADD(day, -30, GETDATE())
            GROUP BY CAST(pv.CheckInAt AS DATE)
            ORDER BY VisitDate DESC
        """
        visitor_stats = execute_query(visitor_query)
        
        # Top items distributed
        top_items_query = """
            SELECT TOP 10
                fi.Name,
                SUM(d.QtyDistributed) as TotalDistributed
            FROM DISTRIBUTES d
            JOIN FOOD_ITEM fi ON d.ItemID = fi.ItemID
            GROUP BY fi.Name
            ORDER BY TotalDistributed DESC
        """
        top_items = execute_query(top_items_query)
        
        return render_template('reports.html',
                             donations_by_type=donations_by_type,
                             expiring_items=expiring_items,
                             visitor_stats=visitor_stats,
                             top_items=top_items)
    except Exception as e:
        print(f"Reports error: {e}")
        flash('Error loading reports', 'error')
        return redirect(url_for('index'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
