from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)


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


@app.route('/querypage', methods=['GET', 'POST'])
def querypage():
    df1 = pd.read_excel('data/nfldata.xlsx')
    years = list(range(1983, 2024))

    if request.method == 'GET':
        return render_template('querypage.html', years=years)

    if request.method == 'POST':
        year = request.form.get('year')
        if year:
            year = int(year)
            game_weeks = df1[df1['Year'] == year]['Game Week #'].unique().tolist()
            return render_template('querypage.html', years=years, selected_year=year, game_weeks=game_weeks)

        game_week = request.form.get('game_week')
        if game_week:
            game_week = int(game_week)
            selected_year = int(request.form.get('selected_year'))
            matches = df1[(df1['Year'] == selected_year) & (df1['Game Week #'] == game_week)]
            matchups = [f"{row['Home Team']} vs {row['Opposing Team']}" for index, row in matches.iterrows()]
            return render_template('querypage.html', years=years, selected_year=selected_year,  selected_game_week=game_week, matchups=matchups)

        selected_matchup = request.form.get('matchup')
        if selected_matchup:
            selected_year = int(request.form.get('selected_year'))
            selected_game_week = int(request.form.get('selected_game_week'))
            home_team, opposing_team = selected_matchup.split(" vs ")

            past_matches = int(request.form.get('past_matches', 4))

            current_matchup = df1[(df1['Home Team'] == home_team) & (df1['Opposing Team'] == opposing_team) & (df1['Year'] == selected_year) & (df1['Game Week #'] == selected_game_week)].iloc[0].to_dict()

            #last 4 games of the home team
            home_team_games = get_last_n_games(df1, home_team, selected_year, selected_game_week, past_matches)

            #last 4 games of the opposing team
            opposing_team_games = get_last_n_games(df1, opposing_team, selected_year, selected_game_week, past_matches)

            return render_template('queryresults.html',
                                   result=f"You selected matchup: {selected_matchup}",
                                   current_matchup=current_matchup,
                                   home_team_games=home_team_games,
                                   opposing_team_games=opposing_team_games,
                                   past_matches=past_matches)

    return render_template('querypage.html', years=years)

def get_last_n_games(df, team, year, game_week, n):
    # Filter the games of the current year up to the selected game week loogic
    current_year_games = df[(df['Home Team'] == team) & (df['Year'] == year) & (df['Game Week #'] < game_week)]
    # If the number of games found is less than required, get the remaining from the previous year logic is below
    if len(current_year_games) < n and year > 1983:
        previous_year_games = df[(df['Home Team'] == team) & (df['Year'] == year - 1)]
        combined_games = pd.concat([previous_year_games, current_year_games])
        combined_games = combined_games.sort_values(by=['Year', 'Game Week #'], ascending=False)
        return combined_games.head(n).to_dict(orient='records')
    else:
        current_year_games = current_year_games.sort_values(by=['Year', 'Game Week #'], ascending=False)
        return current_year_games.head(n).to_dict(orient='records')

@app.route('/game_details', methods=['POST'])
def game_details():
    year = int(request.form.get('year'))
    game_week = int(request.form.get('game_week'))
    home_team = request.form.get('home_team')

    game = df[(df['Year'] == year) & (df['Game Week #'] == game_week) & (df['Home Team'] == home_team)].iloc[0]

    game_details = {
        'This Game SU #': int(game['This Game SU #']),
        'This Game Line #': int(game['This Game Line #']),
        'This Game ATS #': int(game['This Game ATS #']),
        'This Game Total': int(game['This Game Total']),
        'This Game Scored': int(game['This Game Scored']),
        'This Game Allowed': int(game['This Game Allowed'])
    }

    return jsonify(game_details)


if __name__ == '__main__':
    app.run(debug=True)
