import streamlit as st
import json

class StreamlitApp:
    def __init__(self, api_handler):
        self.api_handler = api_handler

    def run(self):
        st.title('Bienvenido a MONGO ADC')
        st.subheader('🔮 Predicciones de fútbol y búsqueda de jugadores')

        with st.sidebar:
            if 'user' not in st.session_state:
                st.title('🔐 Acceso')
                login_option = st.radio('Selecciona una opción', ['Iniciar Sesión', 'Registrarse'])

                if login_option == "Iniciar Sesión":
                    self.display_login_section()
                elif login_option == "Registrarse":
                    self.display_register_section()
            else:
                self.display_user_section()
                st.empty()

        
                self.handle_prediction_section()

                if 'current_view' not in st.session_state:
                    st.session_state['current_view'] = None

                if 'selected_prediction_option' in st.session_state:
                    if st.session_state['selected_prediction_option'] == 'Predecir ganador':
                        
                        if st.session_state['current_view'] == 'teams_selection':
                            self.handle_teams_selection()
                        else:    
                            self.handle_competition_selection()
                        

                        
                    elif st.session_state['selected_prediction_option'] == 'Viabilidad de fichajes (1-50)':
                        self.handle_search_player_rank()
                        

                    elif st.session_state['selected_prediction_option'] == 'Buscar 11 ideal de un equipo en una temporada':
                            
                        if st.session_state['current_view'] == 'team_selection_by_season':
                            self.handle_team_lineup_selection()
                        else:
                            self.handle_competition_and_season_selection()
        
        # Sección de predicciones
        if 'current_view' in st.session_state:
            if st.session_state['current_view'] == 'predict_winner_return':
                st.subheader('Predecir ganador')
                self.predict_winner()

            if st.session_state['current_view'] == 'search_best_players_return':
                st.subheader('Viabilidad de fichajes (1-50)')
                self.get_player_rank()

            if st.session_state['current_view'] == 'team_lineup_return':
                st.subheader(f'11 de la temporada {st.session_state["season"]} del {st.session_state["team_name"]}')
                self.get_best_players_by_season_and_team()
           

   

    def handle_teams_selection(self):

        if 'selected_competition_id' in st.session_state:
            st.title('Selecciona los equipos')
            teams_data = self.api_handler.get_request(f'get_teams/{st.session_state["selected_competition_id"]}').json()
            teams_options = {team['name']: team['club_id'] for team in teams_data}

            # Selección del equipo local
            selected_local_team_name = st.selectbox(
                'Selecciona el equipo local',
                list(teams_options.keys()),
                key='local_team_select_box'
            )

            available_away_teams = {name: club_id for name, club_id in teams_options.items() if name != selected_local_team_name}


            # Selección del equipo visitante
            selected_away_team_name = st.selectbox(
                'Selecciona el equipo visitante',
                list(available_away_teams.keys()),
                key='away_team_select_box'
            )

        
            if st.button("Confirmar selección de equipos"):
                
                st.session_state['selected_local_team_name'] = selected_local_team_name
                st.session_state['selected_local_team_id'] = teams_options[st.session_state['selected_local_team_name']]

                st.session_state['selected_away_team_name'] = selected_away_team_name
                st.session_state['selected_away_team_id'] = available_away_teams[st.session_state['selected_away_team_name']]

                st.session_state['current_view'] = 'predict_winner_return'

                st.rerun()

            st.empty()
            
            st.title('¿Quieres cambiar la competición?')
            if st.button("Cambiar competición", key='change_competition'):
                # Limpiar selección actual y regresar al inicio
                for key in ['selected_competition_id', 'selected_local_team_id', 'selected_away_team_id']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    def handle_competition_and_season_selection(self):
        st.title('Selecciona la competición y la temporada')

        # Carga de datos de competiciones
        competitions_data = self.api_handler.get_request('get_competitions').json()
        competitions_options = {competition['name']: competition['competition_id'] for competition in competitions_data}

        selected_competition_name = st.selectbox(
            'Selecciona la competición',
            list(competitions_options.keys()),
            key='competition_select_box'
        )

        # Carga de datos de temporadas
        seasons_data = self.api_handler.get_request('get_seasons').json()

        selected_season = st.selectbox(
            'Selecciona la temporada',
            seasons_data,  # Aquí pasamos la lista de temporadas directamente
            key='season_select_box'
        )

        if st.button("Confirmar selección de competición y temporada"):
            st.session_state['selected_competition_id'] = competitions_options[selected_competition_name]
            st.session_state['season'] = selected_season
            st.session_state['current_view'] = 'team_selection_by_season'
            st.rerun()
    
    def handle_team_lineup_selection(self):
        st.title('Selecciona el equipo')
        teams_data = self.api_handler.get_request(f'get_teams_by_season/{st.session_state["selected_competition_id"]}/{st.session_state["season"]}').json()
        
        teams_options = {team['name']: team['club_id'] for team in teams_data}

        selected_team_name = st.selectbox(
            'Selecciona el equipo',
            list(teams_options.keys()),
            key='team_select_box'
        )

        if st.button("Confirmar selección de equipo"):
            st.session_state['team_name'] = selected_team_name
            st.session_state['team_id'] = teams_options[selected_team_name]
            st.session_state['current_view'] = 'team_lineup_return'
            st.rerun()

    def handle_prediction_section(self):
        prediction_option = st.selectbox(
            "¿Qué quieres hacer?",
            ["Predecir ganador", "Viabilidad de fichajes (1-50)", "Buscar 11 ideal de un equipo en una temporada"],
            key='prediction_option_select_box'
        )
        st.session_state['selected_prediction_option'] = prediction_option
        

    def handle_competition_selection(self):
        st.title('Selecciona la competición')

        competitions_data = self.api_handler.get_request('get_competitions').json()
        competitions_options = {competition['name']: competition['competition_id'] for competition in competitions_data}

        selected_competition_name = st.selectbox(
            'Selecciona la competición',
            list(competitions_options.keys()),
            key='competition_select_box'
        )

        if st.button("Confirmar selección de competición"):
            st.session_state['selected_competition_id'] = competitions_options[selected_competition_name]
            st.session_state['current_view'] = 'teams_selection'
            st.rerun()

    def handle_search_player_rank(self):


        players = self.api_handler.get_request('get_players').json()
        player_options = {player['player_name']: player['player_id'] for player in players}

        player = st.selectbox("Selecciona el jugador", list(player_options.keys()))

        if st.button("Buscar ranking del jugador"):
            st.session_state['player_id'] = player_options[player]
            st.session_state['player_name'] = player
            st.session_state['current_view'] = 'search_best_players_return'
            st.rerun()
        


    def predict_winner(self):
        response = self.api_handler.post_request('predict_winner', {
            'local_team_id': st.session_state['selected_local_team_id'],
            'away_team_id': st.session_state['selected_away_team_id']
        })

        if response.status_code == 200:
            prediction = response.json()
            st.markdown(f"#### {prediction['prediction']}") 

    def get_player_rank(self):
        response = self.api_handler.get_request(f'get_player_rank/{st.session_state["player_id"]}')

        if response.status_code == 200:
            player_rank = response.json()
            st.markdown(f"#### {st.session_state['player_name']} está en el grupo {player_rank+1} de mejores jugadores para fichar actualmente, siendo 1 el mejor y 50 el peor, suponiendo que se adquieran todos al mismo precio.")
        else:
            st.error("No se ha podido obtener la información del jugador")

    def get_best_players_by_season_and_team(self):
        response = self.api_handler.post_request('get_best_players_by_season_and_team', {
            'season': st.session_state['season'],
            'club_id': st.session_state['team_id']
        })

        if response.status_code == 200:
            best_players = response.json()

            goalkeepers = []
            defenders = []
            midfielders = []
            forwards = []

            for player in best_players:
                if player['position'] == 'Goalkeeper':
                    goalkeepers.append(player)
                elif player['position'] == 'Defender':
                    defenders.append(player)
                elif player['position'] == 'Midfield':
                    midfielders.append(player)
                elif player['position'] == 'Attack':
                    forwards.append(player)
            
            if goalkeepers:
                st.markdown("#### Porteros:")
                for player in goalkeepers:
                    st.markdown(f"##### - {player['player_name']}: {player['total_minutes']} minutos jugados")

            if defenders:
                st.markdown("#### Defensas:")
                for player in defenders:
                    st.markdown(f"##### - {player['player_name']}: {player['total_minutes']} minutos jugados")

            if midfielders:
                st.markdown("#### Medios:")
                for player in midfielders:
                    st.markdown(f"##### - {player['player_name']}: {player['total_minutes']} minutos jugados")

            if forwards:
                st.markdown("#### Delanteros:")
                for player in forwards:
                    st.markdown(f"##### - {player['player_name']}: {player['total_minutes']} minutos jugados")
        else:
            st.error("No se han encontrado jugadores")



    def display_login_section(self):
        email, password = st.text_input("Email"), st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            auth_response = self.api_handler.post_request("login", {"email": email, "password": password})
            if auth_response.status_code == 200:
                st.success("¡Inicio de sesión exitoso!")
                st.session_state["user"] = {"email": email, "password": password}
                st.rerun()
            else:
                st.error("No se ha podido iniciar sesión")

    def display_register_section(self):
        user_details = {
            "email": st.text_input("Email"),
            "password": st.text_input("Contraseña", type="password"),
            "name": st.text_input("Nombre")
        }
        if st.button("Registrar"):
            reg_response = self.api_handler.post_request("create_user", user_details)
            if reg_response.status_code == 201:
                st.success("¡Usuario creado exitosamente!")
            elif reg_response.status_code == 409:
                st.error("El usuario ya existe")
            else:
                st.error("Error al crear el usuario. Por favor, verifica los datos ingresados.")

    def display_user_section(self):
        st.title('👤 Usuario')
        st.write(f"Email: {st.session_state['user']['email']}")
        if st.button("Cerrar Sesión"):
            self.api_handler.post_request("logout", {})
            st.session_state.pop("user")
            st.rerun()