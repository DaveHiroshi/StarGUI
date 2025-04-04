from time import sleep
import json
import time
import random

#################################################################
# Basisklasse für alle Spielobjekte
class GameObject:

    roomcounter = 0

    def __init__(self, name, description):
        self.name = name  # Name des Objekts
        self.description = description  # Beschreibung des Objekts

    def __repr__(self):
        # Gibt eine string-Repräsentation des Objekts zurück
        return f"{self.name}: {self.description}"

    def interact(self):
        # Standardinteraktion mit dem Objekt
        print(f"You interact with {self.name}.")

    @staticmethod
    def is_valid_name(name):
        
        return isinstance(name, str) and len(name.strip()) > 0      #es wird gesvhaut ob der name gültig ist

#################################################################
# Klasse für Räume im Spiel, erbt von GameObject
class Room(GameObject):
    def __init__(self, name, description, planet, objective=None, requirement=None, items=None, picture=None):
        super().__init__(name, description)
        self.planet = planet
        self.connections = []
        self.items = items if items else []
        self.requirement = requirement if requirement else []
        self.objective = objective
        self.npc = None
        self.picture = picture 


    def add_connection(self, connection):
        """Fügt eine Verbindung zu diesem Raum hinzu."""
        self.connections.append(connection)

    def add_npc(self, npc):
        """Weist einen NPC diesem Raum zu."""
        self.npc = npc

    def show_connected_rooms(self, current_room):
        """Zeigt alle verbundenen Räume an."""
        for index, connection in enumerate(self.connections):
            print(f"[{index + 1}] {connection}")

    def get_connection(self, index):
        """Gibt die Verbindung an einem bestimmten Index zurück."""
        return self.connections[index]

    def remove_item(self, item):
        """Entfernt einen Gegenstand aus dem Raum."""
        if item in self.items:
            self.items.remove(item)
    
    def remove_requirements(self):
        self.requirement = []

    def __repr__(self):
        # Gibt eine detaillierte Beschreibung des Raums zurück
        return f"Area: {self.name}\nDescription: {self.description}"

#################################################################
# Klasse für Planeten im Spiel, erbt von GameObject

class Planet(GameObject):
    def __init__(self, name, picture):
        # Validieren des Planetennamens mithilfe der statischen Methode
        if not GameObject.is_valid_name(name):
            raise ValueError(f"Ungültiger Planetname: '{name}'. Der Name muss ein nicht-leerer String sein.")
        
        super().__init__(name, description="Ein Planet im Spiel.")
        self.picture = picture
        self.rooms = {}  # Dictionary zur Speicherung von Räumen auf diesem Planeten

    def add_room(self, room):
        """Fügt einen Raum zum Planeten hinzu."""
        if room.name in self.rooms:
            print(f"⚠️ Warnung: Raum '{room.name}' existiert bereits auf dem Planeten '{self.name}'.")
        else:
            self.rooms[room.name] = room  # Raum wird zum Dictionary hinzugefügt


#################################################################
# Klasse für Verbindungen zwischen Räumen
class Connection:
    def __init__(self, from_room, to_room, connection_type):
        self._from_room = from_room  # Ausgangsraum (Room-Objekt)
        self._to_room = to_room.name  # Zielraum (nur Name)
        self._connection_type = connection_type  # Typ der Verbindung (z.B. 'interplanetary')

    @property
    def from_room(self):
        return self._from_room

    @from_room.setter
    def from_room(self, value):
        self._from_room = value

    @property
    def to_room(self):
        return self._to_room  # Gibt den Namen des Zielraums zurück

    @to_room.setter
    def to_room(self, value):
        self._to_room = value

    @property
    def connection_type(self):
        return self._connection_type

    @connection_type.setter
    def connection_type(self, value):
        self._connection_type = value

    def __repr__(self):
        # Gibt eine kurze Beschreibung der Verbindung zurück
        return f"Connection: to {self._to_room}"

