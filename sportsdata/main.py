import pandas as pd
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sportsstatistics-49902-default-rtdb.firebaseio.com/'
})

root_ref = db.reference('/')
root_ref.delete()


excel_file_path = '../data/nfldata.xlsx'
df = pd.read_excel(excel_file_path)

def sanitize_key(key):
    return key.replace('#', 'no').replace('.', '').replace('$', '').replace('[', '').replace(']', '').replace('/', '')


years = df['Year'].unique()

for year in years:
    year_data = df[df['Year'] == year]
    teams = year_data['Home Team'].unique()

    for team in teams:
        team_data = year_data[year_data['Home Team'] == team]
        total_matches = team_data.shape[0]

        team_data_sorted = team_data.sort_values(by='Game Week #')

        year_ref = db.reference(str(year))
        team_ref = year_ref.child(sanitize_key(team))
        all_matches_ref = team_ref.child('All matches')

        order_of_matches = team_data_sorted.index.tolist()

        order_of_matches_with_teams = []
        for idx in order_of_matches:
            match = team_data_sorted.loc[idx]
            order_of_matches_with_teams.append({
                'match_id': idx,
                'team_vs_opposing': f"{match['Home Team']} vs {match['Opposing Team']}"
            })

        all_matches_ref.set({
            'total matches': total_matches,
            'order of matches': order_of_matches_with_teams
        })

        game_types = team_data['This Game Type'].unique()

        for game_type in game_types:
            game_type_data = team_data_sorted[team_data_sorted['This Game Type'] == game_type]
            for index, match in game_type_data.iterrows():
                match_id = index
                match_data = match.to_dict()
                del match_data['Year']
                del match_data['Home Team']

                sanitized_match_data = {sanitize_key(k): v for k, v in match_data.items()}

                game_type_ref = team_ref.child(sanitize_key(game_type)).child(str(match_id))
                game_type_ref.set(sanitized_match_data)

print("Data has been successfully uploaded to Firebase!")
