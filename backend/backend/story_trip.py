from abc import ABC, abstractmethod

# =========================================
# ABSTRACT BASE CLASS
# =========================================
class TravelExperience(ABC):
    def __init__(self, personality, mood, budget, preference):
        self.personality = personality
        self.mood = mood
        self.budget = budget
        self.preference = preference

    @abstractmethod
    def show_experience(self):
        pass


# =========================================
# STORY TRIP CLASS
# =========================================
class StoryTrip(TravelExperience):
    def __init__(self, personality, mood, budget, preference):
        super().__init__(personality, mood, budget, preference)
        self.destination = ""
        self.role_text = ""
        self.companion = ""
        self.environment = ""
        self.ending = ""
        self.mission = ""
        self.danger = ""
        self.reward = ""
        self.image_file = "default.jpeg"

    def generate_world(self):
        if self.mood == 1:
            if self.budget == 1:
                self.destination = "Raya Keep, Omal"
                self.role_text = "a teenage orphan discovering hidden magical powers"
                self.image_file = "raya keep orphanage.jpeg"
            elif self.budget == 2:
                self.destination = "Alcahla, Nizhal"
                self.role_text = "a respected city guardian protecting peaceful citizens"
                self.image_file = "nizhl village.jpeg"
            else:
                self.destination = "Ivory Palace, Lukub"
                self.role_text = "the Queen ruling over a kingdom of light and music"
                self.image_file = "jasad kingdom.jpeg"

        elif self.mood == 2:
            if self.budget == 1:
                self.destination = "Southern Woods, Spring Court"
                self.role_text = "a herbal healer living among ancient forests"
                self.image_file = "spring.jpeg"
            elif self.budget == 2:
                self.destination = "Fauna, Winter Court"
                self.role_text = "a royal seamstress crafting enchanted winter garments"
                self.image_file = "winter.jpeg"
            else:
                self.destination = "Valaris, Night Court"
                self.role_text = "a High Lord surrounded by stars and endless beauty"
                self.image_file = "night court.jpeg"

        elif self.mood == 3:
            if self.budget == 1:
                self.destination = "Streets of Arabian Lands"
                self.role_text = "a street thief surviving through intelligence and speed"
                self.image_file = "thief.jpeg"
            elif self.budget == 2:
                self.destination = "Bahr Al-Sirr"
                self.role_text = "a time traveler uncovering forbidden dimensions"
                self.image_file = "time traveler.jpeg"
            else:
                self.destination = "Al-Qasr Al-Abyad"
                self.role_text = "a disguised princess hunting the empire's dark secrets"
                self.image_file = "queen of arabian land.jpeg"

        else:
            if self.budget == 1:
                self.destination = "Braderhelm Prison"
                self.role_text = "a prisoner fighting against hopeless darkness"
                self.image_file = "prison.jpeg"
            elif self.budget == 2:
                self.destination = "Hermes Ruins"
                self.role_text = "a lonely lorekeeper watching civilizations collapse"
                self.image_file = "library.jpeg"
            else:
                self.destination = "Genesis Core"
                self.role_text = "the daughter of a ruthless galactic emperor"
                self.image_file = "genesis core.jpeg"

    def generate_companion(self):
        if self.personality == 1:
            self.companion = "a calm and intelligent companion who quietly understands your pain"
        else:
            self.companion = "a fearless and energetic companion who turns every moment into chaos"

    def generate_environment(self):
        if "Court" in self.destination:
            self.environment = "magical kingdoms glowing beneath eternal twilight skies"
        elif "Arabian" in self.destination or "Bahr" in self.destination:
            self.environment = "golden deserts hiding ancient temples and forbidden relics"
        elif any(word in self.destination for word in ["Genesis", "Prison", "Ruins"]):
            self.environment = "ruined futuristic worlds powered by forgotten celestial energy"
        else:
            self.environment = "mysterious lands beyond imagination"

    def generate_mission(self):
        if self.preference == 1:
            self.mission = "heal broken souls and uncover emotional truths"
        elif self.preference == 2:
            self.mission = "survive deadly battles against powerful enemies"
        else:
            self.mission = "explore forgotten lands and reveal hidden mysteries"

    def generate_danger(self):
        if self.mood == 1:
            self.danger = "A hidden betrayal threatens the peace of the kingdom"
        elif self.mood == 2:
            self.danger = "Ancient spirits awaken beneath the silent forests"
        elif self.mood == 3:
            self.danger = "Deadly hunters track your every move across the desert"
        else:
            self.danger = "A powerful empire seeks to erase your existence"

    def generate_reward(self):
        if self.budget == 1:
            self.reward = "freedom and survival"
        elif self.budget == 2:
            self.reward = "respect, power, and forgotten knowledge"
        else:
            self.reward = "a legendary throne capable of reshaping reality"

    def generate_ending(self):
        if self.mood == 1:
            self.ending = "Joy fills your world as hope shines brighter than ever"
        elif self.mood == 2:
            self.ending = "Peace slowly heals the scars buried deep within you"
        elif self.mood == 3:
            self.ending = "Adventure transforms you into a fearless legend"
        else:
            self.ending = "Even sorrow becomes part of your destiny and strength"

    # =========================================
    # REQUIRED METHOD (FIX)
    # =========================================
    def show_experience(self):
        return (
            f"You are in {self.destination}. "
            f"You are {self.role_text}. "
            f"You travel through {self.environment}. "
            f"Your mission is: {self.mission}. "
            f"Danger: {self.danger}. "
            f"Reward: {self.reward}. "
            f"Ending: {self.ending}. "
            f"Companion: {self.companion}."
        )