#################################################################
# Klasse für den Spieler, erbt von GameObject
class Player(GameObject):
    def __init__(self, name, health=100):
        super().__init__(name, description="Der Spielercharakter.")
        self.current_planet = None  # Aktueller Planet, auf dem sich der Spieler befindet
        self.current_room = None  # Aktueller Raum, in dem sich der Spieler befindet
        self.health = health  # Gesundheit des Spielers
        self.inventory = {}  # Inventar des Spielers als Dictionary

    def add_item(self, item):
        """Fügt einen Gegenstand zum Inventar hinzu."""
        self.inventory[item] = True
        return f"You picked up {item}."

    def has_weapon(self):
        """Überprüft, ob der Spieler eine Waffe im Inventar hat."""
        weapons = ["P90", "M9", "C4", "Staff Weapon"]  # Liste aller Waffen
        return any(item in self.inventory for item in weapons)

    def __repr__(self):
        # Gibt eine Beschreibung des Spielers zurück, einschließlich Inventar
        inventory_str = ', '.join(self.inventory.keys())
        return f"Player: {self.name}, Health: {self.health}, Inventory: {inventory_str}"

#################################################################
# Klasse für Nicht-Spieler-Charaktere (NPCs), erbt von GameObject
class Npc(GameObject):
    def __init__(self, firstname, lastname, room, hostile, inventory=None, dialogues=None):
        super().__init__(name=f"{firstname} {lastname}", description="Ein NPC im Spiel.")
        self.firstname = firstname  # Vorname des NPC
        self.lastname = lastname  # Nachname des NPC
        self.room = room  # Raum, in dem sich der NPC befindet
        self.hostile = hostile  # Ob der NPC feindlich ist
        self.dead = False  # Status, ob der NPC tot ist
        self.inventory = inventory if inventory else []  # Inventar des NPC
        self.dialogues = dialogues if dialogues else {}  # Dialogoptionen des NPC

    def interact(self):
        """Behandelt die Interaktion mit dem NPC."""
        # Anzeige des Standarddialogs zuerst
        default_dialogues = self.dialogues.get("default", [])
        if default_dialogues:
            print(f"{self.firstname} {self.lastname}: {random.choice(default_dialogues)}")
        else:
            print(f"{self.firstname} {self.lastname} has nothing to say.")
            return

        # Anzeige verfügbarer Dialogthemen
        topics = [key for key in self.dialogues.keys() if key != "default"]
        if not topics:
            print(f"{self.firstname} {self.lastname} has no other topics to discuss.")
            return

        print("\nTopics to discuss:")
        for index, topic in enumerate(topics, start=1):
            print(f"[{index}] {topic.capitalize()}")

        # Ermöglicht dem Spieler, ein Thema auszuwählen
        try:
            choice = int(input("\nChoose a topic by entering the number: ").strip())
            if 1 <= choice <= len(topics):
                topic = topics[choice - 1]
                topic_dialogues = self.dialogues[topic]
                if topic_dialogues:
                    print(f"\n{self.firstname} {self.lastname}: {random.choice(topic_dialogues)}")
                else:
                    print(f"{self.firstname} {self.lastname} has no dialogue for this topic.")
            else:
                print("⚠️ Invalid choice. Please try again.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")

