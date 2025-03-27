import os
import pickle
import customtkinter as ctk
from PIL import Image
from game_engine import GameEngine 
import random


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Confirm", message="Do you really want to quit?"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.result = False
        self.grab_set()  # make modal
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

# --- Main Application using customtkinter ---
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stargate Adventure (CustomTkinter)")
        self.geometry("800x600")
        
        # Initialize game engine
        self.engine = GameEngine()
        self.current_ctk_image = None  # To hold CTkImage reference
        
        # --- Frame for Room Image (top) ---
        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.pack(side="top", fill="x", pady=5)
        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.pack(side="top", padx=10, pady=10)
        
        # --- Textbox for Game Messages (middle) ---
        self.textbox = ctk.CTkTextbox(self, width=750)
        self.textbox.pack(side="top", fill="both", expand=True, pady=5)
        self.textbox.configure(state="disabled")
        
        # --- Frame for Main Action Buttons ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.pack(side="top", fill="x", pady=5)
        
        # --- Frame for Dynamic Sub-Buttons (for move/travel) ---
        self.sub_button_frame = ctk.CTkFrame(self)
        self.sub_button_frame.pack(side="top", fill="x", pady=5)
        
        # Ask for player name after the window loads
        self.after(100, self.ask_player_name)

    def ask_player_name(self):
        dialog = ctk.CTkInputDialog(text="Enter your name:", title="Player Name")
        player_name = dialog.get_input()
        if not player_name or player_name.strip() == "":
            player_name = "Player"
        self.start_game(player_name)

    def start_game(self, player_name):
        status = self.engine.initialize_game(player_name)
        self.update_text(status)
        self.update_image()
        self.update_actions()

    def update_text(self, message):
        if not self.textbox.winfo_exists():
            return
        try:
            self.textbox.configure(state="normal")
            self.textbox.insert("end", message + "\n")
            self.textbox.configure(state="disabled")
            self.textbox.yview("end")
        except Exception as e:
            print("Error updating text:", e)

    def update_image(self):
        room = self.engine.player.current_room
        if room.picture and os.path.exists(room.picture):
            img = Image.open(room.picture)
            # Use Pillow's LANCZOS resampling (ANTIALIAS is removed)
            img = img.resize((600, 300), Image.Resampling.LANCZOS)
            self.current_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(600, 300))
            self.image_label.configure(image=self.current_ctk_image, text="")
        else:
            if room.picture:
                self.image_label.configure(text=f"Image not found: {room.picture}", image=None)
            else:
                self.image_label.configure(text="No image", image=None)

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
        # Create buttons for actions provided by the engine.
        for action in actions:
            btn = ctk.CTkButton(self.action_frame, text=action.capitalize(),
                                command=lambda a=action: self.handle_action(a))
            btn.pack(side="left", padx=5)
        # Add extra buttons for Save and Load.
        save_btn = ctk.CTkButton(self.action_frame, text="Save", command=self.save_game)
        save_btn.pack(side="left", padx=5)
        load_btn = ctk.CTkButton(self.action_frame, text="Load", command=self.load_game)
        load_btn.pack(side="left", padx=5)

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
            self.update_image()
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
        self.update_image()
        self.update_actions()

    def handle_travel(self):
        if self.engine.player.current_planet.name == "Mars":
            destinations = ["Earth", "Ha'tak"]
        else:
            destinations = ["Mars"]
        for idx, dest in enumerate(destinations):
            btn = ctk.CTkButton(self.sub_button_frame, text=dest,
                                command=lambda i=idx: self.travel_to_destination(i))
            btn.pack(side="left", padx=5)
        cancel_btn = ctk.CTkButton(self.sub_button_frame, text="Cancel", command=self.cancel_sub_buttons)
        cancel_btn.pack(side="left", padx=5)

    def travel_to_destination(self, choice_idx):
        result = self.engine.travel(choice_idx)
        self.update_text(result)
        self.clear_frame(self.sub_button_frame)
        status = self.engine.get_room_status()
        self.update_text(status)
        self.update_image()
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
            self.update_image()
            self.update_actions()
        return cmd
    
    def show_pickup_dialog(self):
        dialog = ctk.CTkInputDialog(title="Pick up item", text="Enter item name:")
        item_name = dialog.get_input()
        if item_name:
            text = self.engine.pickup(item_name)
            self.update_text(text)

    def show_kill_dialog(self):
        dialog = ctk.CTkInputDialog(title="Kill Enemy", text="Enter enemy name:")
        enemy_name = dialog.get_input()
        if enemy_name:
            text = self.engine.kill(enemy_name)
            self.update_text(text)



    def create_travel_command(self, index):
        def cmd():
            result = self.engine.travel(index)
            self.clear_frame(self.sub_button_frame)
            self.update_text(result)
            self.update_image()
            self.update_actions()
        return cmd


    def display_travel_options(self):
        current_room = self.engine.player.current_room
        self.interplanetary_conns = [
            conn for conn in current_room.connections if conn.connection_type == "interplanetary"
        ]

        if not self.interplanetary_conns:
            self.update_text("⚠️ No interplanetary connections available.")
            return

        for index, conn in enumerate(self.interplanetary_conns):
            btn = ctk.CTkButton(self.sub_button_frame, text=conn.to_room.capitalize())
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


    def save_game(self):
        try:
            with open("savegame.pkl", "wb") as f:
                pickle.dump(self.engine, f)
            self.update_text("Game saved successfully.")
        except Exception as e:
            self.update_text(f"Error saving game: {e}")

    def load_game(self):
        try:
            with open("savegame.pkl", "rb") as f:
                self.engine = pickle.load(f)
            self.update_text("Game loaded successfully.")
            self.update_image()
            self.update_actions()
        except Exception as e:
            self.update_text(f"Error loading game: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    app = MainApp()
    app.mainloop()
