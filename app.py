from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Read the Excel file
df = pd.read_excel('data/nfldata.xlsx')


@app.route('/')
def home():
    return render_template('query.html')


@app.route('/year/<int:yr>')
def year_info(yr):
    return render_template('year.html', year=yr)


@app.route('/teams')
def teams():
    team_type = request.args.get('type')
    teams_dict = {
        'ARI': {'full_name': 'Arizona Cardinals', 'formerly': None},
        'ATL': {'full_name': 'Atlanta Falcons', 'formerly': None},
        'BAL': {'full_name': 'Baltimore Ravens', 'formerly': None},
        'BUF': {'full_name': 'Buffalo Bills', 'formerly': None},
        'CAR': {'full_name': 'Carolina Panthers', 'formerly': None},
        'CHI': {'full_name': 'Chicago Bears', 'formerly': None},
        'CIN': {'full_name': 'Cincinnati Bengals', 'formerly': None},
        'CLE': {'full_name': 'Cleveland Browns', 'formerly': None},
        'DAL': {'full_name': 'Dallas Cowboys', 'formerly': None},
        'DEN': {'full_name': 'Denver Broncos', 'formerly': None},
        'DET': {'full_name': 'Detroit Lions', 'formerly': None},
        'GB': {'full_name': 'Green Bay Packers', 'formerly': None},
        'HOU': {'full_name': 'Houston Texans', 'formerly': None},
        'IND': {'full_name': 'Indianapolis Colts', 'formerly': None},
        'JAK': {'full_name': 'Jacksonville Jaguars', 'formerly': None},
        'KC': {'full_name': 'Kansas City Chiefs', 'formerly': None},
        'MIA': {'full_name': 'Miami Dolphins', 'formerly': None},
        'MIN': {'full_name': 'Minnesota Vikings', 'formerly': None},
        'NE': {'full_name': 'New England Patriots', 'formerly': None},
        'NO': {'full_name': 'New Orleans Saints', 'formerly': None},
        'NYG': {'full_name': 'New York Giants', 'formerly': None},
        'NYJ': {'full_name': 'New York Jets', 'formerly': None},
        'PHI': {'full_name': 'Philadelphia Eagles', 'formerly': None},
        'PIT': {'full_name': 'Pittsburgh Steelers', 'formerly': None},
        'RAI': {'full_name': 'Las Vegas Raiders', 'formerly': 'OAK - Oakland Raiders'},
        'SD': {'full_name': 'Los Angeles Chargers', 'formerly': 'SD - San Diego Chargers'},
        'SEA': {'full_name': 'Seattle Seahawks', 'formerly': None},
        'SF': {'full_name': 'San Francisco 49ers', 'formerly': None},
        'STL': {'full_name': 'Los Angeles Rams', 'formerly': 'STL - St. Louis Rams'},
        'TB': {'full_name': 'Tampa Bay Buccaneers', 'formerly': None},
        'TEN': {'full_name': 'Tennessee Titans', 'formerly': None},
        'WAS': {'full_name': 'Washington Football Team', 'formerly': 'WAS - Washington Redskins'}
    }

    if team_type == 'home':
        teams = df['Home Team'].unique().tolist()
        teams_with_names = []
        for team in teams:
            full_name = teams_dict.get(team, {}).get('full_name')
            formerly = teams_dict.get(team, {}).get('formerly')
            if formerly:
                teams_with_names.append(f"{team} - {full_name} (formerly known as {formerly})")
            else:
                teams_with_names.append(f"{team} - {full_name}")
    elif team_type == 'year':
        teams_with_names = df['Year'].dropna().unique().tolist()
        teams_with_names = [f'<a href="/year/{year}">{year}</a>' for year in teams_with_names]
    else:
        teams_with_names = []

    teams_html = '<br>'.join(teams_with_names)
    return teams_html


if __name__ == '__main__':
    app.run(debug=True)
