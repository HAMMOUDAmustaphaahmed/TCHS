from datetime import datetime
from flask import session
from functools import wraps

def get_season_codes(year):
    """Generate season codes for a given year"""
    return {
        'normal': f"S{year}",  # Regular season (e.g., S2026)
        'summer': f"E{year}"   # Summer school (e.g., E2026)
    }

def get_active_season_dates(year):
    """Get start and end dates for a season year"""
    return {
        'normal': {
            'start': datetime(year-1, 10, 1),  # Oct 1st previous year
            'end': datetime(year, 9, 30)       # Sept 30th current year (au lieu de juin)
        },
        'summer': {
            'start': datetime(year, 7, 1),     # July 1st
            'end': datetime(year, 8, 31)       # August 31st
        }
    }

def is_valid_season_date(date, season_type, year):
    """Check if a date falls within the specified season"""
    dates = get_active_season_dates(year)
    season_dates = dates.get(season_type)
    if not season_dates:
        return False
    return season_dates['start'].date() <= date <= season_dates['end'].date()

def apply_season_filter(query, model, season_type='all'):
    """Apply season filtering to a database query"""
    if 'saison_code' not in session:
        return query
        
    year = session.get('saison')  # This is now already an integer
    season_type = session.get('saison_type')  # 'S' or 'E'
    
    codes = get_season_codes(year)
    
    if season_type == 'S':
        return query.filter(model.code_saison == codes['normal'])
    elif season_type == 'E':
        return query.filter(model.code_saison == codes['summer'])
    else:  # 'all'
        return query.filter(model.code_saison.in_([codes['normal'], codes['summer']]))


def season_required(f):
    """Decorator to ensure active season is set"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('saison'):
            from flask import flash, redirect, url_for
            flash("Veuillez sélectionner une saison", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class SeasonContext:
    """Context manager for season-specific operations"""
    def __init__(self, model):
        self.model = model
        
    def filter_query(self, query, season_type='all'):
        return apply_season_filter(query, self.model, season_type)
        
    def get_active_codes(self):
        if 'saison' not in session:
            return None
        return get_season_codes(session['saison'])
        
    def is_valid_date(self, date, season_type='normal'):
        if 'saison' not in session:
            return False
        return is_valid_season_date(date, season_type, session['saison'])
# Example usage in routes:
"""
from filter_functions import SeasonContext, season_required

@app.route('/adherents')
@season_required
def list_adherents():
    season = SeasonContext(Adherent)
    query = Adherent.query
    query = season.filter_query(query)
    adherents = query.all()
    return render_template('adherents.html', adherents=adherents)
"""

# Specific filter functions for different models
def filter_adherents(query, season_type='all'):
    """Filter adherents based on active season"""
    return apply_season_filter(query, Adherent, season_type)

def filter_paiements(query, season_type='all'):
    """Filter payments based on active season"""
    return apply_season_filter(query, Paiement, season_type)

def filter_presences(query, season_type='all'):
    """Filter attendance records based on active season"""
    return apply_season_filter(query, Presence, season_type)

def filter_seances(query, season_type='all'):
    """Filter sessions based on active season dates"""
    if not session.get('saison'):
        return query
        
    year = int(session['saison'])
    dates = get_active_season_dates(year)
    
    if season_type == 'normal':
        return query.filter(
            Seance.date.between(
                dates['normal']['start'].date(),
                dates['normal']['end'].date()
            )
        )
    elif season_type == 'summer':
        return query.filter(
            Seance.date.between(
                dates['summer']['start'].date(),
                dates['summer']['end'].date()
            )
        )
    else:  # 'all'
        return query.filter(
            (Seance.date.between(
                dates['normal']['start'].date(),
                dates['normal']['end'].date()
            )) |
            (Seance.date.between(
                dates['summer']['start'].date(),
                dates['summer']['end'].date()
            ))
        )

def generate_season_code(date=None):
    """Generate season code based on date"""
    if date is None:
        date = datetime.now()
    
    year = date.year
    if date.month >= 10:  # October or later
        return f"S{year + 1}"  # Next year's season
    elif date.month >= 7:  # July to September
        return f"E{year}"  # Current year's summer season
    else:  # January to June
        return f"S{year}"  # Current year's season