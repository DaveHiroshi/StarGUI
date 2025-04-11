import random
from game import Game, Player


# Hauptklasse, die das Spiel steuert
class GameEngine:
    def __init__(self):
        self.game = Game()  # Neues Spielobjekt
        self.game.load_json()  # Lädt Story und Spielwelt aus JSON
        self.game.create_game()  # Erstellt Spielstruktur
        self.player = None  # Spielerobjekt (noch leer)

    # Initialisiert das Spiel mit einem Spielernamen
    def initialize_game(self, player_name):
        self.player = Player(player_name)
        self.game.player = self.player
        # Startposition: Planet Erde, Raum "Quarters"
        self.player.current_planet = self.game.planets["Earth"]
        self.player.current_room = self.player.current_planet.rooms["Quarters"]
        return self.get_room_status()

    # Gibt aktuellen Raumstatus (Name, Beschreibung, NPCs, Items, Ziel)
    def get_room_status(self):
        room = self.player.current_room
        msg = f"\n Location: {room.name}\n{room.description}"
        if room.npc and not room.npc.dead:  #falls npc im raum
            msg += f"\n You see {room.npc.name} here."  #an msg wird angehängt
        if room.items:
            msg += f"\n Items in room: {', '.join(room.items)}"
        msg += f"\n Current Objective: {self.game.current_objective[-1]}"
        return msg

    # Gibt verfügbare Aktionen basierend auf Rauminhalt zurück
    def get_available_actions(self):
        room = self.player.current_room
        actions = ["move", "quit"]
        if room.items:  #wenn items existieren
            actions.append("pickup")
        if room.npc and not room.npc.dead:
            actions.append("interact")
            if room.npc.hostile:    #falls npc hostile
                actions.append("kill")
        if any(conn.connection_type == "interplanetary" for conn in room.connections):  #falls interplanetary connections existieren, iterate über alle connections
            actions.append("travel")    
        if room.name.lower() == "reactor":  #falls im raum reactor
            actions.append("plant")
        if room.name.lower() == "shield generator": #falls im raum shield generator
            actions.append("drop")
        return actions

    # Bewegung zu einem benachbarten Raum (nicht interplanetar)
    def move(self, direction_name):
        room = self.player.current_room
        connections = [
            conn for conn in room.connections if conn.connection_type != "interplanetary" # iterate über alle connections, die nicht interplanetary sind
        ]
        for conn in connections:
            if conn.to_room.lower() == direction_name.lower():   # falls der Raum existiert
                next_room = self.game.find_room_by_name(conn.to_room) # suche den Raum mit namen
                if not next_room:                                      # falls der Raum nicht existiert
                    return f" The room '{conn.to_room}' could not be found."
                if self.game.check_room_requirements(next_room):       # prüfe ob die Anforderungen erfüllt sind
                    self.player.current_room = next_room               # setze den aktuellen Raum auf den nächsten Raum
                    self.game.update_current_objective(next_room)       # aktualisiere das aktuelle Ziel
                    if next_room.name.lower() == "front gate":          # falls der Raum der Front Gate ist
                        self.game.kill_player()                         # töte den Spieler
                    return f" You moved to {next_room.name}.\n" + self.get_room_status() # gebe den neuen Raumstatus zurück
                else:
                    return f"🚫 Requirements not met for room {next_room.name}, you're missing {next_room.requirement[0]} ."
        return f" No connection to room '{direction_name}'."

    # Reisen zu einem anderen Planeten (interplanetar)
    def travel(self, destination_index):
        room = self.player.current_room  # Raum des Spielers
        interplanetary = [
            conn for conn in room.connections if conn.connection_type == "interplanetary" # alle interplanetary connections
        ]
        if 0 <= destination_index < len(interplanetary):    # falls der Index gültig ist
            conn = interplanetary[destination_index]        # Verbindung zu einem anderen Raum
            next_room = self.game.find_room_by_name(conn.to_room)   # suche den Raum mit dem Namen
            if not next_room:                                   # falls der Raum nicht existiert
                return f" Room '{conn.to_room}' not found."     
            if self.game.check_room_requirements(next_room):    # prüfe ob die Anforderungen erfüllt sind
                if room.name.lower() == "shuttle bay" and next_room.name.lower() == "briefing room":    # falls der Raum Shuttle Bay ist und der nächste Raum Briefing Room ist
                    # Spielsieg bei Zielerreichung
                    outro = self.game.story_data.get("game_story", {}).get("outro", [])     # gebe die Outro-Story zurück
                    return "\n".join(outro) + "\n You win!"     
                self.player.current_room = next_room           # setze den aktuellen Raum auf den nächsten Raum
                self.player.current_planet = next(              # setze den aktuellen Planeten auf den nächsten Planeten
                    planet for planet in self.game.planets.values() # iteriere über alle Planeten
                    if next_room.name in planet.rooms               # falls der Raum im Planeten existiert
                )
                self.game.update_current_objective(next_room)       # aktualisiere das aktuelle Ziel
                return f" You traveled to {next_room.name}.\n" + self.get_room_status() # gebe den neuen Raumstatus zurück
            else:
                return f" Cannot travel. Requirements not met for {next_room.requirement}."
        return " Invalid travel destination index."

    # Interaktion mit einem NPC im Raum
    def interact(self):
        npc = self.player.current_room.npc  # NPC im aktuellen Raum
        if not npc or npc.dead:             # falls kein NPC existiert oder der NPC tot ist
            return "There's no one to interact with."

        lines = []                          # Liste für Dialogzeilen
        default_dialog = npc.dialogues.get("default", [])
        if default_dialog:
            lines.append(f"{npc.name}: {random.choice(default_dialog)}")    # zufällige Zeile aus dem Standarddialog

        if npc.hostile:                             # falls der NPC feindlich ist
            if self.player.has_weapon():            # falls der Spieler bewaffnet ist
                lines.append(f" {npc.name} is hostile. You are armed.") 
            else:
                lines.append(f" {npc.name} is hostile, and you're unarmed. Be careful.")
        else:
            topics = [k for k in npc.dialogues.keys() if k != "default"]    # erstes k ist was zur liste hinzugefügt wird, was nicht default ist, zweites k ist was in der liste ist
            if topics:                       # falls Themen existieren
                lines.append(f"🗣️ Topics: {', '.join(topics)} (not interactive in GUI yet)")
        return "\n".join(lines)

    # Gegenstand im Raum aufnehmen
    def pickup(self, item_name):
        room = self.player.current_room     # aktueller Raum des Spielers
        if item_name in room.items:       # falls der Gegenstand im Raum existiert
            room.remove_item(item_name)     # entferne den Gegenstand aus dem Raum
            self.player.add_item(item_name)   # füge den Gegenstand zum Inventar des Spielers hinzu
            return f"✅ You picked up {item_name}." 
        return f" '{item_name}' is not in this room."

    # Gegner töten, wenn Spieler bewaffnet ist
    def kill(self, enemy_name):
        npc = self.player.current_room.npc  # NPC im aktuellen Raum
        if not npc or npc.dead:             # falls kein NPC existiert oder der NPC tot ist
            return " There's no enemy here."
        if npc.firstname.lower() != enemy_name.lower(): # falls der Name des NPCs nicht mit dem eingegebenen Namen übereinstimmt
            return f" No enemy named '{enemy_name}' here."
        if not self.player.has_weapon():        # falls der Spieler keine Waffe hat
            return " You don't have a weapon!"
        npc.dead = True                # setze den NPC auf tot
        self.player.current_room.npc = None # entferne den NPC aus dem Raum
        return f" You killed {npc.firstname} {npc.lastname}."

    # C4 im Reaktor platzieren
    def plant(self):
        room = self.player.current_room 
        if room.name.lower() != "reactor":  # falls der Raum nicht der Reaktor ist
            return " You're not in the Reactor."
        if "C4" in self.player.inventory:   # falls C4 im Inventar des Spielers ist
            del self.player.inventory["C4"] # entferne C4 aus dem Inventar
            room.remove_requirements()  # entferne die Anforderungen des Raums
            return "💣 You planted C4 in the reactor!"  
        return " You don't have C4."

    # Granate beim Generator werfen
    def drop(self):
        room = self.player.current_room # aktueller Raum des Spielers
        if room.name.lower() != "shield generator": # falls der Raum nicht der Schildgenerator ist
            return "⚠️ You're not in the Shield Generator."
        if "Grenade" in self.player.inventory:  # falls Granate im Inventar des Spielers ist    
            del self.player.inventory["Grenade"]    # entferne Granate aus dem Inventar
            return "💥 You threw the grenade at the generator!"
        return "❌ You don't have a grenade."

    # Spiel beenden
    def quit_game(self):
        return "🛑 Game ended. Thanks for playing!"