#################################################################
# Hauptklasse für das Spiel
class Game:
    def __init__(self):
        self.planets = {}  # Dictionary zur Speicherung aller Planeten
        self.room_map = {}  # Karte zur Zuordnung von Raumnamen zu Room-Objekten
        self.story_data = {}  # Daten für die Spielgeschichte
        self.rooms = {}  # Dictionary zur Speicherung aller Räume
        self.player = None  # Spielerobjekt
        self.current_objective = ["Go to the briefing room and talk to General Hammond."]  # Aktuelle Ziele des Spielers
        

    def load_json(self):
        """Lädt die Spielgeschichte aus einer JSON-Datei."""
        with open("game_story.json", 'r') as story_file:
            self.story_data["game_story"] = json.load(story_file)

    def create_game(self, world_file="world.json"):
        """Erstellt die Spielwelt, indem sie aus einer JSON-Datei geladen wird."""
        import json

        # Lade die Spieldaten aus der JSON-Datei
        with open(world_file, 'r') as file:
            world_data = json.load(file)

        # Zwischenspeicher für Verbindungen, die später hinzugefügt werden
        pending_connections = []

        #  Zuerst alle Planeten und Räume erstellen
        for planet_data in world_data["planets"]:
            planet_name = planet_data["name"]

            # Planet erstellen und im Dictionary speichern
            if planet_name in self.planets:
                print(f"⚠️ Warnung: Planet '{planet_name}' existiert bereits und wird übersprungen!")
                continue

            planet = Planet(name=planet_name, picture = planet_data.get("picture", None))  # Planet-Objekt erstellen
            self.planets[planet_name] = planet  # Planet in das Dictionary einfügen

            for room_data in planet_data["rooms"]:
                room_name = room_data["name"]

                # Überprüfen, ob der Raumname bereits existiert
                if room_name in self.rooms:
                    print(f"⚠️ Warnung: Raum '{room_name}' existiert bereits und wird übersprungen!")
                    continue

                # Raum-Objekt erstellen
                room = Room(
                    name=room_name,
                    description=room_data["description"],
                    planet=planet,
                    objective=room_data.get("objective"),
                    requirement=room_data.get("requirement", []),
                    items=room_data.get("items", []),
                    picture=room_data.get("picture", None)
                )

                # NPCs verarbeiten, falls vorhanden
                npc_data = room_data.get("npc")
                if npc_data:
                    npc = Npc(
                        firstname=npc_data["first_name"],
                        lastname=npc_data["last_name"],
                        room=room,
                        hostile=npc_data.get("hostile", False),
                        inventory=npc_data.get("inventory", []),
                        dialogues=npc_data.get("dialogues", {})
                    )
                    room.npc = npc  # NPC dem Raum zuweisen

                # Raum zur Raumliste und zum Planeten hinzufügen
                self.rooms[room_name] = room  # Raum im Raum-Dictionary speichern
                planet.add_room(room)  # Raum zum Planeten hinzufügen

                # Verbindungen zwischenspeichern, da andere Räume vielleicht noch nicht existieren
                for connection_data in room_data.get("connections", []):
                    pending_connections.append({
                        "from_room": room_name,
                        "to_room": connection_data["to_room"],
                        "type": connection_data["type"]
                    })

        #  Verbindungen verarbeiten, nachdem alle Räume erstellt wurden
        for connection in pending_connections:
            from_room = self.rooms.get(connection["from_room"])
            to_room = self.rooms.get(connection["to_room"])

            if from_room and to_room:
                conn = Connection(
                    from_room=from_room,
                    to_room=to_room,
                    connection_type=connection["type"]
                )
                from_room.add_connection(conn)
            else:
                if not from_room:
                    print(f"⚠️ Warnung: Ausgangsraum '{connection['from_room']}' nicht gefunden!")
                if not to_room:
                    print(f"⚠️ Warnung: Zielraum '{connection['to_room']}' nicht gefunden!")

        #  Interplanetare Verbindungen verarbeiten (optional, wenn sie außerhalb der Planeten definiert sind)
        for connection_data in world_data.get("connections", []):
            from_room = self.rooms.get(connection_data["from_room"])
            to_room = self.rooms.get(connection_data["to_room"])

            if from_room and to_room:
                connection = Connection(
                    from_room=from_room,
                    to_room=to_room,
                    connection_type=connection_data["type"]
                )
                from_room.add_connection(connection)
            else:
                if not from_room:
                    print(f"⚠️ Warnung: Ausgangsraum '{connection_data['from_room']}' nicht gefunden!")
                if not to_room:
                    print(f"⚠️ Warnung: Zielraum '{connection_data['to_room']}' nicht gefunden!")

    def find_room_by_name(self, room_name):
        """Findet einen Raum anhand seines Namens über alle Planeten hinweg."""
        for planet in self.planets.values():  # Zugriff auf die Werte des Planeten-Dictionary
            for room in planet.rooms.values():  # Zugriff auf die Räume des Planeten
                if room.name == room_name:
                    return room
        return None  # Rückgabe von None, wenn der Raum nicht gefunden wird

    def update_current_objective(self, room):
        """Aktualisiert das aktuelle Ziel des Spielers basierend auf dem betretenen Raum."""
        if room.objective and room.objective not in self.current_objective:
            self.current_objective.append(room.objective)

    def handle_trade(self, npc):
        """Behandelt den Handel mit einem NPC."""
        print(f"{npc.firstname} {npc.lastname}'s Inventory: {', '.join(npc.inventory)}")
        if not npc.inventory:
            print("The NPC has nothing to trade.")
            return

        choice = input("Which item would you like? Enter the name or type 'cancel': ").strip()
        if choice.lower() == "cancel":
            print("You decided not to trade.")
            return

        if choice in npc.inventory:
            npc.inventory.remove(choice)
            self.player.add_item(choice)
            print(f"You received {choice}!")
        else:
            print("Invalid choice. No trade was made.")

    def display_room_status(self):
        """Zeigt den aktuellen Status des Raums an, in dem sich der Spieler befindet."""
        print("\n" + "=" * 40)
        print(f"🌟 Current Objective: {self.current_objective[-1]}")
        print(f"📍 Current Location: {self.player.current_room.name}")
        print("-" * 40)
        print(f"{self.player.current_room.description}")
        if self.player.current_room.npc:
            print(f"🧑 You see {self.player.current_room.npc.firstname} {self.player.current_room.npc.lastname} here.")
        print("=" * 40)

    def kill_player(self):
        """Tötet den Spieler und beendet das Spiel."""
        print("⚠️ You have been captured by the Jaffa forces and have been killed!")
        print("Game Over.")
        self.player.current_room = self.rooms["Ascend"]
        
        

    def pickup_item(self):
        """Ermöglicht dem Spieler, einen Gegenstand aus dem aktuellen Raum aufzuheben."""
        room = self.player.current_room
        if not room.items:
            print(f"There are no items in {room.name}.")
            return

        print(f"\nItems in {room.name}:")
        for index, item in enumerate(room.items, start=1):
            print(f"[{index}] {item}")

        try:
            choice = int(input("Enter the number of the item you want to pick up: ").strip())
            if 1 <= choice <= len(room.items):
                item = room.items[choice - 1]
                self.player.add_item(item)  # Füge den Gegenstand zum Inventar des Spielers hinzu
                room.remove_item(item)  # Entferne den Gegenstand aus dem Raum
                print(f"You picked up {item}.")
            else:
                print("⚠️ Invalid choice. Please select a valid item number.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")

    def start(self):
        """Startet das Spiel."""
        self.load_json()  # Lade die Spielgeschichte
        self.create_game()  # Erstelle die Spielwelt

        # Zeige die Einführungsgeschichte an
        intro = self.story_data.get("game_story", {}).get("intro", {})
        if isinstance(intro, dict) and "text" in intro:         #Wenn Intro ein Dict ist und der Key text vorhanden ,dann holt es sich ihn
            print("\n" + "=" * 40)
            for line in intro["text"]:
                print(line)
            print("=" * 40)
        else:
            print("\n" + "=" * 40)
            print("Welcome to the Stargate Text Adventure!")
            print("=" * 40)

        # Erstelle den Spieler und setze den Startpunkt
        self.player = Player(input("\nEnter your name: "))
        self.player.current_planet = self.planets["Earth"]  # Startplanet
        self.player.current_room = self.player.current_planet.rooms["Quarters"]  # Startraum

        self.display_room_status()  # Zeige den Status des Startraums an

        # Hauptspielschleife
        while True:
            print("\n--- Available Actions ---")
            if self.player.current_room.items:
                print("[pickup] Pick up an item.")
            if self.player.current_room.npc:
                print("[interact] Interact with the NPC.")
            if any(conn.connection_type == "interplanetary" for conn in self.player.current_room.connections):
                print("[travel] Travel to another planet.")
            print("[move] Move to another room.")
            # Zusätzliche Aktionen für spezifische Räume hinzufügen
            if self.player.current_room.name.lower() == "reactor":
                print("[plant] Plant C4.")
            if self.player.current_room.name.lower() == "shield generator":
                print("[drop] Drop a grenade.")
            print("[quit] Quit the game.")
            print("-" * 40)

            action = input("What do you want to do? ").strip().lower()
            print("=" * 40)

            if action == "pickup" and self.player.current_room.items:
                self.pickup_item()
            elif action == "interact" and self.player.current_room.npc:
                self.interact_with_npc()
            elif action == "travel" and any(conn.connection_type == "interplanetary" for conn in self.player.current_room.connections):
                self.handle_gate_travel()
            elif action == "move":
                self.move()
            elif action == "plant" and self.player.current_room.name.lower() == "reactor":
                self.plant_c4()
            elif action == "drop" and self.player.current_room.name.lower() == "shield generator":
                self.drop_grenade()
            elif action == "quit":
                print("Thanks for playing!")
                break
            else:
                print("⚠️ Invalid action. Please try again.")

    def interact_with_npc(self):
        """Ermöglicht dem Spieler, mit einem NPC im aktuellen Raum zu interagieren."""
        npc = self.player.current_room.npc
        if not npc:
            print("There is no one here to interact with.")
            return

        # Wenn der NPC bereits tot ist
        if npc.dead:
            print(f"{npc.firstname} {npc.lastname} is already dead. There is nothing more to interact with.")
            return

        # Anzeige des Standarddialogs
        default_dialogues = npc.dialogues.get("default", [])
        if default_dialogues:
            print(f"{npc.firstname} {npc.lastname}: {random.choice(default_dialogues)}")
        else:
            print(f"{npc.firstname} {npc.lastname} has nothing to say.")

        # Umgang mit feindlichen NPCs
        if npc.hostile:
            print(f"\n⚠️ {npc.firstname} {npc.lastname} looks hostile!")
            if self.player.has_weapon():
                choice = input(f"\nYou have a weapon. Do you want to attack {npc.firstname}? (yes/no): ").strip().lower()
                if choice == "yes":
                    print(f"\n🔫 You attacked and killed {npc.firstname} {npc.lastname}!")
                    npc.dead = True
                    self.player.current_room.npc = None  # Entferne den NPC aus dem Raum
                    return
                else:
                    print("\nYou chose not to attack.")
            else:
                print("\n⚠️ You don't have a weapon to defend yourself. Be cautious.")
            return  # Beende die Interaktion, wenn der NPC feindlich ist

        # Umgang mit nicht feindlichen NPCs mit zusätzlichen Dialogthemen
        topics = [key for key in npc.dialogues.keys() if key != "default"]
        if not topics:
            print(f"{npc.firstname} {npc.lastname} has no additional topics to discuss.")
            return

        # Präsentation der Themen für den Spieler
        while True:
            print("\nTopics to discuss:")
            for index, topic in enumerate(topics, start=1):
                print(f"[{index}] {topic.capitalize()}")
            print(f"[{len(topics) + 1}] End Conversation")

            # Ermöglicht dem Spieler, ein Thema auszuwählen
            try:
                choice = int(input("\nChoose a topic by entering the number: ").strip())
                if 1 <= choice <= len(topics):
                    topic = topics[choice - 1]
                    topic_dialogues = npc.dialogues.get(topic, [])
                    if topic_dialogues:
                        print(f"\n{npc.firstname} {npc.lastname}: {random.choice(topic_dialogues)}")
                    else:
                        print(f"{npc.firstname} {npc.lastname} has nothing more to say about {topic}.")
                elif choice == len(topics) + 1:
                    print(f"You end the conversation with {npc.firstname} {npc.lastname}.")
                    break
                else:
                    print("⚠️ Invalid choice. Please try again.")
            except ValueError:
                print("⚠️ Invalid input. Please enter a number.")

    def check_room_requirements(self, next_room):
        """Überprüft, ob der Spieler die Anforderungen erfüllt, um einen Raum zu betreten."""
        requirements = next_room.requirement
        if all(item in self.player.inventory for item in requirements):
            return True
        else:
            missing_items = [item for item in requirements if item not in self.player.inventory]
            print(f"⚠️ You cannot enter {next_room.name}. Missing items: {', '.join(missing_items)}.")
            return False

    def handle_gate_travel(self):
        """Behandelt das Reisen durch das Stargate zwischen Planeten."""
        interplanetary_connections = [
            conn for conn in self.player.current_room.connections if conn.connection_type == "interplanetary"
        ]
        if not interplanetary_connections:
            print("⚠️ No Stargate connections available from this room.")
            return

        current_room_name = self.player.current_room.name.lower()

        print("\nAvailable Stargate Destinations:")
        for index, connection in enumerate(interplanetary_connections, start=1):
            print(f"[{index}] {connection.to_room}")

        try:
            choice = int(input("Enter the number of the destination: ").strip())
            if 1 <= choice <= len(interplanetary_connections):
                connection = interplanetary_connections[choice - 1]
                next_room = self.find_room_by_name(connection.to_room)
                if next_room:
                    if self.check_room_requirements(next_room):
                        # Spezifische Reisebedingung: Shuttlebay -> Briefing Room
                        if current_room_name == "shuttle bay" and connection.to_room.lower() == "briefing room":
                            print("You travel back to the Briefing Room by using a deathglider.")
                            outro = self.story_data.get("game_story", {}).get("outro", {})
                            for line in outro:
                                print(line)
                            exit(0)
                        else:
                            print("You step through the event horizon.")  # Standardnachricht für andere Reisen

                        # Aktualisieren des Spielerstandorts
                        self.player.current_room = next_room
                        self.player.current_planet = next(
                            planet for planet in self.planets.values() if next_room.name in planet.rooms
                        )
                        self.update_current_objective(next_room)  # Aktualisiere das Ziel
                        self.display_room_status()
                else:
                    print(f"⚠️ The room '{connection.to_room}' could not be found.")
            else:
                print("⚠️ Invalid choice. Please select a valid destination number.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")

    def move(self):
        """Behandelt die lokale Bewegung zwischen Räumen."""
        local_connections = [
            conn for conn in self.player.current_room.connections if conn.connection_type != "interplanetary"
        ]

        if not local_connections:
            print("⚠️ There are no local connections from this room.")
            return

        print("\nAvailable rooms:")
        for index, connection in enumerate(local_connections, start=1):
            print(f"[{index}] {connection.to_room}")

        try:
            choice = int(input("Enter the number of the room you want to move to: ").strip())
            if 1 <= choice <= len(local_connections):
                connection = local_connections[choice - 1]
                next_room = self.find_room_by_name(connection.to_room)
                if not next_room:
                    print(f"⚠️ The room '{connection.to_room}' could not be found.")
                    return

                if self.check_room_requirements(next_room):
                    self.player.current_room = next_room
                    self.update_current_objective(next_room)  # Aktualisiere das Ziel
                    self.display_room_status()

                    # Beispiel: Wenn der Spieler den "Front Gate" betritt, wird er getötet
                    if next_room.name.lower() == "front gate":
                        self.kill_player()
            else:
                print("⚠️ Invalid choice. Please select a valid room number.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")

    #################################################################
    # Neue Methode zum Pflanzen von C4 im Reactor-Raum
    def plant_c4(self):
        """Ermöglicht dem Spieler, C4 im Reactor-Raum zu pflanzen."""
        reactor_room = self.find_room_by_name("Reactor")
        if reactor_room and reactor_room == self.player.current_room:
            # Überprüfen, ob der Spieler C4 bereits im Inventar hat
            if "C4" in self.player.inventory:
                print("You carefully plant the C4 in the Reactor.")
                # Entferne C4 aus dem Inventar nach dem Pflanzen
                del self.player.inventory["C4"]
                # Füge eine neue Bedingung oder ein neues Ziel hinzu
                self.player.current_room.remove_requirements()
                
                print("C4 is planted. It will explode soon.")
            else:
                print("You don't have C4 to plant.")
        else:
            print("⚠️ You are not in the Reactor room.")

    #################################################################
    # Neue Methode zum Werfen einer Granate im ShieldGenerator-Raum
    def drop_grenade(self):
        """Ermöglicht dem Spieler, eine Granate im ShieldGenerator-Raum zu werfen."""
        shield_room = self.find_room_by_name("Shield Generator")
        if shield_room and shield_room == self.player.current_room:
            # Überprüfen, ob der Spieler eine Granate im Inventar hat
            if "Grenade" in self.player.inventory:
                print("You throw the grenade at the Shield Generator.")
                # Entferne die Granate aus dem Inventar nach dem Werfen
                del self.player.inventory["Grenade"]
                # Füge eine neue Bedingung oder ein neues Ziel hinzu
                print("Grenade thrown. You shouldnt stick around and watch it explode.")
            else:
                print("You don't have a grenade to drop.")
        else:
            print("⚠️ You are not in the Shield Generator room.")


#################################################################
# Funktion zum Starten des Spiels
def startgame(): 
    game = Game()
    game.start()

# Überprüft, ob das Skript direkt ausgeführt wird
if __name__ == "__main__":
    startgame()
