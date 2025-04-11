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
            conn for conn in room.connections if conn.connection_type != "interplanetary"
        ]
        for conn in connections:
            if conn.to_room.lower() == direction_name.lower():
                next_room = self.game.find_room_by_name(conn.to_room)
                if not next_room:
                    return f" The room '{conn.to_room}' could not be found."
                if self.game.check_room_requirements(next_room):
                    self.player.current_room = next_room
                    self.game.update_current_objective(next_room)
                    if next_room.name.lower() == "front gate":
                        self.game.kill_player()
                    return f" You moved to {next_room.name}.\n" + self.get_room_status()
                else:
                    return f"🚫 Requirements not met for room {next_room.name}, you're missing {next_room.requirement[0]} ."
        return f" No connection to room '{direction_name}'."

    # Reisen zu einem anderen Planeten (interplanetar)
    def travel(self, destination_index):
        room = self.player.current_room
        interplanetary = [
            conn for conn in room.connections if conn.connection_type == "interplanetary"
        ]
        if 0 <= destination_index < len(interplanetary):
            conn = interplanetary[destination_index]
            next_room = self.game.find_room_by_name(conn.to_room)
            if not next_room:
                return f" Room '{conn.to_room}' not found."
            if self.game.check_room_requirements(next_room):
                if room.name.lower() == "shuttle bay" and next_room.name.lower() == "briefing room":
                    # Spielsieg bei Zielerreichung
                    outro = self.game.story_data.get("game_story", {}).get("outro", [])
                    return "\n".join(outro) + "\n You win!"
                self.player.current_room = next_room
                self.player.current_planet = next(
                    planet for planet in self.game.planets.values()
                    if next_room.name in planet.rooms
                )
                self.game.update_current_objective(next_room)
                return f" You traveled to {next_room.name}.\n" + self.get_room_status()
            else:
                return f" Cannot travel. Requirements not met for {next_room.requirement}."
        return " Invalid travel destination index."

    # Interaktion mit einem NPC im Raum
    def interact(self):
        npc = self.player.current_room.npc
        if not npc or npc.dead:
            return "There's no one to interact with."

        lines = []
        default_dialog = npc.dialogues.get("default", [])
        if default_dialog:
            lines.append(f"{npc.name}: {random.choice(default_dialog)}")

        if npc.hostile:
            if self.player.has_weapon():
                lines.append(f" {npc.name} is hostile. You are armed.")
            else:
                lines.append(f" {npc.name} is hostile, and you're unarmed. Be careful.")
        else:
            topics = [k for k in npc.dialogues.keys() if k != "default"]
            if topics:
                lines.append(f"🗣️ Topics: {', '.join(topics)} (not interactive in GUI yet)")
        return "\n".join(lines)

    # Gegenstand im Raum aufnehmen
    def pickup(self, item_name):
        room = self.player.current_room
        if item_name in room.items:
            room.remove_item(item_name)
            self.player.add_item(item_name)
            return f"✅ You picked up {item_name}."
        return f" '{item_name}' is not in this room."

    # Gegner töten, wenn Spieler bewaffnet ist
    def kill(self, enemy_name):
        npc = self.player.current_room.npc
        if not npc or npc.dead:
            return " There's no enemy here."
        if npc.firstname.lower() != enemy_name.lower():
            return f" No enemy named '{enemy_name}' here."
        if not self.player.has_weapon():
            return " You don't have a weapon!"
        npc.dead = True
        self.player.current_room.npc = None
        return f" You killed {npc.firstname} {npc.lastname}."

    # C4 im Reaktor platzieren
    def plant(self):
        room = self.player.current_room
        if room.name.lower() != "reactor":
            return " You're not in the Reactor."
        if "C4" in self.player.inventory:
            del self.player.inventory["C4"]
            room.remove_requirements()
            return "💣 You planted C4 in the reactor!"
        return " You don't have C4."

    # Granate beim Generator werfen
    def drop(self):
        room = self.player.current_room
        if room.name.lower() != "shield generator":
            return "⚠️ You're not in the Shield Generator."
        if "Grenade" in self.player.inventory:
            del self.player.inventory["Grenade"]
            return "💥 You threw the grenade at the generator!"
        return "❌ You don't have a grenade."

    # Spiel beenden
    def quit_game(self):
        return "🛑 Game ended. Thanks for playing!"
