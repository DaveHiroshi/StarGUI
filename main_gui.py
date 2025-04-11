import os
import customtkinter as ctk
from PIL import Image
from game_engine import GameEngine 
import random


# Name small window
class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Confirm", message="Do you really want to quit?"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.result = False
        self.grab_set()  
        self.protocol("WM_DELETE_WINDOW", self.on_no)

        label = ctk.CTkLabel(self, text=message)
        label.pack(pady=20)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        yes_button = ctk.CTkButton(button_frame, text="Yes", command=self.on_yes)
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(button_frame, text="No", command=self.on_no)
        no_button.pack(side="left", padx=10)

        self.wait_window(self)

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()




# Main GUI class
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stargate Adventure (CustomTkinter)")
        self.geometry("800x600")
        
        self.engine = GameEngine()
        self.current_ctk_image = None

        # 'bg_image = Image.open("img/background.jpeg")
        # bg_image = bg_image.resize((800, 600))
        # self.bg_image_ctk = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(800, 600))
        # self.bg_label = ctk.CTkLabel(self, image=self.bg_image_ctk, text="")
        # self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)'

        #Room image frame
        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.pack(side="top", fill="x", pady=5)
        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.pack(side="top", padx=10, pady=10)

        #Middle Frame
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.pack(side="top", fill="both", expand=True, pady=5)

        #Textbox for story
        self.textbox = ctk.CTkTextbox(self.middle_frame, width=500, text_color="white")
        self.textbox.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=5)

        #Minimap for planet
        self.minimap = ctk.CTkLabel(self.middle_frame, text="Mini-Map", width=200, anchor="center")
        self.minimap.pack(side="right", fill="y", padx=(5, 10), pady=5)

        #Action Frame
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.pack(side="top", fill="x", pady=5)

        #Sub Button Frame
        self.sub_button_frame = ctk.CTkFrame(self)
        self.sub_button_frame.pack(side="top", fill="x", pady=5)


        
        # Ask for player name 
        self.after(100, self.ask_player_name)




    def ask_player_name(self):      # calls input mini GUI
        dialog = ctk.CTkInputDialog(text="Enter your name:", title="Player Name")
        player_name = dialog.get_input()
        if not player_name or player_name.strip() == "":
            player_name = "Player"
        self.start_game(player_name)

    def start_game(self, player_name):      #starts the game
        status = self.engine.initialize_game(player_name)
        self.update_text(status)
        self.update_room_image()
        self.update_planet_image()
        self.update_actions()

    def update_text(self, message):     #updates the text box with the message
        if not self.textbox.winfo_exists():
            return
        try:
            self.textbox.configure(state="normal")
            self.textbox.insert("end", message + "\n")
            self.textbox.configure(state="disabled")
            self.textbox.yview("end")
        except Exception:
            print("Error updating text:", Exception)

    def update_room_image(self):    #updates the room image
        room = self.engine.player.current_room
        if room.picture and os.path.exists(room.picture):
            img = Image.open(room.picture)
            img = img.resize((600, 300))
            self.current_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(600, 300))
            self.image_label.configure(image=self.current_ctk_image, text="")
        else:
            if room.picture:
                self.image_label.configure(text=f"Image not found: {room.picture}", image=None)
            else:
                self.image_label.configure(text="No image", image=None)

    def update_planet_image(self):
        planet = self.engine.player.current_planet
        if planet.picture and os.path.exists(planet.picture):
            img = Image.open(planet.picture)
            img = img.resize((180, 120))
            self.planet_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 200))
            self.minimap.configure(image=self.planet_ctk_image, text="")
        else:
            self.minimap.configure(text="No minimap available", image=None)

    


    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()


    def create_topic_response(self, npc, topic):
        def cmd():
            responses = npc.dialogues.get(topic, [])
            if responses:
                self.update_text(f"{npc.name}: {random.choice(responses)}")
            else:
                self.update_text(f"{npc.name} has nothing more to say about {topic}.")
        return cmd

    

    def display_npc_dialogue(self):
        self.clear_frame(self.sub_button_frame)
        npc = self.engine.player.current_room.npc
        if not npc or npc.dead:
            self.update_text("There's no one to talk to.")
            return

        # Show default dialogue
        default_lines = npc.dialogues.get("default", [])
        if default_lines:
            self.update_text(f"{npc.name}: {random.choice(default_lines)}")

        # List topics
        topics = [topic for topic in npc.dialogues if topic != "default"]
        if not topics:
            self.update_text(f"{npc.name} has no topics to discuss.")
            return

        self.update_text("🗣️ Topics:")
        for topic in topics:
            btn = ctk.CTkButton(self.sub_button_frame, text=topic.capitalize())
            btn.configure(command=self.create_topic_response(npc, topic))
            btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="End", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)


    def update_actions(self):
        self.clear_frame(self.action_frame)
        self.clear_frame(self.sub_button_frame)
        actions = self.engine.get_available_actions()

        for action in actions:
            btn = ctk.CTkButton(self.action_frame, text=action.capitalize())
            btn.configure(command=self.create_action_command(action))
            btn.pack(side="left", padx=5)

    def create_action_command(self, action):
        def cmd():
            self.handle_action(action)
        return cmd


        

    def handle_action(self, action):
        self.clear_frame(self.sub_button_frame)
        major_action = False

        if action == "move":
            self.display_move_options()
            return  # Wait for user to click direction
        elif action == "travel":
            self.display_travel_options()
            return  # Wait for user to click destination
        elif action == "interact":
            self.display_npc_dialogue()
            return  # early return to wait for button click
        elif action == "pickup":
            self.show_pickup_dialog()
        elif action == "kill":
            self.show_kill_dialog()
        elif action == "plant":
            text = self.engine.plant()
            self.update_text(text)
            major_action = True
        elif action == "drop":
            text = self.engine.drop()
            self.update_text(text)
            major_action = True
        elif action == "quit":
            dialog = ConfirmDialog(self, message="Do you really want to quit?")
            if dialog.result:
                self.update_text(self.engine.quit_game())
                self.destroy()
                return

        if major_action:
            self.update_text(self.engine.get_room_status())
            self.update_room_image()
            self.update_planet_image()
            self.update_actions()



    def handle_move(self):
        current_room = self.engine.player.current_room
        connections = current_room.connections
        self.directions_map = {}  # Maps button text to actual room name

        if not connections:
            self.update_text("There are no available directions to move.")
            self.update_text(self.engine.get_room_status())
            self.update_actions()
            return

        for conn in connections:
            room_name = conn.to_room
            self.directions_map[room_name] = room_name
            btn = ctk.CTkButton(self.sub_button_frame, text=room_name.capitalize())
            btn.configure(command=self.make_move_callback(room_name))
            btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)



    def move_to_direction(self, direction):
        result = self.engine.move(direction)
        self.update_text(result)
        self.clear_frame(self.sub_button_frame)
        status = self.engine.get_room_status()
        self.update_text(status)
        self.update_room_image()
        self.update_actions()

    def create_travel_destination_command(self, index):
        def cmd():
            self.travel_to_destination(index)
        return cmd


    def handle_travel(self):
        if self.engine.player.current_planet.name == "Mars":
            destinations = ["Earth", "Ha'tak"]
        else:
            destinations = ["Mars"]
        for idx, dest in enumerate(destinations):
            btn = ctk.CTkButton(self.sub_button_frame, text=dest)
            btn.configure(command=self.create_travel_destination_command(idx))

            btn.pack(side="left", padx=5)
        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)

    def travel_to_destination(self, choice_idx):
        result = self.engine.travel(choice_idx)
        self.update_text(result)
        self.clear_frame(self.sub_button_frame)
        status = self.engine.get_room_status()
        self.update_text(status)
        self.update_room_image()
        self.update_planet_image()
        self.update_actions()

    def cancel_sub_buttons(self):
        self.clear_frame(self.sub_button_frame)
        status = self.engine.get_room_status()
        self.update_text(status)
        self.update_actions()
    
    def create_move_command(self, room_name):
        def cmd():
            text = self.engine.move(room_name)
            self.clear_frame(self.sub_button_frame)
            self.update_text(text)
            self.update_room_image()
            self.update_actions()
        return cmd
    

    def show_pickup_dialog(self):
        self.clear_frame(self.sub_button_frame)
        room = self.engine.player.current_room
        items = room.items

        if not items:
            self.update_text("There are no items to pick up.")
            return

        self.update_text(" Choose an item to pick up:")

        for item_name in items:
            btn = ctk.CTkButton(self.sub_button_frame, text=item_name)
            btn.configure(command=self.create_pickup_command(item_name))
            btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)


    def create_pickup_command(self, item_name):
        def cmd():
            result = self.engine.pickup(item_name)
            self.update_text(result)
            self.clear_frame(self.sub_button_frame)
            self.update_actions()
        return cmd
    
    def create_kill_command(self, enemy_name):
        def cmd():
            result = self.engine.kill(enemy_name)
            self.update_text(result)
            self.clear_frame(self.sub_button_frame)
            self.update_actions()
        return cmd



    def show_kill_dialog(self):
        self.clear_frame(self.sub_button_frame)
        npc = self.engine.player.current_room.npc

        if npc and not npc.dead and npc.hostile:
            self.update_text("Choose an enemy to attack:")
            btn = ctk.CTkButton(self.sub_button_frame, text=npc.name)
            btn.configure(command=self.create_kill_command(npc.firstname))
            btn.pack(side="left", padx=5)

            cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
            cancel_btn.pack(side="left", padx=5)
        else:
            self.update_text("There are no enemies to kill.")




    def create_travel_command(self, index):
        def cmd():
            result = self.engine.travel(index)
            self.clear_frame(self.sub_button_frame)
            self.update_text(result)
            self.update_room_image()
            self.update_planet_image()
            self.update_actions()
        return cmd


    def display_travel_options(self):
        current_room = self.engine.player.current_room
        interplanetary_conns = [
            conn for conn in current_room.connections if conn.connection_type == "interplanetary"
        ]

        if not interplanetary_conns:
            self.update_text("No interplanetary connections available.")
            return

        self.clear_frame(self.sub_button_frame)
        self.update_text("Choose a destination:")

        for index, conn in enumerate(interplanetary_conns):
            to_room = self.engine.game.find_room_by_name(conn.to_room)
            if to_room:
                planet_name = to_room.planet.name
                btn = ctk.CTkButton(self.sub_button_frame, text=planet_name)
                btn.configure(command=self.create_travel_command(index))
                btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)



    
    def display_move_options(self):
        current_room = self.engine.player.current_room
        connections = [conn.to_room for conn in current_room.connections if conn.connection_type != "interplanetary"]

        if not connections:
            self.update_text("There are no available directions to move.")
            self.update_text(self.engine.get_room_status())
            self.update_actions()
            return

        self.move_buttons = []

        for room_name in connections:
            btn = ctk.CTkButton(self.sub_button_frame, text=room_name.capitalize())
            btn.configure(command=self.create_move_command(room_name))
            btn.pack(side="left", padx=5)
            self.move_buttons.append(btn)

        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)


    

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = MainApp()
    app.mainloop()
