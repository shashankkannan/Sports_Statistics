from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("sportsstatistics-49902-firebase-adminsdk-zv0k0-b61e4fcdfb.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sportsstatistics-49902-default-rtdb.firebaseio.com/'
})

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
            return render_template('querypage.html', years=years, selected_year=selected_year,
                                   selected_game_week=game_week, matchups=matchups)

        selected_matchup = request.form.get('matchup')
        if selected_matchup:
            selected_year = int(request.form.get('selected_year'))
            selected_game_week = int(request.form.get('selected_game_week'))
            home_team, opposing_team = selected_matchup.split(" vs ")

            past_matches = int(request.form.get('past_matches', 4))

            current_matchup = df1[(df1['Home Team'] == home_team) & (df1['Opposing Team'] == opposing_team) & (
                        df1['Year'] == selected_year) & (df1['Game Week #'] == selected_game_week)].iloc[0].to_dict()

            # last 4 games of the home team
            home_team_games = get_last_n_games(df1, home_team, selected_year, selected_game_week, past_matches)

            # last 4 games of the opposing team
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


@app.route('/select_year', methods=['GET', 'POST'])
def select_year():
    if request.method == 'POST':
        year = request.form['year']
        return redirect(url_for('select_team', year=year))

    ref = db.reference('/')
    years = ref.get().keys()
    return render_template('select_year.html', years=years)


@app.route('/select_team/<year>', methods=['GET', 'POST'])
def select_team(year):
    if request.method == 'POST':
        team = request.form['team']
        return redirect(url_for('display_data', year=year, team=team))

    ref = db.reference(f'/{year}')
    teams = ref.get().keys()
    return render_template('select_team.html', year=year, teams=teams)


@app.route('/display_data/<year>/<team>', methods=['GET'])
def display_data(year, team):
    ref = db.reference(f'/{year}/{team}')
    opposing_teams = []
    # Fetch all matches
    all_matches = ref.child('All matches').get()
    total_matches = all_matches.get('total matches', 0) if all_matches else 0

    # Get the selected game type from the query parameters
    game_type = request.args.get('game_type', 'all')

    # Fetch matches for the selected game type
    if game_type == 'all':
        match_data = {}
        for game_type in ['Con', 'Div', 'Int']:
            game_matches = ref.child(game_type).get()
            if game_matches:
                match_data[game_type] = []
                for match_id, match in game_matches.items():
                    opposing_team = match.get('Opposing Team', 'Unknown Team')
                    opposing_teams.append(opposing_team)
                    game_week_no = match.get('Game Week no', 'Unknown Game Week')
                    match_data[game_type].append({
                        'match_id': match_id,
                        'opposing_team': opposing_team,
                        'game_week_no': game_week_no,
                        'hometm': team
                    })
    else:
        game_matches = ref.child(game_type).get()
        match_data = {game_type: []}
        if game_matches:
            for match_id, match in game_matches.items():
                opposing_team = match.get('Opposing Team', 'Unknown Team')
                opposing_teams.append(opposing_team)
                game_week_no = match.get('Game Week no', 'Unknown Game Week')
                match_data[game_type].append({
                    'match_id': match_id,
                    'opposing_team': opposing_team,
                    'game_week_no': game_week_no,
                    'hometm': team
                })

    return render_template('display_data.html', year=year, team=team, total_matches=total_matches,
                           match_data=match_data, opposing_teams=opposing_teams)


