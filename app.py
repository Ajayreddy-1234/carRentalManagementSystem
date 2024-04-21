from flask import Flask, render_template, request
import pymysql


app = Flask(__name__)

# Database connection info
db_host = "carrentalmanagementsystem.cp2we2aaom6h.us-east-2.rds.amazonaws.com"
db_user = "root"
db_password = "carrental.."
db_name = "CarRentalDB"


# Create a connection to the database
def get_db_connection():
    connection = pymysql.connect(host=db_host,
                                 user=db_user,
                                 password=db_password,
                                 db=db_name,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


@app.route('/', methods=['GET', 'POST'])
def index():
    search = ''
    search = request.form.get('search', '')  # The search term from the form
    # Get sort and search parameters from the query string
    sort = request.args.get('sort', 'VehicleID')  # Default sort by VehicleID
    order = request.args.get('order', 'asc')  # Default sort order

    query = """
    SELECT 
        v.VehicleID, 
        v.Make, 
        v.Model, 
        v.Type, 
        v.Year, 
        v.RateDaily, 
        v.NearestAirportCity, 
        l.City as LocationCity,
        l.State as LocationState,
        l.Country as LocationCountry,
        f.FuelType,
        o.OwnerID,
        r.RenterTripsTaken,
        r.ReviewCount,
        r.Rating
    FROM 
        Vehicles v
    LEFT JOIN Locations l ON v.LocationID = l.LocationID
    LEFT JOIN FuelTypes f ON v.FuelTypeID = f.FuelTypeID
    LEFT JOIN Owners o ON v.OwnerID = o.OwnerID
    LEFT JOIN RentalActivity r ON v.VehicleID = r.VehicleID
    """

    numberOfRows = """
    SELECT 
        COUNT(*)
    FROM 
        Vehicles v
    LEFT JOIN Locations l ON v.LocationID = l.LocationID
    LEFT JOIN FuelTypes f ON v.FuelTypeID = f.FuelTypeID
    LEFT JOIN Owners o ON v.OwnerID = o.OwnerID
    LEFT JOIN RentalActivity r ON v.VehicleID = r.VehicleID
    """
    # If there is a search term, add a WHERE clause to the SQL query
    if search:
        query += " WHERE Make LIKE %s OR Model LIKE %s"
        numberOfRows += " WHERE Make LIKE %s OR Model LIKE %s"
        search_pattern = f"%{search}%"
    
    # Add ORDER BY clause to SQL query
    query += f" ORDER BY {sort} {order}"

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page

    # Add limit and offset to your query
    paginated_query = query + " LIMIT %s OFFSET %s"

    # Execute the query with search terms if applicable
    conn = get_db_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute(paginated_query, (search_pattern, search_pattern, per_page, offset))
    else:
        cursor.execute(paginated_query, (per_page, offset))
    vehicles = cursor.fetchall()
    
    if search:
        cursor.execute(numberOfRows, (search_pattern, search_pattern))
    else:
        cursor.execute(numberOfRows)
    count_result = cursor.fetchone()

    # Extract the total count from the result
    total_count = count_result['COUNT(*)'] if count_result else 0

    cursor.close()
    conn.close()

    total_pages = (total_count + per_page - 1) // per_page

    return render_template('index.html', vehicles=vehicles, sort=sort, order=order, search=search, page=page, total_pages=total_pages, per_page=per_page)


if __name__ == "__main__":
    app.run(debug=True)