@app.route('/fetch_match_details', methods=['POST'])
def fetch_match_details():
    year = request.json['year']
    team = request.json['team']
    match_id = request.json['match_id']
    game_type = request.json['game_type']
    gameweek = request.json.get('match_gameweek_no')
    hmt = request.json.get('hmt')

    ref = db.reference(f'/{year}/{team}/{game_type}/{match_id}')
    match_details = ref.get()

    ref1 = db.reference(f'/{year}/{team}/All matches/total matches')
    tot = ref1.get()
    if tot is not None:
        total_gameweeks = int(tot)
        print("Total gameweeks: ",total_gameweeks)
    else:
        total_gameweeks = 16

    if gameweek:
        match_details['Gameweek'] = gameweek
        previous_gameweeks_home_team = []
        previous_gameweeks_opp_team = []
        current_gameweek = int(gameweek)

        # Get total gameweeks for the home team and the opposing team
        total_gameweeks_home_team = db.reference(f'/{year-1}/{match_details["Opposing Team"]}/All matches/total matches').get()
        ref_opp_team = db.reference(f'/{year-1}/{match_details["Opposing Team"]}/All matches/total matches')
        tot_opp_team = ref_opp_team.get()
        if tot_opp_team is not None:
            total_gameweeks_opp_team = int(tot_opp_team)
            print("Total gameweeks for Opposing Team: ", total_gameweeks_opp_team)
        else:
            total_gameweeks_opp_team = 16

        for i in range(1, 5):
            # Calculate previous gameweeks for the home team
            if (current_gameweek - i) > 0:
                previous_gameweeks_home_team.append(current_gameweek - i)
            else:
                previous_gameweeks_home_team.append(
                    str(total_gameweeks_home_team + (current_gameweek - i)) + 'P')

            # Calculate previous gameweeks for the opposing team
            if (current_gameweek - i) > 0:
                previous_gameweeks_opp_team.append(current_gameweek - i)
            else:
                previous_gameweeks_opp_team.append(
                    str(total_gameweeks_opp_team + (current_gameweek - i)) + 'P')

        match_details['Previous_Gameweeks_Home_Team'] = previous_gameweeks_home_team
        match_details['Previous_Gameweeks_Opp_Team'] = previous_gameweeks_opp_team
        match_details['year'] = year
        match_details['Selected Team'] = hmt
        match_details['Against Team'] = match_details['Opposing Team']

        def get_match_id(year, team, gameweek_num):
            ref = db.reference(f'/{year}/{team}/All matches/order of matches/{gameweek_num - 1}/match_id')
            return ref.get()

        def find_match_in_game_types(year, team, match_id):
            game_types = ['Con', 'Div', 'Int']
            for game_type in game_types:
                ref = db.reference(f'/{year}/{team}/{game_type}/{match_id}')
                match_data = ref.get()
                if match_data:
                    return match_data, game_type
            return None, None

        yearC = year
        yearP = year - 1

        table = []

        for gw_home, gw_opp in zip(previous_gameweeks_home_team, previous_gameweeks_opp_team):
            if 'P' in str(gw_home):
                gameweek_num_home = int(gw_home[:-1])
                year_to_fetch_home = yearP
            else:
                gameweek_num_home = int(gw_home)
                year_to_fetch_home = yearC

            if 'P' in str(gw_opp):
                gameweek_num_opp = int(gw_opp[:-1])
                year_to_fetch_opp = yearP
            else:
                gameweek_num_opp = int(gw_opp)
                year_to_fetch_opp = yearC

            match_id_for_gw_home = get_match_id(year_to_fetch_home, team, gameweek_num_home)
            match_id_for_gw_opp = get_match_id(year_to_fetch_opp, match_details["Opposing Team"], gameweek_num_opp)

            if match_id_for_gw_home:
                selected_team_data_home, _ = find_match_in_game_types(year_to_fetch_home, team, match_id_for_gw_home)
                against_team_data_home, _ = find_match_in_game_types(year_to_fetch_home, match_details["Opposing Team"],
                                                                     match_id_for_gw_home)

                table.append({
                    'Year': year_to_fetch_home,
                    'Gameweek': gameweek_num_home,
                    'Team': hmt,
                    'Opponent': match_details['Opposing Team'],
                    'Selected_Team_Data': selected_team_data_home
                })

            if match_id_for_gw_opp:
                selected_team_data_opp, _ = find_match_in_game_types(year_to_fetch_opp, match_details["Opposing Team"],
                                                                     match_id_for_gw_opp)
                against_team_data_opp, _ = find_match_in_game_types(year_to_fetch_opp, team, match_id_for_gw_opp)

                table.append({
                    'Year': year_to_fetch_opp,
                    'Gameweek': gameweek_num_opp,
                    'Team': match_details['Opposing Team'],
                    'Opponent': hmt,
                    'Selected_Team_Data': selected_team_data_opp
                })

        match_details['Previous_Matches'] = table

    return jsonify(match_details)




if __name__ == '__main__':
    app.run(debug=True)
